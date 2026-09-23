#!/usr/bin/env python3
"""The census engine's S_k classification of one marked geometry, without the
repeated work: `factorylib.parent.classify_gates` with two memoisations.

WHAT THE ENGINE DOES.  For every compatible subspace it walks the full GL(k,2)
orbit of the subspace's gate and, for EVERY member of that orbit, computes the
k!-permutation S_k canonical form, rebuilds the witness columns and verifies
them.  Two facts make most of that redundant, and both are pure bookkeeping --
the set of recorded (k, S_k class) keys is unchanged:

1.  Two subspaces whose gates lie in the same GL(k,2) orbit yield the SAME
    set of S_k classes (the orbit is the same set of gates), and the engine
    records a class only the first time it is seen (`records.setdefault`).  So
    once an orbit has been processed, every later subspace whose gate is a
    member of it contributes nothing and can be skipped.  On class 2978 origin
    60 the engine visits 59 million (subspace, member) pairs; the distinct
    members number about a million.
2.  Within an orbit, the S_k classes are the connected components under the
    k(k-1)/2 transpositions (a permutation matrix is an element of GL(k,2), so
    every transposition image is in the orbit).  One breadth-first pass finds
    the components; the k! canonical form is then computed once per COMPONENT
    rather than once per member.  At k = 7 that is 5040 permutations per class
    instead of per each of 330,708 members.

The witness of a class is one member's frame, permuted into the canonical
labelling, with its columns re-verified exactly as the engine does
(`verify_columns`, distance to weight max(4, d-1)).  Which member becomes the
witness can differ from the engine's choice; the class does not.

Output: the same file shape as ``cli.py census --class-index C --origin O``
(a restricted run), so ``build_sk_catalog.py`` consumes it unchanged; the file
says in ``engine_note`` how it was produced.

Usage: fast_census.py CLASS ORIGIN --output FILE
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "classification", "rank7_census"))
from factorylib.parent import (Parent, _permute_frame, compatible_subspaces,   # noqa: E402
                               covered_width, gate_key, gate_name, gl_orbit,
                                sk_canonical, transform_frame, verify_columns)
from rank7 import DEFAULT_DATA, WINDOW_NMAX, data_digest, iter_parents          # noqa: E402


def sk_components(k, members):
    """Partition a GL(k,2) orbit (an iterable of gates) into S_k classes by
    breadth-first search over transpositions.  Returns {member: representative}."""
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


def classify_fast(parent, kmax=7):
    records = {}
    done = set()              # every (k, member gate) of every orbit already processed
    subspaces = 0
    n_orbits = 0
    for basis in compatible_subspaces(parent, kmax=kmax):
        if not basis:
            continue
        subspaces += 1
        k = len(basis)
        gate = parent.gate(basis)
        # Keyed by (k, gate): a gate touching only four wires can be a member
        # of a k = 4 orbit AND the start of a k = 5 orbit whose other members
        # are active five-wire gates.  Keying by gate alone lost exactly those.
        if (k, gate) in done:
            continue
        orbit, complete = gl_orbit(k, gate, None)
        assert complete
        n_orbits += 1
        rep_of = sk_components(k, orbit)
        for rep in set(rep_of.values()):
            if covered_width(rep) != k:          # active_only: an idle output is not a class at this width
                continue
            canonical, permutation = sk_canonical(k, rep)
            key = (k, canonical)
            if key in records:
                continue
            frame = _permute_frame(transform_frame(basis, orbit[rep]), permutation)
            canonical_gate = frozenset(frozenset(q) for q in canonical)
            columns = parent.columns(frame)
            parity_ok, distance = verify_columns(columns, k, k + parent.ambient_rank,
                                                 canonical_gate, max(4, parent.distance - 1))
            if not parity_ok or (isinstance(distance, int) and distance < parent.distance):
                raise AssertionError("S_k witness failed independent verification")
            records[key] = {
                "k": k,
                "gate": gate_name(canonical_gate),
                "canonical_key": [list(q) for q in canonical],
                "dedup": "S_k",
                "orbit_complete": True,
                "distance": distance,
                "wants": [list(q) for q in gate_key(canonical_gate)],
                "columns": columns,
            }
        done.update((k, g) for g in orbit)
    ordered = sorted(records.values(), key=lambda r: (r["k"], r["canonical_key"]))
    return dict(n=parent.n, check_rank=parent.check_rank, kappa=parent.kappa, dedup="symmetric",
                complete=True, subspaces_visited=subspaces, n_gates=len(ordered), gates=ordered,
                distinct_orbits=n_orbits, distinct_members=len(done))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("class_index", type=int)
    ap.add_argument("origin", type=int)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    t0 = time.time()
    (orbit, origin, points), = list(iter_parents(mode="all", nmax=WINDOW_NMAX,
                                                 class_indices=[a.class_index], origins=[a.origin]))
    parent = Parent.from_points(points, ambient_rank=7, distance=3)
    gates = classify_fast(parent, kmax=7)
    geometry = {
        "class_index": orbit.index, "origin": origin, "weight": orbit.weight,
        "n": parent.n, "rank": parent.check_rank, "kappa": parent.kappa,
        "quadric_degeneracy": parent.quadric_degeneracy,
        "gate_search_complete": True, "n_gates": gates["n_gates"],
        "subspaces_visited": gates["subspaces_visited"],
        "distinct_orbits": gates["distinct_orbits"], "distinct_members": gates["distinct_members"],
    }
    factories = [{"n": parent.n, "r": parent.check_rank, "N": parent.check_rank + g["k"], "distance": 3,
                  "class_index": orbit.index, "origin": origin, **g} for g in gates["gates"]]
    out = {
        "scope": (f"RESTRICTED distance-3 check-parent-first run (mode=all, kmax=7, "
                  f"class_indices=[{a.class_index}], origins=[{a.origin}]); a subset of the r<=7, "
                  f"n<=44 window, not a certificate for it"),
        "engine_note": ("factorylib.parent.classify_gates with orbit memoisation and per-S_k-class "
                        "canonical forms (fast_census.py): identical class set, witnesses may differ"),
        "data_name": os.path.basename(str(DEFAULT_DATA)), "data_sha256": data_digest(DEFAULT_DATA),
        "mode": "all", "dedup": "symmetric", "kmax": 7,
        "restrictions": {"mode": "all", "nmax": WINDOW_NMAX, "kmax": 7,
                         "class_indices": [a.class_index], "origins": [a.origin], "max_parents": None},
        "covers_full_window": False, "geometries_expected": None,
        "node_budget_per_parent": 0, "orbit_budget_per_gate": 0,
        "complete": False, "geometries": [geometry], "factories": factories,
        "processed_parents": 1, "rank_counts": {str(parent.check_rank): 1},
        "stopped_by_max_parents": False, "untruncated": True,
        "incomplete_reasons": ["the sweep was restricted (see `restrictions`), so it covers a subset "
                               "of the r<=7, n<=44 window"],
        "seconds": round(time.time() - t0, 1),
    }
    tmp = a.output + ".tmp"
    with open(tmp, "w") as f:
        json.dump(out, f, indent=1)
    os.replace(tmp, a.output)
    print(f"wrote {a.output}: {gates['n_gates']} gates from {gates['subspaces_visited']} subspaces, "
          f"{gates['distinct_orbits']} distinct orbits ({gates['distinct_members']:,} members), "
          f"{out['seconds']}s")


if __name__ == "__main__":
    main()
