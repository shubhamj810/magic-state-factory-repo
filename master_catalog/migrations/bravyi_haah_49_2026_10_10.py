#!/usr/bin/env python3
"""One-off migration: credit the [[49,1,5]] class to Bravyi and Haah alone.

    python master_catalog/migrations/bravyi_haah_49_2026_10_10.py [--dry-run]

``49.1.5.a`` is Pareto point 4 of the length-54 classification.  The
classification's own Pareto table attributes it to no published protocol, so
`length54_classification_2026_09_16.py` credited it to the classification and
the symmetry-and-AI report.  But S. Bravyi and J. Haah, "Magic-state
distillation with low overhead", Phys. Rev. A 86, 052329 (2012), Appendix B,
give a 49-qubit triorthogonal code with one output, a transversal T gate and
distance 5 -- the same (n, k, d, gate) class.  The owner's rule is that a class
with an earlier publication is credited to that publication alone, so the row
now cites ``bravyi2012magic`` only.  The Jain-Albert import brought the same
class again (`transversal_t_codes/`) and changed nothing, as a duplicate.

Only ``citations`` changes.  Re-running it changes nothing.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import catalogfile as CF                                          # noqa: E402
import verify_catalog as VC                                       # noqa: E402

LABEL = "49.1.5.a"
CREDIT = ["bravyi2012magic"]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load()
    row, = [r for r in payload["factories"] if r["catalog_label"] == LABEL]
    if (row["n"], row["k"], row["d"], row["gate"]) != (49, 1, 5, "0"):
        raise SystemExit(f"{LABEL} is not the [[49,1,5]] T class")
    if row["citations"] == CREDIT:
        print(f"{LABEL} already cites {CREDIT}; nothing to do")
        return 0
    print(f"{LABEL}: {row['citations']} -> {CREDIT}")
    row["citations"] = list(CREDIT)
    residue = VC.citation_problems(payload)
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the citations would not resolve; nothing written")
    if args.dry_run:
        print("nothing written: dry run")
        return 0
    CF.write(payload)
    print("wrote master_catalog.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
