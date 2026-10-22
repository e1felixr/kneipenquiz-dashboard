# Changelog

Alle nennenswerten Änderungen am Kneipenquiz-Tool werden hier festgehalten.

## v0.8.1 (22.10.2026, 13:11 Uhr)

### Behoben

- **Das Web-Dashboard zeigte wieder den aktuellen Stand** — seit dem 18.07.2026 lief es dem Werkzeug hinterher: Die Eingabe-GUI schrieb ihre `data.json` nach `%LOCALAPPDATA%\E1\Quiz\`, das veröffentlichte Dashboard liest aber die mitversionierte Datei aus dem Projektordner. Jeder seither erfasste Abend landete an einem Ort, den die Web-Ansicht nie sieht; sie stand auf acht Abenden (Apr 25 bis Mai 26), während das Werkzeug zehn kannte (bis Sep 26). Die Nutzerdaten liegen jetzt wieder im **Projektordner** — eine Quelle für Eingabe und Dashboard. Die EXE findet den Ordner über die OneDrive-Wurzel; ist er einmal nicht erreichbar, bleibt `%LOCALAPPDATA%` als Rückfall. Beim ersten Start übernimmt das Werkzeug einen noch an einem der drei früheren Orte liegenden Stand einmalig; das Original bleibt stehen.
- **Joker „(keiner)" im Dashboard** — die Rohdaten-Tabelle zeigt für einen Abend ohne gesetzten Joker „–", und die Joker-Auswertung zählt ihn als null Bonuspunkte statt auf einen leeren Kategorienamen zu greifen. Betraf bislang allein `Sep 26`, den ersten Abend ohne Joker.

### Verbessert

- **Kennzahl „Punkte pro Abend" statt „Gesamtpunkte"** — die Summe über alle Abende wuchs mit jedem Termin und sagte über die Leistung nichts. Die Karte trägt nun den Mittelwert, darunter Median und Spanne: beim derzeitigen Stand Ø 37,0 bei Median 37 und einer Spanne von 28 bis 47 Punkten. Mittelwert und Median fallen zusammen — kein einzelner Abend verzerrt den Durchschnitt.
- **Deutsche Zahlschreibweise in der Kennzahlen-Übersicht** — Ø Platzierung, Ø Teams, Kategorie-Mittelwerte und die Verbesserungs-Angabe tragen jetzt das Dezimalkomma (`7,8` statt `7.8`).

### Intern

- **Dashboard lädt nach einem neuen Abend ohne Neustart** — die Änderungszeit der `data.json` geht in den Cache-Schlüssel ein; vorher hielt `st.cache_data` den Stand des ersten Aufrufs fest.

## v0.8.0 (04.09.2026, 08:35 Uhr)

### Neu

- **Joker „(keiner)" wählbar** — beide Joker-Felder führen die Auswahl „(keiner)" an erster Stelle; ein Abend ohne gesetzten Joker lässt sich damit erfassen, ohne dass die Prüfung ihn abweist. Gespeichert wird ein solcher Joker als leer, in der Übersichtstabelle erscheint „–". Ein *leer gelassenes* Feld bleibt weiterhin ein Fehler — so fällt ein vergessener Joker auf, statt stillschweigend als „keiner" in die Daten zu wandern.

### Behoben

- **Verdoppelte Eingabe beim schnellen Tippen** — wer die nächste Taste drückte, ehe er die vorige losließ, erhielt Wortsalat wie „Verschiedenessch": die eingesetzte Ergänzung wurde vom nachlaufenden Tastendruck als eigene Eingabe gewertet, die Markierung verschwand und alles Weitere hängte sich hinten an. Als getippt gilt jetzt nur noch der Text vor der Markierung; fällt die Markierung dennoch fort, setzt das Feld den Überhang selbsttätig zurecht.

### Verbessert

- **Eingabeformular in zwei Reihen** — die vier Teile stehen als 2×2-Raster neben den Eckdaten statt in einer langen Spalte. Das Formular ist damit halb so hoch, und die Knöpfe „Speichern", „Zurücksetzen" und „Abbrechen" bleiben auch auf niedrigen Bildschirmen sichtbar — vormals schnitt sie der untere Fensterrand ab.
- **Abende-Liste nutzt den freien Raum** — sie wächst nun mit dem Fenster; auf einem großen Schirm sind rund zwanzig Abende ohne Scrollen zu überblicken statt acht.

### Intern

- **Versions-Konstante nachgezogen** — die im Kopf angezeigte Version stand noch auf `0.6.0` und folgt jetzt wieder dem Changelog.

## v0.7.0 (01.08.2026, 12:59 Uhr)

### Verbessert

- **Schnellerer Start: matplotlib lazy-loaded** — matplotlib und FigureCanvasTkAgg werden erst beim ersten Öffnen des Dashboard-Reiters geladen, nicht mehr beim Programmstart. Das reduziert die Ladezeit erheblich, da matplotlib und seine Abhängigkeiten (Figuren, Canvas, Zeichenpipeline) erst bedarfsgerecht initialisiert werden. Die Eingabe-GUI ist damit sofort bedienbar, der Dashboard-Reiter baut sich beim ersten Klick auf.

## v0.6.1 (24.07.2026, 00:22 Uhr)

### Behoben
- **Laufzeit-Daten lagen unter `%APPDATA%\Roaming` statt `%LOCALAPPDATA%`** — `_user_data_dir()` legte `data.json` seit v0.5.0 unter `%APPDATA%\E1\Quiz\` an (Roaming, servergespeichertes Profil); die Regel verlangt `%LOCALAPPDATA%` für Laufzeit-Daten, sonst schieben Roaming-Profile die Daten übers Netz. `_user_data_dir()` zeigt jetzt auf `%LOCALAPPDATA%\E1\Quiz\` (Fallback `~/AppData/Local`, falls die Variable fehlt). Die Einmal-Migration deckt jetzt beide Altorte ab: zuerst wie bisher neben EXE/Modul, danach zusätzlich den alten Roaming-Pfad `%APPDATA%\E1\Quiz\data.json` — beide Male wird nur kopiert, das Original bleibt stehen.

## v0.6.0 (18.07.2026, 12:26 Uhr)

### Neu

- **Fragezeichen-Logo** — die App trägt jetzt eine eigene Bildmarke: ein weißes Fragezeichen auf E1-Grün, im Stil der Schwestertools. Es erscheint im Kopfbereich neben dem Titel und ersetzt zugleich das bisherige Bier-Symbol als Fenster-, Taskleisten- und EXE-Icon. Erzeugt über `_logo_erzeugen.py` (PIL, einmaliger Lauf); im Header via `tk.PhotoImage` geladen — ohne PIL zur Laufzeit.
- **Kategorien tippen mit Live-Filter** — die Kategorie- und Joker-Felder im Eingabeformular sind nicht mehr nur auswählbar, sondern frei betippbar. Während des Tippens schrumpft die Vorschlagsliste auf die Treffer, und der erste passende Eintrag wird ergänzt (der Rest bleibt markiert). „ku" führt so unmittelbar zu „Kunst/Literatur". Rückschritt filtert nur, ohne zu ergänzen.

### Verbessert

- **Fenster startet maximiert** — die Eingabe-Oberfläche öffnet sich im Vollbild; die frühere Größe bleibt als Wiederherstellungsmaß erhalten.
- **Bereits vergebene Kategorien verschwinden** — wählt man eine Kategorie in einem Block, erscheint sie in den übrigen elf Slots gar nicht mehr. Da jede der zwölf Kategorien genau einmal gespielt wird, führt die Auswahl so Schritt für Schritt ans vollständige, widerspruchsfreie Formular.

### Intern

- **Versions-Konstante nachgezogen** — die im Kopf angezeigte Version stand noch auf `0.1.0`; sie folgt jetzt dem Changelog.
- **Build bündelt `logo.png`** — `build_exe.bat` kopiert die Bildmarke in den Build-Ordner und reicht sie als `--include-data-file` ins Onefile-Bundle, analog zum Icon.

## v0.5.0 (18.07.2026, 12:19 Uhr)

### Verbessert
- **Nutzerdaten nach %APPDATA% verlegt** — `data.json` liegt nun unter `%APPDATA%\E1\Quiz\` statt neben der EXE. Die Onefile-EXE bleibt damit eine eigenständige Datei ohne Begleitdateien. Eine noch am alten Ort liegende `data.json` wird beim ersten Start einmalig übernommen, damit keine Quizstände verloren gehen.

## v0.4.5 (18.07.2026, 12:02 Uhr)

### Intern
- **Auf Nuitka-Onefile migriert** — von PyInstaller-onedir; kleinere, einzelne EXE. Cache-gehärtet ({VERSION}). `data.json`- und Icon-Pfadauflösung um den Nuitka-`__compiled__`-Fall ergänzt (kein `sys.frozen`/`sys._MEIPASS` unter Nuitka); Icon-Pfad läuft jetzt über eine Kandidaten-Kaskade (PyInstaller-`_MEIPASS` → neben dem Modul → neben der EXE), analog zum Loriot-Vorbild. `app.py` (Streamlit-Dashboard) bleibt unverändert außerhalb des Bundles, nur als Datendatei neben der EXE für den manuellen System-Python-Aufruf.

## v0.4.4 (18.07.2026, 11:45 Uhr)

### Intern
- **Verfalls-Warnungen gefiltert** — FutureWarning/DeprecationWarning/PendingDeprecationWarning aus `quiz_eingabe` (matplotlib) werden in `start.py` per modul-verengtem Laufzeit-Filter am Einstieg unterdrückt; Warnungen aus fremdem Code bleiben sichtbar.

## v0.4.3 (16.07.2026, 14:39 Uhr)

### Intern
- **Windows-Versionsressource ergänzt** — EXE trägt jetzt CompanyName/FileVersion/ProductName über `make_version_info.py` + `--version-file` (PyInstaller `VSVersionInfo`). Explorer-Hover und Datei-Eigenschaften → Details zeigen künftig Firma und Version.

## v0.4.2 (14.07.2026, 11:11 Uhr)

### Intern
- **CI-Grün vereinheitlicht** — Primärgrün auf das aktuelle E1-Logo-Grün #66b32f umgestellt (zuvor #4a8f24).

## v0.4.1 (06.07.2026, 10:34 Uhr)

### Behoben

- **Defekte data.json konnte die komplette Historie kosten** — Ein Ladefehler (kaputtes JSON, Encoding, Rechte) führte bisher stillschweigend zu „0 Abende"; das nächste Speichern überschrieb die Datei unwiederbringlich. Jetzt wird bei einem Ladefehler automatisch eine Sicherungskopie `data.json.defekt_<Zeitstempel>` angelegt und eine Warnung angezeigt, ehe das Tool mit leerer Liste startet.

## v0.4.0 (28.05.2026, 21:35 Uhr)

### Verbessert

- **Konventions-Rename: Build `build_exe.bat`** — Build-Skript `build.bat` → `build_exe.bat`. UTF-8-Header in allen `.bat`-Skripten gesetzt, damit Box-Zeichen und Umlaute sauber rendern.

## v0.3.0 (28.05.2026, 13:18 Uhr)

### Neu

- **Reiter „Erkenntnisse"** — ein dritter Notebook-Reiter neben Eingabe und Dashboard. Acht thematische Sektionen — Form-Trend, Verläßliche Pfeiler, Wackel-Kandidaten, Joker-Bilanz, Joker-Empfehlung, Sonderrunde, Letzter Abend, Ausblick — leiten datengetriebene Beobachtungen und konkrete Empfehlungen aus dem aktuellen Datenstand ab. Bullets in drei Stilen: neutraler Punkt für Beobachtungen, grüner Pfeil für Empfehlungen, roter Pfeil für Warnungen. Scrollbar für längere Inhalte; Mausrad-Bindung global.
- **Datenmodul-Funktion `compute_insights`** — kapselt die gesamte Logik (Lernkurve, Kategorie-Mittelwerte und Streuung, Joker-Hitrates, Sonderrunden-Themenklassifikation, Konsolidierungs-Empfehlungen). Pure Funktion ohne externe Abhängigkeiten — gut testbar.
- **Sprachliche Politur** — die Texte des Erkenntnisse-Reiters sind vom Deutschlehrer-Agent lektoriert: ruhig, präzise, frei von Stelzen wie „eine spürbare Aufwärtsbewegung" oder „bei wahlweiser Sonderrunde". Begriffe wie „Trefferquote" und „klassische Bildungsthemen" sind reiterübergreifend einheitlich.

### Verbessert

- **Refresh-Verdrahtung erweitert** — der bestehende Tab-Switch-Mechanismus ruft `_refresh_insights` analog zu `_refresh_dashboard` auf; auch nach Speichern und Löschen wird der Erkenntnisse-Reiter aktualisiert.

## v0.2.0 (28.05.2026, 13:18 Uhr)

### Neu

- **Notebook mit zwei Reitern** — Eingabe und Dashboard wohnen unter einem Dach. Reiter „Eingabe" trägt das gewohnte Formular mit Tabelle und Live-Berechnung; Reiter „Dashboard" zeigt die Auswertung direkt im Tk-Fenster.
- **Dashboard-Reiter in matplotlib** — sechs KPI-Karten (Anzahl Abende, Ø Quote, beste Platzierung, Ø Platzierung, stärkste und schwächste Kategorie) und vier eingebettete Charts: Platzierung-und-Quote-Verlauf, Kategorie-Ranking, Heatmap (Kategorien × Monate), Stärke-vs-Konsistenz-Scatter. Eingebunden über `FigureCanvasTkAgg`; Aktualisierung beim Programmstart, nach jedem Save oder Delete und beim Wechsel auf den Reiter.
- **Datenmodul `compute_dashboard_data`** — eine reine Berechnungs-Funktion in `quiz_data.py`, die alle Aggregate für den Dashboard-Reiter liefert (KPIs, Trend, Ranking, Heatmap, Scatter).

### Verbessert

- **Header und Fenstertitel verkürzt** — „🍺 Kneipenquiz Schwabach" tritt an die Stelle von „Kneipenquiz Schwabach — Eingabe"; die Reiter tragen die jeweilige Funktion.
- **Launcher entfällt** — `start.py` schrumpft zu einer Bootstrap-Datei; den separaten Auswahldialog mit zwei Knöpfen braucht es nicht mehr.
- **EXE größer, dafür eigenständig** — `build.bat` schließt `matplotlib` und `numpy` ins Bundle ein (`--collect-data matplotlib`); die `Quiz.exe` wird dadurch deutlich umfangreicher, läuft aber ohne System-Python und ohne Streamlit. Die `app.py` (Streamlit-Version) bleibt im Repo für den manuellen Aufruf erhalten.

## v0.1.0 (28.05.2026, 13:18 Uhr)

### Neu

- **Eingabe-GUI als Tkinter-Tool** — `quiz_eingabe.py` löst die Excel-Pflege ab. Neue Quizabende lassen sich direkt in einer Desktop-Oberfläche im E1-Look anlegen, bearbeiten und löschen. Live-Berechnung von Teil-Summen, Gesamtpunkten und Quote; Validierung sorgt dafür, dass alle 12 Kategorien eindeutig sind und die Joker zu den gespielten Kategorien passen.
- **Datenmodul `quiz_data.py`** — kapselt das Lesen, Schreiben und Aggregieren von `data.json`. Atomarer Schreibvorgang (Temp-File + `os.replace`), dichte Rang-Vergabe in der Kategorien-Tabelle, automatische Ergänzung des `Datum`-Feldes (ISO `YYYY-MM-DD`) beim ersten Laden alter Einträge.
- **Launcher `start.py`** — kleiner Auswahldialog mit zwei Knöpfen (Eingabe / Dashboard). Ist der Haupteinstieg für die Projektverwaltung und EXE-fest: im gebauten EXE-Modus läuft die Eingabe-GUI inline weiter, das Dashboard wird über das System-Python aus dem `PATH` gestartet (Streamlit ist bewusst nicht im Bundle).
- **Build-Skript `build.bat`** — folgt dem etablierten Sechs-Schritt-Schema (`_buildlib.bat` aus `260507_Diverses`). PyInstaller `--onedir`, venv auf dem Desktop, EXE und `_internal\` wandern ins Quellverzeichnis zurück. Version aus `EXE_VERSION`-Variable der Projektverwaltung, Fallback `0.0.0`. Streamlit/Pandas/Plotly bewusst aus dem Bundle ausgeschlossen.
- **`quiz_data.py` EXE-fest** — `DATA_PATH` liegt im gebauten EXE-Modus neben der EXE, im Source-Modus neben dem Modul.
- **Bier-Icon als App-Symbol** — `icon.ico` aus dem 🍺-Emoji gerendert (sieben Größen, 16 bis 256 Pixel). Beide Tk-Fenster (Launcher und Eingabe-GUI) setzen es, `build.bat` reicht es als EXE-Ressource (`--icon`) und zusätzlich ins Bundle (`--add-data icon.ico;.`).

### Verbessert

- **Bonus wird automatisch berechnet** — der Joker-Bonus ergibt sich aus den gewählten Joker-Kategorien und ihren Punkten (≥ 3 Punkte verdoppeln die Kategorie, sonst verfällt der Joker). Das Eingabefeld ist entfallen; an seine Stelle tritt eine Live-Anzeige im Eingabeformular.
- **Combobox-Optik aufgehellt** — Hintergrund und Schrift der Kategorie-Dropdowns sind weiß auch im `readonly`-Zustand; die Auswahlliste hebt den Treffer in Corporate-Grün hervor. Wirkt nicht mehr „ausgegraut".
- **Type-ahead in den Kategorie-Comboboxen** — Tippen mehrerer Buchstaben in den Joker- und Slot-Comboboxen springt zur passenden Kategorie (`Ku` → Kunst/Literatur, `Wi` → Wissensch./Natur). Der Tasten-Puffer wird nach 800 ms Idle zurückgesetzt.
- **Tabelle übersichtlicher** — die Datum-Spalte ist entfallen; die Monat-Spalte zeigt den Monatsnamen ausgeschrieben („April 2026") und ist linksbündig.

### Behoben

- **`build.bat`: VSVersionInfo-Flags entfernt** — `--file-version` / `--product-version` sind keine direkten PyInstaller-Flags. Sie wurden aus dem `pyinstaller`-Aufruf gestrichen; die Versionierung kann später über eine `version.txt` mit `--version-file` nachgereicht werden.
- **`build.bat`: APPNAME auf `Quiz`** — die `.deploy.json` der Projektverwaltung erwartet `Quiz.exe`; entsprechend trägt die EXE nun diesen Namen statt `Kneipenquiz.exe`.

### Verbessert

- **Dashboard-Datenquelle** — `app.py` liest weiterhin `data.json`, weist im Footer nun aber `data.json` als Quelle aus statt `Kneipenquiz.xlsx`.

### Entfernt

- **`Kneipenquiz.xlsx` und `build_data.py`** — wurden ins Unterverzeichnis `_archiv/` verschoben. Das Konvertierskript wird nicht mehr gebraucht, weil die Eingabe-GUI direkt `data.json` schreibt. Die alte `start.bat` mit XLSX-Konvertierungsschritt wurde entfernt.
