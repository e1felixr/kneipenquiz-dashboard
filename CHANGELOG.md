# Changelog

Alle nennenswerten Änderungen am Kneipenquiz-Tool werden hier festgehalten.

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
- **Launcher `start.py`** — kleiner Auswahldialog mit zwei Knöpfen (Eingabe / Dashboard). Ist der Haupteinstieg für den Projektverwalter und EXE-fest: im gebauten EXE-Modus läuft die Eingabe-GUI inline weiter, das Dashboard wird über das System-Python aus dem `PATH` gestartet (Streamlit ist bewusst nicht im Bundle).
- **Build-Skript `build.bat`** — folgt dem etablierten Sechs-Schritt-Schema (`_buildlib.bat` aus `260507_Diverses`). PyInstaller `--onedir`, venv auf dem Desktop, EXE und `_internal\` wandern ins Quellverzeichnis zurück. Version aus `EXE_VERSION`-Variable des Projektverwalters, Fallback `0.0.0`. Streamlit/Pandas/Plotly bewusst aus dem Bundle ausgeschlossen.
- **`quiz_data.py` EXE-fest** — `DATA_PATH` liegt im gebauten EXE-Modus neben der EXE, im Source-Modus neben dem Modul.
- **Bier-Icon als App-Symbol** — `icon.ico` aus dem 🍺-Emoji gerendert (sieben Größen, 16 bis 256 Pixel). Beide Tk-Fenster (Launcher und Eingabe-GUI) setzen es, `build.bat` reicht es als EXE-Ressource (`--icon`) und zusätzlich ins Bundle (`--add-data icon.ico;.`).

### Verbessert

- **Bonus wird automatisch berechnet** — der Joker-Bonus ergibt sich aus den gewählten Joker-Kategorien und ihren Punkten (≥ 3 Punkte verdoppeln die Kategorie, sonst verfällt der Joker). Das Eingabefeld ist entfallen; an seine Stelle tritt eine Live-Anzeige im Eingabeformular.
- **Combobox-Optik aufgehellt** — Hintergrund und Schrift der Kategorie-Dropdowns sind weiß auch im `readonly`-Zustand; die Auswahlliste hebt den Treffer in Corporate-Grün hervor. Wirkt nicht mehr „ausgegraut".
- **Type-ahead in den Kategorie-Comboboxen** — Tippen mehrerer Buchstaben in den Joker- und Slot-Comboboxen springt zur passenden Kategorie (`Ku` → Kunst/Literatur, `Wi` → Wissensch./Natur). Der Tasten-Puffer wird nach 800 ms Idle zurückgesetzt.
- **Tabelle übersichtlicher** — die Datum-Spalte ist entfallen; die Monat-Spalte zeigt den Monatsnamen ausgeschrieben („April 2026") und ist linksbündig.

### Behoben

- **`build.bat`: VSVersionInfo-Flags entfernt** — `--file-version` / `--product-version` sind keine direkten PyInstaller-Flags. Sie wurden aus dem `pyinstaller`-Aufruf gestrichen; die Versionierung kann später über eine `version.txt` mit `--version-file` nachgereicht werden.
- **`build.bat`: APPNAME auf `Quiz`** — die `.deploy.json` des Projektverwalters erwartet `Quiz.exe`; entsprechend trägt die EXE nun diesen Namen statt `Kneipenquiz.exe`.

### Verbessert

- **Dashboard-Datenquelle** — `app.py` liest weiterhin `data.json`, weist im Footer nun aber `data.json` als Quelle aus statt `Kneipenquiz.xlsx`.

### Entfernt

- **`Kneipenquiz.xlsx` und `build_data.py`** — wurden ins Unterverzeichnis `_archiv/` verschoben. Das Konvertierskript wird nicht mehr gebraucht, weil die Eingabe-GUI direkt `data.json` schreibt. Die alte `start.bat` mit XLSX-Konvertierungsschritt wurde entfernt.
