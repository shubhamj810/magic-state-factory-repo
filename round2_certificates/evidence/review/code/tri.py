#!/usr/bin/env python3
"""Independent gate check, written from the definitions only (no catalogue code).

A column with support S contributes to the Z_8 phase of monomial x^T (T subset of S, |T| <= 3) with weight
+-2^(|T|-1).  So the circuit deposits, on wires, the parities
    n1(i)     = #columns containing i            (mod 2: T^odd on wire i)
    n2(i,j)   = #columns containing i and j      (mod 2: CS-type on (i,j))
    n3(i,j,l) = #columns containing i, j, l      (mod 2: CCZ on (i,j,l))
A factory with pure T on every output needs: n1 odd on every output, n1 even on every check, n2 even on every
pair of distinct wires, n3 even on every triple of distinct wires.  (Any odd parity touching a check is
contamination; an odd pair/triple on outputs is a non-T gate.)  Also: all N rows independent over F_2 (outputs
independent modulo checks and no redundant check).

    python tri.py PROBLEM.json [--triples]
"""
import hashlib
import json
import sys
import time

import numpy as np


def load(path):
    d = json.load(open(path))
    return d


def sha(cols):
    return hashlib.sha256(json.dumps(cols, separators=(",", ":")).encode()).hexdigest()


def gf2_rank(M):
    """rank over F_2 of a 0/1 uint8 matrix (rows), by packed elimination."""
    A = np.packbits(M.astype(np.uint8), axis=1)
    A = A.copy()
    nrows, nbytes = A.shape
    r = 0
    ncols = M.shape[1]
    for c in range(ncols):
        byte, bitpos = divmod(c, 8)
        mask = np.uint8(1 << (7 - bitpos))
        col = (A[r:, byte] & mask) != 0
        idx = np.nonzero(col)[0]
        if idx.size == 0:
            continue
        p = r + idx[0]
        if p != r:
            A[[r, p]] = A[[p, r]]
        others = np.nonzero((A[:, byte] & mask) != 0)[0]
        others = others[others != r]
        if others.size:
            A[others] ^= A[r]
        r += 1
        if r == nrows:
            break
    return r


def check(path, triples=True):
    t0 = time.time()
    d = load(path)
    k, N, cols = d["k"], d["N"], d["columns"]
    n = len(cols)
    res = {"file": str(path), "n": n, "k": k, "N": N, "sha256": sha(cols), "digest_field": d.get("digest")}
    ok_shape = all(isinstance(q, int) and 0 <= q < N for c in cols for q in c) and \
        all(list(c) == sorted(set(c)) for c in cols) and all(len(c) > 0 for c in cols)
    res["shape_ok"] = ok_shape
    M = np.zeros((N, n), dtype=np.float32)
    for j, c in enumerate(cols):
        M[c, j] = 1.0
    n1 = M.sum(axis=1).astype(np.int64)
    res["singles_outputs_all_odd"] = bool(np.all(n1[:k] % 2 == 1))
    res["singles_checks_all_even"] = bool(np.all(n1[k:] % 2 == 0))
    res["n1_mod8_outputs_hist"] = {str(v): int(c) for v, c in zip(*np.unique(n1[:k] % 8, return_counts=True))}
    G = (M @ M.T).astype(np.int64)
    off = G % 2
    np.fill_diagonal(off, 0)
    res["pairs_odd"] = int(off.sum() // 2)
    res["pairs_odd_with_check"] = int((off[:, k:].sum() + off[k:, :k].sum()) // 2 + 0)
    if triples:
        bad = 0
        badex = []
        for i in range(N):
            Mi = M * M[i]
            T = (Mi @ M.T).astype(np.int64) % 2
            # entries (j, l) with i < j < l
            T = np.triu(T, 1)
            T[: i + 1, :] = 0
            nb = int(T.sum())
            if nb:
                bad += nb
                if len(badex) < 5:
                    jj, ll = np.nonzero(T)
                    badex.append([i, int(jj[0]), int(ll[0])])
        res["triples_odd"] = bad
        res["triples_odd_examples"] = badex
    res["rank_all_rows"] = gf2_rank(M.astype(np.uint8))
    res["rank_checks"] = gf2_rank(M[k:].astype(np.uint8))
    res["ok"] = bool(ok_shape and res["singles_outputs_all_odd"] and res["singles_checks_all_even"]
                     and res["pairs_odd"] == 0 and (not triples or res["triples_odd"] == 0)
                     and res["rank_all_rows"] == N and res["rank_checks"] == N - k)
    res["seconds"] = round(time.time() - t0, 1)
    return res


if __name__ == "__main__":
    print(json.dumps(check(sys.argv[1], "--no-triples" not in sys.argv)), flush=True)
