#!/usr/bin/env python3
"""One-off migration: the contraction regime's sentence names the round-6 search s6-beam.

    python master_catalog/migrations/contraction_sentence_s6_2026_11_09.py [--dry-run]

"AI search: paired-column contraction of catalogue rows and their direct sums" names the searches
s3-mid, s3-d56, s3-d7, s3-T, s4-csum and s5-beam (contraction_sentence_s5_2026_11_08.py). The 83 rows of
the round-6 search s6-beam, wide randomised beams run on the UMD cluster Zaratan and merged on
9 November 2026, use it too, so the sentence now names s6-beam as well, and every row of the regime
takes it as its strongest_claim. Only that text changes. Idempotent.
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

REGIME = "AI search: paired-column contraction of catalogue rows and their direct sums"
OLD = ("small-n searches s3-mid, s3-d56, s3-d7 and s3-T (round 3), s4-csum (round 4) and s5-beam "
       "(round 5, run on the UMD cluster Zaratan) of 7 and 8 November 2026")
NEW = ("small-n searches s3-mid, s3-d56, s3-d7 and s3-T (round 3), s4-csum (round 4), s5-beam "
       "(round 5) and s6-beam (round 6), the last two run on the UMD cluster Zaratan, of 7 to 9 "
       "November 2026")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load_all()
    sentence = payload["regimes"][REGIME]
    if NEW not in sentence:
        if OLD not in sentence:
            raise SystemExit("the regime sentence is not the one expected")
        payload["regimes"][REGIME] = sentence.replace(OLD, NEW)
    changed = 0
    for row in payload["factories"]:
        if row["regimes"][0] == REGIME and row["strongest_claim"] != payload["regimes"][REGIME]:
            row["strongest_claim"] = payload["regimes"][REGIME]
            changed += 1
    rows = payload["factories"]
    residue = (VC.duplicate_label_problems(rows) + VC.provenance_problems(payload)
               + VC.citation_problems(payload) + VC.header_problems(payload))
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the catalogue fails a file-level check; nothing written")
    print(f"{changed} row(s) take the new sentence")
    if args.dry_run or not DP._changes(payload):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write_all(payload)
    print("wrote master_catalog.json, master_catalog_large.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
