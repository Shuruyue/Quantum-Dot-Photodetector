"""All figures → docs/figures/."""
from _path import FIGURES

from quantum_dot_photodetector.plotting import make_all  # noqa: E402

if __name__ == "__main__":
    for p in make_all(FIGURES):
        print(p)
