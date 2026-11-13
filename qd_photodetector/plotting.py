"""Figures (14 cm wide, 300 dpi). Every plotted value comes from the model modules."""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from . import dark_current as dc  # noqa: E402
from . import data as D  # noqa: E402
from . import quantum_size as qs  # noqa: E402
from . import surface as sf  # noqa: E402
from . import transport as tr  # noqa: E402
from .summary import compute  # noqa: E402

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"  # categorical slots 1–3
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
WIDTH_IN = 14 / 2.54


def _style():
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
        "text.color": INK, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
        "axes.spines.top": False, "axes.spines.right": False, "font.size": 8.5,
        "legend.frameon": False, "lines.linewidth": 1.6,
    })


def _save(fig, outdir, name):
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, name)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return path


def fig_models(outdir):
    r = compute()
    d = np.linspace(2.5, 10, 300)
    fig, ax = plt.subplots(figsize=(WIDTH_IN, WIDTH_IN * 0.55))
    ax.plot(d, qs.gap_ema(d), color=ORANGE, label="EMA, parabolic bands [5]")
    ax.plot(d, qs.gap_hbm(d), color=AQUA, label="hyperbolic bands [18]")
    ax.plot(d, qs.gap_moreels(d), color=BLUE, label="measured sizing curve [7]")
    ax.axhline(D.EG_PBS, color=INK2, lw=0.9, ls="--")
    ax.text(9.9, D.EG_PBS + 0.03, "bulk PbS 0.41 eV", ha="right", color=INK2)
    x = r["d1400"]
    ax.axvline(x, color=INK2, lw=0.8, ls=":")
    for key, c in (("E_ema", ORANGE), ("E_hbm", AQUA), ("E_moreels", BLUE)):
        ax.plot([x], [r[key]], "o", ms=5, color=c, mec=SURFACE, mew=1.2, zorder=5)
        ax.annotate(f"{r[key]:.2f} eV", (x, r[key]), xytext=(6, 4), textcoords="offset points", color=INK)
    ax.text(x - 0.07, 0.47, f"d = {x:.1f} nm", color=INK2, ha="right", va="bottom")
    ax.set(xlim=(2.5, 10), ylim=(0.3, 2.2), xlabel="PbS dot diameter d (nm)", ylabel="Band gap E (eV)")
    ax.legend(loc="upper right", fontsize=7.5)
    return _save(fig, outdir, "f_models.png")


def fig_surface(outdir):
    r = compute()
    ds = np.round(np.arange(2.0, 12.01, 0.25), 3)
    rows = sf.curve(ds)
    fig, ax = plt.subplots(figsize=(WIDTH_IN, WIDTH_IN * 0.5))
    dd = np.linspace(2.0, 12.0, 200)
    ax.plot(dd, [100 * sf.shell_fraction(x) for x in dd], color=ORANGE, label="one-monolayer shell, t = a/2")
    ax.plot([x for x, _, _ in rows], [100 * f for _, f, _ in rows], "o", ms=3.5, color=BLUE,
            label="atom count on the rock-salt lattice")
    for key, dkey, pos in (("surf_940", "d940", (4.3, 52)), ("surf_1400", "d1400", (6.3, 36))):
        ax.plot([r[dkey]], [100 * r[key]], "o", ms=7, color=BLUE, mec=SURFACE, mew=1.2, zorder=5)
        ax.annotate(f"{r[dkey]:.1f} nm: {100 * r[key]:.0f} %", (r[dkey], 100 * r[key]), xytext=pos,
                    textcoords="data", color=INK, fontweight="bold",
                    arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7, shrinkA=2, shrinkB=5))
    ax.set(xlim=(2, 12), ylim=(0, 70), xlabel="Dot diameter d (nm)", ylabel="Atoms at the surface (%)")
    ax.legend(loc="upper right")
    return _save(fig, outdir, "f_surface.png")


def fig_tunnel(outdir):
    r = compute()
    x = np.linspace(0, 6, 100)
    fig, ax = plt.subplots(figsize=(WIDTH_IN, WIDTH_IN * 0.5))
    lines = ((f"QD film [19, 20]: β = {r['beta_qd']:.2f} Å⁻¹", r["beta_qd"], BLUE),
             (f"alkane SAM [21]: β = {D.BETA_SAM:.2f} Å⁻¹", D.BETA_SAM, ORANGE),
             (f"vacuum gap, φ = {D.PHI_VAC} eV: β = {r['beta_vac']:.2f} Å⁻¹", r["beta_vac"], AQUA))
    for lab, b, c in lines:
        ax.semilogy(x, [tr.relative_rate(b, v) for v in x], color=c, label=lab)
    ax.set(xlim=(0, 6), ylim=(1e-6, 1.5), xlabel="Extra gap Δd (Å)", ylabel="Relative rate exp(−β·Δd)")
    ax.legend(loc="lower left")
    return _save(fig, outdir, "f_tunnel.png")


def fig_dark(outdir):
    r = compute()
    iga = D.INGAAS_FPA
    t = np.linspace(-40, 60, 200)
    fig, ax = plt.subplots(figsize=(WIDTH_IN, WIDTH_IN * 0.55))
    for n, ls in ((1, "-"), (2, "--")):
        J = [dc.scale_with_temperature(iga["dark_current"], iga["temperature"], v + 273.15, iga["gap"], n) * 1e9
             for v in t]
        lab = ("diffusion (n = 1): ∝ T³·exp(−Eg/kT)" if n == 1 else "generation (n = 2): ∝ T^1.5·exp(−Eg/2kT)")
        ax.semilogy(t, J, color=ORANGE, ls=ls, label=f"InGaAs projection, {lab}")
    pts = ((25.0, D.QD_PHOTODIODE["dark_current"], BLUE, "o", "PbS CQD photodiode [23]: 140", (-10, -3), "right"),
           (25.0, iga["dark_current"], ORANGE, "o", "InGaAs FPA [24]: 2.25", (10, -14), "left"))
    for T, J, c, m, lab, off, ha in pts:
        ax.semilogy([T], [J * 1e9], m, ms=7, color=c, mec=SURFACE, mew=1.2, zorder=5)
        ax.annotate(lab, (T, J * 1e9), xytext=off, textcoords="offset points", color=INK, ha=ha)
    ax.semilogy([-30.0], [r["J_imx990_nA"]], "D", ms=6, color=ORANGE, mec=SURFACE, mew=1.2, zorder=5)
    ax.annotate(f"IMX990 at −30 °C [25]: {r['J_imx990_nA']:.3f}", (-30.0, r["J_imx990_nA"]), xytext=(-16, 0.004),
                textcoords="data", color=INK, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7))
    ax.set(xlim=(-40, 60), ylim=(1e-4, 1e3), xlabel="Temperature (°C)", ylabel="Dark current (nA cm⁻²)")
    ax.legend(loc="lower right", fontsize=7.5)
    ax.text(27, 0.35, f"PbS CQD / InGaAs = {r['jd_ratio_meas']:.0f}× at room\ntemperature, although the QD gap\n"
                      f"is wider ({D.QD_PHOTODIODE['gap']:.2f} vs {iga['gap']:.2f} eV)", va="top", color=INK2)
    return _save(fig, outdir, "f_dark.png")


def make_all(outdir="docs/figures"):
    return [fig_models(outdir), fig_surface(outdir), fig_tunnel(outdir), fig_dark(outdir)]


_style()
