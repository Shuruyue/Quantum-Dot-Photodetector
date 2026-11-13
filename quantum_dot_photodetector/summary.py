"""Every number used in the report, computed in one place."""
from . import dark_current as dc
from . import data as D
from . import detector as det
from . import quantum_size as qs
from . import surface as sf
from . import transport as tr
from .constants import HC


def compute():
    r = {}
    # ---------------------------------------------------------------- size and gap
    lam_short, lam_long = D.ST_WAVELENGTHS_NM
    r["d940"] = qs.diameter_for_wavelength(lam_short)
    r["d1400"] = qs.diameter_for_wavelength(lam_long)
    r["Eg940"] = HC / lam_short
    r["Eg1400"] = HC / lam_long
    d = r["d1400"]
    r["E_ema"] = float(qs.gap_ema(d))
    r["E_hbm"] = float(qs.gap_hbm(d))
    r["E_moreels"] = float(qs.gap_moreels(d))
    r["conf_ema"] = float(qs.confinement_ema(d))
    r["coulomb"] = float(qs.coulomb(d))
    r["over_ema"] = qs.overestimate(r["E_ema"], d)
    r["over_hbm"] = qs.overestimate(r["E_hbm"], d)
    r["conf_over_bulk_gap"] = r["conf_ema"] / D.EG_PBS
    big = 400.0
    conf_hbm_big = float(qs.gap_hbm_no_coulomb(big)) - D.EG_PBS
    r["hbm_ema_rel_diff_400nm"] = abs(conf_hbm_big / float(qs.confinement_ema(big)) - 1)
    r["d_for_1p29eV"] = qs.diameter_for_gap(1.29)
    r["coulomb_coeff"] = D.COULOMB_COEFF
    # absorption edges
    r["bulk_edge_um"] = qs.cutoff_wavelength_nm(D.EG_PBS) / 1000
    r["si_edge_um"] = qs.cutoff_wavelength_nm(D.EG_SI) / 1000
    r["ingaas_edge_um"] = qs.cutoff_wavelength_nm(D.EG_INGAAS) / 1000
    # ---------------------------------------------------------------- surface atoms
    for key, dd in (("940", r["d940"]), ("1400", r["d1400"])):
        r["surf_" + key] = sf.surface_fraction(dd)
        r["shell_" + key] = sf.shell_fraction(dd)
        r["N_" + key] = sf.count_sites(dd, "atom")[0]
    # ---------------------------------------------------------------- transport
    r["beta_qd_low"], r["beta_qd_high"] = D.BETA_QD
    r["beta_qd"] = sum(D.BETA_QD) / 2                     # midpoint of the range reported by [19]
    r["factor_qd"] = 1 / tr.relative_rate(r["beta_qd"], 1.0)
    r["kappa_qd"] = r["beta_qd"] / 2
    r["barrier_qd_m0"] = tr.barrier_from_beta(r["beta_qd"], 1.0)
    r["m_sam"] = tr.mass_from_beta_and_barrier(D.BETA_SAM, D.PHI_SAM)
    r["barrier_qd_msam"] = tr.barrier_from_beta(r["beta_qd"], r["m_sam"])
    # as presented (factor 2.6 per Å); kept to check the slides and the script, see README, Correction
    r["beta_qd_presented"] = tr.beta_from_factor(D.MOBILITY_FACTOR_PER_A_PRESENTED)
    r["kappa_qd_presented"] = r["beta_qd_presented"] / 2
    r["barrier_qd_m0_presented"] = tr.barrier_from_beta(r["beta_qd_presented"], 1.0)
    r["barrier_qd_msam_presented"] = tr.barrier_from_beta(r["beta_qd_presented"], r["m_sam"])
    r["beta_vac"] = tr.beta_from_barrier(D.PHI_VAC)
    r["factor_vac"] = 1 / tr.relative_rate(r["beta_vac"], 1.0)
    r["factor_sam"] = 1 / tr.relative_rate(D.BETA_SAM, 1.0)
    # ---------------------------------------------------------------- dark current
    r["jd_ratio_n1"] = dc.ideal_ratio(r["Eg1400"], r["Eg940"], 300.0, 1)
    r["jd_ratio_n2"] = dc.ideal_ratio(r["Eg1400"], r["Eg940"], 300.0, 2)
    r["halving_n1"] = dc.halving_interval(r["Eg1400"], 300.0, 1)
    r["halving_n2"] = dc.halving_interval(r["Eg1400"], 300.0, 2)
    iga, imx, qd = D.INGAAS_FPA, D.IMX990, D.QD_PHOTODIODE
    r["J_imx990"] = det.dark_current_density(imx["dark_e_per_s"], imx["pitch_um"])
    r["J_imx990_nA"] = r["J_imx990"] * 1e9
    for n in (1, 2):
        r[f"J_iga_m30C_n{n}"] = dc.scale_with_temperature(iga["dark_current"], iga["temperature"],
                                                          imx["temperature"], iga["gap"], n)
    r["jd_ratio_meas"] = qd["dark_current"] / iga["dark_current"]
    r["jd_ratio_gap_only"] = dc.ideal_ratio(iga["gap"], qd["gap"], iga["temperature"], 1) ** -1
    # ---------------------------------------------------------------- detector metrics
    r["R_st"] = det.responsivity(D.ST_QE_1400, lam_long)
    r["R_qd"] = det.responsivity(qd["eqe"], qd["wavelength_nm"])
    r["R_iga"] = det.responsivity(iga["eqe"], iga["wavelength_nm"])
    r["dstar_shot_qd"] = det.dstar_shot_limit(r["R_qd"], qd["dark_current"])
    r["dstar_shot_iga"] = det.dstar_shot_limit(r["R_iga"], iga["dark_current"])
    r["dstar_ratio_meas"] = iga["dstar"] / qd["dstar"]
    p = D.PIXEL_PITCH_UM
    r["area_acuros_st"] = det.pixel_area_ratio(p["acuros"], p["st"])
    r["area_imx_st"] = det.pixel_area_ratio(p["imx990"], p["st"])
    return r
