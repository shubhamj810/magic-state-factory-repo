#!/usr/bin/env python3
"""The least odd weight in a binary code, proved by the Brouwer-Zimmermann
bound of `min_distance.py`, for a code of dimension k > n/2.

    python transversal_t_codes/odd_distance.py --berardini   # the [89,45] code, ~2 min

The distance of the CSS code with X stabilisers C and the all-ones logical
is the least weight of an odd word of C^perp (`certify_distances.py`).
Berardini, Dastbasteh and Etxezarreta Martinez (arXiv:2412.08586, Example 1)
take C the cyclic self-orthogonal [89,44] code with the generator polynomial
`G_EXP` below and state that this least odd weight is 17; their Theorem 12
then doubles the [[89,1,17]] code onto a triorthogonal code.

THE ARGUMENT
------------
C^perp is an [89,45] code, so two information sets S1 and S2 of size 45
cannot be disjoint; they can meet in a single coordinate.  Listing every
codeword with at most t1 ones on S1 and every one with at most t2 ones on
S2 (`min_distance.lightest_listed`'s meet in the middle, here keeping the
lightest ODD word), a word that is not listed has at least t1 + 1 ones on S1
and t2 + 1 on S2, so at least t1 + t2 + 1 ones in all.  The least odd weight
is therefore at least the smaller of t1 + t2 + 1 (or the next odd number) and
the lightest odd word listed, and equal to the latter when the latter is
smaller.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import min_distance as M                                          # noqa: E402

#: Berardini et al., Example 1: g(x) = sum of x^e, the cyclic [89,44] code.
G_EXP = [45, 44, 42, 38, 36, 35, 33, 32, 30, 27, 26, 24, 23, 20, 19, 18, 16,
         15, 12, 8, 5, 4, 3, 0]
N89 = 89


def weight(v):
    return bin(v).count("1")


def basis(vectors):
    piv = {}
    for v in vectors:
        while v:
            h = v.bit_length() - 1
            if h in piv:
                v ^= piv[h]
            else:
                piv[h] = v
                break
    return list(piv.values())


def dual(rows, n):
    """A basis of the dual of the span of ``rows`` (length ``n``)."""
    rows = M._rref_on(basis(rows), _pivots(basis(rows)))
    pivots = _pivots(rows)
    free = [c for c in range(n) if c not in pivots]
    out = []
    for f in free:
        v = 1 << f
        for r, p in zip(rows, pivots):
            if (r >> f) & 1:
                v |= 1 << p
        out.append(v)
    return out


def _pivots(rows):
    """Pivot columns of a set of independent rows, by elimination."""
    work, piv = list(rows), []
    for _ in range(len(rows)):
        r = work.pop(0)
        for c in range(r.bit_length()):
            if (r >> c) & 1 and c not in piv:
                piv.append(c)
                work = [w ^ r if (w >> c) & 1 else w for w in work]
                break
    return piv


def lightest_odd_listed(words, t, chunk=1 << 22, witness=False):
    """The lightest ODD sum of 1 to ``t`` rows (row = 1 on its own information
    coordinate plus ``words[i]`` outside), or ``None``; with ``witness``,
    ``(weight, rows)``, the rows (indices into ``words``) of one such sum."""
    import itertools
    k = len(words)
    half = k // 2
    left, right = words[:half], words[half:]
    lsums = [M._sums(left, a) for a in range(min(t, half) + 1)]
    rsums = [M._sums(right, b) for b in range(min(t, k - half) + 1)]
    best, where = None, None
    for a in range(len(lsums)):
        for b in range(len(rsums)):
            if a + b == 0 or a + b > t:
                continue
            L, R = lsums[a], rsums[b]
            step = max(1, chunk // max(1, len(R)))
            for start in range(0, len(L), step):
                block = L[start:start + step, None] ^ R[None, :]
                w = M.popcount64(block).astype(np.int32) + a + b
                w = np.where((w & 1) == 1, w, 1 << 20)
                low = int(w.min())
                if low < (1 << 20) and (best is None or low < best):
                    i, j = np.unravel_index(int(w.argmin()), w.shape)
                    best, where = low, (a, b, start + int(i), int(j))
    if not witness:
        return best
    if best is None:
        return None, None
    a, b, i, j = where
    left_rows = list(itertools.combinations(range(half), a))[i] if a else ()
    right_rows = list(itertools.combinations(range(k - half), b))[j] if b else ()
    return best, sorted(list(left_rows) + [half + r for r in right_rows])


def two_sets_meeting_once(rows, n, seed=0, tries=200):
    """Information sets S1, S2 of a [n, k] code with k > n/2 that share
    exactly 2k - n coordinates, and the systematic forms on each."""
    k = len(rows)
    rng = random.Random(seed)
    for _ in range(tries):
        order = list(range(n))
        rng.shuffle(order)
        g1 = None
        first = []
        work = list(rows)
        for c in order:
            p = next((i for i, r in enumerate(work) if (r >> c) & 1), None)
            if p is None:
                continue
            pr = work.pop(p)
            work = [r ^ pr if (r >> c) & 1 else r for r in work]
            first.append(c)
            if len(first) == k:
                break
        g1 = M._rref_on(rows, first)
        rest = [c for c in range(n) if c not in first]
        extra = 2 * k - n
        for shared in (rng.sample(first, extra) for _ in range(50)):
            second = rest + shared
            g2 = M._rref_on(rows, second)
            if g1 is not None and g2 is not None:
                return first, g1, second, g2
    raise ValueError("no such pair of information sets found")


def odd_distance_bound(rows, n, t1, t2, seed=0):
    k = len(rows)
    s1, g1, s2, g2 = two_sets_meeting_once(rows, n, seed)
    shared = len(set(s1) & set(s2))
    found = []
    for info, systematic, t in ((s1, g1, t1), (s2, g2, t2)):
        other = [c for c in range(n) if c not in set(info)]
        found.append(lightest_odd_listed(M._side_words(systematic, info, other), t))
    lightest = min(x for x in found if x is not None)
    # one lightest odd word, from the first information set, checked
    other1 = [c for c in range(n) if c not in set(s1)]
    w1, picked = lightest_odd_listed(M._side_words(g1, s1, other1), t1, witness=True)
    word = 0
    for i in picked:
        word ^= g1[i]
    if w1 != lightest or weight(word) != lightest or len(basis(rows + [word])) != k:
        raise AssertionError("the lightest odd word does not check")
    floor = t1 + t2 + 2 - shared
    floor += 1 - floor % 2                         # the next odd number
    return {"bound": min(lightest, floor), "lightest_odd_listed": lightest,
            "unlisted_at_least": floor, "t": [t1, t2], "shared": shared,
            "information_sets": [sorted(s1), sorted(s2)], "sides": found,
            "lightest_odd_word": [c for c in range(n) if (word >> c) & 1]}


def berardini_code():
    """C (the cyclic [89,44] code) and a basis of C^perp, both checked."""
    g = sum(1 << e for e in G_EXP)
    full = (1 << N89) - 1
    # g divides x^89 + 1: reduce x^89 + 1 modulo g over GF(2)
    r = (1 << N89) | 1
    while r.bit_length() >= g.bit_length():
        r ^= g << (r.bit_length() - g.bit_length())
    if r:
        raise AssertionError("g(x) does not divide x^89 + 1")
    C = [g << i for i in range(N89 - 45)]
    if len(basis(C)) != 44:
        raise AssertionError("C is not of dimension 44")
    if any(weight(a & b) % 2 for a in C for b in C):
        raise AssertionError("C is not self-orthogonal")
    D = dual(C, N89)
    if len(basis(D)) != 45 or any(weight(a & b) % 2 for a in C for b in D):
        raise AssertionError("the dual is wrong")
    if len(basis(C + [full])) != 45:
        raise AssertionError("the all-ones vector is in C")
    return C, D


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--berardini", action="store_true")
    ap.add_argument("--t", type=int, nargs=2, default=[8, 7])
    ap.add_argument("--out")
    args = ap.parse_args(argv)
    C, D = berardini_code()
    result = odd_distance_bound(D, N89, args.t[0], args.t[1])
    result["code"] = "the dual of the cyclic [89,44] code of Berardini et al. (arXiv:2412.08586, Example 1)"
    print(json.dumps({k: v for k, v in result.items() if k != "information_sets"}))
    if args.out:
        Path(args.out).write_text(json.dumps(result, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
