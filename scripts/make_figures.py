"""All figures → docs/figures/."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from qd_photodetector.plotting import make_all  # noqa: E402

if __name__ == "__main__":
    for p in make_all("docs/figures"):
        print(p)
