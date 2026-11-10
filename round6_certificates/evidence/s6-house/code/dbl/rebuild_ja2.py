#!/usr/bin/env python3
"""transversal_t_codes/factories.json circuits (native column order X1 | X2 | Y): check that each
doubled one has the same check span and the same full span, column by column, as s4-d8's
dbl.double applied to the factories.json circuit it names (label [1]).  Equal spans on the same
column order mean the same accepted and harmful fault sets, so the same A_w."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = Path("/Users/shubhamjain/Documents/IBM internship/Shraddha (Magic states)")
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "magic-state-factory-repo" / "transversal_t_codes"))
import dbl                                           # noqa: E402
import build_codes as BC                             # noqa: E402
fac = {e["label"]: e for e in json.loads((ROOT / "magic-state-factory-repo/transversal_t_codes/factories.json").read_text())}
CASES = [("G-177", "JA-95", "gong41"), ("JA-189", "JA-95", "qr47"), ("G-271", "G-177", "qr47"),
         ("JA-283", "JA-189", "qr47"), ("G-401", "G-271", "gong65"), ("JA-441", "JA-283", "qr79")]
blk = {"gong41": lambda: (BC.gong_self_dual(41), 41), "gong65": lambda: (BC.gong_self_dual(65), 65),
       "qr47": lambda: (BC.quantum_qr(47), 47), "qr79": lambda: (BC.quantum_qr(79), 79)}
print(sorted(l for l in fac if l.startswith(("JA-9", "G-1", "JA-1"))))
for lab, inner, b in CASES:
    if inner not in fac:
        print(lab, "inner", inner, "not in factories.json"); continue
    x, y = fac[inner], fac[lab]
    rows = dbl.rows_from_cols(x["columns"], x["N"])
    S, nb = blk[b]()
    f = dbl.double(S, [(1 << nb) - 1], nb, rows[x["k"]:], rows[:x["k"]], x["n"])
    A = dbl.rows_from_cols(f["columns"], f["N"]); B = dbl.rows_from_cols(y["columns"], y["N"])
    hA, hB = A[1:], B[1:]
    ok_h = dbl.rank(hA) == dbl.rank(hB) == dbl.rank(hA + hB)
    ok_g = dbl.rank(A) == dbl.rank(B) == dbl.rank(A + B)
    print(lab, "= double(", b, ",", inner, "):", "check span equal", ok_h, "| full span equal", ok_g)
