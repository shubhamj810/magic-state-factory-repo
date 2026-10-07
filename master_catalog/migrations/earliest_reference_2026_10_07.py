#!/usr/bin/env python3
"""One-off migration: a class an earlier work published is not also credited
to the Borrowed Identities paper.

    python master_catalog/migrations/earliest_reference_2026_10_07.py [--dry-run]

`distance_two_2026_10_07.py` credited every class the borrowed-identity
searches found to S. Singh, C. Gidney and C. Jones (arXiv:2606.28518), after
any earlier publication of the same class.  The owner's rule is that a class
with an earlier reference is credited to that reference alone: the paper
recovered it rather than introducing it.  So ``singh2026borrowed`` is removed
from every row that also cites a work published before it -- a year before
2026, or a 2026 arXiv identifier below 2606.28518.  Concurrent publications of
the same class (Eastin's and Jones's 8 T -> CCZ factories) both stay.

A row whose other citations are all later -- the length-54 classification
(arXiv:2609.30860) and the symmetry-and-AI report (arXiv:2610.06535), on
``31.1.3.a`` -- keeps the paper.  So does every class the paper is the first
to state.  Only ``citations`` changes; no circuit and no other field does.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import catalogfile as CF                                          # noqa: E402
import verify_catalog as VC                                       # noqa: E402

KEY = "singh2026borrowed"
PUBLISHED = (2026, "2606.28518")
YEAR = re.compile(r"\((\d{4})\)")
ARXIV = re.compile(r"arXiv:(\d{4}\.\d{4,5})")


def published(entry):
    """``(year, arXiv id or None)``, or ``None`` for an unpublished work."""
    if not entry.get("url"):
        return None
    year = YEAR.search(entry["short"])
    arxiv = ARXIV.search(entry["full"])
    return int(year.group(1)), arxiv.group(1) if arxiv else None


def earlier(entry):
    """Whether a reference was published before the Borrowed Identities paper."""
    date = published(entry)
    if date is None:
        return False
    year, arxiv = date
    if year != PUBLISHED[0]:
        return year < PUBLISHED[0]
    return arxiv is not None and float(arxiv) < float(PUBLISHED[1])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load()
    references = payload["references"]
    changed = []
    for row in payload["factories"]:
        if KEY not in row["citations"]:
            continue
        before = [key for key in row["citations"]
                  if key != KEY and earlier(references[key])]
        if before:
            row["citations"] = [key for key in row["citations"] if key != KEY]
            changed.append((row["catalog_label"], row["citations"]))
    for label, keys in changed:
        print(f"  {label}: {', '.join(keys)}")
    kept = sum(KEY in row["citations"] for row in payload["factories"])
    print(f"{len(changed)} rows credited to an earlier work alone; "
          f"{kept} still cite {KEY}")
    residue = VC.citation_problems(payload) + VC.header_problems(payload)
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the catalogue would fail its checks; nothing written")
    if args.dry_run or not changed:
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write(payload)
    print("wrote master_catalog.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
