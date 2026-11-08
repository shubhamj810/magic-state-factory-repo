#!/usr/bin/env python3
"""One-off migration: no row's text says it is undominated.

    python master_catalog/migrations/record_wording_2026_11_07.py [--dry-run]

The owner's rule of 7 November 2026 (master_catalog/records.py): a direct sum
can be in the catalogue but is not a record, and a row is a record only when
no other row and no direct sum of rows of its gate class reaches its inputs,
outputs and distance. The 84 rows imported that day from the gamma frontier
release's San-José records carried, in their source's ``provenance``, the
words "sparse: release record, undominated": the research's sparse search had
found no single catalogue row dominating them on 6 November 2026. That check
did not count direct sums, and a stored "undominated" goes stale as rows come
in. The words become "sparse: release record"; whether a row is a record is
decided by records.py on the rows as they stand.

Only provenance changes. The file-level checks pass before anything is
written. Idempotent.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import catalogfile as CF                                          # noqa: E402
import distance_policy_2026_11_07 as DP                           # noqa: E402
import verify_catalog as VC                                       # noqa: E402

OLD = "sparse: release record, undominated"
NEW = "sparse: release record"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load_all()
    changed = []
    for row in payload["factories"]:
        for source in row["sources"]:
            text = source.get("provenance") or ""
            if OLD in text:
                source["provenance"] = text.replace(OLD, NEW)
                changed.append(row["catalog_label"])
    rows = payload["factories"]
    residue = (VC.duplicate_label_problems(rows) + VC.provenance_problems(payload)
               + VC.citation_problems(payload) + VC.header_problems(payload))
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the catalogue fails a file-level check; nothing written")
    print(f"{len(changed)} row(s) changed: {', '.join(changed)}")
    if args.dry_run or not DP._changes(payload):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write_all(payload)
    print("wrote master_catalog.json, master_catalog_large.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
