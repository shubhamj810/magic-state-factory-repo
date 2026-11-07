#!/usr/bin/env python3
"""A_8 of 512.39.6.a by a literal count over the affine 3-flats of F_2^9.

The columns of 512.39.6.a are the 512 points of F_2^9 (parents REPORT §2, frame_identity.py).  This script
does not use that identification as given: it finds 9 check wires of weight 256 whose incidence vectors
give every column a distinct 9-bit label, and then checks that every check wire is a product of at most 2
of these coordinates and every output wire a product of exactly 3 (so the circuit is the m = 9 monomial
frame).  Then it lists all 3-dimensional subspaces V of F_2^9 in reduced echelon form (their number must be
the Gaussian binomial [9, 3]_2 = 788,035) and, for each V and each of its 64 cosets a + V, XORs the 8
columns' check masks and output masks literally.  It reports how many 3-flats the checks accept (must be all)
and how many of those flip an output.

Every undetected fault of weight 8 is a 3-flat because the accepted faults are the words of the dual of
RM(2, 9), which is RM(6, 9), and its minimum-weight words are the 3-flats (MacWilliams and Sloane, ch. 13,
Thm 8).  The count of harmful 3-flats is then A_8.

usage: python flat512.py      (about 10 s)
"""
import json
import sys
import time
from itertools import combinations
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def main():
    t0 = time.time()
    row = json.loads((HERE / "data" / "rows" / "512.39.6.a.json").read_text())
    cols, k, N = row["columns"], row["k"], row["N"]
    n = len(cols)
    assert n == 512
    inc = np.zeros((N, n), dtype=np.uint8)
    for j, c in enumerate(cols):
        inc[c, j] = 1
    weight = inc.sum(axis=1)
    half = [w for w in range(k, N) if weight[w] == 256]
    # choose 9 weight-256 checks giving distinct labels (greedy over the independent ones)
    coords = []
    for w in half:
        trial = coords + [w]
        lab = np.zeros(n, dtype=np.int64)
        for b, ww in enumerate(trial):
            lab |= inc[ww].astype(np.int64) << b
        if len(np.unique(lab)) == 2 ** len(trial):
            coords = trial
        if len(coords) == 9:
            break
    assert len(coords) == 9, coords
    label = np.zeros(n, dtype=np.int64)
    for b, ww in enumerate(coords):
        label |= inc[ww].astype(np.int64) << b
    assert sorted(label.tolist()) == list(range(512))
    col_of = np.empty(512, dtype=np.int64)
    col_of[label] = np.arange(n)
    # every wire as a monomial in the coordinates: its incidence must equal prod_{i in S} x_i for one S
    x = np.array([[(p >> b) & 1 for b in range(9)] for p in range(512)], dtype=np.uint8)   # x[p, b]
    def monomial(w):
        pts = inc[w][col_of]                    # indicator over points p
        for deg in range(0, 10):
            for S in combinations(range(9), deg):
                v = np.ones(512, dtype=np.uint8)
                for b in S:
                    v &= x[:, b]
                if np.array_equal(v, pts):
                    return S
        return None
    mons = {w: monomial(w) for w in range(N)}
    assert all(m is not None for m in mons.values())
    assert all(len(mons[w]) <= 2 for w in range(k, N)), "a check of degree > 2"
    assert all(len(mons[w]) == 3 for w in range(k)), "an output not of degree 3"
    assert len({mons[w] for w in range(N)}) == N
    # masks per POINT
    chk = np.zeros(512, dtype=np.uint64)
    out = np.zeros(512, dtype=np.uint64)
    for p in range(512):
        for q in cols[col_of[p]]:
            if q < k:
                out[p] |= np.uint64(1) << np.uint64(q)
            else:
                chk[p] |= np.uint64(1) << np.uint64(q - k)
    # 3-dim subspaces in reduced echelon form: pivots p1 > p2 > p3 (highest set bit of each basis vector)
    bases = []
    for piv in combinations(range(8, -1, -1), 3):
        free = [[b for b in range(piv[i]) if b not in piv] for i in range(3)]
        sizes = [len(f) for f in free]
        for m0 in range(1 << sizes[0]):
            v0 = (1 << piv[0]) | sum(1 << free[0][t] for t in range(sizes[0]) if (m0 >> t) & 1)
            for m1 in range(1 << sizes[1]):
                v1 = (1 << piv[1]) | sum(1 << free[1][t] for t in range(sizes[1]) if (m1 >> t) & 1)
                for m2 in range(1 << sizes[2]):
                    v2 = (1 << piv[2]) | sum(1 << free[2][t] for t in range(sizes[2]) if (m2 >> t) & 1)
                    bases.append((v0, v1, v2))
    nV = len(bases)
    assert nV == 788035, nV
    B = np.array(bases, dtype=np.int64)
    span = np.stack([np.zeros(nV, dtype=np.int64), B[:, 0], B[:, 1], B[:, 0] ^ B[:, 1], B[:, 2],
                     B[:, 0] ^ B[:, 2], B[:, 1] ^ B[:, 2], B[:, 0] ^ B[:, 1] ^ B[:, 2]], axis=1)   # nV x 8
    assert all(len(set(r)) == 8 for r in span[:1000].tolist())
    pts = np.arange(512, dtype=np.int64)
    accepted = harmful = 0
    harmful_subspaces = 0
    per_output = np.zeros(k, dtype=np.int64)
    for lo in range(0, nV, 2048):
        sp = span[lo:lo + 2048]                                 # b x 8
        idx = pts[None, None, :] ^ sp[:, :, None]               # b x 8 x 512: point a ^ v
        cx = np.bitwise_xor.reduce(chk[idx], axis=1)            # b x 512 (each coset 8 times)
        ox = np.bitwise_xor.reduce(out[idx], axis=1)
        acc = cx == 0
        har = acc & (ox != 0)
        accepted += int(acc.sum())
        harmful += int(har.sum())
        harmful_subspaces += int(har.any(axis=1).sum())
        for q in range(k):
            per_output[q] += int((((ox >> np.uint64(q)) & np.uint64(1)) == 1).sum())
    assert accepted % 8 == 0 and harmful % 8 == 0
    res = {"row": "512.39.6.a", "sha256": row["sha256"], "subspaces": nV, "flats": nV * 64,
           "accepted_flats": accepted // 8, "harmful_flats": harmful // 8, "subspaces_with_harmful_coset": harmful_subspaces,
           "flips_per_output_min_max": [int(per_output.min() // 8), int(per_output.max() // 8)],
           "coordinates_wires": coords, "seconds": round(time.time() - t0, 1)}
    print(json.dumps(res))
    with open(HERE / "data" / "flat512.json", "w") as f:
        json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
