#!/usr/bin/env python3
"""One-off migration: move the four longest main-file rows to the large file.

    python master_catalog/migrations/explicit_storage_2026_11_07.py [--dry-run]

The imports of 2026-11-07 took `master_catalog.json` past GitHub's
recommended 50 MB.  The four gamma frontier rows 1675.373.4.a, 1676.372.4.a,
1683.365.4.a and 1715.287.6.a hold 4.3 MB of it and have no construction rule.
They move to `master_catalog_large.json` as ``explicit`` constructions
(`constructions.explicit`: the same columns, in the same order, compressed),
with ``columns_sha256`` pinning them.  Nothing about the circuits changes:
``d_witness`` and ``rotation_powers`` count in the same order.  Every moved row
passes `verify_catalog.verify_row`, which rebuilds the columns from the rule
and checks the digest, before anything is written.  Idempotent.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import catalogfile as CF                                          # noqa: E402
import constructions as CO                                        # noqa: E402
import distance_policy_2026_11_07 as DP                           # noqa: E402
import verify_catalog as VC                                       # noqa: E402

MOVE = ("1675.373.4.a", "1676.372.4.a", "1683.365.4.a", "1715.287.6.a")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load_all()
    moved = []
    for i, row in enumerate(payload["factories"]):
        if row["catalog_label"] not in MOVE or CF.is_large(row):
            continue
        rule = CO.explicit(row["columns"], row["k"], row["N"])
        if CO.columns(rule) != row["columns"]:
            raise SystemExit(f"{row['catalog_label']}: the rule does not rebuild it")
        new = {}
        for key, value in row.items():          # storage fields after columns
            new[key] = value
            if key == "columns":
                new["construction"] = rule
                new["columns_sha256"] = CO.digest(row["columns"])
        payload["factories"][i] = new
        moved.append(new)
    for row in moved:
        started = time.time()
        _facts, problems = VC.verify_row(row)
        print(f"  {row['catalog_label']} moved; verified in {time.time() - started:.0f}s"
              + (f": {problems}" if problems else ""))
        if problems:
            raise SystemExit("a moved row fails verification; nothing written")
    rows = payload["factories"]
    main = sorted((r for r in rows if not CF.is_large(r)), key=DP.MR.sort_key)
    large = sorted((r for r in rows if CF.is_large(r)), key=DP.MR.sort_key)
    payload["factories"] = main + large
    print(f"{len(moved)} row(s) moved")
    if args.dry_run or not DP._changes(payload):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write_all(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
