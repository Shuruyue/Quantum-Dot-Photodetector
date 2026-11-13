"""Run every check; exit code 1 if any fails.

    python scripts/validate.py              # table on stdout
    python scripts/validate.py --markdown   # also write VALIDATION.md and outputs/validation_table.json
"""
import json
import os
import sys
from dataclasses import asdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from qd_photodetector.validation import run_all, to_markdown  # noqa: E402

if __name__ == "__main__":
    rows = run_all()
    for c in rows:
        print(f"{c.num:3d} {'PASS' if c.passed else 'FAIL'}  {c.category}  {c.name}")
    ok = sum(c.passed for c in rows)
    print(f"{ok}/{len(rows)} checks passed")
    if "--markdown" in sys.argv:
        os.makedirs("outputs", exist_ok=True)
        with open("outputs/validation_table.json", "w", encoding="utf8") as f:
            json.dump([asdict(c) for c in rows], f, ensure_ascii=False, indent=1)
        with open("VALIDATION.md", "w", encoding="utf8") as f:
            f.write(to_markdown(rows))
    sys.exit(0 if ok == len(rows) else 1)
