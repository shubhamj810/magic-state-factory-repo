#!/usr/bin/env python3
"""Own implementation of the fibre decomposition for W punctured at P (written from REPORT.md 2.2-2.4 and the
definitions; no code from research/search2/weighted is used).

Dual word c of W <-> fibres h_z (z in F_2^3) with h_z in RM(6,8), all congruent mod RM(5,8), sum in RM(4,8).
The fault of c is c minus P, of weight w(c) = sum_z |h_z minus P_z|, flipping |c cap P| outputs.

Per fibre z (points y in F_2^8, punctures P_z):
  psi2(y) = (1, y_i, y_i y_j) (37 bits), phi3(y) = (y_i y_j y_k) (56 bits), psi3 = (psi2 high, phi3 low).
  An echelon basis of psi3(P_z) has every pivot inside the psi2 bits (psi2(P_z) is independent).  Full
  reduction gives, for each y outside P_z, a canonical v(y) = (r(y), kappa'(y)) and the mask Q_y of punctures
  used.  For a set F outside P_z:
    sum_F r = 0           <=> F = h minus P_z for a (unique) h in RM(5,8); then h's cubic class is
                              kappa = sum_F kappa', and h cap P_z = XOR of the Q_y;
    sum_F v = 0           <=> F = h minus P_z for h in RM(4,8).
  A class g (28 bits) of RM(6,8) mod RM(5,8): delta_z(g) = least |B| over B outside with
    sum_B r = red_z((0, g)).

Outputs:
  case A: min over nonzero g of sum_z min(delta_z(g), 3) over the classes lying in some V_z (the classes of RM(6,8)
          words inside P_z); every other class has delta >= 1 in all fibres (bound 8).
  case B: exact counts, for each total weight t <= T, of words with g = 0, kappa nonzero in >= 2 fibres, zero
          elsewhere; and the flipped-output total.  Uses full tables for set sizes <= 4 and targeted counts for
          sizes 5 and 6.
  case C: done separately with sweep.c on v (all fibres), see casec.py.

    python fibown.py PROBLEM.json T
"""
import itertools
import json
import sys
import time
from collections import defaultdict

PAIRS = [(i, j) for i in range(8) for j in range(i + 1, 8)]
TRIPLES = list(itertools.combinations(range(8), 3))
M56 = (1 << 56) - 1


def psi2(y):
    v = 1
    for i in range(8):
        v |= ((y >> i) & 1) << (1 + i)
    for t, (i, j) in enumerate(PAIRS):
        v |= (((y >> i) & (y >> j)) & 1) << (9 + t)
    return v


def phi3(y):
    v = 0
    for t, (i, j, k) in enumerate(TRIPLES):
        v |= (((y >> i) & (y >> j) & (y >> k)) & 1) << t
    return v


def psi3(y):
    return (psi2(y) << 56) | phi3(y)


class Basis:
    """echelon basis with full (canonical) reduction; tracks combination masks"""

    def __init__(self):
        self.vec = {}   # pivot -> (vector, mask)

    def reduce(self, v, m=0):
        for p in sorted(self.vec, reverse=True):
            if (v >> p) & 1:
                bv, bm = self.vec[p]
                v ^= bv
                m ^= bm
        return v, m

    def add(self, v, m):
        v, m = self.reduce(v, m)
        if v == 0:
            return False
        self.vec[v.bit_length() - 1] = (v, m)
        return True


def fibre_data(Pz):
    B = Basis()
    for i, y in enumerate(Pz):
        assert B.add(psi3(y), 1 << i), "psi3(P_z) dependent"
    assert all(p >= 56 for p in B.vec), "pivot outside psi2 bits"
    # psi2(P_z) independent follows from all pivots >= 56
    out = [y for y in range(256) if y not in set(Pz)]
    V = {}
    for y in out:
        v, m = B.reduce(psi3(y), 0)
        V[y] = (v >> 56, v & M56, m)
    return B, out, V


def popc(x):
    return bin(x).count("1")


def tables(out, V, wmax_full=4):
    """N[w][kappa] = [count, flips] over sets F of size w with sum r = 0 and kappa != 0, for w <= 4.
    Also counts of sets with sum r = 0 and kappa = 0 (these are RM(4,8) words) for a cross-check."""
    N = {w: defaultdict(lambda: [0, 0]) for w in range(1, wmax_full + 1)}
    zero_kappa = {w: 0 for w in range(1, wmax_full + 1)}
    idx = {y: i for i, y in enumerate(out)}
    r = [V[y][0] for y in out]
    kp = [V[y][1] for y in out]
    qm = [V[y][2] for y in out]
    n = len(out)
    by_r = defaultdict(list)
    for i in range(n):
        by_r[r[i]].append(i)

    def rec(w, kap, q):
        if kap:
            e = N[w][kap]
            e[0] += 1
            e[1] += popc(q)
        else:
            zero_kappa[w] += 1
    for i in range(n):
        if r[i] == 0:
            rec(1, kp[i], qm[i])
    # pairs
    pairs_by_r = defaultdict(list)
    for i in range(n):
        for j in range(i + 1, n):
            rr = r[i] ^ r[j]
            pairs_by_r[rr].append((i, j))
            if rr == 0:
                rec(2, kp[i] ^ kp[j], qm[i] ^ qm[j])
    # triples: pair (i,j) plus l > j with r[l] = r[i]^r[j]
    for rr, lst in pairs_by_r.items():
        cand = by_r.get(rr)
        if not cand:
            continue
        for (i, j) in lst:
            for l in cand:
                if l > j:
                    rec(3, kp[i] ^ kp[j] ^ kp[l], qm[i] ^ qm[j] ^ qm[l])
    # 4-sets: two disjoint pairs with equal r; each 4-set appears as 3 unordered pairs of pairs; count the one
    # whose first pair contains the smallest element and whose pair partner is the smallest remaining... simpler:
    # require i < k (first pair holds the minimum) and count; each 4-set {a<b<c<d} has the splits
    # {a,b}{c,d}, {a,c}{b,d}, {a,d}{b,c}: exactly 3 with the minimum in the first pair.  Divide by 3 at the end.
    four = defaultdict(lambda: [0, 0])
    fz = 0
    for rr, lst in pairs_by_r.items():
        L = len(lst)
        if L < 2:
            continue
        for a in range(L):
            i, j = lst[a]
            for b in range(L):
                k, l = lst[b]
                if i < k and k != j and l != j:
                    kap = kp[i] ^ kp[j] ^ kp[k] ^ kp[l]
                    q = qm[i] ^ qm[j] ^ qm[k] ^ qm[l]
                    if kap:
                        e = four[kap]
                        e[0] += 1
                        e[1] += popc(q)
                    else:
                        fz += 1
    for kap, (c, f) in four.items():
        assert c % 3 == 0 and f % 3 == 0
        N[4][kap] = [c // 3, f // 3]
    zero_kappa[4] = fz // 3
    return N, zero_kappa, (r, kp, qm, pairs_by_r, by_r)


def targeted(aux, w, Kset):
    """{kappa: [count, flips]} for sets of size w in {5, 6} with sum r = 0 and class in Kset."""
    r, kp, qm, pairs_by_r, by_r = aux
    n = len(r)
    res = defaultdict(lambda: [0, 0])
    if not Kset:
        return res
    # triples keyed by full value (r, kappa)
    trip = defaultdict(list)
    for rr, lst in pairs_by_r.items():
        for (i, j) in lst:
            for l in range(j + 1, n):
                trip[(r[i] ^ r[j] ^ r[l], kp[i] ^ kp[j] ^ kp[l])].append((i, j, l))
    if w == 5:
        # 2 + 3, disjoint, each 5-set counted C(5,2) = 10 times
        for rr, lst in pairs_by_r.items():
            for (i, j) in lst:
                ka = kp[i] ^ kp[j]
                for K in Kset:
                    for (a, b, c) in trip.get((rr, ka ^ K), ()):
                        if a in (i, j) or b in (i, j) or c in (i, j):
                            continue
                        e = res[K]
                        e[0] += 1
                        e[1] += popc(qm[i] ^ qm[j] ^ qm[a] ^ qm[b] ^ qm[c])
        div = 10
    elif w == 6:
        # 3 + 3, ordered disjoint, each 6-set counted C(6,3) = 20 times
        for (rr, ka), lst in list(trip.items()):
            for K in Kset:
                other = trip.get((rr, ka ^ K))
                if not other:
                    continue
                for t1 in lst:
                    s1 = set(t1)
                    for t2 in other:
                        if s1.isdisjoint(t2):
                            e = res[K]
                            e[0] += 1
                            q = 0
                            for x in t1 + t2:
                                q ^= qm[x]
                            e[1] += popc(q)
        div = 20
    else:
        raise ValueError(w)
    out = {}
    for K, (c, f) in res.items():
        assert c % div == 0 and f % div == 0, (w, c, f)
        out[K] = [c // div, f // div]
    return out


def case_a(fib, data):
    """min over classes g in union of V_z of sum_z min(delta_z(g), 3)"""
    R1, R2 = {}, {}
    for z in range(8):
        B, out, V = data[z]
        rs = [V[y][0] for y in out]
        R1[z] = set(rs)
        R2[z] = {a ^ b for a, b in itertools.combinations(rs, 2)}

    def red(z, g):
        B = data[z][0]
        v, _ = B.reduce((g << 9) << 56, 0)
        return v >> 56

    worst = None
    nclasses = 0
    dims = {}
    for z0 in range(8):
        Pz = fib[z0]
        # kernel of psi1 on P_z0, tracked quadratic parts
        basis = {}
        gens = []
        for y in Pz:
            lo = psi2(y) & 0x1FF
            hi = psi2(y) >> 9
            for p in sorted(basis, reverse=True):
                if (lo >> p) & 1:
                    blo, bhi = basis[p]
                    lo ^= blo
                    hi ^= bhi
            if lo:
                basis[lo.bit_length() - 1] = (lo, hi)
            else:
                gens.append(hi)
        # independent generators of V_z0
        G = Basis()
        for g in gens:
            G.add(g, 0)
        gb = [v for v, _ in G.vec.values()]
        dims[z0] = len(gb)
        # Gray code over nonzero combinations; reductions are linear
        redg = [[red(z, g) for z in range(8)] for g in gb]
        cur = [0] * 8
        g = 0
        for step in range(1, 1 << len(gb)):
            bitp = (step & -step).bit_length() - 1
            g ^= gb[bitp]
            for z in range(8):
                cur[z] ^= redg[bitp][z]
            tot = 0
            for z in range(8):
                c = cur[z]
                if c == 0:
                    dz = 0
                elif c in R1[z]:
                    dz = 1
                elif c in R2[z]:
                    dz = 2
                else:
                    dz = 3
                tot += dz
            nclasses += 1
            assert cur[z0] == 0
            if worst is None or tot < worst[0]:
                worst = (tot, z0, g)
    return {"A_min_bound": worst[0] if worst else None, "A_classes": nclasses, "A_dims": dims,
            "A_worst": [worst[1], worst[2]] if worst else None}


def combine(N, aux, T):
    """counts[t] = [words, flips] of case-B words of total weight t, for t <= T (T <= 8)."""
    counts = {t: [0, 0] for t in range(1, T + 1)}

    def wparts(m, t):
        # compositions of t into m parts each >= 1
        if m == 1:
            yield (t,)
            return
        for a in range(1, t - m + 2):
            for rest in wparts(m - 1, t - a):
                yield (a,) + rest
    big_cache = {}
    for t in range(2, T + 1):
        for m in range(2, t + 1):
            for zs in itertools.combinations(range(8), m):
                for ws in wparts(m, t):
                    # last part is the lookup target: choose the part with the largest weight
                    order = sorted(range(m), key=lambda i: ws[i])
                    last = order[-1]
                    rest = order[:-1]
                    if any(ws[i] > 4 for i in rest):
                        continue        # two parts above 4 would need t >= 10 > 8
                    if any(not N[zs[i]][ws[i]] for i in rest):
                        continue
                    # product over the rest
                    acc = {0: [1, 0]}
                    for i in rest:
                        tab = N[zs[i]][ws[i]]
                        new = defaultdict(lambda: [0, 0])
                        for k1, (c1, f1) in acc.items():
                            for k2, (c2, f2) in tab.items():
                                e = new[k1 ^ k2]
                                e[0] += c1 * c2
                                e[1] += f1 * c2 + c1 * f2
                        acc = new
                    zl, wl = zs[last], ws[last]
                    if wl <= 4:
                        tab = N[zl][wl]
                    else:
                        key = (zl, wl)
                        need = {k for k in acc if k}
                        have = big_cache.setdefault(key, {})
                        missing = need - set(have)
                        if missing:
                            got = targeted(aux[zl], wl, missing)
                            for k in missing:
                                have[k] = got.get(k, [0, 0])
                        tab = have
                    for k1, (c1, f1) in acc.items():
                        if k1 == 0:
                            continue
                        e = tab.get(k1)
                        if e and e[0]:
                            counts[t][0] += c1 * e[0]
                            counts[t][1] += f1 * e[0] + c1 * e[1]
    return counts


def main(path, T):
    t0 = time.time()
    d = json.load(open(path))
    P = d["points"]
    fib = {z: sorted(p & 255 for p in P if p >> 8 == z) for z in range(8)}
    data = {z: fibre_data(fib[z]) for z in range(8)}
    res = {"file": path, "fibre_sizes": [len(fib[z]) for z in range(8)]}
    res.update(case_a(fib, data))
    res["t_case_a"] = round(time.time() - t0, 1)
    print(json.dumps(res), flush=True)
    N, AUX, ZK = {}, {}, {}
    for z in range(8):
        B, out, V = data[z]
        N[z], ZK[z], AUX[z] = tables(out, V)
        res.setdefault("B_table_sizes", {})[z] = {w: len(N[z][w]) for w in N[z]}
        res.setdefault("B_min_eps", {})[z] = min((w for w in N[z] if N[z][w]), default=None)
        res.setdefault("zero_kappa_counts", {})[z] = ZK[z]
    res["t_tables"] = round(time.time() - t0, 1)
    print(json.dumps({"B_min_eps": res["B_min_eps"], "zero_kappa": res["zero_kappa_counts"], "t": res["t_tables"]}),
          flush=True)
    res["B_counts"] = combine(N, AUX, T)
    res["seconds"] = round(time.time() - t0, 1)
    print(json.dumps(res), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))
