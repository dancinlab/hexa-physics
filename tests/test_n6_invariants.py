"""hexa-physics tests/test_n6_invariants.py — pytest wrapper for verify/n6_arithmetic.py."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from verify import n6_arithmetic  # noqa: E402


@pytest.mark.auto
def test_master_identity():
    ok, detail = n6_arithmetic.check_master()
    assert ok, detail


@pytest.mark.auto
def test_verb_count():
    ok, detail = n6_arithmetic.check_verb_count()
    assert ok, detail
    assert detail["count"] == 9


@pytest.mark.auto
def test_manifest_verb_count():
    ok, detail = n6_arithmetic.check_manifest_verb_count()
    assert ok, detail


@pytest.mark.auto
def test_limit_breakthrough_real_limits():
    ok, detail = n6_arithmetic.check_limit_breakthrough_real_limits()
    assert ok, detail


@pytest.mark.auto
def test_no_lattice_fit_on_external_constants():
    ok, detail = n6_arithmetic.check_no_lattice_fit_on_external_constants()
    assert ok, detail
