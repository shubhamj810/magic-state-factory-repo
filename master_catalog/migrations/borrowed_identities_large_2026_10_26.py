#!/usr/bin/env python3
"""One-off migration: the large-sweep circuits too long to store as columns.

    python master_catalog/migrations/borrowed_identities_large_2026_10_26.py [--dry-run]

`borrowed_identities_unified_2026_10_26.py` merged the unified borrowed-
identity search up to ``n = 4095`` inputs.  Its large sweep goes on to
``n = 65534``: 127 more level-3 two-group circuits, 1.7 million columns in
all, which would take ``master_catalog.json`` to about 99 MB, at GitHub's
100 MB hard limit on a file and twice its recommended 50 MB.  `borrowed_identities/export_unified.py` checked each of them on
the circuit the upstream code builds and wrote it as the two-group
construction that rebuilds it (``master_catalog/constructions.py``), in
``borrowed_identities/circuits/factories_unified_l3_large.json``.

This merges that file through `merge_results.merge`, the same bar as every
merge: the columns are rebuilt from each construction and the row is derived
and verified from them exactly as from stored columns.  An accepted row keeps
its construction and the SHA-256 of its columns, and `catalogfile.write_all`
writes it to ``master_catalog_large.json`` -- which this migration creates --
without the columns.  Each new class is credited to the paper; the large-sweep
table names no earlier work.  Re-running it changes nothing.
"""
from __future__ import annotations

import argparse
import collections
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE.parent
REPO = CATALOGUE.parent
sys.path.insert(0, str(CATALOGUE))

import catalogfile as CF                                          # noqa: E402
import merge_results as MR                                        # noqa: E402
import verify_catalog as VC                                       # noqa: E402

RESULTS = "borrowed_identities/circuits/factories_unified_l3_large.json"


def _changes(payload):
    """Whether writing ``payload`` would change any of the three files."""
    real = (CF.CATALOG_JSON, CF.CATALOG_LARGE_JSON, CF.CATALOG_MD)
    with tempfile.TemporaryDirectory() as scratch:
        trial = [Path(scratch) / path.name for path in real]
        if real[1].exists():
            # `write_all` rewrites an existing large file even with no rows to
            # put in it, so the trial must start with one too
            trial[1].write_text("", encoding="utf-8")
        CF.write_all(payload, *trial)
        return any((path.read_text(encoding="utf-8") if path.exists() else None)
                   != (out.read_text(encoding="utf-8") if out.exists() else None)
                   for path, out in zip(real, trial))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load_all()
    before = len(payload["factories"])
    records = MR.read_records(REPO / RESULTS)
    verdicts = MR.merge(payload, records, RESULTS)
    tally = collections.Counter(verdict for _i, verdict, _row, _d in verdicts)
    reasons = collections.Counter(kind for _i, verdict, _row, problems in verdicts
                                  if verdict == "rejected"
                                  for kind, _detail in problems)
    large = sum(1 for row in payload["factories"] if CF.is_large(row))
    print(f"{len(records)} results: " + ", ".join(
        f"{n} {v}" for v, n in sorted(tally.items()))
        + (f"; refused as {dict(reasons)}" if reasons else "")
        + f"; {before} -> {len(payload['factories'])} classes, {large} of "
          f"them in the large file")
    residue = (VC.duplicate_class_problems(payload["factories"])
               + VC.duplicate_label_problems(payload["factories"])
               + VC.provenance_problems(payload)
               + VC.citation_problems(payload)
               + VC.header_problems(payload))
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the merged catalogue fails a file-level check; "
                         "nothing written")
    if args.dry_run or not _changes(payload):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write_all(payload)
    VC.persist_metric_cache()
    problems = VC.large_file_problems(CF.CATALOG_LARGE_JSON)
    if problems:
        raise SystemExit(f"the large file written fails its own check: "
                         f"{problems}")
    print("wrote master_catalog.json, master_catalog_large.json and "
          "MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
