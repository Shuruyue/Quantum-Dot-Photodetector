"""Check the physics of the interactive page web/quantum-dot-explorer.html against the Python package.

The page contains a block of pure JavaScript functions between the markers
"// ---- physics: begin" and "// ---- physics: end". This script runs that block in Node.js for random
wavelengths, temperatures and ligand steps and compares every number with quantum_dot_photodetector:

- dot diameter for a wavelength (the page solves the Moreels curve in closed form, the package with Brent's method),
- the effective-mass, hyperbolic-band and measured gaps and the confinement ratios,
- atom and surface-atom counts on the lattice (which must be identical) and the surface and shell fractions,
- ideal dark-current ratios and halving steps for n = 1 and 2,
- tunnelling rates, barriers and the constants derived from the data (β of the film, SAM mass, vacuum β).

Usage: python scripts/verify_web_page.py [--cases 300]
Requires Node.js on the PATH.
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from quantum_dot_photodetector import dark_current as dc
from quantum_dot_photodetector import quantum_size as qs
from quantum_dot_photodetector import surface as sf
from quantum_dot_photodetector import transport as tr
from quantum_dot_photodetector.constants import HC
from quantum_dot_photodetector.summary import compute

PAGE = ROOT / "web" / "quantum-dot-explorer.html"
TOLERANCE = 1e-9

NODE_HARNESS = r"""
const fs = require("fs"), vm = require("vm");
const page = fs.readFileSync(process.argv[1], "utf8");  // with -e the first argument is argv[1]
const after = page.split("// ---- physics: begin")[1], block = after.slice(after.indexOf("\n")).split("// ---- physics: end")[0];
const ctx = {}; vm.createContext(ctx);
vm.runInContext(block + "\n;this.api = { diameterForWavelength, gapEma, gapHbm, gapMoreels, overestimate, countSites, surfaceFraction, shellFraction, idealRatio, halvingInterval, relativeRate, barrierFromBeta, BETA_FILM, M_SAM, BETA_VAC, measuredDarkRatio, gapOnlyDarkRatio, HC };", ctx);
const a = ctx.api, cases = JSON.parse(fs.readFileSync(0, "utf8")), out = [];
for (const c of cases) {
  const d = a.diameterForWavelength(c.lam), E = a.HC / c.lam, Er = a.HC / c.ref, ema = a.gapEma(d), hbm = a.gapHbm(d);
  out.push({ d, ema, hbm, moreels: a.gapMoreels(d), overEma: a.overestimate(ema, d), overHbm: a.overestimate(hbm, d),
             atom: a.countSites(d, 0), cube: a.countSites(d, 0.5), surf: a.surfaceFraction(d), shell: a.shellFraction(d),
             r1: a.idealRatio(E, Er, c.T, 1), r2: a.idealRatio(E, Er, c.T, 2), h1: a.halvingInterval(E, c.T, 1), h2: a.halvingInterval(E, c.T, 2),
             rate: a.relativeRate(c.beta, c.dx), barrier: a.barrierFromBeta(c.beta, c.m) });
}
process.stdout.write(JSON.stringify({ cases: out, constants: { betaFilm: a.BETA_FILM, mSam: a.M_SAM, betaVac: a.BETA_VAC,
  measured: a.measuredDarkRatio(), gapOnly: a.gapOnlyDarkRatio() } }));
"""


def random_cases(n, seed=0):
    rng = random.Random(seed)
    return [{"lam": rng.uniform(800, 1800), "ref": rng.uniform(800, 1800), "T": rng.uniform(230, 330),
             "dx": rng.uniform(0, 6), "beta": rng.uniform(0.5, 2.5), "m": rng.uniform(0.1, 1.0)} for _ in range(n)]


def expected(c):
    d = qs.diameter_for_wavelength(c["lam"])
    E, Er = HC / c["lam"], HC / c["ref"]
    ema, hbm = float(qs.gap_ema(d)), float(qs.gap_hbm(d))
    return {"d": d, "ema": ema, "hbm": hbm, "moreels": float(qs.gap_moreels(d)),
            "overEma": qs.overestimate(ema, d), "overHbm": qs.overestimate(hbm, d),
            "atom": list(sf.count_sites(d, "atom")), "cube": list(sf.count_sites(d, "interstitial")),
            "surf": sf.surface_fraction(d), "shell": sf.shell_fraction(d),
            "r1": dc.ideal_ratio(E, Er, c["T"], 1), "r2": dc.ideal_ratio(E, Er, c["T"], 2),
            "h1": dc.halving_interval(E, c["T"], 1), "h2": dc.halving_interval(E, c["T"], 2),
            "rate": tr.relative_rate(c["beta"], c["dx"]), "barrier": tr.barrier_from_beta(c["beta"], c["m"])}


def rel(a, b):
    return abs(a - b) / max(abs(b), 1e-300)


def run(n_cases=300):
    """Returns (largest relative difference per quantity, number of differing counts)."""
    node = shutil.which("node")
    if node is None:
        raise RuntimeError("Node.js is needed to run the page's JavaScript")
    cases = random_cases(n_cases)
    proc = subprocess.run([node, "-e", NODE_HARNESS, str(PAGE)], input=json.dumps(cases), capture_output=True,
                          text=True, encoding="utf-8", check=True)
    page = json.loads(proc.stdout)
    worst, counts_differ = {}, 0
    for c, got in zip(cases, page["cases"], strict=True):
        want = expected(c)
        for key, value in want.items():
            if key in ("atom", "cube"):
                counts_differ += got[key] != value
                continue
            worst[key] = max(worst.get(key, 0.0), rel(got[key], value))
    r = compute()
    for key, value in (("betaFilm", r["beta_qd"]), ("mSam", r["m_sam"]), ("betaVac", r["beta_vac"]),
                       ("measured", r["jd_ratio_meas"]), ("gapOnly", r["jd_ratio_gap_only"])):
        worst[key] = rel(page["constants"][key], value)
    return worst, counts_differ


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cases", type=int, default=300)
    args = ap.parse_args()
    worst, counts_differ = run(args.cases)
    for key, value in worst.items():
        print(f"{key:10s} largest relative difference {value:.2e}")
    print(f"lattice counts that differ: {counts_differ}")
    ok = max(worst.values()) <= TOLERANCE and counts_differ == 0
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
