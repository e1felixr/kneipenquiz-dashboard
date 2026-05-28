"""Datenmodul fuer die Kneipenquiz-Eingabe-GUI.

Single source of truth ist data.json im selben Verzeichnis. Dieses Modul
kapselt Laden, Speichern, Validieren und das Berechnen der abgeleiteten
Aggregat-Bloecke (months, categories). Die GUI ruft hier rein.
"""
import json
import os
import pathlib
import sys
import tempfile
from datetime import datetime

# Im EXE-Modus liegt data.json neben der EXE; im Source-Modus neben dem Modul.
if getattr(sys, "frozen", False):
    HERE = pathlib.Path(sys.executable).parent
else:
    HERE = pathlib.Path(__file__).parent
DATA_PATH = HERE / "data.json"

GERMAN_MONTHS = ["Jan", "Feb", "Mrz", "Apr", "Mai", "Jun",
                 "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
GERMAN_MONTHS_LONG = ["Januar", "Februar", "März", "April", "Mai", "Juni",
                     "Juli", "August", "September", "Oktober", "November", "Dezember"]

# Fester Kategorien-Kanon. Reihenfolge = Anzeige-Reihenfolge in Comboboxen.
CATEGORIES = [
    "Aktuelles", "Essen/Trinken", "Film/Fernsehen", "Geographie",
    "Geschichte", "Kunst/Literatur", "Musik", "Rel./Mythol.",
    "Sonderrunde", "Sport", "Verschiedenes", "Wissensch./Natur",
]

# Schlagwortlisten fuer die grobe Klassifikation der Sonderrunden-Themen.
# Bewusst schlicht; trifft die typischen Felle der bisherigen Themen.
CLASSICAL_KEYWORDS = [
    "Dürer", "Sixtin", "Kapelle", "Erdmond", "Mond", "Bibel", "Antike",
    "Mythos", "Reformation", "Renaissance", "Kant", "Goethe", "Schiller",
    "Beethoven", "Bach", "Mozart", "Schubert", "Manet", "Monet", "Van Gogh",
    "Caravaggio", "Michelangelo", "Picasso", "Astronomie", "Philosoph",
]
POPCULTURE_KEYWORDS = [
    "Bond", "Loriot", "Spongebob", "Wolken", "DDR", "Star Wars", "Marvel",
    "Disney", "Simpsons", "Tatort", "Schlager", "Olympia", "Bundesliga",
    "Eurovision", "Schlumpf", "Pokémon", "Fernseh", "Comic", "Asterix",
]


def format_monat(year, month):
    """Gibt den Monat als Anzeige-String zurueck, z.B. 'Apr 26' fuer April 2026."""
    return f"{GERMAN_MONTHS[month - 1]} {str(year)[-2:]}"


def format_monat_long(year, month):
    """Gibt den Monat ausgeschrieben zurueck, z.B. 'April 2026'."""
    return f"{GERMAN_MONTHS_LONG[month - 1]} {year}"


def iso_to_monat_long(iso_str):
    """Wandelt ein ISO-Datum '2026-04-01' in 'April 2026' um."""
    dt = datetime.strptime(iso_str[:10], "%Y-%m-%d")
    return format_monat_long(dt.year, dt.month)


def compute_bonus(joker1, joker2, cat_scores):
    """Bonus = Verdopplung der Joker-Kategorie, sofern >=3 Punkte; sonst 0.

    Spiegelt die Regel aus dem bestehenden Dashboard: ein Joker bringt
    seine Kategorie-Punkte als Bonus genau dann, wenn das Team in dieser
    Kategorie mindestens 3 Punkte erreicht hat. Sonst verfaellt der Joker.
    """
    def _b(joker):
        s = cat_scores.get(joker, 0) if joker else 0
        return s if s >= 3 else 0
    return _b(joker1) + _b(joker2)


def parse_monat_to_iso(monat_str):
    """Wandelt einen Anzeige-String wie 'Apr 26' in ein ISO-Datum '2026-04-01' um."""
    parts = monat_str.strip().split()
    if len(parts) != 2:
        raise ValueError(f"Ungueltiges Monat-Format: {monat_str!r}")
    mon_str, yr_str = parts
    if mon_str not in GERMAN_MONTHS:
        raise ValueError(f"Unbekannter Monatsname: {mon_str!r}")
    month = GERMAN_MONTHS.index(mon_str) + 1
    try:
        year_short = int(yr_str)
    except ValueError:
        raise ValueError(f"Ungueltiges Jahr in Monat-String: {yr_str!r}")
    year = 2000 + year_short if year_short < 100 else year_short
    return f"{year:04d}-{month:02d}-01"


def iso_to_monat(iso_str):
    """Wandelt ein ISO-Datum '2026-04-01' in den Anzeige-String 'Apr 26' um."""
    dt = datetime.strptime(iso_str[:10], "%Y-%m-%d")
    return format_monat(dt.year, dt.month)


def load_data():
    """Laedt data.json und ergaenzt fehlende Datum-Felder im Speicher (ohne Datei zu aendern)."""
    if not DATA_PATH.exists():
        return {"months": [], "categories": [], "quiz_nights": []}
    with DATA_PATH.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    quiz_nights = data.get("quiz_nights", [])
    for night in quiz_nights:
        if "Datum" not in night and "Monat" in night:
            try:
                night["Datum"] = parse_monat_to_iso(night["Monat"])
            except ValueError:
                night["Datum"] = None
    data["quiz_nights"] = quiz_nights
    return data


def save_data(quiz_nights):
    """Sortiert die Abende, regeneriert Aggregat-Bloecke und schreibt data.json atomar."""
    sorted_nights = sorted(
        quiz_nights,
        key=lambda n: n.get("Datum") or parse_monat_to_iso(n.get("Monat", "Jan 00")),
    )
    months = [n["Monat"] for n in sorted_nights if "Monat" in n]
    categories = compute_categories(sorted_nights, months)
    payload = {
        "months": months,
        "categories": categories,
        "quiz_nights": sorted_nights,
    }
    json_bytes = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    dir_path = str(DATA_PATH.parent)
    fd, tmp_path = tempfile.mkstemp(dir=dir_path, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(json_bytes)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_path, str(DATA_PATH))
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def compute_categories(quiz_nights, months):
    """Berechnet den Aggregat-Block fuer alle Kategorien aus den Quizabenden."""
    result = []
    totals = {}
    for cat in CATEGORIES:
        total = sum(
            night.get("cat_scores", {}).get(cat, 0)
            for night in quiz_nights
        )
        totals[cat] = total

    num_months = len(months)

    # Dichte Rang-Vergabe (keine Luecken)
    sorted_totals = sorted(set(totals.values()), reverse=True)
    rank_map = {score: i + 1 for i, score in enumerate(sorted_totals)}

    for cat in CATEGORIES:
        total = totals[cat]
        mittelwert = total / num_months if num_months > 0 else 0
        entry = {
            "Kategorie": cat,
            "Punkte_gesamt": total,
            "Mittelwert": mittelwert,
        }
        for monat in months:
            cat_total_for_month = 0
            for night in quiz_nights:
                if night.get("Monat") == monat:
                    cat_total_for_month += night.get("cat_scores", {}).get(cat, 0)
            entry[monat] = cat_total_for_month
        entry["Platz"] = rank_map[total]
        result.append(entry)

    return result


def quiznight_from_form(form):
    """Erstellt einen vollstaendigen quiz_night-Eintrag aus den Formulardaten."""
    year = form["year"]
    month = form["month"]
    monat = format_monat(year, month)
    datum = f"{year:04d}-{month:02d}-01"

    teile = form["teile"]
    teil_sums = [sum(slot["punkte"] for slot in block) for block in teile]

    cat_scores = {}
    for block in teile:
        for slot in block:
            kat = slot["kategorie"]
            cat_scores[kat] = cat_scores.get(kat, 0) + slot["punkte"]

    # Bonus wird nicht eingegeben, sondern aus den Jokern berechnet.
    bonus = compute_bonus(form.get("joker1"), form.get("joker2"), cat_scores)
    gesamt = sum(teil_sums) + bonus
    pct_richtig = sum(teil_sums) / 60.0

    entry = {
        "Datum": datum,
        "Monat": monat,
        "Joker1": form["joker1"],
        "Joker2": form["joker2"],
        "Sonderrunde_Thema": form["sonderrunde_thema"],
        "Teil1": teil_sums[0],
        "Teil2": teil_sums[1],
        "Teil3": teil_sums[2],
        "Teil4": teil_sums[3],
        "Bonus": bonus,
        "Gesamt": gesamt,
        "Pct_richtig": pct_richtig,
        "Platzierung": form.get("platz"),
        "Von": form.get("von"),
        "cat_scores": cat_scores,
    }
    return entry


def compute_dashboard_data(quiz_nights):
    """Aggregiert KPIs und Plotdaten fuer den Dashboard-Reiter.

    Bei leerer Eingabe liefert die Funktion ein dict mit leeren Listen
    und None-Werten -- die GUI muss damit umgehen koennen.

    Rueckgabe: dict mit den Schluesseln
      "kpis"     -> dict (siehe unten)
      "trend"    -> dict mit "monate" (list[str]), "pct" (list[float]),
                    "placements" (list[int|None]), "von" (list[int|None]),
                    "gesamt" (list[int])
      "ranking"  -> list[(kategorie, mittelwert)] absteigend nach Mittelwert,
                    OHNE 'Sonderrunde'
      "heatmap"  -> dict mit "monate" (list[str]), "kategorien" (list[str],
                    aufsteigend nach Mittelwert, also schwaechste oben),
                    "matrix" (list[list[int]] -- aussen kategorien, innen monate),
                    OHNE 'Sonderrunde'
      "scatter"  -> list[(kategorie, mittelwert, std)] OHNE 'Sonderrunde'
    """
    from statistics import mean, pstdev

    # --- Edge case: leere Eingabe ---
    if not quiz_nights:
        return {
            "kpis": {
                "n_abende": 0,
                "first_monat": None,
                "avg_pct": 0.0,
                "best_placement": None,
                "best_placement_monat": None,
                "best_placement_von": None,
                "avg_placement": None,
                "avg_teams": None,
                "best_cat": None,
                "best_cat_avg": None,
                "worst_cat": None,
                "worst_cat_avg": None,
            },
            "trend": {
                "monate": [],
                "pct": [],
                "placements": [],
                "von": [],
                "gesamt": [],
            },
            "ranking": [],
            "heatmap": {
                "monate": [],
                "kategorien": [],
                "matrix": [],
            },
            "scatter": [],
        }

    # --- Chronologisch sortierte Abende ---
    def _sort_key(night):
        d = night.get("Datum")
        if d:
            return d
        try:
            return parse_monat_to_iso(night.get("Monat", "Jan 00"))
        except ValueError:
            return "9999-99-99"

    sorted_nights = sorted(quiz_nights, key=_sort_key)
    monate_list = [n["Monat"] for n in sorted_nights]

    # --- Kategorie-Mittelwerte (ohne Sonderrunde) ---
    cats_no_sonder = [c for c in CATEGORIES if c != "Sonderrunde"]

    def _cat_scores_list(kat):
        return [n.get("cat_scores", {}).get(kat, 0) for n in sorted_nights]

    cat_avgs = {kat: mean(_cat_scores_list(kat)) for kat in cats_no_sonder}

    # --- KPIs ---
    placements = [n["Platzierung"] for n in sorted_nights if n.get("Platzierung") is not None]
    von_values = [n["Von"] for n in sorted_nights if n.get("Von") is not None]
    pct_values = [n["Pct_richtig"] for n in sorted_nights]

    best_placement = min(placements) if placements else None
    if best_placement is not None:
        bp_night = next(
            n for n in sorted_nights if n.get("Platzierung") == best_placement
        )
        best_placement_monat = bp_night["Monat"]
        best_placement_von = bp_night.get("Von")
    else:
        best_placement_monat = None
        best_placement_von = None

    best_cat = max(cat_avgs, key=cat_avgs.get) if cat_avgs else None
    worst_cat = min(cat_avgs, key=cat_avgs.get) if cat_avgs else None

    kpis = {
        "n_abende":             len(sorted_nights),
        "first_monat":          sorted_nights[0]["Monat"],
        "avg_pct":              mean(pct_values),
        "best_placement":       best_placement,
        "best_placement_monat": best_placement_monat,
        "best_placement_von":   best_placement_von,
        "avg_placement":        mean(placements) if placements else None,
        "avg_teams":            mean(von_values) if von_values else None,
        "best_cat":             best_cat,
        "best_cat_avg":         cat_avgs[best_cat] if best_cat else None,
        "worst_cat":            worst_cat,
        "worst_cat_avg":        cat_avgs[worst_cat] if worst_cat else None,
    }

    # --- Trend ---
    trend = {
        "monate":     monate_list,
        "pct":        [n["Pct_richtig"] for n in sorted_nights],
        "placements": [n.get("Platzierung") for n in sorted_nights],
        "von":        [n.get("Von") for n in sorted_nights],
        "gesamt":     [n.get("Gesamt", 0) for n in sorted_nights],
    }

    # --- Ranking: absteigend nach Mittelwert ---
    ranking = sorted(cat_avgs.items(), key=lambda x: x[1], reverse=True)

    # --- Heatmap: aufsteigend nach Mittelwert (schwaechste oben) ---
    kategorien_sorted_asc = sorted(cat_avgs, key=cat_avgs.get, reverse=False)
    matrix = [
        [n.get("cat_scores", {}).get(kat, 0) for n in sorted_nights]
        for kat in kategorien_sorted_asc
    ]
    heatmap = {
        "monate":     monate_list,
        "kategorien": kategorien_sorted_asc,
        "matrix":     matrix,
    }

    # --- Scatter: (kategorie, mittelwert, std) ---
    scatter = []
    for kat in cats_no_sonder:
        scores = _cat_scores_list(kat)
        avg = cat_avgs[kat]
        std = pstdev(scores) if len(scores) >= 2 else 0.0
        scatter.append((kat, avg, std))

    return {
        "kpis":    kpis,
        "trend":   trend,
        "ranking": ranking,
        "heatmap": heatmap,
        "scatter": scatter,
    }


def validate_form(form, *, existing_quiz_nights, edit_datum=None):
    """Prueft das Formular auf Fehler und gibt eine Liste von Fehlermeldungen zurueck."""
    errors = []

    year = form.get("year")
    month = form.get("month")

    if not isinstance(year, int) or not (2000 <= year <= 2099):
        errors.append("Jahr muss eine ganze Zahl zwischen 2000 und 2099 sein.")
    if not isinstance(month, int) or not (1 <= month <= 12):
        errors.append("Monat muss eine ganze Zahl zwischen 1 und 12 sein.")

    teile = form.get("teile", [])
    all_slots = []
    for block_idx, block in enumerate(teile):
        for slot_idx, slot in enumerate(block):
            punkte = slot.get("punkte")
            if not isinstance(punkte, int) or not (0 <= punkte <= 5):
                errors.append(
                    f"Punkte in Block {block_idx + 1}, Slot {slot_idx + 1} "
                    f"muessen eine ganze Zahl zwischen 0 und 5 sein."
                )
            all_slots.append(slot)

    all_kategorien = [slot.get("kategorie") for slot in all_slots]
    invalid_cats = [k for k in all_kategorien if k not in CATEGORIES]
    if invalid_cats:
        errors.append(
            f"Unbekannte Kategorie(n) in den Spielrunden: {', '.join(str(k) for k in invalid_cats)}"
        )
    if len(set(all_kategorien)) != 12:
        errors.append(
            "Die 12 gespielten Kategorien muessen paarweise unterschiedlich sein "
            f"(gefunden: {len(set(all_kategorien))} eindeutige)."
        )

    joker1 = form.get("joker1")
    joker2 = form.get("joker2")
    if joker1 not in CATEGORIES:
        errors.append(f"Joker 1 '{joker1}' ist keine gueltige Kategorie.")
    if joker2 not in CATEGORIES:
        errors.append(f"Joker 2 '{joker2}' ist keine gueltige Kategorie.")
    if joker1 in CATEGORIES and joker2 in CATEGORIES and joker1 == joker2:
        errors.append("Joker 1 und Joker 2 muessen unterschiedliche Kategorien sein.")
    played = set(all_kategorien)
    if joker1 in CATEGORIES and joker1 not in played:
        errors.append(f"Joker 1 '{joker1}' wurde nicht als gespielte Kategorie eingetragen.")
    if joker2 in CATEGORIES and joker2 not in played:
        errors.append(f"Joker 2 '{joker2}' wurde nicht als gespielte Kategorie eingetragen.")

    # Bonus wird automatisch aus den Jokern berechnet -- keine Eingabe-Pruefung.

    platz = form.get("platz")
    von = form.get("von")
    if (platz is None) != (von is None):
        errors.append("Platz und Von muessen beide gesetzt sein oder beide leer.")
    elif platz is not None and von is not None:
        if not (isinstance(platz, int) and isinstance(von, int) and 1 <= platz <= von):
            errors.append(
                f"Platz ({platz}) muss eine ganze Zahl >= 1 und <= Von ({von}) sein."
            )

    return errors


def _classify_theme(thema):
    """Klassifiziert ein Sonderrunden-Thema als 'klassisch', 'popkultur' oder 'sonst'."""
    if not thema:
        return "sonst"
    low = thema.lower()
    if any(kw.lower() in low for kw in CLASSICAL_KEYWORDS):
        return "klassisch"
    if any(kw.lower() in low for kw in POPCULTURE_KEYWORDS):
        return "popkultur"
    return "sonst"


def compute_insights(quiz_nights):
    """Leitet strukturierte Beobachtungen und Empfehlungen aus den Quizabenden ab.

    Rueckgabe: Liste von Sektionen, jede ein dict mit:
      "titel": str
      "lead":  str | None  (optionaler Einleitungssatz unter dem Titel)
      "items": list of {"kind": "info"|"tipp"|"warnung", "text": str}

    Bei leerer Eingabe: leere Liste.
    """
    from statistics import mean, pstdev

    if not quiz_nights:
        return []

    sorted_nights = sorted(
        quiz_nights,
        key=lambda nx: nx.get("Datum") or parse_monat_to_iso(nx.get("Monat", "Jan 00")),
    )
    n = len(sorted_nights)
    cats_no_sonder = [c for c in CATEGORIES if c != "Sonderrunde"]

    def _scores_of(kat):
        return [night.get("cat_scores", {}).get(kat, 0) for night in sorted_nights]

    cat_avgs = {kat: mean(_scores_of(kat)) for kat in cats_no_sonder}
    cat_stds = {kat: pstdev(_scores_of(kat)) if n >= 2 else 0.0
                for kat in cats_no_sonder}

    sections = []

    # ----------------------------------------------------------------------
    # 1. Form-Trend
    # ----------------------------------------------------------------------
    items = []
    if n >= 2:
        half = max(1, n // 2)
        first_half = sorted_nights[:half]
        last_half = sorted_nights[-half:]
        pct_first = mean(q["Pct_richtig"] for q in first_half)
        pct_last = mean(q["Pct_richtig"] for q in last_half)
        diff = pct_last - pct_first
        if diff > 0.03:
            items.append({"kind": "info",
                "text": f"Die Quote zieht an: von {pct_first:.0%} in der frühen auf "
                        f"{pct_last:.0%} in der jüngsten Hälfte — die Form festigt "
                        f"sich über {n} Abende hinweg."})
        elif diff < -0.03:
            items.append({"kind": "warnung",
                "text": f"Die Form flacht ab: von {pct_first:.0%} in der frühen auf "
                        f"{pct_last:.0%} in der jüngsten Hälfte — die Tendenz zeigt "
                        f"nach unten."})
        else:
            items.append({"kind": "info",
                "text": f"Die Quote ruht stabil um {(pct_first + pct_last) / 2:.0%} "
                        f"— weder Aufwärts- noch Abwärtsbewegung."})

        platz_first = [q["Platzierung"] for q in first_half
                       if q.get("Platzierung") is not None]
        platz_last = [q["Platzierung"] for q in last_half
                      if q.get("Platzierung") is not None]
        if platz_first and platz_last:
            p_first = mean(platz_first)
            p_last = mean(platz_last)
            if p_last < p_first - 0.5:
                items.append({"kind": "info",
                    "text": f"Auch die mittlere Platzierung rückt nach vorn: "
                            f"Ø {p_first:.1f} früher, Ø {p_last:.1f} zuletzt."})
            elif p_last > p_first + 0.5:
                items.append({"kind": "warnung",
                    "text": f"Die mittlere Platzierung verschlechtert sich: "
                            f"Ø {p_first:.1f} früher, Ø {p_last:.1f} zuletzt."})

    last_night = sorted_nights[-1]
    items.append({"kind": "info",
        "text": f"Jüngster Abend ({last_night['Monat']}): "
                f"{last_night['Gesamt']} Punkte ({last_night['Pct_richtig']:.0%}), "
                f"Platz {last_night.get('Platzierung', '?')} von "
                f"{last_night.get('Von', '?')}."})
    sections.append({"titel": "Form-Trend", "lead": None, "items": items})

    # ----------------------------------------------------------------------
    # 2. Verlässliche Pfeiler
    # ----------------------------------------------------------------------
    cats_by_strength = sorted(cats_no_sonder,
                              key=lambda k: (-cat_avgs[k], cat_stds[k]))
    top2 = cats_by_strength[:2]
    items = []
    for kat in top2:
        scores = _scores_of(kat)
        items.append({"kind": "info",
            "text": f"{kat} — Ø {cat_avgs[kat]:.2f}/5, "
                    f"Streuung σ {cat_stds[kat]:.2f}, "
                    f"Bandbreite {min(scores)}–{max(scores)}."})
    if cat_stds[top2[0]] < 1.0:
        items.append({"kind": "tipp",
            "text": f"{top2[0]} liefert verlässlich konstant — ein ruhiger "
                    f"Joker-Kandidat."})
    else:
        items.append({"kind": "tipp",
            "text": f"{top2[0]} ist im Mittel stark, schwankt jedoch merklich — "
                    f"als Joker nur dann wählen, wenn das Thema des Abends "
                    f"Zuversicht weckt."})
    sections.append({"titel": "Verlässliche Pfeiler", "lead": None,
                     "items": items})

    # ----------------------------------------------------------------------
    # 3. Wackel-Kandidaten
    # ----------------------------------------------------------------------
    cats_by_weakness = sorted(cats_no_sonder,
                              key=lambda k: (cat_avgs[k], -cat_stds[k]))
    bottom2 = cats_by_weakness[:2]
    items = []
    for kat in bottom2:
        scores = _scores_of(kat)
        recent = scores[-3:] if len(scores) >= 3 else scores
        recent_txt = ", ".join(str(s) for s in recent)
        items.append({"kind": "info",
            "text": f"{kat} — Ø {cat_avgs[kat]:.2f}/5, zuletzt {recent[-1]} "
                    f"(letzte Abende: {recent_txt})."})
        if len(scores) >= 3 and mean(scores[-2:]) < cat_avgs[kat] - 0.5:
            items.append({"kind": "warnung",
                "text": f"In {kat} flacht die Form zuletzt ab — vor dem nächsten "
                        f"Abend lohnt sich gezielte Vorbereitung."})
    sections.append({"titel": "Wackel-Kandidaten", "lead": None, "items": items})

    # ----------------------------------------------------------------------
    # 4. Joker-Bilanz
    # ----------------------------------------------------------------------
    joker_use = {}  # kat -> list of (score, monat, hit)
    for q in sorted_nights:
        for j in (q.get("Joker1"), q.get("Joker2")):
            if j:
                s = q.get("cat_scores", {}).get(j, 0)
                joker_use.setdefault(j, []).append((s, q["Monat"], s >= 3))

    total_jokers = sum(len(v) for v in joker_use.values())
    total_hits = sum(1 for v in joker_use.values() for _, _, h in v if h)
    items = []
    if total_jokers:
        items.append({"kind": "info",
            "text": f"{total_hits} von {total_jokers} Jokern haben getroffen "
                    f"(als Treffer zählt ab 3 Punkten in der Joker-Kategorie)."})
    for kat, uses in sorted(joker_use.items(),
                            key=lambda kv: (-len(kv[1]),
                                            -mean(s for s, _, _ in kv[1]))):
        hits = sum(1 for _, _, h in uses if h)
        avg = mean(s for s, _, _ in uses)
        items.append({"kind": "info",
            "text": f"{kat}: {len(uses)}× gewählt, Ø {avg:.1f}, "
                    f"Treffer {hits} von {len(uses)}."})
    sections.append({"titel": "Joker-Bilanz", "lead": None, "items": items})

    # ----------------------------------------------------------------------
    # 5. Joker-Empfehlung
    # ----------------------------------------------------------------------
    # Score = Mittelwert × (0.5 + Hit-Rate); falls keine Joker-Historie,
    # wird die allgemeine ≥-3-Trefferquote der Kategorie genutzt.
    candidates = []
    for kat in cats_no_sonder:
        uses = joker_use.get(kat, [])
        if uses:
            hit_rate = sum(1 for _, _, h in uses if h) / len(uses)
        else:
            scores = _scores_of(kat)
            hit_rate = (sum(1 for s in scores if s >= 3) / len(scores)
                        if scores else 0)
        score = cat_avgs[kat] * (0.5 + hit_rate)
        candidates.append((kat, score, hit_rate))

    # Sonderrunde nur dann mit aufnehmen, wenn die letzten drei Sonderrunden
    # im Mittel mindestens 3 ergaben (nicht jedes Thema verträgt einen Joker).
    sr_recent = [nx.get("cat_scores", {}).get("Sonderrunde", 0)
                 for nx in sorted_nights[-3:]]
    if sr_recent and mean(sr_recent) >= 3:
        sr_uses = joker_use.get("Sonderrunde", [])
        if sr_uses:
            sr_hit_rate = sum(1 for _, _, h in sr_uses if h) / len(sr_uses)
        else:
            sr_hit_rate = sum(1 for s in sr_recent if s >= 3) / len(sr_recent)
        sr_avg = mean([nx.get("cat_scores", {}).get("Sonderrunde", 0)
                       for nx in sorted_nights])
        candidates.append(("Sonderrunde", sr_avg * (0.5 + sr_hit_rate),
                           sr_hit_rate))

    candidates.sort(key=lambda x: -x[1])
    top_pair = candidates[:2]
    items = [{"kind": "tipp",
        "text": f"Nächste Joker-Wahl: {top_pair[0][0]} und {top_pair[1][0]}."}]
    for kat, _, hr in top_pair:
        items.append({"kind": "info",
            "text": f"{kat} — Trefferquote {hr:.0%}, "
                    f"Ø {cat_avgs.get(kat, mean(_scores_of('Sonderrunde')) if kat == 'Sonderrunde' else 0):.1f}/5."})
    sections.append({"titel": "Joker-Empfehlung",
                     "lead": "Abgeleitet aus historischer Joker-Hit-Rate und "
                             "Kategorie-Mittelwert.",
                     "items": items})

    # ----------------------------------------------------------------------
    # 6. Sonderrunde — was zieht
    # ----------------------------------------------------------------------
    classical, popculture, other = [], [], []
    for q in sorted_nights:
        thema = q.get("Sonderrunde_Thema", "") or ""
        score = q.get("cat_scores", {}).get("Sonderrunde", 0)
        cls = _classify_theme(thema)
        if cls == "klassisch":
            classical.append((thema, score, q["Monat"]))
        elif cls == "popkultur":
            popculture.append((thema, score, q["Monat"]))
        else:
            other.append((thema, score, q["Monat"]))

    items = []
    if classical:
        avg_cl = mean(s for _, s, _ in classical)
        themes = ", ".join(f"{t} ({s}/5)" for t, s, _ in classical)
        items.append({"kind": "info",
            "text": f"Klassische Bildungsthemen ({len(classical)}×, "
                    f"Ø {avg_cl:.1f}/5): {themes}."})
    if popculture:
        avg_pop = mean(s for _, s, _ in popculture)
        themes = ", ".join(f"{t} ({s}/5)" for t, s, _ in popculture)
        items.append({"kind": "info",
            "text": f"Popkultur und Alltagsnähe ({len(popculture)}×, "
                    f"Ø {avg_pop:.1f}/5): {themes}."})
    if other:
        avg_ot = mean(s for _, s, _ in other)
        themes = ", ".join(f"{t} ({s}/5)" for t, s, _ in other)
        items.append({"kind": "info",
            "text": f"Sonstige Themen ({len(other)}×, "
                    f"Ø {avg_ot:.1f}/5): {themes}."})

    if (classical and popculture
            and mean(s for _, s, _ in popculture)
                > mean(s for _, s, _ in classical) + 1):
        items.append({"kind": "tipp",
            "text": "Popkultur und Alltagsthemen liegen Euch deutlich besser "
                    "als klassische Bildungsthemen — bei freier Wahl dorthin "
                    "tendieren."})
    sections.append({"titel": "Sonderrunde — was zieht", "lead": None,
                     "items": items})

    # ----------------------------------------------------------------------
    # 7. Letzter Abend
    # ----------------------------------------------------------------------
    items = []
    cs = last_night.get("cat_scores", {})
    sorted_cs = sorted(cs.items(), key=lambda kv: -kv[1])
    tops = [(k, v) for k, v in sorted_cs if v >= 4]
    flops = [(k, v) for k, v in sorted_cs if v <= 1]
    if tops:
        items.append({"kind": "info",
            "text": "Stark: " + ", ".join(f"{k} ({v}/5)" for k, v in tops) + "."})
    if flops:
        items.append({"kind": "warnung",
            "text": "Schwach: " + ", ".join(f"{k} ({v}/5)" for k, v in flops) + "."})
    if n >= 2:
        avg_gesamt = mean(q["Gesamt"] for q in sorted_nights[:-1])
        diff_g = last_night["Gesamt"] - avg_gesamt
        if diff_g > 3:
            items.append({"kind": "info",
                "text": f"Mit {last_night['Gesamt']} Punkten deutlich über dem "
                        f"Schnitt der bisherigen Abende (Ø {avg_gesamt:.1f}) — "
                        f"ein guter Lauf."})
        elif diff_g < -3:
            items.append({"kind": "warnung",
                "text": f"Mit {last_night['Gesamt']} Punkten unter dem Schnitt "
                        f"der vorigen Abende (Ø {avg_gesamt:.1f})."})
    sections.append({"titel": "Letzter Abend", "lead": None, "items": items})

    # ----------------------------------------------------------------------
    # 8. Ausblick
    # ----------------------------------------------------------------------
    items = [{"kind": "tipp",
        "text": f"Doppel-Joker auf {top_pair[0][0]} und {top_pair[1][0]} "
                f"— beide verbinden hohe Trefferquote mit solidem Mittelwert."}]
    if bottom2:
        items.append({"kind": "tipp",
            "text": f"Vorbereitung lohnt sich in {bottom2[0]} und {bottom2[1]} "
                    f"— hier holt Ihr im Mittel die wenigsten Punkte."})
    if (classical and popculture
            and mean(s for _, s, _ in popculture)
                > mean(s for _, s, _ in classical) + 1):
        items.append({"kind": "tipp",
            "text": "Bei freier Sonderrunden-Wahl: Popkultur und Alltag schlagen "
                    "klassische Bildungsthemen deutlich."})
    sections.append({"titel": "Ausblick", "lead": None, "items": items})

    return sections
