"""Output-state classification shared by the two-group and symmetry-free
catalogue builders. Built directly on classification code from the
`sj-magic-state-factory-searches` companion repository (its `l=3`-only
distance-3 extension of this project), copied/adapted here:

  - `tcount.py`  (Amy-Mosca / Reed-Muller minimum-weight-coset decoder):
    the EXACT minimal T-count of the whole deposited state, at l=3 only.
  - the "FLAG 2" GL(k,2) x shift reduction (`audit_flag2.py`, from that
    repo's `2_entangled_search/`, pasted directly into this module as
    `essential_and_reduced`/`separable_components`): the Clifford-reduced
    (genuine_degree, essential_dimension) of the deposited state, generalized
    here from l=3 (mod 8) to any l (mod 2^l), plus a decomposition into
    separable components (e.g. "CS+CCZ") by reducing to the best GL(k,2)
    frame first and reading off connected components there -- unlike a
    naive identity-frame connected-components read, which can misreport a
    state that a CNOT frame would simplify (this is exactly the bug FLAG 2's
    own docstring calls out in its predecessor: "reported pure CS as T-count 0
    and collapsed CS.CCZ to degree 2. Both wrong.").

A monomial of size r is *genuine* iff its coefficient is nonzero mod 2^r --
NOT "odd", which is a different (and for this purpose wrong) test; see the
module-level note in the git history of this file for the concrete
counterexample ([[4,2,2]], the Iceberg code, which an "odd" test misreads as
Clifford).
"""
from itertools import combinations, permutations, product
import random

from tcount import NotInGroup, tcount_rm, _remap

GATE_BY_SIZE = {2: {1: "S", 2: "CZ"}, 3: {1: "T", 2: "CS", 3: "CCZ"},
                4: {1: "sqrtT", 2: "CT", 3: "CCS", 4: "CCCZ"}}


# --------------------------------------------------------------- shared gate-list -> polynomial
def sigma(G, c, T):
    Tset = set(T)
    return sum(cc for supp, cc in zip(G, c) if Tset <= supp)


def coeff(G, c, T, L):
    return ((-1) ** (len(T) + 1) * 2 ** (len(T) - 1) * sigma(G, c, T)) % (2 ** L)


def phase_polynomial(Gf, cf, O, L):
    """{frozenset(support): coeff mod 2^L} restricted to output set O, remapped
    to 0..k-1 in O's sorted order."""
    O = sorted(O)
    idx = {q: i for i, q in enumerate(O)}
    mod = 1 << L
    P = {}
    for r in range(1, len(O) + 1):
        for T in combinations(O, r):
            c = coeff(Gf, cf, T, L) % mod
            if c:
                P[frozenset(idx[q] for q in T)] = c
    return P


# --------------------------------------------------- FLAG 2: GL(k,2) x shift reduction (adapted)
def genuine_monomials(P):
    """{T: coeff} for monomials with coeff != 0 mod 2^|T| -- a genuine size-|T|
    resource (an even coefficient is a free, lower-level Clifford dressing,
    not real magic)."""
    return {S: c for S, c in P.items() if c % (1 << len(S))}


def _eval_poly(P, xset, mod):
    return sum(c for S, c in P.items() if S <= xset) % mod


def _phase_table(P, qs, mod):
    tab = {}
    for bits in product((0, 1), repeat=len(qs)):
        xset = frozenset(qs[i] for i, b in enumerate(bits) if b)
        tab[bits] = _eval_poly(P, xset, mod)
    return tab


def _gl_matrices(k):
    """All invertible k x k matrices over F2 (columns as bit-ints). Exact
    enumeration -- only call for small k (k<=4 here)."""
    cols = list(range(1, 1 << k))
    out = []
    for combo in permutations(cols, k):
        basis = []
        for v in combo:
            w = v
            for b in basis:
                w = min(w, w ^ b)
            if w:
                basis.append(w)
        if len(basis) == k:
            out.append(combo)
    return out


def _apply_linear(tab, qs, M):
    k = len(qs)
    newtab = {}
    for bits in product((0, 1), repeat=k):
        y = 0
        for j in range(k):
            if bits[j]:
                y ^= M[j]
        ybits = tuple((y >> i) & 1 for i in range(k))
        newtab[bits] = tab[ybits]
    return newtab


def _tab_to_poly(tab, qs, mod):
    """Mobius inversion: recover the multilinear coeff dict mod `mod` from a truth table."""
    k = len(qs)
    P = {}
    for mask in range(1, 1 << k):
        T = frozenset(qs[i] for i in range(k) if (mask >> i) & 1)
        s, sub = 0, mask
        while True:
            xbits = tuple((sub >> i) & 1 for i in range(k))
            popc = bin(sub).count("1")
            s += ((-1) ** (bin(mask).count("1") - popc)) * tab[xbits]
            if sub == 0:
                break
            sub = (sub - 1) & mask
        if s % mod:
            P[T] = s % mod
    return P


# Practical GL(k,2) sampling budget for k>=5 (exact enumeration is only
# feasible to k<=4, |GL(4,2)|=20160). FLAG 2 itself defaults to 60,000 samples
# (400,000 tries); at k=6/7 that took 20-60s per call, which does not scale to
# sweeping the hundreds of k>=6 rows in the two-group catalogue (over an hour
# projected). Reduced here for practicality -- still a documented, correct
# UPPER bound (can only overstate degree/essential_dim, never understate it),
# just a looser one; override back up for a one-off high-precision check.
_GL_SAMPLE_CAP = 4_000
_GL_SAMPLE_TRIES = 40_000
_GL_SEED = 12345


def essential_and_reduced(P, qs, L):
    """Minimize (essential_dim, degree) over GL(k,2) x shift, at level L (mod
    2^L). essential_dim = # qubits the genuine monomials touch in the best
    frame found; degree = the largest genuine monomial size there. Exact for
    k<=4; a documented random-frame upper bound (never an understatement)
    for k>=5. Returns (essential_dim, degree, best_genuine, exact)."""
    k = len(qs)
    mod = 1 << L
    tab = _phase_table(P, qs, mod)

    def score(pp):
        g = genuine_monomials(pp)
        touched = {q for S in g for q in S}
        return (len(touched), max((len(S) for S in g), default=0), g)

    best = None
    if k <= 4:
        Ms = _gl_matrices(k)
        exact = True
    else:
        rnd = random.Random(_GL_SEED)
        Ms = [tuple(1 << i for i in range(k))]
        tries = 0
        while len(Ms) < _GL_SAMPLE_CAP and tries < _GL_SAMPLE_TRIES:
            cols = [rnd.randrange(1, 1 << k) for _ in range(k)]
            basis = []
            for v in cols:
                w = v
                for b in basis:
                    w = min(w, w ^ b)
                if w:
                    basis.append(w)
            if len(basis) == k:
                Ms.append(tuple(cols))
            tries += 1
        exact = False
    for M in Ms:
        nt = _apply_linear(tab, qs, M)
        pp = _tab_to_poly(nt, qs, mod)
        sc = score(pp)
        if best is None or sc[:2] < best[:2]:
            best = sc
    ess, red_deg, g = best
    return ess, red_deg, g, exact


def separable_components(g, qs):
    """Partition qs into connected components under the genuine-monomial hypergraph."""
    parent = {q: q for q in qs}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for S in g:
        Sl = list(S)
        for i in range(1, len(Sl)):
            parent[find(Sl[0])] = find(Sl[i])
    comps = {}
    for q in qs:
        comps.setdefault(find(q), set()).add(q)
    return list(comps.values())


_DECOMP_TERM_CAP = 4   # per-component: list every genuine monomial up to this
                       # many; a denser component (e.g. a fully-symmetric k=7
                       # two-group state, which can have ~70 simultaneously
                       # genuine monomials) gets a summary instead, since
                       # listing all of them defeats the point of a readable
                       # label -- the per-block essential_dim/degree numbers
                       # still fully describe it either way.


def decompose(g, touched, L):
    """Qubit-indexed decomposition string (e.g. "CS01+CS02", "CCZ012") of the
    best-frame genuine monomials `g`, one connected component at a time: one
    term per genuine monomial in that component, named by its size and the
    specific (best-frame) qubits it acts on -- not just an aggregate count,
    so e.g. two CS terms sharing a qubit ("CS01+CS02", one 3-qubit essential
    block) reads differently from two disjoint ones ("CS01+CS23", two
    independent 2-qubit blocks). A component with more than
    `_DECOMP_TERM_CAP` genuine monomials (a densely entangled block) is
    summarized as its top-degree gate name over its touched qubits plus a
    count, e.g. "CCZ0123456(35+21 terms)", rather than spelled out in full.

    Qubit labels are 0-indexed positions in the REDUCED frame found by
    `essential_and_reduced` (the touched qubits, renumbered in sorted order),
    not necessarily the original circuit's physical output wires -- the whole
    point of the frame search is that a CNOT change of basis on the outputs
    can be needed to see the genuine content at all.
    """
    if not g:
        return "trivial"
    touched = sorted(touched)
    relabel = {q: i for i, q in enumerate(touched)}
    comps = separable_components(g, touched)
    parts = []
    for comp in comps:
        gc = {S: c for S, c in g.items() if S <= comp}
        if not gc:
            continue
        if len(gc) <= _DECOMP_TERM_CAP:
            terms = []
            for S in gc:
                name = GATE_BY_SIZE.get(L, {}).get(len(S), f"deg{len(S)}")
                qubits = "".join(str(relabel[q]) for q in sorted(S))
                terms.append((len(S), qubits, f"{name}{qubits}"))
            terms.sort(key=lambda t: (-t[0], t[1]))
            parts.append((max(t[0] for t in terms), "+".join(t[2] for t in terms)))
        else:
            comp_qubits = "".join(str(relabel[q]) for q in sorted(comp))
            top = max(len(S) for S in gc)
            name = GATE_BY_SIZE.get(L, {}).get(top, f"deg{top}")
            by_size = {}
            for S in gc:
                by_size[len(S)] = by_size.get(len(S), 0) + 1
            counts = "+".join(str(by_size[sz]) for sz in sorted(by_size, reverse=True))
            parts.append((top, f"{name}{comp_qubits}({counts} terms)"))
    parts.sort(key=lambda p: (-p[0], p[1]))
    return "+".join(p[1] for p in parts)


# ------------------------------------------------------------------------- public entry point
def classify(Gf, cf, O, L):
    """Full classification of a factory's deposited output state.

    Returns dict(degree, essential_dim, degree_note, t_count, t_count_note,
    decomposition). `degree`/`essential_dim`/`decomposition` come from the
    GL(k,2) x shift reduction above; `t_count` is the independent exact
    Reed-Muller-coset answer from tcount.py (l=3 only).
    """
    P = phase_polynomial(Gf, cf, O, L)
    k = len(O)
    qs = list(range(k))
    if not P:
        ess, deg, g, exact = 0, 0, {}, True
    else:
        ess, deg, g, exact = essential_and_reduced(P, qs, L)
    degree_note = None if exact else (
        f"essential_dim/degree is an UPPER BOUND: |GL({k},2)| too large for exact "
        f"enumeration; min over identity + up to {_GL_SAMPLE_CAP:,} random frames")
    touched = {q for S in g for q in S}
    decomposition = decompose(g, touched, L)
    t_count, t_count_note = (None, "only defined at l=3")
    if L == 3:
        if not P:
            t_count, t_count_note = 0, None
        else:
            Pr, kk = _remap({S: c for S, c in P.items()})
            if kk > 6:
                # tcount.py's exact decoder packs 2^k-1 bits into a uint64
                # (its own docstring: "k<=6 fits uint64... larger k overflows
                # loudly"). k=7 needs 127 bits and does exactly that.
                t_count, t_count_note = None, (
                    f"exact T-count decoder only supports k<=6 (uint64 vector "
                    f"packing); this state touches {kk} qubits")
            else:
                try:
                    t_count, t_count_note = tcount_rm(Pr, kk), None
                except NotInGroup:
                    t_count, t_count_note = None, "gate not in the pi/4 parity-rotation group (needs ancillas)"
    return dict(degree=deg, essential_dim=ess, degree_note=degree_note,
                t_count=t_count, t_count_note=t_count_note,
                decomposition=decomposition)
