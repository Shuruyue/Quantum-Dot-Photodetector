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
    cat = "常數"
    return [
        _close(cat, "ħ²/2m0 (eV nm²)", C.HB2_2M0, sc.hbar**2 / (2 * sc.m_e) / sc.e * 1e18, 1e-6,
               "與 scipy.constants（CODATA 2018）比較，相對誤差", rel=True),
        _close(cat, "e²/4πε0 (eV nm)", C.E2_4PIE0, sc.e / (4 * math.pi * sc.epsilon_0) * 1e9, 1e-6,
               "同上", rel=True),
        _close(cat, "hc (eV nm)", C.HC, sc.h * sc.c / sc.e * 1e9, 1e-6, "同上", rel=True),
        _close(cat, "k_B (eV/K)", C.KB, sc.k / sc.e, 1e-6, "同上", rel=True),
    ]


# ---------------------------------------------------------------- quantum size
def _quantum_size(r):
    cat = "量子尺寸"
    out = []
    for lam in D.ST_WAVELENGTHS_NM:
        d = qs.diameter_for_wavelength(lam)
        out.append(_close(cat, f"Moreels 反解：E(d({lam:.0f} nm)) = hc/λ (eV)", float(qs.gap_moreels(d)), C.HC / lam,
                          1e-9, "求得直徑後代回 Moreels 曲線，應回到原能量"))
    d = r["d1400"]
    R_m = d / 2 * 1e-9
    conf_si = (sc.hbar**2 * math.pi**2 / (2 * R_m**2)) * (2 / (D.M_STAR * sc.m_e)) / sc.e
    out.append(_close(cat, "EMA 侷限能 @ d(1400 nm)：SI 單位重算 (eV)", r["conf_ema"], conf_si, 1e-6,
                      "ħ²π²/(2R²)·(1/me*+1/mh*) 直接用 SI 常數計算，不經過模組常數", rel=True))
    coul_si = D.COULOMB_COEFF * sc.e / (4 * math.pi * sc.epsilon_0 * D.EPS_INF * R_m)
    out.append(_close(cat, "庫侖項 @ d(1400 nm)：SI 單位重算 (eV)", r["coulomb"], coul_si, 1e-6,
                      "1.786e²/(4πε0εR) 以 SI 常數計算", rel=True))
    k = math.pi / (d / 2)
    Ec = math.sqrt((D.EG_PBS / 2) ** 2 + D.EG_PBS * C.HB2_2M0 * k**2 / D.M_STAR)
    out.append(_close(cat, "HBM 能隙 = 導帶能量 × 2（鏡像能帶）", float(qs.gap_hbm_no_coulomb(d)), 2 * Ec, 1e-12,
                      "由 E_c(k) = [(Eg/2)² + Eg ħ²k²/2m*]^½ 逐項計算"))
    for D_big in (40.0, 100.0, 400.0):
        x = float(qs.confinement_ema(D_big))
        ratio = (float(qs.gap_hbm_no_coulomb(D_big)) - D.EG_PBS) / x
        u = x / D.EG_PBS
        series = 1 - u / 2 + u**2 / 2
        out.append(_close(cat, f"小 k 極限：HBM/EMA 侷限能比 @ d = {D_big:.0f} nm", ratio - 1, series - 1, 0.01,
                          "√(1+2u) 的級數展開 1 + u − u²/2 + u³/2，u = EMA 侷限能/Eg；相對誤差", rel=True))
    ds = np.linspace(2.5, 10, 301)
    out.append(_flag(cat, "2.5–10 nm：HBM ≤ EMA", np.all(qs.gap_hbm(ds) <= qs.gap_ema(ds) + 1e-12),
                     "雙曲線色散永遠在拋物線下方"))
    out.append(_flag(cat, "2.5–10 nm：Moreels < HBM", np.all(qs.gap_moreels(ds) < qs.gap_hbm(ds)),
                     "實驗曲線低於兩個無限位能障模型"))
    out.append(_flag(cat, "2.5–10 nm：三條曲線都隨 d 單調下降",
                     all(np.all(np.diff(f(ds)) < 0) for f in (qs.gap_ema, qs.gap_hbm, qs.gap_moreels)),
                     "尺寸變大，能隙變小"))
    for name, f in (("EMA", qs.gap_ema), ("HBM", qs.gap_hbm), ("Moreels", qs.gap_moreels)):
        out.append(_close(cat, f"{name} 在 d = 1000 nm 回到塊材 0.41 eV", float(f(1000.0)), D.EG_PBS, 1e-3,
                          "大顆極限"))
    out.append(_close(cat, "EMA 高估倍數（定義式）", r["over_ema"],
                      (r["E_ema"] - D.EG_PBS) / (r["E_moreels"] - D.EG_PBS), 1e-12,
                      "(E_EMA − Eg)/(E_meas − Eg)"))
    return out


# ---------------------------------------------------------------- surface atoms
def _surface(r):
    cat = "表面原子"
    out = []
    for d in (2.0, r["d940"], r["d1400"]):
        for c in sf.CENTRINGS:
            a, b = sf.count_sites(d, c), sf.count_sites_naive(d, c)
            out.append(_flag(cat, f"兩種演算法計數一致 @ d = {d:.3f} nm（{c}）", a == b,
                             f"向量化網格 vs 逐點集合迴圈：(N, 表面) = {a} vs {b}"))
    d = 20.0
    N = sf.count_sites(d, "atom")[0]
    out.append(_close(cat, "原子數密度：N / (πd³/6 ÷ h³) @ d = 20 nm", N / ((math.pi * d**3 / 6) / sf.H**3), 1.0, 0.01,
                      "rock salt 每 a³ 有 8 個原子 = 每 h³ 一個；大顆時計數應接近連續體積"))
    t = sf.H
    out.append(_close(cat, "殼層模型 @ d(940 nm)：手算", r["shell_940"], 1 - ((r["d940"] - 2 * t) / r["d940"]) ** 3,
                      1e-12, "1 − (內徑/外徑)³，殼層厚度 a/2"))
    m = sf.mean_max_direction_cosine()
    rng = np.random.default_rng(0)
    v = rng.normal(size=(400_000, 3))
    v /= np.linalg.norm(v, axis=1)[:, None]
    m_mc = float(np.abs(v).max(1).mean())
    out.append(_close(cat, "E[max|n_i|]：Fibonacci 球面 vs Monte Carlo", m, m_mc, 0.002,
                      "兩種取樣方法，相對誤差", rel=True))
    ds = np.arange(30.0, 71.0, 5.0)
    y = np.array([sf.surface_fraction(x) * x / (6 * sf.H) for x in ds])
    intercept = float(np.polyfit(1 / ds, y, 1)[1])
    out.append(_close(cat, "大顆極限：f·d/(6h) 外插至 d → ∞", intercept, m, 0.005,
                      "簡單立方晶面每單位面積暴露 max|n_i|/h² 個原子，故 f → 6h·E[max|n_i|]/d；"
                      "d = 30–70 nm 對 1/d 線性外插，相對誤差", rel=True))
    out.append(_close(cat, "殼層模型大顆極限：f·d/(6h) @ d = 1000 nm", sf.shell_fraction(1000.0) * 1000 / (6 * sf.H),
                      1.0, 0.005, "f ≈ 6t/d", rel=True))
    fs = [sf.surface_fraction(x) for x in (3.0, 5.0, 8.0, 12.0)]
    out.append(_flag(cat, "表面比例隨尺寸遞減（3, 5, 8, 12 nm）", all(a > b for a, b in zip(fs, fs[1:])),
                     ", ".join(f"{x:.3f}" for x in fs)))
    out.append(_flag(cat, "計數模型 < 殼層模型 @ 3.1 與 5.1 nm",
                     r["surf_940"] < r["shell_940"] and r["surf_1400"] < r["shell_1400"],
                     "計數只算缺鄰居的原子，殼層模型把整層厚度 a/2 都算進去"))
    return out


# ---------------------------------------------------------------- transport
def _transport(r):
    cat = "載子傳輸"
    out = [
        _close(cat, "β = ln 2.6 → 每 Å 速率比", 1 / tr.relative_rate(r["beta_qd"], 1.0), D.MOBILITY_FACTOR_PER_A, 1e-12,
               "exp(β·1 Å) 應回到 2.6"),
    ]
    beta_si = 2 * math.sqrt(2 * sc.m_e * D.PHI_VAC * sc.e) / sc.hbar * 1e-10
    out.append(_close(cat, "真空 4.5 eV：β = 2(2m0φ)^½/ħ，SI 重算 (Å⁻¹)", r["beta_vac"], beta_si, 1e-6,
                      "以 SI 常數直接計算", rel=True))
    out.append(_close(cat, "φ(β) 與 β(φ) 互為反函數", tr.beta_from_barrier(tr.barrier_from_beta(0.9555, 0.3), 0.3),
                      0.9555, 1e-12, "代回"))
    out.append(_close(cat, "SAM：(β, φ, m*) 自洽", tr.beta_from_barrier(D.PHI_SAM, r["m_sam"]), D.BETA_SAM, 1e-12,
                      "用推得的 m* 與 φ = 1.39 eV 重算 β，應回到 0.79 Å⁻¹"))
    out.append(_flag(cat, "β 排序：SAM < QD 薄膜 < 真空", D.BETA_SAM < r["beta_qd"] < r["beta_vac"],
                     f"{D.BETA_SAM:.2f} < {r['beta_qd']:.3f} < {r['beta_vac']:.3f} Å⁻¹"))
    return out


# ---------------------------------------------------------------- dark current
def _dark(r):
    cat = "暗電流"
    out = []
    out.append(_close(cat, "n = 2 比值 = √(n = 1 比值)", r["jd_ratio_n2"], math.sqrt(r["jd_ratio_n1"]), 1e-9,
                      "exp(ΔE/2kT) = [exp(ΔE/kT)]^½", rel=True))
    out.append(_close(cat, "溫度外推在 T = T0 時不變", dc.scale_with_temperature(2.25e-9, 298.15, 298.15, 0.75, 1),
                      2.25e-9, 1e-12, "定義", rel=True))
    for n, key in ((1, "halving_n1"), (2, "halving_n2")):
        Eg = r["Eg1400"]
        up = brentq(lambda x: dc.scale_with_temperature(1.0, 300.0, 300.0 + x, Eg, n) - 2.0, 0.1, 50.0)
        down = brentq(lambda x: dc.scale_with_temperature(1.0, 300.0, 300.0 - x, Eg, n) - 0.5, 0.1, 50.0)
        out.append(_flag(cat, f"局部減半間隔介於精確降溫減半與升溫加倍之間（n = {n}）", down < r[key] < up,
                         f"ln J 對 T 為凹函數；精確解 {down:.2f} K（300 K 降溫減半）< 局部 {r[key]:.2f} K "
                         f"< {up:.2f} K（升溫加倍）", model=r[key]))
    h = 1e-3
    for n in (1, 2):
        num = (math.log(dc.scale_with_temperature(1, 300, 300 + h, 0.8856, n))
               - math.log(dc.scale_with_temperature(1, 300, 300 - h, 0.8856, n))) / (2 * h)
        out.append(_close(cat, f"d lnJ/dT：數值微分 vs 解析式（n = {n}）", num,
                          math.log(2) / dc.halving_interval(0.8856, 300, n), 1e-6, "中央差分", rel=True))
    J_hand = 64.6 * 1.602176634e-19 / (5e-4) ** 2
    out.append(_close(cat, "IMX990：64.6 e⁻/s ÷ (5 µm)² (A/cm²)", r["J_imx990"], J_hand, 1e-12,
                      "手算 64.6 × q / (5×10⁻⁴ cm)²", rel=True))
    out.append(_flag(cat, "冷卻的 IMX990 落在 n = 1 與 n = 2 外推之間",
                     r["J_iga_m30C_n1"] < r["J_imx990"] < r["J_iga_m30C_n2"],
                     f"{r['J_iga_m30C_n1']:.3g} < {r['J_imx990']:.3g} < {r['J_iga_m30C_n2']:.3g} A/cm²"))
    out.append(_flag(cat, "量子點 dark current 不是能隙造成的",
                     r["jd_ratio_gap_only"] < 1 < r["jd_ratio_meas"],
                     f"只看能隙，QD/InGaAs 應為 {r['jd_ratio_gap_only']:.2f}×；實測 {r['jd_ratio_meas']:.0f}×"))
    return out


# ---------------------------------------------------------------- detector
def _detector(r):
    cat = "偵測器"
    qd = D.QD_PHOTODIODE
    out = [
        _close(cat, "Vafaie 2021：EQE 80 % @ 1550 nm → R (A/W)", r["R_qd"], qd["responsivity_reported"], 0.01,
               "R = ηqλ/hc 與論文報告的 1 A/W 比較", rel=True),
    ]
    R_si = 0.6 * sc.e * 1400e-9 / (sc.h * sc.c)
    out.append(_close(cat, "R(η = 0.6, 1400 nm)：SI 重算 (A/W)", r["R_st"], R_si, 1e-6, "ηqλ/(hc)", rel=True))
    J_si = qd["dark_current"] * 1e4                       # A/m²
    D_si = r["R_qd"] / math.sqrt(2 * sc.e * J_si) * 100  # m → cm
    out.append(_close(cat, "D* 單位換算：SI 重算 (Jones)", r["dstar_shot_qd"], D_si, 1e-9,
                      "在 SI 中計算 R/(2qJ)^½ 再把 m 換成 cm", rel=True))
    out.append(_flag(cat, "實測 D* 低於 shot-noise 極限（兩種元件）",
                     qd["dstar"] < r["dstar_shot_qd"] and D.INGAAS_FPA["dstar"] < r["dstar_shot_iga"],
                     "還有熱雜訊、1/f 雜訊與讀出雜訊"))
    return out


# ---------------------------------------------------------------- slide registry
def _slides(r):
    out = []
    for e in slides.REGISTRY:
        model, ok = slides.check(e, r)
        where = " / ".join(x for x in (e.slide_text and f"投影片「{e.slide_text}」",
                                        e.script_text and f"講稿「{e.script_text}」") if x)
        if e.within is not None:
            how = f"範圍 {e.within[0]:g}–{e.within[1]:g}；{where}"
            out.append(Check(f"簡報數值 p{e.slide}", e.quantity, ok, model, None, None, how))
        else:
            out.append(Check(f"簡報數值 p{e.slide}", e.quantity, ok, model, e.value, e.tol, where))
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
