#!/usr/bin/env python3
"""
Slot-ansatz factory search, v2.

Upgrades over slot_search_v1.py:
  * blocks may be fully symmetric ('S', lam) or cyclic ('C', lam);
    cyclic orbits = necklace classes, so far fewer gates per orbit and
    a much richer label vocabulary (this is what CCZ needs);
  * exact T-count OPTIMISATION per geometry with CP-SAT (OR-Tools):
    the at-most-one slot rule, the XOR parity constraints and the
    objective are native, and the solver proves optimality;
  * optional distance-4 mode: label triples that can cancel on every
    check block are excluded unless their output patterns XOR to zero
    (a sound over-approximation of the fatal-triple condition);
  * fast exact verifier (meet-in-the-middle) for true distance <= 4.

Run ``python slot_search.py --help`` for the command-line interface.

(slot_search_v1.py itself is superseded and not shipped in this repository.)
"""
import argparse
import itertools
import re
from math import comb
from ortools.sat.python import cp_model


# ---------------------------------------------------------------- orbits
def _perm_group_orbits(lam, gens):
    """Orbits of an explicit permutation group (given by generator perms,
    each a tuple of length lam mapping i->perm[i]) on all subsets of
    range(lam), via BFS closure. gens=[] gives the trivial group (every
    subset its own singleton orbit) -- used to de-symmetrize a block."""
    def apply_perm(mask, perm):
        m2 = 0
        for i in range(lam):
            if mask >> i & 1:
                m2 |= 1 << perm[i]
        return m2
    full = 1 << lam
    seen = [False] * full
    orbs = []
    for start in range(full):
        if seen[start]:
            continue
        seen[start] = True
        comp = [start]
        stack = [start]
        while stack:
            cur = stack.pop()
            for g in gens:
                nxt = apply_perm(cur, g)
                if not seen[nxt]:
                    seen[nxt] = True
                    comp.append(nxt)
                    stack.append(nxt)
        orbs.append(tuple(frozenset(i for i in range(lam) if m >> i & 1)
                          for m in sorted(comp)))
    return orbs


def block_orbits(kind, lam, gens=None):
    """List of orbits; each orbit is a tuple of frozensets (local coords)."""
    if kind == 'S':
        return [tuple(frozenset(c) for c in itertools.combinations(range(lam), w))
                for w in range(lam + 1)]
    if kind == 'C':
        def canon(mask):
            best = mask
            for s in range(1, lam):
                m = ((mask << s) | (mask >> (lam - s))) & ((1 << lam) - 1)
                best = min(best, m)
            return best
        classes = {}
        for mask in range(1 << lam):
            classes.setdefault(canon(mask), set()).add(mask)
        orbs = []
        for rep in sorted(classes):
            orbs.append(tuple(frozenset(i for i in range(lam) if m >> i & 1)
                              for m in sorted(classes[rep])))
        return orbs
    if kind == 'P':
        return _perm_group_orbits(lam, gens or [])
    raise ValueError(kind)


def orbit_contain_count(orbit, T):
    """Number of sets in the orbit containing T (callers reduce mod 2)."""
    return sum(1 for S in orbit if T <= S)


# ---------------------------------------------------- monomial orbit reps
def block_monomial_reps(kind, lam, gens=None):
    """Representative point-sets of size 0..3 per symmetry class."""
    if kind == 'S':
        return [frozenset(range(t)) for t in range(min(3, lam) + 1)]
    if kind == 'C':
        def canon(mask):
            best = mask
            for s in range(1, lam):
                m = ((mask << s) | (mask >> (lam - s))) & ((1 << lam) - 1)
                best = min(best, m)
            return best
        reps = set()
        for t in range(min(3, lam) + 1):
            for c in itertools.combinations(range(lam), t):
                m = 0
                for i in c:
                    m |= 1 << i
                reps.add(canon(m))
        return [frozenset(i for i in range(lam) if m >> i & 1)
                for m in sorted(reps)]
    if kind == 'P':
        reps = []
        for orb in _perm_group_orbits(lam, gens or []):
            small = [S for S in orb if len(S) <= 3]
            if small:
                reps.append(small[0])
        return reps
    raise ValueError(kind)


# ---------------------------------------------------------------- model
class Geometry:
    """Slot ansatz on k outputs plus one check block per entry of ``blocks``.

    A *label* picks one orbit index per block; together with an output
    pattern P it defines a slot of ``label_cost`` columns, namely
    P ∪ (one member set per block of the chosen orbits).  A slot enters the
    circuit wholly or not at all, so the circuit is a union of full orbits
    and is invariant under the block symmetry groups by construction.  The
    all-empty-check label is excluded: its columns would be output-only,
    i.e. weight-1 undetectable faults.
    """
    def __init__(self, k, blocks):
        self.k = k
        self.blocks = blocks           # [('S',4), ('C',7), ('P',lam,gens), ...]
        self.orbits = [block_orbits(*b) for b in blocks]
        self.mreps = [block_monomial_reps(*b) for b in blocks]
        self.N = k + sum(b[1] for b in blocks)
        # labels: one orbit index per block, not all-empty
        idx = [range(len(o)) for o in self.orbits]
        self.labels = [lab for lab in itertools.product(*idx)
                       if any(len(self.orbits[i][j][0]) > 0
                              for i, j in enumerate(lab))]

    def label_cost(self, lab):
        """Columns generated by one slot of this label (product of orbit sizes)."""
        c = 1
        for i, j in enumerate(lab):
            c *= len(self.orbits[i][j])
        return c

    def monomials(self):
        """Degree-1..3 monomial classes (Q, Ts): Q an output subset, Ts one
        representative point-set per block.  One representative per
        block-symmetry class suffices: the circuit is a union of full
        orbits, so monomial parities are constant on symmetry classes."""
        outs = list(range(self.k))
        mons = []
        for qs in range(0, min(3, self.k) + 1):
            for Q in itertools.combinations(outs, qs):
                pools = []
                for reps in self.mreps:
                    pools.append([T for T in reps if len(T) <= 3 - qs])
                for combo in itertools.product(*pools):
                    deg = qs + sum(len(T) for T in combo)
                    if 1 <= deg <= 3:
                        mons.append((Q, combo))
        return mons

    def coeff(self, lab, mon):
        """#gates of a type with this label containing the monomial, mod 2
        (output condition handled by caller)."""
        _, Ts = mon
        c = 1
        for i, j in enumerate(lab):
            c *= orbit_contain_count(self.orbits[i][j], Ts[i])
            if c == 0:
                return 0
        return c & 1


def tri_cancel_block(orbit1, orbit2, orbit3):
    """Exists a in O1, b in O2, c in O3 with a^b^c = empty (as sets)."""
    o3 = set(orbit3)
    for a in orbit1:
        for b in orbit2:
            if frozenset(a ^ b) in o3:
                return True
    return False


# ------------------------------------------------ output-pattern restrictions
def target_monomials(k, target):
    """Return the nonzero degree-<=3 output monomials of ``target``.

    Custom targets use the same representation as ``solve``/``verify``: an
    iterable of frozensets (or other iterables) of output indices.  Named
    ``'T'`` means a product T on all k outputs.
    """
    if not isinstance(target, str):
        out = frozenset(frozenset(Q) for Q in target)
    elif target == 'T':
        out = frozenset(frozenset({i}) for i in range(k))
    elif target == 'CS':
        if k < 2:
            raise ValueError('CS needs at least two outputs')
        out = frozenset({frozenset({0, 1})})
    elif target == 'CCZ':
        if k < 3:
            raise ValueError('CCZ needs at least three outputs')
        out = frozenset({frozenset({0, 1, 2})})
    else:
        raise ValueError(f'unknown target {target!r}')
    if any(not Q or len(Q) > 3 or any(i < 0 or i >= k for i in Q)
           for Q in out):
        raise ValueError('target monomials must be nonempty output subsets of degree <= 3')
    return out


def canonical_phase_support(k, target, include_zero=False):
    """Canonical parity-vector support Y for a degree-<=3 target.

    A monomial gate on Q is the XOR (over phase-polynomial coefficients) of
    every nonempty parity vector P subseteq Q.  Products of gates combine by
    symmetric difference.  This gives a sparse, canonical support even when
    k>3, where the target equations no longer determine exact-label parities.
    """
    support = set()
    for Q in target_monomials(k, target):
        q = sorted(Q)
        for size in range(1, len(q) + 1):
            for P in itertools.combinations(q, size):
                P = tuple(P)
                if P in support:
                    support.remove(P)
                else:
                    support.add(P)
    if include_zero:
        support.add(())
    return tuple(sorted(support, key=lambda P: (len(P), P)))


def _normalise_patterns(k, patterns):
    """Normalise explicit output patterns (index iterables or bit masks)."""
    out = set()
    for P in patterns:
        if isinstance(P, int):
            if P < 0 or P >= (1 << k):
                raise ValueError(f'output-pattern mask {P} does not fit k={k}')
            P = tuple(i for i in range(k) if P >> i & 1)
        else:
            P = tuple(sorted(set(P)))
        if any(i < 0 or i >= k for i in P):
            raise ValueError(f'output pattern {P} does not fit k={k}')
        out.add(P)
    if not out:
        raise ValueError('at least one output pattern must be allowed')
    return tuple(sorted(out, key=lambda P: (len(P), P)))


# --------------------------------------------------- Reed--Muller slice domains
def _rm_rminus3_spectrum(r):
    """Exact weight spectrum of RM(r-3,r), for the small cases and r>=6."""
    if r < 3:
        return {0}
    if r == 3:
        return {0, 8}
    if r == 4:
        return {0, 8, 16}
    if r == 5:
        # NB: strict superset of the true RM(2,5) spectrum
        # {0,8,12,16,20,24,32} -- 14 and 18 are not codeword weights.  A
        # superset only weakens pruning; it can never discard a factory.
        return {0, 8, 12, 14, 16, 18, 20, 24, 32}
    length = 1 << r
    return ({0, 8, length - 8, length}
            | set(range(12, length - 11, 2)))


def rm_total_counts(r, max_count=None):
    """Sound total-column domains from the check-side RM(r-4,r) word.

    A distance-three factory with ``n`` columns has augmented check-support
    weight ``n + (n mod 2)``.  For r>=8 this uses the exact Carlet--Sole
    spectrum.  At r=4,5 the spectra are elementary.  At r=6 the quadratic-form
    rank classification gives the exact RM(2,6) spectrum.  RM(3,7) is doubly
    even, so at r=7 we combine that divisibility with the exact sub-32 spectrum
    and conservatively admit every multiple of four from 32 upward.  The r=7
    domain is a deliberate superset, so it can weaken pruning but can never
    discard a factory.
    """
    length = 1 << r
    if max_count is None:
        max_count = length - 1
    max_count = min(max_count, length - 1)

    def allowed_augmented(weight):
        if r < 4:
            return weight == 0
        if r == 4:
            return weight in (0, 16)
        if r == 5:
            return weight in (0, 16, 32)
        if r == 6:
            return weight in (0, 16, 24, 28, 32, 36, 40, 48, 64)
        if r == 7:
            return weight in (0, 16, 24, 28) or (
                32 <= weight <= length and weight % 4 == 0
            )
        return (
            weight in (0, 16, 24, length - 24, length - 16, length)
            or (28 <= weight <= length - 28 and weight % 2 == 0)
        )

    return tuple(n for n in range(max_count + 1)
                 if allowed_augmented(n + (n & 1)))


def rm_linear_slice_counts(r, max_count=None):
    """Allowed unaugmented sizes of an affine output hyperplane cell.

    The augmented size is w+(w mod 2) and must be in RM(r-3,r).
    """
    if max_count is None:
        max_count = (1 << r) - 1
    spec = _rm_rminus3_spectrum(r)
    return tuple(w for w in range(max_count + 1) if w + (w & 1) in spec)


def rm_pair_slice_counts(r, max_count=None):
    """Allowed sizes of a rank-two affine output cell (RM(r-2,r))."""
    if max_count is None:
        max_count = (1 << r) - 1
    length = 1 << r
    if r < 2:
        spec = {0}
    elif r == 2:
        spec = {0, 4}
    else:
        spec = {0, length} | set(range(4, length - 3, 2))
    return tuple(w for w in range(max_count + 1) if w + (w & 1) in spec)


def _rank_two_bases(k):
    """One canonical basis for each 2-dimensional subspace of F_2^k."""
    seen = set()
    bases = []
    for u in range(1, 1 << k):
        for v in range(u + 1, 1 << k):
            space = tuple(sorted((u, v, u ^ v)))
            if space in seen:
                continue
            seen.add(space)
            bases.append((space[0], space[1]))
    return bases


def _dot_pattern(mask, P):
    return sum((mask >> i) & 1 for i in P) & 1


def _add_rm_slice_pruning(model, x, g, Ps, max_count, level, d_target):
    """Add RM affine-slice cardinality domains -- SOUND ONLY FOR d >= 3.

    Every nonzero level adds the q=0 total-column domain.  Level=1 adds all
    rank-one output hyperplanes.  Level=2 additionally adds all rank-two
    affine cells, deduplicated by their 2-dimensional subspace.

    The domains come from the distance-3 identity: for a REDUCED distance >= 3
    factory the origin-augmented check support is a codeword of RM(r-4,r), so
    its weight -- and the weight of every affine slice of it -- is restricted to
    that code's spectrum (see ``rm_total_counts``).  At d = 2 the identity does
    not hold: zero and repeated syndromes are allowed, the support need not be
    an RM codeword, and these domains would then exclude legal factories, so a
    reported optimum or UNSAT would be wrong.  Hence the d_target guard rather
    than a comment: a caller cannot silently combine the two.
    """
    if level not in (0, 1, 2):
        raise ValueError('rm_pruning must be 0 (off), 1 (linear), or 2 (linear+pairs)')
    if level == 0:
        return
    if d_target < 3:
        raise ValueError(
            f'rm_pruning={level} is only sound for d_target >= 3 (it assumes the '
            f'check support is an RM(r-4,r) codeword, which needs distinct '
            f'nonzero syndromes); got d_target={d_target}')
    r = sum(block[1] for block in g.blocks)
    total_domain = cp_model.Domain.FromValues(rm_total_counts(r, max_count))
    # a selected slot contributes all its label_cost columns, and they all
    # share the output pattern P, so a slot lands in one slice entirely
    total_terms = [g.label_cost(g.labels[li]) * x[li, P]
                   for li in range(len(g.labels)) for P in Ps]
    total = model.NewIntVarFromDomain(total_domain, 'rm0_total')
    model.Add(total == sum(total_terms))

    linear_domain = cp_model.Domain.FromValues(rm_linear_slice_counts(r, max_count))
    for u in range(1, 1 << g.k):
        for bit in (0, 1):
            terms = [g.label_cost(g.labels[li]) * x[li, P]
                     for li in range(len(g.labels)) for P in Ps
                     if _dot_pattern(u, P) == bit]
            cell = model.NewIntVarFromDomain(linear_domain, f'rm1_{u}_{bit}')
            model.Add(cell == sum(terms))
    if level < 2:
        return
    pair_domain = cp_model.Domain.FromValues(rm_pair_slice_counts(r, max_count))
    for u, v in _rank_two_bases(g.k):
        for bu, bv in itertools.product((0, 1), repeat=2):
            terms = [g.label_cost(g.labels[li]) * x[li, P]
                     for li in range(len(g.labels)) for P in Ps
                     if _dot_pattern(u, P) == bu and _dot_pattern(v, P) == bv]
            cell = model.NewIntVarFromDomain(pair_domain,
                                             f'rm2_{u}_{v}_{bu}_{bv}')
            model.Add(cell == sum(terms))


def solve(k, blocks, target, d_target=3, time_s=120, verbose=False, cap=None,
          allowed_costs=None, allowed_patterns=None, phase_support_only=False,
          rm_pruning=0, min_count=None, workers=8, random_seed=0):
    """Optimise a slot-ansatz factory.

    ``phase_support_only=True`` restricts output labels to the canonical
    target phase support Y plus the check-only label 0.  This is a search
    ansatz, not a general WLOG theorem.  ``rm_pruning`` adds redundant
    affine-slice Reed--Muller weight domains (1: total and all linear slices;
    2: total, linear, and rank-two slices); they are sound only at
    ``d_target >= 3`` and raise otherwise.  ``min_count`` may encode
    a separately proved target-specific lower bound.

    ``cap`` bounds the T-count from above (turning optimisation into
    feasibility once tight); ``allowed_costs`` restricts slots to the given
    orbit sizes; ``allowed_patterns`` whitelists explicit output patterns
    (index iterables or bit masks).  Returns a dict: ``status`` in
    OPTIMAL/FEASIBLE/UNSAT/UNKNOWN, and on success ``n`` (T-count),
    ``assignment`` [(label, P), ...], ``geometry``, plus solver statistics.
    """
    g = Geometry(k, blocks)
    mons = g.monomials()
    if allowed_patterns is not None and phase_support_only:
        raise ValueError('choose allowed_patterns or phase_support_only, not both')
    if phase_support_only:
        Ps = canonical_phase_support(k, target, include_zero=True)
    elif allowed_patterns is not None:
        Ps = _normalise_patterns(k, allowed_patterns)
    else:
        Ps = tuple(tuple(P) for s in range(k + 1)
                   for P in itertools.combinations(range(k), s))

    m = cp_model.CpModel()
    x = {}
    for li, lab in enumerate(g.labels):
        for P in Ps:
            x[li, P] = m.NewBoolVar(f'x_{li}_{P}')
        m.AddAtMostOne(x[li, P] for P in Ps)   # slot rule: <=1 pattern per label

    if allowed_costs is not None:                # restrict to given orbit sizes
        allowed = set(allowed_costs)
        for li, lab in enumerate(g.labels):
            if g.label_cost(lab) not in allowed:
                for P in Ps:
                    m.Add(x[li, P] == 0)

    tvar = m.NewBoolVar('true')
    m.Add(tvar == 1)          # constant TRUE literal, pads XORs that must be even

    def tbit(mon):
        """Required parity: 1 iff mon is a target output monomial; every
        check-touching monomial must have even parity."""
        Q, Ts = mon
        if any(len(T) for T in Ts):
            return 0
        if not isinstance(target, str):        # custom: set of output-monomials
            return 1 if frozenset(Q) in target else 0
        if target == 'T' and len(Q) == 1:
            return 1
        if target == 'CS' and Q == (0, 1):
            return 1
        if target == 'CCZ' and Q == (0, 1, 2):
            return 1
        return 0

    # one XOR constraint per monomial class: slot (lab, P) contributes iff
    # Q <= P and an odd number of its columns contain the check part Ts
    for mon in mons:
        Q = set(mon[0])
        lits = []
        for li, lab in enumerate(g.labels):
            if g.coeff(lab, mon):
                for P in Ps:
                    if Q <= set(P):
                        lits.append(x[li, P])
        want = tbit(mon)
        if not lits:
            if want:
                return {'status': 'UNSAT', 'N': g.N}
            continue
        m.AddBoolXOr(lits + ([tvar] if want == 0 else []))  # XOR(lits) == want

    if d_target >= 4:
        nb = len(blocks)
        # per-block triple-cancellation tables over orbit indices
        tabs = []
        for bi in range(nb):
            orbs = g.orbits[bi]
            tab = {}
            for i1 in range(len(orbs)):
                for i2 in range(i1, len(orbs)):
                    for i3 in range(i2, len(orbs)):
                        if tri_cancel_block(orbs[i1], orbs[i2], orbs[i3]):
                            for p in set(itertools.permutations((i1, i2, i3))):
                                tab[p] = True
            tabs.append(tab)

        # forbid every label triple that can cancel on all check blocks
        # unless the three output patterns XOR to zero.  Sound
        # over-approximation: the per-block cancelling columns always exist
        # in the slots, but may fail to be three DISTINCT columns, so some
        # genuinely d>=4 factories are excluded (exact_d4.py lifts this).
        L = len(g.labels)
        for a in range(L):
            for b in range(a, L):
                for c in range(b, L):
                    la, lb, lc = g.labels[a], g.labels[b], g.labels[c]
                    if not all(tabs[i].get((la[i], lb[i], lc[i]), False)
                               for i in range(nb)):
                        continue
                    if a == b == c:
                        # three columns from one slot: output XOR = P
                        for P in Ps:
                            if P:
                                m.Add(x[a, P] == 0)
                    elif a == b or b == c or a == c:
                        # two columns from the repeated slot (output XOR 0)
                        # plus one from the other: fatal iff its P2 != 0
                        rep = a if a == b or a == c else b
                        oth = c if a == b else (a if b == c else b)
                        for P2 in Ps:
                            if P2:
                                for P1 in Ps:
                                    m.AddBoolOr([x[rep, P1].Not(),
                                                 x[oth, P2].Not()])
                    else:
                        for P1 in Ps:
                            for P2 in Ps:
                                for P3 in Ps:
                                    xr = set(P1) ^ set(P2) ^ set(P3)
                                    if xr:      # residual output-only error
                                        m.AddBoolOr([x[a, P1].Not(),
                                                     x[b, P2].Not(),
                                                     x[c, P3].Not()])

    obj = sum(g.label_cost(g.labels[li]) * x[li, P]
              for li in range(len(g.labels)) for P in Ps)
    if min_count is not None:
        if min_count < 0:
            raise ValueError('min_count must be nonnegative')
        if cap is not None and min_count > cap:
            raise ValueError('min_count cannot exceed cap')
        m.Add(obj >= min_count)
    if cap is not None:
        m.Add(obj <= cap)          # T-count ceiling: turns min into feasibility
    # n <= 2^r - 1: block supports are disjoint, so a column's check part
    # determines its label and combo -- selected columns have pairwise
    # distinct nonzero check parts
    max_count = min((1 << sum(block[1] for block in blocks)) - 1,
                    cap if cap is not None else (1 << sum(block[1] for block in blocks)) - 1)
    _add_rm_slice_pruning(m, x, g, Ps, max_count, rm_pruning, d_target)
    m.Minimize(obj)

    sol = cp_model.CpSolver()
    sol.parameters.max_time_in_seconds = time_s
    sol.parameters.num_search_workers = workers
    sol.parameters.random_seed = random_seed
    sol.parameters.log_search_progress = verbose
    st = sol.Solve(m)
    if st == cp_model.INFEASIBLE:
        return {'status': 'UNSAT', 'N': g.N,
                'bound': sol.BestObjectiveBound(),
                'wall_time': sol.WallTime(), 'branches': sol.NumBranches(),
                'conflicts': sol.NumConflicts()}
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {'status': 'UNKNOWN', 'N': g.N,
                'bound': sol.BestObjectiveBound(),
                'wall_time': sol.WallTime(), 'branches': sol.NumBranches(),
                'conflicts': sol.NumConflicts()}
    asg = []
    for li, lab in enumerate(g.labels):
        for P in Ps:
            if sol.Value(x[li, P]):
                asg.append((lab, P))
    return {'status': 'OPTIMAL' if st == cp_model.OPTIMAL else 'FEASIBLE',
            'n': int(sol.ObjectiveValue()), 'N': g.N, 'assignment': asg,
            'bound': sol.BestObjectiveBound(), 'geometry': g,
            'patterns': Ps, 'rm_pruning': rm_pruning,
            'phase_support_only': phase_support_only,
            'wall_time': sol.WallTime(), 'branches': sol.NumBranches(),
            'conflicts': sol.NumConflicts()}


# ------------------------------------------------------------- verifier
def columns_of(gm, assignment):
    """Expand a solve()/exact_solve() assignment into explicit columns:
    frozensets of global qubit indices (outputs 0..k-1, then the check
    blocks in declaration order)."""
    starts, s = [], gm.k
    for b in gm.blocks:
        starts.append(s)
        s += b[1]
    cols = []
    for lab, P in assignment:
        pools = []
        for i, j in enumerate(lab):
            pools.append([frozenset(starts[i] + q for q in S)
                          for S in gm.orbits[i][j]])
        for combo in itertools.product(*pools):
            supp = set(P)
            for c in combo:
                supp |= c
            cols.append(frozenset(supp))
    return cols


def verify(k, N, cols, target, dmax=4):
    """Independent column-level check.  Returns (data_ok, d).

    data_ok: every degree-<=3 parity over all N qubits matches the target
    (check-touching monomials must be even).  d: true circuit distance via
    meet-in-the-middle over column-mask XORs -- the exact value when
    <= dmax, else the string '>dmax'."""
    n = len(cols)
    if len(set(cols)) != n:
        # See factorylib.verification.verify: not an assert, because a verifier's
        # input checks must survive `python -O`.
        raise ValueError(
            f"{n - len(set(cols))} repeated column(s): a factory with a repeated "
            f"column has an undetectable weight-2 fault, so its distance is 2")

    def par(qs):
        qs = set(qs)
        return sum(1 for c in cols if qs <= c) & 1

    def want(*S):
        if not isinstance(target, str):        # custom: set of output-monomials
            return 1 if frozenset(S) in target else 0
        if target == 'T':
            return 1 if len(S) == 1 and S[0] < k else 0
        if target == 'CS':
            return 1 if set(S) == {0, 1} else 0
        if target == 'CCZ':
            return 1 if set(S) == {0, 1, 2} else 0
        return 0

    ok = True
    for a in range(N):
        ok &= par([a]) == want(a)
    for a, b in itertools.combinations(range(N), 2):
        ok &= par([a, b]) == want(a, b)
    for a, b, c in itertools.combinations(range(N), 3):
        ok &= par([a, b, c]) == want(a, b, c)

    masks = []
    for c in cols:
        mm = 0
        for q in c:
            mm |= 1 << q
        masks.append(mm)
    outm = (1 << k) - 1
    bad_targets = [t for t in range(1, 1 << k)]   # nonzero output-only errors

    def is_bad(v):
        return v != 0 and (v & ~outm) == 0

    for v in masks:                                   # weight 1
        if is_bad(v):
            return ok, 1
    for i, j in itertools.combinations(range(n), 2):  # weight 2
        if is_bad(masks[i] ^ masks[j]):
            return ok, 2
    pairval = {}
    for i, j in itertools.combinations(range(n), 2):
        pairval.setdefault(masks[i] ^ masks[j], []).append((i, j))
    if dmax >= 3:                                     # weight 3
        for t in bad_targets:
            for i in range(n):
                for (a, b) in pairval.get(masks[i] ^ t, []):
                    if i not in (a, b):
                        return ok, 3
    if dmax >= 4:                                     # weight 4
        for t in bad_targets:
            for v, plist in pairval.items():
                for (a, b) in pairval.get(v ^ t, []):
                    for (c, d) in plist:
                        if len({a, b, c, d}) == 4:
                            return ok, 4
    return ok, f'>{dmax}'


def block_tag(blocks):
    """Human-readable tag; 'P' blocks (explicit perm-group) render as P<lam>#<i>."""
    parts = []
    for i, b in enumerate(blocks):
        kd, lm = b[0], b[1]
        parts.append(f'{kd}{lm}#{i}' if kd == 'P' else f'{kd}{lm}')
    return '+'.join(parts)


#: Output arity of each named slot target.  A width-w gate needs w output
#: wires; without the check below, `--k 1 --target CS` constrained a "CS on
#: outputs 0,1" where wire 1 was a CHECK qubit, and the CLI printed
#: `OPTIMAL n=0 data_ok=False` and exited 0.
_TARGET_WIDTH = {'T': 1, 'CS': 2, 'CCZ': 3}


def run(k, target, geoms, d_target=3, time_s=120):
    """Solve each geometry, expand + independently verify the winner, and
    print one summary line plus the slot assignment.

    Returns the number of geometries this run did NOT settle: a winner that
    failed the independent column-level check, and equally a solve that timed
    out (UNKNOWN).  The CLI turns a nonzero count into a nonzero exit.  UNSAT is
    settled -- it is the answer "no factory on this geometry" -- but UNKNOWN is
    "no answer yet", and `--time 0` used to print UNKNOWN for every geometry and
    exit 0, which a script reads as success.
    """
    width = _TARGET_WIDTH.get(target)
    if width is not None and width > k:
        raise ValueError(
            f'target {target!r} acts on {width} output qubits but k={k}: '
            f'a width-{width} gate needs k >= {width}')
    print(f'==== k={k} target={target} d>={d_target} ====', flush=True)
    failures = 0
    for blocks in geoms:
        r = solve(k, blocks, target, d_target, time_s)
        tag = block_tag(blocks)
        if r['status'] in ('UNSAT', 'UNKNOWN'):
            if r['status'] == 'UNKNOWN':
                failures += 1
                note = '  (unresolved: the solver hit --time)'
            else:
                note = ''
            print(f'  {tag:14s} N={r["N"]:3d}  {r["status"]}{note}', flush=True)
            continue
        gm = r['geometry']
        cols = columns_of(gm, r['assignment'])
        ok, d = verify(k, gm.N, cols, target, dmax=max(4, d_target))
        print(f'  {tag:14s} N={r["N"]:3d}  n={r["n"]:4d}  '
              f'[[{r["n"]},{k},{d}]]  {r["status"]}  data_ok={ok}', flush=True)
        for lab, P in sorted(r['assignment']):
            sz = gm.label_cost(lab)
            print(f'      P={set(P) if P else "{}"} lab={lab} ({sz} gates)',
                  flush=True)
        short = isinstance(d, int) and d < d_target
        if not ok or short:
            failures += 1
            why = [] if ok else ['target parities are wrong']
            if short:
                why.append(f'verified distance {d} < requested {d_target}')
            print(f'      FAILED independent verification: {"; ".join(why)}',
                  flush=True)
    if failures:
        print(f'  {failures} of {len(geoms)} geometr'
              f'{"y" if len(geoms) == 1 else "ies"} unresolved or failed',
              flush=True)
    return failures


def parse_geometry(spec):
    """Parse ``S4+C7`` into the block tuples consumed by :class:`Geometry`.

    The compact CLI intentionally supports the two publishable built-in block
    families: ``S`` (fully symmetric) and ``C`` (cyclic). Programmatic callers
    can still pass explicit ``P`` permutation groups directly to ``solve``.
    """
    blocks = []
    for token in spec.replace(",", "+").split("+"):
        match = re.fullmatch(r"([SC])(\d+)", token.strip(), re.IGNORECASE)
        if not match:
            raise ValueError(
                f"invalid block {token!r}; use e.g. S4, C7, or S3+C4"
            )
        blocks.append((match.group(1).upper(), int(match.group(2))))
    if not blocks:
        raise ValueError("a geometry must contain at least one block")
    return blocks


def main(argv=None):
    """Run one or more slot geometries from a stable, documented CLI."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--k", type=int, required=True, help="number of outputs")
    parser.add_argument("--target", choices=("T", "CS", "CCZ"), required=True)
    parser.add_argument(
        "--geometry", action="append", required=True,
        help="check-block geometry such as S4, C7, or S3+C4; repeatable",
    )
    parser.add_argument("--distance", type=int, choices=(3, 4), default=3)
    parser.add_argument("--time", type=float, default=120, help="seconds per geometry")
    args = parser.parse_args(argv)
    try:
        geometries = [parse_geometry(spec) for spec in args.geometry]
    except ValueError as error:
        parser.error(str(error))
    try:
        failures = run(args.k, args.target, geometries, args.distance, args.time)
    except ValueError as error:            # invalid target/width combination
        parser.error(str(error))
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
