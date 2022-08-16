# mwl - Mauerweglaufdaten analysieren

## Wozu?

* Planungshilfe für die [100 Meilen Berlin](http://100meilen.de/), Neugier, Zahlenspielerei

## Was kann angezeigt werden?

* Streckeninfo, Ranking, Durchlaufzeiten an den VPs, Läuferdetails

## Daten

* 2013 - 2018: die Daten wurden von [SPORTident](https://www.sportident.com/) erfasst und sind als csv-Dateien verfügbar (oben rechts unter "Downloads" auf der jeweiligen Veranstaltungsseite); die von der SPORTident-Webseite heruntergeladenen csv-Dateien sind nicht UTF-8-kodiert
* ab 2021: die Daten wurden von [race result](https://www.raceresult.com) erfasst; die csv-Dateien wurden auf Anfrage zur Verfügung gestellt; [Ergebnisse bei race result](http://my.raceresult.com/184322/)
* die Ergebnislisten befinden sich im Ordner ``results``
* fehlende Daten:
    * 2019: keine verwertbaren Daten bzw. Zwischenzeiten aufgrund eines technischen Problems
    * 2020: Veranstaltung wegen Covid19 abgesagt

## Benutzung

* Repository klonen oder Archiv herunterladen und entpacken und ins entsprechende Verzeichnis wechseln
* Python-Interpreter starten

### Daten laden

```python
from analyze100miles import Results
res = Results(2018) # lädt die Daten des Jahres 2018
```

### Streckeninfo

```python
res.course_info()
```

#### Ausgabe

```
Verpflegungspunkte/Zeitmessung
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
VP    Split km  Abs km    Name
---------------------------------------------------------------------------------
VP1   8,6       8,6       Checkpoint Charlie
VP2   4,8       13,4      East Side Gallery
[...]
VP26  3,0       157,4     Wollankstrasse
Ziel  3,9       161,3     Friedrich-Ludwig-Jahn-Sportpark
---------------------------------------------------------------------------------
```

### Durchlaufzeiten an den VPs

```python
res.vp_stats("VP5")

# Filtern nach Frauen/Männern/Staffeln
# 2011: nur ein Gesamtclassement und keine Staffeln
# 2013: keine 10plus-Staffeln

res.vp_stats("VP5", "f") 
res.vp_stats("VP5", "m") 
res.vp_stats("VP5", "r2")
res.vp_stats("VP5", "r4")
res.vp_stats("VP5", "r10")

# Wie zuvor, Anzeige der ersten n Läufer (default 10, 0 für alle)

res.vp_stats("VP5", "f", 3) # listet die ersten 3 Männer 
res.vp_stats("VP5", "m", 20) # listet die ersten 20 Frauen
res.vp_stats("VP5", "r4", 0) # listet alle 4er-Staffeln
res.vp_stats("VP5", "all", 0) # listet alle
```

#### Ausgabe

```
VP5 - Imbiss "Am Ziel"/Dörferblick - km 31,4
************************************************************************
Anzahl Läufer/Staffeln: 507 von 508 (99.8 %)

  1:  8:41:17 Uhr - Ishikawa, Yoshihiko (5)
  2:  8:42:03 Uhr - RUEL, Stephane (4)
  3:  8:45:36 Uhr - Dehling, Sascha (1)
  4:  8:45:38 Uhr - Laenger, Uwe (418)
  5:  8:46:29 Uhr - Iguchi, Shinpei (429)
  6:  8:49:11 Uhr - Jänicke, Marc Cornelius (2)
  7:  8:53:30 Uhr - Wiegand, Frank (362)
  8:  8:53:30 Uhr - Wilsdorf, Stefan (453)
  9:  8:54:16 Uhr - Strykowski, Jaroslaw (95)
 10:  8:55:51 Uhr - Tribius, Thomas (346)

25 %:  9:45:34 Uhr
50 %:  10:10:14 Uhr
75 %:  10:29:12 Uhr
100 %: 12:00:10 Uhr (Besenstaffel)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Split pace in min/km

1: 4:13 - FH Runners Berlin (4029)
2: 4:22 - Ishikawa, Yoshihiko (5)
3: 4:22 - BSG EDEKA (1022)
4: 4:25 - Die Meisels (4002)
5: 4:27 - RUEL, Stephane (4)
************************************************************************
```

### Ranking

```python
# Ausgabe der Ergebnislisten nach Kategorie

res.ranking("m")
res.ranking("f")
res.ranking("r2")
res.ranking("r4")
res.ranking("r10")

# Ausnahme: Ergebnisse von 2011 sind nicht kategorisiert

res.ranking()
```

#### Ausgabe

```
~~~~~~~~~~~~~~~~~~~~~~~~~
Ranking 
~~~~~~~~~~~~~~~~~~~~~~~~~

Finisher: 259  (82.7 %)
DNF:      53   (16.9 %)
DSQ:      1    (0.3 %)
-------------------------
Total:    313
=========================

---------------------------------------------------------------------------------
Platz  StartNr Name                                     Zeit       Kategorie
---------------------------------------------------------------------------------
1      5       Ishikawa, Yoshihiko                      13:17:41   Senioren M30 (30-34 Jahre)
2      418     Laenger, Uwe                             14:30:53   Senioren M50 (50-54 Jahre)
[...]
DNF    196     Kuhn, Enrico                             fehlt!     Senioren M30 (30-34 Jahre)
DNF    446     Kohlsdorf, Detlef                        fehlt!     Senioren M55 (55-59 Jahre)
[...]
DSQ    4       RUEL, Stephane                           14:25:24   Senioren M50 (50-54 Jahre)
---------------------------------------------------------------------------------
```

### Läuferdetails

```python
res.runner_stats(100) # StartNr, siehe Ranking/Durchlaufzeiten
```

#### Ausgabe

```
Name: Roch, Karl (GER) - Platz: 92
StartNr: 100 - Kategorie: Senioren M55 (55-59 Jahre)
Zeit: 22:13:56 - Pace: 8:14 - Rückstand: 8:56:15
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
VP     Split time   Split pace   Time (total)   
VP1      00:57:29         6:41        0:57:29   
VP2      00:26:53         5:36        1:24:22   
[...]
VP26     00:34:49        11:13       21:36:29   
Ziel     00:37:27         8:55       22:13:56   
```

#### Bug in Daten von 2021

> "Split pace" zeigt nicht die Pace zwischen zwei Messpunkten, sondern die kumulierte Gesamtpace.

## Übertragbarkeit auf andere mit SPORTident erfasste Veranstaltungen

* **ungetestet**
* da die csv-Dateien immer den gleichen Aufbau haben, sollte sich das Skript auch leicht an andere Veranstaltungen anpassen lassen:
  * ``vp_list.yaml``: Details der Messstationen anpassen/erstellen
  * ``analyze100miles.py``: Dictionary ``YEAR_COURSE`` entsprechend anpassen
  * csv-Datei(en) in ``/results`` speichern
