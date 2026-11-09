#!/usr/bin/env python3
"""One-off migration: every row gains ``gate_family`` and the frame showing it.

    python master_catalog/migrations/gate_family_2026_11_09.py [--dry-run] [--cross FILE]

The record tables ranked a row in the gate class its STORED frame shows. A
catalogue entry is a gate up to a CNOT frame, so that class depended on which
frame a source happened to use: 48.5.3.d is stored as CS01·CS34·CCZ012·CCZ234
and is CS01·CS13·CS24·CS34 in another frame (found by the research's t6-lit
agent, research/search2/t6-lit/, and checked by the lead). The owner ruled on
2026-11-09 that the class of the entry, not the stored frame, sets the record.

`gatefamily.decide` gives ``T``, ``CS``, ``CCZ`` or ``mixed`` over all frames,
and a frame when the stored one does not show the family. This script adds
the four fields after ``intrinsic_width`` and checks every frame a second way,
sharing no code with `gatefamily` or `glcanon`: it XORs the stored output rows
over the columns into the new output rows and reads T, CS and CCZ off their
literal overlap parities. With ``--cross`` it also compares the T and CS
decisions with an independent search (t6-lit's ``data/families.json``) on every
row both decided. Nothing is written unless all checks and the file-level
checks pass. ``k``, the stored gate and every other field stay as they are.
Idempotent.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import catalogfile as CF                                          # noqa: E402
import distance_policy_2026_11_07 as DP                           # noqa: E402
import verify_catalog as VC                                       # noqa: E402

FIELDS = ("gate_family", "gate_family_frame", "gate_family_gate", "gate_family_human")

#: Rows the lead checked by hand on 2026-11-09 (research/search2/lead/CHECKS.md,
#: "t6-lit"): GL-equivalent to the stored gate, and CS only in the new frame.
LEAD = {"12.3.2.a": "CS", "42.12.2.a": "CS", "48.5.3.b": "CS", "48.5.3.c": "CS",
        "48.5.3.d": "CS", "48.5.3.e": "CS", "48.5.3.f": "CS", "31.2.3.a": "T"}


def literal_kind(columns, k, frame):
    """The gate in ``frame``, read off the columns: T on i iff the new output
    row i has odd weight, CS on {i, j} iff two rows overlap oddly, CCZ on
    {i, j, l} iff three do. Returns the monomial list."""
    rows = [0] * k
    for j, column in enumerate(columns):
        for q in column:
            if q < k:
                rows[q] |= 1 << j
    new = []
    for b in frame:
        r = 0
        for q in range(k):
            if b >> q & 1:
                r ^= rows[q]
        new.append(r)
    out = []
    for i in range(k):
        if new[i].bit_count() & 1:
            out.append((i,))
    for i in range(k):
        for j in range(i + 1, k):
            if (new[i] & new[j]).bit_count() & 1:
                out.append((i, j))
    for i in range(k):
        for j in range(i + 1, k):
            ij = new[i] & new[j]
            for l in range(j + 1, k):
                if (ij & new[l]).bit_count() & 1:
                    out.append((i, j, l))
    return out


def insert_after(row, key, values):
    items = [(k_, v) for k_, v in row.items() if k_ not in values]
    row.clear()
    for k_, v in items:
        row[k_] = v
        if k_ == key:
            row.update(values)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--cross", help="t6-lit's data/families.json, for the cross-check")
    args = parser.parse_args(argv)
    payload = CF.load_all()
    rows = payload["factories"]
    started = time.time()
    counts, moved, undecided = collections.Counter(), [], []
    for index, row in enumerate(rows):
        k = row["k"]
        facts = VC.family_facts(k, VC.row_monomials(row))
        fam, frame = facts["gate_family"], facts["gate_family_frame"]
        if frame is not None:
            got = literal_kind(row["columns"], k, frame)
            kinds = {len(m) for m in got}
            want = {"T": {1}, "CS": {2}, "CCZ": {3}}[fam]
            if kinds != want:
                raise SystemExit(f"{row['catalog_label']}: the literal overlaps in the "
                                 f"{fam} frame give terms of sizes {sorted(kinds)}")
            if VC.SK.gate_string(got, k) != facts["gate_family_gate"]:
                raise SystemExit(f"{row['catalog_label']}: the literal gate in the frame "
                                 f"differs from the derived one")
        if row["catalog_label"] in LEAD and LEAD[row["catalog_label"]] != fam:
            raise SystemExit(f"{row['catalog_label']}: family {fam}, the lead found "
                             f"{LEAD[row['catalog_label']]}")
        insert_after(row, "intrinsic_width", facts)
        counts[fam] += 1
        if frame is not None:
            moved.append(row)
        if fam is None:
            undecided.append(row["catalog_label"])
        if index % 500 == 0:
            print(f"  {index} rows, {time.time() - started:.0f}s", flush=True)
    missing = [label for label in LEAD if label not in {r["catalog_label"] for r in rows}]
    if missing:
        raise SystemExit(f"rows the lead checked are missing: {missing}")
    if args.cross:
        other = json.load(open(args.cross))["catalogue_mixed_lt127"]
        by_label = {r["catalog_label"]: r for r in rows}
        compared = 0
        for x in other:
            mine = by_label[x["label"]]["gate_family"]
            if mine is None or x.get("T") is None or x.get("CS") is None:
                continue
            theirs = "T" if x["T"] else "CS" if x["CS"] else "mixed"
            if mine != theirs:
                raise SystemExit(f"{x['label']}: family {mine}, the independent search {theirs}")
            compared += 1
        print(f"cross-check: {compared} rows agree with the independent search")
    residue = (VC.duplicate_label_problems(rows) + VC.provenance_problems(payload)
               + VC.citation_problems(payload) + VC.header_problems(payload))
    residue += [(kind, f"{r['catalog_label']}: {detail}") for r in rows
                for kind, detail in CF.type_problems(r)]
    if residue:
        for kind, detail in residue[:20]:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the catalogue fails a file-level check; nothing written")
    report = [{"label": r["catalog_label"], "stored": r["gate_human"][:80],
               "family": r["gate_family"], "in_frame": r["gate_family_human"][:80]}
              for r in moved]
    print(json.dumps(report[:40]))
    print(f"{len(rows)} rows: {dict(counts)}; {len(moved)} shown in a new frame; "
          f"undecided: {undecided} ({time.time() - started:.0f}s)")
    if args.dry_run or not DP._changes(payload):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write_all(payload)
    print("wrote master_catalog.json, master_catalog_large.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
