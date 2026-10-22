"""Erzeugt logo.png (256x256) und icon.ico — weisses Fragezeichen auf E1-Gruen.

Analog zum Schwesterprojekt 260609_IES-Dateien (_logo_erzeugen.py): ein PIL-
Generator, der einmalig vor dem Build mit System-Python laufen soll:

    py -3.13 _logo_erzeugen.py

Resultat: logo.png (Header-Logo, via tk.PhotoImage geladen -- kein PIL zur
Laufzeit noetig) UND icon.ico (Fenster-/Taskleisten-/EXE-Icon). Beide tragen
dasselbe Motiv: ein Kneipenquiz-Fragezeichen im E1-Look.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

GROESSE = 256
CORPORATE_GREEN = (102, 179, 47, 255)      # #66b32f
GRUEN_DUNKEL = (58, 109, 27, 255)          # #3a6d1b
WEISS = (255, 255, 255, 255)
RASTER = (255, 255, 255, 55)               # zarte Ringe im Hintergrund
SCHATTEN = (30, 60, 15, 90)                # weicher Schlagschatten unter dem ?

# Schrift-Kandidaten fuer ein fettes, freundliches Fragezeichen.
FONT_KANDIDATEN = [
    "C:/Windows/Fonts/ariblk.ttf",     # Arial Black
    "C:/Windows/Fonts/arialbd.ttf",    # Arial Bold
    "C:/Windows/Fonts/segoeuib.ttf",   # Segoe UI Bold
]


def _lade_font(groesse: int) -> ImageFont.FreeTypeFont:
    """Laedt den ersten verfuegbaren fetten TrueType-Font in der Wunschgroesse."""
    for pfad in FONT_KANDIDATEN:
        if Path(pfad).exists():
            return ImageFont.truetype(pfad, groesse)
    # Notnagel: Default-Bitmap-Font (nicht skalierbar, aber immer da)
    return ImageFont.load_default()


def _zeichne_motiv(img: Image.Image) -> None:
    """Zeichnet das Fragezeichen-Motiv auf ein quadratisches RGBA-Bild."""
    size = img.width
    d = ImageDraw.Draw(img, "RGBA")
    cx = size // 2

    # --- Hintergrund-Ringe (konzentrisch, Mittelpunkt oben mittig) ---
    ring_cx, ring_cy = cx, int(size * 0.30)
    for r_frac in (0.34, 0.60, 0.86, 1.12):
        r = int(size * 0.42 * r_frac)
        d.arc(
            [ring_cx - r, ring_cy - r, ring_cx + r, ring_cy + r],
            start=0, end=180, fill=RASTER, width=max(2, size // 90),
        )

    # --- weisser Badge-Ring nahe der Kante ---
    rand = int(size * 0.055)
    d.ellipse(
        [rand, rand, size - rand, size - rand],
        outline=(255, 255, 255, 90), width=max(2, size // 64),
    )

    # --- Fragezeichen ---
    font = _lade_font(int(size * 0.72))
    zeichen = "?"
    bbox = d.textbbox((0, 0), zeichen, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = cx - tw / 2 - bbox[0]
    ty = size / 2 - th / 2 - bbox[1]

    # weicher Schlagschatten, leicht versetzt
    versatz = max(2, size // 64)
    d.text((tx + versatz, ty + versatz), zeichen, font=font, fill=SCHATTEN)
    # Fragezeichen selbst
    d.text((tx, ty), zeichen, font=font, fill=WEISS)


def _basis_bild(size: int) -> Image.Image:
    """Erzeugt ein Motiv-Bild der gewuenschten Kantenlaenge."""
    img = Image.new("RGBA", (size, size), CORPORATE_GREEN)
    _zeichne_motiv(img)
    return img


def main() -> None:
    ordner = Path(__file__).resolve().parent

    # 256er-Master fuer das Header-Logo
    master = _basis_bild(GROESSE)
    png_ziel = ordner / "logo.png"
    master.save(png_ziel, format="PNG")
    print(f"[OK] {png_ziel.name} geschrieben ({png_ziel.stat().st_size} Bytes)")

    # icon.ico mit mehreren Groessen -- PIL skaliert den 256er-Master herunter.
    ico_groessen = [(16, 16), (24, 24), (32, 32), (48, 48),
                    (64, 64), (128, 128), (256, 256)]
    ico_ziel = ordner / "icon.ico"
    master.save(ico_ziel, format="ICO", sizes=ico_groessen)
    print(f"[OK] {ico_ziel.name} geschrieben ({ico_ziel.stat().st_size} Bytes)")


if __name__ == "__main__":
    main()
