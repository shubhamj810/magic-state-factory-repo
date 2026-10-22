#!/usr/bin/env python3
"""The leading error coefficient ``A_d`` of a factory, counted exactly.

A fault is a set of columns whose rotations fail, each failure a ``Z`` on the
wires of its column (`faultcore`).  The checks accept it when its syndrome --
the XOR of the columns' check parts -- is zero, and it is harmful when the XOR
of their output parts is not zero.  The distance ``d`` is the least weight of
a fault that is both; ``A_d`` is HOW MANY there are at that weight.  With each
rotation failing independently with probability ``p``, an accepted run then
carries an output error with probability ``A_d p^d + O(p^(d+1))``, which is the
number a reader compares factories of equal distance by.  For the 15-to-1
factory ``A_3 = 35`` (Bravyi and Kitaev's ``35 p^3``), for the 8-``T`` ``CCZ``
factory ``A_2 = 28`` (all ``C(8,2)`` pairs).  It is a number about the
CIRCUIT, not the class: two circuits for the same gate at the same ``n`` and
``d`` can differ, as the catalogue's ``[[20,4,2]]`` (``A_2 = 22``) and Bravyi
and Haah's (``3k + 1 = 13``) do.

TWO COUNTS, AND THE DIFFERENCE OF TWO MORE
------------------------------------------
Write ``M`` for the ``N x n`` matrix of the wires and ``C`` for its check rows.
The accepted faults are the kernel of ``C``, the harmless accepted ones the
kernel of ``M``, so

    A_w = B_w(ker C) - B_w(ker M),

``B_w`` the number of words of weight ``w``.  Each term is computed by
whichever of two methods is cheap for it:

* **MacWilliams.**  ``ker C`` is the dual of the row space of ``C``, so its
  weight distribution follows from the row space's, which has only ``2^rank``
  words:  ``B_w = 2^-rank sum_i D_i K_w(i)``, ``D_i`` the number of row-space
  words of weight ``i`` and ``K_w`` the Krawtchouk polynomial.  Cheap when the
  rank is small -- few checks, which is exactly when accepted faults are many.
* **Enumeration.**  `faultcore.scan_weight`'s meet-in-the-middle sweeps,
  counting faults with zero syndrome instead of harmful ones.  Cheap when the
  syndromes are long and collisions rare -- ``ker M`` on a wide register,
  where harmless accepted faults are few.

And, wherever its budget lets it finish, the DIRECT count -- the harmful
faults themselves, enumerated by `faultcore.scan_weight` on the circuit as it
is -- must agree with the difference.  It shares the sweep with the second
method but none of the algebra, and on the small circuits of the tests both
are pinned to a literal ``C(n, d)`` enumeration as well.

Where neither method reaches -- weight 7 with long syndromes, or weight 6 at
``n ~ 850`` -- the count is ``None``, and nothing is guessed.
"""
from __future__ import annotations

from math import comb

import numpy as np

import faultcore as FC

#: the largest row-space dimension the MacWilliams count enumerates outright
#: when it is the first choice, and when it is the fallback.  At ``n = 1023``
#: it takes 2.5 s at rank 25 and 40 s at rank 29, where the weight-5 sweep
#: takes 25-55 s whatever it finds, so 28 is about where the two cross
MACWILLIAMS_FIRST = 28
MACWILLIAMS_LIMIT = 30
#: what the counting sweeps may spend: a count visits every accepted fault
#: several times, so it needs far more than a search for one witness
COUNT_BUDGET = dict(max_candidates=60_000_000, max_triples=200_000_000)

_POP16 = np.array([bin(i).count("1") for i in range(1 << 16)], dtype=np.uint16)


# ------------------------------------------------------------- MacWilliams
def _basis(vectors):
    """A basis of the span of ``vectors`` (ints), by elimination."""
    out = []
    for v in vectors:
        for b in out:
            v = min(v, v ^ b)
        if v:
            out.append(v)
    return out


def _words(v, W):
    return np.array([(v >> (64 * i)) & 0xFFFF_FFFF_FFFF_FFFF for i in range(W)],
                    dtype=np.uint64)


def span_weights(basis, n):
    """The weight distribution, ``[D_0, ..., D_n]``, of the span of ``basis``.

    Every word is visited once: a table of the spans of the first (up to) 18
    vectors, XORed with each word of the rest in Gray-code order.  Integer
    numpy only -- popcounts by a 16-bit table -- so no BLAS threads.
    """
    W = max(1, (n + 63) // 64)
    low = min(len(basis), 18)
    table = np.zeros((1, W), dtype=np.uint64)
    for v in basis[:low]:
        table = np.concatenate([table, table ^ _words(v, W)])
    high = [_words(v, W) for v in basis[low:]]
    hist = np.zeros(n + 1, dtype=np.int64)
    current = np.zeros(W, dtype=np.uint64)
    for g in range(1 << len(high)):
        if g:
            current ^= high[(g & -g).bit_length() - 1]
        weights = _POP16[(table ^ current).view(np.uint16)].sum(axis=1,
                                                                dtype=np.int64)
        hist += np.bincount(weights, minlength=n + 1)
    return [int(x) for x in hist]


def krawtchouk(w, i, n):
    return sum((-1) ** j * comb(i, j) * comb(n - i, w - j)
               for j in range(min(i, w) + 1))


def dual_count(distribution, n, w):
    """Words of weight ``w`` in the dual of a code with this distribution."""
    size = sum(distribution)
    total = sum(D * krawtchouk(w, i, n) for i, D in enumerate(distribution) if D)
    if total % size:
        raise AssertionError(f"MacWilliams sum {total} is not a multiple of "
                             f"{size}: the distribution is not a code's")
    return total // size


# ------------------------------------------------------------- enumeration
class _Accepted(FC.Circuit):
    """The circuit with "harmful" read as "accepted": zero syndrome, whatever
    the outputs do.  With ``k = 0`` every wire is a check, so the faults it
    counts are the kernel of the whole matrix."""

    def harmful(self, indices) -> bool:
        s = 0
        for index in indices:
            s ^= self.syn[index]
        return s == 0


def _enumerated(columns, k, N, w):
    circuit = _Accepted(columns, k, N, FC.Budget(**COUNT_BUDGET))
    status, _witness, count = FC.scan_weight(circuit, w, want_count=True)
    return count if status != "skipped" else None


# ------------------------------------------------------------------- A_w
def accepted_count(columns, k, N, w):
    """``(B_w, method)``: accepted faults of weight ``w`` when the outputs are
    wires ``0..k-1`` (``k = 0``: every wire is checked), or ``(None, None)``."""
    n = len(columns)
    rows = FC.rows_over_columns(columns, N)
    basis = _basis(rows[k:])
    if len(basis) <= MACWILLIAMS_FIRST:
        return dual_count(span_weights(basis, n), n, w), "macwilliams"
    count = _enumerated(columns, k, N, w)
    if count is not None:
        return count, "enumeration"
    if len(basis) <= MACWILLIAMS_LIMIT:
        return dual_count(span_weights(basis, n), n, w), "macwilliams"
    return None, None


def error_coefficient(columns, k, N, w):
    """The number of harmful accepted faults of weight ``w``, and how it was
    got: ``{"count", "accepted", "harmless", "methods", "direct"}``.

    ``count`` is ``None`` when either term is out of reach.  ``direct`` is the
    harmful faults enumerated outright, or ``None`` where that sweep's budget
    stopped it; when both exist they must agree, and a disagreement raises.
    """
    accepted, how_c = accepted_count(columns, k, N, w)
    harmless, how_m = accepted_count(columns, 0, N, w) if accepted is not None \
        else (None, None)
    count = None if harmless is None else accepted - harmless
    status, _witness, direct = FC.scan_weight(FC.Circuit(columns, k, N), w,
                                              want_count=True)
    if status == "skipped":
        direct = None
    if count is not None and direct is not None and count != direct:
        raise AssertionError(f"A_{w}: {accepted} accepted - {harmless} "
                             f"harmless = {count}, but the harmful faults "
                             f"enumerated directly number {direct}")
    return {"count": count if count is not None else direct,
            "accepted": accepted, "harmless": harmless,
            "methods": [how_c, how_m], "direct": direct}


def leading_coefficient(row):
    """``A_d`` for a catalogue row, or ``None``: only an exact distance has
    one, since a floor leaves the lighter weights unproved."""
    if not row["d_is_exact"]:
        return None
    return error_coefficient(row["columns"], row["k"], row["N"],
                             row["d"])["count"]
