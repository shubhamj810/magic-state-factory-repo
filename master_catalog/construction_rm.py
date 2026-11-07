#!/usr/bin/env python3
"""Reed-Muller-type factories given by a rule: four construction families.

Each family turns a small JSON object into the columns of a circuit, in the
order `constructions.py` fixes for every stored construction: each column
sorted ascending, then the list of columns sorted lexicographically.  Wires
0..k-1 are the outputs and k..N-1 the checks; a column lists the wires (rows)
it touches.  ``columns_sha256`` is `digest` of that list, the SHA-256 of its
compact JSON text, exactly as in `constructions.py`.

`native_columns` gives the same circuit in the order the research code wrote
it (one column per surviving coordinate, in increasing coordinate order).  The
research digests were taken over that order, so the tests compare both.

The builders do not check that a result is a factory.  The verifier does
that on the columns, as for a stored circuit.  The two CCZ-frame checks at
the end (`packing_check`, `frame_check`) are separate functions that the
builders never call.  `problems` checks only the
shape of an object, with bounds, before anything is built, so that a corrupted
object is a named rejection and never a long loop or a large allocation.  The
one failure `columns` can still raise is a ValueError for a puncture set whose
points are dependent in the parent; finding that out costs as much as building.

Every family stores ``k`` and ``N`` as well, because the catalogue compares
them with the row's (`catalogfile._rule_problems`); `problems` requires them
to equal what the other fields imply.

THE FAMILIES
------------
``punctured-rm``  ``{"family", "m", "r", "punctures", "k", "N"}``
    The punctured Reed-Muller factories of Haah and Hastings
    (arXiv:1709.02832).  Points of F_2^m are the integers 0..2^m-1, bit i
    being coordinate x_i.  The parent rows are the evaluation vectors of the
    monomials of degree at most r, ordered by degree and then
    lexicographically by variable set (the order of
    ``itertools.combinations(range(m), d)``), so N = sum_{d<=r} C(m, d).
    ``punctures`` is strictly increasing.  For j = 0, 1, ..., t-1 in turn,
    with p = punctures[j]: take the first row with index >= j that is 1 at p,
    swap it into position j, and add it to every other row that is 1 at p.
    Rows 0..t-1 are then the outputs (output j is 1 at punctures[j] and 0 at
    the other punctures) and rows t..N-1 the checks, in their final order.
    Each surviving point is a column.  The reduction is the one in
    `research/search/lift/rm/rmfac.py`, written again here.

``punctured-weighted-rm``  ``{"family", "m", "weights", "cutoff", "punctures", "k", "N"}``
    Weighted Reed-Muller parents (Wills, arXiv:2608.24000, Definition 2.15, as
    the research reports cite it): the squarefree monomials x^a, a an m-bit
    mask, whose weighted degree sum_{i in a} weights[i] is at most
    ``cutoff``, in increasing order of the integer a; monomial a is 1 at the
    point x exactly when x & a == a.  ``punctures`` is an ordered list of
    distinct points; its order is the output order.  For each puncture p in
    turn: take the first row, in the current row order, that has not been
    chosen yet and is 1 at p; it becomes the next output; add it to every
    other row (outputs included) that is 1 at p.  The outputs are the chosen
    rows in puncture order, and the checks are the rows never chosen, in
    parent order.  The reduction is the one of `monomial.factory` in
    `research/search/sparse/code` and `research/search2/weighted/code`.  It is
    NOT the reduction of ``punctured-rm``, so the two families give different
    check rows for the same parent and puncture set, and the family name
    decides which one is meant.

``ccz-frame``  ``{"family", "q", "triples", "k", "N"}``
    The CCZ frame on RM(q-1, m), m = 3q (`research/search/parents/REPORT.md`
    section 1).  ``triples`` is a list of c triples, each a list of three
    q-subsets of {0..m-1} (each subset a strictly increasing list).  The
    outputs are the monomials x_S for the 3c sets S, triple by triple, so
    output 3i + j is triples[i][j]; the checks are all monomials of degree at
    most q-1, by degree and then lexicographically.  Every point x of F_2^m
    is a column, touching output i when x contains S_i and check j when x
    contains the j-th check's variable set.  k = 3c and
    N = 3c + sum_{d<q} C(m, d).

``four-block``  ``{"family", "L", "removed_flats", "punctures", "k", "N"}``
    The four-block parent of the gamma-frontier release
    (`research/search2/strategy/REPORT.md` section 3.1).  S is F_2^L minus
    the listed 4-flats, each [o, d1, d2, d3, d4] = o + span(d1..d4).  The
    points of S are numbered 0..M-1 in increasing order.  A = span{1, x_0..x_{L-1}}
    on S, AA = A plus the products x_i x_j (i < j), and F the vectors of F_2^S
    orthogonal to AA.  The basis of F is the reduced one: bring AA's row space
    to reduced echelon form with the pivot of each row at its highest
    coordinate; for each non-pivot coordinate j, in increasing j, the basis
    vector is the element of F that is 1 at j and 0 at every other non-pivot
    coordinate.  Coordinate b*M + i is point i of S in block b (b = 0..3).
    The parent rows, in order, are (f, f, f, f) for each basis vector f, then
    (0, a, 0, a) and then (0, 0, a, a) for a = 1, x_0, ..., x_{L-1}.  The
    punctures are coordinates, reduced as in ``punctured-weighted-rm``.  The
    object format matches `research/search2/fourblock/code/fbconstruct.py`
    (with k and N required here).

THE CCZ FRAME THEOREM (research/search/parents/REPORT.md, section 1.2)
---------------------------------------------------------------------
Let q >= 1 and m = 3q.  Let F be a family of q-subsets of [m] = {0..m-1} that
splits into c triples, each a partition of [m], such that no other three
members of F partition [m].  Take all 2^m points of F_2^m as columns, the
monomials of degree at most q-1 as check wires and the monomials x_S, S in F,
as outputs.  This circuit is a factory with gate CCZ^c on the c triples,
effective width 3c and distance exactly 2^q.

Proof.  Three wires with monomials x_A, x_B, x_C (repeats allowed) overlap in
2^(m - |A u B u C|) columns, so the overlap is odd exactly when
A u B u C = [m].  If one of the wires is a check, |A u B u C| <= (q-1) + 2q
< m, so no parity that touches a check is odd and there is no contamination.
One or two outputs cover at most 2q < m coordinates, so there is no T and no
CS.  Three outputs have odd overlap exactly when they partition [m], and by
hypothesis that happens on the c designated triples and nowhere else.  So the
gate is CCZ on c disjoint triples, with no spectator.

Monomials of degree at most q are linearly independent functions on F_2^m, so
the check rows are independent and the outputs are independent modulo the
checks.

A fault E (a set of points) is undetected when every check monomial is 1 on
an even number of points of E, that is, when 1_E is orthogonal to RM(q-1, m).
The dual of RM(q-1, m) is RM(2q, m) (MacWilliams and Sloane, The Theory of
Error-Correcting Codes, ch. 13, Thm 4), whose nonzero words weigh at least
2^q (ibid., Thm 3).  So every nonempty undetected fault, harmful or not, has
weight at least 2^q.

For an output S, let E be the span of the unit vectors e_i, i in S.  Its
indicator is the product of (1 + x_j) over the 2q coordinates j outside S, a
polynomial of degree 2q, so E is undetected.  The output x_S is 1 at exactly
one point of E, so E flips output S, and d = 2^q.  The degree-1 checks recover
each point, so the columns are distinct.  QED.

`packing_check` tests the hypothesis on the family itself, and `frame_check`
tests, from the columns alone, that a circuit is this frame for the family.

PROVENANCE AND TESTS
--------------------
Each builder was written from the definitions above and imports nothing from
the research tree.  `tests/test_construction_rm.py` rebuilds the research
circuits and compares digests, both in the research's own column order and in
the order above.
"""
from __future__ import annotations

import hashlib
import json
from itertools import combinations
from math import comb

FAMILIES = {
    "punctured-rm": ("m", "r", "punctures", "k", "N"),
    "punctured-weighted-rm": ("m", "weights", "cutoff", "punctures", "k",
                              "N"),
    "ccz-frame": ("q", "triples", "k", "N"),
    "four-block": ("L", "removed_flats", "punctures", "k", "N"),
}

DESCRIPTIONS = {
    "punctured-rm": (
        "Haah and Hastings (arXiv:1709.02832): points of F_2^m are the "
        "integers 0..2^m-1, bit i being x_i; parent rows are the monomials of "
        "degree <= r evaluated at all points, ordered by degree then by "
        "itertools.combinations(range(m), d), so N = sum_{d<=r} C(m,d); "
        "punctures strictly increasing; for j = 0..t-1 with p = punctures[j], "
        "swap the first row with index >= j that is 1 at p into position j and "
        "add it to every other row that is 1 at p; rows 0..t-1 are outputs "
        "(k = t), rows t..N-1 checks; one column per surviving point listing "
        "the rows that are 1 there; columns sorted ascending, then the list "
        "sorted lexicographically"),
    "punctured-weighted-rm": (
        "weighted Reed-Muller parent (Wills, arXiv:2608.24000, Def. 2.15): "
        "the squarefree monomials x^a (a an m-bit mask) with sum of "
        "weights[i] over bits i of a <= cutoff, in increasing a, monomial a "
        "being 1 at point x iff x & a == a; for each puncture p in list order "
        "the first not-yet-chosen row (current order) that is 1 at p becomes "
        "the next output and is added to every other row that is 1 at p; "
        "outputs are the chosen rows in puncture order, checks the unchosen "
        "rows in parent order; one column per surviving point listing the "
        "wires that are 1 there; columns sorted ascending, then the list "
        "sorted lexicographically"),
    "ccz-frame": (
        "CCZ frame on RM(q-1, 3q): every point x of F_2^m (m = 3q, bit i = "
        "x_i) is a column; outputs are the monomials x_S for the q-sets S of "
        "triples, triple by triple (output 3i+j = triples[i][j]); checks are "
        "all monomials of degree <= q-1, by degree then by "
        "itertools.combinations(range(m), d); column x touches output i iff "
        "x contains S_i and check j iff x contains its variable set; the "
        "gate is CCZ on outputs (3i, 3i+1, 3i+2) and d = 2^q when each "
        "triple partitions {0..m-1} and no other three of the sets do; "
        "columns sorted ascending, then the list sorted lexicographically"),
    "four-block": (
        "four-block parent: S = F_2^L minus the 4-flats [o,d1,d2,d3,d4] in "
        "removed_flats, points numbered 0..M-1 in increasing order; F = the "
        "vectors on S orthogonal to 1, x_i and x_i x_j, with the basis "
        "e_j + (pivots of the rows that are 1 at j) for each non-pivot j in "
        "increasing order, after reducing those functions to echelon form "
        "with each pivot at its row's highest coordinate; coordinate b*M+i is "
        "point i in block b; parent rows (f,f,f,f) for each basis f, then "
        "(0,a,0,a), then (0,0,a,a) for a = 1, x_0..x_{L-1}; for each "
        "puncture (a coordinate) in list order the first not-yet-chosen row "
        "that is 1 there becomes the next output and is added to every other "
        "row that is 1 there; checks are the unchosen rows in parent order; "
        "one column per surviving coordinate; columns sorted ascending, then "
        "the list sorted lexicographically"),
}

#: Bounds checked before anything is built.  The parents have 2^m (or 4M)
#: coordinates and at most a few thousand rows; at these caps the largest
#: build is about 16,000 columns and takes seconds.  Every circuit the
#: research produced for these families is inside them.
MAX_M = 12            # punctured-rm and punctured-weighted-rm: 4096 points
MAX_WEIGHT = 16
MAX_Q = 4             # ccz-frame: m = 12, 4096 columns
MIN_L, MAX_L = 4, 12  # four-block: up to 4 * 4096 coordinates


def _is_int(value) -> bool:
    return type(value) is int


def _int_list(value) -> bool:
    return isinstance(value, list) and all(type(v) is int for v in value)


def _rm_dim(m, r):
    return sum(comb(m, d) for d in range(r + 1))


def _weighted_delta(m, weights, cutoff):
    return [a for a in range(1 << m)
            if sum(weights[i] for i in range(m) if a >> i & 1) <= cutoff]


def problems(construction) -> list[str]:
    """What is wrong with the SHAPE of a construction; empty if nothing."""
    if not isinstance(construction, dict):
        return [f"the construction is a {type(construction).__name__}, not "
                f"an object"]
    family = construction.get("family")
    if family not in FAMILIES:
        return [f"unknown construction family {family!r}; this module knows "
                f"{', '.join(FAMILIES)}"]
    fields = FAMILIES[family]
    found = [name for name in construction if name != "family"]
    if sorted(found) != sorted(fields):
        return [f"a {family} construction has the fields "
                f"{', '.join(fields)}, not {', '.join(sorted(found))}"]
    for name in ("k", "N"):
        if not _is_int(construction[name]) or construction[name] < 1:
            return [f"{name} must be a positive whole number, not "
                    f"{construction[name]!r}"]
    return {"punctured-rm": _problems_rm,
            "punctured-weighted-rm": _problems_weighted,
            "ccz-frame": _problems_ccz,
            "four-block": _problems_four_block}[family](construction)


def _puncture_problems(P, n_points, n_rows, ordered):
    if not _int_list(P):
        return ["punctures must be a list of whole numbers"]
    if not 1 <= len(P) <= n_rows:
        return [f"need 1 to {n_rows} punctures (the parent's dimension), "
                f"not {len(P)}"]
    bad = [p for p in P if not 0 <= p < n_points]
    if bad:
        return [f"puncture {bad[0]} is outside 0..{n_points - 1}"]
    if ordered and any(a >= b for a, b in zip(P, P[1:])):
        return ["punctures must be strictly increasing"]
    if len(set(P)) != len(P):
        return ["a point is punctured twice"]
    return []


def _k_N_problems(c, k, N):
    return [f"{name}={c[name]} but the other fields give {name}={want}"
            for name, want in (("k", k), ("N", N)) if c[name] != want]


def _problems_rm(c):
    m, r = c["m"], c["r"]
    if not _is_int(m) or not 1 <= m <= MAX_M:
        return [f"m must be a whole number from 1 to {MAX_M}, not {m!r}"]
    if not _is_int(r) or r < 0 or 3 * r >= m:
        return [f"r must be a whole number with 0 <= 3r < m = {m}, "
                f"not {r!r}"]
    N = _rm_dim(m, r)
    out = _puncture_problems(c["punctures"], 1 << m, N, ordered=True)
    return out or _k_N_problems(c, len(c["punctures"]), N)


def _problems_weighted(c):
    m, w, cut = c["m"], c["weights"], c["cutoff"]
    if not _is_int(m) or not 1 <= m <= MAX_M:
        return [f"m must be a whole number from 1 to {MAX_M}, not {m!r}"]
    if not _int_list(w) or len(w) != m \
            or not all(1 <= x <= MAX_WEIGHT for x in w):
        return [f"weights must be a list of {m} whole numbers from 1 to "
                f"{MAX_WEIGHT}, not {w!r}"]
    if not _is_int(cut) or not 0 <= cut <= sum(w):
        return [f"cutoff must be a whole number from 0 to {sum(w)}, "
                f"not {cut!r}"]
    N = len(_weighted_delta(m, w, cut))
    out = _puncture_problems(c["punctures"], 1 << m, N, ordered=False)
    return out or _k_N_problems(c, len(c["punctures"]), N)


def _problems_ccz(c):
    q, triples = c["q"], c["triples"]
    if not _is_int(q) or not 1 <= q <= MAX_Q:
        return [f"q must be a whole number from 1 to {MAX_Q}, not {q!r}"]
    m = 3 * q
    if not isinstance(triples, list) or not triples:
        return ["triples must be a non-empty list"]
    if len(triples) > comb(m, q) // 3:
        return [f"{len(triples)} triples need more than the C({m},{q}) "
                f"distinct {q}-sets there are"]
    seen = set()
    for i, t in enumerate(triples):
        if not isinstance(t, list) or len(t) != 3:
            return [f"triple {i} is not a list of three sets"]
        for s in t:
            if not _int_list(s) or len(s) != q \
                    or any(not 0 <= v < m for v in s) \
                    or any(a >= b for a, b in zip(s, s[1:])):
                return [f"set {s!r} of triple {i} is not a strictly "
                        f"increasing list of {q} coordinates in 0..{m - 1}"]
            if tuple(s) in seen:
                return [f"set {s!r} occurs twice"]
            seen.add(tuple(s))
    k = 3 * len(triples)
    return _k_N_problems(c, k, k + sum(comb(m, d) for d in range(q)))


def _flat_points(fl):
    o, dirs = fl[0], fl[1:]
    pts = set()
    for mask in range(16):
        x = o
        for i in range(4):
            if mask >> i & 1:
                x ^= dirs[i]
        pts.add(x)
    return pts


def _problems_four_block(c):
    L, flats = c["L"], c["removed_flats"]
    if not _is_int(L) or not MIN_L <= L <= MAX_L:
        return [f"L must be a whole number from {MIN_L} to {MAX_L}, "
                f"not {L!r}"]
    if not isinstance(flats, list) or len(flats) > (1 << (L - 4)) - 1:
        return [f"removed_flats must be a list of fewer than {1 << (L - 4)} "
                f"flats"]
    gone = set()
    for fl in flats:
        if not _int_list(fl) or len(fl) != 5 \
                or any(not 0 <= v < 1 << L for v in fl):
            return [f"removed flat {fl!r} is not [offset, d1, d2, d3, d4] "
                    f"with entries in 0..{(1 << L) - 1}"]
        pts = _flat_points(fl)
        if len(pts) != 16:
            return [f"removed flat {fl!r} is not 4-dimensional"]
        if pts & gone:
            return [f"removed flat {fl!r} meets an earlier one"]
        gone |= pts
    M = (1 << L) - len(gone)
    rows, _M = _four_block_parent(L, flats)
    out = _puncture_problems(c["punctures"], 4 * M, len(rows), ordered=False)
    return out or _k_N_problems(c, len(c["punctures"]), len(rows))


# ------------------------------------------------------------------ builders
def columns(construction) -> list[list[int]]:
    """The circuit, in the order `constructions.py` fixes."""
    return sorted(native_columns(construction))


def native_columns(construction) -> list[list[int]]:
    """The circuit in the research's order: one column per kept coordinate,
    in increasing coordinate order, each column sorted ascending."""
    wrong = problems(construction)
    if wrong:
        raise ValueError("; ".join(wrong))
    c = construction
    family = c["family"]
    if family == "punctured-rm":
        rows = _monomial_rows(c["m"], [a for d in range(c["r"] + 1)
                                       for a in _subsets(c["m"], d)])
        wires = _swap_reduce(rows, c["punctures"])
        return _transpose(wires, 1 << c["m"], set(c["punctures"]))
    if family == "punctured-weighted-rm":
        rows = _monomial_rows(c["m"], _weighted_delta(c["m"], c["weights"],
                                                      c["cutoff"]))
        wires = _first_free_reduce(rows, c["punctures"])
        return _transpose(wires, 1 << c["m"], set(c["punctures"]))
    if family == "ccz-frame":
        q = c["q"]
        m = 3 * q
        outs = [sum(1 << i for i in s) for t in c["triples"] for s in t]
        checks = [a for d in range(q) for a in _subsets(m, d)]
        return _transpose(_monomial_rows(m, outs + checks), 1 << m, set())
    if family == "four-block":
        rows, M = _four_block_parent(c["L"], c["removed_flats"])
        wires = _first_free_reduce(rows, c["punctures"])
        return _transpose(wires, 4 * M, set(c["punctures"]))
    raise AssertionError(family)                   # `problems` lets no other


def _subsets(m, d):
    """The d-subsets of range(m) as bitmasks, in itertools.combinations order."""
    return [sum(1 << i for i in s) for s in combinations(range(m), d)]


def _monomial_rows(m, masks):
    """Row of monomial a: bit x set iff x & a == a, for every point x."""
    full = (1 << (1 << m)) - 1
    coord = []
    for i in range(m):
        v = 0
        for x in range(1 << m):
            if x >> i & 1:
                v |= 1 << x
        coord.append(v)
    rows = []
    for a in masks:
        v = full
        for i in range(m):
            if a >> i & 1:
                v &= coord[i]
        rows.append(v)
    return rows


def _swap_reduce(rows, P):
    rows = list(rows)
    N = len(rows)
    for j, p in enumerate(P):
        piv = next((i for i in range(j, N) if rows[i] >> p & 1), None)
        if piv is None:
            raise ValueError(f"puncture {p} (index {j}) is dependent on the "
                             f"earlier ones")
        rows[j], rows[piv] = rows[piv], rows[j]
        for i in range(N):
            if i != j and rows[i] >> p & 1:
                rows[i] ^= rows[j]
    return rows


def _first_free_reduce(rows, P):
    rows = list(rows)
    taken = [False] * len(rows)
    chosen = []
    for p in P:
        piv = next((i for i, r in enumerate(rows)
                    if not taken[i] and r >> p & 1), None)
        if piv is None:
            raise ValueError(f"puncture {p} is dependent on the earlier ones")
        taken[piv] = True
        chosen.append(piv)
        for i in range(len(rows)):
            if i != piv and rows[i] >> p & 1:
                rows[i] ^= rows[piv]
    return [rows[i] for i in chosen] + [r for i, r in enumerate(rows)
                                        if not taken[i]]


def _transpose(wire_rows, n_coords, removed):
    """Column per kept coordinate (increasing), listing the wires set there."""
    cols = [[] for _ in range(n_coords)]
    for w, r in enumerate(wire_rows):
        x = r
        while x:
            low = x & -x
            cols[low.bit_length() - 1].append(w)
            x ^= low
    return [col for j, col in enumerate(cols) if j not in removed]


def _four_block_parent(L, flats):
    gone = set()
    for fl in flats:
        gone |= _flat_points(fl)
    pts = [p for p in range(1 << L) if p not in gone]
    M = len(pts)

    def ev(fn):
        return sum(1 << i for i, p in enumerate(pts) if fn(p))

    lin = [ev(lambda p, i=i: p >> i & 1) for i in range(L)]
    affine = [ev(lambda p: True)] + lin
    quad = affine + [lin[i] & lin[j] for i in range(L)
                     for j in range(i + 1, L)]
    piv = {}                           # pivot -> fully reduced row
    for v in quad:
        for pc, r in piv.items():
            if v >> pc & 1:
                v ^= r
        if v:
            pc = v.bit_length() - 1
            for c in piv:
                if piv[c] >> pc & 1:
                    piv[c] ^= v
            piv[pc] = v
    F = []
    for j in range(M):
        if j in piv:
            continue
        v = 1 << j
        for pc, r in piv.items():
            if r >> j & 1:
                v |= 1 << pc
        F.append(v)
    rows = [f | f << M | f << 2 * M | f << 3 * M for f in F]
    rows += [a << M | a << 3 * M for a in affine]
    rows += [b << 2 * M | b << 3 * M for b in affine]
    return rows, M


# ------------------------------------------------------------------- digests
def canonical_text(cols) -> str:
    """The text ``columns_sha256`` is computed over: compact JSON."""
    return json.dumps(cols, separators=(",", ":"))


def digest(cols) -> str:
    return hashlib.sha256(canonical_text(cols).encode("ascii")).hexdigest()


def sorted_position(native):
    """``pos[i]``: where native column i lands in the sorted order.

    Equal columns keep their native order (a stable sort), so the map is a
    bijection even if two columns coincide.
    """
    order = sorted(range(len(native)), key=lambda i: native[i])
    pos = [0] * len(native)
    for new, old in enumerate(order):
        pos[old] = new
    return pos


# ------------------------------------------------------------- the CCZ frame


def packing_check(construction) -> list[str]:
    """The theorem's hypothesis for a ccz-frame object; empty if it holds.

    The 3c sets must be distinct q-subsets of [m], each designated triple
    must partition [m], and no other three members of the family may
    partition [m].  The last part runs over all C(3c, 3) triples of sets.
    """
    wrong = problems(construction)
    if wrong:
        return wrong
    if construction["family"] != "ccz-frame":
        return [f"packing_check is for ccz-frame, not "
                f"{construction['family']}"]
    q = construction["q"]
    m = 3 * q
    full = (1 << m) - 1
    sets = [sum(1 << i for i in s) for t in construction["triples"]
            for s in t]
    out = []
    if len(set(sets)) != len(sets):
        out.append("the sets are not distinct")
    if any(s.bit_count() != q or s & ~full for s in sets):
        out.append(f"a set is not a {q}-subset of 0..{m - 1}")
    designated = set()
    for i in range(len(construction["triples"])):
        a, b, c = sets[3 * i:3 * i + 3]
        designated.add((3 * i, 3 * i + 1, 3 * i + 2))
        if a | b | c != full or a & b or a & c or b & c:
            out.append(f"designated triple {i} does not partition "
                       f"0..{m - 1}")
    extra = []
    for i, j, l in combinations(range(len(sets)), 3):
        if sets[i] | sets[j] | sets[l] == full and (i, j, l) not in designated:
            extra.append((i, j, l))
    if extra:
        out.append(f"{len(extra)} undesignated triple(s) of sets partition "
                   f"0..{m - 1}, first {extra[0]}")
    return out


def frame_check(columns, k, N, construction) -> list[str]:
    """Whether ``(columns, k, N)`` is the CCZ frame of ``construction``,
    read from the columns alone; empty if it is.

    The checks follow `research/search/parents/code/frame_identity.py`.
    There must be m check rows of weight 2^(m-1), and they must label the
    columns as the 2^m points of F_2^m, coordinate i being the i-th such row
    in wire order.  The check rows must be distinct and be exactly the
    products of at most q-1 coordinate rows.  Output 3i + j must be the
    product of the q coordinate rows in triples[i][j].  The gate that the
    catalogue's `faultcore` recovers must be CCZ on the designated triples and
    nothing else, and so must the literal list of output triples whose sets
    partition the coordinates.
    """
    wrong = problems(construction)
    if wrong:
        return wrong
    if construction["family"] != "ccz-frame":
        return [f"frame_check is for ccz-frame, not "
                f"{construction['family']}"]
    q = construction["q"]
    m = 3 * q
    n = len(columns)
    out = []
    if (k, N) != (construction["k"], construction["N"]):
        out.append(f"k={k}, N={N} but the construction has "
                   f"k={construction['k']}, N={construction['N']}")
        return out
    if n != 1 << m:
        return [f"{n} columns, not 2^{m}"]
    rows = [0] * N
    for j, col in enumerate(columns):
        for w in col:
            if type(w) is not int or not 0 <= w < N:
                return [f"wire label {w!r} in column {j} is outside "
                        f"0..{N - 1}"]
            rows[w] |= 1 << j
    full = (1 << n) - 1
    coord = [w for w in range(k, N) if rows[w].bit_count() == 1 << (m - 1)]
    if len(coord) != m:
        return [f"{len(coord)} check rows have weight 2^{m - 1}, not {m}"]
    labels = [sum(1 << i for i, w in enumerate(coord) if rows[w] >> j & 1)
              for j in range(n)]
    if sorted(labels) != list(range(n)):
        out.append("the coordinate rows do not label the columns as the "
                   "points of F_2^m")

    def product(S):
        v = full
        for i in S:
            v &= rows[coord[i]]
        return v

    low = {product(S): S for d in range(q) for S in combinations(range(m), d)}
    checks = rows[k:N]
    if len(set(checks)) != len(checks):
        out.append("two check rows are equal")
    if set(checks) != set(low):
        out.append(f"the check rows are not exactly the products of at most "
                   f"{q - 1} coordinate rows")
    top = {product(S): S for S in combinations(range(m), q)}
    outsets = [top.get(rows[i]) for i in range(k)]
    if any(s is None for s in outsets):
        out.append(f"an output row is not a product of {q} coordinate rows")
    want_sets = [tuple(s) for t in construction["triples"] for s in t]
    if outsets != want_sets:
        out.append("the output sets differ from the construction's triples")
    designated = frozenset(frozenset((3 * i, 3 * i + 1, 3 * i + 2))
                           for i in range(k // 3))
    import faultcore as FC                     # the catalogue's own read-off
    gate = FC.recover_gate(rows, k)
    if gate != designated:
        out.append("the recovered gate is not CCZ on the designated triples")
    if all(s is not None for s in outsets):
        masks = [sum(1 << i for i in s) for s in outsets]
        allm = (1 << m) - 1
        literal = frozenset(frozenset(t) for t in combinations(range(k), 3)
                            if masks[t[0]] | masks[t[1]] | masks[t[2]] == allm)
        if literal != designated:
            out.append("the output triples whose sets partition the "
                       "coordinates are not the designated ones")
    return out
