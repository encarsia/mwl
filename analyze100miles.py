#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import collections
import csv
import datetime
import types
import yaml


Stage = collections.namedtuple("Stage", [
            "time",
            "pace",
            "time_total",
            "note",
            ])

YEAR_COURSE = {2011: "clockwise_2011",
               2013: "counterclockwise_2013",
               2014: "clockwise",
               2015: "counterclockwise",
               2016: "clockwise",
               2017: "counterclockwise",
               2018: "clockwise_new",
               2021: "clockwise_new",
               }

TAGS = {"f": "Frauen",
        "m": "Männer",
        "r2": "2er-Staffeln",
        "r4": "4er-Staffeln",
        "r10": "10plus-Staffeln",
        }

VP_FILE = "vp_list.yaml"

RULE = "---------------------------------------------------------------------------------\n"


class Results:
    
    def __init__(self, year=0): # avoid missing positional argument TypeError
        
        if year in YEAR_COURSE.keys():
            self.year = year
            
            self.vp_list = self._read_vplist(VP_FILE, self.year)
            self.vp_index = list(self.vp_list.keys())
            
            csv_file = "results/result_course_{}.csv".format(self.year)
            data = self._read_csv(csv_file)
            if self.year > 2018:
                self.results = self._runner_details_RR(data, self.vp_index)
            else:
                self.results = self._runner_details_SI(data, self.vp_index)
            self.results, self.rankings = self._get_ranking(self.results)
        else:
            print("Optionen (int): {}".format(YEAR_COURSE.keys()))


    def _read_vplist(self, filename, year):
        
        """read yaml file and returns data as dict"""
        
        with open(filename) as f:
            vp_list = yaml.safe_load(f)
        vp_list = vp_list[YEAR_COURSE[year]]
        return vp_list


    def _read_csv(self, filename):
        
        """returns results from SportIdent csv file as list"""
        
        with open(filename) as f:
            reader = csv.reader(f, delimiter=";")
            data = list(reader)
        return data


    def _get_course(self, vp_list):
        
        returnstring = ("""
Verpflegungspunkte/Zeitmessung
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
""")
        row = "{:<5} {:<9} {:<9} {}\n"
        returnstring += row.format("VP", "Split km", "Abs km", "Name")
        returnstring += RULE
        for vp in vp_list:
            returnstring += row.format(vp,
                              vp_list[vp]["km"],
                              vp_list[vp]["km_kum"],
                              vp_list[vp]["name"],
                              )
        returnstring += RULE
        return returnstring


    def _get_ranking(self, results):
        
        """results table = ranking
           <= 2018 sorted by category, 2021 sorted by finishing
        """
        
        ranking = {"m": {"FIN": [],
                         "DNF": [],
                         "DSQ": [],
                         "DNS": [],}, # 2017
                   "f": {"FIN": [],
                         "DNF": [],
                         "DSQ": [],
                         "DNS": [],}, # 2017
                   "r2": {"FIN": [],
                          "DNF": [],
                          "DSQ": [],
                          "DNS": [],}, # 2017
                   "r4": {"FIN": [],
                          "DNF": [],
                          "DSQ": [],
                          "DNS": [],}, # 2017
                   "r10": {"FIN": [],
                           "DNF": [],
                           "DSQ": [],
                           "DNS": [],}, # 2017
                    }

        for startnr, r in results.items():
            if "DNF" in r.rank:
                ranking[r.tag]["DNF"].append(startnr)
            elif "DSQ" in r.rank:
                ranking[r.tag]["DSQ"].append(startnr)
            elif r.rank == "":
                ranking[r.tag]["DNS"].append(startnr)
            else:
                # ordered list of finishers
                ranking[r.tag]["FIN"].append(startnr)

        # add total numbers of starters for later use in vp_stats and ranking table
        ranking["total"] = 0
        for _ in TAGS.keys():
            _total = len(ranking[_]["FIN"]) + len(ranking[_]["DSQ"]) + len(ranking[_]["DNF"]) + len(ranking[_]["DNS"])
            ranking[_]["total"] = _total
            ranking["total"] += _total

        # overwrite rank value from csv table (consecutive order of finishing) with real rank
        for tag in TAGS.keys():
            for _rank, startnr in enumerate(ranking[tag]["FIN"], 1):
                results[startnr].rank = _rank

        return results, ranking


    def ranking(self, tag=""): # avoid missing positional argument TypeError

        """ranking table by category
           
           Argument:
                tag: "f": women's results 
                     "m": men's results 
                     "r2": 2-person relay
                     "r4": 4-person relay
                     "r10": 10plus-person relay
        """

        if tag not in TAGS.keys():
            print("Optionen (str): {}".format(TAGS.keys()))
            return
        
        ranking_list = self.rankings[tag]
        
        stats = (len(ranking_list["FIN"]),
                 len(ranking_list["DNF"]),
                 len(ranking_list["DSQ"]),
                 len(ranking_list["DNS"]), # only in 2017
                 ranking_list["total"],
                )

        returnstring = """
~~~~~~~~~~~~~~~~~~~~~~~~~
Ranking {}
~~~~~~~~~~~~~~~~~~~~~~~~~

Finisher: {:<4} ({} %)
DNF:      {:<4} ({} %)
DSQ:      {:<4} ({} %)
-------------------------
Total:    {}
=========================

""".format(TAGS[tag],
           stats[0], round(stats[0] / stats[4] * 100, 1),
           stats[1], round(stats[1] / stats[4] * 100, 1),
           stats[2], round(stats[2] / stats[4] * 100, 1),
           stats[4],
           )

        returnstring += RULE
        row = "{:<6} {:<7} {:<40} {:<10} {}\n"
        returnstring += row.format("Platz", "StartNr", "Name", "Zeit", "Kategorie")
        returnstring += RULE
        
        for _ in ("FIN", "DNF", "DSQ", "DNS"):
            for startnr in ranking_list[_]:
                returnstring += row.format(self.results[startnr].rank,
                                           startnr,
                                           self.results[startnr].name,
                                           self.results[startnr].time,
                                           self.results[startnr].cat,
                                    )
            if len(ranking_list[_]) > 0: # avoid unnecessary rules
                returnstring += RULE
        
        print(returnstring)


    def _sort_pace(self, pace):
        
        try:
            hour, minute = pace[0].split(":")
            return int(hour), int(minute)
        except ValueError:
            return


    def _runner_details_RR(self, data, vp_index):
        
        """reads data list and returns dict of namedtuples with runner
           details and stage times"""
        
        # results as dict of "startnr: namedtuple" items
        res = dict()
        
        for d in data:
            if d[1] != "StartNr": # ignore table headers
                stage_time = []
                stage_pace = []
                stage_total = []
                stage_note = []
                total = datetime.timedelta()
                for t in d[13:91:3]:
                    try:
                        if len(t.split(":")) < 2:
                            stage_note.append("(Messung fehlt/fehlerhaft)")
                            stage_time.append("")
                        elif len(t.split(":")) == 2:
                            m, s = t.split(":")
                            stage_time.append(t)
                            stage_note.append("")
                            delta = datetime.timedelta(hours=0, minutes=int(m), seconds=int(s))
                            total += delta
                        elif len(t.split(":")) == 3:
                            h, m, s = t.split(":")
                            stage_time.append(t)
                            stage_note.append("")
                            delta = datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s))
                            total += delta
                    except ValueError:
                        # total = t
                        break
                    stage_total.append(total)
                
                # Ziel is total time not split time so calculate it
                try:
                    h, m, s = d[-2].split(":")
                    _stagetime = datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s)) - total
                    if int(_stagetime.total_seconds() / 3600) > 0:
                        _stagestr = "{}:{:>02}:{:>02}".format(int(_stagetime.total_seconds() // 3600),
                                                              int(_stagetime.total_seconds() % 3600 // 60),
                                                              int(_stagetime.total_seconds() % 60),
                                                              )
                    else:
                        _stagestr = "{:>02}:{:>02}".format(int(_stagetime.total_seconds() % 3600 // 60),
                                                           int(_stagetime.total_seconds() % 60),
                                                              )
                    stage_time.append(_stagestr)
                    total += _stagetime
                    stage_note.append("")
                    stage_total.append(total)
                except ValueError:
                    stage_note.append("(Messung fehlt/fehlerhaft)")
                    stage_time.append("")
                    stage_total.append(total)
                
                # pace is overall pace, TODO calculate split pace
                for p in d[14:96:3]:
                    stage_pace.append(p)
                
                stages = dict()
                for i, t, p, tot, n in zip(vp_index, stage_time, stage_pace, stage_total, stage_note):
                    stages[i] = Stage(t, p, tot, n)
                
                _name = d[2]

                if d[6] == "m":
                    tag = "m"
                    starttime = datetime.timedelta(hours=6)
                    cat = d[2].split("(")[1][:-1] # in brackets in name column
                    _name = d[2].split("(")[0][:-1] # cut category after name
                elif d[6] == "w":
                    tag = "f"
                    # TODO starttime in course info
                    starttime = datetime.timedelta(hours=6)
                    cat = d[2].split("(")[1][:-1] # in brackets in name column
                    _name = d[2].split("(")[0][:-1]
                elif d[5] == "2er":
                    tag = "r2"
                    starttime = datetime.timedelta(hours=7)
                    cat = TAGS[tag]
                elif d[5] == "4er":
                    tag = "r4"
                    starttime = datetime.timedelta(hours=7, minutes=30)
                    cat = TAGS[tag]
                elif d[5] == "10+":
                    tag = "r10"
                    starttime = datetime.timedelta(hours=8)
                    cat = TAGS[tag]
                else:
                    # shouldn't happen but will nonetheless
                    tag = "invalid"
                    cat = "invalid"

                _runner_dict = {
                    "rank": d[0],
                    "name": _name,
                    "nation": d[3],
                    "cat": cat,
                    "tag": tag,
                    "starttime": starttime,
                    "time": d[11], # TODO calculate overall time
                    "pace": d[10],
                    "lag": d[11],
                    "stages": stages,
                    }
                
                # make runner results dictionary dot notation accessible
                _runner_dict = types.SimpleNamespace(**_runner_dict)
                
                res[int(d[1])] = _runner_dict
            
        return res


    def _runner_details_SI(self, data, vp_index):
        
        """reads data list and returns list of namedtuples with list of
           runner details and stage times
        """
        
        # results as dict of "startnr: namedtuple" items
        res = dict()
        
        for d in data:
            if d[1] != "StartNr": # ignore table headers
                stage_time = []
                stage_pace = []
                stage_total = []
                stage_note = []
                total = datetime.timedelta()
                for t in d[15:97:3]:
                    stage_time.append(t)
                    try:
                        h, m, s = t.split(":")
                        delta = datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s))
                        total += delta
                    except ValueError:
                        total = t
                        break
                    stage_total.append(total)
                for p in d[16:98:3]:
                    stage_pace.append(p.split(" min/km")[0])
                    stage_note.append("")   # dummy note so print table doesn't break
                
                stages = dict()
                for i, t, p, tot, n in zip(vp_index, stage_time, stage_pace, stage_total, stage_note):
                    stages[i] = Stage(t, p, tot, n)

                _name = d[3]
                # team name is encoded in club column in 2017
                if _name.startswith("Team,"):
                    _name = d[5]

                cat = d[8]
                
                if d[8].startswith("Senioren") or d[8].startswith("Männer"):
                    tag = "m"
                    starttime = datetime.timedelta(hours=6)
                elif d[8].startswith("Seniorinnen") or d[8].startswith("Frauen"):
                    tag = "f"
                    starttime = datetime.timedelta(hours=6)
                else:
                    # relay information is set in different columns over the years
                    if d[8].startswith("2er")or d[8].startswith("Staffel 2x") or d[7].startswith("2er"):
                        tag = "r2"
                        cat = TAGS[tag]
                    elif d[8].startswith("4er") or d[8].startswith("Staffel 4x") or d[7].startswith("4er"):
                        tag = "r4"
                        cat = TAGS[tag]
                    elif d[8].startswith("10Plus") or d[8].startswith("10er") or d[7].startswith("10+"):
                        tag = "r10"
                        cat = TAGS[tag]
                    elif d[8].startswith("Gesamt"): # 2011
                        tag = "all"
                        cat = "keine Information"
                    else:
                        tag = "invalid"
                        cat = "invalid"
                    starttime = datetime.timedelta(hours=7)

                _runner_dict = {
                    "rank": d[0],
                    "name": _name,
                    "nation": d[4],
                    "cat": cat,
                    "tag": tag,
                    "starttime": starttime,
                    "time": d[11], 
                    "pace": d[12].split(" min/km")[0],
                    "lag": d[13],
                    "stages": stages,
                    }
                
                # make runner results dictionary dot notation accessible
                _runner_dict = types.SimpleNamespace(**_runner_dict)
                
                res[int(d[1])] = _runner_dict

        return res


    def vp_stats(self, vp, tag="all", list_runners=10):
        
        """reads all runner results at a given vp (refreshing point = time measurement) and returns string with
           first 3/quartils times of passing the vp.
           
           Arguments:
                vp: pass vp index as string, p.e. "VP1"..."Ziel"
                tag: "all" (default): include single runners and relays
                     "f": women's results only
                     "m": men's results only
                     "r": relay results only
                     "r2": 2-person relay
                     "r4": 4-person relay
                     "r10": 10plus-person relay
                list_runners: first number of runners to be listed
                                - default is 10
                                - use 0 to show all
        """
        pass_all = []
        pace = []
        for startnr, r in self.results.items():
            try:
                pass_time = r.starttime + r.stages[vp].time_total
                # probably measurement error at Sportident
                # 2018: startno 2001, total time of > 42 hours...?
                if pass_time > datetime.timedelta(days=2):
                    raise KeyError
                # ignore if stage pace is missing
                if r.stages[vp].pace == "-":
                    raise KeyError
                if tag == r.tag:
                    try:
                        if not r.stages[vp].note == "(Messung fehlt/fehlerhaft)":
                            pass_all.append([pass_time, r.name, startnr])
                            pace.append((r.stages[vp].pace, r.name, startnr))
                    except KeyError:
                        pass
                elif tag == "all":
                    try:
                        if not r.stages[vp].note == "(Messung fehlt/fehlerhaft)":
                            pass_all.append([pass_time, r.name, startnr])
                            pace.append((r.stages[vp].pace, r.name, startnr))
                    except KeyError:
                        pass
            except KeyError:
                pass
        pass_all = sorted(pass_all)
        # just for readability convenience
        for p in pass_all:
            p[0] = str(p[0]).replace("1 day", "Sonntag")
        pace = sorted(pace, key=self._sort_pace)

        if tag == "all":
            _total = self.rankings["total"]
        else:
            _total = self.rankings[tag]["total"]

        returnstring = """
{} - {} - km {}
************************************************************************
Anzahl Läufer/Staffeln: {} von {} ({} %)

""".format(vp,
           self.vp_list[vp]["name"],
           self.vp_list[vp]["km_kum"],
           len(pass_all),
           _total,
           round(len(pass_all) / _total * 100, 1),
           )
           
        if list_runners == 0 or list_runners > len(pass_all):
            list_runners = len(pass_all)
        for i in range(list_runners):
            returnstring += """{:>3}:  {} Uhr - {} ({})
""".format(i + 1,
           pass_all[i][0],
           pass_all[i][1],
           pass_all[i][2],
           )

        returnstring += """
25 %:  {} Uhr
50 %:  {} Uhr
75 %:  {} Uhr
100 %: {} Uhr ({})
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Split pace in min/km

1: {} - {} ({})
2: {} - {} ({})
3: {} - {} ({})
4: {} - {} ({})
5: {} - {} ({})
************************************************************************
""".format(pass_all[int(len(pass_all) * .25)][0],
           pass_all[int(len(pass_all) * .5)][0],
           pass_all[int(len(pass_all) * .75)][0],
           pass_all[-1][0], pass_all[-1][1],
           
           pace[0][0], pace[0][1], pace[0][2],
           pace[1][0], pace[1][1], pace[1][2],
           pace[2][0], pace[2][1], pace[2][2],
           pace[3][0], pace[3][1], pace[3][2],
           pace[4][0], pace[4][1], pace[4][2],
           )
           
        print(returnstring)


    def runner_stats(self, nr):
        
        """print result table for given startnr"""
        
        r = self.results[nr]
        print("""
Name: {} ({}) - Platz: {}
StartNr: {} - Kategorie: {}
Zeit: {} - Pace: {} - Rückstand: {}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~""".format(r.name,
                                                                r.nation,
                                                                r.rank,
                                                                nr,
                                                                r.cat,
                                                                r.time,
                                                                r.pace,
                                                                r.lag,
                                                                )
                        )
        row = "{:<6} {:<11} {:<11} {:<10} {}"
        print(row.format("VP",
                          "Split time",
                          "Split pace",
                          "Time (total)",
                          "", # placeholder for note
                          ))
        for stage in r.stages:
            t = r.stages[stage].time_total.total_seconds()
            time_total = "{}:{:>02}:{:>02}".format(int(t // 3600),
                                           int(t % 3600 // 60),
                                           int(t % 60,))
            print(row.format(stage,
                             r.stages[stage].time,
                             r.stages[stage].pace,
                             time_total,
                             r.stages[stage].note,
                             )
                  )
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    def course_info(self):
        print(self._get_course(self.vp_list))
