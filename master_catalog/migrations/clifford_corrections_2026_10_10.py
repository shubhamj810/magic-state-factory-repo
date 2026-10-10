#!/usr/bin/env python3
"""One-off migration: give every row its Clifford correction.

    python master_catalog/migrations/clifford_corrections_2026_10_10.py [--dry-run]

A row's ``gate`` names the level-3 part of the phase its rotations deposit; the
rest is a diagonal Clifford the factory must undo, after the rotations and
before the checks are measured, for the accepted action to be exactly that gate.
This adds two fields to every row, both derived from the columns by
`clifford.py` (see its docstring for the method -- the weight expansion of
Bravyi and Haah, PRA 86, 052329 (2012)):

* ``clifford_correction`` -- ``{"S": [[wire, p], ...], "CZ": [[q, r], ...]}``,
  ``S^p`` on each listed wire and ``CZ`` on each pair.  Unique.
* ``rotation_powers`` -- rotations to run as ``T^3``, ``T^5`` or ``T^7`` so
  that no correction is needed (``[]`` when none is needed anyway), or ``null``
  when no choice of powers avoids ``S`` or ``CZ`` gates.

They go in after ``d_witness``, where `merge_results` puts them on a new row,
so the key order of every row stays the one a merge would write.  The header's
``verification`` sentence gains the new check.  Nothing else changes.

Before anything is written, every row passes `verify_catalog.clifford_problems`
-- the literal comparison, the direct evaluation of the corrected logical
action, the re-proof of every ``null`` and, on small circuits, the gate-by-gate
statevector simulation.  Re-running it on a migrated file changes nothing.
"""
from __future__ import annotations

import argparse
import collections
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import catalogfile as CF                                          # noqa: E402
import clifford as CL                                             # noqa: E402
import faultcore as FC                                            # noqa: E402
import verify_catalog as VC                                       # noqa: E402

AFTER = "d_witness"
OLD_VERIFICATION_TAIL = ("and exact minimal T-count and CNOT-frame-reduced "
                         "degree where those are computable")
NEW_VERIFICATION_TAIL = (
    "exact minimal T-count and CNOT-frame-reduced degree where those are "
    "computable, and the Clifford correction that makes the accepted action "
    "exactly the gate (compared literally, then the corrected logical action "
    "evaluated directly, and simulated gate by gate on small circuits), with "
    "the rotation powers that avoid it or the proof that none do")


def fields(row):
    """``(clifford_correction, rotation_powers)`` for one row, from its columns."""
    columns, k, N = row["columns"], row["k"], row["N"]
    rows = FC.rows_over_columns(columns, N)
    gate = FC.recover_gate(rows, k)
    corr = CL.correction(rows, k, N, gate)
    return corr, CL.rotation_powers(rows, len(columns), N, corr), gate


def with_fields(row, corr, powers):
    """``row`` with the two fields placed right after ``d_witness``."""
    out = {}
    for key, value in row.items():
        if key in ("clifford_correction", "rotation_powers"):
            continue
        out[key] = value
        if key == AFTER:
            out["clifford_correction"] = corr
            out["rotation_powers"] = powers
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load()
    started = time.time()
    kinds = collections.Counter()
    changed = 0
    failures = []
    for position, row in enumerate(payload["factories"]):
        corr, powers, gate = fields(row)
        new = with_fields(row, corr, powers)
        if new != row or list(new) != list(row):
            changed += 1
        facts = {"n": len(row["columns"]), "k": row["k"], "N": row["N"],
                 "columns": row["columns"], "monomials": gate,
                 "clifford_correction": corr}
        problems = VC.clifford_problems(facts, new)
        if problems:
            failures.append((row["catalog_label"], problems))
        kinds[CF.correction_kind(new)] += 1
        payload["factories"][position] = new
    verification = payload["verification"]
    if OLD_VERIFICATION_TAIL in verification:
        payload["verification"] = verification.replace(
            ", " + OLD_VERIFICATION_TAIL, ", " + NEW_VERIFICATION_TAIL)
        changed += 1
    print(f"{len(payload['factories'])} rows in {time.time() - started:.0f}s: "
          + ", ".join(f"{kind}: {count}" for kind, count in sorted(kinds.items())))
    if failures:
        for label, problems in failures:
            for kind, detail in problems:
                print(f"  - {label}: {kind}: {detail}")
        raise SystemExit("a row failed its Clifford checks; nothing written")
    if args.dry_run or not changed:
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write(payload)
    print(f"wrote master_catalog.json and MASTER_CATALOG.md ({changed} changes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
