#!/usr/bin/env python3
"""A_w of a doubled factory from its parts (the doubling theorem's fault map, counted exactly).

The doubled factory (Jain-Albert map, generalised to k outputs by s3-d7 and s4-d8; research/search2/
s4-d8/code/dbl.py) lives on X1 | X2 | Y, with X = the union of the weak blocks (block b: n_b positions,
X stabilisers S_b, label l_b in F_2^k), Y = the inner factory F_t (checks C_t, outputs L):
    outputs (M_i, M_i, L_i);  checks (s, s, 0) for s in S,  (0, 0, c) for c in C_t,  (0, M_i, L_i),
with M_i = the union of the blocks whose label has bit i.  For a fault (e1, e2, e3) put u = e1 + e2,
g = e2 & u, e' = e2 - u.  Then (proof in the report, section 2):
    accepted  <=>  u in S^perp (blockwise),  C_t e3 = 0,  M(g) + M(e') = L e3;
    harmful   <=>  accepted and  M u + L e3 != 0;
    weight    =    |u| + 2|e'| + |e3|.
(e1, e2) <-> (u, g, e') is a bijection, M x depends only on the block parities of x, so

    A_w = sum_{w3, v} Inner(w3, v) * sum_{mu : mu + v != 0} DP[w - w3][mu][v],

Inner(w3, v) = #{e3 : |e3| = w3, C_t e3 = 0, L e3 = v} (Inner(0, 0) = 1), and DP[x][mu][m] = the number
of (u, g, e') with |u| + 2|e'| = x, M u = mu, M(g + e') = m, a product over blocks of
    W_b(j) * (2^(j-1) choices of g of each parity if j > 0, else g empty) * C(n_b - j, t_b),
W_b(j) the number of words of weight j in S_b^perp.  Every (w3, v) with a non-zero coefficient must
have its Inner value supplied, or the program stops; Inner(w3, v != 0) = 0 for w3 below the inner
distance needs no input.

    python dblformula.py SPEC.json        (SPEC: blocks, labels, k, w, inner counts; see main)
"""
from __future__ import annotations

import json
import sys
from math import comb
from pathlib import Path


def dp_table(blocks, k, wmax):
    """blocks: list of (n_b, W_b dict j -> count, label int).  Returns dict (x, mu, m) -> count."""
    cur = {(0, 0, 0): 1}
    for nb, W, lab in blocks:
        local = {}                       # (x, mu_bit, m_bit) -> count, before multiplying by the label
        for j, cnt in W.items():
            if cnt == 0 or j > wmax:
                continue
            gpar = {0: 1} if j == 0 else {0: 2 ** (j - 1), 1: 2 ** (j - 1)}
            for t in range(0, (wmax - j) // 2 + 1):
                ways_e = comb(nb - j, t)
                if ways_e == 0:
                    continue
                for pg, gw in gpar.items():
                    key = (j + 2 * t, j & 1, (pg + t) & 1)
                    local[key] = local.get(key, 0) + cnt * gw * ways_e
        nxt = {}
        for (x, mu, m), c in cur.items():
            for (y, bu, bm), c2 in local.items():
                if x + y > wmax:
                    continue
                key = (x + y, mu ^ (lab if bu else 0), m ^ (lab if bm else 0))
                nxt[key] = nxt.get(key, 0) + c * c2
        cur = nxt
    return cur


def a_w(blocks, k, w, inner, d_t):
    """inner: dict (w3, v) -> count for the supplied values.  Returns (A_w, terms)."""
    dp = dp_table(blocks, k, w)
    total, terms = 0, []
    for w3 in range(0, w + 1):
        for v in range(1 << k):
            coef = sum(c for (x, mu, m), c in dp.items() if x == w - w3 and m == v and (mu ^ v))
            if coef == 0:
                continue
            if (w3, v) == (0, 0):
                val = 1
            elif w3 == 0:
                val = 0                       # the empty e3 has L e3 = 0
            elif (w3, v) in inner:
                val = inner[(w3, v)]
            elif v != 0 and w3 < d_t:
                val = 0                       # below the inner distance no harmful set exists
            else:
                raise SystemExit(f"needs Inner({w3}, {v:0{k}b}), coefficient {coef}")
            terms.append({"w3": w3, "v": v, "coef": coef, "inner": val})
            total += coef * val
    return total, terms


def main():
    spec = json.loads(Path(sys.argv[1]).read_text())
    blocks = [(b["n_b"], {int(j): c for j, c in b["W"].items()}, b["label"]) for b in spec["blocks"]]
    inner = {(int(a), int(b)): c for a, b, c in spec["inner"]}
    out = {}
    for w in spec["weights"]:
        tot, terms = a_w(blocks, spec["k"], w, inner, spec["d_t"])
        out[w] = {"A_w": tot, "terms": terms}
        print(w, tot, terms)
    print(json.dumps({"name": spec.get("name"), "A": {w: out[w]["A_w"] for w in out}}))


if __name__ == "__main__":
    main()
