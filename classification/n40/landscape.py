#!/usr/bin/env python3
"""THE CLASSIFIER, with the error coefficient: every S_k class of one check
parent, and for each class the minimum leading fault coefficient over every
output subspace that realises it, with a witness attaining that minimum.

WHY THE COEFFICIENT
-------------------
A distance-3 factory detects every fault on one or two of its n injections.
What reaches the output first is a set of three injections that (a) passes
every check -- its three check syndromes XOR to zero -- and (b) acts on the
outputs.  Under independent injection errors of rate p the logical error is

    P_fail ~ a3 * p^3 + O(p^4),   a3 = #{ X, |X| = 3 : X undetected and harmful }.

Two circuits with the same (n, k, gate) can have very different a3: more
independent checks mean fewer undetected triples.  A catalogue that keeps one
witness per class hides that.  This module records, per class, the minimum
a3 over everything the parent realises, so a catalogue can publish the best
circuit per (class, check rank).

TWO FACTS THAT MAKE IT CHEAP
----------------------------
1.  Whether an undetected triple X is harmful depends only on the output
    SUBSPACE, not on the basis chosen inside it: X is harmless iff every
    output row has even overlap with X, and that property is closed under
    XOR.  (It also does not depend on the coset representative of a row:
    an undetected X has even overlap with every check row.)  So a3 is one
    number per compatible subspace, shared by every gate the subspace's
    GL(k,2) output bases realise.
2.  The overlap parity of a quotient element with a fixed X is linear in the
    element's coordinates, so one bitmask per quotient basis vector (which
    triples it hits) gives every element's mask by XOR, and a subspace's
    harmful set is the OR of its basis vectors' masks.  a3 is a popcount.

THE ALGORITHM (the orbit-memoised S_k classifier of ``../rank7_census/
fast_census.py``, with the coefficient threaded through)
  * for every compatible subspace (``factorylib.parent.compatible_subspaces``,
    no cap unless asked): compute a3; if its gate's GL(k,2) orbit has not been
    walked, walk it once and split it into S_k classes; for every class the
    orbit realises, record this subspace if its a3 is the smallest so far;
  * afterwards, for every class, rebuild the witness frame on its best
    subspace -- relabelled into the canonical S_k frame -- verify its columns
    independently (``verify_columns``: gate parities, distance) and recount
    a3 from the columns by a second, direct method.
The set of (k, S_k class) keys is exactly the one the plain classifier
records; only the choice of witness changes.  Nothing has a budget.
"""
from __future__ import annotations

import sys
from collections import defaultdict, deque
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from factorylib.parent import (Parent, _matmul_rows, _permute_frame,          # noqa: E402
                               compatible_subspaces, covered_width, gate_key,
                               gate_name, gl_orbit, sk_canonical, transform_frame,
                               verify_columns)


# ------------------------------------------------------------ F_2 matrices
def inverse_rows(matrix, k):
    """Inverse of a k x k F_2 matrix given as row ints (bit j of row i = M[i][j])."""
    rows = [(int(r), 1 << i) for i, r in enumerate(matrix)]     # [M | I]
    for col in range(k):
        pivot = next((i for i in range(col, k) if (rows[i][0] >> col) & 1), None)
        if pivot is None:
            raise ValueError("singular matrix")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        for i in range(k):
            if i != col and (rows[i][0] >> col) & 1:
                rows[i] = (rows[i][0] ^ rows[col][0], rows[i][1] ^ rows[col][1])
    return tuple(inv for _m, inv in rows)


# ---------------------------------------------------------- the coefficient
def undetected_triples(parent):
    """Column masks of every 3-set of injections whose check syndromes XOR to
    zero.  A code invariant of the parent: the pool a3 is drawn from."""
    pts = parent.points
    where = {p: j for j, p in enumerate(pts)}
    masks = []
    for a, b in combinations(range(len(pts)), 2):
        c = where.get(pts[a] ^ pts[b])
        if c is not None and c > b:
            masks.append((1 << a) | (1 << b) | (1 << c))
    return masks


def harm_masks(parent, triples):
    """``hv[v]`` for every quotient coordinate int v: bit t set iff quotient
    element v has odd overlap with triple t.  Linear in v, so built by XOR."""
    basis_masks = []
    for row in parent.quotient_basis:
        h = 0
        for t, X in enumerate(triples):
            if (row & X).bit_count() & 1:
                h |= 1 << t
        basis_masks.append(h)
    hv = [0] * (1 << parent.kappa)
    for v in range(1, 1 << parent.kappa):
        low = v & -v
        hv[v] = hv[v ^ low] ^ basis_masks[low.bit_length() - 1]
    return hv


def a3_of_columns(columns, k, N):
    """Direct recount from explicit columns: undetected AND harmful 3-sets."""
    rows = [0] * N
    for j, col in enumerate(columns):
        for i in col:
            rows[i] |= 1 << j
    n = len(columns)
    syn = [sum(((rows[b] >> j) & 1) << (b - k) for b in range(k, N)) for j in range(n)]
    osyn = [sum(((rows[b] >> j) & 1) << b for b in range(k)) for j in range(n)]
    where = defaultdict(list)
    for j, s in enumerate(syn):
        where[s].append(j)
    count = 0
    for a, b in combinations(range(n), 2):
        for c in where.get(syn[a] ^ syn[b], ()):
            if c > b and (osyn[a] ^ osyn[b] ^ osyn[c]):
                count += 1
    return count


# ------------------------------------------------------------ the classifier
def sk_components(k, members):
    """Partition a GL(k,2) orbit into S_k classes by BFS over transpositions."""
    members = set(members)
    swaps = [(i, j) for i in range(k) for j in range(i + 1, k)]
    rep_of = {}
    for start in members:
        if start in rep_of:
            continue
        rep_of[start] = start
        queue = deque([start])
        while queue:
            g = queue.popleft()
            for i, j in swaps:
                image = frozenset(frozenset(j if q == i else i if q == j else q for q in mono) for mono in g)
                if image not in rep_of:
                    if image not in members:
                        raise AssertionError("a transposition image left the orbit: the orbit was not closed")
                    rep_of[image] = start
                    queue.append(image)
    return rep_of


def _classes_of_orbit(k, orbit):
    """{S_k canonical key: (member gate, permutation into the canonical frame)}
    for the active classes of a walked orbit."""
    rep_of = sk_components(k, orbit)
    out = {}
    for rep in set(rep_of.values()):
        if covered_width(rep) != k:          # an idle output is not a class at this width
            continue
        canonical, permutation = sk_canonical(k, rep)
        out[canonical] = (rep, permutation)
    return out


def classify_landscape(parent, kmax=None):
    """Every (k, S_k class) of ``parent`` with the witness of minimum a3.

    Returns the class records plus bookkeeping: ``mu`` (widest compatible
    subspace met), ``t3`` (undetected triples of the parent), counts.
    """
    triples = undetected_triples(parent)
    hv = harm_masks(parent, triples)
    orbit_of = {}            # (k, member gate) -> orbit id
    orbit_start = {}         # orbit id -> start gate
    orbit_keys = {}          # orbit id -> tuple of canonical keys (active classes)
    best = {}                # (k, canonical) -> [a3, basis, n_subspaces, a3_max]
    subspaces = 0
    members = 0
    mu = 0
    for basis in compatible_subspaces(parent, kmax=kmax):
        if not basis:
            continue
        subspaces += 1
        k = len(basis)
        mu = max(mu, k)
        gate = parent.gate(basis)
        harmful = 0
        for v in basis:
            harmful |= hv[v]
        a3 = harmful.bit_count()
        oid = orbit_of.get((k, gate))
        if oid is None:
            orbit, complete = gl_orbit(k, gate, None)
            if not complete:
                raise AssertionError("an uncapped GL orbit reported itself incomplete")
            oid = len(orbit_start)
            orbit_start[oid] = gate
            orbit_keys[oid] = tuple(_classes_of_orbit(k, orbit))
            for g in orbit:
                orbit_of[(k, g)] = oid
            members += len(orbit)
        for canonical in orbit_keys[oid]:
            key = (k, canonical)
            b = best.get(key)
            if b is None:
                best[key] = [a3, basis, 1, a3]
            else:
                b[2] += 1
                if a3 > b[3]:
                    b[3] = a3
                if a3 < b[0]:
                    b[0], b[1] = a3, basis

    # Witnesses: one re-walk per orbit that holds a best subspace; the frame
    # on the best basis (gate g = T(g0, Mg)) that shows class member rep
    # (= T(g0, Mr)) is transform_frame(basis, Mr . Mg^-1), since
    # T(T(x, A), B) = T(x, B . A) in gl_orbit's convention.
    needed = defaultdict(list)
    for key, (a3, basis, cnt, a3max) in best.items():
        needed[orbit_of[(key[0], parent.gate(basis))]].append(key)
    records = {}
    for oid, keys in needed.items():
        k = keys[0][0]
        orbit, _ = gl_orbit(k, orbit_start[oid], None)
        classes = _classes_of_orbit(k, orbit)
        for key in keys:
            a3, basis, cnt, a3max = best[key]
            rep, permutation = classes[key[1]]
            matrix = _matmul_rows(orbit[rep], inverse_rows(orbit[parent.gate(basis)], k))
            frame = _permute_frame(transform_frame(basis, matrix), permutation)
            canonical_gate = frozenset(frozenset(q) for q in key[1])
            columns = parent.columns(frame)
            N = k + parent.ambient_rank
            parity_ok, distance = verify_columns(columns, k, N, canonical_gate, max(4, parent.distance - 1))
            if not parity_ok or (isinstance(distance, int) and distance < parent.distance):
                raise AssertionError("S_k witness failed independent verification")
            recount = a3_of_columns(columns, k, N)
            if recount != a3:
                raise AssertionError(f"a3 recount from columns {recount} != subspace value {a3}")
            records[key] = {
                "k": k,
                "gate": gate_name(canonical_gate),
                "canonical_key": [list(q) for q in key[1]],
                "distance": distance,
                "wants": [list(q) for q in gate_key(canonical_gate)],
                "a3": a3,
                "a3_max": a3max,
                "n_subspaces": cnt,
                "columns": columns,
            }
    ordered = sorted(records.values(), key=lambda r: (r["k"], r["canonical_key"]))
    return dict(complete=True, mu=mu, t3=len(triples), subspaces_visited=subspaces,
                n_gates=len(ordered), gates=ordered, distinct_orbits=len(orbit_start),
                distinct_members=members)


__all__ = ["Parent", "classify_landscape", "a3_of_columns", "undetected_triples", "inverse_rows"]
