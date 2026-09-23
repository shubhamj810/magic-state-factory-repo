#!/usr/bin/env python3
"""Marking: a classified weight-40 support -> every check parent it carries.

A copy of the two support-level markers of ``../exhaustive_n38/marking.py``
(``marked_even_support``, ``marked_odd_support``), kept here verbatim so this
directory is auditable on its own and standard-library only; plus one driver,
``marked_geometries``, that enumerates the three marking cases of
``../exhaustive_n38/docs/THEORY_EXHAUSTIVENESS.md`` section 4 for a weight-40
representative S in F_2^m:

  | parity | origin o          | check support            | count       |
  |--------|-------------------|--------------------------|-------------|
  | n = 39 | o in S            | (S + o) \\ {0}, rank m    | 40          |
  | n = 40 | o in F_2^m \\ S    | S + o, rank m            | 2^m - 40    |
  | n = 40 | o outside the flat| {(s, 1)}, rank m + 1     | 1 (the lift)|

Every origin is marked: the family is a superset of the inequivalent parents
(origins related by an affine automorphism of S repeat a parent), which is what
makes an absence statement over it a valid certificate.  No automorphism
quotient is taken -- it is cheap enough not to.
"""
from __future__ import annotations


def marked_even_support(m, S):
    """n = |S| (even): origin outside support, plus the hyperplane-miss case."""
    S = frozenset(S)
    for origin in range(1 << m):
        if origin in S:
            continue
        cs = frozenset(p ^ origin for p in S)
        if 0 in cs:
            raise AssertionError('origin entered check set')
        yield m, tuple(sorted(cs))
    # hyperplane-miss lift: embed S in the affine hyperplane x_{m+1}=1 of
    # F_2^{m+1}; every lifted point has bit m set, so 0 is never in the set.
    yield m + 1, tuple(sorted(p | (1 << m) for p in S))


def marked_odd_support(m, S):
    """n = |S| - 1 (odd): origin on support, translated to 0 and dropped."""
    S = frozenset(S)
    for s in S:
        cs = frozenset((p ^ s) for p in S if (p ^ s) != 0)
        yield m, tuple(sorted(cs))


def marked_geometries(m, S):
    """Yield ``(n, origin, ambient_rank, points)`` for all 2^m + 1 markings of
    a classified support S of (even) weight w: n = w - 1 with the origin on S,
    n = w with it off S or off the flat.

    ``origin`` is the marked point as an int, or the string ``"lift"`` for the
    hyperplane-miss case.  Order: the w odd markings (origin on S, ascending),
    then the 2^m - w even ones (origin off S, ascending), then the lift.
    """
    S = frozenset(S)
    w = len(S)
    if w % 2 or w > (1 << m):
        raise ValueError(f"a classified support has even weight inside F_2^m; got {w} points, m = {m}")
    for s in sorted(S):
        yield w - 1, s, m, tuple(sorted(p ^ s for p in S if p != s))
    for o in range(1 << m):
        if o in S:
            continue
        yield w, o, m, tuple(sorted(p ^ o for p in S))
    yield w, "lift", m + 1, tuple(sorted(p | (1 << m) for p in S))


def geometry_count(m) -> int:
    return (1 << m) + 1
