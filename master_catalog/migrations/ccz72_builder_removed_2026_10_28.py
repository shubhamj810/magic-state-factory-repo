#!/usr/bin/env python3
"""One-off migration: the 72 T -> CCZ protocol of Gong et al. is kept as its row.

    python master_catalog/migrations/ccz72_builder_removed_2026_10_28.py [--dry-run]

``literature_imports/ccz72_d6/`` rebuilt the (8T -> CCZ) * (9CCZ -> CCZ) chain
of A. Gong, C. A. Pattison, P. Rall and A. Wills (arXiv:2608.09727) as one
circuit, and that circuit was merged as ``72.3.6.a`` on 2026-10-26.  The row
holds the circuit and is verified from its columns like every other row, so
the builder and its tests were removed; they are in this repository's history
at commit ``1cc8de4``.

This rewrites the description of the row's regime in the catalogue header,
which named the removed folder, and the row's ``strongest_claim``, which is a
copy of it.  The row's source keeps its ``file``, as a record of where the
circuit came from.  Re-running it changes nothing.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import catalogfile as CF                                          # noqa: E402
import verify_catalog as VC                                       # noqa: E402

REGIME = "Gong et al.: F8 codes concatenated with 8T->CCZ"
DESCRIPTION = ("a concatenated protocol of Gong, Pattison, Rall and Wills "
               "(arXiv:2608.09727): an F8 code fed by copies of the 8T->CCZ "
               "protocol, rebuilt from the paper's construction and written "
               "as one circuit on 18 wires; a verified witness, not a maximum")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load_all()
    old = payload["regimes"][REGIME]
    rows = [row for row in payload["factories"]
            if row["regimes"][0] == REGIME
            and row["strongest_claim"] != DESCRIPTION]
    if old == DESCRIPTION and not rows:
        print("nothing to change")
        return 0
    print(f"{REGIME}:\n  was {old}\n  now {DESCRIPTION}\n"
          f"  strongest_claim of {', '.join(r['catalog_label'] for r in rows)}")
    if args.dry_run:
        print("nothing written: dry run")
        return 0
    payload["regimes"][REGIME] = DESCRIPTION
    for row in rows:
        row["strongest_claim"] = DESCRIPTION
    residue = VC.provenance_problems(payload) + VC.header_problems(payload)
    if residue:
        raise SystemExit(f"the edited catalogue fails a file-level check, "
                         f"nothing written: {residue}")
    CF.write_all(payload)
    print("wrote master_catalog.json, master_catalog_large.json and "
          "MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
