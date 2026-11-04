"""Shared brand constants and vector glyph helpers."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from PIL import ImageFont

AUSGABE = Path("/mnt/steam-library/flexibilizar")
SCHRIFTEN = Path("/mnt/steam-library/marek-doku/schriften")

TINTE = "#1e1a16"  # warm near-black, the film's ink
ELFENBEIN = "#eee6d6"
ELFENBEIN_SCHATTEN = "#c9bfaa"
MARKER = "#f7d63e"
MARKER_SCHATTEN = "#c9a91e"
TISCH = "#17140f"


@lru_cache
def _archivo_instanz(gewicht: int, breite: int) -> TTFont:
    return instancer.instantiateVariableFont(
        TTFont(SCHRIFTEN / "Archivo[wdth,wght].ttf"), {"wght": gewicht, "wdth": breite}
    )


@lru_cache
def _courier(fett: bool) -> TTFont:
    return TTFont(SCHRIFTEN / ("CourierPrime-Bold.ttf" if fett else "CourierPrime-Regular.ttf"))


def text_pfad(font: TTFont, text: str, x: float, y: float, groesse: float, sperrung: float = 0.0):
    """SVG path data for `text` with baseline at (x, y), real outlines, y pointing down.

    Returns (path data, advance width). Kerning comes from nothing but advances: all-caps names
    in Archivo Black-ish weights set tight with a small negative `sperrung` instead.
    """
    einheiten = font["head"].unitsPerEm
    s = groesse / einheiten
    glyphen, cmap, hmtx = font.getGlyphSet(), font.getBestCmap(), font["hmtx"]
    pen = SVGPathPen(glyphen, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
    cx = x
    for z in text:
        name = cmap[ord(z)]
        glyphen[name].draw(TransformPen(pen, (s, 0, 0, -s, cx, y)))
        cx += hmtx[name][0] * s + sperrung * groesse
    return pen.getCommands(), cx - x


def archivo(gewicht: int = 900, breite: int = 100) -> TTFont:
    return _archivo_instanz(gewicht, breite)


def courier(fett: bool = True) -> TTFont:
    return _courier(fett)


def pil_archivo(groesse: int, gewicht: int = 900, breite: int = 100) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(str(SCHRIFTEN / "Archivo[wdth,wght].ttf"), groesse)
    f.set_variation_by_axes([gewicht, breite])
    return f


def pil_courier(groesse: int, fett: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(SCHRIFTEN / ("CourierPrime-Bold.ttf" if fett else "CourierPrime-Regular.ttf")), groesse)
