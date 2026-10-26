"""Exact certificate for the smallest distance-2 T-to-D_3 factory on n qubits (l=3), by coset enumeration.

A factory on n = k + r qubits is a parity network sum_y a_y (y.x) (mod 8) equal to target(x_out) up to a
diagonal Clifford, with N = #{y : a_y odd} input T states and no odd rotation on output-only parities (y with
no check bit), which is what makes every fault detectable (d >= 2). The odd patterns of such networks form the
coset (a0 mod 2) + V of the code V = {a mod 2 : M a = 0 mod 8} (punctured RM(n-4, n)), intersected with the
subspace that vanishes on output-only coordinates. N_min(n) is the minimum weight of that affine space, found
here by exact enumeration. Since an idle extra check qubit preserves any factory, N_min(n) is non-increasing in
n, so a value at n bounds every smaller circuit too.
"""
import os, sys, time, argparse
from math import comb

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "classification"))
from tcount import snf_z8, _solve_z8, _matvec_mod, NotInGroup  # noqa: E402

MOD = 8


def coset_dimension(n, k):
    return sum(comb(n, i) for i in range(n - 3)) - sum(comb(k, i) for i in range(n - 3))


def affine_space(target, k, n):
    """Return (b, C0, ncoord): coset representative and basis (Python-int bitmasks over check-touching
    parities), or None when no factory exists at this n."""
    nv = (1 << n) - 1
    chk = ((1 << n) - 1) ^ ((1 << k) - 1)
    M = [[bin(x & y).count("1") & 1 for y in range(1, nv + 1)] for x in range(1, nv + 1)]
    f = []
    for x in range(1, nv + 1):
        xs = {i for i in range(k) if x >> i & 1}
        f.append(sum(c for T, c in target.items() if T <= xs) % MOD)
    U, W, D = snf_z8(M)
    try:
        a0 = _solve_z8(U, W, D, f)
    except NotInGroup:
        return None
    assert _matvec_mod(M, a0) == [v % MOD for v in f]
    basis = []
    for i in range(nv):
        if D[i] % MOD == 0:
            v = 0
            for rr in range(nv):
                if W[rr][i] & 1:
                    v |= 1 << rr
            basis.append(v)
    assert len(basis) == sum(comb(n, i) for i in range(n - 3)), "kernel dimension mismatch"
    a = 0
    for rr in range(nv):
        if a0[rr] & 1:
            a |= 1 << rr
    out_bits = 0
    for y in range(1, nv + 1):
        if not (y & chk):
            out_bits |= 1 << (y - 1)
    piv = {}
    rest = []
    for v in basis:
        for p, pv in piv.items():
            if v >> p & 1:
                v ^= pv
        lo = v & out_bits
        if lo:
            p = lo.bit_length() - 1
            for q in list(piv):
                if piv[q] >> p & 1:
                    piv[q] ^= v
            piv[p] = v
        else:
            rest.append(v)
    for p, pv in piv.items():
        if a >> p & 1:
            a ^= pv
    if a & out_bits:
        return None
    rest2 = []
    for v in rest:
        for p, pv in piv.items():
            if v >> p & 1:
                v ^= pv
        rest2.append(v)
    keep = [y - 1 for y in range(1, nv + 1) if y & chk]
    def compress(v):
        out = 0
        for j, bit in enumerate(keep):
            if v >> bit & 1:
                out |= 1 << j
        return out
    C0 = []
    for v in rest2:
        v = compress(v)
        for w in C0:
            v = min(v, v ^ w)
        if v:
            C0.append(v)
    return compress(a), C0, len(keep)


def to_words(v, nwords):
    return np.array([(v >> (64 * i)) & 0xFFFFFFFFFFFFFFFF for i in range(nwords)], dtype=np.uint64)


def min_weight(b, C0, ncoord, chunk=22, stop_below=None, log=None):
    """Exact minimum weight of b + span(C0)."""
    nwords = (ncoord + 63) // 64
    d = len(C0)
    d1 = min(d, chunk)
    gens = [to_words(v, nwords) for v in C0]
    base = to_words(b, nwords)[None, :]
    for g in gens[:d1]:
        base = np.concatenate([base, base ^ g[None, :]])
    outer = gens[d1:]
    acc = np.zeros(nwords, dtype=np.uint64)
    best = int(np.bitwise_count(base).sum(axis=1).min())
    t0 = time.time()
    total = 1 << len(outer)
    for i in range(1, total):
        j = (i & -i).bit_length() - 1
        acc ^= outer[j]
        w = int(np.bitwise_count(base ^ acc[None, :]).sum(axis=1).min())
        if w < best:
            best = w
        if stop_below is not None and best < stop_below:
            break
        if log and i % 4096 == 0:
            log(f"   {i}/{total} outer steps, best so far {best}, {time.time() - t0:.0f}s")
    return best


def gf2_rref(rows, ncol):
    """Reduced row echelon form over GF(2); rows are int bitmasks over ncol coordinates. Returns (rows, pivots)."""
    rows = [r for r in rows if r]
    piv = []
    out = []
    for col in range(ncol):
        bit = 1 << col
        for i, r in enumerate(rows):
            if r & bit:
                out.append(r)
                rows.pop(i)
                rows = [x ^ r if x & bit else x for x in rows]
                out = [x ^ r if (x & bit and x is not r) else x for x in out]
                piv.append(col)
                break
    return out, piv


def capped_exists(b, C0, ncoord, N_cap, perms=12, seed=1, log=None):
    """Exact decision: does b + span(C0) contain a vector of weight < N_cap?

    Brouwer-Zimmermann style. For several information sets (random column orders), put the affine space in
    systematic form on that set; a vector that has at most w nonzeros on the information set is found by
    enumerating the <= w-subsets of generators. A vector of weight < N_cap has, on some set among m disjoint
    information sets, at most floor((N_cap-1)/m) nonzeros, so enumerating up to that w over m disjoint sets is
    complete. Returns (found, witness_weight)."""
    import random
    from itertools import combinations
    d = len(C0)
    if d == 0:
        w = bin(b).count("1")
        return w < N_cap, w
    rnd = random.Random(seed)
    used = 0
    sets = []
    while True:
        cols = list(range(ncoord))
        rnd.shuffle(cols)
        perm = {c: i for i, c in enumerate(cols)}
        def remap(v):
            out = 0
            for c in range(ncoord):
                if v >> c & 1:
                    out |= 1 << perm[c]
            return out
        G = [remap(v) for v in C0]
        R, piv = gf2_rref(G, ncoord)
        if len(R) < d:
            continue
        info = set(piv)
        if any(info & s for s in sets):
            if len(sets) >= 1 and used > 200:
                break
            used += 1
            continue
        sets.append(info)
        if len(sets) * d > ncoord or len(sets) >= perms:
            break
    m = len(sets)
    w_max = (N_cap - 1) // m
    best = None
    rnd = random.Random(seed)
    for s_idx in range(m):
        pass
    for s_idx in range(m):
        cols = list(range(ncoord))
        rnd2 = random.Random(seed + 1000 * (s_idx + 1))
        info = sorted(sets[s_idx])
        rest = [c for c in range(ncoord) if c not in sets[s_idx]]
        order = info + rest
        perm = {c: i for i, c in enumerate(order)}
        def remap(v):
            out = 0
            for c in range(ncoord):
                if v >> c & 1:
                    out |= 1 << perm[c]
            return out
        G, piv = gf2_rref([remap(v) for v in C0], ncoord)
        bb = remap(b)
        for g, p in zip(G, piv):
            if bb >> p & 1:
                bb ^= g
        for w in range(0, w_max + 1):
            for comb_ in combinations(range(d), w):
                v = bb
                for i in comb_:
                    v ^= G[i]
                wt = bin(v).count("1")
                if best is None or wt < best:
                    best = wt
                if wt < N_cap:
                    return True, wt
        if log:
            log(f"   info set {s_idx + 1}/{m} done (w<= {w_max}), best seen {best}")
    return False, best


def certify(target, k, n, N_star=None, log=print):
    t = time.time()
    sp = affine_space(target, k, n)
    if sp is None:
        return dict(n=n, k=k, feasible=False, Nmin=None, dim=None, seconds=time.time() - t)
    b, C0, ncoord = sp
    Nmin = min_weight(b, C0, ncoord, log=log)
    return dict(n=n, k=k, feasible=True, Nmin=Nmin, dim=len(C0), seconds=time.time() - t)


def parse_target(spec, L=3):
    GEN = {"T": 1, "CS": 2, "CCZ": 4}
    tgt = {}
    for tok in spec.split(","):
        name = tok.rstrip("0123456789")
        qs = frozenset(int(ch) for ch in tok[len(name):])
        tgt[qs] = (tgt.get(qs, 0) + GEN[name]) % (1 << L)
    return tgt


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="CCZ012,CS34")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--n", type=int, default=7)
    a = ap.parse_args()
    print(f"coset dimension at n={a.n}, k={a.k}: {coset_dimension(a.n, a.k)}")
    print(certify(parse_target(a.target), a.k, a.n))
