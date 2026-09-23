#!/usr/bin/env python3
"""Credit a classification catalogue on the master rows it certifies.

    python attribute_classification.py classification/rank7_census/catalog/sk_classes_r7.json \\
        --regime "census r<=7" [--dry-run]

WHY THIS EXISTS
---------------
`merge_results.py` keeps the master catalogue's *circuits* honest: a result
that is a class the catalogue already holds, with a circuit no better, is a
``duplicate`` and changes nothing -- not the row, not its ``sources``.  That is
the right rule for search corpora, where re-merging a file must be a no-op.

A CLASSIFICATION is a different kind of statement.  When the complete
``r <= 7, n <= 44`` S_k table says a class exists, that is the strongest claim
the catalogue has about the class -- "classified subject to the check-rank
bound r <= 7" -- whether or not the classification's witness circuit is the
one the catalogue chooses to keep.  The header promises that ``regimes`` "tells
you the strongest claim available for that class" and that ``discovery`` is
``pre-existing`` exactly when a classification catalogue has the class
(`tests/test_master_catalog.py` enforces both).  A class first merged from a
search campaign and later covered by a classification would break both
promises if only the circuit rule ran.

So this tool does the provenance half only, and touches nothing else:

  * for every row whose ``(n, k, d, GL(k,2) gate)`` class holds a class of the
    given classification catalogue -- decided by `glcanon.gl_isomorphic`,
    since the classification tables key on the finer ``S_k`` relation -- and
    whose ``regimes`` do not yet name the regime: append the regime (in the header's strongest-first order), reset
    ``strongest_claim`` from the header, set ``discovery`` to ``pre-existing``,
    and append a ``sources`` entry pointing at the classification's row --
    ``file``, ``label`` (the gate string that file writes) and the ``N`` / ``d``
    IT published, so `verify_catalog._circuit_provenance_problems` and
    `test_source_attribution_is_real` can follow the citation;
  * no circuit field is read or written.  ``columns``, ``N``, ``d``, the gate
    and the metrics are exactly what they were.

Idempotent: a row already naming the regime is skipped, so running this twice
is a no-op the second time.  Both catalogue files are rewritten through
`catalogfile.write`, deterministically, and the run exits non-zero if
`verify_catalog.provenance_problems` reports anything afterwards.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))

import catalogfile as CF                                  # noqa: E402
import gatelabels as GL                                   # noqa: E402
import glcanon as GC                                      # noqa: E402
import verify_catalog as VC                               # noqa: E402


def classification_gate(rec, gate_field):
    """The monomial set a classification row names in ``gate_field``.

    Read by `gatelabels.parse`, the same reader `merge_results` uses, so a
    string it cannot read is refused rather than guessed at.
    """
    kind, monomials, note = GL.parse(rec[gate_field], rec["k"])
    if kind == "unreadable":
        raise SystemExit(f"cannot read the gate {rec[gate_field]!r} of a "
                         f"[[{rec['n']},{rec['k']}]] row: {note}")
    return monomials


def holding_row(rows, rec, gate):
    """The master row whose class holds ``rec``, or ``None``.

    Decided, not hashed: a same-``(n, k)`` row is the holder when
    `glcanon.gl_isomorphic` says so.  An exhausted search is reported and
    treated as no match, which errs toward NOT crediting a classification --
    the provenance a wrong credit would add is a claim, and an omitted one is
    only a missed annotation.
    """
    for row in rows:
        if (row["n"], row["k"], row["d"]) != (rec["n"], rec["k"], rec["d"]):
            continue
        verdict = GC.gl_isomorphic(rec["k"], VC.row_monomials(row), gate)
        if verdict is None:
            print(f"  undecided: [[{rec['n']},{rec['k']}]] {rec.get('gate')} "
                  f"against {row['gate']}; not credited")
        elif verdict:
            return row
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("catalogue", type=Path,
                    help="a classification catalogue JSON with a `factories` list")
    ap.add_argument("--regime", required=True,
                    help="the header regime this catalogue certifies, e.g. 'census r<=7'")
    ap.add_argument("--gate-field", default="gate")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    payload = CF.load()
    header = payload["regimes"]
    if a.regime not in header:
        raise SystemExit(f"regime {a.regime!r} is not one the catalogue header defines; "
                         f"merge at least one row from it first")
    order = list(header)
    rel_file = str(a.catalogue.resolve().relative_to(REPO))

    blob = json.loads(a.catalogue.read_text(encoding="utf-8"))
    recs = blob["factories"] if isinstance(blob, dict) else blob
    # Several classification rows can fall into ONE master class (they are
    # S_k classes, it is a GL(k,2) class), so a row is credited once, from the
    # first classification row that lands in it.
    touched, seen, already, unmatched = [], set(), 0, 0
    for rec in recs:
        row = holding_row(payload["factories"], rec,
                          classification_gate(rec, a.gate_field))
        if row is None:
            unmatched += 1
            continue
        if id(row) in seen:
            continue
        seen.add(id(row))
        if a.regime in row["regimes"]:
            already += 1
            continue
        touched.append((row, rec))
    matched = len(touched) + already

    print(f"{a.catalogue.name}: {len(recs)} classes; they fall into {matched} rows of the "
          f"master catalogue ({already} already credit {a.regime!r}, {len(touched)} do not)"
          + (f"; {unmatched} are not in the master catalogue -- merge them first"
             if unmatched else ""))
    for row, rec in touched:
        print(f"  [[{row['n']},{row['k']},{row['d']}]] {row['gate']}: regimes {row['regimes']} "
              f"-> + {a.regime!r}; discovery {row['discovery']} -> pre-existing")
    if a.dry_run or not touched:
        print("dry run, nothing written" if a.dry_run else "nothing to do")
        return 0

    for row, rec in touched:
        row["regimes"] = sorted(set(row["regimes"]) | {a.regime}, key=order.index)
        row["strongest_claim"] = header[row["regimes"][0]]
        row["discovery"] = "pre-existing"
        row["sources"].append({
            "regime": a.regime,
            "file": rel_file,
            "label": rec[a.gate_field],
            "N": rec["N"], "d": rec["d"], "d_is_exact": True,
            "origin": None,
            "provenance": rec.get("source"),
        })
    problems = VC.provenance_problems(payload)
    if problems:
        for kind, detail in problems:
            print(f"  {kind}: {detail}")
        raise SystemExit("provenance would be inconsistent; nothing written")
    CF.write(payload)
    print(f"wrote master_catalog.json and MASTER_CATALOG.md: {len(touched)} row(s) now credit "
          f"{a.regime!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
