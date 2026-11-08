#!/usr/bin/env python3
"""One-off migration: the credit of 737.1.17.a, and the parent's works on
508.77.6.a.

    python master_catalog/migrations/credit_2026_11_07.py [--dry-run]

737.1.17.a is Theorem 12 of Berardini et al. (arXiv:2412.08586) applied to
their [[89,1,17]] code and A. Gong's [[559,1,15]] (559.1.15.a). The
catalogue's second-round AI search (small-lit) made that doubling, and
`transversal_t_codes/berardini.py` builds it. The owner's decision of
7 November 2026: credit Berardini et al. and Gong, and tag it the way the
codes built by doubling Gong's codes with Jain and Albert's are tagged
(`pre-existing`, regime "Jain-Albert doubling of Gong's codes", citing the
two works), with the AI search named in the provenance. So:

* the regime "AI search: Berardini doubling of Gong's code" is renamed
  "Berardini et al. doubling of Gong's code", in its place in the header's
  order, with a sentence that says who made the doubling;
* the row cites ``berardini2024asymptotically`` and ``gong2025triply``, in
  place of ``jain2026symmetry``, and is ``pre-existing``;
* its source names both works in ``origin`` and says how it was found in
  ``provenance``;
* the header's ``discovery`` sentence names the Berardini doublings.

508.77.6.a came from 512.84.8.a by shortening and output restriction, and the
descent rows are credited also to the parent row's works (as 504.45.6.a,
from the same parent, is); it was imported citing ``jain2026symmetry`` only,
and gains the parent's ``rengaswamy2020optimality`` and
``vuillot2022quantum``.

Only provenance changes. Every changed row passes `verify_catalog.verify_row`
and the file-level checks pass before anything is written. Idempotent.
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

OLD_REGIME = "AI search: Berardini doubling of Gong's code"
NEW_REGIME = "Berardini et al. doubling of Gong's code"
SENTENCE = ("the [[89,1,17]] code of Berardini et al. (arXiv:2412.08586) doubled by "
            "their Theorem 12 onto A. Gong's [[559,1,15]] (github.com/gongaa/RM127, "
            "triply-even/), a doubling the catalogue's second-round AI search of "
            "7 November 2026 made, rebuilt by transversal_t_codes/berardini.py; "
            "d = 17 by that theorem, its inputs proved here")
CITATIONS = ["berardini2024asymptotically", "gong2025triply"]
ORIGIN = ("E. Berardini, R. Dastbasteh, J. Etxezarreta Martinez, S. Jain and "
          "O. Sanz Larrarte, \"Asymptotically good CSS-T codes and a new construction "
          "of triorthogonal codes\", arXiv:2412.08586 (2024), Theorem 12; A. Gong, "
          "\"On some K=1 codes admitting strongly transversal T\", note in "
          "github.com/gongaa/RM127, triply-even/ (2025); the doubling made by the "
          "catalogue's second-round AI search, research/search2/small-lit/REPORT.md "
          "section 5 (research branch, commit f1083d7)")
PROVENANCE = ("found by the catalogue's second-round AI search (small-lit, 7 November "
              "2026), which applied Theorem 12 of Berardini et al. to their cyclic "
              "[89,44] code and A. Gong's [[559,1,15]] (559.1.15.a); built by "
              "transversal_t_codes/berardini.py")
OLD_DISCOVERY = ("the codes of Jain and Albert and of A. Gong rebuilt in "
                 "transversal_t_codes/ and the codes built there by doubling hers "
                 "with theirs")
NEW_DISCOVERY = ("the codes of Jain and Albert and of A. Gong rebuilt in "
                 "transversal_t_codes/ and the codes built there by doubling hers "
                 "with theirs or by Berardini et al.'s Theorem 12")
PARENT_WORKS = {"508.77.6.a": ("512.84.8.a", ["rengaswamy2020optimality",
                                              "vuillot2022quantum"])}


def rename_regime(payload):
    regimes = payload["regimes"]
    if OLD_REGIME not in regimes:
        return
    payload["regimes"] = {(NEW_REGIME if key == OLD_REGIME else key):
                          (SENTENCE if key == OLD_REGIME else value)
                          for key, value in regimes.items()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load_all()
    rows = payload["factories"]
    by = {row["catalog_label"]: row for row in rows}
    users = [row["catalog_label"] for row in rows
             if OLD_REGIME in row["regimes"]
             or any(s["regime"] == OLD_REGIME for s in row["sources"])]
    if users not in ([], ["737.1.17.a"]):
        raise SystemExit(f"rows other than 737.1.17.a use {OLD_REGIME!r}: {users}")
    rename_regime(payload)
    if OLD_DISCOVERY in payload["discovery"]["pre-existing"] \
            and NEW_DISCOVERY not in payload["discovery"]["pre-existing"]:
        payload["discovery"]["pre-existing"] = payload["discovery"]["pre-existing"] \
            .replace(OLD_DISCOVERY, NEW_DISCOVERY)
    changed = []
    row = by["737.1.17.a"]
    (source,) = row["sources"]
    if source["file"] != "transversal_t_codes/berardini_factories.json" \
            or source["label"] != "berardini-737":
        raise SystemExit("737.1.17.a's source is not the Berardini doubling of 559.1.15.a")
    for key in CITATIONS:
        if key not in payload["references"]:
            raise SystemExit(f"the header has no reference {key}")
    row["regimes"] = [NEW_REGIME]
    row["strongest_claim"] = payload["regimes"][NEW_REGIME]
    row["discovery"] = "pre-existing"
    row["citations"] = list(CITATIONS)
    source["regime"] = NEW_REGIME
    source["origin"] = ORIGIN
    source["provenance"] = PROVENANCE
    changed.append(row)
    for label, (parent, works) in PARENT_WORKS.items():
        row = by[label]
        if not any(f"descent from {parent}" in (s.get("provenance") or "")
                   or parent in (s.get("provenance") or "") for s in row["sources"]):
            raise SystemExit(f"{label} does not name {parent} as its parent")
        if not all(key in by[parent]["citations"] for key in works):
            raise SystemExit(f"{parent} does not cite {works}")
        added = [key for key in works if key not in row["citations"]]
        if added:
            row["citations"] = row["citations"] + added
            changed.append(row)
    for row in changed:
        _facts, problems = VC.verify_row(row)
        print(f"  {row['catalog_label']}: citations {row['citations']}, discovery "
              f"{row['discovery']}, regimes {row['regimes']}"
              + (f": {problems}" if problems else ""))
        if problems:
            raise SystemExit("a changed row fails verification; nothing written")
    residue = (VC.duplicate_label_problems(rows) + VC.provenance_problems(payload)
               + VC.citation_problems(payload) + VC.header_problems(payload))
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the catalogue fails a file-level check; nothing written")
    if args.dry_run or not DP._changes(payload):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write_all(payload)
    print("wrote master_catalog.json, master_catalog_large.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
