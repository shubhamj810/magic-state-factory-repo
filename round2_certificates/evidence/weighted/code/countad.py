#!/usr/bin/env python3
"""Exact A_D and the coefficient c (harmful (fault, flipped output) pairs at weight D, over k) for a puncture set
of the parent W, by the fibre decomposition of fibproof.py.

Valid when fibproof proved d >= D with case A's bound above D (so no case-A word has weight D) and the least
case-B weight e satisfies (D - 2e) >= 0.  Then a weight-D dual word is either
  C: one fibre with a nonzero h in RM(4,8), |h minus P_z| = D (from the RM(3,8) problem's harmful list at D), or
  B: a set K of at least two fibres with h_z in RM(5,8) of nonzero classes kappa_z summing to zero, the other
     fibres zero, and sum of |h_z minus P_z| = D (from the RM(2,8) problems' lists).
A fibre outside K with a nonzero RM(4,8) word would add at least d3 >= D, so it cannot occur in B.  The number
of flipped outputs of a word is sum_z |h_z cap P_z|.

    python3 countad.py PROBLEM.json D
"""
from __future__ import annotations

import itertools
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fibproof as FP  # noqa: E402
import monomial as MO  # noqa: E402
import sj_sweep as SW  # noqa: E402


def lists(Pz, r, weights):
    """for the RM(r,8) problem punctured at Pz: arrays (kappa, w, flips) of every harmful set with weight in weights
    (kappa = cubic moments of h = set plus its output punctures; flips = number of punctures in h)."""
    f = MO.factory(8, FP.rm_delta(8, r), list(Pz))
    k, N, cols, surv = f
    syn, out = SW.masks(cols, k)
    PH = [FP.phi3(x) for x in range(256)]
    phP = [PH[x] for x in Pz]
    K, Wt, Fl = [], [], []
    with tempfile.TemporaryDirectory(dir=SW.TMP) as tmp:
        p = Path(tmp) / "p.bin"
        SW.write_problem(p, syn, out, k)
        for w in weights:
            if w == 1:
                rows = [([surv[j]], o) for j, (s, o) in enumerate(zip(syn, out)) if s == 0 and o]
            else:
                lst = Path(tmp) / f"l{w}.txt"
                rr = SW.run_bin(p, w, extra=["--list", str(lst)])
                assert rr["complete"] == 1
                rows = []
                with open(lst) as fh:
                    for line in fh:
                        idx, hx = line.split(":")
                        o = 0
                        for i, wd in enumerate(hx.split()):
                            o |= int(wd, 16) << (64 * i)
                        rows.append(([surv[int(t)] for t in idx.split()], o))
                lst.unlink()
            for svs, o in rows:
                kap = 0
                for x in svs:
                    kap ^= PH[x]
                fl, i, oo = 0, 0, o
                while oo:
                    if oo & 1:
                        kap ^= phP[i]
                        fl += 1
                    oo >>= 1
                    i += 1
                K.append(kap); Wt.append(w); Fl.append(fl)
    return np.array(K, dtype=np.uint64), np.array(Wt, dtype=np.int64), np.array(Fl, dtype=np.int64)


def grouped(K, Wt, Fl, w):
    """class -> (count, total flips) for entries of weight w with nonzero class, as sorted arrays"""
    m = (Wt == w) & (K != 0)
    k, f = K[m], Fl[m]
    if len(k) == 0:
        return np.zeros(0, np.uint64), np.zeros(0, np.int64), np.zeros(0, np.int64)
    u, inv = np.unique(k, return_inverse=True)
    cnt = np.bincount(inv).astype(np.int64)
    fl = np.bincount(inv, weights=f).astype(np.int64)
    return u, cnt, fl


def main():
    prob = json.loads(Path(sys.argv[1]).read_text())
    D = int(sys.argv[2])
    P = prob["points"]
    fib = {z: sorted(p & 255 for p in P if p >> 8 == z) for z in range(8)}
    A, flips = 0, 0
    # case C
    cC, fC = 0, 0
    for z, Pz in fib.items():
        K, Wt, Fl = lists(Pz, 3, [D])
        cC += len(K)
        fC += int(Fl.sum())
    print(json.dumps({"case": "C", "faults": cC, "flips": fC}), flush=True)
    # case B
    wmin = 2
    G = {}
    for z, Pz in fib.items():
        K, Wt, Fl = lists(Pz, 2, list(range(1, D - wmin + 1)))
        assert not np.any((Wt == 1) & (K != 0)), "a weight-1 class: extend the combination search"
        G[z] = {w: grouped(K, Wt, Fl, w) for w in range(wmin, D - wmin + 1)}
        print(json.dumps({"case": "B", "fibre": z, "entries": int(len(K))}), flush=True)
    cB, fB = 0, 0
    # pairs: same class, weights a + b = D
    for z1, z2 in itertools.combinations(range(8), 2):
        for a in range(wmin, D - wmin + 1):
            b = D - a
            u1, n1, f1 = G[z1][a]
            u2, n2, f2 = G[z2][b]
            com, i1, i2 = np.intersect1d(u1, u2, assume_unique=True, return_indices=True)
            cB += int((n1[i1] * n2[i2]).sum())
            fB += int((f1[i1] * n2[i2] + n1[i1] * f2[i2]).sum())
    # triples (and four fibres when 4 * wmin <= D): weights from the small lists
    def combos(parts, total):
        if parts == 1:
            if wmin <= total <= D:
                yield (total,)
            return
        for a in range(wmin, total - wmin * (parts - 1) + 1):
            for rest in combos(parts - 1, total - a):
                yield (a,) + rest
    for parts in range(3, D // wmin + 1):
        for zs in itertools.combinations(range(8), parts):
            for ws in combos(parts, D):
                # meet in the middle: all but the last fibre enumerated, last looked up
                dicts = [dict(zip(G[z][w][0].tolist(), zip(G[z][w][1].tolist(), G[z][w][2].tolist())))
                         for z, w in zip(zs, ws)]
                def rec(i, kap, n, f):
                    nonlocal cB, fB
                    if i == parts - 1:
                        e = dicts[i].get(kap)
                        if e:
                            cB += n * e[0]
                            fB += f * e[0] + n * e[1]
                        return
                    for k2, (n2, f2) in dicts[i].items():
                        rec(i + 1, kap ^ k2, n * n2, f * n2 + n * f2)
                rec(0, 0, 1, 0)
    print(json.dumps({"case": "B", "faults": cB, "flips": fB}), flush=True)
    A, flips = cC + cB, fC + fB
    res = {"digest": prob["digest"], "D": D, "A_D": A, "flips": flips, "k": prob["k"], "c": flips / prob["k"],
           "case_C_faults": cC, "case_B_faults": cB}
    print(json.dumps(res), flush=True)
    with open(HERE.parent / "data" / "A_d.jsonl", "a") as fh:
        fh.write(json.dumps(res) + "\n")


if __name__ == "__main__":
    main()
