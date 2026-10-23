# Changelog

Alle nennenswerten Änderungen am Kneipenquiz-Tool werden hier festgehalten.

## v0.11.0 (23.10.2026, 20:47 Uhr)

### Neu

- **Vierter Reiter „Gegner" — wie das eigene Ergebnis im Feld steht.** Grundlage sind die Ergebnistafeln von neun der elf Abende, ausgelesen aus den Fotos unter `Y:\2028 Kneipenquiz\Gesamtergebnisse`: 62 erfasste Schreibweisen, von Hand auf **45 Teams** zusammengeführt (Verschreiber, Groß- und Kleinschreibung, gekürzte und erweiterte Fassungen desselben Namens; sechs Zusammenlegungen hat Felix einzeln entschieden). Der Reiter zeigt je Abend den Rückstand zur Spitze, das Feldmittel, den Abstand dazu und eine Einstufung über den z-Wert (stark / durchschnittlich / schwach ab \|z\| ≥ 0,5), dazu eine Gegnerbilanz mit gemeinsamen Abenden, Siegen, Niederlagen und mittlerem Punktabstand. Zwei Abende — Jan 26 und Mai 26 — liegen nur als Zwischenstand **vor** der Joker-Vergabe vor; sie würden das ganze Feld systematisch zu schwach ausweisen und bleiben deshalb aus Trend, Bilanz und Einordnung draußen, erscheinen in der Tabelle aber grau mit Strichen.
- **Derselbe Vergleich im Web-Dashboard**, dort ausschließlich mit den Kennungen `T01` bis `T44`. Der Klarnamen-Schlüssel bleibt lokal und wird von `app.py` nicht eingelesen — das Repo ist öffentlich.
- **Ein Abend lässt sich vorab anlegen**, ehe er gespielt ist (Feld `Geplant`). Er steht in der Übersicht mit dem Zusatz „(geplant)" und zählt in **keiner** Auswertung mit — nicht in den Kennzahlen, nicht in den Kategorie-Mittelwerten, nicht im Gegner-Vergleich. Gegenprobe gelaufen: Mit und ohne den Eintrag für den 05.11.2026 („Pumuckl") liefern alle Kennzahlen und Erkenntnisse identische Werte.
- **Der Termin trägt jetzt einen Tag.** Das Eingabefeld heißt „Termin" und erfasst Tag, Monat und Jahr in deutscher Leserichtung; bisher schrieb das Formular hart den Monatsersten. Die elf gespielten Abende tragen seither ihr echtes Datum (24.04., 22.05., 17.07., 25.09.2025 sowie 30.01., 26.03., 23.04., 21.05., 16.07., 03.09. und 22.10.2026) — alles Donnerstage bis auf den 30.01.2026, der auf einen Freitag fiel. Quelle sind die Dateinamen der Ergebnisfotos. Das Datum ist dabei mehr als Zierde: Es verknüpft jeden Abend mit seiner Ergebnisliste und dient beim Bearbeiten und Löschen als Schlüssel.

### Verbessert

- **Die Vollansicht eines Diagramms vergrößert jetzt auch die Schrift.** Zuvor wuchs allein die Zeichenfläche auf das Vierfache, während Titel, Achsen und Werte in ihrer Rastergröße stehenblieben und darin verloren wirkten. Gelöst über die Figure-DPI (100 → 140): Mit ihr wachsen Schrift, Linienstärken und Marker gemeinsam, ohne dass die neunzehn einzeln gesetzten Schriftgrößen der vier Diagramme in zwei Fassungen gepflegt werden müssten. Zugleich werden die Ränder nachgezogen — sie sind in Anteilen der Figur bemessen und beanspruchten in der Vollansicht deshalb die doppelte Pixelzahl. Gemessen an der Heatmap bei 1852 × 909 px: links 113 px und unten 56 px zurück an die Zeichenfläche, die damit von 58 auf 71 Prozent der Figur wächst.

### Behoben

- **Die Zahlen in der Punkte-Heatmap sind auf dunklen Feldern wieder lesbar** (Eingabe-GUI und Web-Dashboard). Die Farbskala RdYlBu läuft an **beiden** Enden ins Dunkle — 0 Punkte in tiefem Blau, 5 Punkte in tiefem Rot —, die Ziffern standen aber durchgehend im dunklen Grau `#374151` und verschwanden dort fast. Ausgerechnet die aussagekräftigsten Felder waren betroffen: die perfekte Runde und der Totalausfall. Die Schriftfarbe richtet sich nun nach der Helligkeit der Zelle.

### Intern

- Die Ergebnislisten (`ergebnisse.json`) tragen zu vier Abenden einen **Nachtrag vom 23.10.2026**: Apr 26 und Jul 26 begründeten ihre Lesung noch gegen die inzwischen korrigierten Werte — in beiden Fällen behielt die Tafel recht, nicht die Erfassung. Bei Sep 26 war die Abweichung ein Versatz-Artefakt des schrägen Aufnahmewinkels; die scheinbar widersprüchlichen Platzziffern sind echte Gleichstände. Bei Jan 26 ist die offene Rückfrage beschieden: Der Abend bleibt als Zwischenstand draußen. Die ursprünglichen Befunde bleiben stehen — die Begründung ist das Protokoll der Auswertung, nicht ihr Ergebnis.
- Die Ergebnisfotos sind aussortiert: Von 19 Aufnahmen über elf Abende waren sieben Mehrfachaufnahmen desselben Abends (Sep 25 allein fünfmal). Sie liegen nun unter `_dubletten\` statt gelöscht zu sein — das Netzlaufwerk kennt keinen Papierkorb. `260130_000001.jpg` bleibt im Hauptordner: Es ist keine Dublette, sondern ein **zweiter** Zwischenstand desselben Abends. Die Rohdatei führt zu jeder Aufnahme ihren Ablageort und verweist nicht mehr auf den Dateinamen vor der Umbenennung.

## v0.10.0 (23.10.2026, 11:33 Uhr)

### Neu

- **Erster Reiter heißt „Übersicht" und trägt die Auswertung** — oben die Knöpfe „+ Neuer Abend", „Bearbeiten" und „Löschen", darunter die sechs Kennzahlen-Kacheln (aus dem Dashboard hierher umgezogen), darunter die Tabelle „Bisherige Abende" über die volle Breite. Ein Abend wird einmal im Monat eingetragen und dauert wenige Minuten, nachgesehen wird oft — die Eingabemaske besetzte den ersten Reiter bislang dauerhaft und drängte die Auswertung an den Rand.
- **Das Eingabeformular öffnet jetzt als eigenes Fenster**, nicht mehr als Hälfte des Reiters. Es erscheint über dem Hauptfenster (`transient`, `grab_set`), trägt den Abend im Titel („Neuer Abend" bzw. „Abend bearbeiten — <Monat>") und schließt nach dem Speichern. Gemessen: 672 × 936 px beim neuen Abend, 691 × 960 px beim Bearbeiten — beide ohne Rollbalken. Die Knöpfe heißen dort „💾 Speichern" und „✕ Abbrechen"; „↶ Formular leeren" ist entfallen, weil ein geschlossenes Fenster nichts zu leeren hat.
- **Jedes Diagramm im Dashboard lässt sich auf volle Reiterbreite schalten** („Vollansicht"), die anderen drei treten dabei zurück; ein Knopf führt zurück ins 2×2-Raster.
- **Die Tabelle führt den ganzen Abend auf**: zusätzlich zu Monat, Jokern, Sonderrunde und Platz nun die vier Teilsummen (T1 bis T4), die Spielpunkte, die Joker-Punkte, den Gesamtwert mit Joker und die Quote. Spaltenbreiten gemessen, Summe 1.231 px — maximiert passt das ohne Rollleiste, bei 1200×800 erscheint sie.

### Verbessert

- **Die Summe je Teil steht wie eine Additionsaufgabe** — doppelte Querlinie unter dem dritten Punktefeld, darunter die Summe in Fettschrift, genau unter den drei Punktzahlen.
- **Alle zwölf Kategoriefelder sind exakt gleich breit** — gemessen 504 px maximiert, 340 px bei 1200×800. Zuvor waren die drei Felder in Teil 1 schmaler, weil die dortige Kopfzeile „Punkte (0–5)" die Punkte-Spalte auseinanderzog.
- **Feldeinträge und Beschriftungen stoßen nicht mehr an den Rand ihres Kastens** — sieben Pixel Einzug, zentral im Stil hinterlegt; Zahlen in Feldern stehen zentriert; die linksbündigen Tabellenspalten tragen einen Zell-Einzug.
- **An jeder Punktzahl ist erkennbar, ob die Joker darin stecken.** Im Web-Dashboard nennt die Kachel „Punkte pro Abend" beide Werte; „Ø Richtig" und „Trend Quote" tragen „(ohne Joker)"; vier Kategorie-Diagramme und die Rohdaten-Spalten ebenso. In der Eingabe-GUI heißt der Ergebniswert „Gesamt (mit Joker)", die Tabelle trennt „Punkte" und „Gesamt m. Joker".

### Behoben

- **Beide Größen in den abgeleiteten Beobachtungen jetzt benannt** (`quiz_data.py`, speist Erkenntnisse-Reiter wie Web-Dashboard) — die Punkte **mit**, die Quote **ohne** Joker, bislang unbeschriftet im selben Satz: Wer „38 Punkte (56 %)" las, musste annehmen, die 56 Prozent bezögen sich auf die 38.
- **Datenkorrektur April 2026:** Die Ergebnistafel des Quizabends weist 44 Punkte auf geteiltem Platz 6 aus, erfasst waren 43 und Platz 7. Der Vergleich der vier Rundensummen zeigte die Abweichung in Teil 2 (9 statt 10); der fehlende Punkt wurde Wissensch./Natur zugeschrieben (1 → 2), weil die beiden anderen Kategorien dieses Teils bei 4 lagen und ein Punkt dort eine „perfekte Runde" erfunden hätte, die es nie gab. Der Joker-Bonus bleibt bei 8. Quote nun 60,0 %.
- **Datenkorrektur Juli 2026:** Hier irrte nicht die Tafel, sondern die Erfassung — die Tafel wies 29 Punkte aus, eingetragen waren 30. Felix hat die Runde nachgerechnet: Teil 4 bestand aus 3 + 2 + 2, erfasst war 3 + 2 + 3. Der Punkt zu viel saß bei Geschichte (3 → 2); Teil 4 fällt damit von 8 auf 7, die Spielpunkte von 26 auf 25, der Gesamtwert von 30 auf 29, die Quote auf 41,7 %. Der Joker-Bonus bleibt bei 4, die Platzierung bei 12 von 15 — Juli bleibt damit der schwächste Abend der Reihe.

### Intern

- Zwei Tk-Fallstricke beim Umbau gefunden und behoben: `winfo_reqheight()` einer frischen Toplevel war vor dem ersten vollen `update()` unzuverlässig, sodass das Fenster nach dem Öffnen sprang; und eine `<Configure>`-Bindung feuerte wegen gemeinsamer Bindtags für jedes Kind-Widget mit, wodurch ein winziges Zahlenfeld die Umbruchbreite der Hinweiszeile überschrieb und rund 55 px Leerraum erzeugte.
- Testläufe der Oberfläche starten ab sofort durchsichtig und außerhalb des sichtbaren Bereichs (`alpha 0`, Position off-screen, `PrintWindow` mit `PW_RENDERFULLCONTENT`) — zuvor sprang bei jeder Sichtprüfung ein maximiertes Fenster vor die laufende Arbeit.
- Die Fotos der Endergebnisse aller Teams (zwanzig Stück) sind ausgewertet und den elf Abenden zugeordnet; die vollständigen Ergebnislisten liegen als `_ergebnisse_roh.json` im Projektordner. Eine Datei trug ein falsches Datum im Namen und heißt nun `250925_000000.jpg`.
- **Fußnote für künftige Auswertungen — September 2026: hier irrte die Tafel, nicht die Erfassung.** Sie führte 34 Punkte und Platz 6, richtig sind 35 und Platz 5: Teil 4 bestand aus 4 + 4 + 4, die Tafel rechnete 11. Das Team hat nicht protestiert, offiziell gewertet wurde der Tafelwert; `data.json` führt gleichwohl die korrekten Zahlen. Die Fotoauswertung (`_ergebnisse_roh.json`) markiert die betroffene Zeile als fehlerhaft, damit ein späterer Vergleich mit den anderen Teams nicht über die Differenz stolpert — dort stammen alle Zahlen aus den Tafeln, und an diesem einen Abend ist die eigene Zeile um einen Punkt zu niedrig. Zusammen mit April und Juli zeigt sich: Die Tafel ist nicht pauschal die verlässlichere Quelle — zweimal irrte die Erfassung, einmal die Tafel.
- Ein Neubau der EXE steht weiterhin aus.

## v0.9.5 (23.10.2026, 09:40 Uhr)

### Verbessert

- **Eingabe-Reiter zweigeteilt** — bisher lag die Liste der bisherigen Abende oben über die volle Breite, darunter zog sich das Formular quer über den Schirm. Der Reiter teilt sich jetzt im Gewicht 11:9: links das Eingabeformular, rechts die Liste. Gemessen im maximierten Fenster brauchte das Formular links fast die ganze Höhe seiner Hälfte (974 von 980 Pixeln), während die Tabelle rechts mit ihren sechs schlanken Spalten nur rund 790 von 1030 verfügbaren Pixeln Breite füllte und unter der letzten Zeile 540 Pixel leer ließ.
- **Modus-Zeile ist jetzt die Überschrift der linken Hälfte** — fett, „Eingabe — Neuer Abend“ bzw. „Eingabe — Bearbeite Okt 26“. Darunter rollt bei Bedarf nur noch der Bereich mit Eckdaten und den vier Teilen untereinander; zuvor stand eine graue Kleinzeile über einem Rahmen namens „Eingabeformular“ — zwei Beschriftungen übereinander, von denen die eine nichts sagte und die andere überlesen wurde. Der Rahmentitel ist entfallen; er kostete genau die acht Pixel, an denen die Rollleiste auch im maximierten Fenster hängenblieb.
- **Erläuternder Hinweis im Bearbeiten-Modus** — unter der Modus-Zeile erscheint dort eine eigene, kleine Zeile: Die Kategorien werden beim Speichern neu auf die vier Teile verteilt, die Teil-Summen können sich dadurch verschieben. Beim Anlegen eines neuen Abends bleibt sie ausgeblendet.
- **Schrift und Tabellenzeilen gewachsen** — die Staffelung 8/9/10/14 pt, die aus dem engen Zweispalten-Layout stammte, ist auf 9/11/12/16 pt angehoben, dazu 14 pt fett für den neuen Gesamtstand; die Zeilenhöhe der Tabelle „Bisherige Abende“ wuchs von 22 auf 30 Pixel.
- **Größere Eingabefelder** — die Kategorie-Felder wachsen jetzt mit der Spaltenbreite statt fest 20 Zeichen zu messen (gemessen 503 Pixel maximiert, 338 Pixel bei 1200×800 — vorher fest 245 Pixel); die Joker-Comboboxen sind von 18 auf 24 Zeichen gewachsen, das Sonderrunden-Feld von 22 auf 28, das Monatsfeld von 8 auf 10.
- **Feldeinträge stoßen nicht mehr an den Rand** — Labels, Rahmenüberschriften, Eingabefelder, Auswahlfelder, Zahlenfelder und die Spaltenköpfe der Tabelle tragen jetzt einen waagrechten Innenabstand von 7 Pixeln an einer einzigen Stelle im Stil, statt wie bisher hart an die Kastenlinie zu stoßen — Text klebte links an ihr, Zahlen rechts. Der senkrechte Anteil bleibt bewusst bei 1 Pixel: Über zwanzig Formularzeilen hätte sich das sonst vervielfacht und die Rollleiste zurückgeholt (gemessen: Das Formular braucht dadurch 774 statt 773 Pixel, bleibt also innerhalb der 802 Pixel des Rollbereichs).
- **Zahlen in Feldern stehen zentriert** — Punkte (0–5), Platz, von und Jahr. In einem schmalen Feld klebte eine rechts- oder linksbündige Ziffer unweigerlich an einer der beiden Kanten.
- **Tabellenzellen tragen jetzt ebenfalls einen Einzug** — die vier linksbündigen Spalten Monat, Joker 1, Joker 2 und Sonderrunde. ttk kennt für die Datenzellen eines Treeview kein Innenpolster — ein Stil-Padding greift nur am Spaltenkopf —, darum steht der Einzug als vorangestelltes Leerzeichen, das die Spaltenbreiten mitmessen. Die zentrierten Zahlenspalten „Gesamt“ und „Platz / Von“ brauchen ihn nicht.
- **„+ Neuer Abend“ entfällt** — das Formular ist dauerhaft eingabebereit, startet mit dem laufenden Monat vorbelegt und steht nach jedem Speichern wieder leer. Ein Knopf, der einen ohnehin vorhandenen Zustand herstellte, war nur ein Zwischenschritt; den Modus „inaktiv“ gibt es damit nicht mehr.
- **„✕ Abbrechen“ entfällt, „↶ Zurücksetzen“ heißt jetzt „↶ Formular leeren“** — Abbrechen schaltete das Formular ab, was ohne den Aktivierungsknopf gegenstandslos wurde. „Formular leeren“ führt jetzt aus dem Bearbeiten-Modus zum neuen Abend zurück und hebt zugleich die Zeilenauswahl in der Liste auf.

### Behoben

- **Live-Quote mit Dezimalpunkt** — „% richtig: 56.4 %“ war die einzige Stelle der Oberfläche mit englischer Schreibweise. Sie steht jetzt mit Komma.
- **Ergebnis-Block und Modus-Zeile waren bei kleinerem Fenster unsichtbar** — beide lagen im Rollbereich des Formulars; bei 1200×800 sah man den Gesamtstand damit nicht, obwohl er laufend mitgerechnet wurde, und drückte „Speichern“, ohne zu erkennen, ob das einen neuen Abend anlegt oder einen vorhandenen überschreibt. Beide sind jetzt fest verankert — die Modus-Zeile oben, der Ergebnis-Block unmittelbar über den Aktionsknöpfen.
- **Ein Doppelklick in die Liste konnte ein gefülltes Formular ohne Rückfrage überschreiben** — eine Geste, mit der man gewöhnlich nur nachschaut, löschte sonst zwölf Kategorien und zwölf Punktwerte ohne Rückholmöglichkeit. „Bearbeiten“ und „Formular leeren“ fragen jetzt nach, wenn etwas zu verlieren ist; im Bearbeiten-Modus wird dafür gegen den geladenen Stand verglichen, damit die Rückfrage nur bei echten Änderungen kommt.
- **Die Tabellenspalten dehnten sich und schnitten dabei Inhalte ab** — bei 1200×800 maßen „Joker 1“ 76 und „Joker 2“ 68 Pixel, sichtbar standen dort „Geschicht“, „Geograph“, „Kunst/Lite“ — ohne Auslassungspunkte, der Verlust blieb also unbemerkt. Die Spalten haben jetzt feste, am längsten vorkommenden Inhalt gemessene Breiten; eine waagrechte Leiste erscheint, wenn sie nicht alle hineinpassen.
- **Die Quote im Ergebnis-Block klebte an der Gesamtsumme** — 385 Pixel Leere auf der einen, 20 auf der anderen Seite. Sie steht jetzt mittig zwischen Joker-Punkten und Gesamtstand (gemessen 267 zu 273 Pixel bei maximiertem Fenster).
- **Das Punktefeld war unbeschriftet, die Quote verschwieg ihren Nenner** — Teil 1 trägt jetzt die Kopfzeile „Kategorie“ und „Punkte (0–5)“ (die Rahmen 2 bis 4 erben die Lesart); die Quote lautet jetzt „% richtig: 56,7 % (von 60)“.

### Intern

- **Waagrechte Rollleiste der Tabelle nur bei Bedarf** — dafür war `before=self.tree` nötig: Der Baum ist mit `expand=True` zuerst gepackt und hätte sonst den ganzen Raum verbraucht — die Leiste galt als gepackt, bekam aber keine Höhe und blieb unsichtbar, obwohl 776 Pixel Spalten auf 475 Pixel Breite trafen.
- **Formular dichter gepackt** — die Zeilenabstände sind von 3 auf 2 Pixel verdichtet, der untere Abstand der Summenzeilen von 5 auf 2. Das Formular (nur noch Eckdaten und Teile, seit Ergebnis und Modus-Zeile fest verankert sind) braucht dadurch 774 statt vorher 809 Pixel und bleibt auch im Bearbeiten-Modus mit seiner zusätzlichen Hinweiszeile (19 Pixel) innerhalb der 802 Pixel des Rollbereichs — maximiert rollt also nichts.
- **Pauschales Spaltenpolster in `_spaltenbreite()` von 24 auf 18 Pixel gesenkt** — der Zell-Einzug steckt seit der neuen Konstante `ZELL_EINZUG` bereits in den gemessenen Proben selbst; ohne die Senkung summierten sich beide, und die Tabelle rollte waagrecht, obwohl sie passte. Gemessen: Spaltensumme 776 Pixel bei 800 Pixel Tabellenbreite (maximiertes Fenster) — keine waagrechte Leiste mehr; bei 1200×800 greift sie weiterhin.
- **Abschlussprobe bei abgefangenem `save_data`**: 21 von 21 Prüfungen bestanden — Autovervollständigung in allen vier Teilen, Rückfrage greift bei Eingaben und schweigt beim leeren Formular, Abbruch lässt die Eingaben stehen, Bearbeiten, Speichern eines vollständigen Abends (11 → 12 Einträge, Gesamt 42 bei 36 Punkten plus 6 Joker-Punkten), beide weiteren Reiter. `data.json` blieb unberührt.
- **Weitere Probe mit abgefangenem Speichern zum Zell-Einzug**: 9 von 9 Prüfungen bestanden. Der Einzug wirkt nur in der Anzeige — Monat und Sonderrunden-Thema werden ohne führendes Leerzeichen gespeichert, und das Bearbeiten findet seinen Abend weiterhin über die Zeilenkennung, nicht über die Zellwerte. `data.json` blieb unberührt.
- **Ein Neubau der EXE steht aus** — `VERSION` ist auf 0.9.5 gezogen, die gebaute `Quiz.exe` trägt noch 0.9.3.0.

## v0.9.4 (23.10.2026, 08:32 Uhr)

### Verbessert

- **Kennzahlen-Karten im Web-Dashboard zu zweit auf dem Telefon** — einspaltig gestapelt lagen zehn Karten à 165 Pixel vor dem ersten Diagramm: ein gemessener Scrollweg von 2.208 Pixeln, also zweieinhalb Telefon-Bildschirme, ehe überhaupt eine Grafik erschien. Auf Telefonbreite (≤ 768 px) stehen die Karten jetzt zu zweit nebeneinander, der Scrollweg sinkt auf 1.078 Pixel — fünf Reihen statt zehn. Diagramm-Spalten bleiben gestapelt, ihnen fehlt bei halber Breite die Lesbarkeit. Umgesetzt mit dem CSS-Selektor `:has()`; kennt ein Browser ihn nicht, bleibt es beim bisherigen Stapeln.
- **Kopfabstand auf dem Telefon verkürzt** — Streamlits Standardabstand von 6rem vor dem Titel kostete mobil einen halben Bildschirm; er ist auf 1,2rem gesetzt, die erste Karte beginnt nun bei 199 statt 276 Pixel.
- **Kennzahlen-Karten mobil einheitlich hoch** — alle zehn Karten messen jetzt 140 Pixel. Die Karte „Perfekte Runden" trug eine mehrzeilige Aufzählung und war als einzige höher (140 gegen 118 Pixel) — derselbe Reihenbruch, der am Schirm bereits in v0.9.3 behoben wurde.
- **Kartenwert „Wissensch./Natur" lief über den Rand** — die Werteschrift ist mobil auf 1,1rem verkleinert und darf umbrechen, damit auch der längste Kennzahlen-Wert innerhalb seiner Karte bleibt.

### Behoben

- **Diagrammtitel auf dem Telefon abgeschnitten** — der Titel des gestapelten Kategorie-Diagramms lief auf 390 Pixel Telefonbreite bis 505 Pixel und war damit rechts abgeschnitten. Er heißt jetzt „Monatssumme nach Kategorie" statt „Punkte je Kategorie und Monat (feste Reihenfolge, stärkste unten)"; was der Zusatz erklärte, steht ohnehin im Fließtext unter dem Diagramm.
- **Legende verdeckte die Monatsnamen** — dieselbe Legende saß relativ zur Zeichenfläche (y = −0,12); elf Einträge brauchten dort auf dem Telefon drei Zeilen statt der einen, die am Schirm reicht, und verdeckten die Monatsnamen vollständig. Sie ist jetzt am unteren Figurenrand verankert (`yref="container"`), der Abstand bleibt damit in jeder Breite gleich.
- **Platzierungsbeschriftungen kollidierten mit Balken und Linie** — im Diagramm „Platzierung & Quote pro Quizabend" rückten die Beschriftungen („7. / 16" usw.) auf 358 Pixel Breite so eng zusammen, dass sie auf Balken und Linie zu liegen kamen. Sie stehen jetzt auf hellem Grund.
- **Graue Schrift auf grauem Grund an vier Stellen** — gemessen am WCAG-Kontrast (Grenze 4,5:1): die Fußzeile mit 2,2:1 (#9ca3af), Kopf-Unterzeile und sämtliche Erläuterungstexte unter den Diagrammen mit 4,1:1 (#6b7280 auf dem Seitengrund #ebedf0) sowie die Farbquadrate der Themenart-Legende mit 1,8:1. Alle Texte stehen jetzt in #4b5563 (5,9:1); die Farbquadrate sind Farbflächen mit Kontur statt eingefärbter Schriftzeichen, womit die Farbtreue zum Diagramm erhalten bleibt.
- **Themenart „übrige" grau auf grau im Sonderrunden-Diagramm** — das Hellgrau #bab0ac taugte als Balkenfarbe, erreichte als Schriftfarbe der Themennamen aber nur 2,2:1 gegen Weiß; „Landkreise in Mittelfranken", „Biene Maja" und „14 Achttausender" standen damit grau auf grau. Die Farbe ist jetzt #6f6a65.
- **Weiße Beschriftung in hellen Stapelsegmenten unlesbar** — die Beschriftung stand durchweg in Weiß, auch auf den hellen Tönen der Palette (Gelb, Grau, Rosa, Hellblau: 1,6 bis 2,3:1). Eine neue Funktion `_lesefarbe()` wählt je Fläche nach WCAG-Kontrast zwischen Weiß und Dunkelgrau.

### Intern

- **Sichtgeprüft mit Playwright in beiden Breiten (390×844 Telefon, 1920×1080 Schirm)** — die Kontraste aller Textelemente maschinell gemessen, danach null Verstöße auf Telefon wie Schirm. `streamlit.testing.v1.AppTest` läuft ohne Ausnahme durch (38 Markdown-Blöcke, ein Aufklapper, eine Tabelle). Am Schirm unverändert: Karten 165 Pixel, kein Element über die Fensterbreite hinaus.

## v0.9.3 (22.10.2026, 15:27 Uhr)

### Behoben

- **Symbolnamen statt Pfeilen** — im Aufklapper und am Sidebar-Umschalter stand Klartext wie `keyboard_arrow_right`. Streamlit zeichnet seine Symbole nicht als Zeichen, sondern als Ligaturen der Schrift „Material Symbols Rounded": Im Element steht der Name, den erst die Schrift zum Pfeil zusammenzieht. Die Schriftregel ganz oben im Stylesheet (`*` mit `!important`) nahm den Symbolen diese Schrift — und damit blieb der Name stehen. Der Fehler lag von Anfang an im Stylesheet; sichtbar wurde er erst mit dem Rohdaten-Aufklapper aus v0.9.0.
- **Stapeldiagramm zeigte das Gegenteil seines Titels** — „stärkste unten" versprach der Titel, tatsächlich lag Aktuelles (Ø 3,3) ganz oben und Wissensch./Natur (Ø 2,2) an der Nulllinie. Eine Umkehrung zu viel. Die stärkste Kategorie steht jetzt unten, wo sich am besten ablesen lässt.

### Verbessert

- **Kennzahlen-Karten sind gleich hoch** — „Trend Richtig-Quote" und „Ø Feldposition" brachen als einzige um und standen dadurch 22 Pixel höher als ihre Nachbarn. Das Label heißt nun kurz „Trend Quote", die Spanne bricht nicht mehr am Gedankenstrich, und alle zehn Karten messen einheitlich 165 Pixel.
- **Sonderrunden-Themenart auch bei null Punkten erkennbar** — die Färbung saß auf den Balken, doch gerade die klassischen Themen haben null Punkte und damit gar keinen Balken, der Farbe tragen könnte. Die Themenart steht jetzt auf der Beschriftung: Die drei rotbraunen Namen stehen allesamt bei null.
- **Erkenntnisse mit Dezimalkomma** — die abgeleiteten Beobachtungen schrieben „Ø 3.2" und „σ 0.90", während das übrige Dashboard Komma setzt. 14 Stellen in `compute_insights()` umgestellt; der Erkenntnisse-Reiter der Eingabe-GUI liest dieselben Texte und profitiert mit.

### Intern

- Sichtgeprüft im Browser (Playwright, Chromium 145): Kartenhöhen gemessen, alle sieben Diagramme und die Erkenntnis-Karten angesehen. Die beiden Befunde oben waren nur am Bild zu erkennen, nicht am Code.

## v0.9.2 (22.10.2026, 15:03 Uhr)

### Verbessert

- **Spalte „Bonus" heißt jetzt „Joker-Pkt."** — der Wert entsteht ausschließlich aus den Jokern (Verdopplung der Joker-Kategorie, sofern dort mindestens 3 Punkte fielen); „Bonus" las sich dagegen wie eine eigene Bonusrunde. Nicht einfach „Joker", weil daneben bereits „Joker 1" und „Joker 2" stehen — die tragen Kategorien, diese Spalte Punkte. Die Fußzeile erklärt die Regel nun mit: zwei Joker à 5 Punkte, Verdopplung erst ab 3 Richtigen, darunter verfällt der Joker.
- **Kein nacktes „Bonus" mehr im Dashboard** — auch die Achsenbeschriftungen des gestapelten Kategorie-Diagramms und der Joker-Auswertung sprechen von Joker-Punkten. Die Eingabe-GUI nannte es mit „Bonus (aus Joker)" von jeher richtig.

## v0.9.1 (22.10.2026, 14:59 Uhr)

### Verbessert

- **Heatmap ohne Farbleiste** — sie kennt nur sechs mögliche Werte, und jeder steht als Ziffer in seiner Zelle; eine Skala daneben erklärte nichts, was nicht schon dasteht, und nahm der Heatmap Breite, die ihr in einer halben Spalte fehlt. Der Titel nennt den Wertebereich jetzt selbst: „Punkte je Kategorie und Monat (0 bis 5)".

### Intern

- **Versionsschranken in `requirements.txt`** — die Streamlit Cloud löst die Datei bei jedem Build neu auf und zog bislang ohne Obergrenze stets die neuesten Fassungen. Lokal läuft plotly 5.18, im Deployment 7.1 — zwei Hauptversionen Unterschied, von denen keine Prüfung etwas merkte. Die Untergrenzen bleiben niedrig, damit ein lokales Setup nichts nachziehen muss; neu sind Obergrenzen je Hauptversion, damit ein Sprung auf plotly 8 oder pandas 4 das Deployment nicht unbemerkt bricht.
- **Gegen die Cloud-Fassungen erprobt** — in einer gesonderten Wegwerf-Umgebung mit streamlit 1.66.1, plotly 7.1.0, pandas 3.1.0 und numpy 2.5.4 läuft das Dashboard ohne Ausnahme durch, mit denselben Elementen wie lokal.

## v0.9.0 (22.10.2026, 14:49 Uhr)

### Neu

- **Erkenntnisse jetzt auch im Web-Dashboard** — acht Abschnitte mit dreißig abgeleiteten Beobachtungen (Form-Trend, verlässliche Pfeiler, Wackel-Kandidaten, Joker-Bilanz und -Empfehlung, Sonderrunden-Muster, letzter Abend, Ausblick). Sie stammen aus derselben `compute_insights()`, die den Erkenntnisse-Reiter der Eingabe-GUI speist — eine Quelle, zwei Darstellungen, keine doppelte Pflege. Die Abschnitte verteilen sich auf zwei Spalten nach Länge, nicht abwechselnd, damit keine Spalte deutlich länger gerät als die andere.
- **Sonderrunden nach Themenart eingefärbt** — die Balken tragen nun die Art des Themas statt noch einmal die Punktzahl, die ihre Länge ohnehin zeigt. Damit springt das deutlichste Muster im Datensatz ins Auge: Klassische Bildungsthemen (Dürer, Sixtinische Kapelle, Erdmond) brachten dreimal null Punkte, Popkultur im Mittel vier von fünf. Die Einteilung kommt aus `_classify_theme()` in `quiz_data.py`.

### Verbessert

- **Kennzahl „Ø Feldposition" statt „Ø Platzierung"** — die alte Angabe von 7,8 bedeutete nichts, weil die Teamzahl zwischen 10 und 16 schwankt: Platz 7 von 16 ist oberes Drittel, Platz 10 von 10 ist der letzte. Die Karte zeigt jetzt die Position im Feld in Prozent — 0 % wäre der Sieg, 100 % der letzte Platz. Beim derzeitigen Stand sind es 55 %, also eine Handbreit unter der Mitte; die alte Angabe steht als Unterzeile daneben.
- **Kategorie-Entwicklung endlich verfolgbar** — das gestapelte Diagramm sortierte die Kategorien in jedem Monat neu, womit jede von ihnen monatlich die Position im Stapel wechselte und sich keine über die Zeit verfolgen ließ — ausgerechnet das, wofür das Diagramm da ist. Reihenfolge und Farbe stehen nun über alle Monate fest, die stärkste Kategorie unten, dazu eine Legende.
- **Rohdaten in einem Aufklapper** — die Tabelle mit dreizehn Spalten ist auf einem Telefon nicht zu lesen und schob dort alles Wesentliche nach unten. Sie bleibt einen Klick entfernt.

### Behoben

- **Auf dem Telefon wurde jedes Diagramm beschnitten** — die mobile Gestaltung deckelte alle Diagramme auf 300 Pixel Höhe, während das niedrigste 400 und die höchsten 500 Pixel messen. Betroffen war ausnahmslos jedes der sieben. Der Deckel ist fort; die Höhen stehen jetzt an einer Stelle als `CHART_H` und `CHART_H_TALL`, statt siebenmal einzeln im Code.

### Intern

- **Tabelle „Punkte pro Kategorie und Monat" entfernt** — sie zeigte dieselbe Matrix aus elf Kategorien und zehn Monaten wie die Heatmap darunter, nur als Ziffern statt als Muster. Die Heatmap bleibt.
- **Fortschrittsleiste der Gesamtpunkte misst gegen 70** statt gegen 50 — erreichbar sind 60 Punkte aus den Teilen 1 bis 4 plus 10 Bonuspunkte; bei einem künftigen Abend über 50 wäre die Leiste sonst am Anschlag gestanden.
- Verifiziert mit `streamlit.testing.v1.AppTest`: Das Skript läuft vollständig durch, keine Ausnahme, fünf Abschnitte, ein Aufklapper, eine Tabelle.

## v0.8.3 (22.10.2026, 14:36 Uhr)

### Verbessert

- **Sonderrunden-Diagramm wieder lesbar** — zehn Themennamen standen waagerecht nebeneinander unter zehn Balken und überschrieben einander bis zur Unkenntlichkeit; „Albrecht Dürer", „Sixtinische Kapelle" und „Spongebob" verschmolzen zu einem Strich, und welcher Balken zu welchem Abend gehörte, war nicht mehr auszumachen. Die Balken liegen jetzt waagerecht, Thema und Monat stehen auf der senkrechten Achse — dort können sie sich nicht überlagern. Die Zeitreihe liest sich von oben nach unten, der älteste Abend zuerst.

### Intern

- **Versions-Konstante nachgezogen** — stand noch auf `0.8.1` und folgt wieder dem Changelog.
- **Abschlussmeldungen des Bauskripts berichtigt** — `build_exe.bat` behauptete noch, `data.json` müsse neben der EXE liegen. Das galt bis v0.4.5; seit v0.8.1 liegt sie im Projektordner, den die EXE über die OneDrive-Wurzel auflöst. Die Meldung nennt nun den richtigen Ort samt Grund.

## v0.8.2 (22.10.2026, 14:27 Uhr)

### Verbessert

- **Konsistenz-Diagramm pflegt sich selbst** — „Stärke vs. Konsistenz" setzte elf Kategorienamen als freischwebende Schilder ins Bild, deren Position für jede Kategorie von Hand als Pixel-Verschiebung eingetragen war. Die Punkte wandern aber mit jedem Quizabend: Die Rangfolge nach Streuung hat sich seit dem Eintragen umgeworfen (Aktuelles von Platz 7 auf 4, Geschichte von 3 auf 5, Sport von 10 auf 8), womit die Schilder Überschneidungen auswichen, die es nicht mehr gab, und in neue hineinliefen. Das Diagramm heißt nun **„Verlässlichkeit je Kategorie"** und stellt die Namen auf die senkrechte Achse, sortiert nach Streuung — verlässlichste oben. Je Kategorie zeigt es den Mittelwert als Punkt, ±σ als Balken und die beobachtete Spanne vom schlechtesten bis zum besten Abend als helle Linie; die Farbe trägt die Stärke in denselben Stufen wie das Ranking daneben. Die Aussage bleibt vollständig, nur ist keine Handarbeit nach einem neuen Abend mehr nötig.

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
