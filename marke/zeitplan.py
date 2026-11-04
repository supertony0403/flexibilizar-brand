"""The intro's timeline in one place: picture (blender/szene.py), sound (ton/mischen.py), edit (blender/zusammenbau.py)."""
FPS = 24
BILDER = 132
DAUER = BILDER / FPS

# Fold windows in frames. They overlap a little, so each fold lifts while the previous one lands.
# Landings sit on the stinger's beat, 0.4286 s apart.
FENSTER = ((36.0, 49.5), (46.5, 59.78), (56.5, 70.08))
SCHREIB_START, SCHREIB_JE, BUCHSTABEN = 72, 2, 12

# Fade to black in seconds. The sound is gone by the end of it, black frames follow.
AUS_START, AUS_ENDE = 4.75, 5.40


def sekunde(bild: float) -> float:
    """Frame 1 is the first picture, at t = 0."""
    return (bild - 1) / FPS


LANDUNG = tuple(sekunde(b) for _, b in FENSTER)
TASTEN = tuple(sekunde(SCHREIB_START + SCHREIB_JE * i) for i in range(BUCHSTABEN))
