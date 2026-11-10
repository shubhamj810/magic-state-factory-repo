#!/usr/bin/env python3
"""One-off migration: "San-José", as the author prints the name, in the catalogue's text.

    python master_catalog/migrations/san_jose_spelling_2026_11_10.py [--dry-run]

arXiv:2609.08203 is by Rodrigo San-José. The catalogue's references and much of its text
had the hyphen, while its two regime names and many row fields did not. The owner chose
the author's own spelling on 10 November 2026. This renames the two regimes, keeping their
place in the header's order, and changes the name in every row field that holds it. Only
that text changes. Idempotent.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import catalogfile as CF                                          # noqa: E402
import distance_policy_2026_11_07 as DP                           # noqa: E402
import verify_catalog as VC                                       # noqa: E402

OLD = re.compile("San Jos[eé]")
NEW = "San-José"
ROW_FIELDS = ("strongest_claim", "d_certified_source")
SOURCE_FIELDS = ("regime", "origin", "provenance")


def spell(text):
    return OLD.sub(NEW, text) if isinstance(text, str) else text


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load_all()
    regimes = {spell(name): spell(sentence) for name, sentence in payload["regimes"].items()}
    if len(regimes) != len(payload["regimes"]):
        raise SystemExit("two regimes would share a name")
    payload["regimes"] = regimes
    changed = 0
    for row in payload["factories"]:
        before = repr(row)
        row["regimes"] = [spell(name) for name in row["regimes"]]
        for field in ROW_FIELDS:
            if row.get(field) is not None:
                row[field] = spell(row[field])
        for entry in row.get("sources") or []:
            for field in SOURCE_FIELDS:
                if entry.get(field) is not None:
                    entry[field] = spell(entry[field])
        for entry in row.get("d_certified_evidence") or []:
            entry["tool"] = spell(entry["tool"])
        changed += repr(row) != before
    rows = payload["factories"]
    residue = (VC.duplicate_label_problems(rows) + VC.provenance_problems(payload)
               + VC.citation_problems(payload) + VC.header_problems(payload))
    if residue:
        for kind, detail in residue[:20]:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the catalogue fails a file-level check; nothing written")
    print(f"{changed} row(s) change")
    if args.dry_run or not DP._changes(payload):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write_all(payload)
    print("wrote master_catalog.json, master_catalog_large.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
