"""Fold geometry of the logo: one paper strip, three folds, one F.

Everything is derived from a single strip of width 1 in material coordinates (u along the
strip, v across it, 0 <= v <= 1). The strip starts at the free end of the top arm and is laid
out towards -x, so the top arm stays where it is while the rest folds onto it:

    top arm  -> fold 1 (45 deg) -> stem down -> fold 2 (180 deg, across) -> flap up
             -> fold 3 (45 deg) -> middle arm

Pure numpy, no Blender: the SVG logo and the Blender intro read the same numbers, so the mark
in the film is the mark on the avatar, and tests can check the fold without rendering.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Masse:
    """Proportions in strip widths."""

    arm_oben: float = 2.15  # visible top arm, measured right of the stem
    arm_mitte: float = 1.45  # visible middle arm, measured right of the stem
    luecke: float = 0.8  # gap between top arm and middle arm
    stiel_unten: float = 1.75  # stem below the middle arm

    @property
    def hoehe(self) -> float:
        return 1 + self.luecke + 1 + self.stiel_unten

    @property
    def y_mitte(self) -> float:
        """Lower edge of the middle arm."""
        return self.stiel_unten

    @property
    def breite(self) -> float:
        return 1 + max(self.arm_oben, self.arm_mitte)


# The banner is a giant crop of the same F: its top arm runs off the frame on the right.
BANNER = Masse(arm_oben=7.0, arm_mitte=3.2, luecke=0.8, stiel_unten=3.0)


@dataclass(frozen=True)
class Falz:
    """A crease in the plane of the unfolded strip: points p with dot(p - punkt, normale) > 0 move."""

    punkt: np.ndarray
    richtung: np.ndarray  # unit vector along the crease
    normale: np.ndarray  # unit vector pointing to the side that moves


def falz_aus(punkt, richtung, normale) -> Falz:
    r = np.asarray(richtung, float)
    n = np.asarray(normale, float)
    return Falz(np.asarray(punkt, float), r / np.linalg.norm(r), n / np.linalg.norm(n))


def laenge_gesamt(m: Masse) -> float:
    """Strip length needed for the F: arm, corner, stem, flap, corner, arm."""
    return m.arm_oben + 1 + (m.hoehe - 1) + (m.y_mitte + 1) + m.arm_mitte


def falze(m: Masse) -> tuple[Falz, Falz, Falz]:
    """The three creases in the flat layout (x to the right, y up; the F's lower left is 0,0).

    Flat, the strip lies at y in [H-1, H] and runs from x = 1 + arm_oben to the left. Each crease
    is given in that flat frame, in the order they sit along the strip.
    """
    h = m.hoehe
    # Fold 1: lower-left to upper-right corner of the stem head: everything further left turns down.
    f1 = falz_aus((0.0, h - 1), (1, 1), (-1, 1))
    # Past f1 the strip continues to x = -(h-1) in flat coordinates: this is y = 0 after folding.
    x2 = -(h - 1)
    # Along -y: fold 1 has already turned the sheet over, so "up towards the viewer" is -z here.
    f2 = falz_aus((x2, h - 1), (0, -1), (-1, 0))
    # After fold 2 the flap runs back up. Flat, y_mitte above the stem foot sits y_mitte further left.
    x3 = x2 - m.y_mitte
    # 45-degree crease that turns the flap to the right once folds 1 and 2 are closed.
    f3 = falz_aus((x3, h - 1), (-1, 1), (-1, -1))
    return f1, f2, f3


def _rotiere(p: np.ndarray, falz: Falz, winkel: np.ndarray, hoehe: float) -> np.ndarray:
    """Rotate points (N, 3) about the crease axis lifted by `hoehe`, per-point angle."""
    a = np.array([falz.punkt[0], falz.punkt[1], hoehe])
    k = np.array([falz.richtung[0], falz.richtung[1], 0.0])
    r = p - a
    c = np.cos(winkel)[:, None]
    s = np.sin(winkel)[:, None]
    return a + r * c + np.cross(k, r) * s + k * (r @ k)[:, None] * (1 - c)


def falten_kette(
    punkte: np.ndarray,
    kette: tuple[Falz, ...],
    winkel: tuple[float, ...],
    radius: float | tuple[float, ...] = 0.0,
    lage: float = 0.004,
) -> np.ndarray:
    """Fold flat points (N, 2 or 3) along a chain of creases, angles in radians (pi = closed).

    `radius` rounds a crease: the angle ramps up over a band of that width, so paper bends
    instead of breaking at a hinge. Inside that band the sheet is only approximately isometric
    (it compresses while bending), so close to landing the radius must shrink to almost nothing.
    `lage` is the layer thickness, keeping stacked layers apart.
    Creases are applied from the far end inward: a later crease only moves points beyond it, and
    those creases still lie in the flat plane at that moment, so the composition is exact.
    """
    p = np.array(punkte, float)
    if p.shape[1] == 2:
        p = np.c_[p, np.zeros(len(p))]
    flach = p[:, :2].copy()
    radien = (radius,) * len(kette) if np.isscalar(radius) else radius
    for i, (falz, a, r) in reversed(list(enumerate(zip(kette, winkel, radien)))):
        if a == 0:
            continue
        d = (flach - falz.punkt) @ falz.normale
        anteil = (d > 0).astype(float) if r <= 0 else np.clip(d / r, 0, 1)
        # Axis heights alternate because every closed fold mirrors z: this stacks the closed
        # layers at 0, 1, 2, 3 times `lage` from the first panel upward.
        p = _rotiere(p, falz, a * anteil, lage * 0.5 * (1 if i % 2 == 0 else -1))
    return p


def falten(punkte, m: Masse, winkel, radius=0.0, lage: float = 0.004) -> np.ndarray:
    """Fold points along the three creases of the F."""
    return falten_kette(punkte, falze(m), winkel, radius, lage)


def falz_mitten(m: Masse) -> list[tuple[float, float]]:
    """For each crease, x at the strip's centre line and dx/dv (the crease's slant across the strip)."""
    aus = []
    h = m.hoehe
    for falz in falze(m):
        # Crease line at y = h - 0.5, the strip's centre line.
        t = (h - 0.5 - falz.punkt[1]) / falz.richtung[1]
        aus.append((float(falz.punkt[0] + t * falz.richtung[0]), float(falz.richtung[0] / falz.richtung[1])))
    return aus


def gitter(m: Masse, dichte: int) -> tuple[np.ndarray, np.ndarray]:
    """Flat grid whose columns are sheared to lie exactly on the 45-degree creases.

    Returns (X, V), shape (columns, rows): x in the flat layout and v in 0..1. A grid that crosses a
    crease diagonally folds into a staircase along the crease, the paper's outer edge there.
    """
    laenge = laenge_gesamt(m)
    rechts = 1 + m.arm_oben
    links = rechts - laenge
    mitten = falz_mitten(m)
    # Columns on a regular step, nudged so that one falls exactly on each crease's centre.
    spalten = np.linspace(links, rechts, int(laenge * dichte) + 1)
    for c, _ in mitten:
        spalten[np.argmin(np.abs(spalten - c))] = c
    schub = np.zeros_like(spalten)
    for c, steigung in mitten:
        schub += steigung * np.clip(1 - np.abs(spalten - c), 0, 1)
    v = np.linspace(0, 1, dichte + 1)
    return spalten[:, None] + schub[:, None] * (v[None, :] - 0.5), np.broadcast_to(v, (len(spalten), len(v))).copy()


def streifen_ecken(m: Masse) -> np.ndarray:
    """Corners of the unfolded strip in the flat frame."""
    rechts, links = 1 + m.arm_oben, 1 + m.arm_oben - laenge_gesamt(m)
    h = m.hoehe
    return np.array([(rechts, h - 1), (rechts, h), (links, h), (links, h - 1)], float)


def _clip(poly: list, punkt: np.ndarray, normale: np.ndarray, aussen: bool) -> list:
    """Sutherland-Hodgman against a half plane."""
    aus = []
    for i, a in enumerate(poly):
        b = poly[(i + 1) % len(poly)]
        da = (a - punkt) @ normale
        db = (b - punkt) @ normale
        ina = da >= 0 if aussen else da <= 0
        inb = db >= 0 if aussen else db <= 0
        if ina:
            aus.append(a)
        if ina != inb:
            aus.append(a + (b - a) * (da / (da - db)))
    return aus


def lagen(m: Masse) -> list[dict]:
    """The strip cut at its creases and folded closed, bottom layer first.

    Returns dicts with `name`, `seite` ('vorn' is the printed side facing up flat, 'hinten' the
    reverse) and `poly` (2D polygon of the visible outline of this layer in final F coordinates).
    """
    f1, f2, f3 = falze(m)
    poly = [np.array(e) for e in streifen_ecken(m)]
    teile = []
    rest = poly
    for name, falz in (("arm_oben", f1), ("stiel", f2), ("lasche", f3)):
        teile.append((name, _clip(rest, falz.punkt, falz.normale, aussen=False)))
        rest = _clip(rest, falz.punkt, falz.normale, aussen=True)
    teile.append(("arm_mitte", rest))
    seiten = {"arm_oben": "vorn", "stiel": "hinten", "lasche": "vorn", "arm_mitte": "hinten"}
    aus = []
    for name, teil in teile:
        q = falten(np.array(teil), m, (np.pi, np.pi, np.pi))[:, :2]
        aus.append({"name": name, "seite": seiten[name], "poly": q})
    return aus
