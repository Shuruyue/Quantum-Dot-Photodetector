"""Automated checks of the models and of every number shown in the presentation.

``run_all()`` returns one row per check. Checks are of four kinds:
constants against CODATA, hand calculations repeated in SI units with ``scipy.constants``,
limits and identities the models must satisfy, and the registry in ``slides.py``.
"""
import math
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np
import scipy.constants as sc
from scipy.optimize import brentq

from . import constants as C
from . import dark_current as dc
from . import data as D
from . import detector as det
from . import quantum_size as qs
from . import slides
from . import surface as sf
from . import transport as tr
from .summary import compute


@dataclass
class Check:
    category: str
    name: str
    passed: bool
    model: Optional[float] = None
    expected: Optional[float] = None
    tol: Optional[float] = None
    how: str = ""
    num: int = field(default=0)
    rel: bool = False


def _close(cat, name, model, expected, tol, how, rel=False):
    err = abs(model - expected)
    lim = tol * abs(expected) if rel else tol
    return Check(cat, name, err <= lim * (1 + 1e-12), float(model), float(expected), tol, how, rel=rel)


def _flag(cat, name, cond, how, model=None, expected=None):
    return Check(cat, name, bool(cond), None if model is None else float(model),
                 None if expected is None else float(expected), None, how)


# ---------------------------------------------------------------- constants
def _constants():
    cat = "Constants"
    return [
        _close(cat, "ħ²/2m0 (eV nm²)", C.HB2_2M0, sc.hbar**2 / (2 * sc.m_e) / sc.e * 1e18, 1e-6,
               "compared with scipy.constants (CODATA 2018), relative error", rel=True),
        _close(cat, "e²/4πε0 (eV nm)", C.E2_4PIE0, sc.e / (4 * math.pi * sc.epsilon_0) * 1e9, 1e-6,
               "as above", rel=True),
        _close(cat, "hc (eV nm)", C.HC, sc.h * sc.c / sc.e * 1e9, 1e-6, "as above", rel=True),
        _close(cat, "k_B (eV/K)", C.KB, sc.k / sc.e, 1e-6, "as above", rel=True),
    ]


# ---------------------------------------------------------------- quantum size
def _quantum_size(r):
    cat = "Quantum size"
    out = []
    for lam in D.ST_WAVELENGTHS_NM:
        d = qs.diameter_for_wavelength(lam)
        out.append(_close(cat, f"Moreels inversion: E(d({lam:.0f} nm)) = hc/λ (eV)", float(qs.gap_moreels(d)), C.HC / lam,
                          1e-9, "the diameter put back into the Moreels curve returns the starting energy"))
    d = r["d1400"]
    R_m = d / 2 * 1e-9
    conf_si = (sc.hbar**2 * math.pi**2 / (2 * R_m**2)) * (2 / (D.M_STAR * sc.m_e)) / sc.e
    out.append(_close(cat, "EMA confinement at d(1400 nm), recomputed in SI (eV)", r["conf_ema"], conf_si, 1e-6,
                      "ħ²π²/(2R²)·(1/me*+1/mh*) with SI constants, bypassing the package constants", rel=True))
    coul_si = D.COULOMB_COEFF * sc.e / (4 * math.pi * sc.epsilon_0 * D.EPS_INF * R_m)
    out.append(_close(cat, "Coulomb term at d(1400 nm), recomputed in SI (eV)", r["coulomb"], coul_si, 1e-6,
                      "1.786e²/(4πε0εR) with SI constants", rel=True))
    k = math.pi / (d / 2)
    Ec = math.sqrt((D.EG_PBS / 2) ** 2 + D.EG_PBS * C.HB2_2M0 * k**2 / D.M_STAR)
    out.append(_close(cat, "HBM gap = 2 × conduction-band energy (mirror bands)", float(qs.gap_hbm_no_coulomb(d)), 2 * Ec, 1e-12,
                      "term by term from E_c(k) = [(Eg/2)² + Eg ħ²k²/2m*]^½"))
    for D_big in (40.0, 100.0, 400.0):
        x = float(qs.confinement_ema(D_big))
        ratio = (float(qs.gap_hbm_no_coulomb(D_big)) - D.EG_PBS) / x
        u = x / D.EG_PBS
        series = 1 - u / 2 + u**2 / 2
        out.append(_close(cat, f"small-k limit: HBM/EMA confinement ratio at d = {D_big:.0f} nm", ratio - 1, series - 1, 0.01,
                          "series √(1+2u) = 1 + u − u²/2 + u³/2 − …, u = EMA confinement / Eg; relative error", rel=True))
    ds = np.linspace(2.5, 10, 301)
    out.append(_flag(cat, "2.5–10 nm: HBM ≤ EMA", np.all(qs.gap_hbm(ds) <= qs.gap_ema(ds) + 1e-12),
                     "the hyperbolic dispersion always lies below the parabola"))
    out.append(_flag(cat, "2.5–10 nm: Moreels < HBM", np.all(qs.gap_moreels(ds) < qs.gap_hbm(ds)),
                     "the measured curve lies below both infinite-wall models"))
    out.append(_flag(cat, "2.5–10 nm: all three curves fall monotonically with d",
                     all(np.all(np.diff(f(ds)) < 0) for f in (qs.gap_ema, qs.gap_hbm, qs.gap_moreels)),
                     "larger dot, smaller gap"))
    for name, f in (("EMA", qs.gap_ema), ("HBM", qs.gap_hbm), ("Moreels", qs.gap_moreels)):
        out.append(_close(cat, f"{name} returns to the bulk 0.41 eV at d = 1000 nm", float(f(1000.0)), D.EG_PBS, 1e-3,
                          "large-dot limit"))
    out.append(_close(cat, "EMA overestimate factor (definition)", r["over_ema"],
                      (r["E_ema"] - D.EG_PBS) / (r["E_moreels"] - D.EG_PBS), 1e-12,
                      "(E_EMA − Eg)/(E_meas − Eg)"))
    return out


# ---------------------------------------------------------------- surface atoms
def _surface(r):
    cat = "Surface atoms"
    out = []
    for d in (2.0, r["d940"], r["d1400"]):
        for c in sf.CENTRINGS:
            a, b = sf.count_sites(d, c), sf.count_sites_naive(d, c)
            out.append(_flag(cat, f"two counting algorithms agree at d = {d:.3f} nm ({c})", a == b,
                             f"vectorised grid vs explicit set loop: (N, surface) = {a} vs {b}"))
    d = 20.0
    N = sf.count_sites(d, "atom")[0]
    out.append(_close(cat, "atom density: N / (πd³/6 ÷ h³) at d = 20 nm", N / ((math.pi * d**3 / 6) / sf.H**3), 1.0, 0.01,
                      "rock salt has 8 atoms per a³, one per h³; for a large dot the count approaches the continuum volume"))
    t = sf.H
    out.append(_close(cat, "shell model at d(940 nm): by hand", r["shell_940"], 1 - ((r["d940"] - 2 * t) / r["d940"]) ** 3,
                      1e-12, "1 − (inner/outer diameter)³, shell thickness a/2"))
    m = sf.mean_max_direction_cosine()
    rng = np.random.default_rng(0)
    v = rng.normal(size=(400_000, 3))
    v /= np.linalg.norm(v, axis=1)[:, None]
    m_mc = float(np.abs(v).max(1).mean())
    out.append(_close(cat, "E[max|n_i|]: Fibonacci sphere vs Monte Carlo", m, m_mc, 0.002,
                      "two sampling methods, relative error", rel=True))
    ds = np.arange(30.0, 71.0, 5.0)
    y = np.array([sf.surface_fraction(x) * x / (6 * sf.H) for x in ds])
    intercept = float(np.polyfit(1 / ds, y, 1)[1])
    out.append(_close(cat, "large-dot limit: f·d/(6h) extrapolated to d → ∞", intercept, m, 0.005,
                      "a simple-cubic facet exposes max|n_i|/h² atoms per unit area, so f → 6h·E[max|n_i|]/d; "
                      "linear extrapolation in 1/d over d = 30–70 nm, relative error", rel=True))
    out.append(_close(cat, "shell-model large-dot limit: f·d/(6h) at d = 1000 nm", sf.shell_fraction(1000.0) * 1000 / (6 * sf.H),
                      1.0, 0.005, "f ≈ 6t/d", rel=True))
    fs = [sf.surface_fraction(x) for x in (3.0, 5.0, 8.0, 12.0)]
    out.append(_flag(cat, "surface fraction falls with size (3, 5, 8, 12 nm)", all(a > b for a, b in zip(fs, fs[1:])),
                     ", ".join(f"{x:.3f}" for x in fs)))
    out.append(_flag(cat, "atom count < shell model at 3.1 and 5.1 nm",
                     r["surf_940"] < r["shell_940"] and r["surf_1400"] < r["shell_1400"],
                     "the count includes only atoms that miss a neighbour; the shell model counts the whole a/2 layer"))
    return out


# ---------------------------------------------------------------- transport
def _transport(r):
    cat = "Transport"
    lo, hi = D.BETA_QD
    out = [
        _flag(cat, "β of the QD film within the range of [19]", lo <= r["beta_qd"] <= hi,
              f"{lo} ≤ {r['beta_qd']:.3f} ≤ {hi} Å⁻¹; rate factor {r['factor_qd']:.2f} per Å"),
        _close(cat, "as presented: β = ln 2.6 → rate factor per Å", 1 / tr.relative_rate(r["beta_qd_presented"], 1.0),
               D.MOBILITY_FACTOR_PER_A_PRESENTED, 1e-12, "exp(β·1 Å) returns 2.6; corrected to [19], see README"),
    ]
    beta_si = 2 * math.sqrt(2 * sc.m_e * D.PHI_VAC * sc.e) / sc.hbar * 1e-10
    out.append(_close(cat, "vacuum 4.5 eV: β = 2(2m0φ)^½/ħ, recomputed in SI (Å⁻¹)", r["beta_vac"], beta_si, 1e-6,
                      "computed directly with SI constants", rel=True))
    out.append(_close(cat, "φ(β) and β(φ) are inverse functions", tr.beta_from_barrier(tr.barrier_from_beta(0.9555, 0.3), 0.3),
                      0.9555, 1e-12, "round trip"))
    out.append(_close(cat, "SAM: (β, φ, m*) self-consistent", tr.beta_from_barrier(D.PHI_SAM, r["m_sam"]), D.BETA_SAM, 1e-12,
                      "β recomputed from the derived m* and φ = 1.39 eV returns 0.79 Å⁻¹"))
    out.append(_flag(cat, "β ordering: SAM < QD film < vacuum", D.BETA_SAM < r["beta_qd"] < r["beta_vac"],
                     f"{D.BETA_SAM:.2f} < {r['beta_qd']:.3f} < {r['beta_vac']:.3f} Å⁻¹"))
    return out


# ---------------------------------------------------------------- dark current
def _dark(r):
    cat = "Dark current"
    out = []
    out.append(_close(cat, "n = 2 ratio = √(n = 1 ratio)", r["jd_ratio_n2"], math.sqrt(r["jd_ratio_n1"]), 1e-9,
                      "exp(ΔE/2kT) = [exp(ΔE/kT)]^½", rel=True))
    out.append(_close(cat, "temperature projection unchanged at T = T0", dc.scale_with_temperature(2.25e-9, 298.15, 298.15, 0.75, 1),
                      2.25e-9, 1e-12, "definition", rel=True))
    for n, key in ((1, "halving_n1"), (2, "halving_n2")):
        Eg = r["Eg1400"]
        up = brentq(lambda x: dc.scale_with_temperature(1.0, 300.0, 300.0 + x, Eg, n) - 2.0, 0.1, 50.0)
        down = brentq(lambda x: dc.scale_with_temperature(1.0, 300.0, 300.0 - x, Eg, n) - 0.5, 0.1, 50.0)
        out.append(_flag(cat, f"local halving interval lies between the exact halving and doubling steps (n = {n})", down < r[key] < up,
                         f"ln J is concave in T: exact {down:.2f} K (halving on cooling from 300 K) < local {r[key]:.2f} K "
                         f"< {up:.2f} K (doubling on warming)", model=r[key]))
    h = 1e-3
    for n in (1, 2):
        num = (math.log(dc.scale_with_temperature(1, 300, 300 + h, 0.8856, n))
               - math.log(dc.scale_with_temperature(1, 300, 300 - h, 0.8856, n))) / (2 * h)
        out.append(_close(cat, f"d lnJ/dT: numerical vs analytic (n = {n})", num,
                          math.log(2) / dc.halving_interval(0.8856, 300, n), 1e-6, "central difference", rel=True))
    J_hand = 64.6 * 1.602176634e-19 / (5e-4) ** 2
    out.append(_close(cat, "IMX990: 64.6 e⁻/s ÷ (5 µm)² (A/cm²)", r["J_imx990"], J_hand, 1e-12,
                      "by hand: 64.6 × q / (5×10⁻⁴ cm)²", rel=True))
    out.append(_flag(cat, "cooled IMX990 lies between the n = 1 and n = 2 projections",
                     r["J_iga_m30C_n1"] < r["J_imx990"] < r["J_iga_m30C_n2"],
                     f"{r['J_iga_m30C_n1']:.3g} < {r['J_imx990']:.3g} < {r['J_iga_m30C_n2']:.3g} A/cm²"))
    out.append(_flag(cat, "the QD dark current is not set by the gap",
                     r["jd_ratio_gap_only"] < 1 < r["jd_ratio_meas"],
                     f"by the gap alone QD/InGaAs would be {r['jd_ratio_gap_only']:.2f}×; measured {r['jd_ratio_meas']:.0f}×"))
    return out


# ---------------------------------------------------------------- detector
def _detector(r):
    cat = "Detector"
    qd = D.QD_PHOTODIODE
    out = [
        _close(cat, "Vafaie 2021: EQE 80 % at 1550 nm → R (A/W)", r["R_qd"], qd["responsivity_reported"], 0.01,
               "R = ηqλ/hc compared with the reported 1 A/W", rel=True),
    ]
    R_si = 0.6 * sc.e * 1400e-9 / (sc.h * sc.c)
    out.append(_close(cat, "R(η = 0.6, 1400 nm), recomputed in SI (A/W)", r["R_st"], R_si, 1e-6, "ηqλ/(hc)", rel=True))
    J_si = qd["dark_current"] * 1e4                       # A/m²
    D_si = r["R_qd"] / math.sqrt(2 * sc.e * J_si) * 100  # m → cm
    out.append(_close(cat, "D* unit conversion, recomputed in SI (Jones)", r["dstar_shot_qd"], D_si, 1e-9,
                      "R/(2qJ)^½ in SI, then m converted to cm", rel=True))
    out.append(_flag(cat, "measured D* below the shot-noise limit (both devices)",
                     qd["dstar"] < r["dstar_shot_qd"] and D.INGAAS_FPA["dstar"] < r["dstar_shot_iga"],
                     "thermal, 1/f and read-out noise add to the shot noise"))
    return out


# ---------------------------------------------------------------- slide registry
def _slides(r):
    out = []
    for e in slides.REGISTRY:
        model, ok = slides.check(e, r)
        where = " / ".join(x for x in (e.slide_text and f"slide: “{e.slide_text}”",
                                        e.script_text and f"script: “{e.script_text}”") if x)
        if e.corrected:
            where += f"; corrected after the talk to {r[e.corrected] * e.scale:.3g} (README, Correction)"
        if e.within is not None:
            how = f"range {e.within[0]:g}–{e.within[1]:g}; {where}"
            out.append(Check(f"Slide {e.slide}", e.quantity, ok, model, None, None, how))
        else:
            out.append(Check(f"Slide {e.slide}", e.quantity, ok, model, e.value, e.tol, where))
    return out


def run_all() -> List[Check]:
    r = compute()
    rows = _constants() + _quantum_size(r) + _surface(r) + _transport(r) + _dark(r) + _detector(r) + _slides(r)
    for i, c in enumerate(rows, 1):
        c.num = i
    return rows


def _fmt(x):
    if x is None:
        return "—"
    if x == 0:
        return "0"
    return f"{x:.4g}"


def to_markdown(rows):
    ok = sum(c.passed for c in rows)
    lines = [
        "# Validation results",
        "",
        f"{ok} / {len(rows)} checks passed. Generated by `python scripts/validate.py --markdown`; "
        "CI reruns every check on each push.",
        "",
        "| # | Category | Check | Model | Expected | Tolerance | Result | How it is checked |",
        "|---|---|---|---|---|---|---|---|",
    ]
    esc = lambda t: str(t).replace("|", "\\|")
    for c in rows:
        tol = _fmt(c.tol) + (" (rel)" if c.rel and c.tol is not None else "")
        lines.append(f"| {c.num} | {c.category} | {esc(c.name)} | {_fmt(c.model)} | {_fmt(c.expected)} | {tol} | "
                     f"{'PASS' if c.passed else 'FAIL'} | {esc(c.how)} |")
    return "\n".join(lines) + "\n"
