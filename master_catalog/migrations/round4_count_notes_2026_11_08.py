#!/usr/bin/env python3
"""One-off migration: say in the source of a round-4 row where its A_d was counted but is not stored.

    python master_catalog/migrations/round4_count_notes_2026_11_08.py [--dry-run]

round1_certificates/count_weight.py counted the harmful faults of weight d of these rows twice
(mitml in list mode, every set re-checked, and mydist.py), and the two agree. The count is not
stored as A_d, because round1_certificates/assemble.py binds a count to its list, and these lists
are too large for this repository (over 5 MB gzipped). The list and the run's record are kept in
the research worktree. Each row's s4-csum source gets one sentence that says so. Only that text
changes. Idempotent.
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

WHERE = "research/search2/catalogue/stage3/data/lists/"
#: label -> (source label, weight, count, gzipped size of the list)
NOTES = {
    "452.66.6.a": ("s4-csum 635dd6a7cd", 6, 2452268, "42 MB"),
    "348.22.7.a": ("s4-csum 80ade620a8", 7, 877306, "11 MB"),
    "470.28.7.a": ("s4-csum 9c8f7d3120", 7, 833477, "11 MB"),
}


def sentence(w, count, size):
    return (f"; mitml in list mode and mydist.py (round1_certificates/count_weight.py, run here on "
            f"8 November 2026) agree on A_{w} = {count:,}, which is not stored because the list "
            f"({size} gzipped) is too large for this repository; the list and the run's record are "
            f"kept in the research worktree, {WHERE}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load_all()
    by = {row["catalog_label"]: row for row in payload["factories"]}
    changed = 0
    for label, (source, w, count, size) in NOTES.items():
        row = by[label]
        if row["d"] != w or not row["d_is_exact"] or row["A_d"] is not None:
            raise SystemExit(f"{label} is not an exact row at d = {w} with A_d null")
        (entry,) = [s for s in row["sources"] if s["label"] == source]
        text = sentence(w, count, size)
        if not entry["provenance"].endswith(text):
            entry["provenance"] += text
            changed += 1
    rows = payload["factories"]
    residue = (VC.duplicate_label_problems(rows) + VC.provenance_problems(payload)
               + VC.citation_problems(payload) + VC.header_problems(payload))
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the catalogue fails a file-level check; nothing written")
    print(f"{changed} source(s) take the note")
    if args.dry_run or not DP._changes(payload):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write_all(payload)
    print("wrote master_catalog.json, master_catalog_large.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
