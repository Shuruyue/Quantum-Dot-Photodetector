"""Size dependence of the PbS quantum-dot band gap.

Three descriptions of the same dot are compared:

* ``gap_ema``      – effective-mass approximation with parabolic bands (Brus 1984) [5]
* ``gap_hbm``      – two-band mirror-image hyperbolic bands (Wang et al. 1987) [18]
* ``gap_moreels``  – empirical sizing curve fitted to TEM size and first-exciton absorption [7]

All diameters ``d`` are in nm and all energies in eV.
"""
import math

import numpy as np
from scipy.optimize import brentq

from . import data as D
from .constants import E2_4PIE0, HB2_2M0, HC


def gap_moreels(d):
    """Measured sizing curve E0 = Eg + 1/(a d² + b d) of Moreels et al. (2009)."""
    d = np.asarray(d, float)
    return D.EG_PBS + 1.0 / (D.MOREELS_A * d**2 + D.MOREELS_B * d)


def diameter_for_gap(E):
    """Invert the Moreels curve: diameter (nm) whose first exciton sits at E (eV)."""
    if E <= D.EG_PBS:
        raise ValueError("E must exceed the bulk gap")
    return brentq(lambda d: float(gap_moreels(d)) - E, 0.3, 1e4, xtol=1e-12, rtol=1e-14)


def diameter_for_wavelength(lam_nm):
    return diameter_for_gap(HC / lam_nm)


def confinement_ema(d, me=D.M_STAR, mh=D.M_STAR):
    """Kinetic confinement energy ħ²π²/(2R²)·(1/me + 1/mh) for infinite walls."""
    R = np.asarray(d, float) / 2
    return HB2_2M0 * math.pi**2 / R**2 * (1 / me + 1 / mh)


def coulomb(d, eps=D.EPS_INF):
    """Electron–hole attraction 1.786 e²/(4π ε0 ε R)."""
    R = np.asarray(d, float) / 2
    return D.COULOMB_COEFF * E2_4PIE0 / (eps * R)


def gap_ema(d, me=D.M_STAR, mh=D.M_STAR, eps=D.EPS_INF):
    return D.EG_PBS + confinement_ema(d, me, mh) - coulomb(d, eps)


def gap_hbm_no_coulomb(d, m=D.M_STAR, Eg=D.EG_PBS):
    """Hyperbolic bands E_c,v(k) = ±[(Eg/2)² + Eg ħ²k²/(2m)]^½ at k = π/R.

    The gap is E_c − E_v = [Eg² + 4 Eg (ħ²/2m0) k² / m]^½.
    """
    R = np.asarray(d, float) / 2
    k2 = (math.pi / R) ** 2
    return np.sqrt(Eg**2 + 4 * Eg * HB2_2M0 * k2 / m)


def gap_hbm(d, m=D.M_STAR, eps=D.EPS_INF):
    return gap_hbm_no_coulomb(d, m) - coulomb(d, eps)


def overestimate(gap_model, d):
    """Confinement energy of a model relative to the measured one, (E − Eg)/(E_meas − Eg)."""
    return (gap_model - D.EG_PBS) / (float(gap_moreels(d)) - D.EG_PBS)


def cutoff_wavelength_nm(E):
    """Absorption edge λ = hc/E."""
    return HC / E
