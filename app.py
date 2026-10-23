import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import json

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Kneipenquiz Schwabach",
    page_icon="🍺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Custom CSS – technical, clean look
# ---------------------------------------------------------------------------
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
<style>
    /* Font */
    *, .stApp, .stMarkdown, .stDataFrame, p, span, div, h1, h2, h3, h4, h5, h6 {
        font-family: 'Roboto', sans-serif !important;
    }

    /* Main background */
    .stApp {
        background: #ebedf0;
    }

    /* Limit content width to 75% on desktop only */
    @media (min-width: 769px) {
        .block-container {
            max-width: 75% !important;
            margin: 0 auto !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }

    /* Header */
    .dashboard-header {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
    }
    .dashboard-header h1 {
        font-size: 2.8rem;
        font-weight: 800;
        color: #2c3e50;
        margin-bottom: 0.2rem;
    }
    .dashboard-header p {
        /* wie .info-text: auf dem Seitengrund reicht #6b7280 nicht (4,1:1) */
        color: #4b5563;
        font-size: 1.1rem;
    }

    /* KPI cards */
    .kpi-card {
        background: #ffffff;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        padding: 1.2rem 1rem;
        /* Gleiche Hoehe fuer alle Karten einer Reihe. height:100% hilft hier
           nicht: Streamlit schachtelt zwischen Spalte und Karte mehrere
           Container ohne eigene Hoehe, die Prozentangabe laeuft also ins
           Leere. Eine Mindesthoehe, die auch eine zweizeilige Unterzeile
           fasst, ist der stabile Weg -- gemessen waren 141 px einzeilig und
           163 px zweizeilig. */
        min-height: 165px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .kpi-label {
        color: #6b7280;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 0.3rem;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1f2937;
    }
    .kpi-sub {
        color: #4b7c6f;
        font-size: 0.85rem;
        margin-top: 0.2rem;
    }
    .kpi-sub.bad { color: #9b4d4d; }

    /* Section headers */
    .section-title {
        color: #2c3e50;
        font-size: 1.3rem;
        font-weight: 600;
        margin: 2rem 0 0.8rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 2px solid #7f8c8d;
    }

    /* Hide default streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Plotly chart containers */
    .stPlotlyChart {
        background: #ffffff;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        padding: 0.5rem;
    }

    /* Divider */
    .divider {
        height: 1px;
        background: #d1d5db;
        margin: 1.5rem 0;
    }

    /* Info text -- #4b5563 statt #6b7280: Auf dem Seitengrund #ebedf0 erreichte
       das hellere Grau nur 4,1:1 und blieb damit unter der Lesbarkeitsgrenze
       von 4,5:1; bei 12 px Schriftgröße las sich das als grau auf grau.
       #4b5563 bringt 5,9:1. Auf weißen Karten bleibt #6b7280, dort sind es
       4,8:1. */
    .info-text {
        color: #4b5563;
        font-size: 0.75rem;
        margin-top: -0.5rem;
        margin-bottom: 0.5rem;
    }

    /* Farbprobe in Fließtext-Legenden: Ein eingefärbtes Zeichen ■ verschwand
       in den hellen Tönen fast völlig (das Grau erreichte 1,8:1). Die Probe
       trägt jetzt die Farbe als Fläche und eine Kontur, die sie auf jedem
       Grund sichtbar hält -- die Farbtreue zum Diagramm bleibt erhalten. */
    .farbprobe {
        display: inline-block;
        width: 11px;
        height: 11px;
        border-radius: 2px;
        border: 1px solid #4b5563;
        vertical-align: -1px;
        margin-right: 3px;
    }

    /* Erkenntnisse */
    .insight-card {
        background: #ffffff;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        padding: 1rem 1.1rem;
        margin-bottom: 0.8rem;
    }
    .insight-titel {
        color: #2c3e50;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }
    .insight-lead {
        color: #6b7280;
        font-size: 0.82rem;
        margin-bottom: 0.6rem;
    }
    .insight-item {
        color: #374151;
        font-size: 0.85rem;
        line-height: 1.45;
        border-left: 3px solid #d1d5db;
        padding: 0.15rem 0 0.15rem 0.7rem;
        margin-bottom: 0.5rem;
    }

    /* Mobile responsive */
    @media (max-width: 768px) {
        .dashboard-header h1 {
            font-size: 1.6rem;
        }
        .dashboard-header p {
            font-size: 0.9rem;
        }
        .kpi-value {
            font-size: 1.4rem;
        }
        .kpi-label {
            font-size: 0.7rem;
            letter-spacing: 1px;
        }
        .kpi-sub {
            font-size: 0.75rem;
        }
        .kpi-card {
            padding: 0.8rem 0.5rem;
            margin-bottom: 0.5rem;
        }
        .section-title {
            font-size: 1.1rem;
        }
        /* KEIN max-height auf .stPlotlyChart: Der frühere Deckel von 300px
           lag unter der Höhe jedes einzelnen Diagramms (400 bis 500) und
           beschnitt sie damit ausnahmslos. Plotly skaliert ohnehin über die
           Breite; die Höhe steht in CHART_H / CHART_H_TALL. */
        /* Force Streamlit columns to stack vertically */
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
        }
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }

        /* AUSNAHME vom Stapeln: die Kennzahlen-Karten stehen zu zweit
           nebeneinander. Einspaltig gestapelt lagen zehn Karten à 165 px vor
           dem ersten Diagramm -- gemessene 2.208 px Scrollweg, also zweieinhalb
           Telefon-Bildschirme, ehe überhaupt eine Grafik erscheint. Zu zweit
           sind es fünf Reihen statt zehn. Diagramm-Spalten bleiben gestapelt,
           denn ihnen fehlt bei halber Breite die Lesbarkeit.
           ':has' trennt beide Fälle; wo ein Browser es nicht kennt, bleibt es
           beim Stapeln von oben -- schlechter, aber nicht kaputt. */
        [data-testid="stHorizontalBlock"]:has(.kpi-card) {
            flex-direction: row !important;
            flex-wrap: wrap !important;
            gap: 0.5rem !important;
        }
        [data-testid="stHorizontalBlock"]:has(.kpi-card) > [data-testid="stColumn"] {
            width: calc(50% - 0.25rem) !important;
            flex: 0 0 calc(50% - 0.25rem) !important;
            min-width: calc(50% - 0.25rem) !important;
        }
        /* Der Streamlit-Kopfabstand von 6rem kostet auf dem Telefon einen
           halben Bildschirm, ehe der Titel kommt. */
        .block-container {
            padding-top: 1.2rem !important;
        }

        [data-testid="stHorizontalBlock"]:has(.kpi-card) .kpi-card {
            /* 140 px, nicht 118: Die Karte "Perfekte Runden" traegt eine
               mehrzeilige Aufzaehlung und war damit als einzige hoeher --
               genau der Reihenbruch, der am Schirm schon behoben war. */
            min-height: 140px;
            padding: 0.6rem 0.4rem;
            margin-bottom: 0;
        }
        [data-testid="stHorizontalBlock"]:has(.kpi-card) .kpi-label {
            font-size: 0.62rem;
            letter-spacing: 0.5px;
            line-height: 1.2;
        }
        [data-testid="stHorizontalBlock"]:has(.kpi-card) .kpi-value {
            /* "Wissensch./Natur" ist der laengste Kennzahlen-Wert und lief bei
               1,3rem ueber den Kartenrand hinaus. Kleiner gesetzt und mit
               erlaubtem Umbruch bleibt jeder Wert innerhalb seiner Karte. */
            font-size: 1.1rem;
            line-height: 1.25;
            overflow-wrap: anywhere;
        }
        [data-testid="stHorizontalBlock"]:has(.kpi-card) .kpi-sub {
            font-size: 0.68rem;
            line-height: 1.2;
        }
    }

    /* AUSNAHME von der Roboto-Regel ganz oben -- muss am Ende stehen.
       Streamlit zeichnet seine Symbole (Aufklapp-Pfeil, Sidebar-Umschalter,
       Tabellen-Werkzeugleiste) nicht als Zeichen, sondern als LIGATUREN der
       Schrift "Material Symbols Rounded": Im span steht der Klartext
       "expand_more" bzw. "keyboard_double_arrow_right", den erst die Schrift
       zum Pfeil zusammenzieht. Die globale Regel mit * und !important nahm
       den Symbolen diese Schrift -- und damit stand der Name im Klartext da.
       Die Attribut-Selektoren haben hoehere Spezifitaet als * und span und
       gewinnen daher trotz des !important oben. */
    [data-testid="stIconMaterial"],
    span[data-testid="stIconMaterial"],
    .material-symbols-rounded,
    span[class*="material-symbols"] {
        font-family: 'Material Symbols Rounded' !important;
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
    }

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Load pre-computed data from JSON (fast, no openpyxl needed)
# ---------------------------------------------------------------------------
import pathlib

# Eine Datenquelle für beide Welten: die mitversionierte data.json im
# Projektordner. Lokal schreibt die Eingabe-GUI direkt hierher, im Deployment
# (Streamlit Cloud) liegt dieselbe Datei im Repo-Abbild.
DATA_PATH = pathlib.Path(__file__).parent / "data.json"


# Die mtime gehört in den Cache-Schlüssel: sonst zeigt die lokal laufende App
# nach einem neu erfassten Abend weiter den Stand des ersten Aufrufs.
@st.cache_data
def load_data(path: str, mtime: float):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    df_cat = pd.DataFrame(data["categories"])
    months = data["months"]
    quiz_nights = data["quiz_nights"]
    return df_cat, months, quiz_nights


df_cat, months, quiz_nights = load_data(str(DATA_PATH), DATA_PATH.stat().st_mtime)
n_nights = len(quiz_nights)

# quiz_data trägt die Themen-Klassifikation (_classify_theme) und die
# abgeleiteten Beobachtungen (compute_insights), die auch der Tk-Reiter nutzt
# -- beides hier einbinden statt ein zweites Mal pflegen. Reines Standard-
# Python ohne GUI-Abhängigkeit, in der Streamlit Cloud also ladbar. Schlägt
# der Import wider Erwarten fehl, fallen nur diese beiden Zugaben aus statt
# des ganzen Dashboards.
try:
    import quiz_data as qd
except Exception:  # pragma: no cover - Deployment-Absicherung
    qd = None

# ---------------------------------------------------------------------------
# Plotly theme defaults
# ---------------------------------------------------------------------------
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#374151", family="Roboto, sans-serif"),
    margin=dict(l=40, r=40, t=50, b=50),
    hoverlabel=dict(bgcolor="#ffffff", font_color="#1f2937", bordercolor="#7f8c8d"),
)

# Disable zoom/pan on touch devices to allow smooth scrolling
PLOTLY_CONFIG = {"staticPlot": True}

# Diagrammhöhen an einer Stelle: CHART_H für den Regelfall, CHART_H_TALL für
# Diagramme mit einer Zeile je Kategorie oder Abend (elf bzw. zehn Zeilen).
CHART_H = 420
CHART_H_TALL = 500

# Gedeckte aber klar unterscheidbare Farben – 11 Kategorien
CAT_COLORS = [
    "#4e79a7", "#f28e2b", "#76b7b2", "#e15759", "#59a14f",
    "#edc948", "#b07aa1", "#9c755f", "#ff9da7", "#bab0ac",
    "#a0cbe8",
]


def _de(x, dez=1, trim=False):
    """Zahl in deutscher Schreibweise; trim=True laesst die Null nach dem Komma weg."""
    if trim and abs(x - round(x)) < 1e-9:
        return f"{round(x):d}"
    return f"{x:.{dez}f}".replace(".", ",")


def _lesefarbe(hexfarbe, hell="#ffffff", dunkel="#1f2937"):
    """Waehlt Weiss oder Dunkelgrau -- je nachdem, was auf der Flaeche traegt.

    Die Beschriftung in den Stapelbalken stand durchweg in Weiss. Auf den
    dunklen Toenen der Palette ist das richtig, auf den hellen (Gelb #edc948,
    Grau #bab0ac, Rosa #ff9da7, Hellblau #a0cbe8) ergab es 1,6 bis 2,3:1 --
    weiss auf hell, also praktisch unlesbar. Entschieden wird nach dem
    WCAG-Kontrast: Welche der beiden Schriftfarben besser steht, gewinnt.
    """
    r, g, b = (int(hexfarbe[i:i + 2], 16) / 255 for i in (1, 3, 5))

    def _lin(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    lum = 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)
    k_hell = 1.05 / (lum + 0.05)          # Weiss hat Luminanz 1,0
    k_dunkel = (lum + 0.05) / (0.0295 + 0.05)   # #1f2937 hat rund 0,0295
    return hell if k_hell >= k_dunkel else dunkel

# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------
_first_month = months[0] if months else ""
_last_month = months[-1] if months else ""
st.markdown(f"""
<div class="dashboard-header">
    <h1>🍺 Kneipenquiz Schwabach</h1>
    <p>Performance-Dashboard &mdash; {n_nights} Quizabende &mdash; {_first_month} bis {_last_month}</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------------------------
night_points = [q["Gesamt"] for q in quiz_nights]
avg_points = np.mean(night_points)
# Spielwert ohne Joker: Summe der vier Teile, ohne den Joker-Bonus, der in
# "Gesamt" bereits drinsteckt. Beide Werte interessieren -- siehe KPI-Karte
# "Punkte pro Abend" unten, die deshalb beide nennt statt nur den einen.
spiel_points = [q["Teil1"] + q["Teil2"] + q["Teil3"] + q["Teil4"] for q in quiz_nights]
avg_spiel_points = np.mean(spiel_points)
avg_pct = np.mean([q["Pct_richtig"] for q in quiz_nights])
placements = [q["Platzierung"] for q in quiz_nights if q["Platzierung"] is not None]
best_placement = min(placements) if placements else "–"
best_placement_q = min(
    [q for q in quiz_nights if q["Platzierung"] is not None],
    key=lambda q: q["Platzierung"],
)
avg_placement = np.mean(placements) if placements else 0

# Feldposition statt absoluter Platzierung: Die Teamzahl schwankt zwischen
# 10 und 16, damit bedeutet derselbe Platz je Abend etwas anderes -- Platz 7
# von 16 ist oberes Drittel, Platz 10 von 10 ist der letzte. 0 % = Sieg,
# 100 % = letzter Platz.
feldpos = [(q["Platzierung"] - 1) / (q["Von"] - 1) * 100
           for q in quiz_nights
           if q["Platzierung"] is not None and q["Von"] and q["Von"] > 1]
avg_feldpos = np.mean(feldpos) if feldpos else 0

# Trend: last quiz vs previous quiz
prev_pct = quiz_nights[-2]["Pct_richtig"]
last_pct = quiz_nights[-1]["Pct_richtig"]
trend_delta = last_pct - prev_pct
trend_arrow = "↑" if trend_delta > 0 else "↓"
trend_class = "" if trend_delta > 0 else "bad"

cols = st.columns(6)
kpi_data = [
    ("Quizabende", str(n_nights), f"seit {_first_month}", ""),
    # Die Spanne darf nicht am Gedankenstrich umbrechen -- "28-" und "47" auf
    # zwei Zeilen las sich wie zwei Angaben. Der grosse Wert ist "Gesamt" und
    # enthaelt den Joker-Bonus; die zweite Zeile nennt zusaetzlich den reinen
    # Spielwert ohne Joker, sonst stuende unbenannt dieselbe Punktzahl fuer
    # zwei verschiedene Dinge. Median entfaellt hier zugunsten der beiden
    # Joker-Werte -- drei Zeilen sprengten die Kartenhoehe (165 px).
    ("Punkte pro Abend", _de(avg_points),
     f"inkl. Joker · <span style='white-space:nowrap'>Spanne {min(night_points)}–{max(night_points)}</span><br>"
     f"ohne Joker Ø {_de(avg_spiel_points)} Pkt.", ""),
    ("Ø Richtig", f"{avg_pct:.0%}", f"von max. 60 Fragen (ohne Joker)", ""),
    ("Beste Platzierung", f"{best_placement}.", f"{best_placement_q['Monat']} ({best_placement_q['Von']} Teams)", ""),
    ("Ø Feldposition", f"{avg_feldpos:.0f} %",
     f"Ø Platz {_de(avg_placement)} bei {_de(np.mean([q['Von'] for q in quiz_nights if q['Von']]))} Teams",
     "" if avg_feldpos < 50 else "bad"),
    # Kurzes Label: "Trend Richtig-Quote" brach als einziges um und machte
    # seine Karte hoeher als die fuenf daneben.
    ("Trend Quote", f"{trend_arrow} {abs(trend_delta):.0%}",
     f"{quiz_nights[-1]['Monat']} vs. {quiz_nights[-2]['Monat']} (ohne Joker)", trend_class),
]

for col, (label, value, sub, cls) in zip(cols, kpi_data):
    sub_cls = f"kpi-sub {cls}" if cls else "kpi-sub"
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="{sub_cls}">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)

# --- Second row of KPI cards: category insights ---
df_no_sonder = df_cat[df_cat["Kategorie"] != "Sonderrunde"]
best_cat = df_no_sonder.loc[df_no_sonder["Mittelwert"].idxmax()]
worst_cat = df_no_sonder.loc[df_no_sonder["Mittelwert"].idxmin()]

perfect_by_cat = {}
for m in months:
    for _, row in df_cat.iterrows():
        if row[m] == 5:
            cat = row["Kategorie"]
            perfect_by_cat.setdefault(cat, []).append(m)
perfect_labels = []
for cat, ms in perfect_by_cat.items():
    if len(ms) == 1:
        perfect_labels.append(f"{cat} ({ms[0]})")
    else:
        perfect_labels.append(f"{cat} ({', '.join(ms)})")
perfect_count = sum(len(ms) for ms in perfect_by_cat.values())

improvements = {}
_first2 = months[:2]
_last2 = months[-2:]
for _, row in df_no_sonder.iterrows():
    delta = np.mean([row[m] for m in _last2]) - np.mean([row[m] for m in _first2])
    improvements[row["Kategorie"]] = delta
most_improved = max(improvements, key=improvements.get)

cols2 = st.columns([1, 1, 1, 2])
kpi_data2 = [
    ("Stärkste Kategorie", best_cat["Kategorie"], f"Ø {_de(best_cat['Mittelwert'])}/5", ""),
    ("Schwächste Kategorie", worst_cat["Kategorie"], f"Ø {_de(worst_cat['Mittelwert'])}/5", "bad"),
    ("Meiste Verbesserung", most_improved,
     f"+{_de(improvements[most_improved])} Pkt. (Ø erste 2 vs. letzte 2 Abende)", ""),
    ("Perfekte Runden (5/5)", f"{perfect_count}x" if perfect_count else "–",
     ", ".join(perfect_labels) if perfect_labels else "–", ""),
]
for col, (label, value, sub, cls) in zip(cols2, kpi_data2):
    sub_cls = f"kpi-sub {cls}" if cls else "kpi-sub"
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value" style="font-size:1.3rem;">{value}</div>
        <div class="{sub_cls}">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

# --- Rohdaten ---
# Zugeklappt: dreizehn Spalten sind auf einem Telefon nicht zu lesen und
# schieben auf kleinen Schirmen alles Wesentliche nach unten. Wer sie
# braucht, klappt sie auf.
detail_rows_data = []
for q in quiz_nights:
    row = {
        "Monat": q["Monat"],
        "Joker 1": q["Joker1"] or "–",
        "Joker 2": q["Joker2"] or "–",
        "Sonderrunde": q["Sonderrunde_Thema"],
        "Teil 1": q["Teil1"],
        "Teil 2": q["Teil2"],
        "Teil 3": q["Teil3"],
        "Teil 4": q["Teil4"],
        # Der Wert entsteht ausschliesslich aus den Jokern (compute_bonus:
        # Verdopplung der Joker-Kategorie ab 3 Punkten). "Bonus" allein las
        # sich wie eine eigene Bonusrunde. Nicht bloss "Joker", weil daneben
        # schon "Joker 1" und "Joker 2" stehen -- die tragen Kategorien,
        # diese Spalte Punkte.
        "Joker-Pkt.": q["Bonus"],
        "Gesamt": q["Gesamt"],
        "% richtig": round(q["Pct_richtig"] * 100),
        "Platz": q["Platzierung"],
        "von": q["Von"],
    }
    detail_rows_data.append(row)

df_detail = pd.DataFrame(detail_rows_data)

def centered(col_cfg):
    """Inject alignment into column config dicts."""
    col_cfg["alignment"] = "center"
    return col_cfg

with st.expander(f"Rohdaten aller {n_nights} Quizabende"):
    st.dataframe(
        df_detail,
        width='content',
        hide_index=True,
        column_config={
            "Teil 1": centered(st.column_config.NumberColumn("Teil 1", format="%d")),
            "Teil 2": centered(st.column_config.NumberColumn("Teil 2", format="%d")),
            "Teil 3": centered(st.column_config.NumberColumn("Teil 3", format="%d")),
            "Teil 4": centered(st.column_config.NumberColumn("Teil 4", format="%d")),
            "Joker-Pkt.": centered(st.column_config.NumberColumn("Joker-Pkt.", format="%d")),
            "Gesamt": st.column_config.ProgressColumn(
                "Gesamt (inkl. Joker)", min_value=0, max_value=70, format="%d Pkt.",
            ),
            "% richtig": centered(st.column_config.NumberColumn("% richtig (ohne Joker)", format="%.0f %%")),
            "Platz": centered(st.column_config.NumberColumn("Platz", format="%d.")),
            "von": centered(st.column_config.NumberColumn("von", format="%d")),
        },
    )
    st.markdown(
        '<p class="info-text">Teile 1 bis 4 je max. 15 Punkte (60 Fragen), '
        'Joker-Punkte max. 10 (zwei Joker à 5) &ndash; die Fortschrittsleiste '
        'misst gegen 70. Ein Joker verdoppelt seine Kategorie, aber erst ab '
        '3 Richtigen; darunter verfällt er.</p>',
        unsafe_allow_html=True,
    )

# Die frühere Tabelle "Punkte pro Kategorie und Monat" stand hier: dieselbe
# Matrix aus elf Kategorien mal zehn Monaten, die auch die Heatmap unten
# zeigt -- einmal als Ziffern, einmal als Muster. Die Heatmap bleibt.

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# ROW 1: Radar Chart + Placement Trend
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">Performance-Überblick</div>', unsafe_allow_html=True)

with st.container():
    # Dual axis: Placement (inverted) + % correct
    fig_trend = go.Figure()

    months_plot = [q["Monat"] for q in quiz_nights]
    placements_plot = [q["Platzierung"] for q in quiz_nights]
    pct_plot = [q["Pct_richtig"] for q in quiz_nights]

    fig_trend.add_trace(go.Bar(
        x=months_plot, y=pct_plot,
        name="% richtig",
        marker=dict(
            color=pct_plot,
            colorscale=[[0, "#c6dbef"], [0.5, "#6baed6"], [1, "#2171b5"]],
            line=dict(width=0),
        ),
        opacity=0.75,
        yaxis="y",
        hovertemplate="%{x}: %{y:.0%}<extra>% richtig</extra>",
    ))

    fig_trend.add_trace(go.Scatter(
        x=months_plot, y=placements_plot,
        name="Platzierung",
        mode="lines+markers",
        line=dict(color="#34495e", width=3),
        marker=dict(size=10, color="#34495e", line=dict(width=2, color="#ffffff")),
        yaxis="y2",
        hovertemplate="%{x}: Platz %{y}<extra>Platzierung</extra>",
    ))

    # Synchronise both y-axes to 5 intervals
    n_intervals = 5
    max_raw = max(p for p in placements_plot if p is not None) + 2
    max_nice = int(np.ceil(max_raw / n_intervals) * n_intervals)

    # Add annotations for placement labels (fixed pixel offset, always readable)
    annotations = []
    for i, (m, p, q) in enumerate(zip(months_plot, placements_plot, quiz_nights)):
        if p is not None:
            label = f"{p}. / {q['Von']}" if q["Von"] else f"{p}."
            # Normalise placement to y-position on yaxis2 (reversed: max_nice..0)
            y_norm = 1 - (p / max_nice)
            annotations.append(dict(
                x=m, y=y_norm,
                xref="x", yref="paper",
                text=f"<b>{label}</b>",
                showarrow=False,
                font=dict(color="#34495e", size=12),
                # Heller Grund hinter der Zahl: Auf 358 px Telefonbreite
                # ruecken elf Beschriftungen so eng zusammen, dass sie auf
                # Balken und Linie zu liegen kommen -- "7. / 16" stand dort
                # mitten im Liniengrau. Der Grund haelt sie in jeder Breite
                # lesbar, ohne das Bild zu beschweren.
                bgcolor="rgba(255,255,255,0.78)",
                borderpad=1,
                yshift=18,
            ))

    fig_trend.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Platzierung & Quote pro Quizabend", font=dict(size=16)),
        annotations=annotations,
        yaxis=dict(
            title="% richtig (ohne Joker)", tickformat=".0%", range=[0, 1],
            dtick=1 / n_intervals,
            gridcolor="rgba(0,0,0,0.06)", side="left",
        ),
        yaxis2=dict(
            title="Platzierung", overlaying="y", side="right",
            range=[max_nice, 0],
            dtick=max_nice / n_intervals,
            showgrid=False,
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        height=CHART_H,
        bargap=0.4,
    )
    st.plotly_chart(fig_trend, width='content', config=PLOTLY_CONFIG)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# ROW 2: Category Ranking + Heatmap
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">Kategorie-Analyse</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    # Horizontal bar – category ranking
    df_bar = df_cat[df_cat["Kategorie"] != "Sonderrunde"].sort_values("Mittelwert", ascending=True)

    colors = []
    for val in df_bar["Mittelwert"]:
        if val >= 3.2:
            colors.append("#08519c")
        elif val >= 2.8:
            colors.append("#2171b5")
        elif val >= 2.5:
            colors.append("#6baed6")
        else:
            colors.append("#c6dbef")

    fig_rank = go.Figure()
    fig_rank.add_trace(go.Bar(
        y=df_bar["Kategorie"],
        x=df_bar["Mittelwert"],
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:.1f}" for v in df_bar["Mittelwert"]],
        textposition="outside",
        textfont=dict(color="#374151", size=13),
        hovertemplate="%{y}: %{x:.2f}/5<extra></extra>",
    ))
    fig_rank.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Kategorie-Ranking (Ø Punkte)", font=dict(size=16)),
        xaxis=dict(range=[0, 4.5], gridcolor="rgba(0,0,0,0.05)", title="Ø Punkte (max. 5, ohne Joker)"),
        yaxis=dict(tickfont=dict(size=12)),
        height=CHART_H,
    )
    st.plotly_chart(fig_rank, width='content', config=PLOTLY_CONFIG)

with col2:
    # Heatmap – Categories x Months
    df_heat = df_cat[df_cat["Kategorie"] != "Sonderrunde"].set_index("Kategorie")[months]
    # Sort by average descending
    df_heat["avg"] = df_heat.mean(axis=1)
    df_heat = df_heat.sort_values("avg", ascending=True).drop(columns="avg")

    fig_heat = go.Figure(go.Heatmap(
        z=df_heat.values,
        x=df_heat.columns.tolist(),
        y=df_heat.index.tolist(),
        colorscale="RdYlBu",
        reversescale=True,
        zmin=0, zmax=5,
        text=df_heat.values,
        texttemplate="%{text}",
        textfont=dict(size=14, color="#374151"),
        hovertemplate="%{y} – %{x}: %{z}/5<extra></extra>",
        # Keine Farbleiste: Es gibt nur sechs mögliche Werte (0 bis 5), und
        # jeder steht als Ziffer in seiner Zelle. Eine Skala erklärt damit
        # nichts, was nicht schon dasteht -- sie kostete nur Breite, die der
        # Heatmap in einer halben Spalte fehlt.
        showscale=False,
    ))
    fig_heat.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Punkte je Kategorie und Monat (0 bis 5, ohne Joker)", font=dict(size=16)),
        xaxis=dict(tickfont=dict(size=12)),
        yaxis=dict(tickfont=dict(size=11), automargin=True),
        height=CHART_H,
    )
    st.plotly_chart(fig_heat, width='content', config=PLOTLY_CONFIG)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# ROW 3: Category Development over time (Line Chart)
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">Kategorie-Entwicklung</div>', unsafe_allow_html=True)

# Short category names for legend
CAT_SHORT = {
    "Aktuelles": "Akt.",
    "Essen/Trinken": "Essen",
    "Film/Fernsehen": "Film",
    "Geographie": "Geo.",
    "Geschichte": "Gesch.",
    "Kunst/Literatur": "Kunst",
    "Musik": "Musik",
    "Rel./Mythol.": "Rel.",
    "Sport": "Sport",
    "Verschiedenes": "Versch.",
    "Wissensch./Natur": "Wissen.",
}

# Eine Spur je Kategorie, Reihenfolge und Farbe über alle Monate FEST.
# Vorher wurde der Stapel in jedem Monat neu nach Punktzahl sortiert: Jede
# Kategorie wechselte damit monatlich ihre Position, und genau das machte
# eine Entwicklung -- den Zweck des Diagramms -- unverfolgbar. Fest
# gestapelt behält jede Kategorie ihr Band, das über die Monate dicker
# oder dünner wird.
df_dev = df_cat[df_cat["Kategorie"] != "Sonderrunde"].copy()
df_dev = df_dev.sort_values("Mittelwert", ascending=False)
all_cats = df_dev["Kategorie"].tolist()
cat_color_map = {cat: CAT_COLORS[i % len(CAT_COLORS)] for i, cat in enumerate(all_cats)}
fig_dev2 = go.Figure()

# Plotly stapelt die zuerst hinzugefügte Spur unten, und all_cats ist nach
# Mittelwert absteigend sortiert -- die stärkste Kategorie kommt also zuerst
# und landet damit an der Nulllinie, wo sich am besten ablesen lässt.
for cat in all_cats:
    werte = [int(df_cat[df_cat["Kategorie"] == cat].iloc[0][m]) for m in months]
    fig_dev2.add_trace(go.Bar(
        x=months,
        y=werte,
        name=CAT_SHORT.get(cat, cat),
        legendgroup=cat,
        text=[CAT_SHORT.get(cat, cat) if v >= 3 else "" for v in werte],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(size=10, color=_lesefarbe(cat_color_map[cat])),
        marker=dict(
            color=cat_color_map[cat],
            line=dict(width=0.5, color="#ffffff"),
        ),
        hovertemplate=f"%{{x}}: {cat} %{{y}}/5<extra></extra>",
    ))

fig_dev2.update_layout(
    **PLOTLY_LAYOUT,
    # Kurzer Titel mit Bedacht: Der frühere Zusatz "(feste Reihenfolge,
    # stärkste unten)" machte ihn 64 Zeichen lang -- auf 390 px Telefonbreite
    # lief er bis 505 px und war damit rechts abgeschnitten. Was er erklärte,
    # steht ohnehin im Fließtext unter dem Diagramm.
    title=dict(text="Monatssumme nach Kategorie", font=dict(size=16)),
    barmode="stack",
    yaxis=dict(title="Punkte (ohne Sonderrunde und Joker)",
               gridcolor="rgba(0,0,0,0.05)"),
    xaxis=dict(gridcolor="rgba(0,0,0,0.05)", automargin=True),
    showlegend=True,
    # Legende am unteren Figurenrand verankert (yref="container"), nicht an
    # der Zeichenfläche: Bei y=-0.12 relativ zur Fläche lag sie auf dem Telefon
    # über den Monatsnamen und verdeckte sie vollständig -- elf Einträge
    # brauchen dort drei Zeilen statt der einen, die am Schirm reicht. Vom
    # Figurenrand aus gemessen bleibt der Abstand in jeder Breite derselbe.
    legend=dict(orientation="h", yref="container", yanchor="bottom", y=0.01,
                xanchor="center", x=0.5, font=dict(size=10),
                traceorder="reversed"),
    height=CHART_H_TALL,
)
# margin steckt bereits in PLOTLY_LAYOUT; der untere Rand wird hier erhoeht,
# damit die abgesenkte Legende Platz findet.
fig_dev2.update_layout(margin_b=130)
st.plotly_chart(fig_dev2, width='content', config=PLOTLY_CONFIG)
st.markdown(
    '<p class="info-text">Jede Kategorie behält Farbe und Position über alle '
    'Monate &ndash; ihr Band lässt sich so von links nach rechts verfolgen. '
    'Die Gesamthöhe ist die Punktsumme der elf Kategorien ohne Sonderrunde '
    'und ohne Joker-Punkte.</p>',
    unsafe_allow_html=True,
)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# ROW 4: Sonderrunde + Joker + Consistency
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">Spezialauswertungen</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    # Sonderrunden: waagerechte Balken, Thema und Monat auf der y-Achse.
    # Senkrecht standen zehn Themennamen nebeneinander unter den Balken und
    # ueberschrieben einander bis zur Unlesbarkeit -- "Albrecht Duerer" und
    # "Sixtinische Kapelle" brauchen Platz, den eine Drittel-Spalte nicht hat.
    # Auf einer Achse stehen die Namen gesetzt, und die Zeitreihe liest sich
    # von oben nach unten.
    sonder_themen = [q["Sonderrunde_Thema"] for q in quiz_nights]
    sonder_scores = [q["cat_scores"].get("Sonderrunde", 0) for q in quiz_nights]
    sonder_labels = [f"{t}<br>({q['Monat']})" for t, q in zip(sonder_themen, quiz_nights)]

    # Farbe nach Themenart statt nach Punktzahl: Die Punktzahl steht bereits
    # als Balkenlänge da, die Themenart dagegen ist die eigentliche Erkenntnis
    # -- klassische Themen gingen bislang ausnahmslos leer aus.
    # "sonst" trug bis hierher #bab0ac -- ein Hellgrau, das als Balken taugt,
    # als Schriftfarbe der Themennamen aber nur 2,2:1 gegen Weiß erreichte:
    # "Landkreise in Mittelfranken", "Biene Maja" und "14 Achttausender"
    # standen damit grau auf grau. #6f6a65 bringt 5,2:1 und bleibt ein
    # neutrales Grau zwischen dem Blau und dem Rotbraun.
    ART_FARBE = {"klassisch": "#9b4d4d", "popkultur": "#2171b5", "sonst": "#6f6a65"}
    ART_NAME = {"klassisch": "klassisch", "popkultur": "Popkultur", "sonst": "übrige"}
    sonder_arten = [qd._classify_theme(t) if qd else "sonst" for t in sonder_themen]
    sonder_colors = [ART_FARBE.get(a, ART_FARBE["sonst"]) for a in sonder_arten]

    # Plotly zeichnet das erste Element unten: umkehren stellt den
    # aeltesten Abend nach oben.
    fig_sonder = go.Figure()
    fig_sonder.add_trace(go.Bar(
        y=sonder_labels[::-1],
        x=sonder_scores[::-1],
        orientation="h",
        marker=dict(color=sonder_colors[::-1], line=dict(width=0)),
        text=sonder_scores[::-1],
        textposition="outside",
        textfont=dict(color="#374151", size=13),
        cliponaxis=False,
        hovertemplate="%{y}: %{x}/5 Punkte<extra>Sonderrunde</extra>",
    ))
    fig_sonder.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Sonderrunden-Ergebnisse", font=dict(size=16)),
        xaxis=dict(range=[0, 5.5], tickvals=[0, 1, 2, 3, 4, 5],
                   gridcolor="rgba(0,0,0,0.05)", title="Punkte (max. 5, ohne Joker)"),
        # Die Themenart gehört auf die Beschriftung, nicht nur auf den Balken:
        # Die klassischen Themen brachten ausnahmslos null Punkte, haben also
        # gar keinen Balken, der eine Farbe tragen könnte -- ausgerechnet dort
        # wäre sie am aussagekräftigsten.
        yaxis=dict(tickfont=dict(size=10), automargin=True,
                   tickmode="array",
                   tickvals=sonder_labels[::-1],
                   ticktext=[f'<span style="color:{ART_FARBE.get(a, ART_FARBE["sonst"])}">{lbl}</span>'
                             for lbl, a in zip(sonder_labels[::-1], sonder_arten[::-1])]),
        height=CHART_H_TALL,
        bargap=0.25,
    )
    st.plotly_chart(fig_sonder, width='content', config=PLOTLY_CONFIG)

    # Nur die Farblegende: Was die Themenarten im Mittel bringen und was
    # daraus folgt, steht unten unter "Erkenntnisse" -- dieselbe Aussage
    # zweimal auf einer Seite wäre genau die Redundanz, die hier sonst
    # ausgeräumt wurde.
    _legende = [
        f'<span class="farbprobe" style="background:{ART_FARBE[_a]};"></span>{ART_NAME[_a]}'
        for _a in ("popkultur", "sonst", "klassisch")
        if _a in set(sonder_arten)
    ]
    st.markdown(
        '<p class="info-text">Farbe = Themenart: '
        + ' &nbsp;·&nbsp; '.join(_legende)
        + '</p>',
        unsafe_allow_html=True,
    )

with col2:
    # Joker analysis – doubles score only if >= 3 correct
    joker_months = [q["Monat"] for q in quiz_nights]
    # Joker kann None sein (Abend ohne Joker) -> 0 Punkte, kein Bonus.
    joker1_scores = [q["cat_scores"].get(q["Joker1"] or "", 0) for q in quiz_nights]
    joker2_scores = [q["cat_scores"].get(q["Joker2"] or "", 0) for q in quiz_nights]
    # Bonus only triggers at >= 3
    joker_bonus = [
        (j1 if j1 >= 3 else 0) + (j2 if j2 >= 3 else 0)
        for j1, j2 in zip(joker1_scores, joker2_scores)
    ]
    max_bonus = 10  # 2 × 5
    joker_pct = [b / max_bonus for b in joker_bonus]

    fig_joker = go.Figure()
    fig_joker.add_trace(go.Bar(
        x=joker_months,
        y=joker_bonus,
        text=[f"{b}/{max_bonus}" for b in joker_bonus],
        textposition="outside",
        textfont=dict(color="#374151", size=12),
        marker=dict(color="#2171b5", line=dict(width=0)),
        hovertemplate="%{x}: %{y} Joker-Bonus<extra></extra>",
    ))

    avg_joker_pct = np.mean(joker_pct)
    fig_joker.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text=f"Joker-Bonus (Ø {avg_joker_pct:.0%} von max. {max_bonus})",
                   font=dict(size=16)),
        yaxis=dict(range=[0, 11], gridcolor="rgba(0,0,0,0.05)", title="Joker-Punkte",
                   dtick=2),
        showlegend=False,
        height=CHART_H,
        bargap=0.3,
    )
    st.plotly_chart(fig_joker, width='content', config=PLOTLY_CONFIG)
    st.markdown(
        '<p class="info-text">Joker verdoppelt die Kategorie-Punkte, '
        'aber nur ab min. 3 Richtigen. Unter 3 verfällt der Joker.</p>',
        unsafe_allow_html=True,
    )

with col3:
    # Verlässlichkeit: Kategorien stehen auf der y-Achse, sortiert nach
    # Streuung. Ersetzt den früheren Scatter mit handgesetzten Label-
    # Positionen -- dessen Punkte wanderten mit jedem Abend, die festen
    # Pixel-Offsets wanderten nicht mit und mieden Kollisionen, die es
    # längst nicht mehr gab. Auf einer Achse stehen die Namen gesetzt.
    df_cons = df_cat[df_cat["Kategorie"] != "Sonderrunde"].copy()
    df_cons["Std"] = df_cons[months].std(axis=1)
    df_cons["Min"] = df_cons[months].min(axis=1)
    df_cons["Max"] = df_cons[months].max(axis=1)
    # Plotly zeichnet das erste Element unten: absteigend sortieren stellt
    # die verlässlichste Kategorie nach oben.
    df_cons = df_cons.sort_values("Std", ascending=False).reset_index(drop=True)
    cats_y = df_cons["Kategorie"].tolist()

    # Die Farbe trägt die Stärke, in denselben Stufen wie das Ranking links
    # -- so lassen sich beide Kategorie-Diagramme zusammen lesen.
    def _staerke_farbe(val):
        if val >= 3.2:
            return "#08519c"
        if val >= 2.8:
            return "#2171b5"
        if val >= 2.5:
            return "#6baed6"
        return "#c6dbef"

    cons_colors = [_staerke_farbe(v) for v in df_cons["Mittelwert"]]

    fig_cons = go.Figure()

    # Hinterste Ebene: beobachtete Spanne vom schlechtesten bis zum besten Abend.
    x_spanne, y_spanne = [], []
    for cat, lo, hi in zip(cats_y, df_cons["Min"], df_cons["Max"]):
        x_spanne += [lo, hi, None]
        y_spanne += [cat, cat, None]
    fig_cons.add_trace(go.Scatter(
        x=x_spanne, y=y_spanne,
        mode="lines",
        line=dict(color="#d1d5db", width=2),
        hoverinfo="skip",
        showlegend=False,
    ))

    # Mittelwert als Punkt, Streuung als Balken darum.
    fig_cons.add_trace(go.Scatter(
        x=df_cons["Mittelwert"], y=cats_y,
        mode="markers",
        error_x=dict(type="data", array=df_cons["Std"],
                     color="#6b7280", thickness=3, width=0),
        marker=dict(size=13, color=cons_colors,
                    line=dict(width=1.5, color="#ffffff")),
        hovertemplate="%{y}: Ø %{x:.2f} Pkt.<extra></extra>",
        showlegend=False,
    ))

    # Zahlenspalte am rechten Rand: die Streuung je Kategorie.
    fig_cons.add_trace(go.Scatter(
        x=[5.45] * len(cats_y), y=cats_y,
        mode="text",
        text=[f"σ {_de(s, 2)}" for s in df_cons["Std"]],
        textposition="middle center",
        textfont=dict(size=11, color="#6b7280"),
        hoverinfo="skip",
        showlegend=False,
    ))

    fig_cons.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text=f"Verlässlichkeit je Kategorie ({n_nights} Abende)",
                   font=dict(size=16)),
        xaxis=dict(title="Punkte je Abend (max. 5, ohne Joker)",
                   range=[-0.2, 5.9], tickvals=[0, 1, 2, 3, 4, 5],
                   gridcolor="rgba(0,0,0,0.05)"),
        yaxis=dict(tickfont=dict(size=11), automargin=True),
        height=CHART_H_TALL,
    )
    st.plotly_chart(fig_cons, width='content', config=PLOTLY_CONFIG)
    st.markdown(
        '<p class="info-text">Punkt = Mittelwert, grauer Balken = ±σ, '
        'helle Linie = schlechtester bis bester Abend. Nach unten nimmt die '
        'Schwankung zu; die Farbe trägt die Stärke wie im Ranking links.<br>'
        '<b>Joker-Tipp:</b> dunkle Punkte weit rechts mit kurzem Balken &ndash; '
        'dort ist eine hohe Punktzahl am wahrscheinlichsten. Lange Balken sind '
        'riskant: mal top, mal flop.</p>',
        unsafe_allow_html=True,
    )

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# ERKENNTNISSE
# ---------------------------------------------------------------------------
# Dieselben abgeleiteten Beobachtungen, die der Erkenntnisse-Reiter der
# Eingabe-GUI zeigt -- compute_insights() ist die eine Quelle dafür, hier
# wird sie nur anders dargestellt.
_sektionen = []
if qd is not None:
    try:
        _sektionen = qd.compute_insights(quiz_nights)
    except Exception:  # pragma: no cover - Deployment-Absicherung
        _sektionen = []

if _sektionen:
    st.markdown('<div class="section-title">Erkenntnisse</div>', unsafe_allow_html=True)
    KIND_FARBE = {"info": "#2171b5", "tipp": "#4b7c6f", "warnung": "#9b4d4d"}
    _spalten = st.columns(2)
    # Nicht abwechselnd verteilen: Die Sektionen sind verschieden lang (drei
    # bis neun Beobachtungen), und streng alternierend geriete eine Spalte
    # deutlich länger als die andere. Jede Sektion geht in die derzeit
    # kürzere Spalte.
    _fuellstand = [0, 0]
    for _sek in sorted(_sektionen, key=lambda s: -len(s.get("items", []))):
        _i = 0 if _fuellstand[0] <= _fuellstand[1] else 1
        _fuellstand[_i] += len(_sek.get("items", [])) + 2
        teile = [f'<div class="insight-card">'
                 f'<div class="insight-titel">{_sek.get("titel", "")}</div>']
        if _sek.get("lead"):
            teile.append(f'<div class="insight-lead">{_sek["lead"]}</div>')
        for _it in _sek.get("items", []):
            _farbe = KIND_FARBE.get(_it.get("kind"), "#d1d5db")
            teile.append(f'<div class="insight-item" style="border-left-color:{_farbe};">'
                         f'{_it.get("text", "")}</div>')
        teile.append("</div>")
        _spalten[_i % 2].markdown("".join(teile), unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("""
<!-- #4b5563 statt #9ca3af: Das alte Grau erreichte auf dem Seitengrund nur
     2,2:1 und war bei 13 px kaum zu entziffern. -->
<div style="text-align:center; color:#4b5563; padding:2rem 0 1rem 0; font-size:0.8rem;">
    Kneipenquiz Schwabach Dashboard &mdash; Datenquelle: data.json &mdash; Built with Streamlit & Plotly
</div>
""", unsafe_allow_html=True)
