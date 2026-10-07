"""EXACT minimal T-count of a diagonal level-3 magic state, via the
Amy--Mosca / Reed--Muller minimum-weight-coset method.  COMPLETELY SELF-CONTAINED
(pure Python + numpy; no other project modules required).

A deposited magic state on k output qubits is a diagonal gate
    U = diag_x exp(i (pi/4) f(x)),    f: F_2^k -> Z_8 multilinear (coeffs mod 8),
built from a named product decomposition
    T_i -> +1 on {i},  CS_ij -> +2 on {i,j},  CCZ_ijk -> +4 on {i,j,k}.

A level-3 diagonal gate is a product of pi/4 rotations on PARITIES:
    f(x) = sum_{y != 0} a_y (y . x mod 2)  (mod 8),   a_y in Z_8,
and the T-count of a representation {a_y} is #{y : a_y odd}.  The representation is NOT
unique -- two representations differ by an element of the kernel
    V = { a mod 2 : M a == 0 (mod 8) }   (the Amy--Mosca / punctured RM(k-4,k) code),
so the exact minimal T-count is the MINIMUM-WEIGHT COSET LEADER of (a0 mod 2) + V.

Algorithm (exact):
  1. Parity matrix  M[x,y] = popcount(x AND y) mod 2  over the nonzero points of F_2^k.
     fvec[x] = f(x) mod 8.
  2. Solve  M a == fvec (mod 8)  for a particular a0 (Smith normal form of M over Z/8).
  3. V = mod-2 image of the Z_8 kernel of M (columns of W at the free/order-8 coordinates,
     reduced mod 2).  dim(V) is cross-checked against the RM formula sum_{i=0}^{k-4} C(k,i).
  4. minimal T-count = min over v in V of popcount( (a0 mod 2) XOR v ).

Public API:
    tcount_rm(P, k)          -- P = {frozenset(support): coeff mod 8}, qubit labels in 1..k
    tcount_rm_decomp("T1 CS12") -- convenience wrapper on a decomposition string

Run:  python3 -m factorylib.tcount     (self-test: anchors + dim(V) + exact k=6 values)
"""
from itertools import combinations
from math import comb

import numpy as np

MOD = 8


# ============================================================ decomposition -> polynomial
def poly_from_terms(terms):
    """terms: list of (frozenset(support), strength).  Returns coeff dict mod 8 (multilinear)."""
    P = {}
    for S, s in terms:
        S = frozenset(S)
        P[S] = (P.get(S, 0) + s) % MOD
    return {S: c for S, c in P.items() if c}


def parse_gate(name):
    """'T1'->({1},1)  'CS12'->({1,2},2)  'CCZ123'->({1,2,3},4).  1-indexed qubit labels."""
    if name.startswith("CCZ"):
        return (frozenset(int(d) for d in name[3:]), 4)
    if name.startswith("CS"):
        return (frozenset(int(d) for d in name[2:]), 2)
    if name.startswith("T"):
        return (frozenset(int(d) for d in name[1:]), 1)
    raise ValueError(name)


def poly_from_decomp(decomp):
    """decomp: space-separated gate names, e.g. 'T1 CS12'.  Returns (P, qubits)."""
    P = poly_from_terms([parse_gate(g) for g in decomp.split()])
    return P, sorted({q for S in P for q in S})


def eval_poly(P, xset):
    """P(x) mod 8 at the point whose 1-bits are xset."""
    return sum(c for S, c in P.items() if S <= xset) % MOD


# ============================================================ exact Z/8 linear algebra
def _val2(x, mod=MOD):
    """2-adic valuation of x mod `mod` (a power of 2); returns a large number for 0."""
    x %= mod
    if x == 0:
        return 99
    v = 0
    while x % 2 == 0:
        x //= 2
        v += 1
    return v


def snf_z8(Mrows, mod=MOD):
    """Smith normal form over Z/mod (mod a power of 2): (U M W) == diag(D), U,W invertible,
    every D[i] a power of two dividing `mod` (or 0)."""
    A = [row[:] for row in Mrows]
    n = len(A)
    m = len(A[0]) if n else 0
    U = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    W = [[1 if i == j else 0 for j in range(m)] for i in range(m)]

    def rowswap(i, j):
        A[i], A[j] = A[j], A[i]
        U[i], U[j] = U[j], U[i]

    def colswap(i, j):
        for r in A:
            r[i], r[j] = r[j], r[i]
        for r in W:
            r[i], r[j] = r[j], r[i]

    def rowaddmul(dst, src, q):
        Ad, As = A[dst], A[src]
        for c in range(m):
            Ad[c] = (Ad[c] - q * As[c]) % mod
        Ud, Us = U[dst], U[src]
        for c in range(n):
            Ud[c] = (Ud[c] - q * Us[c]) % mod

    def coladdmul(dst, src, q):
        for r in range(n):
            A[r][dst] = (A[r][dst] - q * A[r][src]) % mod
        for r in range(m):
            W[r][dst] = (W[r][dst] - q * W[r][src]) % mod

    for t in range(min(n, m)):
        best = None
        for i in range(t, n):
            for j in range(t, m):
                if A[i][j] % mod:
                    v = _val2(A[i][j], mod)
                    if best is None or v < best[0]:
                        best = (v, i, j)
                        if v == 0:
                            break
            if best is not None and best[0] == 0:
                break
        if best is None:
            break
        _, pi, pj = best
        if pi != t:
            rowswap(pi, t)
        if pj != t:
            colswap(pj, t)
        # The pivot has minimal 2-adic valuation among the remaining entries,
        # so over Z/2^r it exactly divides each of them: the brute-force
        # quotient search below always terminates with an exact q.
        piv = A[t][t]
        for i in range(t + 1, n):
            if A[i][t] % mod:
                for q in range(mod):
                    if (A[i][t] - q * piv) % mod == 0:
                        rowaddmul(i, t, q)
                        break
        for j in range(t + 1, m):
            if A[t][j] % mod:
                for q in range(mod):
                    if (A[t][j] - q * piv) % mod == 0:
                        coladdmul(j, t, q)
                        break
    D = [A[i][i] % mod for i in range(min(n, m))]
    return U, W, D


def _matvec_mod(Mat, vec, mod=MOD):
    out = [0] * len(Mat)
    for i, row in enumerate(Mat):
        out[i] = sum(row[j] * vec[j] for j in range(len(vec))) % mod
    return out


class NotInGroup(ValueError):
    """The gate is not in the group generated by pi/4 parity rotations.

    An expected OUTCOME, not a failure: `metrics_from_named` catches it and
    reports `t_count = None` with a note.  It has its own type because it used to
    be signalled with `assert`, and under `python -O` that assertion vanished --
    leaving `_solve_z8` to return a vector that does not solve the system, and the
    second stripped assertion to wave it through, so the decoder reported a
    confident and wrong T-count for any gate outside the group.
    """


def _solve_z8(U, W, D, fvec, mod=MOD):
    """Particular solution a0 of M a == fvec (mod), given Smith form U M W = diag(D).

    Raises `NotInGroup` when the system is unsolvable over Z_8."""
    c = _matvec_mod(U, fvec, mod)
    n = len(D)
    ap = [0] * n
    for i in range(n):
        d, ci = D[i] % mod, c[i] % mod
        if d == 0:
            if ci != 0:
                raise NotInGroup(
                    f"no Z_8 solution: free coordinate {i} requires {ci} == 0")
            ap[i] = 0
        else:
            for val in range(mod):
                if (d * val) % mod == ci:
                    ap[i] = val
                    break
            else:
                raise NotInGroup(f"no Z_8 solution: {d}*a == {ci} mod {mod}")
    return _matvec_mod(W, ap, mod)


# ============================================================ parity matrix / f evaluation
def parity_matrix(k):
    """M[x,y] = popcount(x AND y) mod 2, x,y over the nonzero points of F_2^k."""
    n = (1 << k) - 1
    return [[bin(x & y).count("1") & 1 for y in range(1, n + 1)] for x in range(1, n + 1)]


def _fvec(P, k):
    """fvec[x-1] = f(x) mod 8 for x = 1 .. 2^k-1 (bit i <-> qubit label i+1)."""
    n = (1 << k) - 1
    fv = [0] * n
    for x in range(1, n + 1):
        xset = frozenset(i + 1 for i in range(k) if (x >> i) & 1)
        fv[x - 1] = eval_poly(P, xset)
    return fv


def _remap(P):
    """Relabel the qubits actually used by P to 1..k (T-count is relabel-invariant)."""
    qs = sorted({q for S in P for q in S})
    idx = {q: i + 1 for i, q in enumerate(qs)}
    return {frozenset(idx[q] for q in S): c for S, c in P.items()}, len(qs)


# ============================================================ min-weight coset leader
def _popcount_u64(a):
    """Vectorized SWAR popcount for a uint64 numpy array."""
    a = a.astype(np.uint64)
    m1 = np.uint64(0x5555555555555555)
    m2 = np.uint64(0x3333333333333333)
    m4 = np.uint64(0x0F0F0F0F0F0F0F0F)
    h = np.uint64(0x0101010101010101)
    one, two, four, fifty6 = (np.uint64(1), np.uint64(2), np.uint64(4), np.uint64(56))
    a = a - ((a >> one) & m1)
    a = (a & m2) + ((a >> two) & m2)
    a = (a + (a >> four)) & m4
    return (a * h) >> fifty6


def _min_coset_weight(base, basis):
    """min over v in span(basis) of popcount(base XOR v).  base/basis are <=63-bit ints."""
    # Materialises the whole 2^dim(V) coset by array doubling: 8*2^dim(V)
    # bytes.  Vectors live on n = 2^k - 1 bits, so k <= 6 fits uint64
    # (k=6: 63 bits, dim(V)=22 -> 32 MB); larger k overflows loudly.
    if not basis:
        return int(bin(base).count("1"))
    arr = np.array([base], dtype=np.uint64)
    for b in basis:
        arr = np.concatenate([arr, arr ^ np.uint64(b)])
    return int(_popcount_u64(arr).min())


# ============================================================ public API
def _rm_dim_formula(k):
    return sum(comb(k, i) for i in range(0, max(k - 3, 0)))       # sum_{i=0}^{k-4} C(k,i)


def _tcount_core(P, k, check_dim=True):
    """Return (tcount, dimV) for a polynomial on qubit labels 1..k."""
    if k == 0 or not P:
        return 0, 0
    M = parity_matrix(k)
    U, W, D = snf_z8(M)
    fv = _fvec(P, k)
    a0 = _solve_z8(U, W, D, fv)
    # The decoder checking its own answer, which is the reason the published
    # T-counts can be called exact -- so it runs under `python -O` too.
    if _matvec_mod(M, a0) != [v % MOD for v in fv]:
        raise RuntimeError(
            "Z_8 solve failed: a0 does not satisfy M a == fvec, so the coset "
            "being minimised over is not the right one")
    n = (1 << k) - 1
    free = [i for i in range(n) if D[i] % MOD == 0]
    basis = []
    for i in free:
        vec = 0
        for r in range(n):
            if W[r][i] & 1:
                vec |= (1 << r)
        basis.append(vec)
    if check_dim and len(basis) != _rm_dim_formula(k):
        raise RuntimeError(
            f"dim(V)={len(basis)} but the Reed--Muller formula gives "
            f"{_rm_dim_formula(k)} at k={k}: the coset lattice is wrong, so the "
            f"minimum weight over it would not be the T-count")
    base = 0
    for r in range(n):
        if a0[r] & 1:
            base |= (1 << r)
    return _min_coset_weight(base, basis), len(basis)


def tcount_rm(P, k):
    """EXACT minimal T-count of diag_x exp(i pi/4 f(x)), P = {frozenset(support): coeff mod 8},
    on qubit labels within 1..k.  Amy--Mosca minimum-weight-coset decoder."""
    return _tcount_core(P, k)[0]


def tcount_rm_decomp(decomp_str):
    """Convenience wrapper: 'T1 CS12' -> exact minimal T-count."""
    P, _ = poly_from_decomp(decomp_str)
    if not P:
        return 0
    Pr, k = _remap(P)
    return tcount_rm(Pr, k)


# ============================================================ self-test
if __name__ == "__main__":
    anchors = [("T1", 1), ("CS12", 3), ("CCZ123", 7),
               ("T1 T2 CS12", 1),      # ZZ  (Clifford-equivalent to a single T)
               ("T1 T2", 2),           # T (x) T
               ("T1 T2 T3 CCZ123", 4)] # T4  (degree 2, T-count 4)
    print("anchor checks (RM coset decoder must reproduce known minimal T-counts):")
    ok = True
    for decomp, exp in anchors:
        got = tcount_rm_decomp(decomp)
        ok &= (got == exp)
        print(f"  {decomp:20s} RM={got}  expected={exp}  {'PASS' if got == exp else '**FAIL**'}")
    print("  -> " + ("ALL PASS" if ok else "FAILURE"))

    print("\ndim(V) vs Reed-Muller formula sum_{i=0}^{k-4} C(k,i):")
    for k in range(1, 7):
        _, W, D = snf_z8(parity_matrix(k))
        dimV = sum(1 for i in range((1 << k) - 1) if D[i] % MOD == 0)
        exp = _rm_dim_formula(k)
        print(f"  k={k}: dim(V)={dimV}  formula={exp}  {'PASS' if dimV == exp else '**FAIL**'}")

    print("\nexact minimal T-counts, k=6 pure-CCZ (no upper bounds):")
    for decomp in ("CCZ123 CCZ124 CCZ125 CCZ126", "CCZ123 CCZ124 CCZ156",
                   "CCZ123 CCZ456", "CCZ123 CCZ145 CCZ246"):
        print(f"  {decomp:32s} -> {tcount_rm_decomp(decomp)}")