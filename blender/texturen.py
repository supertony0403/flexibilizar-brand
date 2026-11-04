"""Paper textures for the fold strip and the banner strip: chart-recorder paper and marker reverse.

    .venv/bin/python -m blender.texturen
Decorative only: the trace is a seeded random signal, it shows no real data.
"""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw

from marke.grund import AUSGABE, pil_archivo, pil_courier
from marke.spur import spur

ARBEIT = AUSGABE / "arbeit"
PAPIER = np.array((236, 227, 208), float)
RASTER = (176, 150, 112)


def faser(h: int, b: int, saat: int, staerke: float) -> np.ndarray:
    """Paper fibre: white noise smeared along the sheet, added to flat tone."""
    z = np.random.default_rng(saat)
    grob = z.normal(0, 1, (h // 4 + 1, b // 12 + 1))
    bild = Image.fromarray(((grob + 4) * 32).clip(0, 255).astype("uint8")).resize((b, h), Image.BICUBIC)
    fein = z.normal(0, 1, (h, b))
    return (np.asarray(bild, float) / 32 - 4) * staerke + fein * staerke * 0.8


def papier_grund(b: int, h: int, saat: int = 3) -> Image.Image:
    a = PAPIER[None, None] + faser(h, b, saat, 2.6)[..., None]
    return Image.fromarray(a.clip(0, 255).astype("uint8"))


def raster(bild: Image.Image, je_einheit: int, rand_oben: float = 0.08, zahlen: bool = True, start: int = 0) -> None:
    """Printed chart grid: fine 0.1 lines, bold 0.5 lines, a scale along one margin."""
    z = ImageDraw.Draw(bild)
    b, h = bild.size
    schritt = je_einheit / 10
    for i in range(int(b / schritt) + 1):
        x = round(i * schritt)
        z.line((x, 0, x, h), fill=RASTER + (), width=3 if i % 5 == 0 else 1)
    for i in range(11):
        y = round(i * (h - 1) / 10)
        z.line((0, y, b, y), fill=RASTER, width=3 if i % 5 == 0 else 1)
    if zahlen:
        f = pil_courier(int(je_einheit * 0.075))
        for i in range(0, int(b / je_einheit) + 1):
            z.text((i * je_einheit + 6, h * rand_oben * 0.25), f"{start + i * 10:03d}", font=f, fill=(120, 96, 64))


def tinte_spur(b: int, h: int, je_einheit: int, staerke: float = 0.024) -> Image.Image:
    """The trace alone (RGBA) so the shader can reveal it under the moving pen."""
    y = spur(b)
    ebene = Image.new("L", (b, h), 0)
    z = ImageDraw.Draw(ebene)
    pts = list(zip(range(b), (h * 0.5 - y * h * 0.36).tolist()))
    z.line(pts, fill=255, width=max(2, round(je_einheit * staerke)), joint="curve")
    return ebene


def banner_vorn(laenge: float, je: int = 700) -> Image.Image:
    """Front of the banner strip: chart grid and one trace low on the band, room for the name above."""
    b, h = round(laenge * je), je
    bild = papier_grund(b, h, saat=9)
    raster(bild, je, start=100)
    y = spur(b, saat=23)
    z = ImageDraw.Draw(bild)
    z.line(list(zip(range(b), (h * 0.845 - y * h * 0.115).tolist())), fill=(30, 26, 22), width=round(je * 0.0085), joint="curve")
    return bild


def marker_rueckseite(b: int, h: int) -> Image.Image:
    """Reverse side: highlighter ink, faint streaks along the stroke, never one flat tone."""
    z = np.random.default_rng(11)
    streifen = np.convolve(z.normal(0, 1, h), np.ones(9) / 9, "same")
    a = np.array((247, 214, 62), float)[None, None] * (1 + streifen[:, None, None] * 0.03)
    a = a + faser(h, b, 5, 1.6)[..., None] * np.array((1.0, 1.0, 0.6))
    return Image.fromarray(a.clip(0, 255).astype("uint8"))


def wortmarke_bild(b: int, h: int, text: str = "FLEXIBILIZAR") -> tuple[Image.Image, list[float]]:
    """Name on transparency, plus each letter's right edge as a fraction of the width."""
    f = pil_archivo(int(h * 0.98), 900, 100)
    bild = Image.new("L", (b, h), 0)
    z = ImageDraw.Draw(bild)
    links, oben, rechts, unten = z.textbbox((0, 0), text, font=f)
    skala = 1.0
    if rechts - links > b:
        skala = b / (rechts - links)
        f = pil_archivo(int(h * 0.98 * skala), 900, 100)
        links, oben, rechts, unten = z.textbbox((0, 0), text, font=f)
    z.text((-links, h - unten), text, font=f, fill=255)
    kanten = [z.textlength(text[: i + 1], font=f) / b for i in range(len(text))]
    return bild, kanten


def main() -> None:
    ARBEIT.mkdir(parents=True, exist_ok=True)
    from marke.falz import BANNER, Masse, laenge_gesamt

    je = 400
    b, h = round(laenge_gesamt(Masse()) * je), je
    grund = papier_grund(b, h)
    raster(grund, je)
    grund.save(ARBEIT / "streifen_vorn.png")
    tinte_spur(b, h, je).save(ARBEIT / "streifen_spur.png")
    marker_rueckseite(b // 2, h // 2).save(ARBEIT / "streifen_hinten.png")

    banner_vorn(laenge_gesamt(BANNER)).save(ARBEIT / "banner_vorn.png")

    wort, kanten = wortmarke_bild(3000, 400)
    wort.save(ARBEIT / "wortmarke.png")
    (ARBEIT / "wortmarke_kanten.txt").write_text("\n".join(f"{k:.5f}" for k in kanten))
    print("Wortmarke-Bbox", wort.getbbox())


if __name__ == "__main__":
    main()
