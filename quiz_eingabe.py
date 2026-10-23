"""
quiz_eingabe.py  –  Tkinter-Desktop-GUI fuer die Eingabe von Kneipenquiz-Abenden.

Kommentare/Docstrings: ae/oe/ue (ASCII).
Nutzer-sichtbarer Text: mit Umlauten.
"""

import pathlib
import shutil
import sys
import time
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont
from datetime import datetime

from quiz_data import (
    CATEGORIES,
    JOKER_KEINER,
    GERMAN_MONTHS,
    GERMAN_MONTHS_LONG,
    DATA_PATH,
    load_data,
    save_data,
    quiznight_from_form,
    validate_form,
    iso_to_monat_long,
    compute_bonus,
    normalize_joker,
    compute_dashboard_data,
    compute_insights,
)

# Auswahl der Joker-Comboboxen: '(keiner)' vorweg, dann der Kategorien-Kanon.
JOKER_CHOICES = [JOKER_KEINER] + list(CATEGORIES)


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


# Steuertasten, die beim Tippen im Autocomplete-Feld nichts filtern sollen.
_AUTOCOMPLETE_STEUERTASTEN = {
    "Left", "Right", "Up", "Down", "Return", "Escape", "Tab",
    "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R",
    "Home", "End", "Prior", "Next",
}


def _bind_combo_autocomplete(combo):
    """Editierbare Combobox: Tippen filtert die Liste und vervollstaendigt.

    Die Kandidaten stehen in combo._full_choices (dynamisch gepflegt, z. B.
    ohne bereits belegte Kategorien). Beim Tippen wird die Dropdown-Liste
    (values) auf die Treffer reduziert -- Praefix-Treffer zuerst, dann Teil-
    string -- und auf den ersten Praefix-Treffer vervollstaendigt; der
    ergaenzte Teil bleibt markiert, sodass Weitertippen ihn ersetzt.
    BackSpace/Delete filtert nur, ohne erneut zu vervollstaendigen.

    Als "getippt" gilt der Text VOR der Markierung, nicht der ganze Feldinhalt.
    Sonst haelt ein zweiter Handler-Lauf die eigene Ergaenzung faelschlich fuer
    Eingabe, hebt die Markierung auf -- und Weitertippen haengt hinten an
    ("Verschiedenessch"). Das passiert real beim schnellen Tippen: wer die
    naechste Taste drueckt, ehe er die vorige losgelassen hat, erzeugt
    KeyRelease-Ereignisse, die dem bereits ergaenzten Text nachlaufen.
    Faellt die Markierung dennoch weg, wird der Ueberschuss hinter der
    Ergaenzung an den eigenen Praefix zurueckgesetzt (Selbstheilung).
    """
    combo._full_choices = list(combo.cget("values"))
    combo._auto_typed = ""     # zuletzt vom Nutzer getippter Praefix
    combo._auto_match = ""     # die daraus eingesetzte Vollform
    combo._auto_stamp = 0.0

    def merken(typed, match):
        combo._auto_typed = typed
        combo._auto_match = match
        combo._auto_stamp = time.monotonic()

    def getippter_teil():
        """Liefert (Nutzer-Eingabe, ob der Feldinhalt zu reparieren ist)."""
        text = combo.get()
        try:
            if combo.selection_present():
                return text[:int(combo.index("sel.first"))], False
        except tk.TclError:
            pass
        # Ohne Markierung: haengt hinter der letzten Ergaenzung Weiteres, hat
        # der Nutzer im Tippfluss darueber hinweggeschrieben -- Ueberschuss an
        # den eigenen Praefix zuruecksetzen. Nur unmittelbar nach der
        # Ergaenzung, damit spaeteres Weiterschreiben unangetastet bleibt.
        match = combo._auto_match
        if (match and text.startswith(match) and len(text) > len(match)
                and time.monotonic() - combo._auto_stamp < 5.0):
            return combo._auto_typed + text[len(match):], True
        return text, False

    def on_keyrelease(event):
        ks = event.keysym
        if ks in _AUTOCOMPLETE_STEUERTASTEN:
            return
        typed, repariert = getippter_teil()
        if repariert:
            combo.delete(0, "end")
            combo.insert(0, typed)
        full = getattr(combo, "_full_choices", None) or []
        if not typed:
            merken("", "")
            combo.configure(values=full)
            return
        low = typed.lower()
        starts = [c for c in full if c.lower().startswith(low)]
        contains = [c for c in full if low in c.lower() and c not in starts]
        combo.configure(values=(starts + contains) or full)
        if ks in ("BackSpace", "Delete"):
            merken(typed, "")
            return  # nur filtern, nicht ergaenzen
        if starts:
            match = starts[0]
            combo.delete(0, "end")
            combo.insert(0, match)
            combo.select_range(len(typed), "end")
            combo.icursor(len(typed))
            merken(typed, match)
        else:
            merken(typed, "")

    combo.bind("<KeyRelease>", on_keyrelease)
    combo._autocomplete_handler = on_keyrelease  # Testhaken, sonst ungenutzt


# Icon-Pfad: Kandidaten-Kaskade analog Loriot/encoder.py (resolve_ffmpeg).
#   1) PyInstaller _MEIPASS (falls gesetzt, EXE-Kompat)
#   2) Nuitka-Onefile: gebuendelte Ressource liegt neben dem Modul (__file__)
#   3) Neben der gefrorenen EXE (Fallback)
#   4) Entwicklung: neben dem Modul
def _resolve_icon_path():
    candidates = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(pathlib.Path(meipass) / "icon.ico")
    if getattr(sys, "frozen", False) or "__compiled__" in globals():
        candidates.append(pathlib.Path(__file__).parent / "icon.ico")
        candidates.append(pathlib.Path(sys.executable).parent / "icon.ico")
    else:
        candidates.append(pathlib.Path(__file__).parent / "icon.ico")
    for c in candidates:
        if c.exists():
            return c
    return candidates[-1]


ICON_PATH = _resolve_icon_path()


# Logo-Pfad: gleiche Kandidaten-Kaskade wie beim Icon, nur fuer die
# Header-Bildmarke (logo.png). Wird via tk.PhotoImage geladen -- kein PIL
# zur Laufzeit noetig (Tk 8.6 liest PNG nativ).
def _resolve_logo_path():
    candidates = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(pathlib.Path(meipass) / "logo.png")
    if getattr(sys, "frozen", False) or "__compiled__" in globals():
        candidates.append(pathlib.Path(__file__).parent / "logo.png")
        candidates.append(pathlib.Path(sys.executable).parent / "logo.png")
    else:
        candidates.append(pathlib.Path(__file__).parent / "logo.png")
    for c in candidates:
        if c.exists():
            return c
    return candidates[-1]


LOGO_PATH = _resolve_logo_path()

# ---------------------------------------------------------------------------
# Design-Konstanten
# ---------------------------------------------------------------------------
CORPORATE_GREEN = "#66b32f"
CORPORATE_GREEN_HOVER = "#3a6d1b"
BACKGROUND = "#e5e7eb"
CARD_BG = "#ffffff"
TEXT_PRIMARY = "#333333"
TEXT_SECONDARY = "#666666"
ERROR_RED = "#ef4444"

# Schriftgroessen: Das Fenster startet maximiert (auf dem Arbeitsplatz
# 1920x1129), und das Eingabeformular fuellt nur eine Haelfte davon. Die
# fruehere Staffelung 8/9/10/14 pt stammte aus dem Zweispalten-Layout, in dem
# jedes Pixel knapp war -- im heutigen Aufbau laesst sie Platz ungenutzt.
FONT_FAMILY = "Roboto"  # Fallback Segoe UI
FONT_SMALL = (FONT_FAMILY, 9)
FONT_NORMAL = (FONT_FAMILY, 11)
FONT_HEADER = (FONT_FAMILY, 12, "bold")
FONT_TITLE = (FONT_FAMILY, 16, "bold")
FONT_GROSS = (FONT_FAMILY, 14, "bold")   # Gesamt-Punktestand
FONT_SUM = (FONT_FAMILY, 11, "bold")     # Summenzeile je Teil (Rechnungsstrich)

PAD_LARGE = 15
PAD_MEDIUM = 10
PAD_SMALL = 5

# Einzug der linksbuendigen Tabellenzellen. ttk kennt fuer die Datenzellen
# eines Treeview kein Innenpolster -- ein Stil-Padding greift nur am
# Spaltenkopf. Ein vorangestelltes Leerzeichen loest das ohne Klimmzug; die
# Spaltenbreiten messen es mit.
ZELL_EINZUG = " "

# Anordnung der vier Teil-Bloecke im Eingabeformular: 1 = untereinander,
# 2 = zu zweit nebeneinander. Siehe _build_teile().
TEILE_SPALTEN = 1

VERSION = "0.10.0"

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
# Spaltenbreiten-Messung (Treeview "Bisherige Abende")
# ---------------------------------------------------------------------------
def _spaltenbreite(kopf, zellinhalte, polster=18):
    """Minwidth einer Treeview-Spalte: Kopf (FONT_HEADER) und die laengsten
    vorkommenden Zellinhalte (FONT_NORMAL) werden gemessen, das Maximum
    zaehlt, dazu ein Polster fuer Zellrand und Luft.

    Polster 18 statt 24: Der Einzug der linksbuendigen Zellen steckt seit
    ZELL_EINZUG in den Proben selbst und muss nicht mehr pauschal
    draufgeschlagen werden -- sonst summierten sich beide und die Tabelle
    rollte waagrecht, obwohl sie passt.
    """
    f_kopf = tkfont.Font(font=FONT_HEADER)
    f_zelle = tkfont.Font(font=FONT_NORMAL)
    breite = f_kopf.measure(kopf)
    for text in zellinhalte:
        breite = max(breite, f_zelle.measure(str(text)))
    return breite + polster


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
        # Wiederherstellungs-Groesse (falls der Nutzer entmaximiert)
        self.geometry("1200x800")
        self._center_window(1200, 800)
        self.configure(bg=BACKGROUND)
        self.resizable(True, True)

        # Fragezeichen-Icon (still bei Fehler, falls Datei fehlt)
        try:
            if ICON_PATH.exists():
                self.iconbitmap(str(ICON_PATH))
        except Exception:
            pass

        # Anwendungsstatus. Das Eingabeformular existiert nur, solange das
        # Eingabefenster offen ist (siehe _open_eingabe_fenster) -- seine
        # Widget-Listen starten darum leer statt aufgebaut-aber-deaktiviert.
        self.quiz_nights = []
        self._mode = "new"        # "new" | ("edit", datum)
        self._logo_img = None     # GC-Schutz fuer das Header-Logo
        self._edit_stand = None   # Formular-Abzug beim Laden in _on_edit,
                                   # fuer den Verwerfen-Schutz (_darf_formular_verwerfen)
        self._eingabe_fenster = None   # Toplevel, solange das Formular offen ist
        self._punkt_vars = []
        self._cat_cmbs = []
        self._teil_sum_labels = []
        self.lbl_mode_hinweis = None

        self._setup_styles()
        self._build_ui()
        self._load_data()
        self._refresh_dashboard()
        self._refresh_insights()

        # Immer maximiert starten (Windows: "zoomed")
        try:
            self.state("zoomed")
        except tk.TclError:
            self.attributes("-zoomed", True)

    # ------------------------------------------------------------------
    # Font-Hilfsmethoden
    # ------------------------------------------------------------------
    def _patch_fonts(self, family):
        """Aktualisiert alle globalen Font-Tupel mit dem registrierten Fontnamen."""
        global FONT_SMALL, FONT_NORMAL, FONT_HEADER, FONT_TITLE, FONT_GROSS, FONT_SUM
        global FONT_FAMILY
        FONT_FAMILY = family
        FONT_SMALL = (family, 9)
        FONT_NORMAL = (family, 11)
        FONT_HEADER = (family, 12, "bold")
        FONT_TITLE = (family, 16, "bold")
        FONT_GROSS = (family, 14, "bold")
        FONT_SUM = (family, 11, "bold")

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

        # Innenabstaende an einer Stelle. Ohne sie stiess jeder Eintrag hart an
        # den Rand seines Kastens -- Text klebte links an der Linie, Zahlen
        # rechts an ihr. EINZUG_X wirkt waagrecht, der zweite Wert bleibt
        # bewusst klein: Jedes vertikale Pixel vervielfacht sich ueber zwanzig
        # Formularzeilen und holte die Rollleiste zurueck.
        EINZUG_X = 7
        feld_polster = (EINZUG_X, 1)

        style.configure("TFrame", background=BACKGROUND)
        style.configure("TLabelframe", background=BACKGROUND,
                        foreground=TEXT_PRIMARY, font=FONT_HEADER)
        style.configure("TLabelframe.Label", background=BACKGROUND,
                        foreground=TEXT_PRIMARY, font=FONT_HEADER,
                        padding=(EINZUG_X, 0))
        style.configure("TLabel", background=BACKGROUND,
                        foreground=TEXT_PRIMARY, font=FONT_NORMAL,
                        padding=(EINZUG_X, 0))
        style.configure("TButton", padding=(10, 5), font=FONT_NORMAL)

        # Eingabefelder: Text bekommt Luft zum Rahmen.
        style.configure("TEntry", padding=feld_polster)
        style.configure("TSpinbox", padding=feld_polster)

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

        # rowheight 30 statt 22: Die Zeile muss die groessere Schrift fassen.
        style.configure("Treeview", font=FONT_NORMAL, rowheight=30,
                        background=CARD_BG, fieldbackground=CARD_BG)
        style.configure("Treeview.Heading", font=FONT_HEADER,
                        background=BACKGROUND, foreground=TEXT_PRIMARY,
                        padding=(EINZUG_X, 3))
        # Zellen der Tabelle: ttk kennt keinen Innenabstand je Zelle, wohl aber
        # einen am Item-Element des Layouts. Greift er in dieser Tk-Fassung
        # nicht, faengt der Einzug ueber die Spaltenbreite ihn auf.
        try:
            style.configure("Treeview.Item", padding=(EINZUG_X, 0))
        except tk.TclError:
            pass
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
                        darkcolor=CARD_BG,
                        padding=feld_polster)
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
        self._tab_uebersicht = ttk.Frame(self.notebook)
        self._tab_dashboard = ttk.Frame(self.notebook)
        self._tab_insights = ttk.Frame(self.notebook)
        self.notebook.add(self._tab_uebersicht, text="Übersicht")
        self.notebook.add(self._tab_dashboard, text="Dashboard")
        self.notebook.add(self._tab_insights, text="Erkenntnisse")
        self._build_uebersicht_tab(self._tab_uebersicht)
        self._dashboard_built = False
        self._build_insights_tab(self._tab_insights)
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    # --- 1. Header ---
    def _build_header(self):
        hdr = tk.Frame(self, bg=BACKGROUND)
        hdr.pack(fill="x", padx=PAD_LARGE, pady=(PAD_LARGE, 0))

        # Fragezeichen-Logo links, ueber beide Textzeilen (Schwesterprojekt-Stil)
        self._logo_img = self._load_logo(44)
        if self._logo_img is not None:
            logo_lbl = tk.Label(hdr, image=self._logo_img, bg=BACKGROUND)
            logo_lbl.image = self._logo_img  # GC-Schutz
            logo_lbl.grid(row=0, column=0, rowspan=2, sticky="w",
                          padx=(0, PAD_MEDIUM))

        tk.Label(hdr, text="Kneipenquiz Schwabach",
                 font=FONT_TITLE, bg=BACKGROUND, fg=TEXT_PRIMARY
                 ).grid(row=0, column=1, sticky="sw")
        tk.Label(hdr, text=f"Version {VERSION}",
                 font=FONT_SMALL, bg=BACKGROUND, fg=TEXT_SECONDARY
                 ).grid(row=1, column=1, sticky="nw")

        sep = tk.Frame(self, height=3, bg=CORPORATE_GREEN)
        sep.pack(fill="x", padx=0, pady=(PAD_SMALL, 0))

    def _load_logo(self, zielhoehe):
        """Laedt logo.png und skaliert es per subsample auf ~zielhoehe px.

        Nutzt tk.PhotoImage (Tk liest PNG nativ) -- kein PIL zur Laufzeit.
        Gibt None zurueck, wenn die Datei fehlt oder nicht ladbar ist.
        """
        try:
            if not LOGO_PATH.exists():
                return None
            raw = tk.PhotoImage(file=str(LOGO_PATH))
            factor = max(1, round(raw.height() / zielhoehe))
            return raw.subsample(factor, factor)
        except Exception:
            return None

    # --- 2. Uebersicht-Reiter: Aktionen, Kacheln, Tabelle -- volle Breite ---
    def _build_uebersicht_tab(self, parent):
        """Baut den Reiter 'Uebersicht' von oben nach unten: Aktionsknoepfe,
        die sechs KPI-Kacheln (umgezogen aus dem Dashboard), die Tabelle
        'Bisherige Abende' ueber die volle restliche Hoehe.

        Ein Abend wird einmal im Monat eingetragen und dauert wenige
        Minuten, waehrend die Uebersicht oft angeschaut wird -- das
        Eingabeformular steht darum nicht mehr dauerhaft im Reiter, sondern
        oeffnet sich nur auf Knopfdruck als eigenes Fenster
        (_open_eingabe_fenster).
        """
        self._build_uebersicht_toolbar(parent)
        self._build_kpi_row(parent)
        self._build_table_block(parent)

    def _build_uebersicht_toolbar(self, parent):
        """Aktionsknoepfe ganz oben links: Neuer Abend, Bearbeiten, Loeschen."""
        bar = tk.Frame(parent, bg=BACKGROUND)
        bar.pack(side="top", fill="x", padx=PAD_LARGE, pady=(PAD_MEDIUM, 0))

        self.btn_new = ttk.Button(bar, text="+ Neuer Abend",
                                  style="Accent.TButton",
                                  command=lambda: self._open_eingabe_fenster("new"))
        self.btn_new.pack(side="left", padx=(0, PAD_SMALL))

        self.btn_edit = ttk.Button(bar, text="Bearbeiten",
                                   state="disabled",
                                   command=self._on_edit)
        self.btn_edit.pack(side="left", padx=(0, PAD_SMALL))

        self.btn_delete = ttk.Button(bar, text="Löschen",
                                     style="Danger.TButton",
                                     state="disabled",
                                     command=self._on_delete)
        self.btn_delete.pack(side="left")

    def _build_kpi_row(self, parent):
        """Die sechs KPI-Kacheln -- umgezogen aus dem Dashboard-Reiter in die
        Uebersicht, wo sie zusammen mit der Tabelle sofort sichtbar sind.
        Flacher Innenabstand, groessere Schrift fuer Beschriftung/Unterzeile:
        7 pt liess die Karten trotz ihrer Hoehe fast leer wirken."""
        self._kpi_frame = tk.Frame(parent, bg=BACKGROUND)
        self._kpi_frame.pack(side="top", fill="x", padx=PAD_LARGE,
                             pady=(PAD_SMALL, PAD_SMALL))

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
                                 font=FONT_SMALL, bg=CARD_BG, fg=TEXT_SECONDARY)
            lbl_label.pack(anchor="w", padx=8, pady=(4, 0))
            lbl_value = tk.Label(card, text="–", font=FONT_GROSS,
                                 bg=CARD_BG, fg=TEXT_PRIMARY)
            lbl_value.pack(anchor="w", padx=8, pady=0)
            lbl_sub = tk.Label(card, text="", font=FONT_SMALL,
                               bg=CARD_BG, fg=TEXT_SECONDARY, wraplength=160,
                               justify="left")
            lbl_sub.pack(anchor="w", padx=8, pady=(0, 4), fill="x")
            self._kpi_frame.columnconfigure(i, weight=1)
            self._kpi_cards.append({"label": lbl_label, "value": lbl_value, "sub": lbl_sub})

    # --- 3. Tabellen-Block (Uebersicht, volle Breite/Hoehe) ---
    def _build_table_block(self, parent):
        outer = ttk.LabelFrame(parent, text="Bisherige Abende")
        outer.pack(fill="both", expand=True, padx=PAD_LARGE,
                   pady=(PAD_SMALL, PAD_LARGE))

        tree_frame = tk.Frame(outer, bg=BACKGROUND)

        cols = ("monat", "joker1", "joker2", "sonderrunde",
                "teil1", "teil2", "teil3", "teil4",
                "punkte", "bonus", "gesamt", "pct", "platz")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                 show="headings", height=8)

        # stretch=False auf allen Spalten (Hausvorgabe): so breit wie noetig,
        # so schmal wie moeglich. minwidth kommt aus der gemessenen Breite
        # des laengsten vorkommenden Zellinhalts -- ohne das schnitt
        # Joker 1/Joker 2 Kategorienamen wie "Geschicht", "Geograph",
        # "Kunst/Lite" ab, ohne Auslassungspunkte und ohne Rollleiste, der
        # Verlust blieb also unbemerkt.
        # Die Proben tragen den Zell-Einzug mit, damit die gemessene Breite zu
        # dem passt, was _reload_tree tatsaechlich einsetzt.
        MONAT_PROBE = ZELL_EINZUG + max(GERMAN_MONTHS_LONG, key=len) + " 2026"
        KATEGORIE_PROBE = ZELL_EINZUG + max(CATEGORIES, key=len)
        PLATZ_PROBE = "50 / 50"
        # Die Tabelle traegt seit dem Umbau der Uebersicht auch die vier
        # Teilsummen (kurz "T1".."T4", sonst passen die Spalten nicht
        # nebeneinander), die Joker-Punkte ("Joker-Pkt.", Feldname Bonus)
        # und die Quote ("Quote", Pct_richtig als Prozent mit Dezimalkomma).
        # "Punkte" bleibt die Summe der vier Teile ohne Joker-Bonus,
        # "Gesamt m. Joker" die Summe inkl. Bonus -- wie bisher steht an
        # keiner Stelle offen, welche der beiden Groessen gemeint ist.
        headings = {
            "monat": ("Monat", [MONAT_PROBE], "w"),
            "joker1": ("Joker 1", [KATEGORIE_PROBE], "w"),
            "joker2": ("Joker 2", [KATEGORIE_PROBE], "w"),
            "sonderrunde": ("Sonderrunde", [], "w"),
            "teil1": ("T1", ["15"], "center"),
            "teil2": ("T2", ["15"], "center"),
            "teil3": ("T3", ["15"], "center"),
            "teil4": ("T4", ["15"], "center"),
            "punkte": ("Punkte", ["99"], "center"),
            "bonus": ("Joker-Pkt.", ["10"], "center"),
            "gesamt": ("Gesamt m. Joker", ["99"], "center"),
            "pct": ("Quote", ["100,0 %"], "center"),
            "platz": ("Platz / Von", [PLATZ_PROBE], "center"),
        }
        # Reiner Kopftext je Spalte (ohne Sortierpfeil) -- _update_tree_headings
        # haengt das Pfeilchen der aktiven Sortierspalte hier an.
        self._tree_heading_base = {col: h[0] for col, h in headings.items()}
        for col, (heading, proben, anchor) in headings.items():
            breite = _spaltenbreite(heading, proben)
            self.tree.heading(col, text=heading, anchor=anchor,
                              command=lambda c=col: self._on_tree_heading_click(c))
            self.tree.column(col, width=breite, minwidth=breite,
                             anchor=anchor, stretch=False)

        # Ausgangszustand: Datum absteigend (neuester Abend oben) -- wie
        # bisher, nur jetzt als benanntes Sortierkriterium statt eines
        # fest verdrahteten sorted() in _reload_tree.
        self._sort_column = "monat"
        self._sort_reverse = True

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                            command=self.tree.yview)
        self._tree_hsb = ttk.Scrollbar(tree_frame, orient="horizontal",
                                       command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set,
                            xscrollcommand=self._tree_hsb.set)

        vsb.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        # Die waagrechte Leiste erscheint nur, wenn die Spalten wirklich
        # breiter sind als die Tabelle. Fest gepackt stand sie auch im
        # maximierten Fenster da, wo 796 px Spalten auf 799 px Breite treffen
        # -- eine Leiste, die nichts zu rollen hat, ist nur ein Streifen.
        self.tree.bind("<Configure>", self._on_tree_resize)

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<Double-1>", lambda e: self._on_edit())
        self._tree_frame = tree_frame

        # Keine Knoepfe mehr unterhalb der Tabelle: "Bearbeiten"/"Löschen"
        # stehen jetzt in der Aktionsleiste ganz oben im Reiter, zusammen mit
        # "+ Neuer Abend" (_build_uebersicht_toolbar).
        tree_frame.pack(fill="both", expand=True, padx=PAD_SMALL, pady=PAD_SMALL)

    def _tune_sonderrunde_spalte(self):
        """Erweitert die Sonderrunde-Spalte auf die Breite des laengsten
        tatsaechlich vorkommenden Themas.

        Beim Einrichten der Tabelle liegen die Daten noch nicht vor, darum
        startet die Spalte mit der reinen Kopfbreite; hier wird sie nach dem
        Laden nachgezogen. Sie schrumpft dabei nie wieder zurueck -- faellt
        ein noch laengeres Thema ein, faengt die waagrechte Rollleiste den
        Rest auf.
        """
        themen = [n.get("Sonderrunde_Thema", "") for n in self.quiz_nights]
        if not themen:
            return
        breite = _spaltenbreite("Sonderrunde",
                                [ZELL_EINZUG + t for t in themen])
        aktuell = self.tree.column("sonderrunde", "minwidth")
        if breite > aktuell:
            self.tree.column("sonderrunde", width=breite, minwidth=breite)

    # --- 4. Eingabefenster (Toplevel, nur auf Knopfdruck offen) ---
    def _open_eingabe_fenster(self, mode):
        """Oeffnet das Eingabeformular als eigenes Fenster -- neu oder zum
        Bearbeiten eines bestehenden Abends.

        Die Formular-Widgets (self.cmb_monat, self._cat_cmbs, ...) entstehen
        hier frisch und verschwinden mit dem Fenster wieder; siehe
        _destroy_eingabe_fenster fuer das Gegenstueck. Waehrend das Fenster
        offen ist, haelt grab_set() das Hauptfenster ruhig -- ein zweiter
        Aufruf (etwa durch einen hereinkommenden Doppelklick) hebt darum nur
        das bestehende Fenster an.
        """
        if self._eingabe_fenster is not None:
            self._eingabe_fenster.lift()
            self._eingabe_fenster.focus_set()
            return

        self._mode = mode

        fenster = tk.Toplevel(self)
        self._eingabe_fenster = fenster
        fenster.configure(bg=BACKGROUND)
        fenster.transient(self)

        if mode == "new":
            fenster.title("Neuer Abend")
        else:
            _, datum = mode
            fenster.title(f"Abend bearbeiten — {iso_to_monat_long(datum)}")

        try:
            if ICON_PATH.exists():
                fenster.iconbitmap(str(ICON_PATH))
        except Exception:
            pass

        self._build_eingabe_inhalt(fenster)

        if mode == "new":
            self._edit_stand = None
            self._form_defaults()
        else:
            _, datum = mode
            night = self._night_by_datum(datum)
            self._fill_form(night)
            self._edit_stand = self._read_form()

        fenster.protocol("WM_DELETE_WINDOW", self._on_eingabe_fenster_close)
        # update() statt nur update_idletasks(): Eine frische Toplevel mit
        # tiefer ttk-Hierarchie liefert winfo_reqheight() erst zuverlaessig,
        # nachdem sie tatsaechlich einmal gemappt wurde -- sonst las die
        # Messung hier einen zu kleinen Zwischenstand, und Tk zog das Fenster
        # beim ersten echten Event-Zyklus auf seine eigene, groessere
        # natuerliche Groesse hoch (sichtbar als Luecke vor dem
        # Ergebnis-Block im Bearbeiten-Modus).
        fenster.update()
        self._size_and_center_eingabe_fenster(fenster)
        fenster.update_idletasks()
        # Erst jetzt binden (siehe Kommentar in _build_eingabe_inhalt):
        # spaetere ECHTE Groessenaenderungen (Nutzer zieht das Fenster
        # breiter/schmaler) sollen den Umbruch weiterhin nachziehen.
        fenster.bind("<Configure>", self._on_eingabe_fenster_resize)

        fenster.grab_set()
        fenster.focus_set()

    def _build_eingabe_inhalt(self, fenster):
        """Baut den Inhalt des Eingabefensters.

        Reihenfolge ist bindend wie zuvor im Reiter: Knopfleiste zuerst
        (side='bottom'), danach der Ergebnis-Block (ebenfalls 'bottom',
        stapelt sich direkt darueber), danach die Hinweiszeile ('top', nur
        im Bearbeiten-Modus), zuletzt der Canvas-Rollbereich (fuellt den
        Rest) mit Eckdaten und den vier Teilen.
        """
        self._eingabe_btn_frame = self._build_eingabe_buttons(fenster)
        self._eingabe_ergebnis_frame = self._build_ergebnis(fenster)

        # Die Modus-Ueberschrift ("Eingabe — Neuer Abend" / "— Bearbeite …")
        # entfaellt im eigenen Fenster: Der Fenstertitel traegt diese Auskunft
        # bereits. Die Hinweiszeile zur Neuverteilung der Kategorien beim
        # Bearbeiten bleibt inhaltlich richtig und steht darum weiterhin im
        # Fenster, nur ohne die Ueberschrift darueber.
        self.lbl_mode_hinweis = ttk.Label(
            fenster, font=FONT_SMALL, foreground=TEXT_SECONDARY, text="",
            wraplength=560, justify="left")
        if isinstance(self._mode, tuple) and self._mode[0] == "edit":
            self.lbl_mode_hinweis.configure(
                text="Die Kategorien werden beim Speichern neu auf die vier "
                     "Teile verteilt; die Teil-Summen können sich dadurch "
                     "verschieben.")
            self.lbl_mode_hinweis.pack(side="top", fill="x",
                                       padx=PAD_MEDIUM, pady=(PAD_SMALL, 0))
        # Die <Configure>-Bindung kommt erst NACH der ersten Groessensetzung
        # (siehe _open_eingabe_fenster): Waehrend die frische Toplevel noch
        # entsteht, feuert Windows mehrere Zwischen-Configure-Ereignisse mit
        # vorlaeufig schmaler Breite -- ungebunden ueberschrieb genau das
        # die in _size_and_center_eingabe_fenster korrekt berechnete
        # Umbruchbreite wieder auf ihren 200px-Mindestwert.

        bereich = tk.Frame(fenster, bg=BACKGROUND)
        bereich.pack(fill="both", expand=True)

        self._form_canvas = tk.Canvas(bereich, bg=BACKGROUND,
                                      highlightthickness=0, bd=0)
        self._form_vsb = ttk.Scrollbar(bereich, orient="vertical",
                                       command=self._form_canvas.yview)
        self._form_canvas.configure(yscrollcommand=self._form_vsb.set)
        self._form_canvas.pack(side="left", fill="both", expand=True)

        self.form_frame = ttk.Frame(self._form_canvas)
        self._form_window = self._form_canvas.create_window(
            (0, 0), window=self.form_frame, anchor="nw")

        self._form_canvas.bind("<Configure>", self._on_form_canvas_resize)
        self.form_frame.bind(
            "<Configure>",
            lambda e: self._form_canvas.configure(
                scrollregion=self._form_canvas.bbox("all")))
        # Mausrad nur, solange der Zeiger ueber dem Formular steht.
        self._form_canvas.bind("<Enter>", lambda e: self._form_canvas.bind_all(
            "<MouseWheel>", self._on_form_wheel))
        self._form_canvas.bind("<Leave>", lambda e: self._form_canvas.unbind_all(
            "<MouseWheel>"))

        self._build_eckdaten(row=0)
        self._build_teile(row=1)

        self.form_frame.columnconfigure(0, weight=1)
        self.form_frame.rowconfigure(1, weight=1)

    def _build_eingabe_buttons(self, parent):
        """Knopfleiste des Eingabefensters: Speichern/Abbrechen, fest am
        unteren Rand. Ersetzt das fruehere Paar 'Speichern'/'Formular
        leeren' -- ein Leeren-Knopf ergibt keinen Sinn mehr, wenn das
        Fenster beim naechsten 'Neuer Abend' ohnehin frisch entsteht.
        Gibt den Knopf-Rahmen zurueck, zur Hoehenmessung in
        _size_and_center_eingabe_fenster."""
        btn_frame = tk.Frame(parent, bg=BACKGROUND)
        btn_frame.pack(side="bottom", fill="x", padx=PAD_MEDIUM,
                       pady=(PAD_SMALL, PAD_SMALL))

        self.btn_save = ttk.Button(btn_frame, text="💾 Speichern",
                                   style="Accent.TButton",
                                   command=self._on_save)
        self.btn_save.pack(side="left", padx=(0, PAD_SMALL))

        self.btn_cancel = ttk.Button(btn_frame, text="✕ Abbrechen",
                                     command=self._on_eingabe_fenster_close)
        self.btn_cancel.pack(side="left")
        return btn_frame

    def _on_eingabe_fenster_resize(self, event):
        """Haelt den Umbruch der Hinweiszeile an der Fensterbreite -- an das
        Label selbst gebunden geriete die Messung in eine Schleife (der
        Umbruch aendert die Hoehe, die Hoehe loest ein neues Ereignis aus).

        Wichtig: event.widget auf das Fenster selbst pruefen. Tk teilt
        Bindtags zwischen einer Toplevel und all ihren Kindern -- eine auf
        das Fenster gebundene <Configure>-Behandlung feuert sonst bei JEDER
        Groessenaenderung JEDES Kind-Widgets (Comboboxen, Labelframes, ...)
        mit, und die zuletzt verarbeitete -- meist ein winziges inneres
        Widget -- ueberschreibt die Umbruchbreite mit einem viel zu kleinen
        Wert.
        """
        if event.widget is not self._eingabe_fenster:
            return
        if self.lbl_mode_hinweis is not None:
            self.lbl_mode_hinweis.configure(
                wraplength=max(200, event.width - 2 * PAD_MEDIUM))

    def _size_and_center_eingabe_fenster(self, fenster):
        """Bemisst das Fenster nach dem tatsaechlichen Bedarf des Formulars
        (Rollbereich + Ergebnis + Knopfleiste, ggf. Hinweiszeile), deckelt
        die Hoehe auf die Bildschirmhoehe und zentriert ueber dem
        Hauptfenster. Der Canvas im Rollbereich gibt seine eigene
        Soll-Groesse nicht an den Inhalt weiter -- gemessen wird darum am
        form_frame selbst, nicht am Canvas.

        Die Breite steht zuerst fest (haengt nicht von der Hinweiszeile ab);
        deren Umbruchbreite wird darum HIER explizit aus dem Ergebnis
        gesetzt, statt sich auf das <Configure>-Ereignis zu verlassen --
        das feuert waehrend des Aufbaus mehrfach mit vorlaeufigen Breiten
        (siehe _on_eingabe_fenster_resize) und lieferte sonst eine falsche
        Hoehe fuer die Hinweiszeile.
        """
        breite = max(self.form_frame.winfo_reqwidth(),
                    self._eingabe_ergebnis_frame.winfo_reqwidth()) + 2 * PAD_MEDIUM
        breite = max(breite, 520)

        if self.lbl_mode_hinweis.winfo_ismapped():
            self.lbl_mode_hinweis.configure(
                wraplength=max(200, breite - 2 * PAD_MEDIUM))
            self.lbl_mode_hinweis.update_idletasks()

        inhalt_h = (self.form_frame.winfo_reqheight()
                   + self._eingabe_ergebnis_frame.winfo_reqheight()
                   + self._eingabe_btn_frame.winfo_reqheight())
        if self.lbl_mode_hinweis.winfo_ismapped():
            inhalt_h += self.lbl_mode_hinweis.winfo_reqheight() + PAD_SMALL

        hoehe = inhalt_h + 2 * PAD_SMALL + 20
        hoehe = min(hoehe, self.winfo_screenheight() - 80)

        mx, my = self.winfo_x(), self.winfo_y()
        mw, mh = self.winfo_width(), self.winfo_height()
        x = mx + max(0, (mw - breite) // 2)
        y = my + max(0, (mh - hoehe) // 2)

        fenster.geometry(f"{breite}x{hoehe}+{x}+{y}")

    def _on_eingabe_fenster_close(self):
        """Abbrechen oder Schliesskreuz: fragt bei ungesicherten Eingaben
        nach, schliesst dann."""
        if not self._darf_formular_verwerfen():
            return
        self._destroy_eingabe_fenster()
        self._clear_selection()

    def _destroy_eingabe_fenster(self):
        """Raeumt das Eingabefenster vollstaendig ab: Punkte-IntVar-Traces
        loesen, alle Formular-Widget-Referenzen auf None/leer setzen,
        Fenster zerstoeren.

        Ohne das Loesen der Traces koennte eine verwaiste IntVar nach dem
        Schliessen noch _recalc() ausloesen, das dann auf bereits zerstoerte
        Comboboxen zugreift (TclError) -- die Absicherung in _recalc()
        selbst (Rueckgabe, solange kein Fenster offen ist) faengt das
        zusaetzlich ab.
        """
        fenster = self._eingabe_fenster
        self._eingabe_fenster = None

        for teil_vars in self._punkt_vars:
            for var in teil_vars:
                trace_id = getattr(var, "_e1_trace_id", None)
                if trace_id is not None:
                    try:
                        var.trace_remove("write", trace_id)
                    except tk.TclError:
                        pass

        self._punkt_vars = []
        self._cat_cmbs = []
        self._teil_sum_labels = []
        self.form_frame = None
        self._form_canvas = None
        self._form_vsb = None
        self._form_window = None
        self.cmb_monat = None
        self.spn_jahr = None
        self.cmb_joker1 = None
        self.cmb_joker2 = None
        self.ent_sonderrunde = None
        self.spn_platz = None
        self.spn_von = None
        self.lbl_bonus_value = None
        self.lbl_pct = None
        self.lbl_gesamt = None
        self.lbl_mode_hinweis = None
        self._left_frame = None
        self._right_frame = None
        self._eingabe_ergebnis_frame = None
        self._eingabe_btn_frame = None
        self.btn_save = None
        self.btn_cancel = None

        if fenster is not None:
            try:
                fenster.grab_release()
            except tk.TclError:
                pass
            fenster.destroy()

    def _on_tree_resize(self, event):
        """Blendet die waagrechte Leiste der Tabelle nur bei Bedarf ein."""
        noetig = sum(int(self.tree.column(c, "width"))
                     for c in self.tree.cget("columns"))
        if noetig > event.width:
            if not self._tree_hsb.winfo_ismapped():
                # 'before' ist noetig: Der Baum ist mit expand=True zuerst
                # gepackt und haette sonst den ganzen Raum verbraucht -- die
                # Leiste erschiene zwar als gepackt, bekaeme aber keine Hoehe.
                self._tree_hsb.pack(side="bottom", fill="x", before=self.tree)
        elif self._tree_hsb.winfo_ismapped():
            self._tree_hsb.pack_forget()
            self.tree.xview_moveto(0)

    def _on_form_canvas_resize(self, event):
        """Haelt das Formular auf Canvas-Breite und blendet die Rollleiste
        nur ein, wenn die Hoehe wirklich nicht reicht."""
        self._form_canvas.itemconfigure(self._form_window, width=event.width)
        noetig = self.form_frame.winfo_reqheight()
        if noetig > event.height:
            if not self._form_vsb.winfo_ismapped():
                self._form_vsb.pack(side="right", fill="y")
        elif self._form_vsb.winfo_ismapped():
            self._form_vsb.pack_forget()
            self._form_canvas.yview_moveto(0)

    def _on_form_wheel(self, event):
        """Mausrad im Formular -- nur wirksam, wenn es etwas zu rollen gibt."""
        if self._form_vsb.winfo_ismapped():
            self._form_canvas.yview_scroll(-int(event.delta / 120), "units")

    def _build_eckdaten(self, row):
        """Eckdaten-Block: Monat, Jahr, Joker, Sonderrunde, Platzierung."""
        lf = ttk.LabelFrame(self.form_frame, text="Eckdaten")
        lf.grid(row=row, column=0, sticky="new",
                padx=PAD_MEDIUM, pady=(PAD_SMALL, 0))
        self._left_frame = lf
        # Spalte 4 nimmt den Ueberschuss. Haetten die Feldspalten das Gewicht,
        # risse es "Jahr" quer durch den Rahmen von "Monat" weg.
        lf.columnconfigure(4, weight=1)

        zeile_pady = (PAD_SMALL, PAD_SMALL)

        # Monat / Jahr
        ttk.Label(lf, text="Monat:").grid(
            row=0, column=0, sticky="w", padx=PAD_SMALL, pady=zeile_pady)
        self.cmb_monat = ttk.Combobox(lf, values=GERMAN_MONTHS, state="readonly",
                                      width=10, font=FONT_NORMAL)
        self.cmb_monat.grid(row=0, column=1, sticky="w",
                            padx=PAD_SMALL, pady=zeile_pady)
        _bind_combo_typeahead(self.cmb_monat)

        ttk.Label(lf, text="Jahr:").grid(
            row=0, column=2, sticky="w", padx=(PAD_MEDIUM, PAD_SMALL),
            pady=zeile_pady)
        # Zahlen zentriert: In einem schmalen Feld klebt eine rechts- oder
        # linksbuendige Ziffer unweigerlich an einer der beiden Kanten.
        self.spn_jahr = ttk.Spinbox(lf, from_=2024, to=2099, width=8,
                                    font=FONT_NORMAL, justify="center")
        self.spn_jahr.grid(row=0, column=3, sticky="w",
                           padx=PAD_SMALL, pady=zeile_pady)

        # Joker 1 -- '(keiner)' steht als erste Wahl fuer einen Abend ohne Joker.
        ttk.Label(lf, text="Joker 1:").grid(
            row=1, column=0, sticky="w", padx=PAD_SMALL, pady=zeile_pady)
        self.cmb_joker1 = ttk.Combobox(lf, values=JOKER_CHOICES,
                                        state="normal", width=24,
                                        font=FONT_NORMAL)
        self.cmb_joker1.grid(row=1, column=1, columnspan=3, sticky="ew",
                              padx=PAD_SMALL, pady=zeile_pady)
        _bind_combo_autocomplete(self.cmb_joker1)
        self.cmb_joker1.bind("<<ComboboxSelected>>", lambda e: self._recalc())
        self.cmb_joker1.bind("<FocusOut>", lambda e: self._recalc())

        # Joker 2
        ttk.Label(lf, text="Joker 2:").grid(
            row=2, column=0, sticky="w", padx=PAD_SMALL, pady=zeile_pady)
        self.cmb_joker2 = ttk.Combobox(lf, values=JOKER_CHOICES,
                                        state="normal", width=24,
                                        font=FONT_NORMAL)
        self.cmb_joker2.grid(row=2, column=1, columnspan=3, sticky="ew",
                              padx=PAD_SMALL, pady=zeile_pady)
        _bind_combo_autocomplete(self.cmb_joker2)
        self.cmb_joker2.bind("<<ComboboxSelected>>", lambda e: self._recalc())
        self.cmb_joker2.bind("<FocusOut>", lambda e: self._recalc())

        # Sonderrunden-Thema
        ttk.Label(lf, text="Sonderrunde:").grid(
            row=3, column=0, sticky="w", padx=PAD_SMALL, pady=zeile_pady)
        self.ent_sonderrunde = ttk.Entry(lf, width=28, font=FONT_NORMAL)
        self.ent_sonderrunde.grid(row=3, column=1, columnspan=3, sticky="ew",
                                   padx=PAD_SMALL, pady=zeile_pady)

        # Platz / Von
        ttk.Label(lf, text="Platz:").grid(
            row=4, column=0, sticky="w", padx=PAD_SMALL, pady=zeile_pady)
        self.spn_platz = ttk.Spinbox(lf, from_=1, to=50, width=7,
                                     font=FONT_NORMAL, justify="center")
        self.spn_platz.grid(row=4, column=1, sticky="w",
                             padx=PAD_SMALL, pady=zeile_pady)

        ttk.Label(lf, text="von:").grid(
            row=4, column=2, sticky="w", padx=(PAD_MEDIUM, PAD_SMALL),
            pady=zeile_pady)
        self.spn_von = ttk.Spinbox(lf, from_=1, to=50, width=8,
                                    font=FONT_NORMAL, justify="center")
        self.spn_von.grid(row=4, column=3, sticky="w",
                          padx=PAD_SMALL, pady=zeile_pady)

    def _build_ergebnis(self, parent):
        """Ergebnis-Block: Joker-Punkte, Gesamt, Quote -- alles live gerechnet.

        Liegt ausserhalb des Rollbereichs, direkt ueber den Aktionsknoepfen
        (als Kind von form_frame verschwand er bei kleinen Fenstern im
        Rollbereich -- der Gesamtstand war beim Druck auf 'Speichern' nicht
        zu sehen). Gibt den Rahmen zurueck, zur Hoehenmessung in
        _size_and_center_eingabe_fenster.
        """
        lf = ttk.LabelFrame(parent, text="Ergebnis")
        lf.pack(side="bottom", fill="x", padx=PAD_MEDIUM,
               pady=(PAD_SMALL, PAD_SMALL))
        # Spalte 1 (links der Quote) und Spalte 3 (rechts, vor "Gesamt")
        # tragen zu gleichen Teilen die freie Breite -- zusammen mit
        # sticky="" auf lbl_pct sitzt "% richtig" dadurch mittig zwischen
        # Joker-Punkten und Gesamt (gemessen: 267 px Leere vor der Quote,
        # 273 px danach bei maximiertem Fenster -- vorher 385 zu 20).
        # Eine Gewichtung von Spalte 1 UND der Quote-Spalte selbst (statt
        # Spalte 3) ergab messbar nur ein 2:1-Verhaeltnis, keine Mitte.
        lf.columnconfigure(1, weight=1)
        lf.columnconfigure(3, weight=1)

        ttk.Label(lf, text="Joker-Punkte:").grid(
            row=0, column=0, sticky="w", padx=PAD_SMALL, pady=PAD_SMALL)
        self.lbl_bonus_value = ttk.Label(lf, text="0 Pkt.",
                                          font=FONT_NORMAL,
                                          foreground=TEXT_PRIMARY)
        self.lbl_bonus_value.grid(row=0, column=1, sticky="w",
                                   padx=PAD_SMALL, pady=PAD_SMALL)

        self.lbl_pct = ttk.Label(lf, text="% richtig: 0,0 % (von 60)",
                                  font=FONT_NORMAL, foreground=TEXT_SECONDARY)
        self.lbl_pct.grid(row=0, column=2, sticky="",
                           padx=PAD_MEDIUM, pady=PAD_SMALL)

        self.lbl_gesamt = ttk.Label(lf, text="Gesamt (mit Joker): 0 Pkt.",
                                    font=FONT_GROSS, foreground=TEXT_PRIMARY)
        self.lbl_gesamt.grid(row=0, column=3, sticky="e",
                              padx=(PAD_MEDIUM, PAD_SMALL), pady=PAD_SMALL)
        return lf

    def _build_teile(self, row):
        """Die vier Teil-Blöcke unter den Eckdaten.

        TEILE_SPALTEN bestimmt, ob sie in einer Spalte untereinander (1)
        oder zu zweit nebeneinander (2) stehen. Eingestellt ist 1:
        Untereinander bekommt jede Kategorie-Zeile die volle Formularbreite
        -- bei Namen wie "Wissensch./Natur" mehr Luft als eine halbierte
        Spalte. Das Formular steht seit dem Umbau in einem eigenen Fenster
        (_open_eingabe_fenster), das sich an seinen tatsaechlichen Bedarf
        anpasst (zuletzt gemessen: rund 810 px Inhaltshoehe, 672 px Breite
        im Neu-Modus) -- der Rollbereich bleibt trotzdem als Auffangnetz
        bestehen, falls Systemschrift oder Bildschirmhoehe es einmal eng
        machen. TEILE_SPALTEN=2 bleibt als Rueckfallmoeglichkeit, falls
        zwei Spalten einmal wieder gebraucht werden.
        """
        raster = ttk.Frame(self.form_frame)
        raster.grid(row=row, column=0, sticky="nsew",
                    padx=PAD_MEDIUM, pady=(PAD_SMALL, 0))
        self._right_frame = raster

        for sp in range(TEILE_SPALTEN):
            raster.columnconfigure(sp, weight=1, uniform="teile")

        # Punkte-Spalte: feste Mindestbreite, gemessen an der tatsaechlichen
        # Kopfzeile "Punkte (0-5)" (die es nur in Teil 1 gibt). Ohne diesen
        # Deckel zieht genau diese Kopfzeile die Punkte-Spalte von Teil 1
        # breiter als die der Teile 2 bis 4 -- jeder der vier Rahmen bemisst
        # seine Spalten unabhaengig, und nur Teil 1 traegt den breiten
        # Kopftext. Die Kategorie-Spalte (Spaltengewicht 2) verliert dadurch
        # in Teil 1 Breite an die Punkte-Spalte, waehrend sie in Teil 2 bis 4
        # den vollen Anteil bekommt -- sichtbar als drei schmalere
        # Comboboxen oben. Gemessen wird ueber winfo_reqwidth() DES ECHTEN
        # Labels (nicht per tkfont.Font nachgerechnet) -- eine Font-Messung
        # allein uebersieht das Innenpolster, das der ttk-Stil "TLabel"
        # jedem Label zusaetzlich mitgibt (EINZUG_X in _setup_styles), und
        # traf die Spaltenbreite real um gut 18 px zu knapp.
        teil_frames = []       # [teil] -> LabelFrame, fuer den Minsize-Deckel
        punkte_header_lbl = None

        # 12 IntVars fuer Punkte, Comboboxen fuer Kategorien
        self._punkt_vars = []   # [teil][slot] -> IntVar
        self._cat_cmbs = []     # [teil][slot] -> Combobox
        self._teil_sum_labels = []  # [teil] -> Label (traegt NUR die Zahl)

        for t in range(4):
            zeile, spalte = divmod(t, TEILE_SPALTEN)
            lf = ttk.LabelFrame(raster, text=f"Teil {t + 1}")
            lf.grid(row=zeile, column=spalte, sticky="new",
                    padx=(0, PAD_SMALL) if spalte == 0 else (PAD_SMALL, 0),
                    pady=(0, PAD_SMALL))
            # Die Kategorie waechst mit, das Punktefeld bleibt dicht daneben.
            # Beide Extreme waren schlechter: ueber die ganze Haelfte gezogen
            # mass das Kategoriefeld 890 px und stand fast leer da; ganz rechts
            # am Rahmenrand lag die Punktzahl 500 px von ihrer Kategorie
            # entfernt -- zum Eintragen ein weiter Weg fuer Auge und Maus.
            # 2:3 statt 3:1 -- die alte Gewichtung liess das Kategoriefeld
            # bei voller Breite wieder auf die eingangs genannten 890 px
            # wachsen; die leere Spalte 2 bekommt jetzt den groesseren Teil.
            lf.columnconfigure(0, weight=2)
            lf.columnconfigure(2, weight=3)
            teil_frames.append(lf)

            teil_vars = []
            teil_cmbs = []

            # Kopfzeile nur in Teil 1 -- die Rahmen 2 bis 4 erben die Lesart.
            start_row = 0
            if t == 0:
                ttk.Label(lf, text="Kategorie", font=FONT_SMALL,
                         foreground=TEXT_SECONDARY).grid(
                    row=0, column=0, sticky="w",
                    padx=PAD_SMALL, pady=(PAD_SMALL, 0))
                punkte_header_lbl = ttk.Label(
                    lf, text="Punkte (0–5)", font=FONT_SMALL,
                    foreground=TEXT_SECONDARY)
                punkte_header_lbl.grid(
                    row=0, column=1, sticky="w",
                    padx=(PAD_SMALL, PAD_MEDIUM), pady=(PAD_SMALL, 0))
                start_row = 1

            for s in range(3):
                var = tk.IntVar(value=0)
                # Trace-Id gemerkt: _destroy_eingabe_fenster loest sie,
                # sonst koennte eine verwaiste IntVar nach dem Schliessen
                # noch _recalc() auf bereits zerstoerten Widgets ausloesen.
                var._e1_trace_id = var.trace_add("write", self._recalc)
                teil_vars.append(var)

                cmb = ttk.Combobox(lf, values=list(CATEGORIES), state="normal",
                                   width=28, font=FONT_NORMAL)
                cmb.grid(row=start_row + s, column=0, sticky="ew",
                         padx=PAD_SMALL, pady=2)
                _bind_combo_autocomplete(cmb)
                cmb.bind("<<ComboboxSelected>>", self._on_cat_changed)
                cmb.bind("<FocusOut>", self._on_cat_changed)
                teil_cmbs.append(cmb)

                spn = ttk.Spinbox(lf, from_=0, to=5, width=5,
                                  textvariable=var, font=FONT_NORMAL,
                                  justify="center")
                spn.grid(row=start_row + s, column=1, sticky="w",
                         padx=(PAD_SMALL, PAD_MEDIUM), pady=2)

            # Rechnungsstrich: doppelte Querlinie in der Breite der
            # Punkte-Spalte, direkt unter dem dritten Punktefeld -- wie bei
            # einer Additionsaufgabe von Hand. sticky="ew" dehnt den Rahmen
            # exakt auf die Spaltenbreite, die die Spinboxen darueber schon
            # festlegen; die beiden 1-px-Kindframes ziehen sich per fill="x"
            # auf diese Breite nach.
            linie_frame = tk.Frame(lf, bg=BACKGROUND)
            linie_frame.grid(row=start_row + 3, column=1, sticky="ew",
                              padx=(PAD_SMALL, PAD_MEDIUM), pady=(4, 0))
            tk.Frame(linie_frame, height=1, bg=TEXT_PRIMARY).pack(fill="x")
            tk.Frame(linie_frame, height=1, bg=TEXT_PRIMARY).pack(
                fill="x", pady=(2, 0))

            # Beschriftung rechtsbuendig links daneben, Zahl fett und in
            # derselben Spalte/Ausrichtung (zentriert) wie die drei
            # Punktzahlen darueber.
            ttk.Label(lf, text=f"Summe Teil {t + 1}:",
                      font=FONT_NORMAL, foreground=TEXT_SECONDARY).grid(
                row=start_row + 4, column=0, sticky="e",
                padx=PAD_SMALL, pady=(1, 2))
            lbl_sum = ttk.Label(lf, text="0", font=FONT_SUM,
                                 foreground=TEXT_PRIMARY, anchor="center")
            lbl_sum.grid(row=start_row + 4, column=1, sticky="ew",
                          padx=(PAD_SMALL, PAD_MEDIUM), pady=(1, 2))

            self._punkt_vars.append(teil_vars)
            self._cat_cmbs.append(teil_cmbs)
            self._teil_sum_labels.append(lbl_sum)

        # Jetzt erst, mit dem echten Label im Baum, die Mindestbreite
        # messen und auf alle vier Punkte-Spalten gleich anwenden.
        punkte_header_lbl.update_idletasks()
        punkte_minsize = (punkte_header_lbl.winfo_reqwidth()
                          + PAD_SMALL + PAD_MEDIUM)
        for lf in teil_frames:
            lf.columnconfigure(1, minsize=punkte_minsize)

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
        """Baut den Dashboard-Reiter: nur noch die vier Diagramme im
        2x2-Raster -- die KPI-Kacheln sind in die Uebersicht umgezogen
        (_build_kpi_row), die vier Diagramme haben dadurch mehr Platz
        bekommen, die Figure-Raender sind entsprechend enger gezogen.

        Jeder Rahmen traegt oben rechts einen Knopf 'Vollansicht': Ein Klick
        blendet die drei anderen per grid_remove() aus und spannt den
        gewaehlten per rowspan/columnspan ueber das ganze Raster
        (_toggle_chart_fullview). Kein Fenster-/Eltern-Wechsel noetig --
        FigureCanvasTkAgg passt die Zeichenflaeche beim Grid-Wechsel von
        selbst an, draw_idle() danach ist nur das Sicherheitsnetz.
        """
        import matplotlib
        matplotlib.use("TkAgg")
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        charts = tk.Frame(parent, bg=BACKGROUND)
        charts.pack(fill="both", expand=True, padx=PAD_MEDIUM,
                   pady=(PAD_MEDIUM, PAD_MEDIUM))
        charts.columnconfigure(0, weight=1, uniform="charts")
        charts.columnconfigure(1, weight=1, uniform="charts")
        charts.rowconfigure(0, weight=1, uniform="charts")
        charts.rowconfigure(1, weight=1, uniform="charts")

        self._chart_frames = {}        # key -> Rahmen (tk.Frame)
        self._chart_buttons = {}       # key -> Vollansicht-Knopf
        self._chart_grid_info = {}     # key -> {"row":.., "column":..}
        self._chart_canvases_by_key = {}
        self._chart_fullview_key = None

        def _chart_frame(row, col, key, raender):
            rahmen = tk.Frame(charts, bg=CARD_BG,
                              highlightbackground="#d1d5db",
                              highlightthickness=1)
            rahmen.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)
            self._chart_frames[key] = rahmen
            self._chart_grid_info[key] = {"row": row, "column": col}

            kopf = tk.Frame(rahmen, bg=CARD_BG)
            kopf.pack(side="top", fill="x")
            # Keine feste width: Der Knopftext wechselt zu "Zurück zur
            # Übersicht" (21 Zeichen) -- eine auf "Vollansicht" (11 Zeichen)
            # bemessene Breite schnitt den laengeren Text sichtbar ab.
            btn = ttk.Button(kopf, text="Vollansicht",
                             command=lambda k=key: self._toggle_chart_fullview(k))
            btn.pack(side="right", padx=4, pady=2)
            self._chart_buttons[key] = btn

            fig = Figure(figsize=(5.5, 3.2), dpi=100, facecolor=CARD_BG)
            fig.subplots_adjust(**raender)
            ax = fig.add_subplot(111)
            canvas = FigureCanvasTkAgg(fig, master=rahmen)
            canvas.get_tk_widget().pack(fill="both", expand=True,
                                        padx=2, pady=2)
            self._chart_canvases_by_key[key] = canvas
            return ax, canvas

        # Raender je Diagramm einzeln, enger als zuvor -- ohne die KPI-Zeile
        # darueber steht mehr Hoehe zur Verfuegung, und die Beschriftungen
        # (Kategorienamen links, rotierte Monatsnamen unten) brauchen davon
        # nur noch einen kleineren Anteil. Ranking und Heatmap brauchen links
        # weiterhin mehr Platz fuer die Kategorienamen, Trend rechts fuer die
        # Sekundaerachse (Platzierung).
        self._ax_trend, self._canvas_trend = _chart_frame(
            0, 0, "trend", dict(left=0.09, right=0.91, top=0.93, bottom=0.17))
        self._ax_ranking, self._canvas_ranking = _chart_frame(
            0, 1, "ranking", dict(left=0.20, right=0.97, top=0.93, bottom=0.12))
        self._ax_heat, self._canvas_heat = _chart_frame(
            1, 0, "heat", dict(left=0.20, right=0.98, top=0.93, bottom=0.18))
        self._ax_scatter, self._canvas_scatter = _chart_frame(
            1, 1, "scatter", dict(left=0.09, right=0.98, top=0.93, bottom=0.12))

        self._dashboard_canvases = [self._canvas_trend, self._canvas_ranking,
                                    self._canvas_heat, self._canvas_scatter]

    def _toggle_chart_fullview(self, key):
        """Knopf 'Vollansicht'/'Zurück zur Übersicht' je Diagrammrahmen."""
        if self._chart_fullview_key == key:
            self._show_chart_grid()
        else:
            self._show_chart_fullview(key)

    def _show_chart_fullview(self, key):
        self._chart_fullview_key = key
        for k, rahmen in self._chart_frames.items():
            if k == key:
                rahmen.grid(row=0, column=0, rowspan=2, columnspan=2,
                           sticky="nsew", padx=4, pady=4)
                self._chart_buttons[k].configure(text="Zurück zur Übersicht")
            else:
                rahmen.grid_remove()
        canvas = self._chart_canvases_by_key.get(key)
        if canvas is not None:
            canvas.draw_idle()

    def _show_chart_grid(self):
        self._chart_fullview_key = None
        for k, rahmen in self._chart_frames.items():
            info = self._chart_grid_info[k]
            rahmen.grid(row=info["row"], column=info["column"],
                       rowspan=1, columnspan=1, sticky="nsew", padx=4, pady=4)
            self._chart_buttons[k].configure(text="Vollansicht")
        for canvas in self._dashboard_canvases:
            canvas.draw_idle()

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
        """Aktualisiert die KPI-Kacheln (Uebersicht-Reiter, immer sichtbar)
        und, falls der Dashboard-Reiter bereits gebaut ist, auch dessen
        vier Diagramme. Die KPI-Kacheln haengen seit dem Umbau nicht mehr
        am verzoegerten Dashboard-Bau -- sie stehen von Anfang an im
        Uebersicht-Reiter."""
        data = compute_dashboard_data(self.quiz_nights)
        self._refresh_kpis(data["kpis"])
        if not getattr(self, "_dashboard_built", False):
            return
        self._draw_trend(data["trend"])
        self._draw_ranking(data["ranking"])
        self._draw_heatmap(data["heatmap"])
        self._draw_scatter(data["scatter"])
        for canvas in self._dashboard_canvases:
            canvas.draw_idle()

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
        # "ohne Joker" dazu: Die Quote bezieht sich auf die reinen
        # Spielpunkte (Pct_richtig = Summe Teil1-4 / 60) -- der Joker-Bonus
        # fliesst hier bewusst nicht ein, anders als bei "Gesamt (mit Joker)".
        self._kpi_cards[1]["sub"].configure(
            text="von max. 60 Fragen, ohne Joker")

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
            ax.set_title("Platzierung & Quote", fontsize=12)
            ax.set_axis_off()
            return
        x = range(len(monate))
        ax.bar(x, pct, color="#6baed6", alpha=0.75, label="% richtig")
        ax.set_ylim(0, 1)
        ax.set_ylabel("% richtig", fontsize=10)
        ax.set_xticks(list(x))
        ax.set_xticklabels(monate, rotation=30, ha="right", fontsize=9)
        ax.tick_params(axis="y", labelsize=9)
        ax.set_title("Platzierung & Quote pro Quizabend", fontsize=12)
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
            ax2.set_ylabel("Platz", fontsize=10)
            ax2.tick_params(axis="y", labelsize=9)

    def _draw_ranking(self, ranking):
        """Horizontaler Bar: Kategorie-Mittelwerte, absteigend."""
        ax = self._ax_ranking
        ax.clear()
        if not ranking:
            ax.set_title("Kategorie-Ranking", fontsize=12)
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
        ax.set_xlabel("Ø Punkte (max. 5)", fontsize=10)
        ax.set_title("Kategorie-Ranking", fontsize=12)
        ax.tick_params(axis="both", labelsize=9)
        ax.grid(axis="x", alpha=0.15)
        for bar, v in zip(bars, vals):
            ax.text(v + 0.05, bar.get_y() + bar.get_height()/2,
                    f"{v:.1f}", va="center", fontsize=9, color="#374151")

    def _draw_heatmap(self, heat):
        """Heatmap Kategorien x Monate, RdYlBu_r."""
        ax = self._ax_heat
        ax.clear()
        monate = heat["monate"]
        kats = heat["kategorien"]
        matrix = heat["matrix"]
        if not monate or not kats:
            ax.set_title("Heatmap", fontsize=12)
            ax.set_axis_off()
            return
        import matplotlib.cm as cm
        im = ax.imshow(matrix, cmap="RdYlBu_r", aspect="auto",
                       vmin=0, vmax=5)
        ax.set_xticks(range(len(monate)))
        ax.set_xticklabels(monate, rotation=30, ha="right", fontsize=9)
        ax.set_yticks(range(len(kats)))
        ax.set_yticklabels(kats, fontsize=9)
        ax.set_title("Punkte-Heatmap (Kategorien × Monate)", fontsize=12)
        # Zellbeschriftung mit Punktzahl
        for i, row in enumerate(matrix):
            for j, val in enumerate(row):
                ax.text(j, i, str(val), ha="center", va="center",
                        fontsize=9, color="#374151")

    def _draw_scatter(self, scatter):
        """Scatter Std vs. Mittelwert mit Kategorie-Labels (Standard-Annotation)."""
        ax = self._ax_scatter
        ax.clear()
        if not scatter:
            ax.set_title("Stärke vs. Konsistenz", fontsize=12)
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
                        fontsize=9, color="#374151")
        ax.set_xlabel("Streuung σ (links = konstanter)", fontsize=10)
        ax.set_ylabel("Ø Punkte", fontsize=10)
        ax.set_title("Stärke vs. Konsistenz", fontsize=12)
        ax.tick_params(axis="both", labelsize=9)
        ax.grid(alpha=0.15)

    # ------------------------------------------------------------------
    # Tab-Wechsel
    # ------------------------------------------------------------------
    def _on_tab_changed(self, event=None):
        """Refresh beim Wechsel auf den Dashboard- oder Erkenntnisse-Reiter."""
        if not hasattr(self, "_insights_inner"):
            return
        current = self.notebook.select()
        if str(current) == str(self._tab_dashboard):
            if not self._dashboard_built:
                self._build_dashboard_tab(self._tab_dashboard)
                self._dashboard_built = True
            self._refresh_dashboard()
        elif str(current) == str(self._tab_insights):
            self._refresh_insights()

    # ------------------------------------------------------------------
    # Daten laden / Treeview befuellen
    # ------------------------------------------------------------------
    def _load_data(self):
        """Laedt Daten aus data.json, befuellt den Treeview.

        Bei defekter/unlesbarer Datei wird eine Sicherungskopie angelegt,
        bevor mit leerer Liste gestartet wird — sonst wuerde der naechste
        Speichervorgang die Historie stillschweigend ueberschreiben."""
        try:
            data = load_data()
            self.quiz_nights = data.get("quiz_nights", [])
        except Exception:
            self.quiz_nights = []
            if DATA_PATH.exists():
                zeitstempel = datetime.now().strftime("%Y%m%d-%H%M%S")
                sicherung = DATA_PATH.with_name(f"data.json.defekt_{zeitstempel}")
                try:
                    shutil.copy2(DATA_PATH, sicherung)
                    messagebox.showwarning(
                        "Daten nicht lesbar",
                        f"{DATA_PATH.name} konnte nicht gelesen werden.\n"
                        f"Eine Sicherung wurde angelegt:\n{sicherung.name}\n\n"
                        "Die App startet mit einer leeren Liste.",
                    )
                except OSError as sicherungs_fehler:
                    messagebox.showwarning(
                        "Daten nicht lesbar",
                        f"{DATA_PATH.name} konnte nicht gelesen werden und "
                        f"auch keine Sicherung angelegt werden ({sicherungs_fehler}).\n\n"
                        "Die App startet mit einer leeren Liste.",
                    )
        self._tune_sonderrunde_spalte()
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
            joker1 = night.get("Joker1") or "–"
            joker2 = night.get("Joker2") or "–"
            sonderrunde = night.get("Sonderrunde_Thema", "")
            teil1 = night.get("Teil1", 0) or 0
            teil2 = night.get("Teil2", 0) or 0
            teil3 = night.get("Teil3", 0) or 0
            teil4 = night.get("Teil4", 0) or 0
            punkte = teil1 + teil2 + teil3 + teil4  # Spielpunkte ohne Joker-Bonus
            bonus = night.get("Bonus", 0) or 0
            gesamt = night.get("Gesamt", 0) or 0
            pct = night.get("Pct_richtig", 0.0) or 0.0
            pct_str = f"{pct * 100:.1f}".replace(".", ",") + " %"
            platz = night.get("Platzierung")
            von = night.get("Von")
            platz_str = f"{platz} / {von}" if platz is not None else "–"
            # Einzug der linksbuendigen Spalten ueber ein vorangestelltes
            # Leerzeichen: ttk kennt fuer die Datenzellen eines Treeview kein
            # Innenpolster -- ein Stil-Padding greift nur am Spaltenkopf und an
            # der Baumspalte. Ohne das klebte jeder Eintrag an der Trennlinie.
            # Die zentrierten Zahlenspalten brauchen es nicht.
            self.tree.insert("", "end", iid=datum,
                             values=(ZELL_EINZUG + monat_lang,
                                     ZELL_EINZUG + joker1,
                                     ZELL_EINZUG + joker2,
                                     ZELL_EINZUG + sonderrunde,
                                     teil1, teil2, teil3, teil4,
                                     punkte, bonus, gesamt, pct_str, platz_str))

        # Aktive Sortierung (Default: Datum absteigend) auf die frisch
        # befuellte Tabelle anwenden -- so bleibt ein vom Nutzer gewaehltes
        # Sortierkriterium auch nach Speichern/Bearbeiten/Loeschen bestehen.
        self._apply_tree_sort()

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
    # Sortierung der Tabelle "Bisherige Abende"
    # ------------------------------------------------------------------
    def _night_by_datum(self, datum):
        """Sucht einen Abend ueber sein ISO-Datum (== Treeview-iid)."""
        for night in self.quiz_nights:
            if night.get("Datum") == datum:
                return night
        return None

    def _on_tree_heading_click(self, col):
        """Klick auf einen Spaltenkopf: sortiert danach, zweiter Klick dreht um."""
        if self._sort_column == col:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column = col
            self._sort_reverse = False
        self._apply_tree_sort()

    def _tree_sort_key(self, col):
        """Liefert die Sortier-Schluesselfunktion fuer eine Spalte.

        Zahlenspalten (T1-T4, Punkte, Joker-Pkt., Gesamt) sortieren
        numerisch ueber den reinen Zellwert, "Quote" und "Platz / Von" ueber
        die zugrundeliegenden Datenfelder (die Zelle selbst traegt bei der
        Quote eine formatierte Prozentzahl, bei Platz/Von einen
        Bruch-Text -- beides ist nicht direkt in float() ueberfuehrbar).
        "Monat" sortiert ueber die iid -- das ISO-Datum -- chronologisch
        statt alphabetisch. Alles andere faellt auf den (vom ZELL_EINZUG
        befreiten) Anzeigetext zurueck.
        """
        if col == "monat":
            return lambda iid: iid  # iid ist das ISO-Datum: "YYYY-MM-DD"
        if col in ("teil1", "teil2", "teil3", "teil4", "punkte", "bonus", "gesamt"):
            def _zahl_key(iid):
                try:
                    return float(self.tree.set(iid, col))
                except (ValueError, TypeError):
                    return float("-inf")
            return _zahl_key
        if col == "pct":
            def _pct_key(iid):
                night = self._night_by_datum(iid)
                return night.get("Pct_richtig", 0.0) if night else 0.0
            return _pct_key
        if col == "platz":
            def _platz_key(iid):
                night = self._night_by_datum(iid)
                platz = night.get("Platzierung") if night else None
                return platz if platz is not None else float("inf")
            return _platz_key

        def _text_key(iid):
            return self.tree.set(iid, col).strip().lower()
        return _text_key

    def _update_tree_headings(self):
        """Haengt ein ▲/▼ an den Kopf der aktiven Sortierspalte an."""
        for col, basis in self._tree_heading_base.items():
            if col == self._sort_column:
                pfeil = " ▼" if self._sort_reverse else " ▲"
                self.tree.heading(col, text=basis + pfeil)
            else:
                self.tree.heading(col, text=basis)

    def _apply_tree_sort(self):
        """Ordnet die vorhandenen Zeilen nach dem aktiven Kriterium neu an.

        Nutzt tree.move() auf die bestehenden iids -- Auswahl und
        Bearbeiten haengen an der iid, nicht an der Zeilenposition, und
        bleiben darum unberuehrt.
        """
        key = self._tree_sort_key(self._sort_column)
        items = sorted(self.tree.get_children(""), key=key,
                       reverse=self._sort_reverse)
        for index, iid in enumerate(items):
            self.tree.move(iid, "", index)
        self._update_tree_headings()

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
        return self._night_by_datum(sel[0])

    # ------------------------------------------------------------------
    # Live-Berechnung
    # ------------------------------------------------------------------
    def _on_cat_changed(self, event=None):
        """Nach Auswahl/Verlassen einer Kategorie-Combobox: neu rechnen und
        die Auswahllisten der uebrigen Slots aktualisieren."""
        if self._eingabe_fenster is None:
            return
        self._recalc()
        self._refresh_cat_choices()

    def _refresh_cat_choices(self):
        """Blendet bereits belegte Kategorien in allen anderen Slots aus.

        Jede der 12 Kategorien wird genau einmal gespielt -- ist sie in einem
        Slot gewaehlt, verschwindet sie aus den Dropdown-Listen der uebrigen
        Slots. Der eigene Wert bleibt in der eigenen Liste erhalten.
        """
        if self._eingabe_fenster is None:
            return
        used = set()
        for t in range(4):
            for s in range(3):
                v = self._cat_cmbs[t][s].get().strip()
                if v in CATEGORIES:
                    used.add(v)
        for t in range(4):
            for s in range(3):
                cmb = self._cat_cmbs[t][s]
                own = cmb.get().strip()
                avail = [c for c in CATEGORIES if c not in used or c == own]
                cmb._full_choices = avail
                cmb.configure(values=avail)

    def _recalc(self, *args):
        """Neuberechnung von Summen, Bonus, Gesamt und Pct nach Aenderungen.

        Schutz gegen eine verwaiste IntVar-Trace: Ist kein Eingabefenster
        offen, existieren die Comboboxen/Labels nicht mehr -- ein Zugriff
        waere ein TclError. _destroy_eingabe_fenster loest die Traces zwar
        explizit, dieser fruehe Ausstieg ist das zusaetzliche Netz.
        """
        if self._eingabe_fenster is None:
            return
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
            self._teil_sum_labels[t].configure(text=str(s))

        joker1 = normalize_joker(self.cmb_joker1.get())
        joker2 = normalize_joker(self.cmb_joker2.get())
        bonus = compute_bonus(joker1, joker2, cat_scores)

        gesamt = sum(teil_sums) + bonus
        pct = sum(teil_sums) / 60.0 * 100 if sum(teil_sums) > 0 else 0.0

        self.lbl_bonus_value.configure(text=f"{bonus} Pkt.")
        self.lbl_gesamt.configure(text=f"Gesamt (mit Joker): {gesamt} Pkt.")
        # Dezimalkomma wie im uebrigen Werkzeug -- "56.4 %" war die einzige
        # Stelle der Oberflaeche mit englischer Schreibweise. Der Nenner
        # (von 60) steht dazu, weil "% richtig: 0,0 %" sonst verschweigt,
        # worauf sich die Quote bezieht.
        self.lbl_pct.configure(
            text="% richtig: " + f"{pct:.1f}".replace(".", ",") + " % (von 60)")

    # ------------------------------------------------------------------
    # Formular aktivieren / deaktivieren -- entfallen (siehe unten)
    # ------------------------------------------------------------------
    # _set_form_state ist seit dem Umbau auf das eigene Eingabefenster
    # gegenstandslos: Das Formular existiert nur noch, waehrend das Fenster
    # offen ist (immer eingabebereit), und verschwindet beim Schliessen
    # vollstaendig (_destroy_eingabe_fenster) statt in einen deaktivierten
    # Zustand zu wechseln. Einen Formular-"disabled"-Zustand gibt es darum
    # nicht mehr.

    # ------------------------------------------------------------------
    # Formular-Defaults setzen
    # ------------------------------------------------------------------
    def _form_defaults(self):
        """Setzt alle Formular-Felder auf Startzustand (leerer neuer Abend)."""
        if self._eingabe_fenster is None:
            return
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

        self._refresh_cat_choices()
        self._recalc()

    # ------------------------------------------------------------------
    # Formular befuellen (Bearbeiten)
    # ------------------------------------------------------------------
    def _fill_form(self, night):
        """Befuellt das Formular mit den Daten eines bestehenden Abends."""
        if self._eingabe_fenster is None:
            return
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

        # Kein Joker gespeichert -> '(keiner)' anzeigen (nicht leer, sonst
        # meldet die Pruefung beim Speichern einen fehlenden Joker).
        self.cmb_joker1.set(night.get("Joker1") or JOKER_KEINER)
        self.cmb_joker2.set(night.get("Joker2") or JOKER_KEINER)

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

        self._refresh_cat_choices()
        self._recalc()

    # ------------------------------------------------------------------
    # Formular lesen
    # ------------------------------------------------------------------
    def _read_form(self):
        """Liest alle Formular-Werte und gibt ein form-Dict zurueck."""
        if self._eingabe_fenster is None:
            return None
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
    # Verwerfen-Schutz
    # ------------------------------------------------------------------
    def _formular_hat_eingaben(self):
        """True, wenn im Modus 'new' etwas vom Startzustand abweicht.

        Monat und Jahr zaehlen nicht mit -- die sind vorbelegt und kein
        Zeichen einer begonnenen Eingabe.
        """
        for t in range(4):
            for s in range(3):
                if self._cat_cmbs[t][s].get().strip():
                    return True
                try:
                    if self._punkt_vars[t][s].get() != 0:
                        return True
                except tk.TclError:
                    pass
        if self.ent_sonderrunde.get().strip():
            return True
        if self.cmb_joker1.get().strip():
            return True
        if self.cmb_joker2.get().strip():
            return True
        if self.spn_platz.get().strip():
            return True
        if self.spn_von.get().strip():
            return True
        return False

    def _darf_formular_verwerfen(self):
        """True, wenn das Formular ohne Rueckfrage verworfen werden darf.

        Im Modus 'new' zaehlt jede Abweichung vom Startzustand, im Modus
        'edit' jede Abweichung vom beim Laden gemerkten Abzug
        (self._edit_stand) -- zwoelf Kategorien und zwoelf Punktwerte
        gingen sonst nach einem Fehlklick ohne Rueckfrage verloren.
        """
        if isinstance(self._mode, tuple) and self._mode[0] == "edit":
            hat_aenderungen = self._read_form() != self._edit_stand
        else:
            hat_aenderungen = self._formular_hat_eingaben()
        if not hat_aenderungen:
            return True
        return messagebox.askyesno(
            "Eingaben verwerfen?",
            "Das Formular enthält nicht gespeicherte Eingaben. Verwerfen?")

    # ------------------------------------------------------------------
    # Aktionen
    # ------------------------------------------------------------------
    def _clear_selection(self):
        """Hebt die Tabellenauswahl auf und deaktiviert Bearbeiten/Löschen."""
        for iid in self.tree.selection():
            self.tree.selection_remove(iid)
        self.btn_edit.configure(state="disabled")
        self.btn_delete.configure(state="disabled")

    def _on_edit(self):
        """Bearbeiten: oeffnet das Eingabefenster mit dem selektierten Abend.

        Eine Verwerfen-Rueckfrage ist hier nicht mehr noetig: Solange ein
        Eingabefenster offen ist, haelt dessen grab_set() das Hauptfenster
        (und damit auch den Bearbeiten-Knopf und die Tabelle) ohnehin
        unerreichbar -- dieser Pfad kann also nur laufen, wenn kein anderes
        Formular bereits offen ist.
        """
        night = self._get_selected_night()
        if night is None:
            return
        datum = night.get("Datum", "")
        self._open_eingabe_fenster(("edit", datum))

    def _on_save(self):
        """Speichern: validieren, erzeugen, sichern, Fenster schliessen,
        Tabelle/Kacheln/Dashboard/Erkenntnisse auffrischen."""
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

        if edit_datum is None:
            self.quiz_nights.append(entry)
        else:
            self.quiz_nights = [
                entry if n.get("Datum") == edit_datum else n
                for n in self.quiz_nights
            ]

        save_data(self.quiz_nights)
        messagebox.showinfo("Gespeichert",
                            f"Abend {entry['Monat']} gespeichert.")

        self._destroy_eingabe_fenster()
        self._clear_selection()
        self._reload_tree()
        self._refresh_status()
        self._refresh_dashboard()
        self._refresh_insights()

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
        self._clear_selection()


# ---------------------------------------------------------------------------
# Einstiegspunkt
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = QuizEingabeApp()
    app.mainloop()
