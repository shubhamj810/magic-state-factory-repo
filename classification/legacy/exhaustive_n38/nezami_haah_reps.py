#!/usr/bin/env python3
"""THE INPUT DATA -- Kasami-Tokura / Nezami-Haah affine class representatives
for every classified check-part weight below 40, plus a marked-support
generator covering the whole n <= 38 ladder.

This module is the entire external input to the exhaustive classification.
Everything else in this directory is derived from it by computation.

A reduced distance >= 3 factory of T-count n has an augmented pure-check codeword
of weight  c = n + (n mod 2), a codeword of the Reed-Muller code RM(r-4, r).
The Kasami-Tokura / Nezami-Haah classification tabulates every affine class of
weight below 2.5 * d_min = 40, so each classified weight decides two consecutive
T-counts:

    weight -> covers n:  16 -> 15,16 ; 24 -> 23,24 ; 28 -> 27,28 ; 30 -> 29,30
                         32 -> 31,32 ; 34 -> 33,34 ; 36 -> 35,36 ; 38 -> 37,38

Weight 40 -> n = 39, 40 would need the separate length-40 classification, which
is deliberately NOT part of this directory: the exhaustive claim shipped here
stops at n <= 38, which is exactly the window the Kasami-Tokura / Nezami-Haah
tables close.  Asking for n >= 39 raises a clear error rather than silently
returning a partial answer.

Representative format `(m, terms)`: the class indicator is a polynomial in m
variables written as a tuple of monomials, each monomial a tuple of 1-indexed
variables -- `()` is the constant 1 and `('not', j)` is `x_j + 1`.  The support
is `{ p in F_2^m : indicator(p) = 1 }` (see `marking.support_of`).

Provenance: every table is transcribed from the Nezami-Haah `Code_Builder.ipynb`
(commit 89c7c5fc).  Transcription is the one place a silent error could enter
the pipeline, so it is checked three ways, all of them cheap and all of them
run by `tests/test_reps.py`:

  1. every representative's support has exactly the advertised weight (also
     re-checked at use time by `marked_all`, so a bad table cannot pass
     silently even outside the tests);
  2. every marked support is triorthogonal -- all pairwise and triple row
     overlaps are even;
  3. the class counts per weight match the published classification
     (1, 1, 2, 1, 10, 1, 14, 8 for weights 16, 24, 28, 30, 32, 34, 36, 38).
"""

from marking import support_of, marked_even, marked_odd

# All 10 weight-32 classes (Nezami--Haah Code_Builder.ipynb; terms format).
WEIGHT32_ALL = (
    (5, ((),)),
    (6, ((1, 2), (3,))),
    (6, ((2, 3), (1, 4), (5,))),
    (7, ((1, 2, 3), (1, 4, 5), (2, 3))),
    (7, ((1, 3, 4), (1, 2, 5), (2, 3, 6))),
    (7, ((1, 2, 4), (1, 5, 6), (2, 3, 7))),
    (8, ((1, 2, 3), (1, 2, 3, 4), (1, 2, 5, 6), (3, 4, 5, 6))),
    (8, ((1, 2, 3, 4), (2, 3, 4, 5), (1, 5, 6, 7))),
    (8, ((1, 2, 3, 5), (1, 2, 6), (1, 2, 4, 6), (3, 4, 5, 7))),
    (9, ((1, 2, 3, 4, 5), (('not', 1), 6, 7, 8, 9))),
)

# weight 34: 1 class.
WEIGHT34_ALL = (
    (8, ((1, 2, 3, 4), (1, 2, 7, 8), (5, 6, 7, 8))),
)

# All 14 weight-36 classes (Nezami--Haah Code_Builder.ipynb; terms format).
WEIGHT36_ALL = (
    (6, ((1, 3), (4, 5), (2, 6), ())),
    (7, ((2, 3, 5), (1, 4, 6), (1, 2))),
    (7, ((1, 2, 4), (1, 3, 4), (2, 3, 5), (1, 6, 7))),
    (7, ((2, 3, 4), (1, 3, 5), (1, 2, 6), (1, 4, 7))),
    (7, ((2, 3, 5), (1, 4, 5), (3, 4, 6), (1, 2, 7))),
    (7, ((1, 2, 3), (2, 3, 4), (1, 2, 5), (1, 3, 6), (4, 5, 6), (1, 2))),
    (7, ((1, 2, 4), (1, 3, 4), (1, 5, 6), (2, 5, 6), (2, 3, 7), (3, 5, 7), (4, 6, 7))),
    (8, ((1, 2, 3, 4), (1, 2, 5, 6), (3, 4, 5, 7))),
    (8, ((2, 3, 4, 5), (1, 2, 4, 7), (1, 3, 6, 8))),
    (8, ((1, 2, 4, 5), (1, 2, 5, 6), (1, 3, 4, 7), (2, 3, 6, 8))),
    (8, ((1, 2, 3, 4), (1, 3, 5, 6), (1, 2, 5, 7), (2, 4, 6, 7))),
    (8, ((2, 3, 4, 5), (1, 4, 5, 6), (2, 4, 5, 6), (1, 2, 3, 7), (1, 3, 6, 8))),
    (8, ((1, 2, 4, 6), (1, 2, 3, 7), (4, 5, 6, 8), (3, 5, 7, 8))),
    (9, ((1, 2, 3, 4, 5), (6, 7, 8, 9, ('not', 5)), (3, 4, 6, 7, 8))),
)

# All 8 weight-38 classes (Nezami--Haah Code_Builder.ipynb; terms format).
WEIGHT38_ALL = (
    (8, ((1, 2, 3, 4), (1, 2, 5, 6), (1, 4, 5, 6), (2, 3, 7, 8))),
    (8, ((1, 2, 3, 5), (1, 2, 4, 6), (2, 4, 5, 7), (1, 3, 6, 8))),
    (8, ((1, 2, 4, 5), (1, 4, 5, 6), (2, 3, 4, 7),
         (1, 5, 6, 7), (1, 2, 3, 8), (1, 2, 6, 8), (2, 3, 7, 8))),
    (8, ((1, 2, 3, 4), (2, 4, 5, 6), (1, 5, 6, 7), (1, 3, 7, 8))),
    (8, ((1, 2, 3, 4), (1, 2, 3, 5), (2, 3, 4, 6), (1, 4, 5, 6), (1, 5, 7, 8))),
    (9, ((1, 2, 3, 4, 5), (3, 6, 7, 8, 9), (4, 5, 6, 7, 8))),
    (9, ((1, 2, 3, 4, 5), (3, 4, 6, 7, 8), (2, 5, 6, 7, 9), (2, 6, 7, 8, 9))),
    (10, ((1, 2, 3, 4, 5, 6), (3, 4, 7, 8, 9, 10),
          (5, 6, 7, 8, 9, 10), (5, 7, 8, 9, 10))),
)

# weights 16/24/28/30 (KT range, Nezami-Haah Code_Builder.ipynb) -> n=15..30.
WEIGHT16_ALL = (
    (4, ((),)),                                # constant 1: full 4-flat
)
WEIGHT24_ALL = (
    (6, ((1, 2), (3, 4))),
)
WEIGHT28_ALL = (
    (6, ((1, 2), (3, 4), (5, 6))),
    (7, ((1, 2, 3), (4, 5, 6))),
)
WEIGHT30_ALL = (
    (8, ((1, 2, 3, 4), (5, 6, 7, 8))),
)

BY_WEIGHT = {16: WEIGHT16_ALL, 24: WEIGHT24_ALL, 28: WEIGHT28_ALL,
             30: WEIGHT30_ALL, 32: WEIGHT32_ALL, 34: WEIGHT34_ALL,
             36: WEIGHT36_ALL, 38: WEIGHT38_ALL}

# Valid T-counts with a classified check part (weight = n + n%2).  This tuple
# IS the exhaustive window of this directory: n <= 38.  There is no n = 39, 40
# here -- those need weight-40 supports, which the KT / Nezami-Haah tables do
# not cover.
VALID_NS = (15, 16, 23, 24, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38)

#: Class counts per weight, from the published classification.  Checked by
#: tests/test_reps.py -- a dropped or duplicated representative changes these.
EXPECTED_CLASS_COUNTS = {16: 1, 24: 1, 28: 2, 30: 1,
                         32: 10, 34: 1, 36: 14, 38: 8}


def marked_all(n):
    """Yield (class_index, r, check_set) for every raw marked support at T-count n.

    `r` is the number of check qubits and `check_set` the tuple of n points of
    F_2^r that form the check part.  "Marking" means choosing an origin for the
    affine class; `marking.marked_even` / `marked_odd` enumerate one
    representative per inequivalent origin, which is what makes the sweep over
    origins finite (see marking.py).

    Dependency-free variant (no numpy), identical in output to
    `classify.marked_all`; `tests/test_reps.py` asserts the two agree."""
    weight = n + (n % 2)
    if weight not in BY_WEIGHT:
        raise ValueError(
            f'n={n} needs check-support weight {weight}, outside the classified '
            f'window of this directory (weights {sorted(BY_WEIGHT)}, n <= 38).')
    reps = BY_WEIGHT[weight]
    marker = marked_even if (n % 2 == 0) else marked_odd
    for ci, (m, terms) in enumerate(reps):
        if len(support_of(m, terms)) != weight:
            raise AssertionError(f'weight-{weight} class {ci} bad weight')
        for r, cs in marker(m, terms):
            yield ci, r, cs
