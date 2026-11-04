"""Banner: type printed onto the rendered band, then the check crops for phone, desktop and TV.

    .venv/bin/python -m marke.banner
The Blender render (mode "banner") is shot straight down, so band pixels are known exactly.
"""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from marke.grund import AUSGABE, pil_archivo, pil_courier

ORDNER = AUSGABE / "banner"
ROH = AUSGABE / "arbeit" / "banner_roh.png"
W, H = 2560, 1440
SICHER = (507, 508, 2053, 931)  # YouTube's 1546 x 423 zone, centred
BAND_OBEN = 530
TEXT_X = 548
NAME_OBEN = 572
CLAIM_NORMAL, CLAIM_MARKIERT = "Dokumentationen. ", "Mit Daten."
TINTE = np.array((30, 26, 22), float) / 255
MARKER = np.array((247, 214, 62), float) / 255


def drucken(bild: np.ndarray, maske: Image.Image, farbe: np.ndarray, deckung: float = 1.0) -> np.ndarray:
    """Multiply a colour into the picture through a mask, so paper and grid stay visible, like ink."""
    a = np.asarray(maske, float)[..., None] / 255 * deckung
    return bild * (1 - a) + bild * farbe * a


def ink_rauschen(maske: Image.Image, saat: int) -> Image.Image:
    """Print is never solid: faint mottling inside the letters, softened edge of a hair."""
    z = np.random.default_rng(saat)
    n = z.normal(0, 1, (H // 2, W // 2))
    grob = Image.fromarray(((n + 4) * 32).clip(0, 255).astype("uint8")).resize((W, H), Image.BICUBIC)
    a = np.asarray(maske.filter(ImageFilter.GaussianBlur(0.5)), float)
    return Image.fromarray((a * (0.965 + (np.asarray(grob, float) / 32 - 4) * 0.012)).clip(0, 255).astype("uint8"))


def setzen() -> Image.Image:
    bild = np.asarray(Image.open(ROH).convert("RGB"), float) / 255

    schrift = pil_archivo(186, 900, 100)
    name = Image.new("L", (W, H), 0)
    z = ImageDraw.Draw(name)
    links, oben, rechts, unten = z.textbbox((0, 0), "FLEXIBILIZAR", font=schrift)
    z.text((TEXT_X - links, NAME_OBEN - oben), "FLEXIBILIZAR", font=schrift, fill=255)
    print("Name:", TEXT_X, "bis", TEXT_X + rechts - links, "Sicher bis", SICHER[2], "Unterkante", NAME_OBEN + unten - oben)
    bild = drucken(bild, ink_rauschen(name, 2), TINTE)

    # The claim is typed, and its second half is run over with the same marker as the reverse side.
    claim = pil_courier(58)
    grund = NAME_OBEN + unten - oben + 28
    breite_a = claim.getlength(CLAIM_NORMAL)
    breite_b = claim.getlength(CLAIM_MARKIERT)
    x_b = TEXT_X + 2 + breite_a
    band = Image.new("L", (W, H), 0)
    ImageDraw.Draw(band).polygon(
        [(x_b - 12, grund + 6), (x_b + breite_b + 16, grund + 2), (x_b + breite_b + 10, grund + 62), (x_b - 8, grund + 66)],
        fill=255,
    )
    # Opaque enough to match the marker on the fold: a pure multiply turns mustard on warm paper.
    a = np.asarray(band.filter(ImageFilter.GaussianBlur(0.8)), float)[..., None] / 255 * 0.82
    bild = bild * (1 - a) + MARKER * bild.mean(axis=2, keepdims=True) ** 0.25 * a
    tipp = Image.new("L", (W, H), 0)
    ImageDraw.Draw(tipp).text((TEXT_X + 2, grund), CLAIM_NORMAL + CLAIM_MARKIERT, font=claim, fill=255)
    bild = drucken(bild, ink_rauschen(tipp, 3), TINTE)
    print("Claim bis", x_b + breite_b, "Zeile", grund, grund + 66)

    return Image.fromarray((bild * 255 + 0.5).clip(0, 255).astype("uint8"))


def pruefung(bild: Image.Image) -> None:
    """All three crops at the real proportions, with the safe zone marked on the TV view."""
    ausschnitte = (
        ("TV 2560x1440", (0, 0, W, H), 1280),
        ("DESKTOP 2560x423", (0, 508, W, 931), 1280),
        ("TABLET 1855x423", (352, 508, 2207, 931), 1280),
        ("HANDY 1546x423", (507, 508, 2053, 931), 780),
    )
    schrift = pil_courier(26)
    hoehe = 30
    for _, b, br in ausschnitte:
        hoehe += 44 + round((b[3] - b[1]) * br / (b[2] - b[0])) + 20
    bogen = Image.new("RGB", (1340, hoehe), (60, 56, 52))
    z = ImageDraw.Draw(bogen)
    y = 20
    for titel, b, br in ausschnitte:
        z.text((30, y), titel, font=schrift, fill=(238, 230, 214))
        y += 40
        k = bild.crop(b).resize((br, round((b[3] - b[1]) * br / (b[2] - b[0]))), Image.LANCZOS)
        bogen.paste(k, (30, y))
        if titel.startswith("TV"):
            s = br / W
            z.rectangle((30 + SICHER[0] * s, y + SICHER[1] * s, 30 + SICHER[2] * s, y + SICHER[3] * s), outline=(120, 220, 120))
        y += k.height + 20
    bogen.save(ORDNER / "pruefung.png", optimize=True)


def main() -> None:
    ORDNER.mkdir(parents=True, exist_ok=True)
    bild = setzen()
    ziel = ORDNER / "banner.png"
    bild.save(ziel, optimize=True, compress_level=9)
    mb = ziel.stat().st_size / 1e6
    print(f"{ziel}: {bild.size}, {mb:.1f} MB")
    assert mb <= 6, "YouTube refuses banners above 6 MB"
    pruefung(bild)


if __name__ == "__main__":
    main()
