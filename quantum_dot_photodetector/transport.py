"""Tunnelling between dots: mobility μ ∝ exp(−β d) with β = 2κ, κ = (2 m* φ)^½ / ħ.

Lengths in Å, energies in eV, masses in units of m0.
"""
import math

from . import data as D
from .constants import HB2_2M0_A


def beta_from_factor(factor_per_A=D.MOBILITY_FACTOR_PER_A):
    """A rate that changes by `factor` per Å has β = ln(factor)."""
    return math.log(factor_per_A)


def kappa_from_barrier(phi, m=1.0):
    return math.sqrt(phi * m / HB2_2M0_A)


def beta_from_barrier(phi, m=1.0):
    return 2 * kappa_from_barrier(phi, m)


def barrier_from_beta(beta, m=1.0):
    return HB2_2M0_A * (beta / 2) ** 2 / m


def mass_from_beta_and_barrier(beta, phi):
    """Effective mass that makes a fitted (β, φ) pair self-consistent."""
    return HB2_2M0_A * (beta / 2) ** 2 / phi


def relative_rate(beta, extra_gap_A):
    return math.exp(-beta * extra_gap_A)
