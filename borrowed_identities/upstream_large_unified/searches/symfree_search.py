"""Symmetry-free, targeted-output distillation-factory search — SINGLE FILE.

Solves the borrowed-identity condition directly for a chosen output (no symmetry ansatz); stage (ii), block
gluing, of unified_search.py. Run on its own it prints the smallest factory per k at l=2,3,4.

Run:    python3 searches/symfree_search.py   (from the repo root)

Self-contained: contains the borrowed-identity framework, the Z_{2^l} linear solver, the search,
N = top-level (pi/2^l, odd-coeff) magic count; Clifford (even-coeff) gates free;
distance computed over the T-gates only.
"""
from itertools import combinations


# ===================================================== borrowed-identity framework
def inputs(c, L):
    """Z(pi/2^L) inputs a rotation of coefficient c consumes; only rotations that are Clifford at level L are free."""
    base = 1 << max(L - 2, 1)
    r = c % base
    return min(r, base - r)


def is_noncliff(c, L):
    """True iff the rotation consumes at least one Z(pi/2^L) input (at L=4 the pi/8 rotations, c=2 mod 4, count)."""
    return inputs(c, L) > 0


def sigma(G, c, T):
    T = set(T)
    return sum(c[g] for g, S in enumerate(G) if T <= set(S))


def coeff(G, c, T, L):
    return ((-1) ** (len(T) + 1) * 2 ** (len(T) - 1) * sigma(G, c, T)) % (2 ** L)


def output_degree(Gf, cf, O, L):
    O = sorted(O); terms = {}
    for r in range(1, len(O) + 1):
        for T in combinations(O, r):
            v = coeff(Gf, cf, T, L)
            if v:
                terms[T] = v
    return (max((len(T) for T in terms), default=0)), terms


def distance(Gf, O, N):
    """min #T-gates whose check-supports XOR to 0 but output-supports don't (GF(2) min-distance)."""
    C = [q for q in range(N) if q not in set(O)]
    chk = [frozenset(set(S) & set(C)) for S in Gf]
    out = [frozenset(set(S) & set(O)) for S in Gf]
    for r in range(1, len(Gf) + 1):
        for E in combinations(range(len(Gf)), r):
            cc = set(); oo = set()
            for g in E:
                cc ^= chk[g]; oo ^= out[g]
            if not cc and oo:
                return r
    return None


def classify(Gf, cf, O, N, L):
    deg, _ = output_degree(Gf, cf, O, L)
    Tg = [s for s, c in zip(Gf, cf) if is_noncliff(c, L)]          # top-level magic gates only
    return dict(k=len(O), N=sum(inputs(c, L) for c in cf), gates=len(Gf), degree=deg, distance=distance(Tg, O, N))


GATE_BY_SIZE = {2: {1: "S", 2: "CZ"}, 3: {1: "T", 2: "CS", 3: "CCZ"},
                4: {1: "√T", 2: "CT", 3: "CCS", 4: "CCCZ"}}


# ===================================================== Z_{2^L} linear solver (2-adic lift)
def gf2_solve(rows, rhs, nvars):
    A = [[m, b & 1] for m, b in zip(rows, rhs)]
    pivc, r = {}, 0
    for col in range(nvars):
        bit = 1 << col
        piv = next((i for i in range(r, len(A)) if A[i][0] & bit), None)
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        for i in range(len(A)):
            if i != r and (A[i][0] & bit):
                A[i][0] ^= A[r][0]; A[i][1] ^= A[r][1]
        pivc[col] = r; r += 1
    if any(A[i][0] == 0 and A[i][1] == 1 for i in range(len(A))):
        return None
    part = 0
    for col, rr in pivc.items():
        if A[rr][1]:
            part |= (1 << col)
    null = []
    for fc in (c for c in range(nvars) if c not in pivc):
        v = 1 << fc
        for col, rr in pivc.items():
            if A[rr][0] & (1 << fc):
                v |= (1 << col)
        null.append(v)
    return part, null


def solve_graded(masks, rs, ms, nvars, L, varlists):
    x = [0] * nvars; mod = 1 << L; nulls = []
    for b in range(L):
        rows, rhs = [], []
        for i in range(len(masks)):
            if ms[i] <= b:
                continue
            cur = sum(x[j] for j in varlists[i])
            res = (rs[i] - cur) % (1 << ms[i])
            if res % (1 << b) != 0:
                return None
            rows.append(masks[i]); rhs.append((res >> b) & 1)
        sol = gf2_solve(rows, rhs, nvars)
        if sol is None:
            return None
        part, null = sol; nulls.append(null)
        for j in range(nvars):
            if part & (1 << j):
                x[j] = (x[j] + (1 << b)) % mod
    for i in range(len(masks)):
        if sum(x[j] for j in varlists[i]) % (1 << ms[i]) != rs[i] % (1 << ms[i]):
            return None
    return x, nulls


def _ok(rs, ms, x, varlists):
    return all(sum(x[j] for j in varlists[i]) % (1 << ms[i]) == rs[i] % (1 << ms[i])
               for i in range(len(varlists)))


def reduce_support(rs, ms, x, nulls, nvars, L, varlists):
    """Greedily subtract homogeneous kernel vectors to minimize the T-count (then total gates)."""
    mod = 1 << L; zero = [0] * len(varlists); gens = []
    for b, NS in enumerate(nulls):
        for v in NS:
            g = [((1 << b) if (v >> j) & 1 else 0) for j in range(nvars)]
            if _ok(zero, ms, g, varlists):
                gens.append(g)
    cost = lambda v: (sum(inputs(t % mod, L) for t in v), sum(1 for t in v if t % mod))
    improved = True
    while improved:
        improved = False
        for g in gens:
            for a in range(1, mod):
                cand = [(x[j] + a * g[j]) % mod for j in range(nvars)]
                if cost(cand) < cost(x) and _ok(rs, ms, cand, varlists):
                    x = cand; improved = True; break
            if improved:
                break
    return x


# ===================================================== the search
def _all_weights(qs):
    out = []; qs = sorted(qs)
    for r in range(1, len(qs) + 1):
        for s in combinations(qs, r):
            out.append(frozenset(s))
    return out


def solve_binding(block_sizes, ncheck, L):
    """Fix output = all-weights blocks (block sizes); SOLVE for the check-coupling gates."""
    k = sum(block_sizes); O = list(range(k)); C = list(range(k, k + ncheck)); n = k + ncheck
    blocks, off = [], 0
    for sz in block_sizes:
        blocks.append(list(range(off, off + sz))); off += sz
    oo = [g for blk in blocks for g in _all_weights(blk)]
    allq = O + C
    cand = [frozenset(s) for r in range(1, len(allq) + 1)
            for s in combinations(allq, r) if set(s) & set(C)]
    cand.sort(key=len); nvars = len(cand)
    masks, rs, ms, varlists = [], [], [], []
    for t in range(1, L + 1):
        mT = L - t + 1
        for T in combinations(allq, t):
            Ts = frozenset(T)
            vl = [i for i, g in enumerate(cand) if Ts <= g]
            mask = 0
            for i in vl:
                mask |= (1 << i)
            sig_oo = sum(1 for g in oo if Ts <= g)
            masks.append(mask); rs.append((-sig_oo) % (1 << mT)); ms.append(mT); varlists.append(vl)
    sol = solve_graded(masks, rs, ms, nvars, L, varlists)
    if sol is None:
        return None
    x, nulls = sol
    x = reduce_support(rs, ms, x, nulls, nvars, L, varlists)
    gates = [(cand[i], x[i] % (1 << L)) for i in range(nvars) if x[i] % (1 << L) != 0]
    return dict(gates=gates, O=O, n=n)


def _partitions(k, maxpart):
    if k == 0:
        yield []; return
    for p in range(min(k, maxpart), 0, -1):
        for rest in _partitions(k - p, p):
            yield [p] + rest


def search(L, k_max=6, max_check=4, n_max=10):
    """Sweep output block-partitions; solve each; return verified d=2 factories."""
    out = []
    for k in range(2, k_max + 1):
        for parts in _partitions(k, L):
            for c in range(1, max_check + 1):
                if k + c > n_max:
                    break
                r = solve_binding(parts, c, L)
                if r is None:
                    continue
                Gf = [g for g, _ in r["gates"]]; cf = [cc for _, cc in r["gates"]]
                info = classify(Gf, cf, set(r["O"]), r["n"], L)
                if info["distance"] != 2 or info["degree"] < 1:
                    continue
                out.append(dict(parts=parts, **info)); break        # smallest check register
    return out


# ===================================================== run + plot
def _comp(parts, gate_by_size):
    from collections import Counter
    c = Counter(parts); s = []
    for sz in sorted(c, reverse=True):
        g = gate_by_size.get(sz, "?")
        s.append(g if c[sz] == 1 else "%d×%s" % (c[sz], g))
    return "+".join(s)


if __name__ == "__main__":
    # standalone run: list the smallest block-gluing factory per k at each level
    for L in (2, 3, 4):
        best = {}
        for r in search(L):
            if r["k"] not in best or r["N"] < best[r["k"]]["N"]:
                best[r["k"]] = r
        print("l=%d: " % L + ", ".join("[[%d,%d,%d]]" % (r["N"], r["k"], r["distance"]) for k, r in sorted(best.items())))
