"""Contact sheet from a folder of frames: .venv/bin/python -m marke.kontakt ORDNER ZIEL [--spalten N] [--breite B]"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from marke.grund import pil_courier


def kontaktbogen(bilder: list[Path], ziel: Path, spalten: int = 6, breite: int = 320, fps: int = 24) -> None:
    probe = Image.open(bilder[0])
    h = round(breite * probe.height / probe.width)
    zeilen = -(-len(bilder) // spalten)
    bogen = Image.new("RGB", (spalten * (breite + 6) + 6, zeilen * (h + 6) + 6), (60, 56, 52))
    schrift = pil_courier(18)
    for i, p in enumerate(bilder):
        k = Image.open(p).convert("RGB").resize((breite, h), Image.LANCZOS)
        ImageDraw.Draw(k).text((6, 4), f"{p.stem} {int(p.stem[1:]) / fps:.2f}s", font=schrift, fill=(238, 230, 214))
        bogen.paste(k, (6 + (i % spalten) * (breite + 6), 6 + (i // spalten) * (h + 6)))
    bogen.save(ziel, optimize=True)


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("ordner", type=Path)
    a.add_argument("ziel", type=Path)
    a.add_argument("--spalten", type=int, default=6)
    a.add_argument("--breite", type=int, default=320)
    a.add_argument("--jedes", type=int, default=1)
    x = a.parse_args()
    kontaktbogen(sorted(x.ordner.glob("f*.png"))[:: x.jedes], x.ziel, x.spalten, x.breite)
