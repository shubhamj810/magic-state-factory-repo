#!/usr/bin/env python3
"""Weight distribution of S^perp for a weak block (X stabilisers S of a self-dual CSS [[n_b,1]] code),
counted two ways: every word of S^perp enumerated (errorcoeff.span_weights on a basis of S^perp), and
MacWilliams from the enumerated distribution of S (errorcoeff.dual_count).  Both must agree.

    python blockw.py gong41|qr47|gong65    -> data/blockw_<name>.json
"""
import json, sys, time
from pathlib import Path
ROOT = Path(__import__('os').environ.get('MSF_ROOT', '/Users/shubhamjain/Documents/IBM internship/Shraddha (Magic states)'))
sys.path.insert(0, str(ROOT / "magic-state-factory-repo" / "transversal_t_codes"))
sys.path.insert(0, str(ROOT / "magic-state-factory-repo" / "master_catalog"))
import build_codes as BC                      # noqa: E402
import errorcoeff as EC                       # noqa: E402
TOP = Path(__file__).resolve().parent.parent


def nullspace(rows, n):
    """basis of {x : x.r = 0 for all r in rows}, by Gaussian elimination."""
    piv = {}
    for r in rows:
        x = r
        for p, v in piv.items():
            if (x >> p) & 1:
                x ^= v
        if x:
            p = x.bit_length() - 1
            for q in list(piv):
                if (piv[q] >> p) & 1:
                    piv[q] ^= x
            piv[p] = x
    free = [i for i in range(n) if i not in piv]
    out = []
    for f in free:
        v = 1 << f
        for p, r in piv.items():
            if (r >> f) & 1:
                v |= 1 << p
        out.append(v)
    return out


name = sys.argv[1]
S, nb = {"gong41": (lambda: BC.gong_self_dual(41), 41), "qr47": (lambda: BC.quantum_qr(47), 47),
         "gong65": (lambda: BC.gong_self_dual(65), 65)}[name]
S = S()
Sb = EC._basis(S)
P = nullspace(Sb, nb)
for v in P:
    assert all(bin(v & s).count("1") % 2 == 0 for s in Sb)
assert len(Sb) + len(P) == nb, (len(Sb), len(P))
t0 = time.time()
import os
if os.environ.get("BLOCKW_WDIST"):          # wdist.c (code/wdist) instead of errorcoeff.span_weights
    sys.path.insert(0, str(Path(__file__).resolve().parent / "wdist"))
    import macw
    span = lambda B, n: macw.dist(B, n, os.environ["BLOCKW_WDIST"])[0]
else:
    span = EC.span_weights
DP = span(P, nb)
t1 = time.time()
DS = span(Sb, nb)
mac = [EC.dual_count(DS, nb, w) for w in range(nb + 1)]
t2 = time.time()
assert mac == DP, "MacWilliams disagrees with the enumeration"
odd = {w: c for w, c in enumerate(DP) if c and w % 2}
even = {w: c for w, c in enumerate(DP) if c and w % 2 == 0}
rec = {"block": name, "n_b": nb, "dim_S": len(Sb), "dim_Sperp": len(P), "W": {w: c for w, c in enumerate(DP) if c},
       "min_odd": min(odd), "min_even_nonzero": min(w for w in even if w), "S_distribution": {w: c for w, c in enumerate(DS) if c},
       "seconds": [round(t1 - t0, 1), round(t2 - t1, 1)], "agree": True,
       "enumerator": "wdist.c" if os.environ.get("BLOCKW_WDIST") else "errorcoeff.span_weights"}
(TOP / "data" / f"blockw_{name}.json").write_text(json.dumps(rec, indent=1))
print(name, "dim S", len(Sb), "dim S^perp", len(P), "min odd", rec["min_odd"], "min even", rec["min_even_nonzero"],
      "W(min odd)", DP[rec["min_odd"]], "seconds", rec["seconds"])
