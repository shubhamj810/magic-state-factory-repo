#!/usr/bin/env python3
"""One-off migration: exact A_d, counted by the research's tools, on the rows
imported from the searches of 6 and 7 November 2026.

    python master_catalog/migrations/import_counts_2026_11_07.py [--dry-run]

The merge counts ``A_d`` with `errorcoeff` and stores ``null`` where neither
of its methods reaches.  For such a row, an evidence file listed in
`FILES` may hold an exact count of the harmful faults of weight ``d`` for
its circuit, bound by the SHA-256 of the stored columns.  This script writes
that count as ``A_d`` with an ``A_d_evidence`` entry per tool.  A row that
already has an ``A_d`` must agree with every record, or nothing is written.

Every changed row passes `verify_catalog.verify_row` (which recounts wherever
`errorcoeff` reaches and otherwise checks the evidence), the file-level checks
pass, and only then is anything written.  Idempotent.
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

FILES = ("round1_certificates/coefficients.json",
         "round2_certificates/weighted_coefficients.json")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load_all()
    counts = []
    for path in FILES:
        records, problem = VC.coefficient_records(path)
        if problem:
            raise SystemExit(problem)
        counts += [dict(r, file=path) for r in records]
    changed = []
    for row in payload["factories"]:
        if not row["d_is_exact"]:
            continue
        digest = CO.digest(row["columns"])
        mine = [c for c in counts if c["columns_sha256"] == digest
                and c["weight"] == row["d"]]
        if not mine:
            continue
        values = {c["count"] for c in mine}
        if len(values) != 1 or (row["A_d"] is not None and row["A_d"] not in values):
            raise SystemExit(f"{row['catalog_label']}: the counts disagree: "
                             f"{sorted(values)} against A_d={row['A_d']}")
        listed = list(row.get("A_d_evidence") or [])
        for c in mine:
            entry = {"file": c["file"], "tool": c["tool"]}
            if entry not in listed:
                listed.append(entry)
        if row["A_d"] == values.copy().pop() and listed == row.get("A_d_evidence"):
            continue
        row["A_d"] = values.pop()
        row["A_d_evidence"] = listed
        changed.append(row)
    for row in changed:
        started = time.time()
        _facts, problems = VC.verify_row(row)
        print(f"  {row['catalog_label']}: A_d = {row['A_d']} from "
              f"{len(row['A_d_evidence'])} record(s); verified in "
              f"{time.time() - started:.0f}s" + (f": {problems}" if problems else ""),
              flush=True)
        if problems:
            raise SystemExit("a changed row fails verification; nothing written")
    rows = payload["factories"]
    residue = [p for row in rows for p in VC.certificate_problems(row)]
    residue += (VC.duplicate_label_problems(rows) + VC.provenance_problems(payload)
                + VC.citation_problems(payload) + VC.header_problems(payload))
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the catalogue fails a file-level check; nothing written")
    print(f"{len(changed)} row(s) changed")
    if args.dry_run or not DP._changes(payload):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write_all(payload)
    VC.persist_metric_cache()
    print("wrote master_catalog.json, master_catalog_large.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
