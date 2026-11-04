import numpy as np
import pytest

from marke.falz import BANNER, Masse, falten, falze, gitter, lagen, laenge_gesamt, streifen_ecken

M = Masse()


def bbox(poly):
    return poly[:, 0].min(), poly[:, 1].min(), poly[:, 0].max(), poly[:, 1].max()


def teil(name):
    return next(l for l in lagen(M) if l["name"] == name)


def test_oberer_arm_bleibt_liegen():
    x0, y0, x1, y1 = bbox(teil("arm_oben")["poly"])
    assert (y0, y1) == pytest.approx((M.hoehe - 1, M.hoehe))
    assert x1 == pytest.approx(1 + M.arm_oben)


def test_stiel_steht_senkrecht_bis_zum_fuss():
    x0, y0, x1, y1 = bbox(teil("stiel")["poly"])
    assert (x0, x1) == pytest.approx((0, 1))
    assert y0 == pytest.approx(0, abs=1e-9)
    assert y1 == pytest.approx(M.hoehe)


def test_lasche_laeuft_vom_fuss_zur_mitte():
    x0, y0, x1, y1 = bbox(teil("lasche")["poly"])
    assert (x0, x1) == pytest.approx((0, 1))
    assert y0 == pytest.approx(0, abs=1e-9)
    assert y1 == pytest.approx(M.y_mitte + 1)


def test_mittlerer_arm_zeigt_nach_rechts():
    x0, y0, x1, y1 = bbox(teil("arm_mitte")["poly"])
    assert (y0, y1) == pytest.approx((M.y_mitte, M.y_mitte + 1))
    assert x0 == pytest.approx(0, abs=1e-9)
    assert x1 == pytest.approx(1 + M.arm_mitte)


def test_kopf_ist_um_45_grad_gefalzt():
    """The outer corner of a strip folded at 45 degrees is cut away, that is the F's mark."""
    p = teil("stiel")["poly"]
    assert not np.any(np.all(np.isclose(p, (0, M.hoehe)), axis=1)), "top-left corner must be open"
    assert np.any(np.all(np.isclose(p, (1, M.hoehe)), axis=1))
    assert np.any(np.all(np.isclose(p, (0, M.hoehe - 1)), axis=1))


def _flaeche(p):
    x, y = p[:, 0], p[:, 1]
    return 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)


def test_seiten_stimmen_mit_der_geometrie_ueberein():
    """A panel showing its reverse is mirrored, so folding must flip its orientation in the plane."""
    punkte = {
        "arm_oben": (2.0, 2.5, 3.0),
        "stiel": (-1.0, -1.5, -2.0),
        "lasche": (falze(M)[1].punkt[0] - 0.2, falze(M)[1].punkt[0] - 0.4, falze(M)[1].punkt[0] - 0.6),
        "arm_mitte": (falze(M)[2].punkt[0] - 1.2, falze(M)[2].punkt[0] - 1.4, falze(M)[2].punkt[0] - 1.6),
    }
    for lage in lagen(M):
        xs = punkte[lage["name"]]
        y = M.hoehe - 1
        flach = np.array([(xs[0], y + 0.4), (xs[1], y + 0.4), (xs[2], y + 0.8)])
        zu = falten(flach, M, (np.pi, np.pi, np.pi))[:, :2]
        gespiegelt = np.sign(_flaeche(flach)) != np.sign(_flaeche(zu))
        assert gespiegelt == (lage["seite"] == "hinten"), lage["name"]


def test_flacher_streifen_wird_nicht_bewegt():
    e = streifen_ecken(M)
    assert falten(e, M, (0, 0, 0))[:, :2] == pytest.approx(e)


@pytest.mark.parametrize("winkel", [(2.0, 1.0, 0.7), (np.pi, np.pi, np.pi), (0.4, 2.9, 1.5)])
def test_falten_dehnt_das_papier_nicht(winkel):
    """Rigid folds keep the distance from any point to its crease, across every fold in the chain."""
    h = M.hoehe
    f1, f2, f3 = falze(M)
    weg = np.array([[f3.punkt[0] - 2.0, h - 0.5]])
    # Length of the path paper -> crease 3 -> crease 2 -> crease 1, measured flat and folded.
    knoten = [f1.punkt + f1.richtung * 0.5 * np.sqrt(2), f2.punkt + f2.richtung * -0.5, f3.punkt + f3.richtung * 0.5 * np.sqrt(2)]
    kette = np.vstack([weg, knoten[2], knoten[1], knoten[0]])
    flach = np.linalg.norm(np.diff(np.c_[kette, np.zeros(4)], axis=0), axis=1)
    zu = np.linalg.norm(np.diff(falten(kette, M, winkel, lage=0.0), axis=0), axis=1)
    assert zu == pytest.approx(flach, abs=1e-9)


def test_kleiner_radius_landet_auf_dem_scharfen_falz():
    """The render presses folds to a tiny radius, outside the band it must match the sharp fold."""
    x, v = gitter(M, 40)
    y = M.hoehe - 1 + v
    p = np.c_[x.ravel(), y.ravel()]
    scharf = falten(p, M, (np.pi, np.pi, np.pi))
    rund = falten(p, M, (np.pi, np.pi, np.pi), radius=0.012)
    abstand = np.min([np.abs((p - f.punkt) @ f.normale) for f in falze(M)], axis=0)
    assert rund[abstand > 0.012][:, :2] == pytest.approx(scharf[abstand > 0.012][:, :2])


def test_zeitplan_landet_im_takt_und_vor_dem_ausblenden():
    from marke.zeitplan import AUS_START, DAUER, LANDUNG, TASTEN

    assert np.diff(LANDUNG) == pytest.approx([0.4286, 0.4286], abs=0.01)
    assert LANDUNG[-1] < TASTEN[0] < TASTEN[-1] < AUS_START < DAUER
    assert 4 <= DAUER <= 6


def test_lagen_liegen_uebereinander_nicht_ineinander():
    """Closed, each later fold sits higher, or stacked paper would z-fight in the render."""
    h, f = M.hoehe, falze(M)
    punkte = np.array(
        [
            (0.5 + 1, h - 0.5),  # top arm
            (f[0].punkt[0] - 2.0, h - 0.5),  # stem
            (f[1].punkt[0] - 0.5, h - 0.5),  # flap
            (f[2].punkt[0] - 1.5, h - 0.5),  # middle arm
        ]
    )
    z = falten(punkte, M, (np.pi, np.pi, np.pi))[:, 2]
    assert np.all(np.diff(z) > 0)


@pytest.mark.parametrize("m", [M, BANNER])
def test_gitter_hat_eine_spalte_genau_auf_jedem_falz(m):
    """Otherwise the outer edge of the fold turns into a staircase."""
    x, v = gitter(m, 40)
    y = m.hoehe - 1 + v
    for falz in falze(m):
        abstand = np.abs((np.dstack((x, y)) - falz.punkt) @ falz.normale).max(axis=1)
        assert abstand.min() == pytest.approx(0, abs=1e-9)


@pytest.mark.parametrize("m", [M, BANNER])
def test_gitter_spalten_ueberschneiden_sich_nicht(m):
    x, _ = gitter(m, 58)
    assert np.all(np.diff(x, axis=0) > 0)


@pytest.mark.parametrize("m", [M, BANNER])
def test_gitter_enden_bleiben_gerade(m):
    x, _ = gitter(m, 40)
    assert np.ptp(x[0]) == pytest.approx(0)
    assert np.ptp(x[-1]) == pytest.approx(0)
