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


def test_seiten_wechseln_mit_jedem_falz():
    assert [l["seite"] for l in lagen(M)] == ["vorn", "hinten", "vorn", "hinten"]


def test_flacher_streifen_wird_nicht_bewegt():
    e = streifen_ecken(M)
    assert falten(e, M, (0, 0, 0))[:, :2] == pytest.approx(e)


def test_papierlaenge_bleibt_beim_falten_erhalten():
    """A rigid fold cannot stretch paper: distances inside one panel stay exact."""
    links = 1 + M.arm_oben - laenge_gesamt(M)
    a, b = np.array([[links, M.hoehe - 1]]), np.array([[links + 0.5, M.hoehe - 1]])
    pa, pb = falten(a, M, (2.0, 1.0, 0.7)), falten(b, M, (2.0, 1.0, 0.7))
    assert np.linalg.norm(pa - pb) == pytest.approx(0.5)


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
