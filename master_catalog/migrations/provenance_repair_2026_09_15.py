#!/usr/bin/env python3
"""One-off migration: two provenance strings that no longer point anywhere.

    python master_catalog/migrations/provenance_repair_2026_09_15.py [--dry-run]

Both defects predate the GL(k,2) re-key and are in ``sources``, which is inert
provenance: no circuit field, no gate and no distance is touched here.
`tests/test_master_catalog.test_source_attribution_is_real` is what catches
them -- it follows every citation into the file it names.

1.  **A renamed classification catalogue.**  997 source entries of the regime
    ``census r<=7`` cite
    ``classification/rank7_census/catalog/sk_classes_r7_PROVISIONAL.json``,
    which commit 2ae7627 ("Promote the rank-7 S_k table from provisional to
    final") renamed to ``sk_classes_r7.json``.  Every one of the 455 distinct
    labels they cite is a label that the renamed file writes, so the citations
    are sound and only the path is stale.

2.  **Two rows citing a scratchpad.**  The ``[[255,43,3]]`` and ``[[511,81,3]]``
    rows of the ``magic-states-AI 255_511_width campaign (2026-09-14)`` regime
    carry ``provenance: null`` and name a ``/private/tmp/claude-501/...`` file
    that exists on no machine.  Their ``origin`` records where the results
    really came from, so that becomes the ``file`` and the provenance says what
    the scratchpad path was.  Nothing is invented: the campaign, the origin and
    the ``N`` / ``d`` each entry published are exactly as merged.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE.parent
sys.path.insert(0, str(CATALOGUE))

import catalogfile as CF                                          # noqa: E402
import verify_catalog as VC                                       # noqa: E402

RENAMED = ("classification/rank7_census/catalog/sk_classes_r7_PROVISIONAL.json",
           "classification/rank7_census/catalog/sk_classes_r7.json")
SCRATCHPAD = "/private/tmp/claude-501/"
CAMPAIGN = "magic-states-AI 255_511_width campaign (2026-09-14)"


def repair(payload):
    renamed = scratch = 0
    for row in payload["factories"]:
        for source in row["sources"]:
            if source.get("file") == RENAMED[0]:
                source["file"] = RENAMED[1]
                renamed += 1
            if source.get("regime") == CAMPAIGN and source.get("file", "").startswith(SCRATCHPAD):
                was = source["file"]
                source["file"] = source["origin"] or was
                if source.get("provenance") is None:
                    source["provenance"] = (
                        f"merged from {source['origin']}; the submitting file "
                        f"was a run scratchpad ({was}) and is not a path this "
                        f"repository or any other keeps")
                scratch += 1
    return renamed, scratch


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load()
    renamed, scratch = repair(payload)
    print(f"{renamed} source entries re-pointed at the renamed rank-7 "
          f"catalogue; {scratch} scratchpad citations replaced by their origin")
    residue = (VC.provenance_problems(payload) + VC.citation_problems(payload)
               + VC.header_problems(payload))
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("provenance would be inconsistent; nothing written")
    if args.dry_run:
        print("dry run: nothing written")
        return 0
    CF.write(payload)
    print("wrote master_catalog.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
