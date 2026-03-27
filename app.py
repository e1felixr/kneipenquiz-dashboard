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
        color: #6b7280;
        font-size: 1.1rem;
    }

    /* KPI cards */
    .kpi-card {
        background: #ffffff;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        padding: 1.2rem 1rem;
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

    /* Info text */
    .info-text {
        color: #6b7280;
        font-size: 0.85rem;
        margin-top: -0.5rem;
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
        /* Smaller charts on mobile */
        .stPlotlyChart {
            max-height: 300px;
        }
        /* Force Streamlit columns to stack vertically */
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
        }
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
    }

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Load pre-computed data from JSON (fast, no openpyxl needed)
# ---------------------------------------------------------------------------
import pathlib
DATA_PATH = pathlib.Path(__file__).parent / "data.json"

@st.cache_data
def load_data():
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    df_cat = pd.DataFrame(data["categories"])
    months = ["Apr 25", "Mai 25", "Jul 25", "Sep 25", "Jan 26", "Mrz 26"]
    quiz_nights = data["quiz_nights"]
    return df_cat, months, quiz_nights

df_cat, months, quiz_nights = load_data()

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

# Gedeckte aber klar unterscheidbare Farben – 11 Kategorien
CAT_COLORS = [
    "#4e79a7", "#f28e2b", "#76b7b2", "#e15759", "#59a14f",
    "#edc948", "#b07aa1", "#9c755f", "#ff9da7", "#bab0ac",
    "#a0cbe8",
]

# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------
st.markdown("""
<div class="dashboard-header">
    <h1>🍺 Kneipenquiz Schwabach</h1>
    <p>Performance-Dashboard &mdash; 6 Quizabende &mdash; Apr 2025 bis Mrz 2026</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------------------------
total_points = sum(q["Gesamt"] for q in quiz_nights)
avg_pct = np.mean([q["Pct_richtig"] for q in quiz_nights])
placements = [q["Platzierung"] for q in quiz_nights if q["Platzierung"] is not None]
best_placement = min(placements) if placements else "–"
best_placement_q = min(
    [q for q in quiz_nights if q["Platzierung"] is not None],
    key=lambda q: q["Platzierung"],
)
avg_placement = np.mean(placements) if placements else 0

# Trend: last quiz vs previous quiz
prev_pct = quiz_nights[-2]["Pct_richtig"]
last_pct = quiz_nights[-1]["Pct_richtig"]
trend_delta = last_pct - prev_pct
trend_arrow = "↑" if trend_delta > 0 else "↓"
trend_class = "" if trend_delta > 0 else "bad"

cols = st.columns(6)
kpi_data = [
    ("Quizabende", "6", "seit Apr 2025", ""),
    ("Gesamtpunkte", str(total_points), f"Ø {total_points/6:.0f} pro Abend", ""),
    ("Ø Richtig", f"{avg_pct:.0%}", f"von max. 60 Fragen", ""),
    ("Beste Platzierung", f"{best_placement}.", f"{best_placement_q['Monat']} ({best_placement_q['Von']} Teams)", ""),
    ("Ø Platzierung", f"{avg_placement:.1f}",
     f"bei Ø {np.mean([q['Von'] for q in quiz_nights if q['Von']]):.1f} Teams", ""),
    ("Trend Richtig-Quote", f"{trend_arrow} {abs(trend_delta):.0%}",
     f"vs. {quiz_nights[-2]['Monat']}", trend_class),
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

# --- Second row of KPI cards: category insights ---
df_no_sonder = df_cat[df_cat["Kategorie"] != "Sonderrunde"]
best_cat = df_no_sonder.loc[df_no_sonder["Mittelwert"].idxmax()]
worst_cat = df_no_sonder.loc[df_no_sonder["Mittelwert"].idxmin()]

perfect_scores = []
for _, row in df_no_sonder.iterrows():
    for m in months:
        if row[m] == 5:
            perfect_scores.append(f"{row['Kategorie']} ({m})")

improvements = {}
for _, row in df_no_sonder.iterrows():
    delta = np.mean([row["Jan 26"], row["Mrz 26"]]) - np.mean([row["Apr 25"], row["Mai 25"]])
    improvements[row["Kategorie"]] = delta
most_improved = max(improvements, key=improvements.get)

cols2 = st.columns(4)
kpi_data2 = [
    ("Stärkste Kategorie", best_cat["Kategorie"], f"Ø {best_cat['Mittelwert']:.1f}/5", ""),
    ("Schwächste Kategorie", worst_cat["Kategorie"], f"Ø {worst_cat['Mittelwert']:.1f}/5", "bad"),
    ("Meiste Verbesserung", most_improved,
     f"+{improvements[most_improved]:.1f} Pkt. (Ø erste 2 vs. letzte 2 Abende)", ""),
    ("Perfekte Runden", f"{len(perfect_scores)}x 5/5" if perfect_scores else "–",
     ", ".join(perfect_scores[:3]) if perfect_scores else "–", ""),
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

# --- Detail tables ---
st.markdown('<div class="section-title">Rohdaten</div>', unsafe_allow_html=True)

detail_rows_data = []
for q in quiz_nights:
    row = {
        "Monat": q["Monat"],
        "Joker 1": q["Joker1"],
        "Joker 2": q["Joker2"],
        "Sonderrunde": q["Sonderrunde_Thema"],
        "Teil 1": q["Teil1"],
        "Teil 2": q["Teil2"],
        "Teil 3": q["Teil3"],
        "Teil 4": q["Teil4"],
        "Bonus": q["Bonus"],
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

st.dataframe(
    df_detail,
    use_container_width=False,
    hide_index=True,
    column_config={
        "Teil 1": centered(st.column_config.NumberColumn("Teil 1", format="%d")),
        "Teil 2": centered(st.column_config.NumberColumn("Teil 2", format="%d")),
        "Teil 3": centered(st.column_config.NumberColumn("Teil 3", format="%d")),
        "Teil 4": centered(st.column_config.NumberColumn("Teil 4", format="%d")),
        "Bonus": centered(st.column_config.NumberColumn("Bonus", format="%d")),
        "Gesamt": st.column_config.ProgressColumn(
            "Gesamt", min_value=0, max_value=50, format="%d Pkt.",
        ),
        "% richtig": centered(st.column_config.NumberColumn("% richtig", format="%.0f %%")),
        "Platz": centered(st.column_config.NumberColumn("Platz", format="%d.")),
        "von": centered(st.column_config.NumberColumn("von", format="%d")),
    },
)

st.markdown("**Punkte pro Kategorie und Monat:**")
df_show = df_cat[["Kategorie", "Platz", "Mittelwert"] + months].copy()
df_show["Mittelwert"] = df_show["Mittelwert"].round(2)
df_show = df_show.sort_values("Platz")

st.dataframe(
    df_show,
    use_container_width=False,
    hide_index=True,
    column_config={
        "Platz": centered(st.column_config.NumberColumn("Platz", format="%d")),
        "Mittelwert": st.column_config.ProgressColumn(
            "Ø", min_value=0, max_value=5, format="%.1f",
        ),
        **{m: centered(st.column_config.NumberColumn(m, format="%d")) for m in months},
    },
)

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
                yshift=18,
            ))

    fig_trend.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Platzierung & Quote pro Quizabend", font=dict(size=16)),
        annotations=annotations,
        yaxis=dict(
            title="% richtig", tickformat=".0%", range=[0, 1],
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
        height=420,
        bargap=0.4,
    )
    st.plotly_chart(fig_trend, use_container_width=False, config=PLOTLY_CONFIG)

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
        xaxis=dict(range=[0, 4.5], gridcolor="rgba(0,0,0,0.05)", title="Ø Punkte (max. 5)"),
        yaxis=dict(tickfont=dict(size=12)),
        height=420,
    )
    st.plotly_chart(fig_rank, use_container_width=False, config=PLOTLY_CONFIG)

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
        colorbar=dict(title="Punkte", tickvals=[0, 1, 2, 3, 4, 5]),
    ))
    fig_heat.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Punkte-Heatmap (Kategorien x Monate)", font=dict(size=16)),
        xaxis=dict(tickfont=dict(size=12)),
        yaxis=dict(tickfont=dict(size=11)),
        height=420,
    )
    st.plotly_chart(fig_heat, use_container_width=False, config=PLOTLY_CONFIG)

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

df_dev = df_cat[df_cat["Kategorie"] != "Sonderrunde"].copy()
df_dev = df_dev.sort_values("Mittelwert", ascending=False)
all_cats = df_dev["Kategorie"].tolist()
cat_color_map = {cat: CAT_COLORS[i % len(CAT_COLORS)] for i, cat in enumerate(all_cats)}
bar_half = 0.4
fig_dev2 = go.Figure()

# For each month, sort categories by their score
sorted_month_data = {}
for m in months:
    cat_vals = [(cat, df_cat[df_cat["Kategorie"] == cat].iloc[0][m]) for cat in all_cats]
    cat_vals.sort(key=lambda x: x[1], reverse=True)  # best at bottom
    sorted_month_data[m] = cat_vals

# We need to add one trace per "slot" (position in stack, 0=bottom to 10=top)
# Each slot can have a different category per month
n_cats = len(all_cats)
cumulative2 = {m: 0 for m in months}
all_connector_x = []
all_connector_y = []

for slot in range(n_cats):
    slot_vals = []
    slot_cats = []
    slot_colors = []
    for m in months:
        cat, val = sorted_month_data[m][slot]
        slot_vals.append(val)
        slot_cats.append(cat)
        slot_colors.append(cat_color_map[cat])

    short_labels = [CAT_SHORT.get(c, c) if v >= 2 else "" for c, v in zip(slot_cats, slot_vals)]
    hover_labels = [f"{m}: {c} {v}/5" for m, c, v in zip(months, slot_cats, slot_vals)]

    # Track tops for connectors
    tops2 = []
    for j, m in enumerate(months):
        tops2.append(cumulative2[m] + slot_vals[j])
        cumulative2[m] += slot_vals[j]
    all_connector_x.extend([j + bar_half, j + 1 - bar_half, None] for j in range(len(months) - 1))
    all_connector_y.extend([tops2[j], tops2[j + 1], None] for j in range(len(months) - 1))

    fig_dev2.add_trace(go.Bar(
        x=months,
        y=slot_vals,
        name=f"Slot {slot}",
        text=short_labels,
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(size=10, color="#ffffff"),
        marker=dict(
            color=slot_colors,
            line=dict(width=0.5, color="#ffffff"),
        ),
        hovertext=hover_labels,
        hovertemplate="%{hovertext}<extra></extra>",
    ))

# Single connector trace instead of 55 shapes
flat_cx = [v for seg in all_connector_x for v in seg]
flat_cy = [v for seg in all_connector_y for v in seg]
fig_dev2.add_trace(go.Scatter(
    x=flat_cx, y=flat_cy, mode="lines",
    line=dict(color="rgba(0,0,0,0.18)", width=1),
    showlegend=False, hoverinfo="skip",
))

fig_dev2.update_layout(
    **PLOTLY_LAYOUT,
    title=dict(text="Punkte pro Kategorie (sortiert, beste unten)", font=dict(size=16)),
    barmode="stack",
    yaxis=dict(title="Gesamtpunkte", gridcolor="rgba(0,0,0,0.05)"),
    xaxis=dict(gridcolor="rgba(0,0,0,0.05)"),
    showlegend=False,
    height=480,
)
st.plotly_chart(fig_dev2, use_container_width=False, config=PLOTLY_CONFIG)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# ROW 4: Sonderrunde + Joker + Consistency
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">Spezialauswertungen</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    # Sonderrunde analysis
    sonder_themen = [q["Sonderrunde_Thema"] for q in quiz_nights]
    sonder_scores = [q["cat_scores"].get("Sonderrunde", 0) for q in quiz_nights]
    sonder_labels = [f"{t}<br>({q['Monat']})" for t, q in zip(sonder_themen, quiz_nights)]

    sonder_colors = ["#2171b5" if s >= 4 else "#6baed6" if s >= 2 else "#c6dbef" for s in sonder_scores]

    fig_sonder = go.Figure()
    fig_sonder.add_trace(go.Bar(
        x=sonder_labels,
        y=sonder_scores,
        marker=dict(color=sonder_colors, line=dict(width=0)),
        text=sonder_scores,
        textposition="outside",
        textfont=dict(color="#374151", size=14),
        hovertemplate="%{x}: %{y}/5 Punkte<extra>Sonderrunde</extra>",
    ))
    fig_sonder.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Sonderrunden-Ergebnisse", font=dict(size=16)),
        yaxis=dict(range=[0, 6], gridcolor="rgba(0,0,0,0.05)", title="Punkte"),
        xaxis=dict(tickfont=dict(size=9), tickangle=0),
        height=420,
    )
    st.plotly_chart(fig_sonder, use_container_width=False, config=PLOTLY_CONFIG)

with col2:
    # Joker analysis – doubles score only if >= 3 correct
    joker_months = [q["Monat"] for q in quiz_nights]
    joker1_scores = [q["cat_scores"].get(q["Joker1"], 0) for q in quiz_nights]
    joker2_scores = [q["cat_scores"].get(q["Joker2"], 0) for q in quiz_nights]
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
        yaxis=dict(range=[0, 11], gridcolor="rgba(0,0,0,0.05)", title="Bonuspunkte",
                   dtick=2),
        showlegend=False,
        height=400,
        bargap=0.3,
    )
    st.plotly_chart(fig_joker, use_container_width=False, config=PLOTLY_CONFIG)
    st.markdown(
        '<p class="info-text">Joker verdoppelt die Kategorie-Punkte, '
        'aber nur ab min. 3 Richtigen. Unter 3 verfällt der Joker.</p>',
        unsafe_allow_html=True,
    )

with col3:
    # Consistency – scatter: mean score vs std deviation
    df_cons = df_cat[df_cat["Kategorie"] != "Sonderrunde"].copy()
    df_cons["Std"] = df_cons[months].std(axis=1)

    fig_cons = go.Figure()

    # Alternate label positions to avoid overlaps
    positions = ["top center", "bottom center", "top right", "bottom left",
                 "top left", "bottom right", "middle right", "middle left",
                 "top center", "bottom center", "top right"]
    # Sort by Std so nearby points get different positions
    df_cons_sorted = df_cons.sort_values("Std").reset_index(drop=True)

    fig_cons.add_trace(go.Scatter(
        x=df_cons_sorted["Std"],
        y=df_cons_sorted["Mittelwert"],
        mode="markers",
        marker=dict(
            size=12,
            color=df_cons_sorted["Mittelwert"],
            colorscale=[[0, "#c6dbef"], [0.5, "#6baed6"], [1, "#2171b5"]],
            cmin=2, cmax=4,
            line=dict(width=1, color="#ffffff"),
        ),
        hovertemplate="%{text}<br>Ø %{y:.1f} Pkt. | σ %{x:.2f}<extra></extra>",
        text=df_cons_sorted["Kategorie"],
    ))

    # Add labels as annotations with individual positioning
    for i, row in df_cons_sorted.iterrows():
        pos = positions[i % len(positions)]
        xshift = {"top center": 0, "bottom center": 0, "top right": 8,
                  "bottom left": -8, "top left": -8, "bottom right": 8,
                  "middle right": 14, "middle left": -14}.get(pos, 0)
        yshift = {"top center": 12, "bottom center": -12, "top right": 10,
                  "bottom left": -10, "top left": 10, "bottom right": -10,
                  "middle right": 0, "middle left": 0}.get(pos, 0)
        fig_cons.add_annotation(
            x=row["Std"], y=row["Mittelwert"],
            text=row["Kategorie"], showarrow=False,
            font=dict(size=8, color="#374151"),
            xshift=xshift, yshift=yshift,
        )
    fig_cons.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Stärke vs. Konsistenz", font=dict(size=16)),
        xaxis=dict(title="Streuung σ (links = konstanter)", gridcolor="rgba(0,0,0,0.05)",
                   range=[0.3, 1.8]),
        yaxis=dict(title="Ø Punkte", gridcolor="rgba(0,0,0,0.05)",
                   range=[2, 3.8]),
        height=400,
    )
    st.plotly_chart(fig_cons, use_container_width=False, config=PLOTLY_CONFIG)
    st.markdown(
        '<p class="info-text">Oben links = stark &amp; konstant (ideal). '
        'Unten rechts = schwach &amp; schwankend.<br>'
        '<b>Joker-Tipp:</b> Kategorien oben links lohnen sich als Joker &ndash; '
        'hohe Punktzahl ist dort am wahrscheinlichsten. '
        'Kategorien rechts sind riskant: mal top, mal flop.</p>',
        unsafe_allow_html=True,
    )

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("""
<div style="text-align:center; color:#9ca3af; padding:2rem 0 1rem 0; font-size:0.8rem;">
    Kneipenquiz Schwabach Dashboard &mdash; Datenquelle: Kneipenquiz.xlsx &mdash; Built with Streamlit & Plotly
</div>
""", unsafe_allow_html=True)
