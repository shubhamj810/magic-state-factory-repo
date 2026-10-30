#!/usr/bin/env python3
"""One-off migration: merge Gong's chain continued by the Jain-Albert doubling.

    python master_catalog/migrations/gong_doubled_2026_10_30.py [--dry-run]

`gong_triply_even_2026_10_30.py` merged A. Gong's four codes, up to
``[[559,1,15]]``.  Doubling that code with the self-dual inputs Jain and Albert
use in their Table I from distance 17 on -- the ``[[101,1,17]]`` code of the
self-dual ``[102,51,18]`` code sub(XQ103), the ``[[103,1,19]]`` quantum QR code,
and the quantum QR codes of length 167, 191 and 199, twice each -- gives
``[[761,1,17]]``, ``[[967,1,19]]``, ``[[1301,1,21]]``, ``[[1635,1,23]]``,
``[[2017,1,25]]``, ``[[2399,1,27]]``, ``[[2797,1,29]]`` and ``[[3195,1,31]]``,
each 16 qubits shorter than the Table I code of the same distance.
`transversal_t_codes/build_codes.py` builds them as ``GJ-761`` ...
``GJ-3195``.  They are the paper's method applied to the codes in her
repository, so each row cites both works (``jain2025transversal`` and
``gong2025triply``), and its regime description and source say how it was
built.

This runs the same steps as that migration: the merge, then the doubling
theorem's distance as ``d_certified`` with an explicit fault of that weight,
then full re-verification of every changed row.  The codes are not triply
even (the ``[[101,1,17]]`` input is not doubly even), so the rows keep the
``rotation_powers`` the merge's solver finds.  The discovery glossary names the
new codes.  A second run writes nothing.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import gong_triply_even_2026_10_30 as GONG                          # noqa: E402

REGIME = "Jain-Albert doubling of Gong's codes"
DISCOVERY_OLD = ("the codes of Jain and Albert and of A. Gong rebuilt in "
                 "transversal_t_codes/")
DISCOVERY_NEW = ("the codes of Jain and Albert and of A. Gong rebuilt in "
                 "transversal_t_codes/ and the codes built there by doubling "
                 "hers with theirs")


def update_header(payload):
    glossary = payload["discovery"]
    if DISCOVERY_NEW in glossary["pre-existing"]:
        return []
    if DISCOVERY_OLD not in glossary["pre-existing"]:
        raise SystemExit("run gong_triply_even_2026_10_30.py first")
    glossary["pre-existing"] = glossary["pre-existing"].replace(
        DISCOVERY_OLD, DISCOVERY_NEW)
    return ["discovery glossary names the codes doubled from Gong's"]


if __name__ == "__main__":
    raise SystemExit(GONG.main(prefix="GJ-", regime=REGIME, triply_even=False,
                               header=update_header, description=__doc__))
