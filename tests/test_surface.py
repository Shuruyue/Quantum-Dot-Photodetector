import pytest

from quantum_dot_photodetector import surface as sf


@pytest.mark.parametrize("d", [1.5, 2.0, 3.056, 4.0])
@pytest.mark.parametrize("centring", ["atom", "interstitial"])
def test_two_counting_algorithms_agree(d, centring):
    assert sf.count_sites(d, centring) == sf.count_sites_naive(d, centring)


def test_single_atom_and_first_shell():
    # a sphere just larger than one Pb–S distance around an atom holds the atom and its 6 neighbours
    N, s = sf.count_sites(2 * sf.H * 1.01, "atom")
    assert (N, s) == (7, 6)


def test_fraction_bounds_and_trend():
    f = [sf.surface_fraction(d) for d in (2.0, 4.0, 8.0, 16.0)]
    assert all(0 < x <= 1 for x in f)
    assert f == sorted(f, reverse=True)


def test_shell_fraction_limits():
    assert sf.shell_fraction(2 * sf.H) == pytest.approx(1.0)
    assert sf.shell_fraction(1e5) == pytest.approx(6 * sf.H / 1e5, rel=1e-3)


def test_values_on_slide_4():
    assert round(100 * sf.surface_fraction(3.0559)) == 43
    assert round(100 * sf.surface_fraction(5.1071)) == 27
