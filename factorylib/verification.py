#!/usr/bin/env python3
"""Exact fault-enumeration verifier, standalone (no OR-Tools dependency).

Byte-for-byte port of `slot_search.verify`: given a factory's explicit
columns it recomputes the target parity and the true circuit distance by
enumerating faults, returning `(parity_ok, distance)`.

It is kept separate from `slot_search` so that any witness -- whoever
produced it, whichever solver -- can be re-checked by a module that imports
nothing but the standard library.  `slot_search` pulls in ortools at import
time, which the classification pipeline (pure Python + numpy) must not
require, and an independent verifier is also the point: the search and the
check should not share code that could be wrong in the same way.
"""

import itertools


def verify(k, N, cols, target, dmax=4):
    """Return (parity_ok, distance) for a factory given as `n` columns
    (subsets of the N qubits; outputs are 0..k-1).

    parity_ok: every degree-<=3 qubit-subset parity of the columns equals the
    target -- `want` is 0 on any subset touching a check qubit, so all
    check-touching parities must vanish.  `target` is 'T'/'CS'/'CCZ' or an
    explicit set of frozenset output-monomials.

    distance: the minimum size (tested ascending, so exact) of a column
    subset whose XOR is nonzero and supported on the k outputs only -- an
    undetectable logical fault -- or the string '>dmax' if none has size
    <= dmax.  Weights 3 and 4 use a meet-in-the-middle over the table of
    pairwise column XORs rather than enumerating triples/quadruples."""
    n = len(cols)
    # A `raise`, not an `assert`: `python -O` strips assertions, and a repeated
    # column is a distance-2 circuit, so an input check inside a VERIFIER is the
    # last thing that should be optional.
    if len(set(cols)) != n:
        raise ValueError(
            f"{n - len(set(cols))} repeated column(s): a factory with a repeated "
            f"column has an undetectable weight-2 fault, so its distance is 2")

    def par(qs):
        qs = set(qs)
        return sum(1 for c in cols if qs <= c) & 1

    def want(*S):
        if not isinstance(target, str):        # custom: set of output-monomials
            return 1 if frozenset(S) in target else 0
        if target == 'T':
            return 1 if len(S) == 1 and S[0] < k else 0
        if target == 'CS':
            return 1 if set(S) == {0, 1} else 0
        if target == 'CCZ':
            return 1 if set(S) == {0, 1, 2} else 0
        return 0

    ok = True
    for a in range(N):
        ok &= par([a]) == want(a)
    for a, b in itertools.combinations(range(N), 2):
        ok &= par([a, b]) == want(a, b)
    for a, b, c in itertools.combinations(range(N), 3):
        ok &= par([a, b, c]) == want(a, b, c)

    masks = []
    for c in cols:
        mm = 0
        for q in c:
            mm |= 1 << q
        masks.append(mm)
    outm = (1 << k) - 1
    bad_targets = [t for t in range(1, 1 << k)]

    def is_bad(v):
        return v != 0 and (v & ~outm) == 0

    for v in masks:                                   # weight 1
        if is_bad(v):
            return ok, 1
    for i, j in itertools.combinations(range(n), 2):  # weight 2
        if is_bad(masks[i] ^ masks[j]):
            return ok, 2
    # pairval[v] = all index pairs whose column XOR is v (meet-in-the-middle:
    # weight 3 = column + pair, weight 4 = pair + pair; index-overlap cases
    # reduce to weights 1/2, already excluded above).
    pairval = {}
    for i, j in itertools.combinations(range(n), 2):
        pairval.setdefault(masks[i] ^ masks[j], []).append((i, j))
    if dmax >= 3:                                     # weight 3
        for t in bad_targets:
            for i in range(n):
                for (a, b) in pairval.get(masks[i] ^ t, []):
                    if i not in (a, b):
                        return ok, 3
    if dmax >= 4:                                     # weight 4
        for t in bad_targets:
            for v, plist in pairval.items():
                for (a, b) in pairval.get(v ^ t, []):
                    for (c, d) in plist:
                        if len({a, b, c, d}) == 4:
                            return ok, 4
    return ok, f'>{dmax}'
