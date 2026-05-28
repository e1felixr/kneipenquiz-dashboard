"""
quiz_eingabe.py  –  Tkinter-Desktop-GUI fuer die Eingabe von Kneipenquiz-Abenden.

Kommentare/Docstrings: ae/oe/ue (ASCII).
Nutzer-sichtbarer Text: mit Umlauten.
"""

import pathlib
import sys
import time
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use("TkAgg")

from quiz_data import (
    CATEGORIES,
    GERMAN_MONTHS,
    DATA_PATH,
    load_data,
    save_data,
    quiznight_from_form,
    validate_form,
    format_monat,
    iso_to_monat,
    iso_to_monat_long,
    compute_bonus,
    compute_dashboard_data,
    compute_insights,
)


def _bind_combo_typeahead(combo):
    """Multi-Char-Lookup auf einer readonly-Combobox.

    'Ku' springt zur ersten Kategorie, die mit 'ku' beginnt. Der Buffer
    wird nach 800 ms Idle zurueckgesetzt; ohne Treffer wird der letzte
    Anschlag isoliert noch einmal probiert (Fallback).
    """
    combo._typeahead_buffer = ""
    combo._typeahead_last = 0.0

    def on_key(event):
        if not event.char or len(event.char) != 1:
            return
        ch = event.char.lower()
        if not (ch.isalpha() or ch == "/" or ch in "äöüß"):
            return
        now = time.monotonic()
        if now - combo._typeahead_last > 0.8:
            combo._typeahead_buffer = ""
        combo._typeahead_buffer += ch
        combo._typeahead_last = now

        values = combo.cget("values")
        if isinstance(values, str):
            values = values.split() if values else []
        for v in values:
            if v.lower().startswith(combo._typeahead_buffer):
                combo.set(v)
                combo.event_generate("<<ComboboxSelected>>")
                return
        combo._typeahead_buffer = ch
        for v in values:
            if v.lower().startswith(ch):
                combo.set(v)
                combo.event_generate("<<ComboboxSelected>>")
                return

    combo.bind("<KeyPress>", on_key)

# Icon-Pfad: im EXE-Modus aus sys._MEIPASS, sonst neben dem Modul.
if getattr(sys, "frozen", False):
    _BUNDLE = pathlib.Path(getattr(sys, "_MEIPASS", str(pathlib.Path(sys.executable).parent)))
else:
    _BUNDLE = pathlib.Path(__file__).parent
ICON_PATH = _BUNDLE / "icon.ico"

# ---------------------------------------------------------------------------
# Design-Konstanten
# ---------------------------------------------------------------------------
CORPORATE_GREEN = "#4a8f24"
CORPORATE_GREEN_HOVER = "#3a6d1b"
BACKGROUND = "#e5e7eb"
CARD_BG = "#ffffff"
TEXT_PRIMARY = "#333333"
TEXT_SECONDARY = "#666666"
ERROR_RED = "#ef4444"

FONT_FAMILY = "Roboto"  # Fallback Segoe UI
FONT_SMALL = (FONT_FAMILY, 8)
FONT_NORMAL = (FONT_FAMILY, 9)
FONT_HEADER = (FONT_FAMILY, 10, "bold")
FONT_TITLE = (FONT_FAMILY, 14, "bold")

PAD_LARGE = 15
PAD_MEDIUM = 10
PAD_SMALL = 5

VERSION = "0.1.0"

# Farbpalette fuer Kategorien (parallel zu app.py)
CAT_COLORS = [
    "#4e79a7", "#f28e2b", "#76b7b2", "#e15759", "#59a14f",
    "#edc948", "#b07aa1", "#9c755f", "#ff9da7", "#bab0ac",
    "#a0cbe8",
]


# ---------------------------------------------------------------------------
# Roboto-Registrierung
# ---------------------------------------------------------------------------
def _register_roboto():
    """Versucht Roboto-Regular.ttf zu registrieren; gibt den Fontnamen zurueck."""
    try:
        import ctypes
        import pathlib

        candidates = [
            pathlib.Path(__file__).parent / "fonts" / "Roboto-Regular.ttf",
            pathlib.Path("C:/Windows/Fonts/Roboto-Regular.ttf"),
        ]
        for p in candidates:
            if p.exists():
                ctypes.windll.gdi32.AddFontResourceExW(str(p), 0x10, 0)
                return "Roboto"
        return "Roboto"  # ttk waehlt selbst Fallback, wenn nicht installiert
    except Exception:
        return "Segoe UI"


# ---------------------------------------------------------------------------
# Haupt-Applikation
# ---------------------------------------------------------------------------
class QuizEingabeApp(tk.Tk):
    """Hauptfenster der Kneipenquiz-Eingabe-Anwendung."""

    def __init__(self):
        super().__init__()

        # Font registrieren und Tupel aktualisieren
        font_family = _register_roboto()
        self._patch_fonts(font_family)

        self.title(f"Kneipenquiz Schwabach v{VERSION}")
        self.geometry("1200x800")
        self._center_window(1200, 800)
        self.configure(bg=BACKGROUND)
        self.resizable(True, True)

        # Bier-Icon (still bei Fehler, falls Datei fehlt)
        try:
            if ICON_PATH.exists():
                self.iconbitmap(str(ICON_PATH))
        except Exception:
            pass

        # Anwendungsstatus
        self.quiz_nights = []
        self._mode = "inactive"   # "inactive" | "new" | ("edit", datum)

        self._setup_styles()
        self._build_ui()
        self._load_data()
        self._refresh_dashboard()
        self._refresh_insights()

    # ------------------------------------------------------------------
    # Font-Hilfsmethoden
    # ------------------------------------------------------------------
    def _patch_fonts(self, family):
        """Aktualisiert alle globalen Font-Tupel mit dem registrierten Fontnamen."""
        global FONT_SMALL, FONT_NORMAL, FONT_HEADER, FONT_TITLE, FONT_FAMILY
        FONT_FAMILY = family
        FONT_SMALL = (family, 8)
        FONT_NORMAL = (family, 9)
        FONT_HEADER = (family, 10, "bold")
        FONT_TITLE = (family, 14, "bold")

    def _center_window(self, w, h):
        """Zentriert das Fenster auf dem Bildschirm."""
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ------------------------------------------------------------------
    # ttk-Styles
    # ------------------------------------------------------------------
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background=BACKGROUND)
        style.configure("TLabelframe", background=BACKGROUND,
                        foreground=TEXT_PRIMARY, font=FONT_HEADER)
        style.configure("TLabelframe.Label", background=BACKGROUND,
                        foreground=TEXT_PRIMARY, font=FONT_HEADER)
        style.configure("TLabel", background=BACKGROUND,
                        foreground=TEXT_PRIMARY, font=FONT_NORMAL)
        style.configure("TButton", padding=(10, 5), font=FONT_NORMAL)

        style.configure("Accent.TButton", padding=(12, 6), font=FONT_HEADER,
                        background=CORPORATE_GREEN, foreground="white",
                        borderwidth=0)
        style.map("Accent.TButton",
                  background=[("active", CORPORATE_GREEN_HOVER),
                               ("disabled", "#9ca3af")],
                  foreground=[("disabled", "#e5e7eb")])

        style.configure("Danger.TButton", padding=(10, 5), font=FONT_NORMAL,
                        background=ERROR_RED, foreground="white", borderwidth=0)
        style.map("Danger.TButton",
                  background=[("active", "#b91c1c"), ("disabled", "#fca5a5")])

        style.configure("Treeview", font=FONT_NORMAL, rowheight=22,
                        background=CARD_BG, fieldbackground=CARD_BG)
        style.configure("Treeview.Heading", font=FONT_HEADER,
                        background=BACKGROUND, foreground=TEXT_PRIMARY)
        style.map("Treeview",
                  background=[("selected", CORPORATE_GREEN)],
                  foreground=[("selected", "white")])

        # Combobox: heller Hintergrund auch im readonly-Modus, damit es
        # nicht nach 'ausgegraut' aussieht.
        style.configure("TCombobox",
                        fieldbackground=CARD_BG,
                        background=CARD_BG,
                        foreground=TEXT_PRIMARY,
                        arrowcolor=TEXT_PRIMARY,
                        bordercolor="#9ca3af",
                        lightcolor=CARD_BG,
                        darkcolor=CARD_BG)
        style.map("TCombobox",
                  fieldbackground=[("readonly", CARD_BG),
                                   ("disabled", "#f3f4f6")],
                  background=[("readonly", CARD_BG)],
                  foreground=[("readonly", TEXT_PRIMARY),
                              ("disabled", "#9ca3af")],
                  selectbackground=[("readonly", CARD_BG)],
                  selectforeground=[("readonly", TEXT_PRIMARY)])

        # Popup-Listbox der Combobox: weisser Hintergrund, gruene Auswahl.
        self.option_add("*TCombobox*Listbox.background", CARD_BG)
        self.option_add("*TCombobox*Listbox.foreground", TEXT_PRIMARY)
        self.option_add("*TCombobox*Listbox.selectBackground", CORPORATE_GREEN)
        self.option_add("*TCombobox*Listbox.selectForeground", "white")
        self.option_add("*TCombobox*Listbox.font", FONT_NORMAL)

    # ------------------------------------------------------------------
    # UI-Aufbau
    # ------------------------------------------------------------------
    def _build_ui(self):
        """Baut alle Bereiche des Fensters auf."""
        self._build_header()
        self._build_statusbar()   # zuerst (wird side='bottom' gepackt)
        self._build_notebook()    # danach (fuellt den Rest)

    def _build_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True,
                           padx=PAD_LARGE, pady=(PAD_MEDIUM, 0))
        self._tab_eingabe = ttk.Frame(self.notebook)
        self._tab_dashboard = ttk.Frame(self.notebook)
        self._tab_insights = ttk.Frame(self.notebook)
        self.notebook.add(self._tab_eingabe, text="Eingabe")
        self.notebook.add(self._tab_dashboard, text="Dashboard")
        self.notebook.add(self._tab_insights, text="Erkenntnisse")
        self._build_table_block(self._tab_eingabe)
        self._build_form_block(self._tab_eingabe)
        self._build_dashboard_tab(self._tab_dashboard)
        self._build_insights_tab(self._tab_insights)
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    # --- 1. Header ---
    def _build_header(self):
        hdr = tk.Frame(self, bg=BACKGROUND)
        hdr.pack(fill="x", padx=PAD_LARGE, pady=(PAD_LARGE, 0))

        tk.Label(hdr, text="🍺 Kneipenquiz Schwabach",
                 font=FONT_TITLE, bg=BACKGROUND, fg=TEXT_PRIMARY
                 ).pack(anchor="w")
        tk.Label(hdr, text=f"Version {VERSION}",
                 font=FONT_SMALL, bg=BACKGROUND, fg=TEXT_SECONDARY
                 ).pack(anchor="w")

        sep = tk.Frame(self, height=3, bg=CORPORATE_GREEN)
        sep.pack(fill="x", padx=0, pady=(PAD_SMALL, 0))

    # --- 2. Tabellen-Block ---
    def _build_table_block(self, parent):
        outer = ttk.LabelFrame(parent, text="Bestehende Abende")
        outer.pack(fill="x", padx=PAD_LARGE, pady=(PAD_MEDIUM, 0))

        tree_frame = tk.Frame(outer, bg=BACKGROUND)
        tree_frame.pack(fill="x", padx=PAD_SMALL, pady=PAD_SMALL)

        cols = ("monat", "joker1", "joker2", "sonderrunde",
                "gesamt", "platz")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                 show="headings", height=8)

        headings = {
            "monat": ("Monat", 140, "w"),
            "joker1": ("Joker 1", 130, "w"),
            "joker2": ("Joker 2", 130, "w"),
            "sonderrunde": ("Sonderrunde", 180, "w"),
            "gesamt": ("Gesamt", 70, "center"),
            "platz": ("Platz / Von", 90, "center"),
        }
        for col, (heading, width, anchor) in headings.items():
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, anchor=anchor, stretch=False)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side="left", fill="x", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<Double-1>", lambda e: self._on_edit())

        # Buttons unterhalb der Tabelle
        btn_frame = tk.Frame(outer, bg=BACKGROUND)
        btn_frame.pack(fill="x", padx=PAD_SMALL, pady=(0, PAD_SMALL))

        self.btn_new = ttk.Button(btn_frame, text="+ Neuer Abend",
                                  style="Accent.TButton",
                                  command=self._on_new)
        self.btn_new.pack(side="left", padx=(0, PAD_SMALL))

        self.btn_edit = ttk.Button(btn_frame, text="Bearbeiten",
                                   state="disabled",
                                   command=self._on_edit)
        self.btn_edit.pack(side="left", padx=(0, PAD_SMALL))

        self.btn_delete = ttk.Button(btn_frame, text="Löschen",
                                     style="Danger.TButton",
                                     state="disabled",
                                     command=self._on_delete)
        self.btn_delete.pack(side="left")

    # --- 3. Formular-Block ---
    def _build_form_block(self, parent):
        self.form_frame = ttk.LabelFrame(parent, text="Eingabeformular")
        self.form_frame.pack(fill="both", expand=True,
                             padx=PAD_LARGE, pady=(PAD_MEDIUM, 0))

        # Status-Label ganz oben
        self.lbl_mode = ttk.Label(self.form_frame, text="Modus: inaktiv",
                                  font=FONT_NORMAL, foreground=TEXT_SECONDARY)
        self.lbl_mode.grid(row=0, column=0, columnspan=2,
                           sticky="w", padx=PAD_MEDIUM, pady=(PAD_SMALL, 0))

        # Zweispaltig
        self._build_left_panel()
        self._build_right_panel()

        # Spaltengewichte
        self.form_frame.columnconfigure(0, weight=0)
        self.form_frame.columnconfigure(1, weight=1)

        # Aktions-Buttons
        self._build_form_buttons()

        # Initiale Deaktivierung
        self._set_form_state("disabled")

    def _build_left_panel(self):
        """Linke Spalte: Eckdaten."""
        lf = ttk.LabelFrame(self.form_frame, text="Eckdaten")
        lf.grid(row=1, column=0, sticky="nsew",
                padx=(PAD_MEDIUM, PAD_SMALL), pady=PAD_SMALL)
        self._left_frame = lf

        # Monat / Jahr
        ttk.Label(lf, text="Monat:").grid(
            row=0, column=0, sticky="w", padx=PAD_SMALL, pady=2)
        self.cmb_monat = ttk.Combobox(lf, values=GERMAN_MONTHS, state="readonly",
                                      width=8, font=FONT_NORMAL)
        self.cmb_monat.grid(row=0, column=1, sticky="w",
                            padx=PAD_SMALL, pady=2)

        ttk.Label(lf, text="Jahr:").grid(
            row=0, column=2, sticky="w", padx=(PAD_MEDIUM, PAD_SMALL), pady=2)
        self.spn_jahr = ttk.Spinbox(lf, from_=2024, to=2099, width=6,
                                    font=FONT_NORMAL)
        self.spn_jahr.grid(row=0, column=3, sticky="w",
                           padx=PAD_SMALL, pady=2)

        # Joker 1
        ttk.Label(lf, text="Joker 1:").grid(
            row=1, column=0, sticky="w", padx=PAD_SMALL, pady=2)
        self.cmb_joker1 = ttk.Combobox(lf, values=list(CATEGORIES),
                                        state="readonly", width=18,
                                        font=FONT_NORMAL)
        self.cmb_joker1.grid(row=1, column=1, columnspan=3, sticky="w",
                              padx=PAD_SMALL, pady=2)
        _bind_combo_typeahead(self.cmb_joker1)
        self.cmb_joker1.bind("<<ComboboxSelected>>", lambda e: self._recalc())

        # Joker 2
        ttk.Label(lf, text="Joker 2:").grid(
            row=2, column=0, sticky="w", padx=PAD_SMALL, pady=2)
        self.cmb_joker2 = ttk.Combobox(lf, values=list(CATEGORIES),
                                        state="readonly", width=18,
                                        font=FONT_NORMAL)
        self.cmb_joker2.grid(row=2, column=1, columnspan=3, sticky="w",
                              padx=PAD_SMALL, pady=2)
        _bind_combo_typeahead(self.cmb_joker2)
        self.cmb_joker2.bind("<<ComboboxSelected>>", lambda e: self._recalc())

        # Sonderrunden-Thema
        ttk.Label(lf, text="Sonderrunde Thema:").grid(
            row=3, column=0, sticky="w", padx=PAD_SMALL, pady=2)
        self.ent_sonderrunde = ttk.Entry(lf, width=22, font=FONT_NORMAL)
        self.ent_sonderrunde.grid(row=3, column=1, columnspan=3, sticky="ew",
                                   padx=PAD_SMALL, pady=2)

        # Platz / Von
        ttk.Label(lf, text="Platz:").grid(
            row=4, column=0, sticky="w", padx=PAD_SMALL, pady=2)
        self.spn_platz = ttk.Spinbox(lf, from_=1, to=50, width=5,
                                     font=FONT_NORMAL)
        self.spn_platz.grid(row=4, column=1, sticky="w",
                             padx=PAD_SMALL, pady=2)

        ttk.Label(lf, text="Von:").grid(
            row=4, column=2, sticky="w", padx=(PAD_MEDIUM, PAD_SMALL), pady=2)
        self.spn_von = ttk.Spinbox(lf, from_=1, to=50, width=5,
                                    font=FONT_NORMAL)
        self.spn_von.grid(row=4, column=3, sticky="w",
                          padx=PAD_SMALL, pady=2)

        # Bonus (Live-Anzeige, wird aus den Jokern berechnet)
        ttk.Label(lf, text="Bonus (aus Joker):").grid(
            row=5, column=0, sticky="w", padx=PAD_SMALL, pady=2)
        self.lbl_bonus_value = ttk.Label(lf, text="0 Pkt.",
                                          font=FONT_NORMAL,
                                          foreground=TEXT_PRIMARY)
        self.lbl_bonus_value.grid(row=5, column=1, columnspan=3,
                                   sticky="w", padx=PAD_SMALL, pady=2)

        # Trennlinie
        sep = ttk.Separator(lf, orient="horizontal")
        sep.grid(row=6, column=0, columnspan=4, sticky="ew",
                 padx=PAD_SMALL, pady=PAD_SMALL)

        # Live-Anzeige Gesamt
        self.lbl_gesamt = ttk.Label(lf, text="Gesamt: 0 Pkt.",
                                    font=FONT_HEADER, foreground=TEXT_PRIMARY)
        self.lbl_gesamt.grid(row=7, column=0, columnspan=4,
                              sticky="w", padx=PAD_SMALL, pady=2)

        # Live-Anzeige Prozent
        self.lbl_pct = ttk.Label(lf, text="% richtig: 0.0 %",
                                  font=FONT_NORMAL, foreground=TEXT_SECONDARY)
        self.lbl_pct.grid(row=8, column=0, columnspan=4,
                           sticky="w", padx=PAD_SMALL, pady=2)

    def _build_right_panel(self):
        """Rechte Spalte: vier Teil-Frames."""
        right = ttk.Frame(self.form_frame)
        right.grid(row=1, column=1, sticky="nsew",
                   padx=(PAD_SMALL, PAD_MEDIUM), pady=PAD_SMALL)
        self._right_frame = right

        # 12 IntVars fuer Punkte, Comboboxen fuer Kategorien
        self._punkt_vars = []   # [teil][slot] -> IntVar
        self._cat_cmbs = []     # [teil][slot] -> Combobox
        self._teil_sum_labels = []  # [teil] -> Label

        for t in range(4):
            lf = ttk.LabelFrame(right, text=f"Teil {t + 1}")
            lf.grid(row=t, column=0, sticky="ew",
                    padx=0, pady=(0, PAD_SMALL))
            right.columnconfigure(0, weight=1)

            teil_vars = []
            teil_cmbs = []

            for s in range(3):
                var = tk.IntVar(value=0)
                var.trace_add("write", self._recalc)
                teil_vars.append(var)

                cmb = ttk.Combobox(lf, values=list(CATEGORIES), state="readonly",
                                   width=20, font=FONT_NORMAL)
                cmb.grid(row=s, column=0, sticky="w",
                         padx=PAD_SMALL, pady=1)
                _bind_combo_typeahead(cmb)
                cmb.bind("<<ComboboxSelected>>", lambda e: self._recalc())
                teil_cmbs.append(cmb)

                spn = ttk.Spinbox(lf, from_=0, to=5, width=4,
                                  textvariable=var, font=FONT_NORMAL)
                spn.grid(row=s, column=1, sticky="w",
                         padx=(PAD_SMALL, PAD_MEDIUM), pady=1)

            # Summen-Label
            lbl_sum = ttk.Label(lf, text=f"Summe Teil {t + 1}: 0",
                                 font=FONT_NORMAL, foreground=TEXT_SECONDARY)
            lbl_sum.grid(row=3, column=0, columnspan=2,
                          sticky="w", padx=PAD_SMALL, pady=(1, PAD_SMALL))

            self._punkt_vars.append(teil_vars)
            self._cat_cmbs.append(teil_cmbs)
            self._teil_sum_labels.append(lbl_sum)

    def _build_form_buttons(self):
        """Aktions-Buttons unter dem Formular."""
        btn_frame = tk.Frame(self.form_frame, bg=BACKGROUND)
        btn_frame.grid(row=2, column=0, columnspan=2,
                       sticky="ew", padx=PAD_MEDIUM, pady=(0, PAD_SMALL))

        self.btn_save = ttk.Button(btn_frame, text="💾 Speichern",
                                   style="Accent.TButton",
                                   command=self._on_save)
        self.btn_save.pack(side="left", padx=(0, PAD_SMALL))

        self.btn_reset = ttk.Button(btn_frame, text="↶ Zurücksetzen",
                                    command=self._on_reset)
        self.btn_reset.pack(side="left", padx=(0, PAD_SMALL))

        self.btn_cancel = ttk.Button(btn_frame, text="✕ Abbrechen",
                                     command=self._on_cancel)
        self.btn_cancel.pack(side="left")

        self._form_action_buttons = [self.btn_save, self.btn_reset,
                                     self.btn_cancel]

    # --- 4. Statuszeile ---
    def _build_statusbar(self):
        status_frame = tk.Frame(self, bg=BACKGROUND)
        status_frame.pack(side="bottom", fill="x", padx=PAD_LARGE,
                          pady=(PAD_SMALL, PAD_MEDIUM))

        self.lbl_status = tk.Label(status_frame, text="",
                                   font=FONT_SMALL, bg=BACKGROUND,
                                   fg=TEXT_SECONDARY, anchor="w")
        self.lbl_status.pack(fill="x")

    # --- 5. Dashboard-Reiter ---
    def _build_dashboard_tab(self, parent):
        """Baut den Dashboard-Reiter: KPI-Karten oben, Charts unten."""
        # KPI-Karten oben
        self._kpi_frame = tk.Frame(parent, bg=BACKGROUND)
        self._kpi_frame.pack(fill="x", padx=PAD_MEDIUM, pady=(PAD_MEDIUM, PAD_SMALL))

        self._kpi_cards = []  # Liste von dicts {label, value, sub}
        KPI_LABELS = [
            "Quizabende", "Ø Richtig", "Beste Platzierung",
            "Ø Platzierung", "Stärkste Kategorie", "Schwächste Kategorie",
        ]
        for i, label in enumerate(KPI_LABELS):
            card = tk.Frame(self._kpi_frame, bg=CARD_BG,
                            highlightbackground="#d1d5db", highlightthickness=1)
            card.grid(row=0, column=i, sticky="nsew", padx=4, pady=2)
            lbl_label = tk.Label(card, text=label.upper(),
                                 font=(FONT_FAMILY, 7), bg=CARD_BG, fg=TEXT_SECONDARY)
            lbl_label.pack(anchor="w", padx=8, pady=(8, 0))
            lbl_value = tk.Label(card, text="–", font=FONT_HEADER,
                                 bg=CARD_BG, fg=TEXT_PRIMARY)
            lbl_value.pack(anchor="w", padx=8, pady=0)
            lbl_sub = tk.Label(card, text="", font=(FONT_FAMILY, 7),
                               bg=CARD_BG, fg=TEXT_SECONDARY, wraplength=140,
                               justify="left")
            lbl_sub.pack(anchor="w", padx=8, pady=(0, 8), fill="x")
            self._kpi_frame.columnconfigure(i, weight=1)
            self._kpi_cards.append({"label": lbl_label, "value": lbl_value, "sub": lbl_sub})

        # Matplotlib-Figure
        self._fig = Figure(figsize=(11, 6), dpi=100, facecolor=BACKGROUND)
        self._gs = self._fig.add_gridspec(2, 2, hspace=0.55, wspace=0.30,
                                           left=0.07, right=0.97,
                                           top=0.93, bottom=0.10)
        self._ax_trend   = self._fig.add_subplot(self._gs[0, 0])
        self._ax_ranking = self._fig.add_subplot(self._gs[0, 1])
        self._ax_heat    = self._fig.add_subplot(self._gs[1, 0])
        self._ax_scatter = self._fig.add_subplot(self._gs[1, 1])

        self._canvas = FigureCanvasTkAgg(self._fig, master=parent)
        self._canvas.get_tk_widget().pack(fill="both", expand=True,
                                           padx=PAD_MEDIUM, pady=(0, PAD_MEDIUM))

    # --- 6. Erkenntnisse-Reiter ---
    def _build_insights_tab(self, parent):
        """Baut den Reiter 'Erkenntnisse': scrollbarer Inhalt mit Sektionen."""
        # Scroll-Container: Canvas + vertikale Scrollbar.
        self._insights_canvas = tk.Canvas(parent, bg=BACKGROUND,
                                           highlightthickness=0)
        vsb = ttk.Scrollbar(parent, orient="vertical",
                            command=self._insights_canvas.yview)
        self._insights_canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._insights_canvas.pack(side="left", fill="both", expand=True)

        # Inneres Frame, das die Sektionen aufnimmt
        self._insights_inner = tk.Frame(self._insights_canvas, bg=BACKGROUND)
        self._insights_window = self._insights_canvas.create_window(
            (0, 0), window=self._insights_inner, anchor="nw")

        # Scroll-Region aktualisieren, sobald sich die Innen-Hoehe aendert
        def _on_inner_configure(event):
            self._insights_canvas.configure(
                scrollregion=self._insights_canvas.bbox("all"))
        self._insights_inner.bind("<Configure>", _on_inner_configure)

        # Innen-Breite an die Canvas-Breite koppeln (gegen Horizontal-Scroll)
        def _on_canvas_configure(event):
            self._insights_canvas.itemconfig(self._insights_window,
                                              width=event.width)
        self._insights_canvas.bind("<Configure>", _on_canvas_configure)

        # Mausrad-Scrolling (nur aktiv, wenn der Insights-Canvas fokussiert ist)
        def _on_mousewheel(event):
            self._insights_canvas.yview_scroll(-int(event.delta / 120), "units")

        def _bind_mousewheel(event):
            self._insights_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_mousewheel(event):
            self._insights_canvas.unbind_all("<MouseWheel>")

        self._insights_canvas.bind("<Enter>", _bind_mousewheel)
        self._insights_canvas.bind("<Leave>", _unbind_mousewheel)

    # ------------------------------------------------------------------
    # Dashboard-Refresh
    # ------------------------------------------------------------------
    def _refresh_dashboard(self):
        """Aktualisiert KPI-Karten und alle Charts aus self.quiz_nights."""
        data = compute_dashboard_data(self.quiz_nights)
        self._refresh_kpis(data["kpis"])
        self._draw_trend(data["trend"])
        self._draw_ranking(data["ranking"])
        self._draw_heatmap(data["heatmap"])
        self._draw_scatter(data["scatter"])
        self._canvas.draw_idle()

    def _refresh_insights(self):
        """Loescht das Inner-Frame und rendert die Sektionen frisch."""
        # Alte Inhalte entfernen
        for child in self._insights_inner.winfo_children():
            child.destroy()

        sections = compute_insights(self.quiz_nights)
        if not sections:
            tk.Label(self._insights_inner,
                     text="Noch keine Daten vorhanden.",
                     font=FONT_NORMAL, bg=BACKGROUND, fg=TEXT_SECONDARY
                     ).pack(padx=PAD_LARGE, pady=PAD_LARGE)
            return

        for section in sections:
            lf = ttk.LabelFrame(self._insights_inner, text=section["titel"])
            lf.pack(fill="x", padx=PAD_MEDIUM, pady=(PAD_MEDIUM, 0))

            if section.get("lead"):
                tk.Label(lf, text=section["lead"],
                         font=FONT_SMALL, bg=BACKGROUND, fg=TEXT_SECONDARY,
                         wraplength=900, justify="left", anchor="w"
                         ).pack(fill="x", padx=PAD_SMALL, pady=(PAD_SMALL, 0))

            for item in section["items"]:
                kind = item["kind"]
                text = item["text"]
                if kind == "tipp":
                    bullet = "▸"
                    color = CORPORATE_GREEN
                elif kind == "warnung":
                    bullet = "▸"
                    color = ERROR_RED
                else:
                    bullet = "•"
                    color = TEXT_PRIMARY

                row = tk.Frame(lf, bg=BACKGROUND)
                row.pack(fill="x", padx=PAD_SMALL, pady=2)
                tk.Label(row, text=bullet, font=FONT_HEADER,
                         bg=BACKGROUND, fg=color, width=2, anchor="nw"
                         ).pack(side="left", anchor="n")
                tk.Label(row, text=text, font=FONT_NORMAL,
                         bg=BACKGROUND, fg=TEXT_PRIMARY,
                         wraplength=850, justify="left", anchor="w"
                         ).pack(side="left", fill="x", expand=True)

    def _refresh_kpis(self, kpis):
        """Setzt die sechs KPI-Karten."""
        def _fmt(val, fmt="{}"):
            return fmt.format(val) if val is not None else "–"

        n = kpis["n_abende"]
        self._kpi_cards[0]["value"].configure(text=str(n))
        self._kpi_cards[0]["sub"].configure(
            text=f"seit {kpis['first_monat']}" if kpis["first_monat"] else "")

        self._kpi_cards[1]["value"].configure(
            text=f"{kpis['avg_pct']:.0%}" if n else "–")
        self._kpi_cards[1]["sub"].configure(text="von max. 60 Fragen")

        bp = kpis["best_placement"]
        self._kpi_cards[2]["value"].configure(text=f"{bp}." if bp else "–")
        sub_bp = ""
        if bp is not None:
            bp_m = kpis["best_placement_monat"]
            bp_v = kpis["best_placement_von"]
            sub_bp = f"{bp_m}" + (f" ({bp_v} Teams)" if bp_v else "")
        self._kpi_cards[2]["sub"].configure(text=sub_bp)

        ap = kpis["avg_placement"]
        self._kpi_cards[3]["value"].configure(
            text=f"{ap:.1f}" if ap is not None else "–")
        self._kpi_cards[3]["sub"].configure(
            text=f"bei Ø {kpis['avg_teams']:.1f} Teams" if kpis["avg_teams"] else "")

        bc = kpis["best_cat"]
        self._kpi_cards[4]["value"].configure(text=bc if bc else "–")
        self._kpi_cards[4]["sub"].configure(
            text=f"Ø {kpis['best_cat_avg']:.1f}/5" if kpis["best_cat_avg"] is not None else "")

        wc = kpis["worst_cat"]
        self._kpi_cards[5]["value"].configure(text=wc if wc else "–")
        self._kpi_cards[5]["sub"].configure(
            text=f"Ø {kpis['worst_cat_avg']:.1f}/5" if kpis["worst_cat_avg"] is not None else "")

    # ------------------------------------------------------------------
    # Chart-Methoden
    # ------------------------------------------------------------------
    def _draw_trend(self, trend):
        """Trend: Quote als Balken (linke Achse), Platzierung als Linie (rechte Achse, invertiert)."""
        ax = self._ax_trend
        ax.clear()
        monate = trend["monate"]
        pct = trend["pct"]
        placements = trend["placements"]
        if not monate:
            ax.set_title("Platzierung & Quote", fontsize=10)
            ax.set_axis_off()
            return
        x = range(len(monate))
        ax.bar(x, pct, color="#6baed6", alpha=0.75, label="% richtig")
        ax.set_ylim(0, 1)
        ax.set_ylabel("% richtig", fontsize=8)
        ax.set_xticks(list(x))
        ax.set_xticklabels(monate, rotation=30, ha="right", fontsize=7)
        ax.tick_params(axis="y", labelsize=7)
        ax.set_title("Platzierung & Quote pro Quizabend", fontsize=10)
        ax.grid(axis="y", alpha=0.15)
        # Sekundaere Achse fuer Platzierung
        valid_pl = [p for p in placements if p is not None]
        if valid_pl:
            ax2 = ax.twinx()
            ax2.plot(x, [p if p is not None else None for p in placements],
                     marker="o", color="#34495e", linewidth=2, markersize=6,
                     label="Platzierung")
            max_pl = max(valid_pl)
            ax2.set_ylim(max_pl + 2, 0)  # invertiert: 1 oben
            ax2.set_ylabel("Platz", fontsize=8)
            ax2.tick_params(axis="y", labelsize=7)

    def _draw_ranking(self, ranking):
        """Horizontaler Bar: Kategorie-Mittelwerte, absteigend."""
        ax = self._ax_ranking
        ax.clear()
        if not ranking:
            ax.set_title("Kategorie-Ranking", fontsize=10)
            ax.set_axis_off()
            return
        # Fuer horizontale Anzeige: kleinste Werte unten -> wir kehren um (matplotlib)
        items = list(reversed(ranking))  # schwaechste unten -> staerkste oben
        cats = [c for c, _ in items]
        vals = [v for _, v in items]
        colors = []
        for v in vals:
            if v >= 3.2: colors.append("#08519c")
            elif v >= 2.8: colors.append("#2171b5")
            elif v >= 2.5: colors.append("#6baed6")
            else: colors.append("#c6dbef")
        bars = ax.barh(cats, vals, color=colors)
        ax.set_xlim(0, 5)
        ax.set_xlabel("Ø Punkte (max. 5)", fontsize=8)
        ax.set_title("Kategorie-Ranking", fontsize=10)
        ax.tick_params(axis="both", labelsize=7)
        ax.grid(axis="x", alpha=0.15)
        for bar, v in zip(bars, vals):
            ax.text(v + 0.05, bar.get_y() + bar.get_height()/2,
                    f"{v:.1f}", va="center", fontsize=7, color="#374151")

    def _draw_heatmap(self, heat):
        """Heatmap Kategorien x Monate, RdYlBu_r."""
        ax = self._ax_heat
        ax.clear()
        monate = heat["monate"]
        kats = heat["kategorien"]
        matrix = heat["matrix"]
        if not monate or not kats:
            ax.set_title("Heatmap", fontsize=10)
            ax.set_axis_off()
            return
        import matplotlib.cm as cm
        im = ax.imshow(matrix, cmap="RdYlBu_r", aspect="auto",
                       vmin=0, vmax=5)
        ax.set_xticks(range(len(monate)))
        ax.set_xticklabels(monate, rotation=30, ha="right", fontsize=7)
        ax.set_yticks(range(len(kats)))
        ax.set_yticklabels(kats, fontsize=7)
        ax.set_title("Punkte-Heatmap (Kategorien × Monate)", fontsize=10)
        # Zellbeschriftung mit Punktzahl
        for i, row in enumerate(matrix):
            for j, val in enumerate(row):
                ax.text(j, i, str(val), ha="center", va="center",
                        fontsize=7, color="#374151")

    def _draw_scatter(self, scatter):
        """Scatter Std vs. Mittelwert mit Kategorie-Labels (Standard-Annotation)."""
        ax = self._ax_scatter
        ax.clear()
        if not scatter:
            ax.set_title("Stärke vs. Konsistenz", fontsize=10)
            ax.set_axis_off()
            return
        cats = [c for c, _, _ in scatter]
        avgs = [m for _, m, _ in scatter]
        stds = [s for _, _, s in scatter]
        ax.scatter(stds, avgs, s=80, c=avgs, cmap="Blues",
                   vmin=2, vmax=4, edgecolors="white", linewidth=1.5)
        for cat, m, s in scatter:
            ax.annotate(cat, (s, m), xytext=(5, 5),
                        textcoords="offset points",
                        fontsize=7, color="#374151")
        ax.set_xlabel("Streuung σ (links = konstanter)", fontsize=8)
        ax.set_ylabel("Ø Punkte", fontsize=8)
        ax.set_title("Stärke vs. Konsistenz", fontsize=10)
        ax.tick_params(axis="both", labelsize=7)
        ax.grid(alpha=0.15)

    # ------------------------------------------------------------------
    # Tab-Wechsel
    # ------------------------------------------------------------------
    def _on_tab_changed(self, event=None):
        """Refresh beim Wechsel auf den Dashboard- oder Erkenntnisse-Reiter."""
        if not hasattr(self, "_canvas"):
            return
        current = self.notebook.select()
        if str(current) == str(self._tab_dashboard):
            self._refresh_dashboard()
        elif str(current) == str(self._tab_insights):
            self._refresh_insights()

    # ------------------------------------------------------------------
    # Daten laden / Treeview befuellen
    # ------------------------------------------------------------------
    def _load_data(self):
        """Laedt Daten aus data.json, befuellt den Treeview."""
        try:
            data = load_data()
            self.quiz_nights = data.get("quiz_nights", [])
        except Exception:
            self.quiz_nights = []
        self._reload_tree()
        self._refresh_status()

    def _reload_tree(self):
        """Leert und befuellt den Treeview, absteigend nach Datum sortiert."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        sorted_nights = sorted(self.quiz_nights,
                               key=lambda x: x.get("Datum", ""),
                               reverse=True)
        for night in sorted_nights:
            datum = night.get("Datum", "")
            try:
                monat_lang = iso_to_monat_long(datum) if datum else night.get("Monat", "")
            except (ValueError, IndexError):
                monat_lang = night.get("Monat", "")
            joker1 = night.get("Joker1", "")
            joker2 = night.get("Joker2", "")
            sonderrunde = night.get("Sonderrunde_Thema", "")
            gesamt = night.get("Gesamt", "")
            platz = night.get("Platzierung")
            von = night.get("Von")
            platz_str = f"{platz} / {von}" if platz is not None else "–"
            self.tree.insert("", "end", iid=datum,
                             values=(monat_lang, joker1, joker2,
                                     sonderrunde, gesamt, platz_str))

    def _refresh_status(self):
        """Aktualisiert die Statuszeile (Anzahl + letzte Aenderung)."""
        n = len(self.quiz_nights)
        try:
            mtime = DATA_PATH.stat().st_mtime
            dt_str = datetime.fromtimestamp(mtime).strftime("%d.%m.%Y %H:%M")
        except Exception:
            dt_str = "–"
        self.lbl_status.configure(
            text=f"{n} Abende gespeichert · letzte Änderung: {dt_str}")

    # ------------------------------------------------------------------
    # Selection-Handling
    # ------------------------------------------------------------------
    def _on_tree_select(self, event=None):
        sel = self.tree.selection()
        state = "normal" if sel else "disabled"
        self.btn_edit.configure(state=state)
        self.btn_delete.configure(state=state)

    def _get_selected_night(self):
        """Gibt den selektierten Abend-Dict zurueck oder None."""
        sel = self.tree.selection()
        if not sel:
            return None
        datum = sel[0]
        for night in self.quiz_nights:
            if night.get("Datum") == datum:
                return night
        return None

    # ------------------------------------------------------------------
    # Live-Berechnung
    # ------------------------------------------------------------------
    def _recalc(self, *args):
        """Neuberechnung von Summen, Bonus, Gesamt und Pct nach Aenderungen."""
        teil_sums = []
        cat_scores = {}
        for t in range(4):
            s = 0
            for slot_idx in range(3):
                try:
                    p = self._punkt_vars[t][slot_idx].get()
                except tk.TclError:
                    p = 0
                kat = self._cat_cmbs[t][slot_idx].get()
                if kat:
                    cat_scores[kat] = cat_scores.get(kat, 0) + p
                s += p
            teil_sums.append(s)
            self._teil_sum_labels[t].configure(
                text=f"Summe Teil {t + 1}: {s}")

        joker1 = self.cmb_joker1.get()
        joker2 = self.cmb_joker2.get()
        bonus = compute_bonus(joker1, joker2, cat_scores)

        gesamt = sum(teil_sums) + bonus
        pct = sum(teil_sums) / 60.0 * 100 if sum(teil_sums) > 0 else 0.0

        self.lbl_bonus_value.configure(text=f"{bonus} Pkt.")
        self.lbl_gesamt.configure(text=f"Gesamt: {gesamt} Pkt.")
        self.lbl_pct.configure(text=f"% richtig: {pct:.1f} %")

    # ------------------------------------------------------------------
    # Formular aktivieren / deaktivieren
    # ------------------------------------------------------------------
    def _set_form_state(self, state):
        """Setzt alle Formular-Widgets auf 'normal' oder 'disabled'."""
        # Eckdaten-Widgets (Bonus ist Live-Anzeige, kein Eingabefeld)
        for widget in (self.cmb_monat, self.spn_jahr,
                       self.cmb_joker1, self.cmb_joker2,
                       self.ent_sonderrunde, self.spn_platz,
                       self.spn_von):
            try:
                widget.configure(state=state)
            except Exception:
                pass

        # Combobox readonly bleibt beim Aktivieren erhalten
        if state == "normal":
            for cmb in (self.cmb_monat, self.cmb_joker1, self.cmb_joker2):
                cmb.configure(state="readonly")

        # Teil-Widgets
        for t in range(4):
            for s in range(3):
                try:
                    self._cat_cmbs[t][s].configure(
                        state="readonly" if state == "normal" else "disabled")
                except Exception:
                    pass
                # Spinbox fuer Punkte
                try:
                    # Spinboxen haben kein direktes Attribut – ueber grid-Info
                    lf = self._cat_cmbs[t][s].master
                    spn_list = [w for w in lf.winfo_children()
                                if isinstance(w, ttk.Spinbox)]
                    if s < len(spn_list):
                        spn_list[s].configure(state=state)
                except Exception:
                    pass

        # Aktions-Buttons
        for btn in self._form_action_buttons:
            btn.configure(state=state)

    # ------------------------------------------------------------------
    # Formular-Defaults setzen
    # ------------------------------------------------------------------
    def _form_defaults(self):
        """Setzt alle Formular-Felder auf Startzustand (leerer neuer Abend)."""
        now = datetime.now()
        # Monat (0-basiert in GERMAN_MONTHS)
        self.cmb_monat.set(GERMAN_MONTHS[now.month - 1])
        self.spn_jahr.set(now.year)
        self.cmb_joker1.set("")
        self.cmb_joker2.set("")
        self.ent_sonderrunde.delete(0, "end")
        self.spn_platz.set("")
        self.spn_von.set("")

        for t in range(4):
            for s in range(3):
                self._cat_cmbs[t][s].set("")
                self._punkt_vars[t][s].set(0)

        self._recalc()

    # ------------------------------------------------------------------
    # Formular befuellen (Bearbeiten)
    # ------------------------------------------------------------------
    def _fill_form(self, night):
        """Befuellt das Formular mit den Daten eines bestehenden Abends."""
        datum = night.get("Datum", "")
        if datum and len(datum) >= 7:
            year = int(datum[:4])
            month = int(datum[5:7])
            self.spn_jahr.set(year)
            self.cmb_monat.set(GERMAN_MONTHS[month - 1])
        else:
            now = datetime.now()
            self.spn_jahr.set(now.year)
            self.cmb_monat.set(GERMAN_MONTHS[now.month - 1])

        self.cmb_joker1.set(night.get("Joker1", "") or "")
        self.cmb_joker2.set(night.get("Joker2", "") or "")

        self.ent_sonderrunde.delete(0, "end")
        self.ent_sonderrunde.insert(0, night.get("Sonderrunde_Thema", "") or "")

        platz = night.get("Platzierung")
        von = night.get("Von")
        self.spn_platz.set(platz if platz is not None else "")
        self.spn_von.set(von if von is not None else "")

        # Bonus wird aus den Jokern + cat_scores live berechnet -- nicht setzen.

        # Kategorien aus cat_scores in 12 Slots aufteilen
        cat_scores = night.get("cat_scores", {})
        items = list(cat_scores.items())
        # Auf 12 Slots auffuellen
        while len(items) < 12:
            items.append(("", 0))
        items = items[:12]

        for i, (kat, pts) in enumerate(items):
            t = i // 3
            s = i % 3
            self._cat_cmbs[t][s].set(kat if kat else "")
            self._punkt_vars[t][s].set(pts if pts else 0)

        self._recalc()

    # ------------------------------------------------------------------
    # Formular lesen
    # ------------------------------------------------------------------
    def _read_form(self):
        """Liest alle Formular-Werte und gibt ein form-Dict zurueck."""
        try:
            year = int(self.spn_jahr.get())
        except ValueError:
            year = datetime.now().year

        monat_str = self.cmb_monat.get()
        try:
            month = GERMAN_MONTHS.index(monat_str) + 1
        except ValueError:
            month = 1

        joker1 = self.cmb_joker1.get()
        joker2 = self.cmb_joker2.get()
        sonderrunde_thema = self.ent_sonderrunde.get().strip()

        platz_raw = self.spn_platz.get().strip()
        von_raw = self.spn_von.get().strip()
        try:
            platz = int(platz_raw) if platz_raw else None
        except ValueError:
            platz = None
        try:
            von = int(von_raw) if von_raw else None
        except ValueError:
            von = None

        teile = []
        for t in range(4):
            teil = []
            for s in range(3):
                kat = self._cat_cmbs[t][s].get()
                try:
                    pts = self._punkt_vars[t][s].get()
                except tk.TclError:
                    pts = 0
                teil.append({"kategorie": kat, "punkte": pts})
            teile.append(teil)

        return {
            "year": year,
            "month": month,
            "joker1": joker1,
            "joker2": joker2,
            "sonderrunde_thema": sonderrunde_thema,
            "platz": platz,
            "von": von,
            "teile": teile,
        }

    # ------------------------------------------------------------------
    # Aktionen
    # ------------------------------------------------------------------
    def _on_new(self):
        """Neuer Abend: Formular aktivieren mit Defaults."""
        self._mode = "new"
        self._set_form_state("normal")
        self._form_defaults()
        self.lbl_mode.configure(text="Modus: Neuer Abend")

    def _on_edit(self):
        """Bearbeiten: selektierten Abend ins Formular laden."""
        night = self._get_selected_night()
        if night is None:
            return
        datum = night.get("Datum", "")
        monat = night.get("Monat", datum)
        self._mode = ("edit", datum)
        self._set_form_state("normal")
        self._fill_form(night)
        self.lbl_mode.configure(
            text=f"Modus: Bearbeite {monat} "
                 f"(Hinweis: Slot-Reihenfolge wird neu aufgebaut)")

    def _on_save(self):
        """Speichern: validieren, erzeugen, sichern, Treeview aktualisieren."""
        form = self._read_form()

        if isinstance(self._mode, tuple) and self._mode[0] == "edit":
            edit_datum = self._mode[1]
        else:
            edit_datum = None

        errors = validate_form(form,
                               existing_quiz_nights=self.quiz_nights,
                               edit_datum=edit_datum)
        if errors:
            messagebox.showerror(
                "Eingabe unvollständig",
                "\n".join(f"- {e}" for e in errors))
            return

        entry = quiznight_from_form(form)

        if self._mode == "new":
            self.quiz_nights.append(entry)
        elif isinstance(self._mode, tuple) and self._mode[0] == "edit":
            self.quiz_nights = [
                entry if n.get("Datum") == edit_datum else n
                for n in self.quiz_nights
            ]

        save_data(self.quiz_nights)
        messagebox.showinfo("Gespeichert",
                            f"Abend {entry['Monat']} gespeichert.")

        self._reload_tree()
        self._refresh_status()
        self._refresh_dashboard()
        self._refresh_insights()
        self._mode = "inactive"
        self._form_defaults()
        self._set_form_state("disabled")
        self.lbl_mode.configure(text="Modus: inaktiv")

    def _on_delete(self):
        """Loeschen: Bestaetigung einholen, dann entfernen."""
        night = self._get_selected_night()
        if night is None:
            return
        monat = night.get("Monat", night.get("Datum", "?"))
        if not messagebox.askyesno("Löschen?",
                                   f"Eintrag für {monat} löschen?"):
            return
        datum = night.get("Datum")
        self.quiz_nights = [n for n in self.quiz_nights
                            if n.get("Datum") != datum]
        save_data(self.quiz_nights)
        self._reload_tree()
        self._refresh_status()
        self._refresh_dashboard()
        self._refresh_insights()
        self.btn_edit.configure(state="disabled")
        self.btn_delete.configure(state="disabled")

    def _on_reset(self):
        """Zuruecksetzen: Formular leeren, Modus bleibt."""
        self._form_defaults()
        if self._mode == "new":
            self.lbl_mode.configure(text="Modus: Neuer Abend")

    def _on_cancel(self):
        """Abbrechen: Formular disablen, Modus inaktiv."""
        self._mode = "inactive"
        self._form_defaults()
        self._set_form_state("disabled")
        self.lbl_mode.configure(text="Modus: inaktiv")


# ---------------------------------------------------------------------------
# Einstiegspunkt
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = QuizEingabeApp()
    app.mainloop()
