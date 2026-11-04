"""Mix the intro's sound to picture: pen, three folds, twelve keys, stinger. Master near -14 LUFS.

    .venv/bin/python ton/mischen.py AUSGABE.wav
Times follow the frames in blender/szene.py (t = (frame - 1) / 24).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROH = Path("/mnt/steam-library/flexibilizar/arbeit/ton")
SR = 48000
DAUER = 132 / 24
LANDUNG = (2.021, 2.449, 2.878)  # fold landings, on the stinger's beat
AKKORD_QUELLE = 3.44  # where the stinger's resolving chord starts in its own file
TASTEN = [(72 + 2 * i - 1) / 24 for i in range(12)]


def lese(name: str) -> np.ndarray:
    roh = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(ROH / name), "-f", "f32le", "-ar", str(SR), "-ac", "2", "-"],
        capture_output=True, check=True,
    ).stdout
    return np.frombuffer(roh, "f4").reshape(-1, 2).astype(float)


def legen(ziel: np.ndarray, klang: np.ndarray, t: float, pegel: float = 1.0) -> None:
    i = round(t * SR)
    if i < 0:
        klang, i = klang[-i:], 0
    n = min(len(klang), len(ziel) - i)
    if n > 0:
        ziel[i : i + n] += klang[:n] * pegel


def norm(a: np.ndarray, spitze: float = 1.0) -> np.ndarray:
    return a / max(np.abs(a).max(), 1e-9) * spitze


def hoch(a: np.ndarray, fc: float) -> np.ndarray:
    """One-pole high-pass, enough to keep effects out of the music's low end."""
    k = np.exp(-2 * np.pi * fc / SR)
    aus = np.zeros_like(a)
    for c in range(a.shape[1]):
        x, y, vx = a[:, c], np.zeros(len(a)), 0.0
        last = 0.0
        for i, v in enumerate(x):
            last = k * (last + v - vx)
            vx = v
            y[i] = last
        aus[:, c] = y
    return aus


def huellkurve(n: int, an: float, ab: float) -> np.ndarray:
    k = np.ones(n)
    a, b = int(an * SR), int(ab * SR)
    if a:
        k[:a] = np.linspace(0, 1, a)
    if b:
        k[-b:] = np.linspace(1, 0, b) ** 2
    return k


def schlag(tief: float, ab: float = 0.22) -> np.ndarray:
    """A soft low thump under a fold, felt rather than heard. Synthesised, no third-party sample."""
    n = int(ab * 2.2 * SR)
    t = np.arange(n) / SR
    y = np.sin(2 * np.pi * (tief * t + 16 * (1 - np.exp(-t * 26)) / 26)) * np.exp(-t / (ab * 0.42))
    y[: 48] *= np.linspace(0, 1, 48)
    return np.c_[y, y]


def main(ziel: Path) -> None:
    mix = np.zeros((round(DAUER * SR), 2))

    # Stinger: chord lands with the third fold. Soft start, as the head of the intro is mid-phrase.
    musik = lese("stinger_b.wav")
    start = LANDUNG[2] - AKKORD_QUELLE
    musik = musik[round(-start * SR) :]
    musik = musik[: round((DAUER + 0.1) * SR)]
    musik = musik * huellkurve(len(musik), 0.05, 0.0)[:, None]
    legen(mix, norm(musik, 0.62), 0.0)

    # Pen scratching while the strip runs: fades as the strip slows, gone when the pen lifts.
    feder = lese("feder.wav")[: round(1.5 * SR)]
    feder = hoch(feder, 300) * huellkurve(round(1.5 * SR), 0.015, 0.55)[:, None]
    legen(mix, norm(feder, 0.34), 0.0)

    # Folds: the effect's transient on the landing, plus a thump that steps up in pitch.
    falz = lese("falz.wav")
    spitze = int(np.argmax(np.abs(falz).sum(axis=1)))
    falz = falz[max(0, spitze - int(0.03 * SR)) : spitze + int(0.3 * SR)]
    falz = falz * huellkurve(len(falz), 0.002, 0.08)[:, None]
    for i, t in enumerate(LANDUNG):
        legen(mix, norm(hoch(falz, 200), 0.8), t - 0.03)
        legen(mix, schlag(46 + i * 10), t, 0.42 + i * 0.08)

    # Keys: one clack, resampled a touch per letter so twelve strikes never sound identical.
    taste = lese("taste.wav")[: int(0.16 * SR)]
    taste = taste * huellkurve(len(taste), 0.0005, 0.05)[:, None]
    z = np.random.default_rng(4)
    for i, t in enumerate(TASTEN):
        rate = z.uniform(0.92, 1.1)
        idx = np.arange(0, len(taste) - 1, rate)
        k = np.c_[np.interp(idx, np.arange(len(taste)), taste[:, 0]), np.interp(idx, np.arange(len(taste)), taste[:, 1])]
        legen(mix, norm(k, 1.0), t, z.uniform(0.2, 0.28))

    # Soft end: everything gone before the black last frames.
    ende = np.ones(len(mix))
    a, b = round(4.75 * SR), round(5.40 * SR)
    ende[a:b] = np.linspace(1, 0, b - a) ** 2.2
    ende[b:] = 0
    mix *= ende[:, None]

    zwischen = ziel.with_suffix(".roh.wav")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "f64le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s24le", str(zwischen)],
        input=mix.astype("f8").tobytes(), check=True,
    )
    # Two-pass loudnorm to -14 LUFS, measured first so it stays linear on so short a clip.
    mess = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(zwischen), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    d = json.loads(mess[mess.rindex("{") : mess.rindex("}") + 1])
    filt = (
        f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={d['input_i']}:measured_TP={d['input_tp']}:"
        f"measured_LRA={d['input_lra']}:measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=true"
    )
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(zwischen), "-af", filt, "-ar", str(SR), "-c:a", "pcm_s24le", str(ziel)], check=True)
    zwischen.unlink()
    print("Eingang", d["input_i"], "LUFS, Spitze", d["input_tp"], "dBTP")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
