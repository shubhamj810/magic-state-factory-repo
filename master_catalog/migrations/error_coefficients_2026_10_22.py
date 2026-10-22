#!/usr/bin/env python3
"""One-off migration: give every row its leading error coefficient ``A_d``.

    python master_catalog/migrations/error_coefficients_2026_10_22.py [--dry-run]

``A_d`` is the number of weight-``d`` faults that the checks accept and that
damage the output: an accepted run fails with probability ``A_d p^d +
O(p^(d+1))`` when each rotation fails with probability ``p``.  The 15-to-1
factory has ``A_3 = 35``, the 8-``T`` ``CCZ`` factory ``A_2 = 28``.
`errorcoeff.py` counts it exactly, as accepted faults less harmless ones, each
by the MacWilliams identity or by enumeration, and checks the difference
against a direct enumeration of the harmful faults wherever that finishes.

The field goes in after ``d_witness``, where `merge_results` puts it on a new
row.  It is ``null`` on a floor (``d_is_exact`` false), where the lighter
weights are not all proved clean and there is no leading coefficient, and on
the exact rows neither method reaches.  The header's ``verification`` sentence
gains the new check.  Re-running it on a migrated file changes nothing.
"""
from __future__ import annotations

import argparse
import collections
import multiprocessing as mp
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import catalogfile as CF                                          # noqa: E402
import errorcoeff as EC                                           # noqa: E402

AFTER = "d_witness"
VERIFICATION_TAIL = ("or the proof that none do")
ADDED = (", and the leading error coefficient A_d -- the number of weight-d "
         "faults the checks accept and the outputs do not survive -- recounted "
         "as accepted less harmless faults and, where it finishes, by direct "
         "enumeration")


def count(row):
    if not row["d_is_exact"]:
        return row["catalog_label"], None, None
    result = EC.error_coefficient(row["columns"], row["k"], row["N"], row["d"])
    return row["catalog_label"], result["count"], result


def with_field(row, value):
    out = {}
    for key, item in row.items():
        if key == "A_d":
            continue
        out[key] = item
        if key == AFTER:
            out["A_d"] = value
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--workers", type=int, default=min(12, mp.cpu_count()))
    args = parser.parse_args(argv)
    payload = CF.load()
    started = time.time()
    rows = payload["factories"]
    # widest first, so the slow counts start early
    order = sorted(rows, key=lambda r: -r["n"])
    with mp.Pool(args.workers) as pool:
        results = {label: (value, detail) for label, value, detail
                   in pool.imap_unordered(count, order, chunksize=1)}
    changed = 0
    tally = collections.Counter()
    for position, row in enumerate(rows):
        value, detail = results[row["catalog_label"]]
        new = with_field(row, value)
        if new != row or list(new) != list(row):
            changed += 1
        rows[position] = new
        tally["floor" if not row["d_is_exact"] else
              "not reached" if value is None else
              "counted twice" if detail["direct"] is not None else
              "counted"] += 1
    verification = payload["verification"]
    if ADDED not in verification and verification.endswith(VERIFICATION_TAIL):
        payload["verification"] = verification + ADDED
        changed += 1
    print(f"{len(rows)} rows in {time.time() - started:.0f}s: "
          + ", ".join(f"{kind}: {n}" for kind, n in sorted(tally.items())))
    if args.dry_run or not changed:
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write(payload)
    print(f"wrote master_catalog.json and MASTER_CATALOG.md ({changed} changes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
