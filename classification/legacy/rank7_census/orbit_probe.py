#!/usr/bin/env python3
"""How much work is left in a geometry: the GL(k,2) orbit sizes of its frames.

Walks the same compatible subspaces the census engine walks and, for each,
the engine's own GL(k,2) orbit (`factorylib.parent.gl_orbit`) -- but WITHOUT
the per-member canonical form, column rebuild and distance verification that
make `classify_gates` cost milliseconds per member.  Orbits are memoised by
member gate, so a GL class shared by many subspaces is walked once.

Reports, per k: subspaces, distinct orbits, total members (= the number of
(subspace, member) verifications the engine has to do), and orbits that hit
the cap.  Run on a FINISHED geometry with a known wall time to calibrate the
milliseconds per member; then on a pending one to estimate.

Usage: orbit_probe.py CLASS ORIGIN [--cap 3000000]
"""
import json
import sys
import time
from collections import Counter, defaultdict

import os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.path.insert(0, HERE)
from factorylib.parent import Parent, compatible_subspaces, gl_orbit   # noqa: E402
from rank7 import iter_parents                                          # noqa: E402

cidx, origin = int(sys.argv[1]), int(sys.argv[2])
cap = int(sys.argv[sys.argv.index("--cap") + 1]) if "--cap" in sys.argv else 3_000_000

(orbit, o, points), = list(iter_parents(mode="all", nmax=44, class_indices=[cidx], origins=[origin]))
parent = Parent.from_points(points, ambient_rank=7, distance=3)
print(f"class {cidx} origin {origin}: n={len(points)} kappa={getattr(parent, 'kappa', '?')}", flush=True)

size_of = {}          # member gate -> orbit size (or -1 if capped)
subspaces = Counter(); members = Counter(); capped = Counter(); orbits = Counter()
walked = 0
t0 = time.time()
for i, basis in enumerate(compatible_subspaces(parent, kmax=7), 1):
    if not basis:
        continue
    k = len(basis)
    gate = parent.gate(basis)
    subspaces[k] += 1
    if gate not in size_of:
        orb, complete = gl_orbit(k, gate, cap)
        size = len(orb) if complete else -1
        for g in orb:
            size_of[g] = size
        orbits[k] += 1
        walked += 1
    s = size_of[gate]
    if s < 0:
        capped[k] += 1
        members[k] += cap
    else:
        members[k] += s
    if i % 50000 == 0:
        print(f"  {i:,} subspaces, {walked} orbits walked, {sum(members.values()):,} members so far, "
              f"{time.time() - t0:.0f}s", flush=True)
out = dict(class_index=cidx, origin=origin, n=len(points), seconds=round(time.time() - t0, 1),
           subspaces=dict(subspaces), distinct_orbits=dict(orbits), members=dict(members),
           capped_subspaces=dict(capped), cap=cap, total_members=sum(members.values()))
print(json.dumps(out, indent=1), flush=True)
