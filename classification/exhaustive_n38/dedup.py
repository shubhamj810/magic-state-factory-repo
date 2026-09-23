#!/usr/bin/env python3
"""Gate equivalence: the S_k deduplication key, and the GL(k,2) annotation.

WHICH EQUIVALENCE THIS CATALOGUE USES
=====================================
**The deduplication key of the n <= 38 catalogue is the S_k canonical form of
the logical gate: two factories collapse to one entry iff their output phase
polynomials agree after some *permutation* of the k output qubits.**  Nothing
coarser is quotiented out.  Every shipped entry additionally carries the
coarser GL(k,2) class as an annotation (``gate_gl_canonical``), so a GL census
can be recovered by grouping, with no re-run.

Two distinct things get called "output relabelling", and the catalogue depends
on keeping them apart:

1.  **Permuting the outputs (S_k) -- the key.**  Send output qubit i to
    sigma(i).  The phase polynomial transforms by the same permutation of its
    variables.  This is a relabelling of the *same* circuit, so factories
    related this way are genuinely one entry.

2.  **Changing the output basis (a CNOT frame).**  Replace the output rows
    a_1, ..., a_k of the factory by another basis of the same subspace of the
    quotient V, e.g. (a_0, a_1) -> (a_0, a_0 + a_1).  This is a *different
    circuit* producing a *different* phase polynomial, because the polynomial
    is read off pointwise products of the rows -- a nonlinear function of the
    basis.  The catalogue therefore lists such frames as separate rows.

    The worked example is ``[[28,2,3]]``, which appears twice.  Take a
    compatible independent pair (a_0, a_1) in V with |a_0| and |a_1| odd and
    |a_0 & a_1| even: the gate is ``0+1`` (T_0 . T_1).  Re-read the *same*
    subspace in the basis (a_0, a_0 + a_1): now |a_0 + a_1| is even and
    |a_0 & (a_0 + a_1)| = |a_0| - |a_0 & a_1| is odd, so the gate is ``0+01``
    (T_0 . CS_01).  One subspace, two rows.

3.  **The GL(k,2) annotation** is a third relation again: it is the orbit of
    the phase polynomial f under variable *substitution* f -> f o M for
    M in GL(k,2).  Since permutation matrices lie in GL(k,2), this is strictly
    coarser than the S_k key and grouping by it merges rows.  It is *not* the
    same as relation 2: ``0+1`` and ``0+01`` above have GL canonical truth
    tables 6 and 2, i.e. they are in different GL classes even though they come
    from one subspace.

Why key on S_k?  A CNOT frame change is free at the Clifford level, so a
coarser key is right if you only care *which magic state comes out*.  It is the
wrong key if you care *which circuit you must build*: the frames above have
different output phase polynomials, different exact T counts, and different
downstream synthillation behaviour.  This is a construction catalogue, so it
keeps the finer key.

Consequence for reading the catalogue, stated plainly: **row counts are
representation-dependent upper bounds on the number of inequivalent gates.**
Maxima (largest k, largest T count, which gates occur at all at a given n) are
unaffected, because those are properties of the set of realisable gates, not of
how the set is partitioned.  ``tests/test_dedup.py`` pins all of this down.

API
---
``sk_canonical(k, wants)`` / ``sk_canonical_with_perm(k, wants)`` / ``sk_name(pc)``
    The catalogue key and its printable label.  ``wants`` is a set of
    ``frozenset`` output-index monomials: ``{0}`` is a T on output 0, ``{0,1}``
    a CS, ``{0,1,2}`` a CCZ.  The canonical form is the lexicographic minimum,
    over all sigma in S_k, of the sorted tuple-of-tuples encoding.
    ``sk_canonical_with_perm`` returns that minimum together with a sigma
    attaining it, which the engines apply to the output qubits of a witness
    circuit so its stored columns deposit exactly the canonical gate rather
    than merely an S_k-equivalent one.

``canonical_gate(k, wants)`` / ``gate_truth_table(k, wants)``
    The GL(k,2) annotation.  A factory's logical action is the F_2 phase
    polynomial  f(x) = sum_{Q in wants} prod_{q in Q} x_q ; relabelling outputs
    by M in GL(k,2) sends f -> f o M.  ``gate_truth_table`` packs f into a
    2^k-bit integer (bit x = f(x)); ``canonical_gate`` returns the lexicographic
    minimum truth table over the whole group orbit, which is a complete
    invariant of the GL(k,2) class.  Both the group enumeration and the
    canonical form are memoised, since the classifier calls this once per
    candidate frame.  |GL(k,2)| = 6, 168, 20160, 9999360 for k = 2,3,4,5, so
    exact canonicalisation is instant through k=4.  At k=5 it is a real cost,
    paid once per process and worth knowing before you invoke it: ``_gl_perms``
    materialises all 9,999,360 index permutations, about a minute and ~3 GB of
    resident memory.  Only the k=5 [[31,5,3]] class needs it, and only when its
    ``gate_gl_canonical`` annotation is computed; the caches are in-memory, so
    every fresh process that reaches k=5 pays it again.

``gate_name(k, wants)``
    Human-readable label: monomials written as concatenated output indices and
    joined by '+', e.g. ``0+1+01`` is T_0 . T_1 . CS_01 and ``012`` is CCZ_012.

Pure Python (``itertools`` only).  Shared by ``classify.py`` (the main engine),
``classify_rowspace.py`` (the independent cross-check) and
``hard_parent_n31.py``, so every code path deduplicates by exactly the same key.
"""

from itertools import permutations


# ------------------------------------------------------------------ S_k key
def _encode(wants):
    """Hashable canonical encoding of a monomial set: a sorted tuple of sorted
    tuples, so that monomial sets are totally ordered."""
    return tuple(sorted(tuple(sorted(Q)) for Q in wants))


def sk_canonical_with_perm(k, wants):
    """``(canonical encoding, permutation attaining it)``.

    The permutation is returned so that a *witness circuit* can be relabelled
    into the canonical frame instead of merely being compared up to S_k: with
    ``perm`` mapping output ``i -> perm[i]``, relabelling the output qubits of
    the circuit by ``perm`` makes it deposit exactly the canonical gate.  That
    is what keeps every catalogued row's columns and its ``gate`` string in
    literal agreement (see ``classify.py``'s ``record`` and
    ``build_catalog.py``'s ``canonicalise_columns``).
    """
    best = None
    best_perm = tuple(range(k))
    for p in permutations(range(k)):
        img = {frozenset(p[i] for i in Q) for Q in wants}
        e = _encode(img)
        if best is None or e < best:
            best, best_perm = e, p
    return best, best_perm


def sk_canonical(k, wants):
    """THE CATALOGUE KEY.  Canonical form of the logical gate under output-qubit
    permutations S_k -- gates are identified only up to relabelling outputs.

    Returns the lexicographic minimum encoding over all k! permutations.  Cost
    is O(k! * |wants|); k <= 5 here, so at most 120 relabellings per call."""
    return sk_canonical_with_perm(k, wants)[0]


def sk_name(pc):
    """Readable label for an ``sk_canonical`` encoding: degree-1 monomials
    first, then degree-2, then degree-3, each group sorted, joined by '+'."""
    order = {1: [], 2: [], 3: []}
    for Q in pc:
        order[len(Q)].append(''.join(map(str, Q)))
    parts = []
    for deg in (1, 2, 3):
        parts += sorted(order[deg])
    return '+'.join(parts) if parts else 'check-only'


# ------------------------------------------------- GL(k,2) class (annotation)
import itertools

_GL_CACHE = {}
_CANON_CACHE = {}


def _gl_perms(k):
    """Index permutations of F_2^k induced by every M in GL(k,2)."""
    if k in _GL_CACHE:
        return _GL_CACHE[k]
    perms = []
    # enumerate invertible matrices as ordered independent column tuples
    for cols in itertools.product(range(1 << k), repeat=k):
        # rank-k check over F_2.  Each stored basis vector was itself reduced
        # against all earlier ones, so stored vectors are zero at every earlier
        # top-bit pivot; hence one in-order min-pass clears every pivot from v
        # and v == 0 iff v is dependent.  (min(v, v^b) clears b's top bit from
        # v iff set.)  Sound only because of that mutual reduction -- do not
        # reuse this pass over an unreduced vector list.
        basis = []
        ok = True
        for c in cols:
            v = c
            for b in basis:
                v = min(v, v ^ b)
            if v == 0:
                ok = False
                break
            basis.append(v)
        if not ok:
            continue
        # M x : column j of M is cols[j]; (Mx)_i = sum_j x_j cols[j]
        perm = [0] * (1 << k)
        for x in range(1 << k):
            y = 0
            for j in range(k):
                if (x >> j) & 1:
                    y ^= cols[j]
            perm[x] = y
        perms.append(tuple(perm))
    _GL_CACHE[k] = perms
    return perms


def gate_truth_table(k, wants):
    """Pack the phase polynomial of `wants` into a 2^k-bit truth table."""
    tt = 0
    for x in range(1 << k):
        v = 0
        for Q in wants:
            p = 1
            for q in Q:
                p &= (x >> q) & 1
            v ^= p
        if v:
            tt |= 1 << x
    return tt


def canonical_gate(k, wants):
    """Canonical form of the target under GL(k,2): min over the group of the
    permuted 2^k-bit truth table.  Cached by raw truth table."""
    tt = gate_truth_table(k, wants)
    key = (k, tt)
    if key in _CANON_CACHE:
        return _CANON_CACHE[key]
    best = tt
    for perm in _gl_perms(k):
        p = 0
        for x in range(1 << k):
            if (tt >> perm[x]) & 1:
                p |= 1 << x
        if p < best:
            best = p
    _CANON_CACHE[key] = best
    return best


def gate_name(k, wants):
    """Human-readable target label from the wanted monomials.

    Monomials are written as concatenated output indices, joined by '+':
    e.g. `0+1+01` is T_0 . T_1 . CS_01, and `012` is CCZ_012.
    """
    parts = []
    for Q in sorted(wants, key=lambda q: (len(q), tuple(sorted(q)))):
        parts.append(''.join(str(q) for q in sorted(Q)))
    return '+'.join(parts) if parts else 'check-only'
