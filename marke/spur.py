"""The decorative recorder trace. Pure numpy, shared with Blender's Python."""
import numpy as np


def spur(n: int, saat: int = 7) -> np.ndarray:
    """Recorder trace in -1..1: slow drift, fine tremor, a few hard kinks. Seeded, so reproducible."""
    z = np.random.default_rng(saat)
    x = np.linspace(0, 1, n)
    y = 0.28 * np.sin(x * 19 + 0.7) + 0.16 * np.sin(x * 47 + 2.1) + 0.05 * np.sin(x * 211)
    zittern = np.convolve(z.normal(0, 1, n), np.ones(n // 300 + 1) / (n // 300 + 1), "same")
    y += zittern * 0.34
    for ort, hub, breite in ((0.17, 0.55, 0.012), (0.42, -0.62, 0.016), (0.63, 0.7, 0.01), (0.86, -0.5, 0.014)):
        d = np.abs(x - ort) / breite
        y += hub * np.clip(1 - d, 0, 1)
    return np.clip(y, -1, 1)
