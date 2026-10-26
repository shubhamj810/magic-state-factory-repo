"""SAT certifier: is there a distance-2 borrowed-identity factory for a target state with fewer than N* inputs?

The search is over ALL Z(pi/2^l) parity rotations on n qubits (no symmetry assumed). A factory must
  (i)   leave the checks in |+> up to a diagonal Clifford: every phase monomial touching a check is Clifford;
  (ii)  deposit the target on the outputs up to a diagonal Clifford;
  (iii) have distance >= 2: every input-consuming rotation touches a check, enforced by never placing a
        rotation on output qubits alone.
UNSAT for N < N* on every n <= n_max certifies that N* is the smallest such factory on up to n_max qubits.
Distance is d=2 only; the output frame is fixed by the target, since CNOTs on the outputs preserve N and d.
"""
import os, sys, time, argparse
from itertools import combinations

import z3

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from unified_search import cliff_exp, inputs  # noqa: E402


def poly_coeffs(target):
    return {frozenset(T): c for T, c in target.items()}


def certify(target, k, n, L, N_star, time_limit=600.0, max_weight=None, symmetry=True, lex_prefix=64):
    """Return ('sat', N, gates) with N < N_star, 'unsat', or 'unknown' (timeout)."""
    mod = 1 << L
    r = n - k
    out = frozenset(range(k))
    supports = [frozenset(S) for w in range(1, n + 1) for S in combinations(range(n), w)
                if (max_weight is None or w <= max_weight) and not frozenset(S) <= out]
    s = z3.Solver()
    s.set("timeout", int(time_limit * 1000))
    c = {S: z3.BitVec("c_" + "_".join(map(str, sorted(S))), L) for S in supports}
    target = poly_coeffs(target)

    def coeff_sum(T):
        terms = [c[S] for S in supports if T <= S]
        return z3.Sum(terms) if terms else z3.BitVecVal(0, L)

    for t in range(1, min(n, L) + 1):
        for T in combinations(range(n), t):
            T = frozenset(T)
            e = cliff_exp(t, L)
            m = (1 << e) - 1
            lhs = ((-1) ** (t + 1)) * (1 << (t - 1))
            expr = coeff_sum(T) * z3.BitVecVal(lhs % mod, L)
            if T <= out:
                want = target.get(T, 0) % mod
                s.add((expr & m) == (want & m))
            else:
                s.add((expr & m) == 0)

    base = 1 << max(L - 2, 1)
    def cost_of(x):
        rem = z3.URem(x, z3.BitVecVal(base, L))
        terms = z3.IntVal(0)
        for v in range(1, base):
            terms = z3.If(rem == v, z3.IntVal(min(v, base - v)), terms)
        return terms
    cost = {S: cost_of(c[S]) for S in supports}
    s.add(z3.Sum(list(cost.values())) < N_star)

    if symmetry:
        # Check qubits are interchangeable: swapping two of them maps solutions to solutions. Lex-leader
        # constraints X <=lex swap(X) for adjacent checks keep at least one member of every orbit.
        idx = {S: i for i, S in enumerate(supports)}
        for q in range(k, n - 1):
            swap = lambda S: frozenset((q + 1 if x == q else q if x == q + 1 else x) for x in S)
            moved = [S for S in supports if swap(S) != S]
            xs = [c[S] for S in moved][:lex_prefix]
            ys = [c[swap(S)] for S in moved][:lex_prefix]
            le = z3.BoolVal(True)
            for x, y in reversed(list(zip(xs, ys))):
                le = z3.Or(z3.ULT(x, y), z3.And(x == y, le))
            s.add(le)

    res = s.check()
    if res == z3.sat:
        m = s.model()
        gates = [(S, m[c[S]].as_long() % mod) for S in supports if m[c[S]] is not None and m[c[S]].as_long() % mod]
        N = sum(inputs(cc, L) for _, cc in gates)
        return "sat", N, gates
    return ("unsat", None, None) if res == z3.unsat else ("unknown", None, None)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="CCZ012,CS34")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--N", type=int, default=18)
    ap.add_argument("--l", type=int, default=3)
    ap.add_argument("--nmin", type=int, default=6)
    ap.add_argument("--nmax", type=int, default=8)
    ap.add_argument("--time", type=float, default=600.0)
    a = ap.parse_args()
    GEN = {"T": 1, "CS": 2, "CCZ": 4}
    tgt = {}
    for tok in a.target.split(","):
        name = tok.rstrip("0123456789"); qs = frozenset(int(ch) for ch in tok[len(name):])
        tgt[qs] = (tgt.get(qs, 0) + GEN[name]) % (1 << a.l)
    for n in range(a.nmin, a.nmax + 1):
        t = time.time()
        res, N, _ = certify(tgt, a.k, n, a.l, a.N, a.time)
        print(f"n={n}: {res}{'' if N is None else f' N={N}'}  ({time.time() - t:.1f}s)", flush=True)
