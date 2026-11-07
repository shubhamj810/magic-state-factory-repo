#!/usr/bin/env python3
"""Own check (no sanjose2 code) of the San Jose theorem's hypotheses on a GRS row, from the binary columns.

Theorem (research/search/sparse/REPORT.md 2.2): if the wires are the binary images, under an F_2-linear inner map
phi: GF(2^m) -> F_2^s, of field vectors on the retained coordinates, with
  odd wires  phi(u g_i)    for u in U, g_i in C, g_i = e_i on R (i-th removed coordinate),
  even wires phi(beta h)   for beta over a basis of GF(2^m)/F_2 and h over a basis of {c in C : c = 0 on R},
then every harmful fault has weight >= delta(C^perp) - |R|.
This script decodes every wire's s-bit blocks to field values, checks the two shapes, checks membership of the
extended vectors in C = GRS_k(A, v) with v_a = r_a^(q/4), r_a = 1/prod_{b != a}(a + b), and the subcode
dimension.  delta(C^perp) = deg + 2 because the dual of a GRS code is GRS (MDS); distinct points and nonzero v
are checked.

    python sjcheck.py COLUMNS.json.gz m L deg R(json) modulus emb(json) U(json)
"""
import gzip
import json
import sys


class GF:
    def __init__(self, m, mod):
        self.m, self.q, self.mod = m, 1 << m, mod

        def pmul(a, b):
            r = 0
            while b:
                if b & 1:
                    r ^= a
                b >>= 1
                a <<= 1
                if a & self.q:
                    a ^= mod
            return r
        # find a primitive element (the modulus need not be primitive, e.g. 283 for GF(256))
        for g in range(2, self.q):
            self.exp = [0] * (2 * self.q)
            self.log = [0] * self.q
            x = 1
            for i in range(self.q - 1):
                self.exp[i] = x
                self.log[x] = i
                x = pmul(x, g)
            if len(set(self.exp[: self.q - 1])) == self.q - 1:
                break
        assert len(set(self.exp[: self.q - 1])) == self.q - 1, "no primitive element: modulus reducible"
        for i in range(self.q - 1, 2 * self.q):
            self.exp[i] = self.exp[i - (self.q - 1)]
        self.pmul = pmul
        assert all(self.mul(a, b) == pmul(a, b) for a in range(1, self.q, 7) for b in range(1, self.q, 5))

    def mul(self, a, b):
        return 0 if a == 0 or b == 0 else self.exp[self.log[a] + self.log[b]]

    def inv(self, a):
        return self.exp[(self.q - 1 - self.log[a]) % (self.q - 1)]

    def pow(self, a, e):
        if e == 0:
            return 1
        return 0 if a == 0 else self.exp[(self.log[a] * e) % (self.q - 1)]

    def tr(self, a):
        t, x = 0, a
        for _ in range(self.m):
            t ^= x
            x = self.mul(x, x)
        return t


def rank(F, rows):
    rows = [list(r) for r in rows]
    r = 0
    ncol = len(rows[0]) if rows else 0
    for c in range(ncol):
        p = next((i for i in range(r, len(rows)) if rows[i][c]), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        iv = F.inv(rows[r][c])
        rows[r] = [F.mul(iv, x) for x in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c]:
                f = rows[i][c]
                rows[i] = [x ^ F.mul(f, y) for x, y in zip(rows[i], rows[r])]
        r += 1
    return r


def main():
    path, m, L, deg = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    R = json.loads(sys.argv[5])
    mod = int(sys.argv[6])
    emb = json.loads(sys.argv[7])
    U = json.loads(sys.argv[8])
    F = GF(m, mod)
    s = len(emb)
    d = json.load(gzip.open(path))
    if "columns" not in d:
        (_, d), = d.items()
    cols, k, N = d["columns"], d["k"], d["N"]
    n = len(cols)
    P = len(R)
    keep = [a for a in range(L) if a not in set(R)]
    res = {"n": n, "k": k, "N": N, "s": s, "retained": len(keep), "n_eq_s_retained": n == s * len(keep)}
    # inner map: bit j of phi(x) = parity(emb[j] & x)
    img = {}
    for x in range(F.q):
        img[tuple(bin(e & x).count("1") & 1 for e in emb)] = x
    res["phi_injective"] = len(img) == F.q
    # trilinear identity on all triples of basis elements (phi linear, RHS F_2-trilinear)
    ok = True
    for i in range(m):
        for j in range(m):
            for l in range(m):
                a, b, c = 1 << i, 1 << j, 1 << l
                lhs = sum((bin(e & a).count("1") & bin(e & b).count("1") & bin(e & c).count("1")) & 1
                          for e in emb) & 1
                rhs = F.tr(F.mul(F.mul(a, b), F.mul(c, a ^ b ^ c)))
                ok &= (lhs == (rhs & 1))
    res["inner_map_identity"] = ok
    # decode wires
    rowsets = [set() for _ in range(N)]
    for j, c in enumerate(cols):
        for q in c:
            rowsets[q].add(j)
    vals = []
    for w in range(N):
        v = []
        for a in range(len(keep)):
            bits = tuple(1 if a * s + j in rowsets[w] else 0 for j in range(s))
            v.append(img[bits])
        vals.append(v)
    nU = len(U)
    assert k == P * nU
    # odd rows u * g_i
    shape_ok = True
    rec = []
    for i in range(P):
        base = [F.mul(F.inv(U[0]), x) for x in vals[i * nU]]
        for t, u in enumerate(U):
            shape_ok &= vals[i * nU + t] == [F.mul(u, x) for x in base]
        full = [0] * L
        for a, x in zip(keep, base):
            full[a] = x
        full[R[i]] = 1
        rec.append(full)
    ne = (N - k) // m
    res["even_blocks"] = ne
    for r in range(ne):
        base = vals[k + r * m]
        for j in range(m):
            shape_ok &= vals[k + r * m + j] == [F.mul(1 << j, x) for x in base]
        full = [0] * L
        for a, x in zip(keep, base):
            full[a] = x
        rec.append(full)
    res["shapes_ok"] = bool(shape_ok and N - k == ne * m)
    # outer code
    A = list(range(L))
    rr = []
    for a in A:
        den = 1
        for b in A:
            if b != a:
                den = F.mul(den, a ^ b)
        rr.append(F.inv(den))
    v = [F.pow(x, F.q // 4) for x in rr]
    res["v_nonzero"] = all(v)
    G = [[F.mul(v[i], F.pow(a, e)) for i, a in enumerate(A)] for e in range(deg + 1)]
    rG = rank(F, G)
    rAll = rank(F, G + rec)
    rRec = rank(F, rec)
    res.update({"rank_G": rG, "rank_G_plus_recovered": rAll, "rank_recovered": rRec,
                "recovered_in_C": rAll == rG, "recovered_full": rRec == len(rec) == deg + 1,
                "subcode_dim_ok": ne == deg + 1 - P})
    # residue moments for field triorthogonality: sum_a r_a a^e = 0 for e <= L-2 (fourth power of C has degree
    # 4 deg <= L - 2 and v^4 = r)
    mom = True
    for e in range(L - 1):
        t = 0
        for a, x in zip(A, rr):
            t ^= F.mul(x, F.pow(a, e))
        mom &= (t == 0)
    res["moments_to_L-2"] = mom
    res["4deg_le_L-2"] = 4 * deg <= L - 2
    res["delta_dual"] = deg + 2
    res["bound"] = deg + 2 - P
    print(json.dumps(res), flush=True)


if __name__ == "__main__":
    main()
