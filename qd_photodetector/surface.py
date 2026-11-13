"""Fraction of atoms at the surface of a spherical PbS (rock-salt) quantum dot.

Rock salt places Pb and S on a simple-cubic lattice of spacing h = a/2, each atom with six nearest
neighbours of the other kind. An atom is counted as a surface atom when fewer than six of its
neighbours lie inside the sphere.

Two independent implementations of the count are provided:

* ``count_sites``       – vectorised occupancy grid (used for all results)
* ``count_sites_naive`` – explicit set of lattice points with a neighbour loop (cross-check)

Because the count depends on where the sphere centre sits on the lattice, results are averaged over
the two high-symmetry centrings: on an atom, and at the centre of a cube of atoms.

``shell_fraction`` is the continuum estimate for a surface layer one Pb–S distance (a/2) thick.
"""
import numpy as np

from . import data as D

H = D.A_PBS / 2  # nm, Pb–S nearest-neighbour distance
CENTRINGS = {"atom": 0.0, "interstitial": 0.5}
_NEIGHBOURS = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))


def count_sites(d, centring="atom"):
    """Return (atoms inside the sphere, surface atoms) for diameter d in nm."""
    R = d / 2
    n = int(np.ceil(R / H)) + 2
    g = np.arange(-n, n + 1, dtype=float) + CENTRINGS[centring]
    r2 = (g[:, None, None] ** 2 + g[None, :, None] ** 2 + g[None, None, :] ** 2) * H**2
    occ = r2 <= R**2 + 1e-12
    full = occ.copy()
    for axis in range(3):           # the grid has an empty border, so np.roll never wraps an atom
        full &= np.roll(occ, 1, axis)
        full &= np.roll(occ, -1, axis)
    return int(occ.sum()), int((occ & ~full).sum())


def count_sites_naive(d, centring="atom"):
    """Same count with an explicit set of integer lattice points (slow; for checking)."""
    R = d / 2
    s = CENTRINGS[centring]
    n = int(np.ceil(R / H)) + 2
    inside = set()
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            for k in range(-n, n + 1):
                if ((i + s) ** 2 + (j + s) ** 2 + (k + s) ** 2) * H**2 <= R**2 + 1e-12:
                    inside.add((i, j, k))
    surf = sum(1 for (i, j, k) in inside
               if any((i + a, j + b, k + c) not in inside for a, b, c in _NEIGHBOURS))
    return len(inside), surf


def surface_fraction(d):
    """Surface-atom fraction from the atom count, averaged over both centrings."""
    out = []
    for c in CENTRINGS:
        N, s = count_sites(d, c)
        out.append(s / N)
    return float(np.mean(out))


def shell_fraction(d, thickness=None):
    """Continuum shell model f = 1 − (1 − 2t/d)³ with t = a/2 by default."""
    t = H if thickness is None else thickness
    return float(1 - (1 - 2 * t / d) ** 3)


def mean_max_direction_cosine(n=400_000):
    """E[max(|nx|, |ny|, |nz|)] for directions uniform on the unit sphere (Fibonacci lattice).

    On a simple-cubic lattice a facet with unit normal n exposes max|n_i|/h² surface sites per unit
    area, so for large dots the counted fraction tends to 6 h E[max|n_i|]/d.
    """
    i = np.arange(n) + 0.5
    z = 1 - 2 * i / n
    r = np.sqrt(1 - z * z)
    phi = np.pi * (1 + 5**0.5) * i
    v = np.stack([r * np.cos(phi), r * np.sin(phi), z], 1)
    return float(np.abs(v).max(1).mean())


def curve(d_values):
    """Rows (d, counted fraction, shell fraction) for plotting."""
    return [(float(d), surface_fraction(d), shell_fraction(d)) for d in d_values]
