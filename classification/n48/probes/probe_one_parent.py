"""Probe one parent (rep, origin): walk its orbits with progress and a member cap."""
import argparse, resource, sys, time
from collections import deque
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import classify48
from sources48 import reps_of, marking_of
from factorylib import parent as P
from factorylib.parent import Parent
import landscape
classify48.enable_orbit_memo(False)

ap = argparse.ArgumentParser()
ap.add_argument("--rep", required=True); ap.add_argument("--origin", type=int, required=True)
ap.add_argument("--cap", type=int, default=2_000_000); ap.add_argument("--source", default="length48")
a = ap.parse_args()

def gl_orbit_capped(k, wants, limit=None):
    identity = tuple(1 << i for i in range(k))
    seen = {wants: identity}; queue = deque([wants]); gens = P._gl_generators(k); t = time.time()
    while queue:
        cur = queue.popleft(); M = seen[cur]
        for g in gens:
            im = P.transform_gate(k, cur, g)
            if im in seen: continue
            seen[im] = P._matmul_rows(g, M); queue.append(im)
            if len(seen) % 200_000 == 0:
                print(f"    k={k} walk at {len(seen)} members, {time.time()-t:.0f}s, "
                      f"maxrss {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/2**20:.0f}MB", flush=True)
            if len(seen) >= a.cap:
                print(f"    k={k} CAP {a.cap} hit for gate with {len(wants)} monomials, degrees "
                      f"{sorted(set(len(q) for q in wants))}; wants={sorted(tuple(sorted(q)) for q in wants)}", flush=True)
                raise SystemExit(3)
    print(f"    k={k} orbit size {len(seen)} ({time.time()-t:.1f}s)", flush=True)
    return seen, True
landscape.gl_orbit = gl_orbit_capped

rep = next(r for r in reps_of(a.source) if r.id == a.rep)
n, amb, pts = marking_of(rep.m, frozenset(rep.support), a.origin)
parent = Parent.from_points(pts, ambient_rank=amb, distance=3)
print(f"{rep.id} origin={a.origin}: n={n} ambient={amb} check_rank={parent.check_rank} kappa={parent.kappa}", flush=True)
t = time.time(); out = landscape.classify_landscape(parent, kmax=None)
print(f"done mu={out['mu']} gates={out['n_gates']} {time.time()-t:.1f}s")
