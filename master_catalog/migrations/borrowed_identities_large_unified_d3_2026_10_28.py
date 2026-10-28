#!/usr/bin/env python3
"""One-off migration: merge the distance-3 rows of the larger unified search.

    python master_catalog/migrations/borrowed_identities_large_unified_d3_2026_10_28.py [--dry-run]

The level-3 table of the larger unified borrowed-identity search (S. Singh, C.
Gidney and C. Jones, arXiv:2606.28518) has 37 single-output two-group rows at
distance 3 or more.  The table gives 12 of them ``d = 3`` and the other 25 only
the floor ``>=3``.  `borrowed_identities/export_large_unified.py` rebuilt and
checked all 37 and measured every one at exactly ``d = 3``; it wrote them to
``borrowed_identities/circuits/large_unified_l3_d3.json``.

This merges them exactly as `borrowed_identities_large_unified_2026_10_28`
merges the distance-2 rows, with the same storage bound and the same credit
rule: a new class is credited to the paper, a held one keeps its credit.  For
one output the class is ``(n, 1, d, T)``, so a row is new exactly when the
catalogue has no single-output class of its ``n`` at distance 3.
Re-running it changes nothing.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
CIRCUITS = "borrowed_identities/circuits/large_unified_l3_d3.json"

_spec = importlib.util.spec_from_file_location(
    "base", HERE / "borrowed_identities_large_unified_2026_10_28.py")
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)


if __name__ == "__main__":
    raise SystemExit(base.main(circuits=CIRCUITS, description=__doc__))
