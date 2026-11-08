"""Own meet-in-the-middle fault search (small-review).  No catalogue or agent code.

A fault is a set E of columns; its effect is the XOR of their supports.  It is accepted when the
check part (wires >= k) cancels, and harmful when, in addition, the output part (wires < k) does not.

join(...) finds sets E = F + A + B with F a fixed set, A an a-subset and B a b-subset of the pool U
(A, B, F pairwise disjoint), whose check syndromes cancel.  With F empty and U all columns, a
complete run over weight w = a + b decides whether a harmful set of weight exactly w exists
(each such set is found C(w, a) times, once per ordered split).
"""
from __future__ import annotations

import math
import time

import numpy as np

MUL = np.array([0x9E3779B97F4A7C15, 0xC2B2AE3D27D4EB4F, 0x165667B19E3779F9, 0xD6E8FEB86659FD93,
                0xFF51AFD7ED558CCD, 0xC4CEB9FE1A85EC53, 0x2545F4914F6CDD1D, 0x94D049BB133111EB],
               dtype=np.uint64)


def pack(cols, k, N):
    r = N - k
    wc = max(1, (r + 63) // 64)
    wo = max(1, (k + 63) // 64)
    n = len(cols)
    S = np.zeros((n, wc), np.uint64)
    O = np.zeros((n, wo), np.uint64)
    for j, c in enumerate(cols):
        for w in c:
            if w < k:
                O[j, w // 64] ^= np.uint64(1) << np.uint64(w % 64)
            else:
                q = w - k
                S[j, q // 64] ^= np.uint64(1) << np.uint64(q % 64)
    return S, O


def keyof(S):
    with np.errstate(over="ignore"):
        h = np.zeros(S.shape[0], np.uint64)
        for i in range(S.shape[1]):
            h ^= S[:, i] * MUL[i % len(MUL)]
            h = (h << np.uint64(13)) | (h >> np.uint64(51))
    return h


def combos(m, b):
    """all b-subsets of range(m), lexicographic, int32 (b <= 3)."""
    if b == 0:
        return np.zeros((1, 0), np.int32)
    if b == 1:
        return np.arange(m, dtype=np.int32)[:, None]
    if b == 2:
        i, j = np.triu_indices(m, 1)
        return np.stack([i, j], 1).astype(np.int32)
    out = []
    for i in range(m - 2):
        i2, j2 = np.triu_indices(m - i - 1, 1)
        out.append(np.stack([np.full(len(i2), i), i2 + i + 1, j2 + i + 1], 1).astype(np.int32))
    return np.concatenate(out) if out else np.zeros((0, 3), np.int32)


def xor_rows(M, idx):
    if idx.shape[1] == 0:
        return np.zeros((len(idx), M.shape[1]), M.dtype)
    acc = M[idx[:, 0]].copy()
    for t in range(1, idx.shape[1]):
        acc ^= M[idx[:, t]]
    return acc


def literal_check(cols, k, E):
    """my own XOR of the supports: (check part empty, output part, check part)."""
    acc = set()
    for j in E:
        acc ^= set(cols[j])
    return (not any(w >= k for w in acc)), sorted(w for w in acc if w < k), sorted(w for w in acc if w >= k)


class Packed:
    def __init__(self, cols, k, N):
        self.cols, self.k, self.N = cols, k, N
        self.S, self.O = pack(cols, k, N)
        self.n = len(cols)


def join(P: Packed, a, b, U=None, F=(), stop_first=True, count=False, order=None, max_pairs=20_000_000,
         time_limit=None):
    """a >= b, b <= 3, a <= 4.  Returns dict with harmful witnesses (as column lists), raw counts."""
    t0 = time.time()
    U = range(P.n) if U is None else U
    U = np.asarray(sorted(set(int(x) for x in U) - set(F)), np.int32)
    m = len(U)
    SU, OU = P.S[U], P.O[U]
    sF = np.bitwise_xor.reduce(P.S[list(F)], axis=0) if F else np.zeros(P.S.shape[1], np.uint64)
    oF = np.bitwise_xor.reduce(P.O[list(F)], axis=0) if F else np.zeros(P.O.shape[1], np.uint64)
    # b side, stored and sorted
    Bi = combos(m, b)
    Bs = xor_rows(SU, Bi)
    Bk = keyof(Bs) if b else np.zeros(1, np.uint64)
    o = np.argsort(Bk, kind="stable")
    Bi, Bs, Bk = Bi[o], Bs[o], Bk[o]
    Bo = xor_rows(OU, Bi)
    # a side: first element p, rest from the lexicographic (a-1)-subsets with first element > p
    R = combos(m, a - 1)
    Rs = xor_rows(SU, R)
    Ro = xor_rows(OU, R)
    if a - 1 >= 1:
        start = np.searchsorted(R[:, 0], np.arange(m + 1), "left")  # rows with R[:,0] >= p
    found, raw, acc = [], 0, 0
    firsts = range(m) if order is None else order
    done_all = True
    for p in firsts:
        if time_limit and time.time() - t0 > time_limit:
            done_all = False
            break
        if a == 1:
            Ai = np.array([[p]], np.int32)
            As = SU[[p]] ^ sF
            Ao = OU[[p]] ^ oF
        else:
            s = start[p + 1]
            if s >= len(R):
                continue
            Ai = np.concatenate([np.full((len(R) - s, 1), p, np.int32), R[s:]], 1)
            As = Rs[s:] ^ SU[p] ^ sF
            Ao = Ro[s:] ^ OU[p] ^ oF
        Ak = keyof(As)
        lo = np.searchsorted(Bk, Ak, "left")
        hi = np.searchsorted(Bk, Ak, "right")
        cnt = hi - lo
        tot = int(cnt.sum())
        if tot == 0:
            continue
        ia = np.repeat(np.arange(len(Ai)), cnt)
        off = np.cumsum(cnt) - cnt
        ib = lo[ia] + (np.arange(tot) - off[ia])
        for s0 in range(0, tot, max_pairs):
            xa, xb = ia[s0:s0 + max_pairs], ib[s0:s0 + max_pairs]
            eq = np.all(As[xa] == Bs[xb], axis=1)
            xa, xb = xa[eq], xb[eq]
            if b and len(xa):
                A_, B_ = Ai[xa], Bi[xb]
                disj = np.ones(len(xa), bool)
                for pa in range(a):
                    for qb in range(b):
                        disj &= A_[:, pa] != B_[:, qb]
                xa, xb = xa[disj], xb[disj]
            acc += len(xa)
            outx = Ao[xa] ^ Bo[xb]
            harm = np.any(outx != 0, axis=1)
            nh = int(harm.sum())
            raw += nh
            for t in np.nonzero(harm)[0][: max(0, 3 - len(found))]:
                E = sorted([int(U[x]) for x in Ai[xa[t]]] + [int(U[x]) for x in Bi[xb[t]]] + list(F))
                found.append(E)
        if found and stop_first and not count:
            done_all = False if order is None or len(order) < m else done_all
            break
    w = a + b
    return {"w": w + len(F), "a": a, "b": b, "F": list(F), "pool": m, "witnesses": found,
            "raw": raw, "accepted_raw": acc,
            "count": raw // math.comb(w, a) if (count and done_all and not F and m == P.n) else None,
            "complete_pass": done_all and order is None, "seconds": round(time.time() - t0, 1)}


def split(w):
    b = min(3, w // 2)
    return w - b, b


def sweep(P: Packed, wmax, wmin=1, log=print, count_last=False, time_limit=None):
    """complete sweep of weights wmin..wmax (w <= 7).  Stops at the first weight with a harmful set."""
    out = {}
    for w in range(wmin, wmax + 1):
        a, b = split(w)
        r = join(P, a, b, stop_first=not (count_last and w == wmax), count=count_last and w == wmax,
                 time_limit=time_limit)
        out[w] = r
        log(f"  w={w} (a={a},b={b}) harmful={'yes' if r['witnesses'] else 'no'} complete={r['complete_pass'] or bool(r['witnesses'])} "
            f"count={r['count']} accepted_raw={r['accepted_raw']} {r['seconds']}s")
        if r["witnesses"]:
            break
    return out
