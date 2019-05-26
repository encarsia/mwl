#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import collections
import csv
import datetime
import yaml

Runner = collections.namedtuple("Runner", [
            "rank",
            "startnr",
            "name",
            "cat",
            "tag",
            "starttime",
            "time",
            "pace",
            "stages",
            ])

Stage = collections.namedtuple("Stage", [
            "time",
            "pace",
            "time_total",
            ])

YEAR_COURSE = {2011: "clockwise_2011",
               2013: "counterclockwise_2013",
               2014: "clockwise",
               2015: "counterclockwise",
               2016: "clockwise",
               2017: "counterclockwise",
               2018: "clockwise_new",
               }

VP_FILE = "vp_list.yaml"

RULE = "---------------------------------------------------------------------------------\n"


class Results:
    
    def __init__(self, year):
        if year in YEAR_COURSE.keys():
            self.year = year
            
            self.vp_list = self._read_vplist(VP_FILE, self.year)
            self.course_info = self._get_course(self.vp_list)
            self.vp_index = list(self.vp_list.keys())
            
            csv_file = "SI_results/result_course_{}.csv".format(self.year)
            data = self._read_csv(csv_file)
            self.results = self._runner_details(data, self.vp_index)
            self.ranking = self._get_ranking(self.results)
        else:
            print("Available options (int): {}".format(YEAR_COURSE.keys()))

    def _read_vplist(self, filename, year):
        """read yaml file and returns data as dict"""
        with open(filename) as f:
            vp_list = yaml.load(f)
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
        returnstring = ("""
Ranking
~~~~~~~
""")
        row = "{:<5} {:<7} {:<40} {:<10} {}\n"
        returnstring += row.format("Platz", "StartNr", "Name", "Zeit", "Kategorie")
        returnstring += RULE
        for r in results:
            returnstring += row.format(r.rank,
                                       r.startnr,
                                       r.name,
                                       r.time,
                                       r.cat,
                                    )
        returnstring += RULE
        return returnstring

    def _sort_pace(self, pace):
        try:
            hour, minute = pace[0].split(":")
            return int(hour), int(minute)
        except ValueError:
            return

    def _runner_details(self, data, vp_index):
        """reads data list and returns list of namedtuples with list of
           runner details and stage times"""
        res = []
        for d in data:
            if d[1] != "StartNr": # ignore table headers
                stage_time = []
                stage_pace = []
                stage_total = []
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
                
                stages = dict()
                for i, t, p, tot in zip(vp_index, stage_time, stage_pace, stage_total):
                    stages[i] = Stage(t, p, tot)

                if d[8].startswith("Senioren") or d[8].startswith("Männer"):
                    tag = "m"
                    starttime = datetime.timedelta(hours=6)
                elif d[8].startswith("Seniorinnen") or d[8].startswith("Frauen"):
                    tag = "f"
                    starttime = datetime.timedelta(hours=6)
                else:
                    tag = "r"
                    starttime = datetime.timedelta(hours=7)
                    
                res.append(Runner(d[0],
                                  int(d[1]),
                                  d[3],
                                  d[8],
                                  tag,
                                  starttime,
                                  d[11],
                                  d[12],
                                  stages,
                                 ))
        return res

    def vp_stats(self, vp, tag="all", list_runners=10):
        print(self._get_vp_stats(vp, tag, list_runners))

    def stats_to_file(self, tag="all", list_runners=0):
        """creates list for all vps and dumps it into file, all runners listed if list_runners not set"""
        data = "Durchlaufzeiten für das Jahr {}\n".format(self.year)
        for vp in self.vp_index:
            data += self._get_vp_stats(vp, tag, list_runners)
        filename = "{}_{}.txt".format(self.year, tag, list_runners)
        with open(filename, "w") as f:
            f.write(data)

    def _get_vp_stats(self, vp, tag, list_runners):
        """reads all runner results at a given vp and returns string with
           first 3/quartils times of passing the vp.
           
           Arguments:
                vp: pass vp index as string, p.e. "VP1"..."Ziel"
                tag: "all" (default): include single runners and relays
                     "f": women's results only
                     "m": men's results only
                     "r": relay results only
                list_runners: first number of runners to be listed
                                - default is 10
                                - use 0 to show all
        """
        pass_all = []
        pace = []
        for r in self.results:
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
                        pass_all.append([pass_time, r.name, r.startnr])
                        pace.append((r.stages[vp].pace, r.name))
                    except KeyError:
                        pass
                elif tag == "all":
                    try:
                        pass_all.append([pass_time, r.name, r.startnr])
                        pace.append((r.stages[vp].pace, r.name))
                    except KeyError:
                        pass
            except KeyError:
                pass
        pass_all = sorted(pass_all)
        # just for readability convenience
        for p in pass_all:
            p[0] = str(p[0]).replace("1 day", "Sonntag")
        pace = sorted(pace, key=self._sort_pace)

        returnstring = """
{} - {} - km {}
************************************************************************
Anzahl Läufer: {}

""".format(vp,
           self.vp_list[vp]["name"],
           self.vp_list[vp]["km_kum"],
           len(pass_all),
           )
           
        if list_runners == 0 or list_runners > len(pass_all):
            list_runners = len(pass_all)
        for i in range(list_runners):
            returnstring += """{}.: {} Uhr - {} ({})
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

1.:  {} ({})
2.:  {} ({})
3.:  {} ({})
4.:  {} ({})
5.:  {} ({})
************************************************************************
""".format(pass_all[int(len(pass_all) * .25)][0],
           pass_all[int(len(pass_all) * .5)][0],
           pass_all[int(len(pass_all) * .75)][0],
           pass_all[-1][0], pass_all[-1][1],
           
           pace[0][0], pace[0][1],
           pace[1][0], pace[1][1],
           pace[2][0], pace[2][1],
           pace[3][0], pace[3][1],
           pace[4][0], pace[4][1],
           )
        return returnstring

    def runner_stats(self, nr):
        for r in self.results:
            if r.startnr == nr:
                print("""
Name: {} - Platz: {}
StartNr: {} - Kategorie: {}
Zeit: {} - Pace: {}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~""".format(r.name,
                                                              r.rank,
                                                              nr,
                                                              r.cat,
                                                              r.time,
                                                              r.pace
                                                              ))
                row = "{:<5} {:<10} {:<10} {}"
                print(row.format("VP",
                                  "Split time",
                                  "Split pace",
                                  "Time (total)",
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
                                      ))
                break
