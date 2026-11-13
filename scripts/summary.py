"""Compute every number used in the report → outputs/results.json."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from qd_photodetector.summary import compute  # noqa: E402

if __name__ == "__main__":
    r = compute()
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/results.json", "w") as f:
        json.dump(r, f, indent=1)
    for k, v in r.items():
        print(f"{k:24s} {v:.6g}")
