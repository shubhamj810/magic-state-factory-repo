#!/usr/bin/env python3
"""Search for the self-dual [70,35] code behind the [[69,1,13]] of Table I.

    .venv/bin/python transversal_t_codes/search_sd70.py      # ~2 min on 16 cores

Jain and Albert's Table I needs a self-dual CSS code ``[[69,1,13]]`` with
logical X on every qubit.  Their puncture-and-dualise map gives one from a
self-dual ``[70,35]`` code ``S`` and a coordinate ``p``: puncture ``S`` at
``p``, and the code's distance is one less than the lightest word of ``S``
through ``p``.  So what is needed is a self-dual ``[70,35]`` code whose words
through ``p`` all weigh at least 14 -- lighter words that miss ``p`` are
allowed.  (The paper cites a ``[70,35,14]`` code of Gulliver and Harada, which
is only formally self-dual, and no self-dual ``[70,35,14]`` code is known.)

Two families can be ruled out by hand: a pure double-circulant code's every
nonzero word touches both circulant halves, whose coordinates its shifts
permute transitively, so it would need distance 14 outright; and a bordered
double-circulant self-dual code of length 70 does not exist (the conditions
reduce to ``b(x)^2 = x mod (x+1)^2``).  Codes with special coordinates are the
place to look, and this script searches all of one such family exhaustively:

**every self-dual [70,35] code with an automorphism of order 23 that has three
23-cycles and one fixed point**, up to equivalence.  By Huffman and Yorgov such
a code is ``F + E``: ``F`` the words constant on each cycle, contracting to a
self-dual ``[4,2]`` code, so ``{cycle 1 + p, cycle 2 + cycle 3}`` up to
relabelling; and ``E = M1 + M2``, where the even-weight polynomials mod
``x^23 - 1`` split into two fields ``I1, I2`` of order ``2^11`` (the two
``[23,11,8]`` even Golay subcodes), ``M1`` is a subspace of ``I1^3`` and ``M2``
the subspace of ``I2^3`` orthogonal to it.  Up to the multiplier ``x -> x^-1``,
``M1`` is one-dimensional, spanned by ``u = (u1, u2, u3)``; up to shifting each
cycle, Frobenius and swapping cycles 2 and 3 that leaves 386 codes.  For each,
every codeword of weight at most 12 is enumerated exactly (two disjoint
information sets of 35 coordinates; a word of weight <= 12 has at most 6 ones
on one of them), and the coordinates none of them touch are reported.

Exactly one of the 386 has such a coordinate: the fixed point.  It is a
``[70,35,12]`` code, and `build_codes.py` builds it from the ``u`` printed here
(``SD70_U``); its tests prove the property again by enumerating all ``2^34``
words through the fixed point.
"""
from __future__ import annotations

import collections
import itertools
import multiprocessing as mp
import sys
import time

import numpy as np

P = 23
FULL = (1 << P) - 1
N = 70
PBIT = 69


# ---------------------------------------------------- F2[x]/(x^23 - 1)
def mul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> P:
            a = (a & FULL) | 1
    return r


def power(a, e, one):
    r = one
    while e:
        if e & 1:
            r = mul(r, a)
        a = mul(a, a)
        e >>= 1
    return r


def bits(*exps):
    return sum(1 << e for e in exps)


G1 = bits(11, 10, 6, 5, 4, 2, 0)              # the two Golay factors of
G2 = bits(11, 9, 7, 6, 5, 1, 0)               # (x^23 - 1)/(x + 1)


def ideal(gen):
    span = {0}
    for k in range(P):
        s = mul(gen, 1 << k)
        span |= {x ^ s for x in span}
    return span


I1 = ideal(mul(bits(1, 0), G2))
I2 = ideal(mul(bits(1, 0), G1))
E1 = min(e for e in I1 if e and mul(e, e) == e)                # identity of I1
GAMMA = min(g for g in I1 if g and power(g, 2047 // 23, E1) != E1
            and power(g, 2047 // 89, E1) != E1)                # generates I1*
#: cosets of the order-23 subgroup {x^k E1} (cycle shifts): 0, then GAMMA^j
REPS = [0] + [power(GAMMA, j, E1) for j in range(89)]


# ------------------------------------------------------------- GF(2)
def rref(rows, n):
    rows = list(rows)
    out, pivots = [], []
    for col in range(n):
        bit = 1 << col
        idx = next((i for i, r in enumerate(rows) if r & bit), None)
        if idx is None:
            continue
        piv = rows.pop(idx)
        rows = [r ^ piv if r & bit else r for r in rows]
        out = [r ^ piv if r & bit else r for r in out]
        out.append(piv)
        pivots.append(col)
    return out, pivots


def basis_of_ideal(gen):
    rows = [mul(gen, 1 << k) for k in range(P)]
    return rref(rows, P)[0]


I2BASIS = basis_of_ideal(mul(bits(1, 0), G1))


def place(polys):
    return sum(f << (P * i) for i, f in enumerate(polys))


def shift(v, k):
    return sum(mul((v >> (P * i)) & FULL, 1 << k) << (P * i) for i in range(3))


def code(u):
    """Generator rows of the self-dual code with M1 = span(u)."""
    rows = [(FULL << 0) | (1 << PBIT), (FULL << P) | (FULL << (2 * P))]
    m1 = [shift(place(u), k) for k in range(P)]
    basis = [b << (P * i) for i in range(3) for b in I2BASIS]
    cons = [sum(1 << j for j, b in enumerate(basis) if (b & m).bit_count() & 1)
            for m in m1]
    red, piv = rref(cons, len(basis))
    free = [j for j in range(len(basis)) if j not in piv]
    m2 = []
    for f in free:
        x = 1 << f
        for r, p in zip(red, piv):
            if (r >> f) & 1:
                x |= 1 << p
        m2.append(_xor(basis[j] for j in range(len(basis)) if (x >> j) & 1))
    return rows + m1 + m2


def _xor(values):
    out = 0
    for v in values:
        out ^= v
    return out


# --------------------------------------------- the light words, exactly
_POP = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)


def _popcount(A):
    return _POP[A.view(np.uint8)].reshape(A.shape + (8,)).sum(axis=(-1, -2))


def _systematic(rows, order):
    perm = [sum(1 << new for new, old in enumerate(order) if (r >> old) & 1)
            for r in rows]
    red, piv = rref(perm, N)
    rest_pos = [c for c in range(N) if c not in set(piv)]
    R = np.array([[(r >> c) & 1 for c in rest_pos] for r in red], dtype=np.int64)
    return [order[c] for c in piv], [order[c] for c in rest_pos], R


def _pack(M):
    out = np.zeros((M.shape[0], (M.shape[1] + 63) // 64), dtype=np.uint64)
    for j in range(M.shape[1]):
        out[:, j // 64] |= M[:, j].astype(np.uint64) << np.uint64(j % 64)
    return out


def light_words(rows, bound=12):
    """Every codeword of weight <= bound, over two disjoint information sets."""
    info, rest, _ = _systematic(rows, list(range(N)))
    orders = [list(range(N)), rest + info]
    if set(_systematic(rows, orders[1])[0]) != set(rest):
        raise RuntimeError("no two disjoint information sets in this order")
    found = set()
    t = bound // 2
    for order in orders:
        info, rest, R = _systematic(rows, order)
        k = len(info)
        subs = [()] + [s for size in range(1, (t + 1) // 2 + 1)
                       for s in itertools.combinations(range(k), size)]
        Mi = np.zeros((len(subs), k), dtype=np.int64)
        for a, s in enumerate(subs):
            Mi[a, list(s)] = 1
        red = (Mi @ R) & 1
        msg, rp = _pack(Mi), _pack(red)
        for a in range(len(subs)):
            wm = _popcount(msg[a:] ^ msg[a])
            w = wm + _popcount(rp[a:] ^ rp[a])
            for h in np.nonzero((wm <= t) & (w <= bound) & (w > 0))[0]:
                b = a + h
                word = 0
                for i in np.nonzero(Mi[a] ^ Mi[b])[0]:
                    word |= 1 << info[i]
                for j in np.nonzero(red[a] ^ red[b])[0]:
                    word |= 1 << rest[j]
                found.add(word)
    return found


def test(item):
    tag, u = item
    rows = code(u)
    if len(rref(rows, N)[0]) != 35 or any(
            (a & b).bit_count() & 1 for i, a in enumerate(rows) for b in rows[i:]):
        return tag, u, None, None
    words = light_words(rows)
    touched = 0
    for w in words:
        touched |= w
    return tag, u, min(w.bit_count() for w in words), \
        [q for q in range(N) if not (touched >> q) & 1]


def candidates():
    def canon(ja, jb):
        best = None
        for f in range(11):
            m = pow(2, f, 89)
            a = 0 if ja == 0 else 1 + ((ja - 1) * m) % 89
            b = 0 if jb == 0 else 1 + ((jb - 1) * m) % 89
            for pair in ((a, b), (b, a)):
                best = pair if best is None or pair < best else best
        return best
    seen, out = set(), []
    for ja in range(90):
        for jb in range(90):
            c = canon(ja, jb)
            if c not in seen:
                seen.add(c)
                out.append((f"(1, g{c[0]}, g{c[1]})", (E1, REPS[c[0]], REPS[c[1]])))
    seen = set()
    for jb in range(90):
        c = 0 if jb == 0 else min(1 + ((jb - 1) * pow(2, f, 89)) % 89 for f in range(11))
        if c not in seen:
            seen.add(c)
            out.append((f"(0, 1, g{c})", (0, E1, REPS[c])))
    out.append(("(0, 0, 1)", (0, 0, E1)))
    return out


def polys(u):
    return [[j for j in range(P) if (f >> j) & 1] for f in u]


def main():
    cands = candidates()
    print(f"{len(cands)} codes, up to equivalence", flush=True)
    started = time.time()
    distances = collections.Counter()
    hits = []
    with mp.Pool(min(16, mp.cpu_count())) as pool:
        for tag, u, d, free in pool.imap_unordered(test, cands, chunksize=2):
            distances[d] += 1
            if free:
                hits.append((tag, u, d, free))
    print(f"searched in {time.time() - started:.0f}s; minimum distances: "
          f"{dict(sorted(distances.items(), key=lambda kv: (kv[0] is None, kv[0])))}")
    for tag, u, d, free in hits:
        print(f"usable: u = {tag}, a [70,35,{d}] code; no word of weight <= 12 "
              f"touches coordinate(s) {free}\n  u as polynomials (exponents): {polys(u)}")
    return 0 if hits else 1


if __name__ == "__main__":
    sys.exit(main())
