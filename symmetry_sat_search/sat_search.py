#!/usr/bin/env python3
"""
Fully exhaustive circuit-level SAT search for magic-state factories.

The raw, ansatz-free search (``../theory/04_symmetry_and_sat.md``): unlike the
slot-ansatz searches (``slot_search.py``, ``exact_d4.py``), which are optimal
only *within* a chosen check-symmetry ansatz, this module searches the
**entire** circuit space and returns the certified minimum-``T`` factory (or
UNSAT) for a target and distance.

Formulation
-----------
One boolean variable per nonzero column ``alpha in F_2^N \\ {0}``
(``v_alpha = 1`` iff the parity-``T`` rotation with support ``alpha`` is in
the circuit).  Qubits ``0..k-1`` are outputs, the rest postselected checks.

* target parity (XOR) constraints, one per degree-1/2/3 monomial:
      XOR_{alpha superset m} v_alpha  ==  D[m]           (eq. sat-linear..cubic)
* distance clauses forbidding every undetected fault of weight ``< d``:
      d>=2 : no output-only column is selected               (weight-1 faults)
      d>=3 : no two selected columns XOR to an output-only error (weight-2)
      d>=4 : no three selected columns XOR to an output-only error (weight-3)
* objective: minimise the ``T``-count ``sum_alpha v_alpha`` (certified).

The Clifford ``level`` sets the constraint degree: 2 (S, CZ), 3 (T, CS, CCZ),
4 (sqrt(T), CT, CCS, CCCZ).  Distance is level-independent.

Search-space reduction (completeness-preserving)
-------------------------------------------------
Optional **symmetry breaking**: the check qubits (and, for a fully symmetric
target such as ``T^{\\otimes k}``, the output qubits) are interchangeable.
For each generator of that permutation group (adjacent transpositions) we add
a lexicographic-leader constraint ``x <= sigma(x)`` on the selection vector.
This never removes the lex-minimal member of an orbit, so the search stays
**exhaustive/complete** -- it just prunes symmetric duplicates.

Backends
--------
* ``backend='cpsat'`` (default): OR-Tools CP-SAT.  Native boolean XOR and a
  linear objective, so it returns a genuine OPTIMAL/UNSAT certificate.  No
  extra dependency.
* ``backend='pysat'`` (optional): python-sat + CaDiCaL, mirroring the legacy
  CNF encoding (Tseitin XOR + sequential-counter cardinality); the minimum
  ``T``-count is found by an at-most-k bisection.  Requires ``python-sat``.
* ``backend='cryptominisat'`` (optional): CryptoMiniSat through ``pycryptosat``.
  Target parity equations are passed as native XOR clauses, while distance
  and exact-T-count constraints are ordinary CNF.  Requires ``pycryptosat``.

Every returned factory is re-verified at the column level with ``evaluator``.

Examples
--------
    import sat_search
    sat_search.search(k=1, N=4, target='T',   d=2)   # -> [[14,1,2]]
    sat_search.search(k=2, N=4, target='CS',  d=2)   # -> [[12,2,2]]
    sat_search.search(k=3, N=4, target='CCZ', d=2)   # -> [[8,3,2]]
    sat_search.search(k=1, N=5, target='T',   d=3)   # -> [[15,1,3]]

Run ``python symmetry_sat_search/sat_search.py --help`` for the stable CLI.
"""
import argparse
import itertools
import json
import os
import sys
from numbers import Integral

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import evaluator                              # noqa: E402  (column-level verify)


# --------------------------------------------------------------------- model
def all_columns(N):
    """Every nonzero column of F_2^N, as an integer bitmask."""
    return list(range(1, 1 << N))


def monomials(N, maxdeg=3):
    """All degree-1..maxdeg monomials (qubit tuples) over [N]."""
    mons = []
    for deg in range(1, maxdeg + 1):
        mons.extend(itertools.combinations(range(N), deg))
    return mons


# named single-gate targets, keyed by Clifford level:
#   level 2 (pi/4): S (w=1), CZ (w=2)
#   level 3 (pi/8): T (w=1), CS (w=2), CCZ (w=3)
#   level 4 (pi/16): sqrtT (w=1), CT (w=2), CCS (w=3), CCCZ (w=4)
# a width-w gate is the degree-w monomial on the first w outputs; the width-1
# gate is put on *every* output (so 'T' is T^{k}, 'S' is S^{k}, etc.).
_NAMED = {
    'S': 1, 'CZ': 2,
    'T': 1, 'CS': 2, 'CCZ': 3,
    'sqrtT': 1, 'CT': 2, 'CCS': 3, 'CCCZ': 4,
}

#: Which Clifford level each named gate belongs to.  `target_D` refuses a
#: mismatch, because the level sets which monomial degrees are constrained.
_LEVEL_OF = {
    'S': 2, 'CZ': 2,
    'T': 3, 'CS': 3, 'CCZ': 3,
    'sqrtT': 4, 'CT': 4, 'CCS': 4, 'CCCZ': 4,
}


def target_D(target, k, N, level=None):
    """Set of monomials whose target parity is 1.

    A dict {deg: [monomials]} is accepted verbatim (entangled / custom
    targets).  A named gate maps to a single monomial: width-1 gates
    ('T','S','sqrtT') put the gate on every output -> {(i,): i in [k]};
    wider gates ('CS','CCZ','CZ','CT','CCS','CCCZ') use the degree-w monomial
    on the first w outputs.  Every other monomial has target 0.
    """
    if isinstance(target, dict):
        # A custom target used to be taken entirely on trust.  It names the
        # monomials whose LOGICAL parity must be 1, so every index in it has to
        # be an output wire: `{2: [(0, 1)]}` at k=1 asked for "CS on wires 0 and
        # 1" where wire 1 is a CHECK, and the solver returned OPTIMAL with
        # target_ok=True for a circuit that is not a k=1 CS factory.
        out = set()
        for deg, mons in target.items():
            for t in mons:
                # Sort only after checking the types: `sorted` on a mix of int
                # and str raises TypeError from inside the comprehension, and a
                # negative index sorts to the front where the `mon[-1] >= k`
                # bound below never sees it.
                if any(not isinstance(q, int) or isinstance(q, bool)
                       for q in t):
                    raise ValueError(
                        f'custom target monomial {tuple(t)} has a non-integer '
                        f'qubit index')
                if any(q < 0 for q in t):
                    raise ValueError(
                        f'custom target monomial {tuple(t)} has a negative '
                        f'qubit index; outputs are numbered 0..{k - 1}')
                mon = tuple(sorted(t))
                if not mon:
                    raise ValueError(
                        'custom target contains an empty monomial; the constant '
                        'term is not a logical gate')
                if len(set(mon)) != len(mon):
                    raise ValueError(f'custom target monomial {mon} repeats a '
                                     f'qubit')
                if mon[-1] >= k:
                    raise ValueError(
                        f'custom target monomial {mon} touches qubit {mon[-1]}, '
                        f'which is a CHECK qubit (k={k}): a logical target may '
                        f'only name output qubits 0..{k - 1}')
                if level is not None and len(mon) > level:
                    raise ValueError(
                        f'custom target monomial {mon} has degree {len(mon)}, '
                        f'above the level-{level} maximum of {level}')
                # The key must BE the degree, and be an integer: `{'2': ...}`,
                # `{'garbage': ...}` and `{True: ...}` all skipped this check
                # when it only fired for ints, so a target could be filed under
                # a degree that says nothing about its contents.
                if not isinstance(deg, int) or isinstance(deg, bool):
                    raise ValueError(
                        f'custom target has key {deg!r}; keys are the monomial '
                        f'degree, so they must be positive integers')
                if len(mon) != deg:
                    raise ValueError(
                        f'custom target lists {mon} under degree {deg}')
                out.add(mon)
        return out
    if target not in _NAMED:
        raise ValueError(f'unknown target {target!r}')
    w = _NAMED[target]
    # A width-w gate needs w output wires.  Without this check `--k 1 --target CS`
    # built a "CS on outputs 0,1" constraint on a circuit with ONE output, so
    # index 1 was a CHECK qubit: the solver dutifully returned an OPTIMAL
    # [[12,1,2]] with target_ok=True that is not a k=1 CS factory at all.
    if w > k:
        raise ValueError(
            f'target {target!r} acts on {w} output qubits but k={k}: '
            f'a width-{w} gate needs k >= {w}')
    # Each named gate belongs to one Clifford level; asking for it at another
    # level silently changes which monomial degrees are constrained.
    if level is not None and _LEVEL_OF[target] != level:
        raise ValueError(
            f'target {target!r} is a level-{_LEVEL_OF[target]} gate but '
            f'level {level} was requested; use level {_LEVEL_OF[target]}')
    if w == 1:
        return {(i,) for i in range(k)}
    return {tuple(range(w))}


def _mask(mon):
    m = 0
    for q in mon:
        m |= 1 << q
    return m


def _perm_generators(N, k, symmetric_outputs):
    """Adjacent-transposition generators of the allowed qubit-permutation
    group: check qubits k..N-1 always interchangeable; outputs 0..k-1 too when
    the target is symmetric under output relabelling (e.g. T^{k})."""
    gens = []
    for a in range(k, N - 1):                 # swap check a <-> a+1
        gens.append((a, a + 1))
    if symmetric_outputs:
        for a in range(0, k - 1):             # swap output a <-> a+1
            gens.append((a, a + 1))
    return gens


def _apply_swap_to_mask(mask, i, j):
    """Apply the qubit transposition (i j) to a column bitmask."""
    bi, bj = (mask >> i) & 1, (mask >> j) & 1
    if bi == bj:
        return mask
    mask &= ~((1 << i) | (1 << j))
    mask |= (bi << j) | (bj << i)
    return mask


def _output_only(mask, k):
    """True iff the column/error is supported entirely on outputs 0..k-1.

    (Currently unused: ``forbidden_faults`` inlines the same predicate.)"""
    outm = (1 << k) - 1
    return mask != 0 and (mask & ~outm) == 0


def forbidden_faults(cols, k, d):
    """Column-index tuples of every undetected fault of weight < d (weight-1
    for d>=2, weight-2 for d>=3, weight-3 for d>=4): a fault is undetected+bad
    iff its columns XOR to a nonzero output-only error.  Level-independent."""
    outm = (1 << k) - 1

    def bad(v):
        return v != 0 and (v & ~outm) == 0

    weight1 = [(i,) for i, c in enumerate(cols) if bad(c)]
    if d <= 2:
        return [weight1]
    weight2 = []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            if bad(cols[i] ^ cols[j]):
                weight2.append((i, j))
    if d <= 3:
        return [weight1, weight2]
    if d == 4:                                   # weight-3 triples summing to L_O
        idx = {c: i for i, c in enumerate(cols)}
        targets = [t for t in range(1, 1 << k)]  # nonzero output-only errors
        triples = set()
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                s = cols[i] ^ cols[j]
                for t in targets:
                    kk = idx.get(s ^ t)
                    if kk is not None and kk != i and kk != j:
                        triples.add(tuple(sorted((i, j, kk))))
        return [weight1, weight2, list(triples)]
    raise NotImplementedError('exhaustive raw SAT implemented for d<=4')


# ------------------------------------------------------------- CP-SAT backend
def _solve_cpsat(N, k, D, d, level, symmetry, symmetric_outputs, time_s, tcount,
                 solver_kwargs=None):
    """OR-Tools CP-SAT backend: native XOR + linear objective, so OPTIMAL /
    INFEASIBLE are genuine certificates.  ``tcount`` (if given) replaces
    minimisation with exact-cardinality feasibility."""
    from ortools.sat.python import cp_model
    cols = all_columns(N)
    m = cp_model.CpModel()
    v = {c: m.NewBoolVar(f'v{c}') for c in cols}
    true = m.NewBoolVar('true')
    m.Add(true == 1)

    # target parity constraints (degree 1..level monomials)
    for mon in monomials(N, level):
        mm = _mask(mon)
        lits = [v[c] for c in cols if (c & mm) == mm]
        want = 1 if tuple(mon) in D else 0
        if not lits:
            if want:
                return {'status': 'UNSAT', 'N': N}
            continue
        m.AddBoolXOr(lits + ([true] if want == 0 else []))

    # distance clauses: forbid every undetected fault of weight < d
    faults = forbidden_faults(cols, k, d)
    for w, fs in enumerate(faults, start=1):
        for tup in fs:
            if w == 1:
                m.Add(v[cols[tup[0]]] == 0)
            else:
                m.AddBoolOr([v[cols[i]].Not() for i in tup])

    # symmetry breaking: x <= sigma(x) lexicographically, per generator
    if symmetry:
        order = cols                                   # fixed column order
        for (a, b) in _perm_generators(N, k, symmetric_outputs):
            ys = [v[_apply_swap_to_mask(c, a, b)] for c in order]
            xs = [v[c] for c in order]
            _cpsat_lex_leq(m, xs, ys)

    if tcount is not None:
        m.Add(sum(v[c] for c in cols) == tcount)
    m.Minimize(sum(v[c] for c in cols))

    sol = cp_model.CpSolver()
    sol.parameters.max_time_in_seconds = time_s
    sol.parameters.num_search_workers = 8
    st = sol.Solve(m)
    if st == cp_model.INFEASIBLE:
        return {'status': 'UNSAT', 'N': N}
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {'status': 'UNKNOWN', 'N': N}
    chosen = [c for c in cols if sol.Value(v[c])]
    return {'status': 'OPTIMAL' if st == cp_model.OPTIMAL else 'FEASIBLE',
            'n': len(chosen), 'N': N, 'masks': chosen}


def _cpsat_lex_leq(m, xs, ys):
    """Enforce (xs <= ys) lexicographically for equal-length boolean lists."""
    eq = m.NewBoolVar('lex_eq0')
    m.Add(eq == 1)                                     # equal-so-far before pos 0
    for xi, yi in zip(xs, ys):
        # if equal-so-far then xi <= yi   (xi implies yi)
        m.AddBoolOr([eq.Not(), xi.Not(), yi])
        nxt = m.NewBoolVar('lex_eq')
        # nxt == eq AND (xi == yi)
        same = m.NewBoolVar('same')
        m.Add(xi == yi).OnlyEnforceIf(same)
        m.Add(xi != yi).OnlyEnforceIf(same.Not())
        m.AddBoolAnd([eq, same]).OnlyEnforceIf(nxt)
        m.AddBoolOr([eq.Not(), same.Not()]).OnlyEnforceIf(nxt.Not())
        eq = nxt


# -------------------------------------------------------------- pysat backend
def _solve_pysat(N, k, D, d, level, symmetry, symmetric_outputs, time_s, tcount,
                 solver_kwargs=None):
    """python-sat (CaDiCaL) backend mirroring the legacy CNF encoding.

    Minimum-T mode sweeps at-most-k bounds upward from 0; at-most-k
    feasibility is monotone in k, so the first SAT bound is the certified
    minimum.  ``time_s`` is not enforced by this backend."""
    from pysat.formula import CNF, IDPool
    from pysat.card import CardEnc, EncType
    from pysat.solvers import Cadical153

    cols = all_columns(N)
    pool = IDPool()
    var = {c: pool.id(('v', c)) for c in cols}
    base = CNF()

    def xor_eq(lits, b):
        """CNF for XOR(lits) == b via a Tseitin chain (matches legacy encoding)."""
        if not lits:
            if b:
                base.append([])                       # empty clause -> UNSAT
            return
        acc = lits[0]
        for nxt in lits[1:]:
            z = pool.id(('xor', acc, nxt))
            # z == acc XOR nxt
            base.extend([[-acc, -nxt, -z], [acc, nxt, -z],
                         [acc, -nxt, z], [-acc, nxt, z]])
            acc = z
        base.append([acc] if b else [-acc])

    for mon in monomials(N, level):
        mm = _mask(mon)
        lits = [var[c] for c in cols if (c & mm) == mm]
        xor_eq(lits, 1 if tuple(mon) in D else 0)

    # distance clauses: forbid every undetected fault of weight < d
    for tup in [t for group in forbidden_faults(cols, k, d) for t in group]:
        base.append([-var[cols[i]] for i in tup])

    if symmetry:
        for (a, b) in _perm_generators(N, k, symmetric_outputs):
            xs = [var[c] for c in cols]
            ys = [var[_apply_swap_to_mask(c, a, b)] for c in cols]
            _pysat_lex_leq(base, pool, xs, ys)

    allv = [var[c] for c in cols]

    def feasible(bound, exact=False):
        cnf = CNF()
        cnf.extend(base.clauses)
        if bound is not None:
            enc = CardEnc.equals if exact else CardEnc.atmost
            card = enc(lits=allv, bound=bound, vpool=pool,
                      encoding=EncType.seqcounter)
            cnf.extend(card.clauses)
        s = Cadical153(bootstrap_with=cnf.clauses)
        ok = s.solve()
        model = set(s.get_model()) if ok else None
        s.delete()
        return ok, model

    if tcount is not None:
        # EXACT T-count (matches the cpsat backend's `== tcount` semantics,
        # not merely "at most tcount")
        ok, model = feasible(tcount, exact=True)
        if not ok:
            return {'status': 'UNSAT', 'N': N}
        chosen = [c for c in cols if var[c] in model]
        return {'status': 'FEASIBLE', 'n': len(chosen), 'N': N, 'masks': chosen}

    # minimum T-count: smallest bound that is still SAT (at-most is monotone)
    ok, _ = feasible(None)
    if not ok:
        return {'status': 'UNSAT', 'N': N}
    best = None
    hi = len(cols)
    for bound in range(0, hi + 1):
        ok, model = feasible(bound)
        if ok:
            best = [c for c in cols if var[c] in model]
            break
    return {'status': 'OPTIMAL', 'n': len(best), 'N': N, 'masks': best}


def _pysat_lex_leq(cnf, pool, xs, ys):
    """CNF for (xs <= ys) lexicographically (equal-so-far chain)."""
    prev = None                                        # None == "true" (equal so far)
    for xi, yi in zip(xs, ys):
        if prev is None:
            cnf.append([-xi, yi])                      # xi -> yi
        else:
            cnf.append([-prev, -xi, yi])               # eq & xi -> yi
        nxt = pool.id(('lex', xi, yi))
        # nxt <-> prev & (xi == yi)
        eqxy = pool.id(('eqxy', xi, yi))
        cnf.extend([[-eqxy, -xi, yi], [-eqxy, xi, -yi],
                    [eqxy, xi, yi], [eqxy, -xi, -yi]])   # eqxy <-> (xi==yi)
        if prev is None:
            cnf.extend([[-nxt, eqxy], [nxt, -eqxy]])    # nxt <-> eqxy
        else:
            cnf.extend([[-nxt, prev], [-nxt, eqxy], [nxt, -prev, -eqxy]])
        prev = nxt


# -------------------------------------------------------- CryptoMiniSat backend
def _add_at_most_sequential(solver, lits, bound, next_var_id):
    """Add a Sinz sequential-counter encoding of ``sum(lits) <= bound``.

    ``lits`` may contain either positive or negative literals.  CryptoMiniSat
    accepts the resulting clauses directly as signed integer literals.
    """
    if bound < 0:
        solver.add_clause([])
        return next_var_id
    if bound >= len(lits):
        return next_var_id
    if bound == 0:
        for lit in lits:
            solver.add_clause([-lit])
        return next_var_id

    s = {}
    for i in range(len(lits)):
        for j in range(1, bound + 1):
            s[(i, j)] = next_var_id
            next_var_id += 1

    for i, lit in enumerate(lits):
        solver.add_clause([-lit, s[(i, 1)]])
        if i == 0:
            continue
        solver.add_clause([-s[(i - 1, 1)], s[(i, 1)]])
        for j in range(2, bound + 1):
            solver.add_clause([-s[(i - 1, j)], s[(i, j)]])
            solver.add_clause([-lit, -s[(i - 1, j - 1)], s[(i, j)]])
        solver.add_clause([-lit, -s[(i - 1, bound)]])
    return next_var_id


def _cryptominisat_lex_leq(solver, xs, ys, next_var_id):
    """Add the CNF encoding of ``xs <= ys`` lexicographically."""
    prev = None                                        # equal so far
    for xi, yi in zip(xs, ys):
        if prev is None:
            solver.add_clause([-xi, yi])               # xi -> yi
        else:
            solver.add_clause([-prev, -xi, yi])        # eq & xi -> yi

        eqxy = next_var_id
        next_var_id += 1
        solver.add_clause([-eqxy, -xi, yi])
        solver.add_clause([-eqxy, xi, -yi])
        solver.add_clause([eqxy, xi, yi])
        solver.add_clause([eqxy, -xi, -yi])

        nxt = next_var_id
        next_var_id += 1
        if prev is None:
            solver.add_clause([-nxt, eqxy])
            solver.add_clause([nxt, -eqxy])
        else:
            solver.add_clause([-nxt, prev])
            solver.add_clause([-nxt, eqxy])
            solver.add_clause([nxt, -prev, -eqxy])
        prev = nxt
    return next_var_id


def _solve_cryptominisat(N, k, D, d, level, symmetry, symmetric_outputs,
                         time_s, tcount, solver_kwargs=None):
    """Solve using CryptoMiniSat's native XOR support via ``pycryptosat``."""
    try:
        from pycryptosat import Solver
    except ImportError as exc:
        raise ImportError(
            "backend='cryptominisat' requires pycryptosat; install it with "
            "`pip install pycryptosat`"
        ) from exc

    if tcount is None:
        # CryptoMiniSat is a decision solver, so reproduce the public
        # minimum-T semantics by solving exact-count instances from low to
        # high, just as the pysat backend does with at-most bounds.
        for candidate in range(len(all_columns(N)) + 1):
            result = _solve_cryptominisat(
                N, k, D, d, level, symmetry, symmetric_outputs, time_s,
                candidate, solver_kwargs
            )
            if result['status'] == 'FEASIBLE':
                result['status'] = 'OPTIMAL'
                return result
            if result['status'] == 'UNKNOWN':
                return result
        return {'status': 'UNSAT', 'N': N}

    cols = all_columns(N)
    var = {c: i for i, c in enumerate(cols, start=1)}
    solver = Solver()

    # Native XOR constraints avoid the Tseitin chains used by the pysat path.
    for mon in monomials(N, level):
        mm = _mask(mon)
        lits = [var[c] for c in cols if (c & mm) == mm]
        want = 1 if tuple(mon) in D else 0
        if lits:
            solver.add_xor_clause(lits, bool(want))
        elif want:
            solver.add_clause([])

    # Distance clauses: forbid every undetected fault of weight < d.
    for tup in [t for group in forbidden_faults(cols, k, d) for t in group]:
        solver.add_clause([-var[cols[i]] for i in tup])

    next_var_id = len(cols) + 1
    if symmetry:
        for a, b in _perm_generators(N, k, symmetric_outputs):
            xs = [var[c] for c in cols]
            ys = [var[_apply_swap_to_mask(c, a, b)] for c in cols]
            next_var_id = _cryptominisat_lex_leq(solver, xs, ys, next_var_id)

    if tcount is not None:
        if tcount > len(cols):
            return {'status': 'UNSAT', 'N': N}
        allv = list(var.values())
        next_var_id = _add_at_most_sequential(solver, allv, tcount,
                                              next_var_id)
        # sum(v) >= tcount is sum(not v) <= len(cols)-tcount.
        _add_at_most_sequential(solver, [-v for v in allv],
                                len(cols) - tcount, next_var_id)

    solve_kwargs = dict(solver_kwargs or {})
    if time_s is not None and 'time_limit' not in solve_kwargs:
        solve_kwargs['time_limit'] = time_s
    sat, assignment = solver.solve(**solve_kwargs)
    if sat is False:
        return {'status': 'UNSAT', 'N': N}
    if sat is None:
        return {'status': 'UNKNOWN', 'N': N}
    if sat is not True:
        return {'status': 'UNKNOWN', 'N': N}

    chosen = [c for c in cols if assignment[var[c]]]
    return {'status': 'FEASIBLE', 'n': len(chosen), 'N': N, 'masks': chosen}


# ------------------------------------------------------------------ frontend
def _masks_to_columns(masks, N):
    return [sorted(i for i in range(N) if mm >> i & 1) for mm in masks]


def _normalise_tcounts(tcount, tcounts):
    """Return sorted exact T-count requests, or ``None`` for minimisation."""
    if tcount is not None and tcounts is not None:
        raise ValueError("pass either tcount or tcounts, not both")

    requested = tcount if tcounts is None else tcounts
    if requested is None:
        return None
    if isinstance(requested, Integral) and not isinstance(requested, bool):
        values = [int(requested)]
    else:
        try:
            raw_values = list(requested)
        except TypeError as exc:
            raise TypeError(
                "tcount must be a nonnegative integer, and tcounts must be "
                "an iterable of nonnegative integers"
            ) from exc
        if any(isinstance(value, bool) or not isinstance(value, Integral)
               for value in raw_values):
            raise TypeError(
                "tcounts must contain only nonnegative integers"
            )
        values = [int(value) for value in raw_values]

    if not values:
        raise ValueError("tcounts must contain at least one value")
    if any(value < 0 for value in values):
        raise ValueError("T-counts must be nonnegative")
    return tuple(sorted(set(values)))


def search(k, N, target='T', d=2, level=3, backend='cpsat', symmetry=True,
           time_s=120, tcount=None, tcounts=None, verify=True, verbose=False,
           solver_kwargs=None):
    """Exhaustive minimum-T factory search over all columns of F_2^N.

    Returns a dict with status, n, N, k, verified distance d, and the explicit
    columns.  ``level`` is the Clifford level (2: S/CZ; 3: T/CS/CCZ; 4:
    sqrtT/CT/CCS/CCCZ) and sets the degree of the parity constraints.
    ``tcount`` fixes the T-count (feasibility mode) instead of minimising.
    ``tcounts`` accepts an iterable of exact counts; candidates are tried in
    ascending order and the first satisfiable count is returned.  The two
    parameters are mutually exclusive.  For CryptoMiniSat, ``solver_kwargs``
    is passed to ``Solver.solve`` (for example ``{'confl_limit': 1000000}``).
    ``symmetry`` toggles the completeness-preserving symmetry break.
    ``backend`` in {'cpsat', 'pysat', 'cryptominisat'}.
    """
    requested_tcounts = _normalise_tcounts(tcount, tcounts)
    # Every output wire has to exist.  Without this, k > N built target
    # monomials on qubits outside F_2^N and died with a bare KeyError deep in
    # the model instead of saying what was wrong.
    if N < 1:
        raise ValueError(f'N={N}: a circuit needs at least one qubit')
    if not 1 <= k <= N:
        raise ValueError(f'k={k} output qubits do not fit in N={N} total qubits '
                         f'(need 1 <= k <= N)')
    D = target_D(target, k, N, level)
    # width-1 gates on every output (T/S/sqrtT) are output-permutation symmetric
    symmetric_outputs = target in ('T', 'S', 'sqrtT')

    def solve_one(exact_tcount):
        args = (N, k, D, d, level, symmetry, symmetric_outputs, time_s,
                exact_tcount, solver_kwargs)
        if backend == 'cpsat':
            return _solve_cpsat(*args)
        if backend == 'pysat':
            return _solve_pysat(*args)
        if backend == 'cryptominisat':
            return _solve_cryptominisat(*args)
        raise ValueError(
            f'unknown backend {backend!r}; choose one of '
            "'cpsat', 'pysat', or 'cryptominisat' "
            "(spelled c-r-y-p-t-o-m-i-n-i-s-a-t)"
        )

    if requested_tcounts is None:
        res = solve_one(None)
    else:
        # Exact cardinality is intentionally used for every requested value;
        # this keeps the API and semantics identical across all three backends.
        unknown = None
        res = None
        for requested in requested_tcounts:
            candidate = solve_one(requested)
            if candidate['status'] in ('FEASIBLE', 'OPTIMAL'):
                res = candidate
                res['tcount_requested'] = requested
                break
            if candidate['status'] == 'UNKNOWN' and unknown is None:
                unknown = candidate
        if res is None:
            res = unknown or {'status': 'UNSAT', 'N': N}
        res['requested_tcounts'] = list(requested_tcounts)

    res.update(k=k, target=target, d_target=d, level=level, backend=backend)
    if res['status'] in ('UNSAT', 'UNKNOWN'):
        return res
    cols = _masks_to_columns(res['masks'], N)
    res['columns'] = cols
    if verify:
        colsets = [set(c) for c in cols]
        # exact distance, capped: a value of max(4, d) + 1 means "greater"
        vd = evaluator._distance([sum(1 << q for q in c) for c in cols], k, max(4, d))
        # target parity checked against the ACTUAL target D over degree<=level
        # monomials (works for entangled dict targets and levels 2/4 too)
        got = {mon for mon in monomials(N, level)
               if sum(1 for c in colsets if set(mon) <= c) & 1}
        target_ok = (got == {tuple(m) for m in D})
        res['verified'] = dict(n=len(cols), k=k, d=vd, N=N, target_ok=target_ok)
        res['d'] = vd
    if verbose:
        print(f"[{backend}] k={k} N={N} {target} d>={d}: "
              f"{res['status']} n={res.get('n')} d={res.get('d')}")
    return res


def run(k, N, target='T', d=2, tcount=None, tcounts=None, **kw):
    """Run a search and print a one-line [[n,k,d]] summary.

    tcount requests one exact T-count.  tcounts requests a set or iterable of
    exact counts; the lowest satisfiable value is returned.
    """
    r = search(k, N, target, d, tcount=tcount, tcounts=tcounts, **kw)
    tlabel = target if isinstance(target, str) else 'custom'
    requested = r.get('requested_tcounts')
    if requested:
        count_label = (f", Tcount={requested[0]}" if len(requested) == 1
                       else f", Tcounts={requested}")
    else:
        count_label = ''
    if r['status'] in ('UNSAT', 'UNKNOWN'):
        print(f"  k={k} N={N} {tlabel:>6} d>={d}{count_label}  "
              f"({r['backend']})  -> {r['status']}")
        return r
    v = r.get('verified', {})
    print(f"  k={k} N={N} {tlabel:>6} d>={d}{count_label}  ({r['backend']})  -> "
          f"[[{r['n']},{k},{r.get('d','?')}]]  {r['status']}  "
          f"target_ok={v.get('target_ok')}")
    return r


# ----------------------------------------------------------------------- CLI
def parse_target_monomials(spec):
    """``'0+01+012'`` -> ``{1: [(0,)], 2: [(0, 1)], 3: [(0, 1, 2)]}``.

    One digit per qubit, so this notation reaches output qubits 0-9 only.  That
    is the same limit the catalogues' own gate strings have and it is far above
    the widest factory known here (k=6); a target on more than ten outputs has
    to be built as a dict and passed to ``search`` directly.

    The catalogue's notation for a gate, and therefore the notation for asking
    for one: 18 of the 57 rows in ``catalog/factories.json`` deposit an entangled
    gate that no named target describes at that row's own k, and until this
    existed they could be re-verified from their columns but not re-SEARCHED from
    the CLI.
    ``target_D`` validates the result (output indices only, degree within the
    level), so a typo naming a check qubit is refused rather than solved.
    """
    by_degree = {}
    for token in spec.replace(",", "+").split("+"):
        token = token.strip()
        if not token:
            continue
        if not token.isdigit():
            raise ValueError(
                f"invalid monomial {token!r}: write each monomial as the digits "
                f"of its output qubits, e.g. 0+01+012")
        mon = tuple(sorted(int(ch) for ch in token))
        by_degree.setdefault(len(mon), []).append(mon)
    if not by_degree:
        raise ValueError("--target-monomials names no monomial")
    return by_degree


def reproduce(backend='cpsat'):
    """Reproduce the small distance-2 malleable base and the 15-to-1 (d=3)."""
    print(f'==== exhaustive SAT reproduction (backend={backend}) ====')
    run(1, 4, 'T',   2, backend=backend)     # [[14,1,2]]
    run(2, 4, 'CS',  2, backend=backend)     # [[12,2,2]]
    run(3, 4, 'CCZ', 2, backend=backend)     # [[8,3,2]]
    run(1, 5, 'T',   3, backend=backend, time_s=120)   # [[15,1,3]]


def main(argv=None):
    """Run one ansatz-free SAT search and optionally save its explicit circuit."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--k", type=int, required=True, help="number of outputs")
    parser.add_argument("--N", type=int, required=True, help="total qubits")
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument(
        "--target", choices=tuple(_NAMED), help="named target gate",
    )
    target_group.add_argument(
        "--target-monomials", help=(
            "custom target in the catalogue's own notation: '+'-joined "
            "monomials of OUTPUT qubit digits, e.g. 0+01+012 for T0.CS01.CCZ012. "
            "This is the shape of the catalogue's CUSTOM rows. One digit per "
            "qubit, so output indices 0-9"),
    )
    parser.add_argument("--distance", type=int, choices=(2, 3, 4), default=3)
    parser.add_argument("--level", type=int, choices=(2, 3, 4), default=3)
    parser.add_argument(
        "--backend", choices=("cpsat", "pysat", "cryptominisat"), default="cpsat"
    )
    parser.add_argument("--time", type=float, default=120, help="solver time limit")
    parser.add_argument("--tcount", type=int, help="require this exact T-count")
    parser.add_argument("--output", help="write the complete result as JSON")
    args = parser.parse_args(argv)
    try:
        target = (args.target if args.target
                  else parse_target_monomials(args.target_monomials))
        result = run(
            args.k, args.N, target, args.distance, level=args.level,
            backend=args.backend, time_s=args.time, tcount=args.tcount,
        )
    except ValueError as error:            # invalid target/k/level combination
        parser.error(str(error))
    if args.output:
        path = os.path.abspath(args.output)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)
            handle.write("\n")
        print(f"wrote {path}")
    # A solver status is not a result.  If the independent column-level check
    # disagrees with what the model claimed -- wrong target parities, or a
    # distance below the one requested -- that is a failure of this run and must
    # not exit 0, however confidently the solver said OPTIMAL.
    verified = result.get("verified")
    if verified is not None:
        problems = []
        if not verified.get("target_ok"):
            problems.append("the expanded circuit does not deposit the requested "
                            "target on the outputs")
        got_d = verified.get("d")
        if isinstance(got_d, int) and got_d < args.distance:
            problems.append(f"verified distance {got_d} < requested "
                            f"{args.distance}")
        if problems:
            print("FAILED independent verification:", file=sys.stderr)
            for problem in problems:
                print(f"  - {problem}", file=sys.stderr)
            return 1
    if result["status"] == "UNKNOWN":
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
