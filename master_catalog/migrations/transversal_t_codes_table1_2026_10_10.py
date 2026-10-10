#!/usr/bin/env python3
"""One-off migration: the rest of Jain and Albert's Table I.

    python master_catalog/migrations/transversal_t_codes_table1_2026_10_10.py [--dry-run]

`transversal_t_codes_2026_10_10.py` merged seventeen of the paper's codes and
left out ``[[417,1,13]]`` and the nine codes doubled from it: they need a
``[[69,1,13]]`` self-dual CSS code, which the paper takes from a ``[70,35,14]``
code that is only formally self-dual.  `transversal_t_codes/search_sd70.py`
then found what is actually needed -- a self-dual ``[70,35,12]`` code, with an
automorphism of order 23, whose words through its fixed coordinate all weigh at
least 14 -- and `build_codes.py` now builds all fifteen codes of Table I, with
exactly the paper's parameters: ``[[417,1,13]]``, ``[[575,1,15]]``,
``[[777,1,17]]``, ``[[983,1,19]]``, ``[[1317,1,21]]``, ``[[1651,1,23]]``,
``[[2033,1,25]]``, ``[[2415,1,27]]``, ``[[2813,1,29]]`` and ``[[3211,1,31]]``.

This runs the first migration's steps again on the extended
``transversal_t_codes/factories.json``: the merge (the seventeen codes already
held are duplicates; the ten new ones are accepted, credited to the paper, each
record noting where its ``[[69,1,13]]`` input comes from), then the paper's
distance as a certified lower bound and an explicit fault of that weight on
each new row, then full re-verification of every changed row.  A second run
writes nothing.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import transversal_t_codes_2026_10_10 as FIRST                     # noqa: E402

if __name__ == "__main__":
    raise SystemExit(FIRST.main())
