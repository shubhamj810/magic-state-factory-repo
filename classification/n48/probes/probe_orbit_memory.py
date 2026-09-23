"""Probe: per-parent orbit sizes and RSS for the reps of one length48 shard.

Runs single-process with the orbit memo OFF, a per-parent wall-clock alarm
and an RSS guard, printing every orbit walk above --big members.  Used to
diagnose the 2026-09-06 memory blow-up (both workers > 16 GB on shard 298).
"""
import argparse, resource, signal, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import classify48                       # installs memo; we switch it off
from sources48 import reps_of, marking_of
from factorylib.parent import Parent
import landscape

classify48.enable_orbit_memo(False)
_raw = landscape.gl_orbit
BIG = 50_000
walks = []
def _spy(k, gate, limit=None):
    t = time.time(); out = _raw(k, gate, limit)
    n = len(out[0]); walks.append((k, n, time.time() - t))
    if n >= BIG:
        print(f"      orbit k={k} size={n} ({time.time()-t:.1f}s)", flush=True)
    return out
landscape.gl_orbit = _spy

def rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20

class Alarm(Exception): pass
def _alarm(*_): raise Alarm()
signal.signal(signal.SIGALRM, _alarm)

ap = argparse.ArgumentParser()
ap.add_argument("--shard", type=int, required=True)
ap.add_argument("--origins", type=int, default=64, help="origins per rep to try (0 = all)")
ap.add_argument("--per-parent", type=int, default=600, help="alarm seconds per parent")
ap.add_argument("--rss-cap", type=float, default=3000, help="MB; stop when max RSS exceeds this")
ap.add_argument("--big", type=int, default=BIG)
ap.add_argument("--first", type=int, default=0, help="first rep index in the shard")
ap.add_argument("--last", type=int, default=None, help="last rep index (exclusive)")
a = ap.parse_args(); BIG = a.big
reps = reps_of("length48"); shards = classify48.plan_shards(reps)
shard = shards[a.shard - 1]
print(f"shard {a.shard}: {len(shard)} reps, m={shard[0].m}..{shard[-1].m}", flush=True)
for rep in shard[a.first:a.last]:
    origins = rep.origins if a.origins == 0 else rep.origins[:a.origins]
    for origin in origins:
        n, amb, pts = marking_of(rep.m, frozenset(rep.support), origin)
        parent = Parent.from_points(pts, ambient_rank=amb, distance=3)
        walks.clear(); t = time.time(); signal.alarm(a.per_parent)
        try:
            out = landscape.classify_landscape(parent, kmax=None); status = f"mu={out['mu']} gates={out['n_gates']}"
        except Alarm:
            status = "ALARM (unfinished)"
        finally:
            signal.alarm(0)
        big = max((w[1] for w in walks), default=0)
        print(f"{rep.id} origin={origin} n={n} kappa={parent.kappa} {status} {time.time()-t:.1f}s "
              f"walks={len(walks)} largest={big} members={sum(w[1] for w in walks)} maxrss={rss_mb():.0f}MB", flush=True)
        if rss_mb() > a.rss_cap:
            print("RSS cap hit; stopping"); sys.exit(2)
