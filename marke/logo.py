"""Three logo directions as real vector files, plus the round-crop comparison sheet.

    .venv/bin/python -m marke.logo
"""
from __future__ import annotations

import subprocess

import numpy as np
from PIL import Image, ImageDraw

from marke.falz import Masse, lagen
from marke.grund import (
    AUSGABE, ELFENBEIN, ELFENBEIN_SCHATTEN, MARKER, MARKER_SCHATTEN, TINTE,
    archivo, courier, pil_courier, text_pfad,
)

ORDNER = AUSGABE / "logo"
G = 800


def poly(p, farbe: str, zus: str = "") -> str:
    pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in p)
    return f'<polygon points="{pts}" fill="{farbe}"{zus}/>'


def svg(inhalt: str, titel: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {G} {G}" width="{G}" height="{G}">'
        f"<title>{titel}</title>{inhalt}</svg>\n"
    )


def falz_f(einheit: float, ox: float, oy: float, vorn: str = ELFENBEIN, hinten: str = MARKER,
           vorn_sch: str = ELFENBEIN_SCHATTEN, hinten_sch: str = MARKER_SCHATTEN, schatten: bool = True) -> str:
    """The folded F. Layers come straight from the fold geometry, bottom layer first."""
    m = Masse()
    h, ym = m.hoehe, m.y_mitte

    def t(pts):
        a = np.asarray(pts, float)
        return np.c_[ox + a[:, 0] * einheit, oy + (h - a[:, 1]) * einheit]

    aus, farben = [], {"vorn": vorn, "hinten": hinten}
    sch = {
        # Wedges, not bands: a shadow starts at nothing on the crease and opens away from it.
        "stiel": (t([(1, h), (1, h - 1), (1.2, h - 1)]), vorn_sch),
        "arm_mitte": (t([(0, ym), (0, ym + 0.3), (1, ym + 1)]), hinten_sch),
    }
    for lage in lagen(m):
        if schatten and lage["name"] in sch:
            aus.append(poly(*sch[lage["name"]]))
        aus.append(poly(t(lage["poly"]), farben[lage["seite"]]))
    if schatten:
        aus.append(poly(t([(0, ym), (1, ym), (1, ym - 0.2)]), vorn_sch))
    return "".join(aus)


def richtung_a() -> str:
    """A: one strip, three folds, an F. Ivory is the printed side, marker the reverse."""
    m = Masse()
    einheit = 134
    ox = (G - m.breite * einheit) / 2 + 4
    oy = (G - m.hoehe * einheit) / 2
    return svg(f'<rect width="{G}" height="{G}" fill="{TINTE}"/>' + falz_f(einheit, ox, oy), "Flexibilizar A: Falz-F")


def richtung_b() -> str:
    """B: a sheet with one corner folded over: the fold shows what is underneath. A trace runs into it."""
    c = 1160.0  # crease is the line x + y = c
    k0, k1 = (800.0, c - 800), (c - 800, 800.0)
    spitze = (c - 800, c - 800)  # the corner (800, 800) mirrored across the crease
    linie = "M 0 300 L 170 300 L 250 470 L 330 250 L 410 330 L 470 330"
    inhalt = (
        f'<rect width="{G}" height="{G}" fill="{ELFENBEIN}"/>'
        + f'<path d="{linie}" fill="none" stroke="{TINTE}" stroke-width="44" stroke-linejoin="miter" stroke-miterlimit="10"/>'
        + poly([(k0[0], k0[1] - 30), k1, (spitze[0] - 30, spitze[1] - 16)], ELFENBEIN_SCHATTEN)
        + poly([k0, (G, G), k1], TINTE)
        + poly([k0, k1, spitze], MARKER)
    )
    return svg(inhalt, "Flexibilizar B: Eselsohr mit Datenspur")


def richtung_c() -> str:
    """C: the typed capital, run over with a highlighter. The stroke's ends are cut by the chisel tip."""
    d, _ = text_pfad(courier(True), "F", 150, 640, 760)
    band = [(52, 402), (748, 346), (734, 474), (760, 512), (66, 566), (46, 500)]
    inhalt = (
        f'<rect width="{G}" height="{G}" fill="{ELFENBEIN}"/>'
        + poly(band, MARKER)
        + f'<path d="{d}" fill="{TINTE}"/>'
    )
    return svg(inhalt, "Flexibilizar C: Getipptes F mit Marker")


def lockup() -> str:
    """Recommended mark with the name set under the middle arm, baseline on the stem's foot (as in the intro)."""
    m = Masse()
    einheit = 100.0
    rand = 60.0
    d, w = text_pfad(archivo(900, 100), "FLEXIBILIZAR", 0, 0, 100, -0.012)
    # Cap height of 0.69 strip widths, the same relation as the intro's lockup.
    groesse = 0.69 * einheit / 0.686
    s = groesse / 100
    x = rand + 1.32 * einheit
    y = rand + m.hoehe * einheit
    b = x + w * s + rand
    h = 2 * rand + m.hoehe * einheit
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {b:.1f} {h:.1f}" width="{b:.0f}" height="{h:.0f}">'
        f"<title>Flexibilizar Wortbildmarke</title>"
        f'<rect width="{b:.1f}" height="{h:.1f}" fill="{TINTE}"/>'
        + falz_f(einheit, rand, rand)
        + f'<path transform="translate({x:.2f} {y:.2f}) scale({s:.4f})" d="{d}" fill="{ELFENBEIN}"/></svg>\n'
    )


def rendern(name: str, inhalt: str) -> Image.Image:
    pfad = ORDNER / f"richtung_{name}.svg"
    pfad.write_text(inhalt)
    png = pfad.with_suffix(".png")
    subprocess.run(["rsvg-convert", "-w", str(G), "-h", str(G), str(pfad), "-o", str(png)], check=True)
    return Image.open(png).convert("RGB")


def rund(bild: Image.Image, d: int, grund: tuple[int, int, int]) -> Image.Image:
    """YouTube's round crop at the size it is shown, supersampled like a browser would."""
    k = bild.resize((d, d), Image.LANCZOS)
    maske = Image.new("L", (d * 4, d * 4), 0)
    ImageDraw.Draw(maske).ellipse((0, 0, d * 4 - 1, d * 4 - 1), fill=255)
    aus = Image.new("RGB", (d, d), grund)
    aus.paste(k, (0, 0), maske.resize((d, d), Image.LANCZOS))
    return aus


def vergleich(bilder: dict[str, Image.Image], titel: dict[str, str]) -> None:
    sp, zei = 620, 760
    bogen = Image.new("RGB", (sp * len(bilder) + 40, zei + 40), (42, 38, 34))
    z = ImageDraw.Draw(bogen)
    for i, (name, bild) in enumerate(bilder.items()):
        x = 40 + i * sp
        z.text((x, 28), f"{name.upper()}  {titel[name]}", font=pil_courier(26), fill=(238, 230, 214))
        bogen.paste(rund(bild, 520, (42, 38, 34)), (x, 80))
        y = 630
        for d, grund in ((98, (15, 15, 15)), (98, (255, 255, 255)), (48, (15, 15, 15)), (48, (255, 255, 255))):
            kasten = Image.new("RGB", (d + 28, d + 28), grund)
            kasten.paste(rund(bild, d, grund), (14, 14))
            bogen.paste(kasten, (x, y))
            x += d + 44
    bogen.save(ORDNER / "vergleich.png", optimize=True)


def main() -> None:
    ORDNER.mkdir(parents=True, exist_ok=True)
    bilder = {
        "a": rendern("a", richtung_a()),
        "b": rendern("b", richtung_b()),
        "c": rendern("c", richtung_c()),
    }
    vergleich(bilder, {"a": "Falz-F (Empfehlung)", "b": "Eselsohr", "c": "Getipptes F"})
    pfad = ORDNER / "wortbildmarke_a.svg"
    pfad.write_text(lockup())
    subprocess.run(["rsvg-convert", "-w", "1800", str(pfad), "-o", str(pfad.with_suffix(".png"))], check=True)


if __name__ == "__main__":
    main()
