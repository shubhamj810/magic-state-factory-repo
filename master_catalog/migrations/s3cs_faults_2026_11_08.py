#!/usr/bin/env python3
"""One-off migration: two s3-cs floors ``d >= 7`` that the sweep proves, made exact by a
fault of weight 7 the research found ([[217,6,7]] and [[319,8,7]]).

    python master_catalog/migrations/s3cs_faults_2026_11_08.py [--dry-run]

The merge of s3-cs's rows on 8 November 2026 stored [[217,6,7]] and [[319,8,7]]
as floors: its sweep proves ``d >= 7`` and finds no fault of weight 7 within its
budget. The research found one for each, re-checked there with faultcore and by
the XOR of the wire masks (research/search2/s3-cs/data/accepted/ at cfa81c0),
and it is re-checked here on the stored (relabelled) columns. The rule is that
of research_faults_2026_11_07.py: for each listed row that is a plain floor at
that weight, re-check the fault both ways, make ``d`` exact with the fault as
``d_upper`` and ``d_witness``, and count ``A_d`` with `errorcoeff` (``null``
where it does not reach). Every changed row passes `verify_catalog.verify_row`
before anything is written. Idempotent.
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
    # [[217,6,7]], s3-cs dec21502..., the research's witness in the stored column order
    "6479dec50a70537d5cddb7ad72692ffcb67c7915260a295bf8748ffa8870c54c":
        [0, 2, 50, 67, 86, 135, 178],
    # [[319,8,7]], s3-cs be100c07..., the same
    "3142c5e73198793970ac91ed9960b6231471db441841875d94d5fd001b018c04":
        [0, 1, 15, 107, 117, 134, 190],
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
