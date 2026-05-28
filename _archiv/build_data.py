"""Liest Kneipenquiz.xlsx und schreibt data.json fuer die Streamlit-App."""
import json
import pathlib
import sys

import pandas as pd

HERE = pathlib.Path(__file__).parent
XLSX = HERE / "Kneipenquiz.xlsx"
JSON_OUT = HERE / "data.json"

GERMAN_MONTHS = ["Jan", "Feb", "Mrz", "Apr", "Mai", "Jun",
                 "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]


def fmt_month(dt):
    return f"{GERMAN_MONTHS[dt.month - 1]} {dt.year % 100:02d}"


def find_row(raw, col, value):
    for i in range(raw.shape[0]):
        v = raw.iat[i, col]
        if pd.notna(v) and v == value:
            return i
    return None


def to_int(v):
    return int(v) if pd.notna(v) else None


def to_float(v):
    return float(v) if pd.notna(v) else None


def build():
    if not XLSX.exists():
        print(f"FEHLER: {XLSX.name} nicht gefunden", file=sys.stderr)
        return 1

    raw = pd.read_excel(XLSX, header=None)

    # --- Block 1: Kategorien-Tabelle (Header in Spalte 1: 'Kategorie') ---
    cat_hdr = find_row(raw, 1, "Kategorie")
    if cat_hdr is None:
        print("FEHLER: 'Kategorie'-Header nicht gefunden", file=sys.stderr)
        return 1

    headers = raw.iloc[cat_hdr]
    col_kat = 1
    col_platz = headers[headers == "Platz"].index[0]
    col_punkte = headers[headers == "Punkte gesamt"].index[0]
    col_mittel = headers[headers == "Mittelwert"].index[0]

    month_cols = []
    for c in range(col_mittel + 1, raw.shape[1]):
        v = headers.iloc[c]
        if pd.notna(v) and isinstance(v, str):
            month_cols.append((c, v.strip()))
        else:
            break
    months = [m for _, m in month_cols]

    categories = []
    for i in range(cat_hdr + 1, raw.shape[0]):
        kat = raw.iat[i, col_kat]
        if pd.isna(kat):
            break
        cat = {
            "Kategorie": str(kat).strip(),
            "Platz": to_int(raw.iat[i, col_platz]),
            "Punkte_gesamt": to_int(raw.iat[i, col_punkte]),
            "Mittelwert": to_float(raw.iat[i, col_mittel]),
        }
        for c, m in month_cols:
            cat[m] = to_int(raw.iat[i, c]) or 0
        categories.append(cat)

    # --- Block 2: Quizabend-Details (Header in Spalte 1: 'Monat') ---
    night_hdr = find_row(raw, 1, "Monat")
    if night_hdr is None:
        print("FEHLER: 'Monat'-Header nicht gefunden", file=sys.stderr)
        return 1

    # Spalten-Layout aus dem Header:
    #  1 Datum | 2 Joker | 3 Sonderrunde-Thema
    #  4-6 Q1-Q3 | 7 Teil1 | 8-10 Q4-Q6 | 11 Teil2
    #  12-14 Q7-Q9 | 15 Teil3 | 16-18 Q10-Q12 | 19 Teil4
    #  24 Bonus | 25 Gesamt | 26 % richtig | 27 Platz | 28 von
    Q_COLS = [(4, 5, 6, 7), (8, 9, 10, 11), (12, 13, 14, 15), (16, 17, 18, 19)]

    quiz_nights = []
    i = night_hdr + 1
    while i + 1 < raw.shape[0]:
        date_cell = raw.iat[i, 1]
        if pd.isna(date_cell):
            break

        if hasattr(date_cell, "month"):
            monat = fmt_month(date_cell)
        else:
            monat = str(date_cell).strip()

        joker1 = str(raw.iat[i, 2]).strip() if pd.notna(raw.iat[i, 2]) else None
        sond_thema = str(raw.iat[i, 3]).strip() if pd.notna(raw.iat[i, 3]) else None
        joker2 = str(raw.iat[i + 1, 2]).strip() if pd.notna(raw.iat[i + 1, 2]) else None

        cat_scores = {}
        teils = []
        for q1, q2, q3, ts in Q_COLS:
            for q in (q1, q2, q3):
                cat_name = raw.iat[i, q]
                score = raw.iat[i + 1, q]
                if pd.notna(cat_name) and pd.notna(score):
                    cat_scores[str(cat_name).strip()] = (
                        cat_scores.get(str(cat_name).strip(), 0) + int(score)
                    )
            teils.append(to_int(raw.iat[i + 1, ts]) or 0)

        quiz_nights.append({
            "Monat": monat,
            "Joker1": joker1,
            "Joker2": joker2,
            "Sonderrunde_Thema": sond_thema,
            "Teil1": teils[0],
            "Teil2": teils[1],
            "Teil3": teils[2],
            "Teil4": teils[3],
            "Bonus": to_int(raw.iat[i + 1, 24]) or 0,
            "Gesamt": to_int(raw.iat[i + 1, 25]) or 0,
            "Pct_richtig": to_float(raw.iat[i + 1, 26]) or 0.0,
            "Platzierung": to_int(raw.iat[i + 1, 27]),
            "Von": to_int(raw.iat[i + 1, 28]),
            "cat_scores": cat_scores,
        })
        i += 2

    out = {
        "months": months,
        "categories": categories,
        "quiz_nights": quiz_nights,
    }
    with open(JSON_OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"OK: {len(categories)} Kategorien, {len(quiz_nights)} Quizabende")
    print(f"    Monate: {', '.join(months)}")
    print(f"    Geschrieben: {JSON_OUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(build())
