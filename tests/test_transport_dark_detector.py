import math

import pytest

from quantum_dot_photodetector import dark_current as dc
from quantum_dot_photodetector import detector as det
from quantum_dot_photodetector import transport as tr


def test_beta_barrier_round_trip():
    for m in (0.1, 0.43, 1.0):
        assert tr.beta_from_barrier(tr.barrier_from_beta(0.9555, m), m) == pytest.approx(0.9555, rel=1e-12)


def test_beta_from_factor():
    assert math.exp(tr.beta_from_factor(2.6)) == pytest.approx(2.6)


def test_generation_ratio_is_square_root_of_diffusion_ratio():
    r1 = dc.ideal_ratio(0.8856, 1.319, 300, 1)
    r2 = dc.ideal_ratio(0.8856, 1.319, 300, 2)
    assert r2 == pytest.approx(math.sqrt(r1), rel=1e-12)


@pytest.mark.parametrize("n", [1, 2])
def test_halving_interval_matches_numerical_derivative(n):
    h = 1e-4
    num = (math.log(dc.scale_with_temperature(1, 300, 300 + h, 0.8856, n))
           - math.log(dc.scale_with_temperature(1, 300, 300 - h, 0.8856, n))) / (2 * h)
    assert math.log(2) / num == pytest.approx(dc.halving_interval(0.8856, 300, n), rel=1e-6)


def test_cooling_factor_prefactor_increases_suppression():
    assert dc.cooling_factor(0.8856, 300, 273, 1, True) > dc.cooling_factor(0.8856, 300, 273, 1, False)


def test_responsivity_unit_quantum_efficiency():
    # η = 1 at 1239.842 nm gives exactly 1 A/W
    assert det.responsivity(1.0, 1239.842) == pytest.approx(1.0)


def test_dark_current_density_hand_calculation():
    assert det.dark_current_density(64.6, 5.0) == pytest.approx(64.6 * 1.602176634e-19 / 2.5e-7, rel=1e-12)


def test_pixel_area_ratio():
    assert det.pixel_area_ratio(15, 1.62) == pytest.approx(85.73, abs=0.01)
