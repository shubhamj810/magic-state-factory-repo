#!/usr/bin/env python3
"""Exact weight enumerators of ker H and ker [H; L] up to weight W by a counting syndrome trellis, and so
A_w = B_w(ker H) - B_w(ker [H; L]) for w <= W (the definition of master_catalog/errorcoeff.py).

The trellis walks the columns in a given order.  After t columns the partial syndrome lies in
S_t = span(first t columns) ∩ span(the rest), whose dimension is the cut rank at t; a state is a vector of S_t
in coordinates of a basis of S_t, and carries the number of prefix subsets of each weight 0..W that reach it.
Column t+1 maps every state s to s and to s + g, and keeps those that lie in S_{t+1}.  Since S_{t+1} lies in
S_t + <g>, every generator of S_t + <g> is written once in a basis of S_{t+1} extended to S_t + <g>; the extra
coordinates say whether a successor is kept.  This file does the linear algebra (Python integers as bit
vectors, Zassenhaus intersections) and writes one step per column; trellis_count.c runs the counting over
the 2^(cut rank) states, with counts modulo 2^64 (exact when the true counts are below 2^64, as the final
ones are here; intermediate wrap-around is harmless because only additions are done).

    python trellis_count.py ROWID W [ORDER.json]     prints {"B_kerH": [...], "B_kerG": [...], "A": [...]}

It shares no code with tropidist, the kernels or faultcore.
"""
import json
import struct
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOP = HERE.parent


def reduce_basis(vecs):
    """Echelon basis {pivot: vector} of the span."""
    piv = {}
    for v in vecs:
        x = v
        while x:
            p = x.bit_length() - 1
            if p in piv:
                x ^= piv[p]
            else:
                piv[p] = x
                break
    return piv


def intersect(U, W, nbits):
    """Basis of span(U) ∩ span(W) (Zassenhaus)."""
    rows = [(u << nbits) | u for u in U] + [w << nbits for w in W]
    piv = {}
    for v in rows:
        x = v
        while x:
            p = x.bit_length() - 1
            if p in piv:
                x ^= piv[p]
            else:
                piv[p] = x
                break
    return [x for p, x in piv.items() if p < nbits]


def steps_for(vecs, nbits, W):
    n = len(vecs)
    # prefix and suffix echelon bases
    pre = [[]]
    piv = {}
    for v in vecs:
        x = v
        while x:
            p = x.bit_length() - 1
            if p in piv:
                x ^= piv[p]
            else:
                piv[p] = x
                break
        pre.append(list(piv.values()))
    suf = [None] * (n + 1)
    suf[n] = []
    piv = {}
    for t in range(n - 1, -1, -1):
        x = vecs[t]
        while x:
            p = x.bit_length() - 1
            if p in piv:
                x ^= piv[p]
            else:
                piv[p] = x
                break
        suf[t] = list(piv.values())
    B = []                                   # basis of S_0 = {0}
    out = []
    maxcut = 0
    for t in range(n):
        g = vecs[t]
        Bn = intersect(pre[t + 1], suf[t + 1], nbits)    # basis of S_{t+1}
        # basis of C = S_t + <g>: Bn first, then extras from B + [g]
        Bc = list(Bn)
        ech = {}                                          # pivot -> (vector, tag)

        def insert(v, tag):
            x, tg = v, tag
            while x:
                p = x.bit_length() - 1
                if p in ech:
                    x ^= ech[p][0]
                    tg ^= ech[p][1]
                else:
                    ech[p] = (x, tg)
                    return True
            return False
        for j, v in enumerate(Bn):
            assert insert(v, 1 << j)
        for v in B + [g]:
            j = len(Bc)
            if insert(v, 1 << j):
                Bc.append(v)
        assert len(Bc) <= 63

        def coords(v):
            x, tg = v, 0
            for p in sorted(ech, reverse=True):
                if (x >> p) & 1:
                    x ^= ech[p][0]
                    tg ^= ech[p][1]
            assert x == 0
            return tg
        # tags are in terms of the inserted vectors; express in terms of Bc: insertion tags were unit vectors
        # of Bc, and the reduction XORs them, so coords(v) is already v's coordinate vector in Bc
        packed = [coords(v) for v in B]
        pg = coords(g)
        out.append((len(B), len(Bn), packed, pg))
        maxcut = max(maxcut, len(Bn))
        B = Bn
    assert B == []
    return out, maxcut


def run(rowid, W, order_file=None, which=("H", "G")):
    row = json.loads((TOP / "data" / "rows" / f"{rowid}.json").read_text())
    k, N = row["k"], row["N"]
    order = json.loads(Path(order_file).read_text()) if order_file else list(range(row["n"]))
    res = {"id": rowid, "sha256": row["sha256"], "W": W, "order": order_file or "stored"}
    for name in which:
        vecs = []
        for j in order:
            c = row["columns"][j]
            if name == "H":
                vecs.append(sum(1 << (q - k) for q in c if q >= k))
            else:
                vecs.append(sum(1 << q for q in c))
        nbits = (N - k) if name == "H" else N
        t0 = time.time()
        steps, maxcut = steps_for(vecs, nbits, W)
        tprep = time.time() - t0
        with tempfile.NamedTemporaryFile(dir=TOP / "tmp", suffix=".bin", delete=False) as f:
            f.write(struct.pack("<iii", len(steps), W, maxcut))
            for a, b, packed, pg in steps:
                f.write(struct.pack("<ii", a, b))
                f.write(struct.pack("<%dQ" % (a + 1), *(packed + [pg])))
            fn = f.name
        t1 = time.time()
        r = subprocess.run([str(HERE / "trellis_count"), fn], capture_output=True, text=True)
        Path(fn).unlink()
        if r.returncode:
            raise SystemExit(r.stderr)
        counts = [int(x) for x in r.stdout.split()]
        res[f"B_ker{name}"] = counts
        res[f"maxcut_{name}"] = maxcut
        res[f"seconds_{name}"] = [round(tprep, 1), round(time.time() - t1, 1)]
    if "B_kerH" in res and "B_kerG" in res:
        res["A"] = [a - b for a, b in zip(res["B_kerH"], res["B_kerG"])]
    return res


if __name__ == "__main__":
    rid, W = sys.argv[1], int(sys.argv[2])
    of = sys.argv[3] if len(sys.argv) > 3 else None
    res = run(rid, W, of)
    print(json.dumps(res))
    with open(TOP / "data" / "trellis_counts.jsonl", "a") as f:
        f.write(json.dumps(res) + "\n")
