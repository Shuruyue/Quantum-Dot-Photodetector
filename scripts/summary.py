"""Compute every number used in the report → outputs/results.json."""
import json
import os

from _path import OUTPUTS

from qd_photodetector.summary import compute  # noqa: E402

if __name__ == "__main__":
    r = compute()
    os.makedirs(OUTPUTS, exist_ok=True)
    with open(os.path.join(OUTPUTS, "results.json"), "w", encoding="utf8") as f:
        json.dump(r, f, indent=1)
    for k, v in r.items():
        print(f"{k:24s} {v:.6g}")
