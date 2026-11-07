#!/usr/bin/env python3
"""One-off migration: a floor ``d >= w`` that the sweep proves, made exact by a
fault of weight ``w`` the research found ([[218,5,7]] and [[708,58,6]]).

    python master_catalog/migrations/research_faults_2026_11_07.py [--dry-run]

The merge stores the floor its own sweep proves, and stores a fault only when
its sweep finds one within budget.  For [[218,5,7]] (small-d7 search,
21a281ee..., imported on 2026-11-07) the sweep proves ``d >= 7`` and finds no
fault of weight 7 within its budget; the research found one, re-checked there
with faultcore and by the XOR of the wire masks (research/search2/small-d7/
data/claimed_factories.json at b873a70).  `FAULTS` lists it by the SHA-256 of
the stored columns.  For each listed row that is a plain floor at that weight,
this script re-checks the fault both ways, makes ``d`` exact with the fault as
``d_upper`` and ``d_witness``, and counts ``A_d`` with `errorcoeff` (``null``
where it does not reach).  Every changed row passes `verify_catalog.verify_row`
before anything is written.  Idempotent.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import catalogfile as CF                                          # noqa: E402
import constructions as CO                                        # noqa: E402
import distance_policy_2026_11_07 as DP                           # noqa: E402
import errorcoeff as EC                                           # noqa: E402
import faultcore as FC                                            # noqa: E402
import verify_catalog as VC                                       # noqa: E402

FAULTS = {
    # [[218,5,7]], small-d7, research/search2/small-d7/data/claimed_factories.json
    # (label c223_218_5_7 there), the fault in the stored column order
    "21a281eea9346dd1fb3293e3567f1a54cabfb7dbc9537795f0ebffc5fc05176b":
        [0, 6, 76, 85, 113, 128, 133],
    # [[708,58,6]], small-cyc, research/search2/small-cyc/data/claims.jsonl at
    # 27ac40e (name c766_708_58_6, witness_D), the same column order
    "b193fae92c64d79fd18dab74a0c142dfa2d1dcc26d8d41cab2a7962edee2f667":
        [0, 58, 182, 298, 505, 639],
}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load_all()
    changed = []
    for row in payload["factories"]:
        digest = CO.digest(row["columns"])
        if digest not in FAULTS or row["d_is_exact"] or "d_certified" in row:
            continue
        fault = sorted(FAULTS[digest])
        acc = 0
        for j in fault:
            for q in row["columns"][j]:
                acc ^= 1 << q
        literal = acc != 0 and (acc >> row["k"]) == 0
        if len(fault) != row["d"] or not literal \
                or not FC.Circuit(row["columns"], row["k"], row["N"]).harmful(fault):
            raise SystemExit(f"{row['catalog_label']}: the fault does not hold")
        row["d_is_exact"] = True
        row["d_upper"], row["d_witness"] = row["d"], fault
        row["A_d"] = EC.error_coefficient(row["columns"], row["k"], row["N"],
                                          row["d"])["count"]
        changed.append(row)
    for row in changed:
        _facts, problems = VC.verify_row(row)
        print(f"  {row['catalog_label']}: d = {row['d']} exact, A_d {row['A_d']}"
              + (f": {problems}" if problems else ""))
        if problems:
            raise SystemExit("a changed row fails verification; nothing written")
    print(f"{len(changed)} row(s) changed")
    if args.dry_run or not DP._changes(payload):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write_all(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
