"""Ideal-diode dark current (Sze & Ng [22]).

* diffusion (n = 1):              J ∝ n_i² ∝ T³ exp(−Eg/kT)
* generation–recombination (n = 2): J ∝ n_i  ∝ T^1.5 exp(−Eg/2kT)

Energies in eV, temperatures in K. Eg is held constant with temperature.
"""
import math

from .constants import KB

_PREFACTOR_POWER = {1: 3.0, 2: 1.5}


def ideal_ratio(Eg_small, Eg_big, T=300.0, n=1):
    """J(Eg_small)/J(Eg_big) for otherwise identical diodes."""
    return math.exp((Eg_big - Eg_small) / (n * KB * T))


def scale_with_temperature(J0, T0, T, Eg, n=1):
    """Project a dark current measured at T0 to temperature T."""
    p = _PREFACTOR_POWER[n]
    return J0 * (T / T0) ** p * math.exp(-Eg / (n * KB) * (1 / T - 1 / T0))


def halving_interval(Eg, T=300.0, n=1):
    """Temperature step (K) that halves (or doubles) J near T: ln2 / (d ln J / dT)."""
    p = _PREFACTOR_POWER[n]
    dlnJ_dT = p / T + Eg / (n * KB * T**2)
    return math.log(2) / dlnJ_dT


def cooling_factor(Eg, T_hot, T_cold, n=1, with_prefactor=True):
    """J(T_hot)/J(T_cold)."""
    if with_prefactor:
        return 1.0 / scale_with_temperature(1.0, T_hot, T_cold, Eg, n)
    return math.exp(Eg / (n * KB) * (1 / T_cold - 1 / T_hot))
