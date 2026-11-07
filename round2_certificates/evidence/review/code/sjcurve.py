#!/usr/bin/env python3
"""Own hypothesis check of the San Jose theorem on a curve row, from the binary columns (no sanjose2 code).
Outer code C = L(a P_inf) on p_K(y) = x^17 over GF(256), points in the order x ascending, then y ascending
(the order the row's R indexes), K as in curvecheck.py.  Decodes every wire, checks the odd/even shapes, that the
extended vectors lie in C and span it, and that dim C = a - g + 1 with C^perp = L(b P_inf) (curvecheck.py).

    python sjcurve.py COLUMNS.json.gz t a R(json) modulus emb(json) U(json)
"""
import gzip
import json
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from sjcheck import GF, rank  # noqa: E402


def main():
    path, t, a = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    R = json.loads(sys.argv[4])
    mod = int(sys.argv[5])
    emb = json.loads(sys.argv[6])
    U = json.loads(sys.argv[7])
    F = GF(8, mod)
    m, s = 8, len(emb)
    sub16 = sorted(x for x in range(256) if F.pow(x, 16) == x)
    Kb = []
    for x in sub16:
        v = x
        for b in Kb:
            v = min(v, v ^ b)
        if v:
            Kb.append(x)
    Kb = Kb[: t.bit_length() - 1]
    K = [0]
    for b in Kb:
        K = K + [k ^ b for k in K]
    pts = []
    for x in range(256):
        rhs = F.pow(x, 17)
        for y in range(256):
            val = 1
            for k in K:
                val = F.mul(val, y ^ k)
            if val == rhs:
                pts.append((x, y))
    L = len(pts)
    g = (t - 1) * 8
    mon = [(i, j) for j in range(t) for i in range(a // t + 1) if t * i + 17 * j <= a]
    G = [[F.mul(F.pow(x, i), F.pow(y, j)) for x, y in pts] for i, j in mon]
    d = json.load(gzip.open(path))
    if "columns" not in d:
        (_, d), = d.items()
    cols, k, N = d["columns"], d["k"], d["N"]
    P = len(R)
    keep = [c for c in range(L) if c not in set(R)]
    res = {"n": len(cols), "k": k, "N": N, "L": L, "dimC_monomials": len(mon), "a-g+1": a - g + 1,
           "n_eq_s_retained": len(cols) == s * len(keep)}
    img = {tuple(bin(e & x).count("1") & 1 for e in emb): x for x in range(256)}
    res["phi_injective"] = len(img) == 256
    ok = True
    for i in range(m):
        for j in range(m):
            for l in range(m):
                aa, bb, cc = 1 << i, 1 << j, 1 << l
                lhs = sum(bin(e & aa).count("1") & bin(e & bb).count("1") & bin(e & cc).count("1") & 1 for e in emb) & 1
                ok &= lhs == F.tr(F.mul(F.mul(aa, bb), F.mul(cc, aa ^ bb ^ cc)))
    res["inner_map_identity"] = bool(ok)
    rowsets = [set() for _ in range(N)]
    for jj, c in enumerate(cols):
        for q in c:
            rowsets[q].add(jj)
    vals = [[img[tuple(1 if p * s + j in rowsets[w] else 0 for j in range(s))] for p in range(len(keep))]
            for w in range(N)]
    nU = len(U)
    shape = k == P * nU
    rec = []
    for i in range(P):
        base = [F.mul(F.inv(U[0]), x) for x in vals[i * nU]]
        for tt, u in enumerate(U):
            shape &= vals[i * nU + tt] == [F.mul(u, x) for x in base]
        full = [0] * L
        for c, x in zip(keep, base):
            full[c] = x
        full[R[i]] = 1
        rec.append(full)
    ne = (N - k) // m
    for r in range(ne):
        base = vals[k + r * m]
        for j in range(m):
            shape &= vals[k + r * m + j] == [F.mul(1 << j, x) for x in base]
        full = [0] * L
        for c, x in zip(keep, base):
            full[c] = x
        rec.append(full)
    res["shapes_ok"] = bool(shape and ne * m == N - k)
    rG = rank(F, G)
    rAll = rank(F, G + rec)
    rRec = rank(F, rec)
    res.update({"rank_G": rG, "rank_G_plus_recovered": rAll, "rank_recovered": rRec,
                "recovered_in_C": rAll == rG, "recovered_span_C": rRec == len(rec) == rG,
                "delta_dual_bound": a - 2 * g + 2, "bound_d": a - 2 * g + 2 - P})
    print(json.dumps(res), flush=True)


if __name__ == "__main__":
    main()
