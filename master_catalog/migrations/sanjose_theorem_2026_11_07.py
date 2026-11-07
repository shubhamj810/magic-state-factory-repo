#!/usr/bin/env python3
"""One-off migration: San Jose's theorem, checked from the columns, on the two
catalogue rows of his construction.

    python master_catalog/migrations/sanjose_theorem_2026_11_07.py [--dry-run]

742.36.8.a and 756.32.6.a came in from the gamma frontier release.  Their
columns are San Jose's GRS construction (arXiv:2609.08203) over GF(64), outer
length 62, degree 15, punctured at P = 9 and P = 8 coordinates
(`theorem_certificates/inputs.json`, names sj_m6_L62_deg15_P9 and _P8), so
the theorem gives d >= 17 - P.  `theorem_certificates/assemble.py` runs
`construction_sanjose.hypothesis_check` on the stored columns, which proves
8 and 9, and re-checks the research's fault of that weight.

* 756.32.6.a: its certificate d >= 9 sat beside the sweep's floor 6, because
  only the release stated it.  It now rests on the checked theorem and the
  fault of weight 9, so by the rule of `distance_policy_2026_11_07.py` d
  becomes 9, exact; the floor goes to ``d_sweep_floor`` and the row becomes
  756.32.9.a, keeping its old label in ``former_labels``.
* 742.36.8.a: its d = 8 already rests on a certificate; the theorem record is
  added to its evidence.

Every changed row passes `verify_catalog.verify_row`, the file-level checks
pass over both files, and only then is anything written.  Idempotent.
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

EVIDENCE = "theorem_certificates/certificates.json"
PROMOTE = "756.32.6.a"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load_all()
    records, problem = VC.evidence_records(EVIDENCE)
    if problem:
        raise SystemExit(problem)
    rows = payload["factories"]
    changed = []
    for row in rows:
        digest = CO.digest(row["columns"])
        mine = [r for r in records if r["columns_sha256"] == digest]
        if not mine:
            continue
        (record,) = mine
        entry = {"file": EVIDENCE, "method": record["method"], "tool": record["tool"]}
        old = row["catalog_label"]
        if old == PROMOTE:
            if record["lower_bound"] != row["d_certified"] or not record["exact"]:
                raise SystemExit(f"{PROMOTE}: the record does not state d = 9")
            floor = row["d"]
            row["d"] = row["d_certified"]
            row["d_is_exact"] = row["d_certified_is_exact"] = True
            row["d_upper"], row["d_witness"] = row["d"], sorted(record["witness"])
            row["d_sweep_floor"] = floor
            row["d_certified_evidence"] = [entry]
            row["d_certified_source"] += (
                "; since 2026-11-07 the row's d: the columns are San Jose's GRS "
                "construction (arXiv:2609.08203) over GF(64), L = 62, degree 15, "
                "P = 8, whose theorem gives d >= 9, its hypotheses checked from the "
                "columns (theorem_certificates/), and a fault of weight 9 found by "
                "the research's sparse-cells search and re-checked")
            row["former_labels"] = (row.get("former_labels") or []) + [old]
            row["catalog_label"] = CF.next_label(rows, row["n"], row["k"], row["d"])
            changed.append((old, row))
        elif CF.rests_on_certificate(row) and record["lower_bound"] == row["d"] \
                and entry not in row["d_certified_evidence"]:
            row["d_certified_evidence"].append(entry)
            changed.append((old, row))
    DP.resort(payload)
    for old, row in changed:
        started = time.time()
        _facts, problems = VC.verify_row(row)
        print(f"  {old} -> {row['catalog_label']}: d = {row['d']}, evidence "
              f"{[e['file'] for e in row['d_certified_evidence']]}; verified in "
              f"{time.time() - started:.0f}s" + (f": {problems}" if problems else ""))
        if problems:
            raise SystemExit("a changed row fails verification; nothing written")
    residue = [p for row in rows for p in VC.certificate_problems(row)]
    residue += [p for row in rows for p in VC.label_problems(row)]
    residue += (VC.duplicate_label_problems(rows) + VC.duplicate_class_problems(rows)
                + VC.provenance_problems(payload) + VC.citation_problems(payload)
                + VC.header_problems(payload))
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
