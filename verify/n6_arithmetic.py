#!/usr/bin/env python3
"""hexa-physics verify/n6_arithmetic.py — n=6 lattice + LATTICE_POLICY compliance.

These checks verify INTERNAL bookkeeping only:
  - the n=6 number-theoretic identities the README advertises
    (sigma(6)=12, tau(6)=4, phi(6)=2, J2(6)=24) are mathematically correct;
  - the manifest declares 9 verbs and references real (not lattice-fit)
    physical limits in LIMIT_BREAKTHROUGH.md per LATTICE_POLICY.md §1.2.

The lattice identities are tautologies of elementary number theory; they are
NOT physics. The "real-limits" check guards LATTICE_POLICY compliance: the
project must verify against physical/mathematical/engineering ceilings
(c, h-bar, k, Carnot, Stefan-Boltzmann, ...) rather than against
lattice-tautology fits.
"""
from __future__ import annotations

import sys
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

N, SIGMA_N, TAU_N, PHI_N, J2 = 6, 12, 4, 2, 24
EXPECTED_VERB_COUNT = 9


def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


def sigma(n):
    return sum(divisors(n))


def tau(n):
    return len(divisors(n))


def euler_phi(n):
    return sum(1 for k in range(1, n + 1) if gcd(k, n) == 1)


def jordan_J2(n):
    # J_2(n) = n^2 * prod_{p | n} (1 - 1/p^2)
    pr = 1
    seen = set()
    m = n
    p = 2
    while p * p <= m:
        if m % p == 0:
            if p not in seen:
                pr *= (1 - 1.0 / (p * p))
                seen.add(p)
            m //= p
        else:
            p += 1
    if m > 1 and m not in seen:
        pr *= (1 - 1.0 / (m * m))
    return int(round(n * n * pr))


def check_master() -> tuple[bool, dict]:
    s, t, p = sigma(N), tau(N), euler_phi(N)
    j2 = jordan_J2(N)
    ok = (s * p == J2) and (N * t == J2) and (j2 == J2)
    return ok, {
        "sigma(6)":     s,
        "tau(6)":       t,
        "phi(6)":       p,
        "J2(6)":        j2,
        "sigma*phi":    s * p,
        "n*tau":        N * t,
        "expected J2":  J2,
    }


def check_verb_count() -> tuple[bool, dict]:
    verbs = [
        "computational-fluid-dynamics", "crystallography",
        "crystallography-materials", "electromagnetism", "fluid",
        "gravity-wave", "light-optics", "optics", "thermodynamics",
    ]
    return len(verbs) == EXPECTED_VERB_COUNT, {
        "verbs":  verbs,
        "count":  len(verbs),
    }


def check_manifest_verb_count() -> tuple[bool, dict]:
    """hexa.toml [verbs] section must list exactly 9 verbs."""
    tf = ROOT / "hexa.toml"
    if not tf.exists():
        return False, {"error": "hexa.toml missing"}
    text = tf.read_text(encoding="utf-8")
    if "[verbs]" not in text:
        return False, {"error": "[verbs] section missing"}
    section = text.split("[verbs]", 1)[1].split("\n[", 1)[0]
    verb_lines = [
        ln for ln in section.splitlines()
        if ln.strip() and not ln.strip().startswith("#") and "=" in ln
    ]
    return len(verb_lines) == EXPECTED_VERB_COUNT, {
        "declared_verbs": len(verb_lines),
        "expected":       EXPECTED_VERB_COUNT,
    }


def check_lattice_policy_present() -> tuple[bool, dict]:
    """LATTICE_POLICY.md must be present per dancinlab Wave K."""
    f = ROOT / "LATTICE_POLICY.md"
    if not f.exists():
        return False, {"error": "LATTICE_POLICY.md missing"}
    text = f.read_text(encoding="utf-8")
    return "real-limits" in text.lower() or "real limits" in text.lower(), {
        "path":         "LATTICE_POLICY.md",
        "size_bytes":   f.stat().st_size,
    }


def check_limit_breakthrough_real_limits() -> tuple[bool, dict]:
    """LIMIT_BREAKTHROUGH.md must reference real physical limits (LATTICE_POLICY §1.2).

    Per raw#10 C3: NIST constants must be NIST values, NOT lattice projections.
    We check that the audit references constants by their canonical names
    AND cites NIST/CODATA/PDG sources, rather than deriving them from sigma/tau/phi.
    """
    f = ROOT / "LIMIT_BREAKTHROUGH.md"
    if not f.exists():
        return False, {"error": "LIMIT_BREAKTHROUGH.md missing"}
    text = f.read_text(encoding="utf-8")
    # Real limits per LATTICE_POLICY §1.2 that should appear in this audit:
    required_real_limits = [
        "Speed of light", "Planck", "Heisenberg", "Carnot",
        "Stefan-Boltzmann", "Bekenstein", "Shannon", "Landauer",
    ]
    missing = [name for name in required_real_limits if name not in text]
    # Honest-source attribution:
    sources = ["NIST", "CODATA", "PDG"]
    has_source = any(s in text for s in sources)
    # Must NOT claim NIST constants are derived from n=6 lattice
    # (raw#10 C3: external entities use their own invariants)
    forbidden = [
        "c = sigma",      # ascii lattice-derive of c
        "c = σ",          # unicode lattice-derive of c
        "hbar = sigma",
        "ℏ = σ",
        "k = sigma",
    ]
    bad = [s for s in forbidden if s in text]
    ok = (len(missing) == 0) and has_source and (len(bad) == 0)
    return ok, {
        "required_limits_present":  len(required_real_limits) - len(missing),
        "required_limits_total":    len(required_real_limits),
        "missing_limits":           missing,
        "has_authoritative_source": has_source,
        "forbidden_lattice_fits":   bad,
    }


def check_no_lattice_fit_on_external_constants() -> tuple[bool, dict]:
    """raw#10 C3 honesty: NIST fundamental constants must not be claimed as
    lattice-derived in LIMIT_BREAKTHROUGH.md or LATTICE_POLICY.md.

    We look for explicit disclaimers and absence of equating NIST constants
    with sigma(6) / tau(6) / phi(6) projections.
    """
    f_lb = ROOT / "LIMIT_BREAKTHROUGH.md"
    f_lp = ROOT / "LATTICE_POLICY.md"
    if not (f_lb.exists() and f_lp.exists()):
        return False, {"error": "limit/policy docs missing"}
    lb = f_lb.read_text(encoding="utf-8")
    lp = f_lp.read_text(encoding="utf-8")
    # LIMIT_BREAKTHROUGH should explicitly disclaim lattice anchoring
    lb_disclaim = "lattice" in lb.lower() and (
        "no n=6 lattice anchoring" in lb.lower()
        or "no n=6 anchoring" in lb.lower()
        or "deliberately avoids n=6" in lb.lower()
    )
    # LATTICE_POLICY must distinguish native invariant vs self-imposed ceiling
    lp_distinguishes = "native invariant" in lp.lower() or "native-lattice" in lp.lower()
    return lb_disclaim and lp_distinguishes, {
        "limit_breakthrough_disclaims_lattice": lb_disclaim,
        "lattice_policy_distinguishes_usage":   lp_distinguishes,
    }


CHECKS = [
    ("master identity   sigma*phi = n*tau = J2 = 24", check_master),
    ("verb_count = 9 (physics rollup)",                check_verb_count),
    ("hexa.toml declares 9 verbs",                     check_manifest_verb_count),
    ("LATTICE_POLICY.md present + real-limits-first",  check_lattice_policy_present),
    ("LIMIT_BREAKTHROUGH.md cites real limits + NIST", check_limit_breakthrough_real_limits),
    ("no n=6 lattice-fit on NIST constants (raw#10 C3)", check_no_lattice_fit_on_external_constants),
]


def main() -> int:
    print("=" * 78)
    print("  hexa-physics — n=6 lattice arithmetic + LATTICE_POLICY compliance")
    print("=" * 78)
    passed = 0
    for name, fn in CHECKS:
        ok, detail = fn()
        mark = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        print(f"  [{mark}] {name}")
        for k, v in detail.items():
            print(f"         . {k}: {v}")
    print("=" * 78)
    print(f"  {passed}/{len(CHECKS)} PASS")
    return 0 if passed == len(CHECKS) else 1


if __name__ == "__main__":
    sys.exit(main())
