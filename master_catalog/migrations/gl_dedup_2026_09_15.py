#!/usr/bin/env python3
"""One-off migration: re-key the master catalogue from S_k to GL(k,2) classes.

    python master_catalog/migrations/gl_dedup_2026_09_15.py [--dry-run]

Until 2026-09-15 a row was one ``(n, k, S_k gate)`` class: gates equal up to a
permutation of the outputs.  From then on a row is one ``(n, k, d, GL(k,2)
gate)`` class: circuits at the same distance whose gates are equal up to an
invertible change of the output basis and diagonal Clifford corrections (the
CNOT+S output equivalence of the length-54 classification).  Several S_k rows
therefore collapse into one; rows at different distances never do.

What this does, and nothing else:

1.  Groups the rows of each ``(n, k, d)`` into GL(k,2) classes with
    `glcanon.gl_isomorphic`, reading every gate off the row's own columns.  An
    undecided pair stops the migration: a class boundary nobody proved is not
    one this script will draw.
2.  Keeps, for each class, the circuit `merge_results.retention_key` prefers --
    the rule every merge already applies (fewest ambient qubits, then fewest
    columns, then the strongest proved distance, then a proved frame).  Among
    circuits that rule ties, it keeps the frame whose gate is simplest to read
    -- fewest ``CCZ``s, then fewest ``CS``s, then fewest monomials -- so a class
    of ``T0.T1`` and ``T0.CS01`` circuits of equal width is shown as ``T0.T1``.  Its circuit fields and notes are untouched.
3.  Folds the other members' PROVENANCE into it, exactly as an ``improved``
    merge does: ``regimes`` unioned in the header's strongest-first order,
    ``strongest_claim`` re-read from the header, ``discovery`` ``pre-existing``
    if any member was, and every member's ``sources`` appended in catalogue
    order, so the history of each absorbed circuit survives.
4.  Rewrites the tail of ``sk_key_note`` on the rows that carry one: it said
    the class was keyed on the permutation-invariant fingerprint, which the
    re-key makes false.  The rest of the note -- which ``k!`` minimisation was
    not proved, and that the circuit is shown as found -- still holds.
5.  Gives every row the default ``citations`` for its length
    (`merge_results.default_citations`) and registers those works in the new
    header ``references`` map.  Literature citations are added separately.
6.  Rewrites the header's ``scope`` and ``dedup_key`` sentences, re-sorts on
    `merge_results.sort_key`, and writes both files through `catalogfile.write`.

The result is then checked with the file-level passes before anything is
written; the full row-level re-verification is `verify_catalog.py`.
"""
from __future__ import annotations

import argparse
import collections
import copy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE.parent
sys.path.insert(0, str(CATALOGUE))

import catalogfile as CF                                          # noqa: E402
import glcanon as GC                                              # noqa: E402
import merge_results as MR                                        # noqa: E402
import verify_catalog as VC                                       # noqa: E402

SCOPE = ("every Clifford level-3, distance >= 3 factory this collection holds, "
         "deduplicated on (n, k, d, GL(k,2) class of the gate); rows arrive from "
         "the repository's classification catalogues and from search campaigns "
         "merged in by merge_results.py")
DEDUP_KEY = ("(n, k, d, gate up to GL(k,2)) -- circuits at different distances "
             "are always different classes; at one distance two gates are one "
             "class when an "
             "invertible change of the output basis (a CNOT frame) and "
             "diagonal Clifford corrections carry one to the other, the CNOT+S "
             "output equivalence; decided for every same-(n,k,d) pair by "
             "glcanon.gl_isomorphic. The stored circuit is one representative, "
             "shown in its S_k-canonical frame where that was proved")


def classes_of(rows):
    """The GL(k,2) classes, as lists of row indices in catalogue order."""
    by_shape = collections.defaultdict(list)
    for index, row in enumerate(rows):
        by_shape[(row["n"], row["k"], row["d"])].append(index)
    classes = []
    for (n, k, d), indices in by_shape.items():
        gates = {i: VC.row_monomials(rows[i]) for i in indices}
        groups: list[list[int]] = []
        for i in indices:
            for group in groups:
                verdict = GC.gl_isomorphic(k, gates[group[0]], gates[i])
                if verdict is None:
                    raise SystemExit(
                        f"[[{n},{k},{d}]] {rows[group[0]]['gate']} against "
                        f"{rows[i]['gate']}: the GL(k,2) search ran out of "
                        f"budget; refusing to guess a class boundary")
                if verdict:
                    group.append(i)
                    break
            else:
                groups.append([i])
        classes += groups
    return classes


def _profile(gate):
    """``(#CCZ, #CS, #monomials)``: lower reads more simply."""
    return (sum(1 for m in gate if len(m) == 3),
            sum(1 for m in gate if len(m) == 2), len(gate))


def fold(rows, members, regimes):
    """One row for a class: the retained circuit with every member's history."""
    keep = min(members, key=lambda i: (MR.retention_key(rows[i]),
                                       _profile(VC.row_monomials(rows[i])),
                                       MR.sort_key(rows[i])))
    row = copy.deepcopy(rows[keep])
    order = list(regimes)
    for i in members:
        if i == keep:
            continue
        other = rows[i]
        row["regimes"] = sorted(set(row["regimes"]) | set(other["regimes"]),
                                key=order.index)
        if other["discovery"] == "pre-existing":
            row["discovery"] = "pre-existing"
        row["sources"] = row["sources"] + copy.deepcopy(other["sources"])
    row["strongest_claim"] = regimes[row["regimes"][0]]
    return row


def migrate(payload):
    rows = payload["factories"]
    classes = classes_of(rows)
    folded = [fold(rows, members, payload["regimes"]) for members in classes]
    references = {}
    stale = ("; the class key is the permutation-invariant fingerprint and "
             "uniqueness was checked by explicit isomorphism test")
    fresh = ("; only the displayed labelling is affected, and this row's class "
             "was decided against every other row of its shape by "
             "glcanon.gl_isomorphic")
    for row in folded:
        row.pop("dedup_note", None)
        if row.get("sk_key_note", "").endswith(stale):
            row["sk_key_note"] = row["sk_key_note"][:-len(stale)] + fresh
        row["citations"] = MR.default_citations(row["n"])
        for key in row["citations"]:
            references.setdefault(key, dict(MR.DEFAULT_REFERENCES[key]))
    folded.sort(key=MR.sort_key)
    payload["factories"] = folded
    payload["n_classes"] = len(folded)
    payload["scope"] = SCOPE
    payload["dedup_key"] = DEDUP_KEY
    # ordered like a bibliography: the classification, then the report
    payload["references"] = {key: references[key]
                             for key in MR.DEFAULT_REFERENCES if key in references}
    return classes


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load()
    before = len(payload["factories"])
    noted = [r for r in payload["factories"] if "dedup_note" in r]
    classes = migrate(payload)
    merged = sum(len(c) - 1 for c in classes)
    print(f"{before} S_k rows -> {len(classes)} GL(k,2) classes "
          f"({merged} rows folded into another row's class)")
    if noted:
        print(f"note: {len(noted)} row(s) carried a dedup_note about S_k "
              f"distinctness; the GL(k,2) passes re-decide them")
    residue = (VC.duplicate_class_problems(payload["factories"])
               + VC.provenance_problems(payload)
               + VC.citation_problems(payload)
               + VC.header_problems(payload))
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the migrated catalogue fails file-level checks; "
                         "nothing written")
    if args.dry_run:
        print("dry run: nothing written")
        return 0
    CF.write(payload)
    print("wrote master_catalog.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
