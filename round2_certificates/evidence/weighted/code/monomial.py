#!/usr/bin/env python3
"""Punctured monomial parents (weighted Reed–Muller codes in Wills's framework, arXiv:2608.24000), with
arbitrary puncture sets, built as catalogue circuits, and their distances measured with the kernel.

Parent: the squarefree monomials x^a (a an m-bit mask) of weighted degree <= cutoff, evaluated at the 2^m
points (monomial a is 1 at point p iff p & a == a).  The parent is triorthogonal at the level of parities
when every union of three monomials misses a variable: popcount(a | b | c) < m for all a, b, c in Delta
(the product monomial then has even weight); `parent` asserts it.

Puncturing (standard systematic construction): row-reduce the parent rows on the puncture columns to
[I_t; 0] (the puncture columns must be independent), delete them; the t systematic rows are the outputs
(odd weight), the rest the checks.  Column of survivor point x = the rows that are 1 at x.

    python3 monomial.py demo
"""
from __future__ import annotations

import itertools
import json
import os
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def parent(m, weights, cutoff):
    delta = [a for a in range(1 << m)
             if sum(weights[i] for i in range(m) if a >> i & 1) <= cutoff]
    # parity-level triorthogonality: every triple union misses a variable
    full = (1 << m) - 1
    unions2 = {a | b for a in delta for b in delta}
    bad = [u for u in unions2 if any((u | c) == full for c in delta)]
    return delta, (not bad)


def rows_of(m, delta):
    """row i = bitmask over the 2^m points of monomial delta[i]"""
    out = []
    for a in delta:
        r = 0
        for p in range(1 << m):
            if p & a == a:
                r |= 1 << p
        out.append(r)
    return out


def factory(m, delta, P, rows=None):
    """(k, N, columns, survivors) for puncture list P, or None if the puncture columns are dependent."""
    rows = list(rows if rows is not None else rows_of(m, delta))
    t = len(P)
    order = []
    used = [False] * len(rows)
    for j, p in enumerate(P):
        piv = next((i for i in range(len(rows)) if not used[i] and rows[i] >> p & 1), None)
        if piv is None:
            return None
        used[piv] = True
        order.append(piv)
        for i in range(len(rows)):
            if i != piv and rows[i] >> p & 1:
                rows[i] ^= rows[piv]
    outs = [rows[i] for i in order]
    checks = [rows[i] for i in range(len(rows)) if not used[i]]
    allrows = outs + checks
    Pset = set(P)
    surv = [x for x in range(1 << m) if x not in Pset]
    columns = []
    for x in surv:
        columns.append([i for i, r in enumerate(allrows) if r >> x & 1])
    k, N = t, len(allrows)
    return k, N, columns, surv


def kernel_distance(columns, k, N, wmax, stop_at_found=True, timeout=None):
    """Sweep weights 1..wmax with the kernel in status mode; returns (floor, witness or None, per-weight)."""
    import sj_sweep as SW
    syn, out = SW.masks(columns, k)
    SW.TMP.mkdir(parents=True, exist_ok=True)
    per = {}
    with tempfile.TemporaryDirectory(dir=SW.TMP) as tmp:
        p = Path(tmp) / "p.bin"
        SW.write_problem(p, syn, out, k)
        floor = 1
        for w in range(1, wmax + 1):
            t = time.time()
            r = SW.run_bin(p, w, timeout=timeout)
            per[w] = {"status": r["status"], "seconds": round(time.time() - t, 2)}
            if r["status"] == "found":
                per[w]["witness"] = sorted(r["witness"])
                return floor, sorted(r["witness"]), per
            if r["status"] != "clean":
                return floor, None, per
            floor = w + 1
    return floor, None, per


def demo():
    m, weights, cutoff = 9, [1, 1, 1, 1, 1, 2, 2, 2, 2], 4
    delta, ok = parent(m, weights, cutoff)
    print("parent dim", len(delta), "triorthogonal", ok)
    rows = rows_of(m, delta)
    # the release's [[486,26,6]]: light points of Hamming weight <= 3
    P = [x for x in range(32) if bin(x).count("1") <= 3]
    f = factory(m, delta, P, rows)
    k, N, cols, _ = f
    print("486-type:", len(cols), k, N, kernel_distance(cols, k, N, 7)[:2])


if __name__ == "__main__":
    demo()
