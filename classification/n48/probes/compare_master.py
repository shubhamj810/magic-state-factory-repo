"""Aggregate the length48 shards swept so far (n = 47/48, rank >= 8) and
compare with the master catalogue rows at n = 47/48.  Read-only probe."""
import gzip, json, glob, sys
from collections import defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
best = {}    # (n, k, key) -> best factory (min a3, then min N)
for p in sorted(glob.glob(str(HERE / "results/length48/shard_*.json.gz"))):
    b = json.load(gzip.open(p, "rt"))
    for r in b["reps"]:
        for f in r["factories"]:
            key = (f["n"], f["k"], tuple(tuple(q) for q in f["canonical_key"]))
            cur = best.get(key)
            if cur is None or (f["a3"], f["N"]) < (cur["a3"], cur["N"]):
                best[key] = dict(f, rep=r["rep_id"])
def gate_str(key):
    return "+".join("".join(str(i) for i in q) for q in sorted(key, key=lambda q: (len(q), q)))
by_nk = defaultdict(list)
for (n, k, key), f in best.items(): by_nk[(n, k)].append(f)
print("classes found so far, by (n, k):")
for (n, k) in sorted(by_nk): print(f"  n={n} k={k}: {len(by_nk[(n,k)])} classes, best a3 {min(f['a3'] for f in by_nk[(n,k)])}, N {min(f['N'] for f in by_nk[(n,k)])}..{max(f['N'] for f in by_nk[(n,k)])}")
master = json.load(open(HERE.parent.parent / "master_catalog/master_catalog.json"))["factories"]

def norm(key): return tuple(sorted(tuple(sorted(q)) for q in key))
ours = {(n, k, norm(key)): f for (n, k, key), f in best.items()}
print("\nmaster-catalogue rows at n = 47/48 vs this sweep (rank >= 8 parents):")
for r in sorted(master, key=lambda r: (r["n"], r["k"], r["N"])):
    if r["n"] not in (47, 48) or r["sk_key"] is None: continue
    f = ours.get((r["n"], r["k"], norm(r["sk_key"])))
    tag = f"FOUND  our best N={f['N']} (r={f['r']}) a3={f['a3']}" if f else "not in this sweep"
    print(f"  [[{r['n']},{r['k']},{r['d']}]] N={r['N']:2d} {r['gate']:<40.40} t={r['t_count']} {r['discovery']:<12} -> {tag}")
mkeys = {(r["n"], r["k"], norm(r["sk_key"])) for r in master if r["sk_key"] is not None}
new = [f for key, f in ours.items() if key not in mkeys]
print(f"\nclasses in this sweep absent from the master catalogue: {len(new)} of {len(ours)}")
from collections import Counter
print("  by (n,k):", dict(sorted(Counter((f['n'], f['k']) for f in new).items())))
print("\nnew classes with k >= 5 (n, k, N, a3, gate):")
for f in sorted(new, key=lambda f: (-f["k"], f["n"], f["a3"])):
    if f["k"] >= 5: print(f"  [[{f['n']},{f['k']},{f['distance']}]] N={f['N']} a3={f['a3']} a3max={f['a3_max']} {gate_str(f['canonical_key'])}  ({f['rep']} origin {f['origin']})")
