# mwl - Mauerweglaufdaten analysieren

## Wozu?

* Planungshilfe für die [100 Meilen Berlin](http://100meilen.de/), Neugier, Zahlenspielerei

## Was kann angezeigt werden?

* Streckeninfo, Ranking, Durchlaufzeiten an den VPs, Läuferdetails

## Daten

* die Daten wurden von [SPORTident](https://www.sportident.com/) erfasst und sind als csv-Dateien verfügbar (oben rechts unter "Downloads" auf der jeweiligen Veranstaltungsseite)
* die von der SPORTident-Webseite heruntergeladenen csv-Dateien sind nicht UTF-8-kodiert
* die Ergebnislisten bis 2018 befinden sich im Ordner ``SI_results``

## Benutzung

* Repository klonen oder Archiv herunterladen und entpacken und ins entsprechende Verzeichnis wechseln
* Python-Interpreter starten

### Daten laden

```python
from analyze100miles import Results
res = Results(2014) # lädt die Daten des Jahres 2014
```

### Streckeninfo

```python
print(res.course_info)
```

#### Ausgabe

```
Verpflegungspunkte/Zeitmessung
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
VP    Split km  Abs km    Name
---------------------------------------------------------------------------------
VP1   7,3       7,3       Brandenburger Tor
VP2   6,46      13,76     East Side Gallery
[...]
VP27  3,02      157,94    Wollankstrasse
Ziel  3,96      161,9     Friedrich-Ludwig-Jahn-Sportpark
---------------------------------------------------------------------------------
```

### Durchlaufzeiten an den VPs

```python
res.vp_stats("VP5")

# Filtern nach Frauen/Männern/Staffeln
res.vp_stats("VP5", "f") 
res.vp_stats("VP5", "m") 
res.vp_stats("VP5", "r")

# Wie zuvor, Anzeige der ersten n Läufer (default 10, 0 für alle)
res.vp_stats("VP5", "f", 3) # listet die ersten 3 Männer 
res.vp_stats("VP5", "m", 20) # listet die ersten 20 Frauen
res.vp_stats("VP5", "r", 0) # listet alle Staffeln
res.vp_stats("VP5", "all", 0) # listet alle
```

#### Ausgabe

```
VP5 - U-Bahnhof Rudow - km 31,2
************************************************************************
Anzahl Läufer: 254

1.: 8:20:08 Uhr - Nagata, Tsutomu (239)
2.: 8:24:18 Uhr - Perkins, Mark (177)
3.: 8:25:07 Uhr - Bonfiglio, Marco (199)
4.: 8:26:24 Uhr - Morstabilini, luca (203)
5.: 8:27:00 Uhr - Tribius, Thomas (228)
6.: 8:38:49 Uhr - Brade, Benjamin (181)
7.: 8:38:55 Uhr - Klug, Matthias (216)
8.: 8:39:00 Uhr - Strykowski, Jaroslaw (135)
9.: 8:41:20 Uhr - Lingg, Dieter (210)
10.: 8:42:32 Uhr - Kuehner, Christof (268)

25 %:  9:13:54 Uhr
50 %:  9:35:07 Uhr
75 %:  9:53:32 Uhr
100 %: 11:07:10 Uhr (Läufer, Besen)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Split pace in min/km

1.:  4:54 (Bonfiglio, Marco)
2.:  5:03 (Perkins, Mark)
3.:  5:03 (Morstabilini, luca)
4.:  5:05 (Zugspitz Trailer)
5.:  5:09 (Nagata, Tsutomu)
************************************************************************
```

### Alle Durchlaufzeiten als Textdatei ausgeben

```python
res.stats_to_file()

# Filtern nach Frauen/Männern/Staffeln
res.stats_to_file("f") 
res.stats_to_file("m") 
res.stats_to_file("r")

# Wie zuvor, Anzeige der ersten n Läufer (default 0 für alle)
res.stats_to_filevp_stats("VP5", "f", 10) # listet jeweils die ersten 10
res.stats_to_filevp_stats("VP5", "m", 10)
res.stats_to_filevp_stats("VP5", "r", 10)
res.stats_to_filevp_stats("VP5", "all", 10)
```

### Ranking

```python
print(res.ranking)
```

### Ausgabe

```
Ranking
~~~~~~~
Platz StartNr Name                      Zeit       Kategorie
-----------------------------------------------------------------
1     177     Perkins, Mark             13:06:52   Senioren M30 (30-34 Jahre)
2     199     Bonfiglio, Marco          14:04:27   Senioren M35 (35-39 Jahre)
[...]
1     266     Seidel, Grit              18:16:29   Seniorinnen W40 (40-44 Jahre)
[...]
15    10000   Läufer, Besen             29:01:19   Staffel 4 x 40 km
[...]
```

### Läuferdetails

```python
res.runner_stats(100) # StartNr, siehe Ranking/Durchlaufzeiten
```

#### Ausgabe

```
Name: Deák, Andreas - Platz: 169
StartNr: 100 - Kategorie: Senioren M50 (50-54 Jahre)
Zeit: 28:23:58 - Pace: 10:35 min/km
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
VP    Split time Split pace Time (total)
VP1   01:04:55   7:11       1:04:55
VP2   00:41:11   6:53       1:46:06
[...]
VP26  01:02:08   10:52      27:10:19
VP27  00:30:12   9:46       27:40:31
Ziel  00:43:27   11:33      28:23:58
```

## Übertragbarkeit auf andere Veranstaltungen

* **ungetestet**
* da die csv-Dateien immer den gleichen Aufbau haben, sollte sich das Skript auch leicht an andere Veranstaltungen anpassen lassen:
  * ``vp_list.yaml``: Details der Messstationen anpassen/erstellen
  * ``analyze100miles.py``: Dictionary ``YEAR_COURSE`` entsprechend anpassen
  * csv-Datei(en) in ``/SI_results`` speichern
