#!/usr/bin/env python3
"""One-off migration: every row gains ``intrinsic_width``.

    python master_catalog/migrations/intrinsic_width_2026_11_07.py [--dry-run]

A gate's trilinear form ``tau(u, v, w) = |f_u f_v f_w| mod 2`` (``f_u`` the
set of columns holding output ``u``, extended linearly in each argument) can
have a nonzero radical: output combinations on which the gate acts as a
Clifford. In a CNOT frame with such a combination as an output, that output is
a spectator, which the stored-frame spectator check (`faultcore.spectators`)
cannot see. The research's s3-mid agent found such rows and the lead confirmed
them (research/search2/lead/CHECKS.md, "Hidden spectators", radcheck.py):
127.37.3.a uses 31 of its 37 outputs, for example.

``intrinsic_width`` is ``k`` less the radical's dimension. This script
computes it twice for every row of both files and requires the two to agree:

* from the stored gate, by `glcanon.intrinsic_width` (the rank of the
  flattened tensor), which is what `verify_catalog` recomputes from now on;
* from the columns directly, by Gaussian elimination of the linear system
  ``sum_u a_u tau(u, v, w) = 0`` over every pair ``v <= w``, written here and
  sharing no code with glcanon (the method of the lead's radcheck_core.py).

The field goes right after ``effective_width``. ``k``, the gate, the labels and
every other field stay as they are. The file-level checks pass before anything
is written; `verify_catalog` recomputes the field on every row it verifies.
Idempotent.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import catalogfile as CF                                          # noqa: E402
import distance_policy_2026_11_07 as DP                           # noqa: E402
import glcanon as GC                                              # noqa: E402
import verify_catalog as VC                                       # noqa: E402

#: The ten rows the lead checked (CHECKS.md): k -> width.
LEAD = {"31.5.3.a": 1, "39.6.3.a": 1, "39.6.3.b": 3, "43.7.3.a": 3, "44.4.3.b": 3,
        "48.4.4.a": 2, "55.5.3.o": 4, "85.2.5.a": 1, "90.10.3.c": 9, "127.37.3.a": 31,
        "63.8.3.d": 8, "127.8.5.a": 8, "93.2.5.a": 2, "8.3.2.a": 3}


def width_from_columns(columns, k):
    """``k`` less the radical's dimension, straight from the columns."""
    n = len(columns)
    bits = [bytearray(n) for _ in range(k)]
    for j, column in enumerate(columns):
        for q in column:
            if q < k:
                bits[q][j] = 1
    # one big integer per output, built once (bit j set iff column j holds it)
    digits = bytes.maketrans(b"\x00\x01", b"01")
    f = [int(bytes(b[::-1]).translate(digits) or b"0", 2) for b in bits]
    pivots = {}                       # top bit -> reduced equation over the a_u
    for v in range(k):
        for w in range(v, k):
            g = f[v] & f[w]
            if not g:
                continue
            eq = 0
            for u in range(k):
                if (f[u] & g).bit_count() & 1:
                    eq |= 1 << u
            for top in sorted(pivots, reverse=True):
                if eq >> top & 1:
                    eq ^= pivots[top]
            if eq:
                pivots[eq.bit_length() - 1] = eq
                if len(pivots) == k:
                    return k
    return len(pivots)


def insert_after(row, key, name, value):
    items = list(row.items())
    row.clear()
    for k_, v in items:
        if k_ == name:
            continue
        row[k_] = v
        if k_ == key:
            row[name] = value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load_all()
    rows = payload["factories"]
    hidden = []
    started = time.time()
    for index, row in enumerate(rows):
        k = row["k"]
        a = GC.intrinsic_width(k, VC.row_monomials(row))
        b = width_from_columns(row["columns"], k)
        if a != b:
            raise SystemExit(f"{row['catalog_label']}: the two widths disagree ({a}, {b})")
        if row["catalog_label"] in LEAD and LEAD[row["catalog_label"]] != a:
            raise SystemExit(f"{row['catalog_label']}: width {a}, the lead found "
                             f"{LEAD[row['catalog_label']]}")
        insert_after(row, "effective_width", "intrinsic_width", a)
        if a < k:
            hidden.append(row)
        if index % 250 == 0:
            print(f"  {index} rows, {time.time() - started:.0f}s", flush=True)
    missing = [label for label in LEAD
               if label not in {r["catalog_label"] for r in rows}]
    if missing:
        raise SystemExit(f"rows the lead checked are missing: {missing}")
    residue = (VC.duplicate_label_problems(rows) + VC.provenance_problems(payload)
               + VC.citation_problems(payload) + VC.header_problems(payload))
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the catalogue fails a file-level check; nothing written")
    report = [{"label": r["catalog_label"], "n": r["n"], "k": r["k"], "d": r["d"],
               "intrinsic_width": r["intrinsic_width"], "regimes": r["regimes"]}
              for r in hidden]
    print(json.dumps(report))
    print(f"{len(rows)} rows; {len(hidden)} with a hidden spectator "
          f"({time.time() - started:.0f}s)")
    if args.dry_run or not DP._changes(payload):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write_all(payload)
    print("wrote master_catalog.json, master_catalog_large.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
