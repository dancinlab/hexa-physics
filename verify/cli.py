#!/usr/bin/env python3
"""hexa-physics verify/cli.py — unified verifier dispatcher."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

VERIFY_DIR = Path(__file__).resolve().parent
ROOT = VERIFY_DIR.parent

CHECKS = [
    ("n6",        "n6_arithmetic.py",  "n=6 lattice + LATTICE_POLICY compliance"),
    ("inventory", "spec_inventory.py", "9-verb spec presence (closed-form catalog)"),
]


def _run_one(name, script, label):
    s = VERIFY_DIR / script
    if not s.exists():
        return {
            "name": name, "label": label, "ok": False, "exit_code": 2,
            "duration_s": 0.0, "stdout": "", "stderr": f"missing: {s}",
        }
    t0 = time.monotonic()
    rc = subprocess.run(
        [sys.executable, str(s)],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    return {
        "name": name, "label": label, "ok": rc.returncode == 0,
        "exit_code": rc.returncode,
        "duration_s": round(time.monotonic() - t0, 3),
        "stdout": rc.stdout, "stderr": rc.stderr,
    }


def main(argv):
    p = argparse.ArgumentParser(prog="verify/cli.py")
    p.add_argument("target", nargs="?", default="all")
    p.add_argument("--json", action="store_true")
    p.add_argument("--quiet", action="store_true")
    p.add_argument("--list", action="store_true")
    a = p.parse_args(argv[1:])
    if a.list:
        for n, s, l in CHECKS:
            ex = (VERIFY_DIR / s).exists()
            mark = "ok " if ex else "MISS"
            print(f"  [{mark}] {n:11s} -> verify/{s:24s}  {l}")
        return 0
    if a.target == "all":
        targets = [(n, s, l) for n, s, l in CHECKS]
    else:
        targets = [(n, s, l) for n, s, l in CHECKS if n == a.target]
        if not targets:
            print(f"unknown check: {a.target!r}", file=sys.stderr)
            return 2
    results = [_run_one(n, s, l) for n, s, l in targets]
    if a.json:
        n_ok = sum(1 for r in results if r["ok"])
        print(json.dumps({
            "tool": "hexa-physics verify/cli.py",
            "ok": n_ok == len(results),
            "checks_total": len(results),
            "checks_pass": n_ok,
            "results": results,
        }, indent=2, ensure_ascii=False))
        return 0 if n_ok == len(results) else 1
    print()
    for r in results:
        if not a.quiet:
            print("=" * 72)
            print(f"  > {r['name']}  -  {r['label']}")
            print("=" * 72)
            if r["stdout"]:
                print(r["stdout"].rstrip("\n"))
        verdict = "PASS" if r["ok"] else "FAIL"
        print(f"  [{verdict}] {r['name']:11s}  ({r['duration_s']:5.2f}s)  {r['label']}")
    n_ok = sum(1 for r in results if r["ok"])
    print("=" * 72)
    print(f"  {n_ok}/{len(results)} checks PASS")
    return 0 if n_ok == len(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
