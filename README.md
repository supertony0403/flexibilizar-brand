# Flexibilizar: Branding

Logo, Banner und Video-Intro für den YouTube-Kanal [Flexibilizar](https://www.youtube.com/@flexibilizar).
Die Medien liegen nicht hier, sondern unter `/mnt/steam-library/flexibilizar/`.

**Die Idee:** Ein einziger Registrierstreifen wird dreimal gefalzt und ergibt ein F. Elfenbein ist die bedruckte
Seite mit der Messkurve, Marker-Gelb die Rückseite, die erst der Falz zeigt. Die Kurve im Bild ist ein gesetztes
Zufallssignal und zeigt keine echten Daten.

**Farben:** nur warmes Fast-Schwarz, Elfenbein und Marker-Gelb. Rot ist gestrichen, weil Schwarz, Rot und Gelb
zusammen Deutschlandfarben ergeben. Kein Blau.

| Datei | Zweck |
| --- | --- |
| `marke/falz.py` | Faltgeometrie als reines numpy, Quelle für Logo, Banner und Intro |
| `marke/logo.py` | drei Logo-Richtungen als Vektor, Vergleichsbogen, Wortbildmarke |
| `marke/banner.py` | Schrift auf den Banner-Render setzen, Prüfausschnitte |
| `blender/szene.py` | Blender-Szene (Modi `intro`, `banner`, `avatar`) |
| `blender/texturen.py` | Papier, Raster, Spur, Marker-Rückseite |
| `blender/zusammenbau.py` | Bilder und Ton zu `intro.mp4` und `intro.mov` |
| `ton/erzeugen.py`, `ton/mischen.py` | Stinger und Geräusche von ElevenLabs, Mischung auf -14 LUFS |

## Bauen

```sh
uv sync
.venv/bin/python -m pytest
.venv/bin/python -m blender.texturen
.venv/bin/python -m marke.logo
BL="systemd-run --user --scope -p MemoryMax=8G <blender> -b --factory-startup --python blender/szene.py --"
$BL banner /mnt/steam-library/flexibilizar/arbeit/banner_roh.png --samples 96
.venv/bin/python -m marke.banner
python3 ton/erzeugen.py                 # Schlüssel aus ~/.config/elevenlabs.env, kostet Credits
.venv/bin/python ton/mischen.py /mnt/steam-library/flexibilizar/arbeit/ton/intro_ton.wav
$BL intro /mnt/steam-library/flexibilizar/arbeit/frames --samples 48
.venv/bin/python -m blender.zusammenbau
```

Schriften: Archivo und Courier Prime (OFL), aus `/mnt/steam-library/marek-doku/schriften/`.
