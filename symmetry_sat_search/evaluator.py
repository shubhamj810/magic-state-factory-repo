#!/usr/bin/env python3
"""
Exact evaluator for LLM-guided (FunSearch / AlphaEvolve / PatternBoost)
distillation-factory search.  No dependencies.

Search object
-------------
A candidate factory is a list of COLUMNS on N qubits: each column is an
iterable of qubit indices (the support of one parity-T rotation).  Qubits
0..k-1 are outputs, the rest are postselected checks.

Contract for a program-search pipeline
--------------------------------------
The evolved program must expose

    def factory(k: int) -> list[set[int]]

(or with extra arguments frozen).  The pipeline calls

    score = evaluate(factory(k), k, target='T', d_target=3)

and keeps programs with higher scores.  `evaluate` is exact and cheap
(polynomial for fixed d_target), and *shaped*: infeasible candidates get
graded penalties (number of violated parity constraints, distance
shortfall) so that evolution receives a gradient-like signal, while any
feasible factory strictly dominates every infeasible one, and among
feasible ones lower T-count wins.

Score layout
------------
  feasible   :  1_000_000 - 1000*n - N          (maximise)
  infeasible :  -1000*V - 100_000*S - n
      V = # violated parity (target) constraints of degree <= 3
      S = d_target - d(x)  (distance shortfall, 0 if d >= d_target)
"""
import itertools


def _distance(masks, k, dmax):
    """True circuit distance, capped at dmax (meet-in-the-middle)."""
    outm = (1 << k) - 1
    n = len(masks)

    # A weight-w fault flips w rotations.  It is undetected iff the XOR of
    # the faulted columns vanishes on every check, and damaging iff that XOR
    # is nonzero on the outputs -- i.e. iff it is a nonzero output-only mask.
    def bad(v):
        return v != 0 and (v & ~outm) == 0

    for v in masks:
        if bad(v):
            return 1
    pairval = {}
    for i, j in itertools.combinations(range(n), 2):
        v = masks[i] ^ masks[j]
        if bad(v):
            return 2
        pairval.setdefault(v, []).append((i, j))
    # w=3: any bad triple {i,a,b} with XOR t splits as single i + pair (a,b)
    # with masks[a]^masks[b] = masks[i]^t, so the pair table finds them all.
    if dmax >= 3:
        for t in range(1, 1 << k):
            for i in range(n):
                for (a, b) in pairval.get(masks[i] ^ t, []):
                    if i not in (a, b):
                        return 3
    # w=4: any bad quadruple splits into two disjoint pairs whose XORs differ
    # by t, so it is found as (pair in pairval[v^t]) x (pair in pairval[v]).
    if dmax >= 4:
        for t in range(1, 1 << k):
            for v, plist in pairval.items():
                for (a, b) in pairval.get(v ^ t, []):
                    for (c, d) in plist:
                        if len({a, b, c, d}) == 4:
                            return 4
    return dmax + 1          # ">= dmax+1"


def _violations(cols, N, k, target):
    """Number of violated degree-<=3 parity constraints.

    Every degree-1..3 monomial over ALL N qubits is constrained: parity must
    be odd exactly on the target's own monomial(s) and even everywhere else
    (in particular on everything touching a check)."""
    def par(qs):
        qs = set(qs)
        return sum(1 for c in cols if qs <= c) & 1

    V = 0
    for a in range(N):
        want = 1 if (target == 'T' and a < k) else 0
        V += par([a]) != want
    for a, b in itertools.combinations(range(N), 2):
        want = 1 if (target == 'CS' and (a, b) == (0, 1)) else 0
        V += par([a, b]) != want
    for a, b, c in itertools.combinations(range(N), 3):
        want = 1 if (target == 'CCZ' and (a, b, c) == (0, 1, 2)) else 0
        V += par([a, b, c]) != want
    return V


def evaluate(columns, k, target='T', d_target=3):
    """Exact shaped score of a candidate factory.  Higher is better."""
    cols = [frozenset(c) for c in columns]
    n = len(cols)
    if n == 0 or len(set(cols)) != n or any(len(c) == 0 for c in cols):
        return -10_000_000                      # malformed
    N = max(max(c) for c in cols) + 1
    N = max(N, k)
    masks = []
    for c in cols:
        m = 0
        for q in c:
            m |= 1 << q
        masks.append(m)

    V = _violations(cols, N, k, target)
    d = _distance(masks, k, d_target)
    S = max(0, d_target - d)

    if V == 0 and S == 0:
        return 1_000_000 - 1000 * n - N
    return -1000 * V - 100_000 * S - n


def params(columns, k, target='T', d_target=4):
    """Convenience: ([[n,k,d]], N, feasible?) of a candidate."""
    cols = [frozenset(c) for c in columns]
    N = max(max(c) for c in cols) + 1
    masks = []
    for c in cols:
        m = 0
        for q in c:
            m |= 1 << q
        masks.append(m)
    V = _violations(cols, N, k, target)
    d = _distance(masks, k, d_target)
    return (len(cols), k, d), N, V == 0


# --------------------------------------------------- output magic-state readout
# gate name for a degree-`deg` non-Clifford monomial at Clifford `level`
_GATE_NAME = {
    (2, 1): 'S',     (2, 2): 'CZ',
    (3, 1): 'T',     (3, 2): 'CS',  (3, 3): 'CCZ',
    (4, 1): 'sqrtT', (4, 2): 'CT',  (4, 3): 'CCS', (4, 4): 'CCCZ',
}


def output_data(columns, k, level=3):
    """The degree-1..level parities restricted to the OUTPUT block 0..k-1,
    reduced mod 2 -- i.e. the non-Clifford target data actually implemented on
    the outputs.  Returns {deg: [output-qubit tuples with odd parity]}."""
    cols = [set(c) for c in columns]

    def par(qs):
        qs = set(qs)
        return sum(1 for c in cols if qs <= c) & 1

    return {deg: [t for t in itertools.combinations(range(k), deg) if par(t)]
            for deg in range(1, level + 1)}


def describe_output(columns, k, level=3):
    """Read off which magic state the circuit outputs, from the output-block
    parities.  Returns (descriptor, magic_outputs, trivial_outputs):

      descriptor      e.g. 'T0 . CS02'  (0-indexed output qubits)
      magic_outputs   output qubits appearing in some non-Clifford term
      trivial_outputs output qubits in NO term -- they carry no magic and come
                      out as |+> spectators (the true output count is
                      k - len(trivial_outputs)).
    """
    D = output_data(columns, k, level)
    terms, involved = [], set()
    for deg in range(1, level + 1):
        name = _GATE_NAME.get((level, deg), f'C{deg - 1}Z')
        for t in D.get(deg, []):
            terms.append(name + ''.join(str(q) for q in t))
            involved |= set(t)
    descriptor = ' . '.join(terms) if terms else 'identity (no non-Clifford output)'
    trivial = [q for q in range(k) if q not in involved]
    return descriptor, sorted(involved), trivial


# ---------------------------------------------------------------- demo
if __name__ == '__main__':
    # seed program: the 15-to-1 factory as a program an LLM could evolve.
    def factory(k=1):
        # columns (1|v) for all nonzero v in F_2^4, output = qubit 0
        cols = []
        for m in range(1, 16):
            cols.append({0} | {1 + i for i in range(4) if m >> i & 1})
        return cols

    print('15-to-1 score:', evaluate(factory(), 1, 'T', 3))
    print('params       :', params(factory(), 1, 'T', 4))
