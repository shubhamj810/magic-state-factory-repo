"""Block-gluing sweep of every l=3 target state on k=7 and k=8 outputs (products of T, CS and CCZ on
disjoint qubits): smallest check register that admits a solution, verified and classified like the
main catalogue (n = input magic states, N = circuit qubits). Writes outputs/l3_k78_targets.csv. About 20 minutes.
Run: python3 searches/large_k_sweep.py
"""
import sys, time
import os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import unified_search as us
from symfree_search import solve_binding, _partitions
L = 3; out = []
for k in (7, 8):
    for parts in _partitions(k, L):
        t = time.time(); sol = None
        for r in range(1, 5):
            sol = solve_binding(parts, r, L)
            if sol is not None: break
        if sol is None:
            print(k, parts, "none", f"{time.time()-t:.0f}s", flush=True); continue
        f = dict(stage="gluing", k=k, r=r, gates=[(S, c % 8) for S, c in sol["gates"]], params="blocks=" + "+".join(map(str, parts)))
        ok = us.is_factory(f, L)
        info = us.classify_factory(f, L) if ok else None
        if info:
            row = dict(k=k, n=info["N"], N=info["n"], d=info["d"], reduced=info["reduced"], zcount=info["zcount"], params=f["params"],
                       quirk=us.quirk_url(f["gates"], info["n"], L))
            out.append(row)
            print(k, parts, "N=%d n=%d d=%s" % (info["N"], info["n"], info["d"]), info["reduced"][:70], f"{time.time()-t:.0f}s", flush=True)
import csv
with open(os.path.join(HERE, "..", "outputs", "l3_k78_targets.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["k", "n", "N", "d", "reduced", "zcount", "params", "quirk"])
    w.writeheader(); w.writerows(out)
