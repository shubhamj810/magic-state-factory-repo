#!/usr/bin/env python3
"""The ``GL(k,2)`` deduplication key: output gates up to a CNOT frame.

The master catalogue keys on ``(n, k, GL(k,2) class of the gate)``: two
factories are one entry iff some invertible change of the OUTPUT basis
(``x -> Ax``, a CNOT circuit on the outputs) carries one deposited gate to the
other modulo diagonal Cliffords.  That is the CNOT+S output equivalence of the
length-54 classification (Wills, Jain and Singh), and it is strictly coarser
than the ``S_k`` relation `skcanon` implements: ``T0.T1`` and ``T0.CS01`` are
one class here, because substituting ``x1 -> x0 + x1`` turns the first into
the second times an ``S``.

WHAT IS COMPARED
----------------
A level-3 diagonal gate is a phase ``f : F_2^k -> Z_8``; the stored monomial set
is ``f`` modulo Clifford (``T = 1``, ``CS = 2``, ``CCZ = 4`` in units of
``pi/4``).  Its third finite difference

    tau(u, v, w) = (D_u D_v D_w f) / 4   (mod 2)

is a symmetric ``F_2``-trilinear form.  On basis vectors it reads off the
monomial set directly -- ``tau(a,a,a)`` is the ``T`` on output ``a``,
``tau(a,a,b) = tau(a,b,b)`` is the ``CS`` on ``{a,b}``, ``tau(a,b,c)`` is the
``CCZ`` on ``{a,b,c}`` -- so it is built here from the monomials without ever
tabulating ``f``, at any ``k``.  It vanishes exactly on Clifford phases, and it
transforms covariantly: the gate ``f(Ax)`` has tensor ``tau(Au, Av, Aw)``.  Two
gates are therefore ``GL(k,2)``-equivalent iff their tensors are congruent, and
that is what `gl_isomorphic` decides.  `tests/test_glcanon.py` pins both facts
against a literal enumeration of ``GL(k,2)`` on truth tables.

Two consequences of working modulo Clifford are worth stating.  AFFINE frames
add nothing: ``f(x + c) - f(x)`` is a level-2 phase, so an ``X`` on an output is
a diagonal Clifford here and "CNOT+S" and "CNOT+S+X" are the same relation.
And a ``T`` and a ``T^dagger`` on the same output (``1`` and ``7``), or ``CS``
and ``CS^dagger``, are one gate, which is exactly the parity read-off of
`faultcore.recover_gate`.

This is NOT the ``gl_class`` annotation of
``classification/exhaustive_n38/dedup.py``, which orbits the gate's XOR (``F_2``)
truth table and so separates ``0+1`` from ``0+01``.  Phases live in ``Z_8``:
substituting ``x1 -> x0 + x1`` (a CNOT) into the phase ``x0 + x1`` of ``T0.T1``
gives ``x0 + (x0 + x1 - 2 x0 x1) = 2 x0 + x1 - 2 x0 x1``, which is ``T1.CS01``
up to the Clifford ``S0`` and ``CS01^2 = CZ01`` -- and ``T1.CS01`` is ``0+01``
after swapping the outputs.  The two gates prepare one magic state up to CNOT
and ``S``, and the catalogue keys on that.

HOW IT IS DECIDED
-----------------
No closed-form canonical form is computed -- ``|GL(7,2)|`` is 1.6e14 -- so,
like `skcanon.sk_isomorphic` for the rows it cannot canonicalise, this is a
bounded decision procedure:

0.  **Fast paths.**  Equal tensors are the identity frame, and gates equal up
    to an output PERMUTATION (`skcanon.sk_isomorphic`) are equal up to a frame.
    Both are exact and cheap at any ``k``.
1.  **Labels.**  For every ``u != 0`` the slice ``B_u = tau(u, ., .)`` is a
    symmetric matrix and ``d_u = tau(u, u, .)`` a vector.  The tuple
    ``(rank B_u, tau(u,u,u), d_u != 0)`` is unchanged by a frame change that
    maps ``u`` to ``Au``, so the multiset of labels is an invariant and a
    mismatch is a proof of inequivalence.  (``d_u`` is a row sum of ``B_u``, so
    it never raises the rank and is not a separate rank invariant.)  Two
    coarser invariants -- the ranks of the tensor's flattening and of
    ``u -> d_u`` -- are checked first at every ``k``.
2.  **Search**, for ``k <= LABEL_K_CAP`` only.  Above the cap no search runs:
    the label pass and the span bookkeeping are exponential in ``k``, so a pair
    that neither the fast paths nor the coarse invariant settle comes back
    ``None`` at once rather than after exhausting memory.
    Otherwise: pick a basis of the right-hand gate from its rarest labels and
    assign each basis vector an image of the same label on the left, keeping
    the images independent.  Every new image is checked against ``tau`` on all
    basis triples already committed -- which, the form being trilinear, is the
    WHOLE condition once the basis is complete -- and against the labels of
    every vector in the span built so far.

The search has a work budget and returns ``None`` when it runs out, never a
guess: a search that gave up has not shown two gates to differ.  Callers treat
``None`` exactly as they treat an undecided `skcanon.sk_isomorphic`.
"""
from __future__ import annotations

import hashlib
from collections import Counter, defaultdict

#: Labels enumerate all ``2^k - 1`` nonzero vectors.  At ``k = 16`` that is 65,535
#: small rank computations per gate, about a second; above it the label pass is
#: skipped and only the coarse invariant is available.
LABEL_K_CAP = 16

#: The isomorphism search is budgeted in WORK, a deterministic quantity, so the
#: same pair gets the same verdict on a fast machine and a slow one.  A candidate
#: costs one unit plus one per tensor triple it is checked against plus one per
#: span vector whose label it is checked against -- the last term is what grows
#: as ``2^depth``, and counting only candidates would let the same allowance
#: buy 65,536 times more work at depth 16 than at depth 0.
WORK_BUDGET = 50_000_000


# ------------------------------------------------------------------- tensor
def tensor(k: int, monomials) -> tuple[tuple[int, ...], ...]:
    """``T[a][b]`` as a bitmask over ``c`` with bit ``c`` set iff ``tau(a,b,c)``.

    Built straight from the monomial set: a ``T`` on ``a`` sets ``(a,a,a)``, a
    ``CS`` on ``{a,b}`` sets every arrangement of ``(a,a,b)`` and ``(a,b,b)``,
    a ``CCZ`` on ``{a,b,c}`` every arrangement of ``(a,b,c)``.
    """
    T = [[0] * k for _ in range(k)]

    def put(a, b, c):
        T[a][b] |= 1 << c

    for mono in monomials:
        m = sorted(mono)
        if not all(isinstance(i, int) and 0 <= i < k for i in m) \
                or len(set(m)) != len(m) or not 1 <= len(m) <= 3:
            raise ValueError(f"not a level-3 monomial on {k} outputs: {mono!r}")
        if len(m) == 1:
            (a,) = m
            put(a, a, a)
        elif len(m) == 2:
            a, b = m
            for x, y, z in ((a, a, b), (a, b, a), (b, a, a),
                            (a, b, b), (b, a, b), (b, b, a)):
                put(x, y, z)
        else:
            a, b, c = m
            for x, y, z in ((a, b, c), (a, c, b), (b, a, c),
                            (b, c, a), (c, a, b), (c, b, a)):
                put(x, y, z)
    return tuple(tuple(row) for row in T)


def _bits(mask: int):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def evaluate(T, u: int, v: int, w: int) -> int:
    """``tau(u, v, w)`` for vectors given as bitmasks over the outputs."""
    acc = 0
    for a in _bits(u):
        row = T[a]
        for b in _bits(v):
            acc ^= row[b]
    return (acc & w).bit_count() & 1


def _rank(vectors) -> int:
    basis = []
    for v in vectors:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return len(basis)


# ------------------------------------------------------------------- invariants
def labels(k: int, T) -> dict[int, tuple]:
    """``u -> (rank B_u, tau(u,u,u), d_u != 0)`` for every nonzero ``u``."""
    return _labels(k, T)


def _labels(k: int, T) -> dict[int, tuple]:
    """The label of every nonzero ``u``, by Gray code over ``F_2^k``.

    ``B_u`` and ``d_u`` are both linear in ``u``, so walking the Gray code
    updates each by one XOR of a basis slice instead of recomputing it.
    """
    if k > LABEL_K_CAP:
        raise ValueError(f"labels are enumerated for k <= {LABEL_K_CAP} only")
    B = [0] * k
    d = 0
    diag = [T[a][a] for a in range(k)]
    out = {}
    u = 0
    for step in range(1, 1 << k):
        a = (step & -step).bit_length() - 1
        u ^= 1 << a
        row = T[a]
        for b in range(k):
            B[b] ^= row[b]
        d ^= diag[a]
        out[u] = (_rank(B), (d & u).bit_count() & 1, int(d != 0))
    return out


def coarse_invariant(k: int, T) -> tuple:
    """What survives without enumerating vectors: two flattening ranks."""
    flat = [sum(T[a][b] << (b * k) for b in range(k)) for a in range(k)]
    diag = [T[a][a] for a in range(k)]
    return (k, _rank(flat), _rank(diag))


def gl_fingerprint(k: int, monomials) -> str:
    """A ``GL(k,2)``-INVARIANT signature: equivalent gates always share it."""
    T = tensor(k, monomials)
    payload = (coarse_invariant(k, T),)
    if k <= LABEL_K_CAP:
        payload += (sorted(Counter(labels(k, T).values()).items()),)
    return hashlib.sha256(repr(payload).encode()).hexdigest()[:16]


# ------------------------------------------------------------------- deciding
class _OutOfNodes(Exception):
    """Raised through the recursion when the node budget runs out."""


def gl_transform(k: int, left, right, node_budget: int | None = None):
    """A witness ``(basis, images)`` with ``tau_left(images) = tau_right(basis)``.

    ``basis`` is a basis of ``F_2^k`` (bitmasks) and ``images[i]`` is where the
    frame change sends ``basis[i]``; the images are independent and the tensor
    agrees on every basis triple, which for a trilinear form is equivalence.
    Returns ``False`` when no such frame change exists and ``None`` when that
    could not be decided -- the work budget ran out, or ``k`` is above
    `LABEL_K_CAP` and neither a fast path nor the coarse invariant settled it.
    ``node_budget`` is a WORK allowance (see `WORK_BUDGET`).
    """
    if node_budget is None:
        node_budget = WORK_BUDGET
    left, right = list(left), list(right)
    # validate both sides first, so a malformed monomial is refused at every k
    TL, TR = tensor(k, left), tensor(k, right)
    standard = [1 << i for i in range(k)]
    if TL == TR:
        return (standard, list(standard))
    if k < 1:
        return False                    # both empty would have been equal
    if coarse_invariant(k, TL) != coarse_invariant(k, TR):
        return False
    if k > LABEL_K_CAP:
        # No labels and no search up here.  The one thing still worth trying is
        # a PERMUTATION: it is a frame change, `skcanon` decides it exactly, and
        # the wide rows are regular gates -- T on every output, disjoint CCZs --
        # where it answers at once.  Below the cap the search decides everything
        # this would, so paying for `sk_isomorphic` there only slows the common
        # case down: its own budget is spent in full on every pair that is not a
        # relabelling, which is most of them.
        import skcanon                  # local: skcanon is the finer relation
        perm = _permutation_witness(k, left, right, skcanon)
        return (standard, perm) if perm is not None else None
    LL, LR = labels(k, TL), labels(k, TR)
    if Counter(LL.values()) != Counter(LR.values()):
        return False
    by_label = defaultdict(list)
    for p, lab in LL.items():
        by_label[lab].append(p)

    # a basis of the RIGHT gate, rarest labels first, so the first choices
    # branch least
    order = sorted(LR, key=lambda p: (len(by_label[LR[p]]), p))
    basis, span = [], {0}
    for p in order:
        if p not in span:
            basis.append(p)
            span |= {s ^ p for s in span}
            if len(basis) == k:
                break
    want = {}
    for i in range(k):
        for j in range(i, k):
            for l in range(j, k):
                want[i, j, l] = evaluate(TR, basis[i], basis[j], basis[l])
    work = 0

    def extend(i, images, spanmap, image_span):
        nonlocal work
        if i == k:
            return list(images)
        b = basis[i]
        for cand in by_label[LR[b]]:
            work += 1
            if work > node_budget:
                raise _OutOfNodes
            if cand in image_span:
                continue
            trial = images + [cand]
            ok = True
            for j in range(i + 1):
                for l in range(j, i + 1):
                    # triples (j, l, i) with j <= l <= i cover every new one
                    work += 1
                    if evaluate(TL, trial[j], trial[l], cand) != want[j, l, i]:
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                continue
            work += len(spanmap)
            if work > node_budget:
                raise _OutOfNodes
            grown = dict(spanmap)
            for s, image in spanmap.items():
                if LL[image ^ cand] != LR[s ^ b]:
                    ok = False
                    break
                grown[s ^ b] = image ^ cand
            if not ok:
                continue
            found = extend(i + 1, trial, grown, set(grown.values()))
            if found is not None:
                return found
        return None

    try:
        images = extend(0, [], {0: 0}, {0})
    except _OutOfNodes:
        return None
    return (basis, images) if images is not None else False


def _permutation_witness(k, left, right, skcanon):
    """Images of the basis under an output permutation relating the gates, or
    ``None`` when there is none or the permutation search did not finish.

    Taken from `skcanon.sk_isomorphism`, which returns the relabelling itself,
    rather than from a canonical form: the rows that most need this fast path
    are exactly the ones whose ``k!`` minimisation was never proved, and they
    have no canonical form to compare.  ``m`` maps a LEFT output to a RIGHT
    one, so the right basis vector ``e_{m[q]}`` is the image of ``e_q``.
    """
    mapping = skcanon.sk_isomorphism(k, left, right)
    if not isinstance(mapping, dict):
        return None                     # ``False`` (not a permutation) or ``None``
    images = [0] * k
    for q, image in mapping.items():
        images[image] = 1 << q
    return images


def gl_isomorphic(k: int, left, right, node_budget: int | None = None):
    """``True``/``False``, or ``None`` when the search ran out of budget."""
    found = gl_transform(k, left, right, node_budget)
    if found is None:
        return None
    return found is not False
