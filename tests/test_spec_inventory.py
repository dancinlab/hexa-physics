"""hexa-physics tests/test_spec_inventory.py — pytest wrapper for verify/spec_inventory.py."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from verify import spec_inventory  # noqa: E402


@pytest.mark.auto
def test_inventory_all_ok():
    r = spec_inventory.evaluate()
    assert r["all_ok"], f"inventory not clean: {r}"
    assert r["total_present"] == r["total_expected"] == 9


@pytest.mark.auto
def test_inventory_every_present_has_h1_and_canonical():
    r = spec_inventory.evaluate()
    for row in r["rows"]:
        if row["present"]:
            assert row["has_h1_header"], row
            assert row["has_canonical_header"], row
