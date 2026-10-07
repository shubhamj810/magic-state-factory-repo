#!/usr/bin/env python3
"""One-off migration: the symmetry-and-AI report is published on the arXiv.

    python master_catalog/migrations/jain_report_published_2026_10_07.py [--dry-run]

S. P. Jain, A. Wills and S. Singh, "Symmetry and AI-assisted discovery of
magic-state factories", is arXiv:2610.06535 (submitted 2026-10-05).  The
header's ``jain2026symmetry`` entry said "in preparation" and carried no
``url``; this gives it the arXiv identifier and link, in the form the other
arXiv entries use -- as `wills_classification_published_2026_10_05.py` did
for the length-54 classification.  Every row credits the work by key, so the
rows themselves are untouched.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import catalogfile as CF                                          # noqa: E402
import merge_results as MR                                        # noqa: E402
import verify_catalog as VC                                       # noqa: E402

KEY = "jain2026symmetry"
ENTRY = MR.DEFAULT_REFERENCES[KEY]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load()
    references = payload["references"]
    if KEY not in references:
        raise SystemExit(f"the header has no reference {KEY!r}")
    if references[KEY] == ENTRY:
        print(f"{KEY!r} is already the published entry; nothing to do")
        return 0
    print(f"{KEY!r}:\n  was {references[KEY]}\n  now {ENTRY}")
    references[KEY] = dict(ENTRY)
    rows = sum(KEY in row["citations"] for row in payload["factories"])
    print(f"{rows} rows cite it; no row changes")
    residue = VC.provenance_problems(payload) + VC.header_problems(payload)
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the header would be inconsistent; nothing written")
    if args.dry_run:
        print("dry run: nothing written")
        return 0
    CF.write(payload)
    print("wrote master_catalog.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
