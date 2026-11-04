"""Fetch the stinger and the sound effects from ElevenLabs once. Existing files are never paid for twice.

    python3 ton/erzeugen.py          (key from ~/.config/elevenlabs.env, never printed)
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from pathlib import Path

ZIEL = Path("/mnt/steam-library/flexibilizar/arbeit/ton")
API = "https://api.elevenlabs.io/v1"

MUSIK = {
    "stinger_a": (
        "Short documentary channel ident, 7 seconds. Dry, close and serious, no vocals. A nervous muted "
        "pizzicato and felt-piano ostinato for 2 seconds, three rising low soft impacts, then one warm "
        "resolved low piano and cello chord that rings out and decays to silence. Understated, no epic trailer "
        "brass, no synth risers, neutral in mood, neither happy nor threatening."
    ),
    "stinger_b": (
        "Very short elegant documentary logo sting, 7 seconds, instrumental. Upright bass pulse and prepared "
        "piano ticking like a machine, tightening for 3 seconds, landing on a single open warm chord of felt "
        "piano and bowed vibraphone with a long soft decay into silence. Intimate, dry, modern, neutral."
    ),
}
EFFEKTE = {
    "feder": ("Fast chart recorder pen scratching on a running paper strip with quiet paper feed motor, dry close microphone, no music", 2.0),
    "falz": ("One single crisp fold of thick paper being creased flat with a soft snap, close microphone, dry room, no reverb", 1.0),
    "taste": ("Single vintage mechanical typewriter key strike, one short clack, dry close microphone", 0.6),
    "tippen": ("Vintage mechanical typewriter typing twelve quick evenly spaced keystrokes then stop, dry close microphone", 2.0),
}


def schluessel() -> str:
    text = (Path.home() / ".config/elevenlabs.env").read_text()
    return re.search(r"ELEVEN\w*KEY\w*\s*=\s*[\"']?([^\s\"']+)", text).group(1)


def post(pfad: str, daten: dict, ziel: Path) -> None:
    if ziel.exists():
        print("vorhanden:", ziel.name)
        return
    anfrage = urllib.request.Request(
        API + pfad,
        data=json.dumps(daten).encode(),
        headers={"xi-api-key": schluessel(), "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(anfrage, timeout=240) as a:
            ziel.write_bytes(a.read())
        print("geladen:", ziel.name, ziel.stat().st_size // 1024, "KB")
    except urllib.error.HTTPError as e:
        # The status line only: an error body could echo request details.
        print("FEHLER", ziel.name, e.code)


def guthaben() -> None:
    anfrage = urllib.request.Request(API + "/user/subscription", headers={"xi-api-key": schluessel()})
    try:
        with urllib.request.urlopen(anfrage, timeout=30) as a:
            d = json.load(a)
        print("Credits:", d.get("character_count"), "/", d.get("character_limit"))
    except urllib.error.HTTPError as e:
        print("Guthaben nicht lesbar:", e.code)


def main() -> None:
    ZIEL.mkdir(parents=True, exist_ok=True)
    guthaben()
    for name, prompt in MUSIK.items():
        post(
            "/music?output_format=mp3_48000_320",
            {"prompt": prompt, "music_length_ms": 7000, "model_id": "music_v2_5", "force_instrumental": True},
            ZIEL / f"{name}.mp3",
        )
    for name, (text, dauer) in EFFEKTE.items():
        post(
            "/sound-generation?output_format=mp3_44100_192",
            {"text": text, "duration_seconds": dauer, "prompt_influence": 0.6},
            ZIEL / f"{name}.mp3",
        )
    guthaben()


if __name__ == "__main__":
    main()
