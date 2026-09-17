#!/usr/bin/env python3
"""The ``S_k`` deduplication key, at the widths the new corpora reach.

The master catalogue keys on ``(n, k, S_k``-canonical gate``)``: two factories
are one entry iff their output phase polynomials agree after some PERMUTATION of
the output qubits (`theory/02_classification.md`, relation 1).  A CNOT frame
change is a different circuit and keeps its own row; the ``GL(k,2)`` class is
strictly coarser and is only ever an annotation.  None of that changes here.

What changes is ``k``.  `classification/legacy/exhaustive_n38/dedup.py` computes the key
by minimising over all ``k!`` relabellings, which is exact and instant at the
``k <= 6`` those catalogues reach and is 1e289 permutations at the ``k = 162``
this catalogue's widest rows reach.  This module keeps the same definition and
computes it three ways, in decreasing order of what can be proved:

1.  **Disjoint cover** -- every monomial pairwise disjoint and together covering
    the outputs.  The lex-minimum is then closed-form: lay the monomials out in
    consecutive blocks with the SMALLEST monomials first.  This is what almost
    every wide gate here is (``T`` on all ``k`` outputs, or a disjoint set of
    ``CCZ``s), and it is exact at any ``k``.
2.  **Brute force** over all ``k!`` permutations for ``k <= 9``, which is the
    upstream definition executed literally, and is what pins case 1 in the tests.
3.  **Branch and bound** for wider irregular gates: assign output labels
    ``0, 1, 2, ...`` in order, and abandon a branch as soon as the best possible
    completion is no better than the best labelling already found.

Case 3 has a node budget, and when it runs out this module returns ``None``
rather than a guess.  A gate with no canonical form is not a gate that can be
deduplicated wrongly: `sk_fingerprint` gives a permutation-invariant signature
for bucketing and `sk_isomorphic` decides the remaining comparisons exactly, so
the KEY is always sound.  What such a row loses is only cosmetic -- it is shown
in its as-found output frame instead of a canonical one, and says so.
"""
from __future__ import annotations

import hashlib
import itertools
from collections import Counter

BRUTE_FORCE_K = 9                 # 9! = 362,880: the largest exhaustive sweep

# The branch and bound is budgeted in WORK rather than in seconds, so the same
# input gets the same answer on a fast machine and a slow one -- a catalogue key
# that depended on how busy the CPU was would not be a key.
#
# A node costs one pass over the monomials plus the sort that orders them, and
# when the best-first ordering is on it costs that once per candidate.  So the
# node allowance is the work allowance divided by what a node actually costs,
# which is what keeps a 9-monomial gate on 11 outputs (needs ~4e6 nodes, and
# gets them) and a 3,587-monomial gate on 36 outputs (would need more nodes than
# exist, and is refused in seconds) both bounded by the same number.
WORK_ALLOWANCE = 2_000_000_000
MIN_NODE_BUDGET = 1_000
#: above this the ordering heuristic costs more than it saves
ORDER_LIMIT = 5_000


def node_budget_for(monomials, k: int) -> int:
    size = max(1, len(monomials))
    ordered = k * size <= ORDER_LIMIT
    per_node = size * max(1, size.bit_length()) * (k if ordered else 1)
    return max(MIN_NODE_BUDGET, WORK_ALLOWANCE // per_node)


def isomorphism_node_budget(k: int, left, right) -> int:
    """The same work allowance, against the ISOMORPHISM search's node cost.

    `node_budget_for` drops the ``k`` factor once ``k * size`` is large, because
    the branch and bound's node is one pass over the monomials and does not grow
    with ``k``.  The re-refining isomorphism node does: every consistent
    candidate pays two full `_refine` passes over all ``k`` vertices.  Charging
    it the cheaper rate let the same node count buy about 250x the work -- a
    constructed k = 160 pair ran past 550 seconds inside one call and
    extrapolated to some forty minutes, where the pre-rewrite search gave up in
    2.2 -- so this function keeps the ``k`` factor unconditionally.  The budget
    is still WORK, not wall clock: the same input must get the same answer on a
    fast machine and a slow one, and a verdict that depended on how busy the CPU
    was would not be a verdict.
    """
    size = max(1, max(len(left), len(right)))
    per_node = size * max(1, size.bit_length()) * max(1, k)
    return max(MIN_NODE_BUDGET, WORK_ALLOWANCE // per_node)


class _Exhausted(Exception):
    """The branch and bound ran out of nodes; no canonical form was proved."""


# ------------------------------------------------------------------- encoding
def encode(monomials) -> tuple:
    """Hashable total order on monomial sets: sorted tuple of sorted tuples."""
    return tuple(sorted(tuple(sorted(Q)) for Q in monomials))


def apply_perm(monomials, perm) -> tuple:
    """Relabel by ``perm``, where output ``i`` becomes output ``perm[i]``."""
    return encode(tuple(perm[i] for i in Q) for Q in monomials)


def gate_string(monomials, k: int) -> str:
    """The catalogue's gate label.

    Degree-1 monomials first, then degree-2, then degree-3, each group sorted:
    byte-for-byte `dedup.sk_name`, so master-catalogue rows keep the exact gate
    strings they already have.  ``0+1+01`` is ``T_0 . T_1 . CS_01``; ``012`` is
    ``CCZ_012``.

    Above ``k = 10`` the concatenated digits stop being separable -- ``012``
    could be ``CCZ`` on 0,1,2 or ``CS`` on 0 and 12 -- so monomials switch to
    comma form, ``0,1,2``.  Only rows wider than any existing one are affected,
    and the machine-readable key is ``sk_key`` either way; this is the label.
    """
    wide = k > 10
    parts = []
    for mono in sorted((tuple(sorted(Q)) for Q in monomials),
                       key=lambda Q: (len(Q), Q)):
        parts.append(",".join(map(str, mono)) if wide else "".join(map(str, mono)))
    return "+".join(parts) if parts else "check-only"


LEVEL_GATE = {1: "T", 2: "CS", 3: "CCZ"}


def gate_human(monomials, k: int) -> str:
    """``{0},{0,1}`` -> ``T0·CS01``; comma-separated indices above ``k = 10``."""
    wide = k > 10
    parts = []
    for mono in sorted((tuple(sorted(Q)) for Q in monomials),
                       key=lambda Q: (len(Q), Q)):
        digits = ",".join(map(str, mono)) if wide else "".join(map(str, mono))
        parts.append(LEVEL_GATE.get(len(mono), f"deg{len(mono)}") + digits)
    return "·".join(parts) if parts else "(identity)"


# ------------------------------------------------------- case 1: disjoint cover
def _disjoint_cover_perm(k: int, monomials):
    """``perm`` for a gate whose monomials are disjoint and cover the outputs.

    Lay the monomials in consecutive label blocks, smallest first.  That is the
    lex-minimum: the sorted encoding compares its first tuple first, and a
    shorter tuple sharing a prefix is smaller -- ``(0,) < (0,1) < (0,1,2)`` --
    so putting a smaller monomial earlier can only reduce the encoding, and
    within one size ordering does not matter because the blocks are consecutive.
    """
    monomials = [tuple(sorted(Q)) for Q in monomials]
    if not monomials:
        return None
    seen: set[int] = set()
    for mono in monomials:
        if seen & set(mono):
            return None                                    # not disjoint
        seen |= set(mono)
    if seen != set(range(k)):
        return None                                        # not a cover
    perm = [None] * k
    label = 0
    for mono in sorted(monomials, key=lambda Q: (len(Q), Q)):
        for q in mono:
            perm[q] = label
            label += 1
    return tuple(perm)


# ----------------------------------------------------------- case 3: branch/bound
def _branch_and_bound(k: int, monomials, node_budget: int):
    """Exact lex-minimum by assigning output labels ``0, 1, ...`` in order.

    The bound is the cheapest thing that is actually sound.  With labels
    ``0..t-1`` placed, a monomial whose members are all placed has a known image;
    one with ``u`` members still unplaced cannot do better than taking the
    smallest labels still available, ``t, t+1, ..., t+u-1``.  Replacing every
    monomial by that minimum and re-sorting gives a list that is entrywise below
    whatever the branch finally produces, so it is a lower bound on the encoding;
    if it is already no better than the best complete labelling in hand, the
    branch is dead.  ``>=`` rather than ``>`` because one optimum is all that is
    wanted, and equality cannot improve on what is already there.

    That bound is weak at the top of the tree, where nothing is placed and every
    monomial's minimum is the same tuple, so the search is ordered BEST-FIRST:
    at each node the candidates are ranked by the bound they would produce and
    tried in that order.  A strong incumbent found in the first descent is what
    makes the bound bite on every sibling afterwards, and it is the difference
    between seconds and not finishing on the wide irregular gates here.  The
    ordering is a heuristic; it changes the order leaves are visited, never
    which leaf is the minimum.
    """
    monomials = [tuple(sorted(Q)) for Q in monomials]
    label_of = [-1] * k
    best_encoding, best_perm = None, None
    nodes = 0
    # ranking every candidate costs |candidates| x |monomials| per node, which
    # pays for itself only while that product is small
    order_by_bound = k * len(monomials) <= ORDER_LIMIT

    def lower_bound(t: int) -> tuple:
        rows = []
        for mono in monomials:
            placed = [label_of[q] for q in mono if label_of[q] >= 0]
            missing = len(mono) - len(placed)
            if missing:
                placed += list(range(t, t + missing))
            rows.append(tuple(sorted(placed)))
        return tuple(sorted(rows))

    def recurse(t: int):
        nonlocal best_encoding, best_perm, nodes
        nodes += 1
        if nodes > node_budget:
            raise _Exhausted
        if t == k:
            encoding = encode(tuple(label_of[q] for q in Q) for Q in monomials)
            if best_encoding is None or encoding < best_encoding:
                best_encoding, best_perm = encoding, tuple(label_of)
            return
        if best_encoding is not None and lower_bound(t) >= best_encoding:
            return
        free = [q for q in range(k) if label_of[q] < 0]
        if order_by_bound and len(free) > 1:
            ranked = []
            for q in free:
                label_of[q] = t
                ranked.append((lower_bound(t + 1), q))
                label_of[q] = -1
            ranked.sort()
            free = [q for _bound, q in ranked]
        for q in free:
            label_of[q] = t
            recurse(t + 1)
            label_of[q] = -1

    recurse(0)
    return best_encoding, best_perm


# ------------------------------------------------------------------- the key
def sk_canonical_with_perm(k: int, monomials, node_budget: int | None = None):
    """``(canonical encoding, perm)``, or ``(None, None)`` if unproved.

    ``perm`` maps output ``i -> perm[i]``; relabelling the output wires of a
    witness circuit by it makes the circuit deposit exactly the canonical gate,
    which is what keeps a catalogue row's columns and its ``gate`` string in
    literal agreement instead of merely ``S_k``-equivalent.
    """
    monomials = [frozenset(Q) for Q in monomials]
    if not monomials:
        return (), tuple(range(k))
    if node_budget is None:
        node_budget = node_budget_for(monomials, k)
    perm = _disjoint_cover_perm(k, monomials)
    if perm is not None:
        return apply_perm(monomials, perm), perm
    if k <= BRUTE_FORCE_K:
        best, best_perm = None, None
        for candidate in itertools.permutations(range(k)):
            encoding = apply_perm(monomials, candidate)
            if best is None or encoding < best:
                best, best_perm = encoding, candidate
        return best, best_perm
    try:
        return _branch_and_bound(k, monomials, node_budget)
    except _Exhausted:
        return None, None


def sk_canonical(k: int, monomials, node_budget: int | None = None):
    return sk_canonical_with_perm(k, monomials, node_budget)[0]


# -------------------------------------------- invariant + exact isomorphism test
def _refine(k: int, monomials, colours):
    """One-dimensional Weisfeiler-Leman on the monomial hypergraph.

    A vertex's signature is its current colour plus, for every monomial it lies
    in, that monomial's size and the sorted colours of its other members.  This
    is invariant under relabelling by construction, so equal-coloured vertices in
    two gates are the only ones an isomorphism can match.
    """
    incident: list[list[tuple]] = [[] for _ in range(k)]
    for mono in monomials:
        members = sorted(mono)
        for q in members:
            incident[q].append((len(members), tuple(x for x in members if x != q)))
    while True:
        signature = []
        for q in range(k):
            marks = sorted((size, tuple(sorted(colours[x] for x in others)))
                           for size, others in incident[q])
            signature.append((colours[q], tuple(marks)))
        ranking = {sig: i for i, sig in enumerate(sorted(set(signature)))}
        new = [ranking[sig] for sig in signature]
        if new == colours:
            return colours, incident
        colours = new


def sk_fingerprint(k: int, monomials) -> str:
    """A permutation-INVARIANT signature: equal classes always share it.

    Used to bucket rows before the exact test below.  Two gates with different
    fingerprints are certainly inequivalent; two with the same one still have to
    be decided, which is what `sk_isomorphic` is for.
    """
    monomials = [frozenset(Q) for Q in monomials]
    sizes = Counter(len(Q) for Q in monomials)
    colours, _incident = _refine(k, monomials, [0] * k)
    payload = repr((k, sorted(sizes.items()), sorted(Counter(colours).items())))
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def sk_isomorphism(k: int, left, right, node_budget: int | None = None):
    """The relabelling itself: ``{left output -> right output}``, or the verdict.

    Returns a dict when the gates ARE one class, ``False`` when they are not and
    ``None`` when the search ran out of budget -- the same three answers as
    `sk_isomorphic`, which is this function with the mapping thrown away.  The
    mapping is what `glcanon` needs to turn "these differ by a permutation" into
    a frame-change witness at widths where no canonical form was ever proved.
    """
    return _sk_isomorphism(k, left, right, node_budget)


def sk_isomorphic(k: int, left, right, node_budget: int | None = None):
    """``True``/``False``, or ``None`` when the search ran out of budget.

    Backtracking over the refined colour classes: a vertex can only map to one
    of the same colour, and every candidate assignment is checked against the
    monomials already committed.  This is the decision the dedup key ultimately
    rests on for the handful of rows too wide to canonicalise.

    It is BOUNDED, for the same reason `_branch_and_bound` is.  Refinement is
    instant, but on a wide gate whose colour classes are large and
    automorphism-rich -- ``[[256,84]]``'s two classes of 56 and 28, or
    ``[[512,84]]``'s single class of 84 -- the backtracking behind it does not
    finish in any time anybody will wait, and an unbounded call here would hang
    the whole-file verify or a merge rather than answer them.  Exhaustion is
    reported as ``None`` and never as ``False``: a search that gave up has not
    shown the two gates to be different, and quietly returning "not isomorphic"
    is how a duplicate class enters a catalogue whose one promise is that it
    has none.  Callers must handle the third answer.

    The search re-refines because the plain one did not finish.  Fixing the
    vertices in one precomputed order and checking only committed monomials
    left three of the catalogue's six fingerprint-keyed rows undecidable
    against their own relabellings -- 4.2s, 0.4s and 0.9s to give up, and ten
    or a hundred times the budget did not rescue two of them.  The blow-up was
    the order, not the allowance: those gates have large automorphism-rich
    colour classes, 84 outputs in a SINGLE class at the widest.  Individualising
    each committed pair and re-refining splits those classes as the search
    descends, and all six now decide against a random relabelling in under a
    second and a half.

    That matters beyond tidiness.  An undecided pair is admitted with a
    ``dedup_note`` rather than refused, so a class that cannot be recognised is
    a class that can be re-filed under a fresh output frame -- one honest
    re-discovery per frame, each verifying clean.  Deciding these is what keeps
    "no duplicate classes" from going soft exactly where the gates are widest.
    """
    verdict = _sk_isomorphism(k, left, right, node_budget)
    return verdict if verdict is None else bool(verdict is not False)


def _sk_isomorphism(k: int, left, right, node_budget: int | None = None):
    """The search itself; returns the mapping, ``False`` or ``None``."""
    if node_budget is None:
        node_budget = isomorphism_node_budget(k, left, right)
    nodes = 0
    left = [frozenset(Q) for Q in left]
    right = [frozenset(Q) for Q in right]
    if k < 1:
        # No outputs, so the only permutation is the empty one and the answer is
        # whether both sides are empty.  Falling through would ask
        # `isomorphism_node_budget` for a per-node cost of zero and divide by it.
        return {} if (not left and not right) else False
    if Counter(len(Q) for Q in left) != Counter(len(Q) for Q in right):
        return False
    left_colours, _ = _refine(k, left, [0] * k)
    right_colours, _ = _refine(k, right, [0] * k)
    if Counter(left_colours) != Counter(right_colours):
        return False
    right_set = {tuple(sorted(Q)) for Q in right}

    def consistent(mapping: dict, q: int) -> bool:
        """Every monomial through ``q`` whose members are all mapped must land."""
        for mono in left:
            if q not in mono or any(x not in mapping for x in mono):
                continue
            if tuple(sorted(mapping[x] for x in mono)) not in right_set:
                return False
        return True

    class _OutOfNodes(Exception):
        """Raised through the recursion when the node budget runs out.

        Named apart from the module-level `_Exhausted` deliberately: that one
        belongs to the canonical-form branch and bound, this one to the
        isomorphism search, and the two must never be caught for each other.
        """

    def recurse(mapping: dict, used: set, lcol: list, rcol: list) -> bool:
        nonlocal nodes
        if len(mapping) == k:
            return {tuple(sorted(mapping[x] for x in Q)) for Q in left} == right_set
        # Chosen from the CURRENT colouring rather than a fixed order: after an
        # individualisation the constraint has moved, and the whole value of
        # re-refining is being able to follow it.
        free = [q for q in range(k) if q not in mapping]
        available = {}
        for q in free:
            available[q] = [c for c in range(k)
                            if c not in used and rcol[c] == lcol[q]]
        q = min(free, key=lambda x: len(available[x]))
        for candidate in available[q]:
            nodes += 1
            if nodes > node_budget:
                raise _OutOfNodes
            mapping[q] = candidate
            used.add(candidate)
            if consistent(mapping, q):
                # Individualise the pair just committed and refine both sides.
                # Fixing one vertex splits the colour classes around it, so the
                # candidate lists below shrink instead of staying at the full
                # class -- which is the difference between deciding a wide gate
                # in a second and not deciding it at all.  Refinement is
                # relabelling-invariant, so a colour multiset that no longer
                # matches is a proof this branch cannot extend.
                mark = -1 - len(mapping)
                sub_left = list(lcol); sub_left[q] = mark
                sub_right = list(rcol); sub_right[candidate] = mark
                sub_left, _ = _refine(k, left, sub_left)
                sub_right, _ = _refine(k, right, sub_right)
                if Counter(sub_left) == Counter(sub_right) \
                        and recurse(mapping, used, sub_left, sub_right):
                    return True
            used.discard(candidate)
            del mapping[q]
        return False

    found: dict[int, int] = {}

    try:
        if not recurse(found, set(), left_colours, right_colours):
            return False
    except _OutOfNodes:
        return None
    return dict(found)
