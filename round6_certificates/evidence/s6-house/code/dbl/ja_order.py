#!/usr/bin/env python3
"""Cut rank of transversal_t_codes/factories.json JA-441 (native order X1 | X2 | Y, recursively doubled:
79 | 79 | (47 | 47 | (47 | 47 | 95))) in a recursively interleaved order, and export that circuit with
the order as data/rows/JA-441.json and data/orders/JA-441.json."""
import json, hashlib, sys
from pathlib import Path
TOP = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(TOP / "code"))
from cutsurvey import profile, vecs_of
ROOT = Path("/Users/shubhamjain/Documents/IBM internship/Shraddha (Magic states)")
fac = {e["label"]: e for e in json.loads((ROOT / "magic-state-factory-repo/transversal_t_codes/factories.json").read_text())}
e = fac["JA-441"]
def inter(off, blocks):
    o = []
    if not blocks:
        return list(range(off, off + 95))
    nb = blocks[0]
    for p in range(nb):
        o += [off + p, off + nb + p]
    return o + inter(off + 2 * nb, blocks[1:])
order = inter(0, [79, 47, 47])
assert sorted(order) == list(range(441))
row = {"label": "JA-441", "k": e["k"], "N": e["N"], "columns": e["columns"],
       "columns_sha256": hashlib.sha256(json.dumps(e["columns"], separators=(",", ":")).encode()).hexdigest()}
(TOP / "data" / "rows" / "JA-441.json").write_text(json.dumps(row))
for name, o in (("native", list(range(441))), ("interleaved", order)):
    print(name, "cut H", max(profile([vecs_of(row, "H")[i] for i in o])), "cut G", max(profile([vecs_of(row, "G")[i] for i in o])))
(TOP / "data" / "orders" / "JA-441.json").write_text(json.dumps(order))
