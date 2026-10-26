#!/usr/bin/env python3
"""One-off migration: merge the unified borrowed-identity search.

    python master_catalog/migrations/borrowed_identities_unified_2026_10_26.py [--dry-run]

In October 2026 the Borrowed Identities repository (S. Singh, C. Gidney and
C. Jones, arXiv:2606.28518) replaced its per-level catalogues with the tables
of one unified search, copied into ``borrowed_identities/upstream_unified/``.
`borrowed_identities/export_unified.py` rebuilt and checked an explicit circuit
for every level-3 row of ``all_factories.csv``, of ``large_sweep.csv`` up to
``n = 4095`` inputs, and of ``l3_k78_targets.csv``, and wrote them to
``borrowed_identities/circuits/factories_unified_l3.json``.  This merges that
file through `merge_results.merge`, the same bar as every merge.

Credit: a class the merge adds is credited to the paper.  A class the catalogue
already holds keeps exactly the credit it had: the merge would append the
paper to it, as it does for any citation a record names, and this migration
puts the old list back.  The first import's rule still holds for those --
each such class cites the earliest work that published it -- and the unified
tables, released in October 2026, are not earlier than any of them.

The Clifford-padding rows, a smaller factory's outputs spread over more wires
by a CNOT relabelling, are refused as pseudo-outputs: an output that equals a
combination of others modulo the checks is one logical qubit wearing two
labels in this catalogue's terms, as the first import's ``[[8,4,2]]`` was.
Re-running it on a migrated file changes nothing.
"""
from __future__ import annotations

import argparse
import collections
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE.parent
REPO = CATALOGUE.parent
sys.path.insert(0, str(CATALOGUE))

import catalogfile as CF                                          # noqa: E402
import merge_results as MR                                        # noqa: E402
import verify_catalog as VC                                       # noqa: E402

RESULTS = "borrowed_identities/circuits/factories_unified_l3.json"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load()
    before = len(payload["factories"])
    credit = {row["catalog_label"]: list(row["citations"])
              for row in payload["factories"]}
    records = MR.read_records(REPO / RESULTS)
    verdicts = MR.merge(payload, records, RESULTS)
    restored = 0
    for row in payload["factories"]:
        old = credit.get(row["catalog_label"])
        if old is not None and row["citations"] != old:
            row["citations"] = old
            restored += 1
    tally = collections.Counter(verdict for _i, verdict, _row, _d in verdicts)
    reasons = collections.Counter(kind for _i, verdict, _row, problems in verdicts
                                  if verdict == "rejected"
                                  for kind, _detail in problems)
    print(f"{len(records)} results: " + ", ".join(
        f"{n} {v}" for v, n in sorted(tally.items()))
        + f"; refused as {dict(reasons)}; credit restored on {restored} held "
          f"row(s); {before} -> {len(payload['factories'])} classes")
    residue = (VC.duplicate_class_problems(payload["factories"])
               + VC.provenance_problems(payload)
               + VC.citation_problems(payload)
               + VC.header_problems(payload))
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the merged catalogue fails a file-level check; "
                         "nothing written")
    # a re-run re-adds the paper to held rows and takes it off again, so what
    # decides whether anything changed is the text, not the counters
    if args.dry_run or CF.serialise(payload) == CF.CATALOG_JSON.read_text(
            encoding="utf-8"):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write(payload)
    VC.persist_metric_cache()
    print("wrote master_catalog.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
