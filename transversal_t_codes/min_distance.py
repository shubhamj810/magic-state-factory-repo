#!/usr/bin/env python3
"""A proved lower bound on the minimum distance of a binary linear code.

    python transversal_t_codes/min_distance.py      # the three codes the tests use

The doubling theorem needs the distance of each self-dual input, and for the
quantum quadratic-residue codes of length 79 and 103 and the ``[[101,1,17]]``
code of ``sub(XQ103)`` that distance comes from the minimum distance of a
classical code of length 80 to 104.  Enumerating every word (2^40 to 2^52) is
out of reach, so this module uses the method of Brouwer and Zimmermann with
two information sets.

THE ARGUMENT
------------
Let ``C`` be an ``[n, k]`` code with ``n = 2k`` and let ``S1`` and ``S2`` be
disjoint information sets that together cover all ``n`` coordinates.  Bring a
generator matrix into systematic form on ``S1``: row ``i`` has a 1 at the
``i``-th coordinate of ``S1`` and 0 at the others.  A codeword is then the sum
of exactly the rows at whose ``S1`` coordinates it has a 1, so the words with
at most ``t`` ones on ``S1`` are the sums of at most ``t`` rows, and listing
those sums lists every such word.  Do the same on ``S2``.  A word not listed
has at least ``t + 1`` ones on each side, so weight at least ``2t + 2``.  The
minimum distance is therefore at least the smaller of ``2t + 2`` and the
lightest non-zero word listed.  The bound is a proof, not an estimate: no
word is sampled, and nothing is skipped.

The sums are formed in two halves (meet in the middle): all sums of ``a`` rows
of the first half against all sums of ``b`` rows of the second, for every
``a + b <= t``.  A word's weight is ``a + b`` on its own information set plus
the popcount of its other half, which fits one 64-bit word for ``k <= 64``.
Integer numpy only.
"""
from __future__ import annotations

import itertools
import random

import numpy as np

_POP16 = np.array([bin(i).count("1") for i in range(1 << 16)], dtype=np.uint8)


def popcount64(values: np.ndarray) -> np.ndarray:
    """The popcount of every entry of a uint64 array."""
    v = values.view(np.uint16).reshape(values.shape + (4,))
    return _POP16[v].sum(axis=-1, dtype=np.int16)


def _rref_on(rows, coords):
    """Rows reduced to systematic form on ``coords`` (a list of coordinates),
    or ``None`` if those coordinates are not an information set."""
    rows = list(rows)
    out = []
    for c in coords:
        pivot = next((i for i, r in enumerate(rows) if (r >> c) & 1), None)
        if pivot is None:
            return None
        p = rows.pop(pivot)
        rows = [r ^ p if (r >> c) & 1 else r for r in rows]
        out = [r ^ p if (r >> c) & 1 else r for r in out]
        out.append(p)
    if any(rows):
        return None                       # the rows were not independent
    return out


def two_information_sets(rows, n, seed=0, tries=200):
    """``(S1, G1, S2, G2)``: two disjoint information sets covering all ``n``
    coordinates and the generator matrix in systematic form on each.

    The first set is chosen by elimination on a seeded random order of the
    coordinates; the complement is accepted when it is an information set too.
    """
    k = len(rows)
    if n != 2 * k:
        raise ValueError(f"two disjoint information sets need n = 2k, not "
                         f"n = {n}, k = {k}")
    rng = random.Random(seed)
    for _ in range(tries):
        order = list(range(n))
        rng.shuffle(order)
        work = list(rows)
        first = []
        for c in order:
            pivot = next((i for i, r in enumerate(work) if (r >> c) & 1), None)
            if pivot is None:
                continue
            p = work.pop(pivot)
            work = [r ^ p if (r >> c) & 1 else r for r in work]
            first.append(c)
            if len(first) == k:
                break
        if len(first) != k:
            raise ValueError("the rows are not independent")
        second = [c for c in range(n) if c not in set(first)]
        g1, g2 = _rref_on(rows, first), _rref_on(rows, second)
        if g1 is not None and g2 is not None:
            return first, g1, second, g2
    raise ValueError("no pair of disjoint information sets found")


def _side_words(systematic, info, other):
    """Each row's part on the coordinates OUTSIDE its information set, packed
    into one uint64 (``other`` lists those coordinates)."""
    if len(other) > 64:
        raise ValueError("the other half must fit one 64-bit word")
    out = []
    for r in systematic:
        v = 0
        for j, c in enumerate(other):
            if (r >> c) & 1:
                v |= 1 << j
        out.append(v)
    return np.array(out, dtype=np.uint64)


def _sums(values, size):
    """All XORs of ``size`` distinct entries of ``values``."""
    if size == 0:
        return np.zeros(1, dtype=np.uint64)
    out = []
    for combo in itertools.combinations(range(len(values)), size):
        acc = 0
        for i in combo:
            acc ^= int(values[i])
        out.append(acc)
    return np.array(out, dtype=np.uint64)


def lightest_listed(words, t, chunk=1 << 22):
    """The lightest non-zero sum of at most ``t`` rows, a row being 1 on its
    own information coordinate plus ``words[i]`` outside it."""
    k = len(words)
    half = k // 2
    left, right = words[:half], words[half:]
    lsums = [_sums(left, a) for a in range(min(t, half) + 1)]
    rsums = [_sums(right, b) for b in range(min(t, k - half) + 1)]
    best = None
    for a in range(len(lsums)):
        for b in range(len(rsums)):
            if a + b == 0 or a + b > t:
                continue
            L, R = lsums[a], rsums[b]
            step = max(1, chunk // max(1, len(R)))
            for start in range(0, len(L), step):
                block = L[start:start + step, None] ^ R[None, :]
                low = int(popcount64(block).min()) + a + b
                best = low if best is None else min(best, low)
    return best


def distance_lower_bound(rows, n, t, seed=0):
    """A proved lower bound on the minimum distance of the span of ``rows``.

    Returns ``{"bound", "lightest_listed", "t", "information_sets"}``: every
    word with at most ``t`` ones on either information set is listed, the
    lightest of them is ``lightest_listed``, and ``bound`` is
    ``min(lightest_listed, 2t + 2)``.  When ``lightest_listed <= 2t + 1`` the
    bound is the minimum distance itself.
    """
    s1, g1, s2, g2 = two_information_sets(rows, n, seed)
    found = []
    for info, systematic, other in ((s1, g1, s2), (s2, g2, s1)):
        found.append(lightest_listed(_side_words(systematic, info, other), t))
    lightest = min(found)
    return {"bound": min(lightest, 2 * t + 2), "lightest_listed": lightest,
            "t": t, "information_sets": [sorted(s1), sorted(s2)]}


def main():
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import build_codes as B
    xq103 = B.extend(B.quadratic_residue_code(103), 103)
    cases = [("extended QR [80,40]", B.extend(B.quadratic_residue_code(79), 79), 80, 6),
             ("extended QR [104,52]", xq103, 104, 8),
             ("sub(XQ103) [102,51]", B.subtract(xq103, 104, 102, 103), 102, 8)]
    for name, rows, n, t in cases:
        result = distance_lower_bound(B.basis(rows), n, t)
        print(f"{name}: every word with at most {t} ones on either information "
              f"set listed, the lightest weighs {result['lightest_listed']}; "
              f"minimum distance >= {result['bound']}")


if __name__ == "__main__":
    main()
