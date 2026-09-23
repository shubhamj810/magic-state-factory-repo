#!/usr/bin/env python3
"""Marking + F_2 linear-algebra primitives for the classification pipeline.

"Marking" turns a *classified support* into a *check parent*.  A KTA /
Nezami-Haah class representative gives a support S in F_2^m (the set of points
where its indicator polynomial is 1).  Two markings turn that support into the
n check columns of a factory:

  * `marked_even` / `marked_even_support` (n = |S| even): the origin lies
    OUTSIDE the support, so the check set is a translate of S itself (n points),
    plus the case where an affine hyperplane misses the origin (which raises the
    ambient dimension r by one);
  * `marked_odd` / `marked_odd_support` (n = |S| - 1 odd): the origin lies ON
    the support; translate any support point to 0 and drop it, leaving n
    distinct nonzero check points.

Both enumerate every inequivalent origin, so the raw marked family is a
*superset* of the deduplicated one -- exhaustive by construction, which is what
makes an UNSAT/absence statement over it a valid certificate.

The rest of the module is the F_2 toolkit the engines share: `row_space_rows`
(degree-<=1/2/3 moment rows of a check set), `nullspace_basis`, `support_of`,
and `columns_from_output_sets` (assemble explicit factory columns from chosen
output rows).

Self-contained: standard library only -- no solver, no numpy.  Keeping this
module dependency-free is deliberate: it is the piece that turns published class
tables into check parents, so it should be readable and runnable by anyone
checking the tables against the literature, without setting up an environment.

The class tables themselves live in `nezami_haah_reps.py`; this module only
turns them into parents.
"""

import itertools


def _term_value(point, term):
    """Value of one monomial at `point`: variables are 1-indexed, x_j reads
    bit j-1 of the point int; a factor ('not', j) is the negated literal
    x_j + 1; the empty term () is the constant 1."""
    value = 1
    for factor in term:
        if isinstance(factor, tuple):
            value &= ((point >> (factor[1] - 1)) & 1) ^ 1
        else:
            value &= (point >> (factor - 1)) & 1
        if not value:
            return 0
    return value


def support_of(m, terms):
    """Points of F_2^m where the indicator polynomial (XOR of `terms`) is 1."""
    return frozenset(
        point for point in range(1 << m)
        if sum(_term_value(point, term) for term in terms) & 1
    )


def row_space_rows(checks, r, degree):
    """Moment rows of a check set, as F_2^n ints (bit i = column i).

    For every subset T of the r check bits with |T| <= degree, the indicator
    of the columns whose point has all bits of T set.  Enumeration order:
    T=() (the all-ones row) first, then |T|=1 (the check rows h_j), then
    |T|=2 (the pointwise products h_i & h_j), ...  Callers slice off the
    leading all-ones row with rows[1:]."""
    rows = []
    for tsize in range(degree + 1):
        for T in itertools.combinations(range(r), tsize):
            mask = 0
            for i, s in enumerate(checks):
                if all((s >> bit) & 1 for bit in T):
                    mask |= 1 << i
            rows.append(mask)
    return rows


def nullspace_basis(rows, n):
    """Basis of {x in F_2^n : <x, row> = 0 for every row}, as ints.

    Standard free-column construction: RREF the rows, then one basis vector
    per non-pivot column (bit `free` set, plus the pivot bits that cancel)."""
    basis = {}
    for row in rows:
        value = row
        for pivot in sorted(basis, reverse=True):
            if (value >> pivot) & 1:
                value ^= basis[pivot]
        if value:
            pivot = value.bit_length() - 1
            for old_pivot, old in list(basis.items()):
                if (old >> pivot) & 1:
                    basis[old_pivot] = old ^ value
            basis[pivot] = value
    pivot_columns = set(basis)
    free_columns = [i for i in range(n) if i not in pivot_columns]
    out = []
    for free in free_columns:
        vector = 1 << free
        for pivot, row in sorted(basis.items()):
            if (row >> free) & 1:
                vector |= 1 << pivot
        out.append(vector)
    return out


def columns_from_output_sets(checks, r, output_sets):
    """Assemble explicit factory columns from chosen output-row masks.

    NB: check qubits are placed at 3+bit, i.e. this assumes exactly THREE
    output rows -- it serves the k=3 CCZ certifiers
    used by certificate-generation scripts; the general-k engines build columns
    themselves (classify.build_columns uses k+bit)."""
    columns = []
    for i, s in enumerate(checks):
        column = {a for a, mask in enumerate(output_sets) if (mask >> i) & 1}
        for bit in range(r):
            if (s >> bit) & 1:
                column.add(3 + bit)
        columns.append(frozenset(column))
    return columns


def marked_even_support(m, S):
    """n = |S| (even): origin outside support, plus the hyperplane-miss case.

    Support-only variant: takes the support set directly, for a class given as
    an explicit point set rather than an indicator polynomial.  `marked_even`
    below is the polynomial-facing wrapper."""
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
    """n = |S| - 1 (odd): origin on support, translated to 0 and dropped.

    Support-only variant (see `marked_even_support`)."""
    S = frozenset(S)
    for s in S:
        cs = frozenset((p ^ s) for p in S if (p ^ s) != 0)
        yield m, tuple(sorted(cs))


def marked_even(m, terms):
    """n = weight (even): origin outside support, plus the hyperplane-miss case."""
    return marked_even_support(m, support_of(m, terms))


def marked_odd(m, terms):
    """n = weight - 1 (odd): origin on support, translated to 0 and dropped."""
    return marked_odd_support(m, support_of(m, terms))


def row_pair_setup(check_set, r):
    """Return (Rbasis, pair_rows) as plain int lists for one instance."""
    checks = tuple(check_set)
    n = len(checks)
    Rbasis = nullspace_basis(row_space_rows(checks, r, 2), n)
    pair_rows = row_space_rows(checks, r, 1)
    return Rbasis, pair_rows
