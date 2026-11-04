"""Frames + mix -> intro.mp4, intro.mov and the contact sheet. Checks length and the black end.

    .venv/bin/python -m blender.zusammenbau
"""
from __future__ import annotations

import re
import subprocess

from marke.grund import AUSGABE
from marke.kontakt import kontaktbogen

ARBEIT = AUSGABE / "arbeit"
ZIEL = AUSGABE / "intro"
TON = ARBEIT / "ton" / "intro_ton.wav"
FPS = 24
BILDER = 132
# Grain goes in before the fades, otherwise the black end would carry noise.
FILTER = (
    "vignette=PI/5.5,noise=alls=5:allf=t,"
    "fade=t=in:st=0:d=0.125,fade=t=out:st=4.75:d=0.65,"
    "scale=out_color_matrix=bt709:out_range=tv,format={fmt}"
)
FARBE = ["-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv"]


def ffmpeg(*args: str) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def bauen() -> None:
    frames = ["-framerate", str(FPS), "-start_number", "1", "-i", str(ARBEIT / "frames" / "f%04d.png")]
    ffmpeg(
        *frames, "-i", str(TON), "-vf", FILTER.format(fmt="yuv420p"), "-c:v", "libx264", "-crf", "16",
        "-preset", "slow", "-profile:v", "high", *FARBE, "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
        "-movflags", "+faststart", "-shortest", str(ZIEL / "intro.mp4"),
    )
    # For the edit: Resolve on Linux reads ProRes and PCM, but not H.264 with AAC.
    ffmpeg(
        *frames, "-i", str(TON), "-vf", FILTER.format(fmt="yuv422p10le"), "-c:v", "prores_ks", "-profile:v", "1",
        *FARBE, "-c:a", "pcm_s24le", "-ar", "48000", "-shortest", str(ZIEL / "intro.mov"),
    )


def pruefen() -> None:
    aus = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,width,height,r_frame_rate,sample_rate,nb_frames:format=duration",
         "-of", "default=nw=1", str(ZIEL / "intro.mp4")],
        capture_output=True, text=True, check=True,
    ).stdout
    print(aus)
    dauer = float(re.search(r"duration=([\d.]+)", aus).group(1))
    assert 4.0 <= dauer <= 6.0, f"intro must last 4 to 6 s, is {dauer}"
    stats = subprocess.run(
        ["ffmpeg", "-hide_banner", "-sseof", "-0.25", "-i", str(ZIEL / "intro.mp4"), "-vf", "signalstats,metadata=print:key=lavfi.signalstats.YMAX",
         "-an", "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    werte = [int(float(w)) for w in re.findall(r"YMAX=([\d.]+)", stats)]
    print("YMAX der letzten Bilder:", werte)
    assert werte and werte[-1] <= 17, "last frame is not black"


def bogen() -> None:
    wahl = list(range(3, BILDER + 1, 5))
    kontaktbogen([ARBEIT / "frames" / f"f{i:04d}.png" for i in wahl], ZIEL / "kontaktbogen.png", spalten=6, breite=400)


def main() -> None:
    ZIEL.mkdir(parents=True, exist_ok=True)
    bauen()
    pruefen()
    bogen()


if __name__ == "__main__":
    main()
