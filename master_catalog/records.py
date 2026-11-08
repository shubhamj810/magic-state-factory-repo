#!/usr/bin/env python3
"""Which rows are records, under the owner's rule of 7 November 2026.

    python master_catalog/records.py            # counts per class
    python master_catalog/records.py LABEL ...  # the verdict on some rows

A direct sum of factories is a factory: (n1, k1, d1) and (n2, k2, d2) of one
gate class give (n1 + n2, k1 + k2, min(d1, d2)) of that class. The owner ruled
that a direct sum "can go in but is not a record". So a row (n, k, d) of gate
class C is a **record** when

* no other row of class C has n' <= n, k' >= k and d' >= d with at least one
  of the three strict, and
* no direct sum of two or more rows of class C, each with d_i >= d, has
  n' <= n and k' >= k. A sum that only equals the row's (n, k, d) also takes
  the record away. A row may appear in a sum more than once.

Outputs are counted by ``intrinsic_width``, not ``k``: since 2026-11-07 a
row whose gate has a hidden spectator (an output combination on which it acts
as a Clifford, `glcanon.intrinsic_width`) is ranked, and enters sums, by the
outputs it really uses. ``k`` itself is not changed.

The classes are read off ``gate_human`` in the stored frame: ``T`` (only T
factors), ``CS``, ``CCZ``, ``mixed``, and ``all`` (any gate, any class in a
sum). Two rows with the same (n, k, d) in one class are a tie, and both stay
records unless something else takes it away.

This module only reads rows; nothing in the catalogue files stores a record
status, so it cannot go stale. The website uses it to decide which factories it
presents as best (`website/build_site.py`).

Sums: for each class and distance floor D, the rows with d >= D are reduced
to their Pareto-minimal (n, k) pairs, and an unbounded knapsack gives S[x],
the most outputs a sum of one or more of them reaches with at most x inputs,
and P[x] = max_i (k_i + S[x - n_i]), the most from two or more.
"""
from __future__ import annotations

import sys
from pathlib import Path

CLASSES = ("T", "CS", "CCZ", "mixed", "all")


def gate_class(gate_human: str) -> str:
    """``T``, ``CS``, ``CCZ`` or ``mixed``, from the factors of the gate."""
    kinds = set()
    for factor in gate_human.split("·"):
        if factor.startswith("CCZ"):
            kinds.add("CCZ")
        elif factor.startswith("CS"):
            kinds.add("CS")
        elif factor.startswith("T"):
            kinds.add("T")
        else:
            raise ValueError(f"unknown factor {factor!r} in a gate")
    if not kinds:
        raise ValueError("an empty gate")
    return kinds.pop() if len(kinds) == 1 else "mixed"


def pareto_items(pairs):
    """The (n, k) pairs no other pair matches with n' <= n and k' >= k."""
    best = {}
    for n, k in pairs:
        best[n] = max(best.get(n, 0), k)
    items, top = [], 0
    for n in sorted(best):
        if best[n] > top:
            items.append((n, best[n]))
            top = best[n]
    return items


def sums_of_two_or_more(items, nmax):
    """P[x], x = 0..nmax: the most outputs of a sum of two or more items with
    at most x inputs in all, or -1 where there is none."""
    S = [-1] * (nmax + 1)
    P = [-1] * (nmax + 1)
    for x in range(1, nmax + 1):
        s, p = S[x - 1], P[x - 1]
        for n, k in items:
            if n > x:
                break
            s = max(s, k)
            rest = S[x - n]
            if rest >= 0:
                s = max(s, rest + k)
                p = max(p, rest + k)
        S[x], P[x] = s, p
    return P


def status(rows):
    """``{catalog_label: {class: verdict}}`` for every row and every class it
    is in (its own and ``all``). A verdict is ``{"record": bool,
    "dominated_by": label or None, "sum_reaches": k or None}``."""
    facts = [{"label": r["catalog_label"], "n": r["n"], "k": r["intrinsic_width"],
              "d": r["d"], "cls": gate_class(r["gate_human"])} for r in rows]
    out = {f["label"]: {} for f in facts}
    for C in CLASSES:
        mine = [f for f in facts if C == "all" or f["cls"] == C]
        for D in sorted({f["d"] for f in mine}):
            judged = [f for f in mine if f["d"] == D]
            pool = [f for f in mine if f["d"] >= D]
            items = pareto_items([(f["n"], f["k"]) for f in pool])
            P = sums_of_two_or_more(items, max(f["n"] for f in judged))
            # one row's single dominator: the pool sorted so a scan stops early
            ordered = sorted(pool, key=lambda f: (f["n"], -f["k"], -f["d"]))
            for f in judged:
                single = None
                for g in ordered:
                    if g["n"] > f["n"]:
                        break
                    if g is not f and g["k"] >= f["k"] and g["d"] >= f["d"] \
                            and (g["n"], g["k"], g["d"]) != (f["n"], f["k"], f["d"]):
                        single = g
                        break
                summed = P[f["n"]] >= f["k"]
                out[f["label"]][C] = {
                    "record": single is None and not summed,
                    "dominated_by": single["label"] if single else None,
                    "sum_reaches": P[f["n"]] if summed else None}
    return out


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import catalogfile as CF
    rows = CF.load_all()["factories"]
    verdicts = status(rows)
    if argv:
        for label in argv:
            print(label, verdicts[label])
        return 0
    for C in CLASSES:
        mine = [v[C] for v in verdicts.values() if C in v]
        print(f"{C}: {sum(v['record'] for v in mine)} records of {len(mine)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
