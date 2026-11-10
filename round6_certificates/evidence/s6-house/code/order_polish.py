#!/usr/bin/env python3
"""Polish a doubled row's column order from data/orders/ROWID.json: give every block pair the best local order
found for any block pair of the same size, then search the arrangement (and direction) of whole block pairs.
usage: python order_polish.py ROWID SECONDS"""
import json, random, sys, time
from pathlib import Path
from cutrank import colvecs
from doubled_order import blocks, score
HERE = Path(__file__).resolve().parent
rid, secs = sys.argv[1], float(sys.argv[2])
row = json.loads((HERE / "data" / "rows" / f"{rid}.json").read_text()); vecs = colvecs(row)
of = HERE / "data" / "orders" / f"{rid}.json"
order = json.loads(of.read_text()); pos = {c: i for i, c in enumerate(order)}
bl = blocks(row)
loc = {s: sorted(range(m), key=lambda t: pos[s + t]) for s, m, p in bl if p}
for s, m, p in bl:
    if not p: continue
    bvec = [vecs[s + t] for t in range(m)]
    for s2, m2, p2 in bl:
        if p2 and m2 == m and score(bvec, loc[s2]) < score(bvec, loc[s]):
            loc[s] = list(loc[s2])
units = []
for s, m, p in bl:
    if not p: units.append([s]); continue
    u = []
    for t in loc[s]: u += [s + t, s + m + t]
    units.append(u)
def ev(perm, flips):
    o = []
    for i, f in zip(perm, flips): o += units[i][::-1] if f else units[i]
    return score(vecs, o), o
cur = (list(range(len(units))), [0] * len(units)); cs, co = ev(*cur); best = (cs, co)
rng = random.Random(1); t0 = time.time()
while time.time() - t0 < secs:
    p, f = list(cur[0]), list(cur[1])
    if rng.random() < 0.5:
        i, j = rng.randrange(len(p)), rng.randrange(len(p)); x = p.pop(i); p.insert(j, x)
    else:
        f[rng.randrange(len(p))] ^= 1
    s, o = ev(p, f)
    if s <= cs: cur, cs = (p, f), s
    if s < best[0]: best = (s, o)
old = score(vecs, order)
print(rid, "before", old, "after", best[0])
if best[0] < old: of.write_text(json.dumps(best[1])); print("saved")
