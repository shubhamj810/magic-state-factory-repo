#!/usr/bin/env python3
"""A structured column order for s4-d8's doubled rows: the two copies of each block position side by side
(X1[p], X2[p]), block after block, then the inner code Y.  Built from rebuild.py's layout and mapped to the
catalogue's (sorted) column indices.  Writes data/orders/LABEL.json only if it beats the stored one."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
TOP = HERE.parent.parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
from cutsurvey import profile, vecs_of
import dbl
st = json.loads((TOP / "data" / "dbl_structure.json").read_text())
for lab in sys.argv[1:]:
    s = st[lab]
    row = json.loads((TOP / "data" / "rows" / f"{lab}.json").read_text())
    inner = json.loads((TOP / "data" / "rows" / f"{s['inner']}.json").read_text()) if (TOP / "data" / "rows" / f"{s['inner']}.json").exists() else None
    ns, nt, k = s["ns"], s["n_t"], s["k"]
    # rebuild the builder's column list to map builder index -> catalogue index
    import hashlib
    sys.path.insert(0, "/Users/shubhamjain/Documents/IBM internship/Shraddha (Magic states)/magic-state-factory-repo/master_catalog")
    import catalogfile as CF
    cat = {r["catalog_label"]: r for r in CF.load_all()["factories"]}
    x = cat[s["inner"]]
    rows = dbl.rows_from_cols(x["columns"], x["N"])
    L, C = rows[:k], rows[k:]
    S = [int(v) for v in s["S"]]
    nb = s["n_b"]
    SS, M = [], [0] * k
    for b, l in enumerate(s["labels"]):
        SS += dbl.shift_rows(S, nb * b)
        for i in range(k):
            if (l >> i) & 1:
                M[i] |= ((1 << nb) - 1) << (nb * b)
    f = dbl.double(SS, M, ns, C, L, x["n"])
    pos = {}
    for j, c in enumerate(row["columns"]):
        pos.setdefault(tuple(c), []).append(j)
    bmap = [pos[tuple(c)].pop() for c in f["columns"]]
    inner_order = list(range(nt))
    io = TOP / "data" / "orders" / f"{s['inner']}.json"
    if io.exists():
        inner_order = json.loads(io.read_text())
    order = []
    for p in range(ns):
        order += [bmap[p], bmap[ns + p]]
    order += [bmap[2 * ns + j] for j in inner_order]
    assert sorted(order) == list(range(len(row["columns"])))
    def sc(o, w):
        v = vecs_of(row, w); pr = profile([v[i] for i in o]); m = max(pr); return (m, pr.count(m), sum(pr))
    of = TOP / "data" / "orders" / f"{lab}.json"
    old = json.loads(of.read_text()) if of.exists() else list(range(len(row["columns"])))
    print(lab, "structured G", sc(order, "G"), "H", sc(order, "H"), "| current G", sc(old, "G"))
    if sc(order, "G") < sc(old, "G"):
        of.write_text(json.dumps(order)); print("saved")
