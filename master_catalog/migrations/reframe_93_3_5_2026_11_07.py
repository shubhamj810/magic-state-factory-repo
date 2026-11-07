#!/usr/bin/env python3
"""One-off migration: store [[93,3,5]] in the frame where its gate is T0.T1.T2.

    python master_catalog/migrations/reframe_93_3_5_2026_11_07.py [--dry-run]

The small-d56 search's [[93,3,5]] (claim 1cf6fe71..., imported on 2026-11-07)
deposits T1.CS01.CS02.  The small-radical search's claim e16b7d73... is the
same circuit in another output basis, where the gate reads T0.T1.T2: one
GL(3,2) class, so the merge files it as a duplicate.  In the T frame the row
shows on the T-only frontier, so the coordinator asked for that frame to be
the stored one.

This script builds the catalogue row the e16b7d73 circuit would become
(`merge_results.candidate_row`, which verifies it), checks that
`merge_results.find_class` puts it in the class of the stored [[93,3,5]] row,
that n, N, d and A_d agree, and replaces the stored circuit by it with
`merge_results.improve`, which keeps the label and appends the new source.
The changed row passes `verify_catalog.verify_row` and the file-level checks
before anything is written.  Idempotent.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import catalogfile as CF                                          # noqa: E402
import constructions as CO                                        # noqa: E402
import distance_policy_2026_11_07 as DP                           # noqa: E402
import merge_results as MR                                        # noqa: E402
import verify_catalog as VC                                       # noqa: E402

#: The claim, copied from research/search2/small-radical/data/claims/ at 103594b.
CLAIM = (Path(__file__).resolve().parents[1] / "imports" / "2026-11-07_small_radical"
         / "e16b7d73.json")
DIGEST_PREFIX = "e16b7d73"


def record():
    c = json.loads(CLAIM.read_text())
    if CO.digest(c["columns"]) != c["sha256"] or not c["sha256"].startswith(DIGEST_PREFIX):
        raise SystemExit("the claim's columns do not have its digest")
    return {"k": c["k"], "N": c["N"], "n": c["n"], "columns": c["columns"], "d": 5,
            "regime": "AI search: invariant radical growth",
            "strength": ("grown by exact invariant radical growth on a triorthogonal "
                         "BCH-type check code, found by the catalogue's second-round "
                         "small-radical search of 7 November 2026, after the small-d56 "
                         "search; a verified witness, not a maximum"),
            "discovery": "AI search", "label": f"small-radical {c['sha256'][:10]}",
            "file": f"research/search2/small-radical/data/claims/{c['sha256']}.json "
                    f"(research branch, commit 103594b)",
            "origin": "research/search2/small-radical/REPORT.md: small-d56's [[93,3,5]] in its T frame",
            "provenance": "the same circuit as small-d56's 1cf6fe71 in another output basis"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load_all()
    rows = payload["factories"]
    rec = record()
    candidate, problems = MR.candidate_row(rec, payload, rec["file"], 0)
    if candidate is None:
        raise SystemExit(f"the T-frame circuit does not verify: {problems}")
    if MR.same_circuit(rows, candidate) is not None:
        print("the T-frame circuit is already stored; nothing to do")
        return 0
    held = MR.find_class(rows, candidate)
    if held is None:
        raise SystemExit("the T-frame circuit is in no class the catalogue holds")
    incumbent = rows[held]
    if not any("1cf6fe71" in str(s.get("label")) for s in incumbent["sources"]):
        raise SystemExit(f"it falls in {incumbent['catalog_label']}, not small-d56's row")
    for name in ("n", "k", "N", "d", "d_is_exact", "A_d"):
        if incumbent[name] != candidate[name]:
            raise SystemExit(f"{name}: {incumbent[name]} against {candidate[name]}")
    label = incumbent["catalog_label"]
    MR.improve(incumbent, candidate, payload["regimes"])
    _facts, problems = VC.verify_row(incumbent)
    print(f"  {label}: gate now {incumbent['gate_human']}"
          + (f": {problems}" if problems else ""))
    if problems:
        raise SystemExit("the changed row fails verification; nothing written")
    residue = (VC.duplicate_class_problems(rows) + VC.duplicate_label_problems(rows)
               + VC.provenance_problems(payload) + VC.citation_problems(payload)
               + VC.header_problems(payload))
    if residue:
        raise SystemExit(f"the catalogue fails a file-level check: {residue}")
    if args.dry_run or not DP._changes(payload):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write_all(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
