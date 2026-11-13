import math

import numpy as np
import pytest

from quantum_dot_photodetector import data as D
from quantum_dot_photodetector import quantum_size as qs
from quantum_dot_photodetector.constants import HC


@pytest.mark.parametrize("lam", [940.0, 1400.0, 1550.0])
def test_moreels_inversion_round_trip(lam):
    d = qs.diameter_for_wavelength(lam)
    assert float(qs.gap_moreels(d)) == pytest.approx(HC / lam, abs=1e-10)


def test_inversion_rejects_energy_below_bulk():
    with pytest.raises(ValueError):
        qs.diameter_for_gap(0.40)


def test_ema_confinement_scales_as_inverse_square():
    assert float(qs.confinement_ema(3.0) / qs.confinement_ema(6.0)) == pytest.approx(4.0, rel=1e-12)


def test_coulomb_scales_as_inverse_radius():
    assert float(qs.coulomb(3.0) / qs.coulomb(6.0)) == pytest.approx(2.0, rel=1e-12)


def test_hbm_reduces_to_bulk_gap_without_confinement():
    assert float(qs.gap_hbm_no_coulomb(1e6)) == pytest.approx(D.EG_PBS, abs=1e-9)


def test_models_are_ordered_and_decreasing():
    d = np.linspace(2.5, 10, 200)
    assert np.all(qs.gap_moreels(d) < qs.gap_hbm(d))
    assert np.all(qs.gap_hbm(d) <= qs.gap_ema(d))
    for f in (qs.gap_ema, qs.gap_hbm, qs.gap_moreels):
        assert np.all(np.diff(f(d)) < 0)


def test_cutoff_wavelength():
    assert qs.cutoff_wavelength_nm(1.0) == pytest.approx(1239.842)
    assert math.isclose(qs.cutoff_wavelength_nm(D.EG_PBS) / 1000, 3.024, rel_tol=1e-3)
