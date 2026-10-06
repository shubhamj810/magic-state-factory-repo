#!/usr/bin/env python3
"""One-off migration: give every row its permanent public name, ``catalog_label``.

    python master_catalog/migrations/catalog_labels_2026_10_06.py [--dry-run]

A label is ``n.k.d.x`` -- ``15.1.3.a`` -- with ``d`` the distance proved here and
``x`` a letter code (``a`` .. ``z``, ``ba``, ``bb``, ... as LMFDB numbers its
isogeny classes).  Within one ``(n, k, d)`` the letters follow the rows' order
in this file, which is the catalogue's own sort order; nothing about the gate
(its terms, its T-count) is used, because none of that is an invariant of the
class.  From here on `merge_results.py` gives a new class the next unused letter
and an improvement keeps the label it had, so a label is never changed or
reused.  Re-running this script on a labelled file is a no-op.
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import catalogfile as CF                                          # noqa: E402
import verify_catalog as VC                                       # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load()
    rows = payload["factories"]
    if all("catalog_label" in row for row in rows):
        print("every row already carries a catalog_label; nothing to do")
        return 0
    counter = defaultdict(int)
    labelled = []
    for row in rows:
        key = (row["n"], row["k"], row["d"])
        label = f"{key[0]}.{key[1]}.{key[2]}.{CF.label_letters(counter[key])}"
        counter[key] += 1
        # first key in the row, so the name is the first thing a reader sees
        labelled.append({"catalog_label": label, **{k: v for k, v in row.items()
                                                     if k != "catalog_label"}})
    payload["factories"] = labelled
    residue = [p for row in labelled for p in VC.label_problems(row)] \
        + VC.duplicate_label_problems(labelled)
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("labels would be inconsistent; nothing written")
    widest = max(counter.items(), key=lambda item: item[1])
    print(f"labelled {len(labelled)} rows in {len(counter)} parameter sets; "
          f"the most at one is {widest[1]} at [[{widest[0][0]},{widest[0][1]},{widest[0][2]}]]")
    if args.dry_run:
        print("dry run: nothing written")
        return 0
    CF.write(payload)
    print("wrote master_catalog.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
