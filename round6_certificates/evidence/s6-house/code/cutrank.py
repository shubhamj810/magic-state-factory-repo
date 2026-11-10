#!/usr/bin/env python3
"""Cut rank of a column order: max over t of rank(G[:, :t]) + rank(G[:, t:]) - rank(G), G = all N wire rows.

    python cutrank.py ROWID [natural|reverse|file:ORDER.json]

This is the quantity tropidist's dense DP reports as cut_rank (research/tropidist/work/dp_estimates.json:
599.1.6.a has 39 in the best of the orders it tries).  A column order with a smaller maximum shrinks
the DP table by a factor 2 per unit.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def colvecs(row):
    return [sum(1 << q for q in c) for c in row["columns"]]


def prefix_ranks(vecs):
    basis = {}          # pivot bit -> vector
    out = [0]
    for v in vecs:
        x = v
        while x:
            p = x.bit_length() - 1
            if p in basis:
                x ^= basis[p]
            else:
                basis[p] = x
                break
        out.append(len(basis))
    return out


def profile(vecs):
    pre = prefix_ranks(vecs)
    suf = prefix_ranks(vecs[::-1])[::-1]
    tot = pre[-1]
    return [pre[t] + suf[t] - tot for t in range(len(vecs) + 1)]


def main():
    row = json.loads((HERE / "data" / "rows" / f"{sys.argv[1]}.json").read_text())
    vecs = colvecs(row)
    how = sys.argv[2] if len(sys.argv) > 2 else "natural"
    if how == "natural":
        order = list(range(len(vecs)))
    elif how == "reverse":
        order = list(range(len(vecs)))[::-1]
    else:
        order = json.loads(Path(how[5:]).read_text())
    prof = profile([vecs[i] for i in order])
    print(json.dumps({"id": sys.argv[1], "order": how, "cut_rank": max(prof), "argmax": prof.index(max(prof))}))


if __name__ == "__main__":
    main()
