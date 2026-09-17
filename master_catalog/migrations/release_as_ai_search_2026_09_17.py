#!/usr/bin/env python3
"""One-off migration: file the 55 <= n <= 64 search release as an AI search.

    python master_catalog/migrations/release_as_ai_search_2026_09_17.py [--dry-run]

The 79 rows of the regime ``search release 55<=n<=64`` come from the public
generalised triorthogonal search release (``search_public_release_adam``), an
AI-assisted search reported in the symmetry-and-AI paper.  They already cite
``jain2026symmetry`` alone and are tagged ``discovery: AI search``; only the
label said otherwise.  This renames the regime -- in the header, keeping its
place in the strongest-first order, in every row's ``regimes`` and in every
source entry -- rewrites its sentence, re-reads ``strongest_claim`` on the rows
it heads, and drops "or search releases" from the ``AI search`` glossary
sentence, since every such release is now an AI search regime.  Citations,
circuits and every other field are untouched.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import catalogfile as CF                                          # noqa: E402
import verify_catalog as VC                                       # noqa: E402

OLD = "search release 55<=n<=64"
NEW = "AI search: generalised triorthogonal search 55<=n<=64"
CLAIM = ("found by the AI-assisted public search for generalised triorthogonal "
         "protocols at lengths 55-64; a verified witness, not a maximum")
AI_SEARCH = ("found only by AI search campaigns: no classification stage this "
             "repository ran, no symmetry-SAT search and no community "
             "contribution is recorded among its sources (the length-54 "
             "classification may have it too); whether it was new to the "
             "literature is what citations says")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load()
    header = payload["regimes"]
    if OLD not in header:
        raise SystemExit(f"the header has no regime {OLD!r}")
    payload["regimes"] = {(NEW if key == OLD else key):
                          (CLAIM if key == OLD else sentence)
                          for key, sentence in header.items()}
    rows = sources = 0
    for row in payload["factories"]:
        if OLD not in row["regimes"]:
            continue
        rows += 1
        row["regimes"] = [NEW if name == OLD else name for name in row["regimes"]]
        for source in row["sources"]:
            if source["regime"] == OLD:
                source["regime"] = NEW
                sources += 1
        row["strongest_claim"] = payload["regimes"][row["regimes"][0]]
    payload["discovery"]["AI search"] = AI_SEARCH
    print(f"{OLD!r} -> {NEW!r}: {rows} rows, {sources} source entries")
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
