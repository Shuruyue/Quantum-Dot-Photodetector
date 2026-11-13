"""Registry of every computed number that appears in the presentation or the spoken script.

Each entry gives the slide number (18-slide deck), the value as shown, the key in
``summary.compute()``, and a tolerance equal to half a unit in the last digit shown (or an allowed
range for qualitative statements). ``slide_text`` is the exact string on the
slide; ``script_text`` is the matching phrase of the spoken script, which was delivered in Chinese
and is given here in English translation. Each number can be traced to where it is used.

Entries with ``corrected`` show a value that was later corrected (README, Correction): they are checked against
the input the presentation used, and ``corrected`` names the key of the corrected value.
"""
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class Shown:
    slide: int
    quantity: str
    key: str
    value: Optional[float] = None
    tol: Optional[float] = None
    scale: float = 1.0                      # model value × scale is compared with the shown value
    within: Optional[Tuple[float, float]] = None  # for qualitative statements
    slide_text: Optional[str] = None
    script_text: Optional[str] = None
    corrected: Optional[str] = None          # key of the corrected value, for a number corrected after the talk


REGISTRY = [
    # ------------------------------------------------------------ slide 4: two nano effects
    Shown(4, "bulk PbS absorption edge (µm)", "bulk_edge_um", 3.0, 0.05, slide_text="0.41 eV · 3.0 µm"),
    Shown(4, "dot diameter for 1400 nm (nm)", "d1400", 5.1, 0.05, slide_text="d = 5.1 nm", script_text="5.1 nm"),
    Shown(4, "gap at 1400 nm (eV)", "Eg1400", 0.89, 0.005, slide_text="0.89 eV · 1400 nm"),
    Shown(4, "dot diameter for 940 nm (nm)", "d940", 3.1, 0.05, slide_text="d = 3.1 nm", script_text="3.1 nm"),
    Shown(4, "gap at 940 nm (eV)", "Eg940", 1.32, 0.005, slide_text="1.32 eV · 940 nm"),
    Shown(4, "surface atoms, 3.1 nm dot (%)", "surf_940", 43, 0.5, scale=100,
          slide_text="3.1 nm: 43 %", script_text="about 43 %"),
    Shown(4, "surface atoms, 5.1 nm dot (%)", "surf_1400", 27, 0.5, scale=100,
          slide_text="5.1 nm: 27 %", script_text="about 27 %"),
    # ------------------------------------------------------------ slide 6: quantum size effect
    Shown(6, "Coulomb coefficient in the Brus formula", "coulomb_coeff", 1.8, 0.05, slide_text="1.8e²/(4πεε₀R)"),
    Shown(6, "EMA gap at 5.1 nm (eV)", "E_ema", 1.71, 0.005, slide_text="EMA 1.71 eV", script_text="EMA gives 1.71 eV"),
    Shown(6, "hyperbolic-band gap at 5.1 nm (eV)", "E_hbm", 1.07, 0.005,
          slide_text="hyperbolic bands [18] 1.07 eV", script_text="gives 1.07 eV"),
    Shown(6, "measured gap at 5.1 nm (eV)", "E_moreels", 0.89, 0.005,
          slide_text="measured [7] 0.89 eV", script_text="the measured value is 0.89 eV"),
    Shown(6, "EMA confinement overestimate (×)", "over_ema", 2.7, 0.05,
          slide_text="EMA 2.7× measured", script_text="overestimates by about 2.7 times"),
    Shown(6, "HBM confinement overestimate (×)", "over_hbm", 1.4, 0.05,
          slide_text="HBM 1.4× measured", script_text="about 1.4 times"),
    Shown(6, "EMA confinement energy at 5.1 nm (eV)", "conf_ema", 1.36, 0.005, script_text="the EMA confinement energy, 1.36 eV"),
    Shown(6, "EMA confinement / bulk gap", "conf_over_bulk_gap", within=(3.0, 4.0), script_text="more than three times"),
    Shown(6, "HBM vs EMA confinement at d = 400 nm", "hbm_ema_rel_diff_400nm", within=(0.0, 0.001),
          script_text="differ by less than 0.1 %"),
    Shown(6, "Moreels diameter for 1.29 eV (nm)", "d_for_1p29eV", 3.14, 0.005, script_text="our code gives 3.14 nm"),
    # ------------------------------------------------------------ slide 8: electrical properties
    Shown(8, "responsivity at η = 0.6, 1400 nm (A/W)", "R_st", 0.68, 0.005,
          slide_text="≈ 0.68 A/W at η = 0.6", script_text="about 0.68 A/W"),
    Shown(8, "β of the QD film (Å⁻¹)", "beta_qd_presented", 0.96, 0.005,
          slide_text="β ≈ 0.96 Å⁻¹ [19, 20]", script_text="β is about 0.96 Å⁻¹", corrected="beta_qd"),
    Shown(8, "κ of the QD film (Å⁻¹)", "kappa_qd_presented", 0.48, 0.005, script_text="κ ≈ 0.48 Å⁻¹",
          corrected="kappa_qd"),
    Shown(8, "barrier of the QD film for m* = m0 (eV)", "barrier_qd_m0_presented", 0.87, 0.005,
          script_text="φ is about 0.87 eV", corrected="barrier_qd_m0"),
    Shown(8, "m* implied by the SAM fit (m0)", "m_sam", 0.43, 0.005, script_text="m* ≈ 0.43 m0"),
    Shown(8, "barrier of the QD film for m* = 0.43 m0 (eV)", "barrier_qd_msam_presented", 2.0, 0.05,
          script_text="φ is about 2.0 eV", corrected="barrier_qd_msam"),
    Shown(8, "rate factor per Å, alkane SAM", "factor_sam", 2.2, 0.05, slide_text="β = 0.79 Å⁻¹, ×2.2/Å"),
    Shown(8, "β of a 4.5 eV vacuum gap (Å⁻¹)", "beta_vac", 2.2, 0.05,
          slide_text="STM, β ≈ 2.2 Å⁻¹", script_text="β is about 2.2 Å⁻¹"),
    Shown(8, "rate factor per Å, vacuum gap", "factor_vac", 9, 0.5, slide_text="β ≈ 2.2 Å⁻¹, ×9/Å"),
    # ------------------------------------------------------------ slide 9: optical properties
    Shown(9, "Si absorption edge (µm)", "si_edge_um", 1.11, 0.005,
          slide_text="Silicon CMOS: edge 1.11 µm", script_text="absorption edge about 1.1 µm"),
    Shown(9, "InGaAs absorption edge (µm)", "ingaas_edge_um", 1.65, 0.005,
          slide_text="InGaAs: edge 1.65 µm", script_text="about 1.65 µm"),
    Shown(9, "bulk PbS absorption edge (µm)", "bulk_edge_um", 3.0, 0.05,
          slide_text="up to bulk edge 3.0 µm", script_text="about 3.0 µm"),
    # ------------------------------------------------------------ slide 10: dark current
    Shown(10, "gap at 940 nm (eV)", "Eg940", 1.32, 0.005, slide_text="Eg 1.32 → 0.89 eV", script_text="the gap falls from 1.32 eV"),
    Shown(10, "gap at 1400 nm (eV)", "Eg1400", 0.89, 0.005, script_text="to 0.89 eV"),
    Shown(10, "ideal-limit increase, diffusion (slide)", "jd_ratio_n1", 1.9e7, 0.05e7, slide_text="×1.9 × 10⁷"),
    Shown(10, "ideal-limit increase, diffusion (script)", "jd_ratio_n1", 2e7, 0.5e7, script_text="about 2 × 10⁷ times"),
    Shown(10, "ideal-limit increase, generation (slide)", "jd_ratio_n2", 4.4e3, 50, slide_text="×4.4 × 10³"),
    Shown(10, "ideal-limit increase, generation (script)", "jd_ratio_n2", 4e3, 500, script_text="4 × 10³ times"),
    Shown(10, "halving interval, diffusion (K)", "halving_n1", 6, 0.5,
          slide_text="halves every ≈ 6 K", script_text="for every ≈ 6 K of cooling"),
    Shown(10, "halving interval, generation (K)", "halving_n2", 11, 0.5,
          slide_text="≈ 11 K (generation)", script_text="and 11 K"),
    Shown(10, "IMX990 dark current at −30 °C (nA/cm²)", "J_imx990_nA", 0.041, 0.0005, slide_text="IMX990 [25]: 0.041"),
    Shown(10, "PbS CQD / InGaAs dark current (×)", "jd_ratio_meas", 62, 0.5,
          slide_text="PbS CQD / InGaAs = 62×", script_text="about 62 times that of InGaAs"),
    # ------------------------------------------------------------ slide 11: industry today
    Shown(11, "shot-noise D*, PbS CQD (Jones)", "dstar_shot_qd", 4.7e12, 0.05e12,
          slide_text="4.7 × 10¹² Jones", script_text="4.7 × 10¹² Jones"),
    Shown(11, "shot-noise D*, InGaAs (Jones)", "dstar_shot_iga", 4.1e13, 0.05e13,
          slide_text="4.1 × 10¹³ Jones", script_text="4.1 × 10¹³ Jones"),
    Shown(11, "PbS CQD / InGaAs dark current, rounded (×)", "jd_ratio_meas", 60, 5, script_text="about 60 times higher"),
    Shown(11, "InGaAs / PbS CQD measured D* (×)", "dstar_ratio_meas", 14, 0.5, script_text="D* about 14 times lower"),
    # ------------------------------------------------------------ slide 12: products
    Shown(12, "pixel area, Acuros / ST (×)", "area_acuros_st", 86, 0.5,
          slide_text="Pixel area: 86×", script_text="86 times the ST pixel"),
    Shown(12, "pixel area, IMX990 / ST (×)", "area_imx_st", 9.5, 0.05,
          slide_text="86× and 9.5× the ST pixel", script_text="about 9.5 times"),
    # ------------------------------------------------------------ slide 13: future development
    Shown(13, "dark-current gap to InGaAs, rounded (×)", "jd_ratio_meas", 60, 5,
          slide_text="close the ≈ 60× gap", script_text="about 60 times"),
    # ------------------------------------------------------------ slide 16: conclusion
    Shown(16, "EMA confinement overestimate (×)", "over_ema", 2.7, 0.05,
          slide_text="overestimates the confinement ×2.7", script_text="overestimates by about 2.7 times"),
    Shown(16, "β of the QD film (Å⁻¹)", "beta_qd_presented", 0.96, 0.005, slide_text="0.96 Å⁻¹",
          corrected="beta_qd"),
    Shown(16, "PbS CQD / InGaAs dark current (×)", "jd_ratio_meas", 62, 0.5, slide_text="62×"),
    Shown(16, "PbS CQD / InGaAs dark current, rounded (×)", "jd_ratio_meas", 60, 5,
          slide_text="dark current (≈ 60× InGaAs)"),
    Shown(16, "pixel area, IMX990 / ST (×)", "area_imx_st", 9.5, 0.05, slide_text="1/9.5 the area"),
]


def check(entry, results):
    """Return (model value in display units, passed)."""
    model = results[entry.key] * entry.scale
    if entry.within is not None:
        lo, hi = entry.within
        return model, lo < model < hi
    return model, abs(model - entry.value) <= entry.tol * (1 + 1e-9)
