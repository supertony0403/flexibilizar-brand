"""Frames + mix -> intro.mp4, intro.mov and the contact sheet. Checks length and the black end.

    .venv/bin/python -m blender.zusammenbau
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from marke.grund import AUSGABE
from marke.kontakt import kontaktbogen
from marke.zeitplan import AUS_ENDE, AUS_START, BILDER, DAUER, FPS

ARBEIT = AUSGABE / "arbeit"
ZIEL = AUSGABE / "intro"
TON = ARBEIT / "ton" / "intro_ton.wav"
# Grain goes in before the fades, otherwise the black end would carry noise.
FILTER = (
    "vignette=PI/5.5,noise=alls=5:allf=t,"
    f"fade=t=in:st=0:d=0.125,fade=t=out:st={AUS_START}:d={AUS_ENDE - AUS_START:.3f},"
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
        "-movflags", "+faststart", str(ZIEL / "intro.mp4"),
    )
    # For the edit: Resolve on Linux reads ProRes and PCM, but not H.264 with AAC.
    ffmpeg(
        *frames, "-i", str(TON), "-vf", FILTER.format(fmt="yuv422p10le"), "-c:v", "prores_ks", "-profile:v", "1",
        *FARBE, "-c:a", "pcm_s24le", "-ar", "48000", str(ZIEL / "intro.mov"),
    )


def bilder_pruefen() -> None:
    """Every frame present, complete and at full size. A skipped re-render must not slip through."""
    from PIL import Image

    for i in range(1, BILDER + 1):
        with Image.open(ARBEIT / "frames" / f"f{i:04d}.png") as b:
            if b.size != (1920, 1080):
                raise RuntimeError(f"frame {i} is {b.size}: rendered as a preview? Render again with --neu")
            b.verify()


def pruefen(datei: Path) -> None:
    aus = subprocess.run(
        ["ffprobe", "-v", "error", "-count_frames", "-show_entries",
         "stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,nb_read_frames:format=duration",
         "-of", "json", str(datei)],
        capture_output=True, text=True, check=True,
    ).stdout
    d = json.loads(aus)
    video = next(s for s in d["streams"] if s["codec_type"] == "video")
    audio = [s for s in d["streams"] if s["codec_type"] == "audio"]
    print(datei.name, video, audio, d["format"]["duration"])
    if int(video["nb_read_frames"]) != BILDER or (video["width"], video["height"]) != (1920, 1080):
        raise RuntimeError(f"{datei.name}: wrong picture: {video}")
    if video["r_frame_rate"] != f"{FPS}/1":
        raise RuntimeError(f"{datei.name}: wrong frame rate: {video['r_frame_rate']}")
    if not audio or audio[0]["sample_rate"] != "48000":
        raise RuntimeError(f"{datei.name}: wrong sound: {audio}")
    if abs(float(d["format"]["duration"]) - DAUER) > 0.06:
        raise RuntimeError(f"{datei.name}: lasts {d['format']['duration']}, should be {DAUER}")
    stats = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(datei), "-vf", "signalstats,metadata=print:key=lavfi.signalstats.YMAX:file=-", "-an", "-f", "null", "-"],
        capture_output=True, text=True,
    ).stdout
    werte = [float(w) for w in re.findall(r"YMAX=([\d.]+)", stats)]
    # 8-bit black is 16, in the mov's 10-bit it is 64.
    schwarz = 17 if "422" not in video.get("pix_fmt", "") and datei.suffix == ".mp4" else 68
    print("YMAX der letzten Bilder:", werte[-4:])
    if not werte or werte[-1] > schwarz:
        raise RuntimeError(f"{datei.name}: last frame is not black")


def bogen() -> None:
    wahl = list(range(3, BILDER + 1, 5))
    kontaktbogen([ARBEIT / "frames" / f"f{i:04d}.png" for i in wahl], ZIEL / "kontaktbogen.png", spalten=6, breite=400)


def main() -> None:
    ZIEL.mkdir(parents=True, exist_ok=True)
    bilder_pruefen()
    bauen()
    pruefen(ZIEL / "intro.mp4")
    pruefen(ZIEL / "intro.mov")
    bogen()


if __name__ == "__main__":
    main()
