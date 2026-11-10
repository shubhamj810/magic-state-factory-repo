#!/usr/bin/env python3
"""Cut rank (max over t of rank(prefix) + rank(suffix) - rank(all)) of the check part H and of all wires G,
for every exported row in data/rows/, in the stored order.   python cutsurvey.py [LABEL ...]"""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent

def profile(vecs):
    def pref(vs):
        piv, out = {}, [0]
        for v in vs:
            x = v
            while x:
                p = x.bit_length() - 1
                if p in piv: x ^= piv[p]
                else: piv[p] = x; break
            out.append(len(piv))
        return out
    a = pref(vecs); b = pref(vecs[::-1])[::-1]; r = a[-1]
    return [a[t] + b[t] - r for t in range(len(vecs) + 1)]

def vecs_of(row, which):
    k = row["k"]
    if which == "H":
        return [sum(1 << (q - k) for q in c if q >= k) for c in row["columns"]]
    return [sum(1 << q for q in c) for c in row["columns"]]

if __name__ == "__main__":
    labels = sys.argv[1:] or sorted(p.stem for p in (HERE / "data" / "rows").glob("*.json"))
    for lab in labels:
        row = json.loads((HERE / "data" / "rows" / f"{lab}.json").read_text())
        print(lab, len(row["columns"]), "d", row["d"], "cutH", max(profile(vecs_of(row, "H"))),
              "cutG", max(profile(vecs_of(row, "G"))), flush=True)
