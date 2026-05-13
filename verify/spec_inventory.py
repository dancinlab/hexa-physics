#!/usr/bin/env python3
"""hexa-physics verify/spec_inventory.py — 9-verb spec presence audit.

Bookkeeping only: confirms each declared verb's primary spec markdown is on disk
and carries the canonical extraction header. NOT a physics validation — the
specs are closed-form derivations applied from canon, not measured physics.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


# Each row: (verb, primary spec path relative to ROOT)
# All 9 verbs in hexa-physics are grounded engineering/physics applications of
# closed-form n=6 derivations. None are flagged speculative at v0.1.0.
VERB_TABLE = [
    ("computational-fluid-dynamics", "computational-fluid-dynamics/computational-fluid-dynamics.md"),
    ("crystallography",              "crystallography/crystallography.md"),
    ("crystallography-materials",    "crystallography-materials/crystallography-materials.md"),
    ("electromagnetism",             "electromagnetism/electromagnetism.md"),
    ("fluid",                        "fluid/fluid.md"),
    ("gravity-wave",                 "gravity-wave/gravity-wave.md"),
    ("light-optics",                 "light-optics/light-optics.md"),
    ("optics",                       "optics/optics.md"),
    ("thermodynamics",               "thermodynamics/thermodynamics.md"),
]
TOTAL_EXPECTED = 9


def evaluate() -> dict:
    rows = []
    for verb, relpath in VERB_TABLE:
        path = ROOT / relpath
        present = path.exists()
        if present:
            text = path.read_text(encoding="utf-8")
            lines = text.count("\n")
            has_h1 = bool(re.search(r"(?m)^#\s+\S", text))
            has_canonical = "@canonical" in text[:1024]
        else:
            lines = 0
            has_h1 = False
            has_canonical = False
        rows.append({
            "verb": verb,
            "path": relpath,
            "present": present,
            "lines": lines,
            "has_h1_header": has_h1,
            "has_canonical_header": has_canonical,
        })
    checks = {
        "all_9_present":               all(r["present"] for r in rows),
        "every_present_has_h1":        all(r["has_h1_header"] for r in rows if r["present"]),
        "every_present_has_canonical": all(r["has_canonical_header"] for r in rows if r["present"]),
        "verb_count_is_9":             len(rows) == TOTAL_EXPECTED,
    }
    return {
        "rows": rows,
        "total_present": sum(1 for r in rows if r["present"]),
        "total_expected": TOTAL_EXPECTED,
        "checks": checks,
        "all_ok": all(checks.values()),
    }


def _print_human(r: dict) -> int:
    print("=" * 80)
    print(f"  hexa-physics — 9-verb spec inventory  (closed-form spec catalog)")
    print("=" * 80)
    print(f"  {'verb':<32} {'lines':>6}  {'H1':>3}  {'@canon':>7}  path")
    print(f"  {'-'*32} {'-'*6}  {'-'*3}  {'-'*7}  {'-'*40}")
    for row in r["rows"]:
        h1 = "ok" if row["has_h1_header"] else "."
        canon = "ok" if row["has_canonical_header"] else "."
        if not row["present"]:
            print(f"  {row['verb']:<32} {'MISS':>6}  {'.':>3}  {'.':>7}  {row['path']}")
        else:
            print(f"  {row['verb']:<32} {row['lines']:>6}  {h1:>3}  {canon:>7}  {row['path']}")
    print()
    print(f"  present:  {r['total_present']}/{r['total_expected']}")
    for k, ok in r["checks"].items():
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {k}")
    print("=" * 80)
    if r["all_ok"]:
        print(f"  {r['total_present']}/{r['total_expected']} verb specs present.")
        return 0
    return 1


def main(argv) -> int:
    p = argparse.ArgumentParser(description="hexa-physics 9-verb spec inventory")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv[1:])
    r = evaluate()
    if args.json:
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return 0 if r["all_ok"] else 1
    return _print_human(r)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
