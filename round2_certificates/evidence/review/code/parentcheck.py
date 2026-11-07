#!/usr/bin/env python3
"""Check from scratch that a circuit is the weighted RM code W punctured at P.

W: functions on F_2^11 (point p = y + 256 z, y = bits 0..7 weight 2, z = bits 8..10 weight 1) whose algebraic
normal form uses only monomials of weighted degree <= 6.  For each wire q build v_q on all 2048 points:
the column values off P (column j <-> j-th point of the sorted complement of P), and on P the unit vector at
P[q] for an output q < k, zero for a check.  The circuit is W punctured at P iff every v_q has ANF inside the
allowed monomials and the N = 324 vectors are independent (then they span W, the checks span the words of W
vanishing on P, and output q is a word of W equal to e_{P[q]} on P).

    python parentcheck.py PROBLEM.json
"""
import json
import sys
import time

import numpy as np

M = 11


def allowed_mask():
    a = np.arange(1 << M)
    wz = np.array([bin(x >> 8).count("1") for x in a])
    wy = np.array([bin(x & 255).count("1") for x in a])
    return (wz + 2 * wy) <= 6


def anf(V):
    """Moebius transform over F_2 along the last axis (length 2^M), rows independent."""
    V = V.copy()
    for i in range(M):
        s = 1 << i
        V = V.reshape(V.shape[0], -1, 2 * s)
        V[:, :, s:] ^= V[:, :, :s]
        V = V.reshape(V.shape[0], -1)
    return V


def main(path):
    t0 = time.time()
    d = json.load(open(path))
    k, N, cols = d["k"], d["N"], d["columns"]
    P = sorted(d["points"])
    assert len(P) == k == len(set(P))
    comp = [x for x in range(1 << M) if x not in set(P)]
    assert len(comp) == len(cols)
    V = np.zeros((N, 1 << M), dtype=np.uint8)
    for j, c in enumerate(cols):
        V[c, comp[j]] = 1
    for q in range(k):
        V[q, P[q]] = 1
    A = anf(V)
    ok_mask = allowed_mask()
    outside = A[:, ~ok_mask].sum()
    res = {"file": path, "allowed_monomials": int(ok_mask.sum()), "anf_entries_outside_W": int(outside)}
    # independence of the 324 ANF coefficient vectors restricted to the allowed monomials
    sys.path.insert(0, __file__.rsplit("/", 1)[0])
    from tri import gf2_rank
    res["rank"] = gf2_rank(A[:, ok_mask])
    res["is_W_punctured_at_P"] = bool(outside == 0 and res["rank"] == N == int(ok_mask.sum()))
    res["fibre_sizes"] = [sum(1 for p in P if p >> 8 == z) for z in range(8)]
    res["seconds"] = round(time.time() - t0, 1)
    print(json.dumps(res), flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
