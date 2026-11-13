"""Detector figures of merit."""
import math

from .constants import HC, Q


def responsivity(eta, lam_nm):
    """R = η q λ / (h c) in A/W; with λ in nm and hc in eV nm this is η λ / 1239.84."""
    return eta * lam_nm / HC


def dstar_shot_limit(R, J_dark):
    """Specific detectivity limited by dark-current shot noise, D* = R / (2 q Jd)^½ (Jones).

    R in A/W, Jd in A cm⁻².
    """
    return R / math.sqrt(2 * Q * J_dark)


def dark_current_density(e_per_s, pitch_um):
    """Dark current density (A cm⁻²) from a per-pixel electron rate and the pixel pitch."""
    area_cm2 = (pitch_um * 1e-4) ** 2
    return e_per_s * Q / area_cm2


def pixel_area_ratio(pitch_big_um, pitch_small_um):
    return (pitch_big_um / pitch_small_um) ** 2
