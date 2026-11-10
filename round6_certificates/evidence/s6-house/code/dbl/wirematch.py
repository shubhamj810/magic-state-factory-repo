#!/usr/bin/env python3
"""Look for a wire permutation (output wire fixed) that maps the columns of JA-441 (factories.json) onto
the catalogue row 441.1.13.a as multisets, by colour refinement on the wire-column incidence and
backtracking.  If found, writes data/orders/441.1.13.a.from_JA.json: the catalogue column index of
each JA-441 column in the annealed JA order, so the trellis can run on the catalogue's own columns."""
import json, sys
from collections import Counter
from pathlib import Path
TOP = Path(__file__).resolve().parent.parent.parent
A = json.loads((TOP / "data/rows/JA-441.json").read_text()); B = json.loads((TOP / "data/rows/441.1.13.a.json").read_text())
N, k = A["N"], A["k"]
def refine(cols, fixed=()):
    col = {w: (0 if w < k else 1) for w in range(N)}
    for i, w in enumerate(fixed):
        col[w] = 2 + i
    for _ in range(8):
        cc = [tuple(sorted(col[w] for w in c)) for c in cols]
        sig = {w: (col[w], tuple(sorted(Counter(cc[j] for j, c in enumerate(cols) if w in c).items()))) for w in range(N)}
        keys = sorted(set(sig.values()))
        col = {w: keys.index(sig[w]) for w in range(N)}
    return col, sig
ca, sa = refine(A["columns"]); cb, sb = refine(B["columns"])
print("classes A", len(set(sa.values())), "B", len(set(sb.values())), "same signatures:", Counter(sa.values()) == Counter(sb.values()))
target = Counter(tuple(c) for c in B["columns"])
byclass = {}
for w in range(N):
    byclass.setdefault(sb[w], []).append(w)
sizes = Counter(len(v) for v in byclass.values()); print("class sizes", sorted(sizes.items()))

def search(fa, fb):
    ca_, sa_ = refine(A["columns"], fa); cb_, sb_ = refine(B["columns"], fb)
    if Counter(sa_.values()) != Counter(sb_.values()):
        return None
    cls = {}
    for w in range(N):
        cls.setdefault(sb_[w], []).append(w)
    amb = [v for v in cls.values() if len(v) > 1]
    if not amb:
        sigma = {w: cls[sa_[w]][0] for w in range(N)}
        mapped = Counter(tuple(sorted(sigma[w] for w in c)) for c in A["columns"])
        return sigma if mapped == target else None
    key = min(amb, key=len)
    wa = next(w for w in range(N) if sa_[w] == sb_[key[0]])
    for wb in key:
        r = search(fa + (wa,), fb + (wb,))
        if r:
            return r
    return None
sigma = search((), ())
print("wire permutation found:", sigma is not None)
if sigma:
    idx = {}
    for j, c in enumerate(B["columns"]):
        idx.setdefault(tuple(c), []).append(j)
    jaorder = json.loads((TOP / "data/orders/JA-441.json").read_text())
    out = [idx[tuple(sorted(sigma[w] for w in A["columns"][j]))].pop() for j in jaorder]
    assert sorted(out) == list(range(len(out)))
    (TOP / "data/orders/441.1.13.a.from_JA.json").write_text(json.dumps(out)); print("order written", sigma[0] == 0)
