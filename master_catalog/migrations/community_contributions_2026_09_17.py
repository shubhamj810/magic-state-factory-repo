#!/usr/bin/env python3
"""One-off migration: make the header ready for community contributions.

    python master_catalog/migrations/community_contributions_2026_09_17.py [--dry-run]

`community_contributions/check_submission.py` merges outside authors' protocols
with the regime ``community contribution`` and ``discovery: pre-existing``.  The two
discovery sentences did not yet say what that means, and this changes exactly
them, then re-renders `MASTER_CATALOG.md` (whose citation paragraph now names
contributions too):

* ``discovery["pre-existing"]`` listed where a class that is *not an AI
  discovery of this project* can come from, and a community contribution was
  not on the list; ``discovery["AI search"]`` did not say a community
  contribution is one of the finders that rule it out;
* nothing else in the header, and no row, changes.  The regime itself is not
  pre-registered: `merge_results` files it, with the checker's sentence, the
  first time a contribution is merged, so the regime table never lists a
  regime with no rows.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import catalogfile as CF                                          # noqa: E402
import verify_catalog as VC                                       # noqa: E402

PRE_EXISTING = ("not an AI discovery of this project: a classification stage "
                "this repository ran, the symmetry-SAT search catalogue, the "
                "exhaustive length-54 classification alone, or a community "
                "contribution has this class")
AI_SEARCH = ("found only by AI search campaigns or search releases: no "
             "classification stage this repository ran, no symmetry-SAT search "
             "and no community contribution is recorded among its sources (the "
             "length-54 classification may have it too); whether it was new to "
             "the literature is what citations says")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load()
    for tag, sentence in (("pre-existing", PRE_EXISTING),
                          ("AI search", AI_SEARCH)):
        was = payload["discovery"][tag]
        payload["discovery"][tag] = sentence
        print(f"discovery[{tag!r}]:\n  was: {was}\n  now: {sentence}")
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
