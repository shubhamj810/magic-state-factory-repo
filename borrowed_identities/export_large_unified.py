#!/usr/bin/env python3
"""Rebuild every level-3 row of the larger unified search.

    .venv/bin/python borrowed_identities/export_large_unified.py          # write circuits/
    .venv/bin/python borrowed_identities/export_large_unified.py --check  # rebuild, compare, write nothing

On 27 and 28 October 2026 the Borrowed Identities repository (S. Singh, C.
Gidney and C. Jones, arXiv:2606.28518) ran its unified search over a larger
range: the two-group and shared-check gluing stages, without Clifford padding
or SAT, at ``k <= 12`` outputs and ``N <= 18`` circuit wires.  The files this
reads are copied byte for byte into ``upstream_large_unified/``.  Its level-3
table, ``outputs/large_unified_factories_l3.csv``, has 1,291 rows, all rebuilt
here: 1,254 at distance 2, and 37 single-output rows at distance 3 or more.
The table gives 12 of those 37 a distance of 3 and the other 25 only the
floor ``>=3``; the distance measured here must be at least the floor.

Like the earlier tables, this one lists each factory by the parameters that
make it, and the circuits are rebuilt by running the upstream code unmodified:
``merge_large_unified.regenerate_circuit``, the function the upstream
``outputs/README.md`` gives for regenerating any row.  At level 3 it builds a two-group row with
``Two_group.build_gate_set`` and every sign ``+1``, and a gluing row with
``symfree_search.solve_binding`` on the row's blocks.  The upstream
``large_unified_l3_circuits.txt.zip`` stores the gates of every gluing row and
of every two-group row on at most 14 wires; each rebuilt circuit it stores
must equal it.

Each circuit is then checked against its row by `rowcheck.checked`, code
independent of the search: the wire count ``N``, the count ``n`` of
odd-coefficient rotations, the borrowed-identity condition, the output gate
against the row's ``raw`` column (only its number of terms where the table
abbreviates it, as on 689 rows), and the distance, measured by the master
catalogue's fault search.  Any mismatch stops the script.  The error
coefficient ``A_2`` is counted too.

A two-group circuit has only coefficient-1 rotations and is fixed by
``(k, N, s_total, s_O)``, so it is written as that rule, a two-group
construction (``master_catalog/constructions.py``), with the SHA-256 of its
columns; the construction must build exactly the columns checked above.  A
gluing circuit is written out as its gates.

OUTPUT
------
``circuits/large_unified_l3.json``: one entry per distance-2 row, in table
order: the table line, stage and parameters, the measured ``d``, witness and
``A_d``, and the construction and digest (two-group) or the gates (gluing).
``master_catalog/migrations/borrowed_identities_large_unified_2026_10_28.py``
merges it.  ``circuits/large_unified_l3_d3.json``: the same for the rows at
distance 3 or more, with ``d_table`` the table's ``>=3`` where it gives only a
floor; ``borrowed_identities_large_unified_d3_2026_10_28.py`` merges it.

The output is deterministic: ``--check`` rebuilds everything and fails if a
committed file differs.  It takes about 9 minutes with 6 workers, most of
it ``A_2`` of the 18-wire circuits.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import sys
import zipfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
UPSTREAM = HERE / "upstream_large_unified"
OUT = HERE / "circuits" / "large_unified_l3.json"
OUT_D3 = HERE / "circuits" / "large_unified_l3_d3.json"
sys.path.insert(0, str(UPSTREAM / "searches"))
sys.path.insert(0, str(UPSTREAM / "classification"))
sys.path.insert(0, str(REPO / "master_catalog"))
sys.path.insert(0, str(HERE))

import merge_large_unified as MLU                                 # noqa: E402
import constructions as K                                         # noqa: E402
from rowcheck import LEVEL, checked                               # noqa: E402

REPOSITORY = "https://github.com/shraggy/Magic_state_factory_search"
COMMIT = "ae9fbf895e2993568f731b22e785e1e1fcb93655"
CITATION = ("S. Singh, C. Gidney and C. Jones, \"Borrowed Identities: "
            "Malleable Distillation Factories and a Unified Numerical Search,\" "
            "arXiv:2606.28518 (2026)")
TABLE = "large_unified_factories_l3.csv"
GATE_LISTS = "large_unified_l3_circuits.txt.zip"
DISTANCE = "2"
STAGES = ("two-group", "gluing")


# ------------------------------------------------------------------ tables
def read_table():
    """``(line, row)`` for every row of the level-3 table, line 2 first."""
    csv.field_size_limit(sys.maxsize)
    with (UPSTREAM / "outputs" / TABLE).open(newline="", encoding="utf-8") as fh:
        return list(enumerate(csv.DictReader(fh), 2))


def read_gate_lists():
    """``{index: (header, gates)}`` from the upstream gate-list file.

    A block is ``# i l=3 k=.. n=.. N=.. stage params`` and then one line
    ``q,q,...:c`` per rotation; ``i`` counts the level-3 table's rows from 0.
    """
    blocks, current = {}, None
    with zipfile.ZipFile(UPSTREAM / "outputs" / GATE_LISTS) as archive:
        name, = archive.namelist()
        with archive.open(name) as fh:
            for line in io.TextIOWrapper(fh, encoding="ascii"):
                line = line.rstrip("\n")
                if line.startswith("# "):
                    index = int(line.split()[1])
                    if index in blocks:
                        raise SystemExit(f"{GATE_LISTS}: block {index} twice")
                    current = blocks[index] = (line, [])
                elif line:
                    support, coeff = line.split(":")
                    current[1].append((tuple(sorted(int(q) for q in
                                                    support.split(","))),
                                       int(coeff) % (1 << LEVEL)))
    return blocks


def header_of(index, row):
    """The block header the upstream writes for ``row``."""
    return (f"# {index} l={row['l']} k={row['k']} n={row['n']} N={row['N']} "
            f"{row['search_stage']} {row['params']}")


# ------------------------------------------------------------- one row
def entry(job):
    """The checked entry of one table row, or a ``SystemExit`` message."""
    line, row, stored = job
    where = f"{TABLE} line {line}"
    built = MLU.regenerate_circuit(l=int(row["l"]), k=int(row["k"]),
                                   N=int(row["N"]), params=row["params"],
                                   stage=row["search_stage"], raw=row["raw"])
    if built is None:
        raise SystemExit(f"{where}: the upstream code builds no circuit")
    gates = sorted((tuple(sorted(S)), int(c) % (1 << LEVEL)) for S, c in built)
    if stored is not None:
        head, listed = stored
        if head != header_of(line - 2, row):
            raise SystemExit(f"{where}: the gate list's block is {head!r}")
        if sorted(listed) != gates:
            raise SystemExit(f"{where}: the rebuilt gates are not the ones "
                             f"{GATE_LISTS} stores")
    columns, d, witness, a_d = checked(row, gates, where)
    out = {
        "id": f"lu-{line:04d}", "table": TABLE, "line": line,
        "stage": row["search_stage"], "params": row["params"],
        "k": int(row["k"]), "wires": int(row["N"]), "n": int(row["n"]),
        "d": d, "d_witness": witness, "A_d": a_d,
        "raw": row["raw"],
    }
    if row["d"] != str(d):
        out["d_table"] = row["d"]
    if row["search_stage"] == "two-group":
        s_total, s_O = (int(part.split("=")[1])
                        for part in row["params"].split(","))
        rule = {"family": "two-group", "k": out["k"], "N": out["wires"],
                "s_total": s_total, "s_O": s_O}
        if K.columns(rule) != columns:
            raise SystemExit(f"{where}: the two-group construction does not "
                             f"build the circuit the upstream code builds")
        if any(c != 1 for _S, c in gates):
            raise SystemExit(f"{where}: a two-group rotation is not one T")
        out["construction"] = rule
        out["columns_sha256"] = K.digest(columns)
    else:
        out["gates"] = [[list(S), c] for S, c in gates]
    return out


def build(workers=None):
    table = read_table()
    stages = {row["search_stage"] for _line, row in table}
    levels = {row["l"] for _line, row in table}
    if not stages <= set(STAGES) or levels != {str(LEVEL)}:
        raise SystemExit(f"{TABLE}: stages {sorted(stages)}, levels "
                         f"{sorted(levels)}")
    lists = read_gate_lists()
    jobs = [(line, row, lists.pop(line - 2, None)) for line, row in table]
    if lists:
        raise SystemExit(f"{GATE_LISTS}: blocks {sorted(lists)[:5]} name "
                         f"no row")
    with ProcessPoolExecutor(workers or os.cpu_count()) as pool:
        entries = list(pool.map(entry, jobs, chunksize=1))
    two = [e for (_l, row, _s), e in zip(jobs, entries)
           if row["d"] == DISTANCE]
    more = [e for (_l, row, _s), e in zip(jobs, entries)
            if row["d"] != DISTANCE]
    return two, more, len(table)


# ------------------------------------------------------------- the file
def one_per_line(head, name, items):
    text = json.dumps(head, indent=1, ensure_ascii=False)[:-2]
    body = ",\n".join("  " + json.dumps(item, ensure_ascii=False,
                                         separators=(",", ":"))
                      for item in items)
    return f"{text},\n \"{name}\": [\n{body}\n ]\n}}\n"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def texts(workers=None):
    """``{path: text}`` of both circuit files."""
    two, more, rows = build(workers)
    return {OUT: text(two, "distance-2 row", rows,
                      {"distance 2, listed here": len(two),
                       f"distance 3 or more, in {OUT_D3.name}": len(more)}),
            OUT_D3: text(more, "row at distance 3 or more", rows,
                         {f"distance 2, in {OUT.name}": len(two),
                          "distance 3 or more, listed here": len(more)},
                         floor=True)}


def text(entries, which, rows, counts, floor=False):
    head = {
        "about": (f"Every {which} of the level-3 table of the larger "
                  "unified borrowed-identity search, rebuilt and checked by "
                  "borrowed_identities/export_large_unified.py. Cite "
                  f"{CITATION}."),
        "source": {"repository": REPOSITORY, "commit": COMMIT,
                   "files": {name: sha256(UPSTREAM / "outputs" / name)
                             for name in (TABLE, GATE_LISTS)}},
        "level": LEVEL,
        "rows": {TABLE: rows, **counts},
        "conventions": (
            "n counts the input T states and N (wires) the circuit wires, as "
            "in the upstream table; wires 0..k-1 are the outputs. A two-group "
            "row gives its circuit as construction, which builds its columns "
            "(master_catalog/constructions.py), with columns_sha256 the "
            "SHA-256 of them as compact JSON; every rotation of it is one T. "
            "A gluing row gives gates, each [support, c] the parity rotation "
            "by c*pi/8 on its support, c modulo 8; the odd-c gates consume T "
            "states and are the columns, and even-c gates are Clifford. d is "
            "measured here over the columns, with d_witness the column "
            "indices of an undetectable damaging fault of that weight, and "
            "A_d is the number of such faults."
            + (" d_table is the table's d where it gives only a floor."
               if floor else "")),
    }
    return one_per_line(head, "circuits", entries)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="rebuild and compare with the file on disk")
    parser.add_argument("--workers", type=int, default=None)
    args = parser.parse_args(argv)
    built = texts(args.workers)
    if args.check:
        differ = [path.relative_to(REPO) for path, body in built.items()
                  if not path.exists()
                  or path.read_text(encoding="utf-8") != body]
        print(f"differs: {', '.join(map(str, differ))}" if differ
              else "up to date")
        return 1 if differ else 0
    for path, body in built.items():
        path.write_text(body, encoding="utf-8")
        print(f"wrote {path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
