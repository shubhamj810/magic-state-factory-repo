#!/usr/bin/env python3
"""
EXACT minimum-T-count distance >= 4 search in the slot ansatz, per geometry.

The slot rule alone guarantees d>=3 structurally, so we drop the triple-rule
over-approximation and instead run CEGAR (lazy constraints):

  1. minimise T-count subject to the slot rule + target parity only;
  2. verify the true distance of the optimal solution;
  3. if some undetected weight-3 logical fault exists, forbid exactly that
     (slot,output) combination and re-solve;
  4. stop when the CP-SAT optimum verifies as d>=4 -- that n is then the
     EXACT slot-ansatz optimum for the geometry (every added clause removes
     only genuinely d<4 configurations, so the relaxed optimum, once it lands
     in the true-feasible set, equals the true optimum).

Run:  ./.venv/bin/python exact_d4.py
"""
import argparse
import itertools
import time
from ortools.sat.python import cp_model
from slot_search import Geometry


def _tbit(mon, k, target):
    """Required parity of a monomial class: 1 iff mon is a target output
    monomial; check-touching monomials must be even.  Named targets only
    ('T', 'CS', 'CCZ') -- unlike slot_search.solve, custom set targets are
    NOT supported here (they silently read as the all-zero target)."""
    Q, Ts = mon
    if any(len(T) for T in Ts):
        return 0
    if target == 'T' and len(Q) == 1:
        return 1
    if target == 'CS' and Q == (0, 1):
        return 1
    if target == 'CCZ' and Q == (0, 1, 2):
        return 1
    return 0


def _columns_tagged(g, assignment):
    """Return [(support_frozenset, slot_id)] with slot_id indexing assignment."""
    starts, s = [], g.k
    for b in g.blocks:
        starts.append(s)
        s += b[1]
    out = []
    for sid, (lab, P) in enumerate(assignment):
        pools = []
        for i, j in enumerate(lab):
            pools.append([frozenset(starts[i] + q for q in S)
                          for S in g.orbits[i][j]])
        for combo in itertools.product(*pools):
            supp = set(P)
            for c in combo:
                supp |= c
            out.append((frozenset(supp), sid))
    return out


def _bad_triples_all(cols_tagged, k, cap=400):
    """Return up to `cap` DISTINCT slot-id sets, each certifying an undetected
    weight<=3 logical fault present in the current selection (None-> empty ->
    d>=4).  Assumes the slot rule (d>=3) holds, so faults have weight exactly 3
    generically; weight 1/2 are checked defensively."""
    masks, sid = [], []
    for supp, s in cols_tagged:
        m = 0
        for q in supp:
            m |= 1 << q
        masks.append(m)
        sid.append(s)
    n = len(masks)
    outm = (1 << k) - 1

    def bad(v):
        return v != 0 and (v & ~outm) == 0

    # a clause is the SET of slots involved; columns sharing a slot collapse
    # under frozenset, yielding a shorter (stronger) but still sound no-good
    clauses = set()
    for i in range(n):
        if bad(masks[i]):
            clauses.add(frozenset({sid[i]}))
    pairval = {}
    for i, j in itertools.combinations(range(n), 2):
        v = masks[i] ^ masks[j]
        if bad(v):
            clauses.add(frozenset({sid[i], sid[j]}))
        pairval.setdefault(v, []).append((i, j))
    for t in range(1, 1 << k):
        for i in range(n):
            for (a, b) in pairval.get(masks[i] ^ t, []):
                if i not in (a, b):
                    clauses.add(frozenset({sid[i], sid[a], sid[b]}))
                    if len(clauses) >= cap:
                        return list(clauses)
    return list(clauses)


def exact_solve(k, blocks, target, time_s=120, max_iters=4000, verbose=True,
                allowed_costs=None, allowed_labels=None, deadline_s=None):
    """Exact minimum-T d>=4 optimum of one geometry via CEGAR.

    Each iteration: CP-SAT minimises the T-count under the slot rule +
    target parities + the no-good clauses accumulated so far; the incumbent
    is distance-verified, and every surviving undetected weight<=3 fault is
    forbidden as a clause over its (label, P) slots.  A no-good removes
    only genuinely d<4 selections (the fault recurs whenever those slots
    are all chosen), so the first OPTIMAL incumbent that verifies d>=4 is
    the exact ansatz optimum; a timed-out relaxation cannot certify, hence
    FEASIBLE_TIMEOUT.  ``allowed_costs`` restricts slots by orbit size;
    ``allowed_labels`` filters on lab[0], the FIRST block's orbit index
    (equivalent to whole-label filtering only for single-block geometries).

    ``time_s`` is the CP-SAT limit for ONE iteration and ``max_iters`` bounds
    the count, so the worst case is their product -- ``--time 180`` could run
    for days before reporting.  ``deadline_s`` bounds the whole call instead:
    when it passes, the loop stops and returns ``status='DEADLINE'`` with the
    iteration count, rather than a result that looks like an optimum.
    """
    # _tbit understands the three named level-3 targets and reads anything else
    # as the all-zero target, which would return a "d>=4 optimum" for the empty
    # gate.  Say so instead.
    if target not in ('T', 'CS', 'CCZ'):
        raise ValueError(
            f'exact_d4 supports the named targets T, CS and CCZ only, not '
            f'{target!r}; slot_search.solve takes custom targets')
    width = {'T': 1, 'CS': 2, 'CCZ': 3}[target]
    if width > k:
        raise ValueError(f'target {target!r} acts on {width} output qubits but '
                         f'k={k}: a width-{width} gate needs k >= {width}')
    started = time.monotonic()
    g = Geometry(k, blocks)
    mons = g.monomials()
    Ps = [tuple(P) for s in range(k + 1)
          for P in itertools.combinations(range(k), s)]
    forbidden = []                 # each: list of (label_index, P)
    tag = '+'.join(f'{b[0]}{b[1]}' for b in blocks)
    allowed = set(allowed_costs) if allowed_costs is not None else None
    allowed_li = set(allowed_labels) if allowed_labels is not None else None

    for it in range(max_iters):
        if deadline_s is not None and time.monotonic() - started > deadline_s:
            return {'status': 'DEADLINE', 'N': g.N, 'iters': it,
                    'elapsed_s': round(time.monotonic() - started, 1)}
        m = cp_model.CpModel()
        x = {}
        for li, lab in enumerate(g.labels):
            for P in Ps:
                x[li, P] = m.NewBoolVar(f'x_{li}_{P}')
            m.AddAtMostOne(x[li, P] for P in Ps)          # slot rule => d>=3
            if allowed is not None and g.label_cost(lab) not in allowed:
                for P in Ps:
                    m.Add(x[li, P] == 0)
            if allowed_li is not None and lab[0] not in allowed_li:
                for P in Ps:
                    m.Add(x[li, P] == 0)
        tvar = m.NewBoolVar('t')
        m.Add(tvar == 1)
        for mon in mons:
            Q = set(mon[0])
            lits = [x[li, P] for li, lab in enumerate(g.labels)
                    if g.coeff(lab, mon) for P in Ps if Q <= set(P)]
            want = _tbit(mon, k, target)
            if not lits:
                if want:
                    return {'status': 'UNSAT', 'N': g.N, 'iters': it}
                continue
            m.AddBoolXOr(lits + ([tvar] if want == 0 else []))
        for clause in forbidden:
            m.AddBoolOr([x[li, P].Not() for (li, P) in clause])
        m.Minimize(sum(g.label_cost(g.labels[li]) * x[li, P]
                       for li in range(len(g.labels)) for P in Ps))

        sol = cp_model.CpSolver()
        sol.parameters.max_time_in_seconds = time_s
        sol.parameters.num_search_workers = 8
        st = sol.Solve(m)
        if st == cp_model.INFEASIBLE:
            return {'status': 'UNSAT', 'N': g.N, 'iters': it}
        if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return {'status': 'UNKNOWN', 'N': g.N, 'iters': it}
        optimal = (st == cp_model.OPTIMAL)
        asg, sid_of = [], {}       # sid_of: column-tag slot id -> (li, P)
        for li, lab in enumerate(g.labels):
            for P in Ps:
                if sol.Value(x[li, P]):
                    sid_of[len(asg)] = (li, P)
                    asg.append((lab, P))
        n = int(sol.ObjectiveValue())
        cols = _columns_tagged(g, asg)
        bad = _bad_triples_all(cols, k)
        if not bad:
            return {'status': 'OPTIMAL' if optimal else 'FEASIBLE',
                    'n': n, 'N': g.N, 'iters': it, 'assignment': asg,
                    'geometry': g}
        if not optimal:
            # can't certify exactness if the solve itself timed out
            return {'status': 'FEASIBLE_TIMEOUT', 'n': n, 'N': g.N,
                    'iters': it, 'assignment': asg, 'geometry': g,
                    'note': 'incumbent had d<4; solve timed out before proof'}
        for bset in bad:
            forbidden.append([sid_of[s] for s in bset])
        if verbose:
            print(f'    [{tag}] iter {it}: n={n} d<4, +{len(bad)} clauses '
                  f'({len(forbidden)} total)', flush=True)
    return {'status': 'ITERCAP', 'N': g.N, 'iters': max_iters}


def run_exact(k, target, geoms, time_s=120, deadline_s=None):
    """exact_solve each geometry, re-verify the columns independently, and
    print one [[n,k,d]] summary line per geometry.

    Returns the number of geometries that did NOT end in a verified optimum, so
    the CLI can exit nonzero.  UNKNOWN, ITERCAP and DEADLINE are all "no answer
    yet", and exiting 0 on them would make a script treat them as results.
    FEASIBLE counts too: the columns are a real verified d>=4 circuit, but the
    solve that produced them timed out before proving MINIMALITY, and exactness
    is the entire claim this module exists to make.  Only OPTIMAL and UNSAT are
    answers.
    """
    print(f'==== EXACT k={k} target={target} d>=4 ====', flush=True)
    from slot_search import columns_of, verify
    unresolved = 0
    for blocks in geoms:
        r = exact_solve(k, blocks, target, time_s=time_s, deadline_s=deadline_s)
        tag = '+'.join(f'{b[0]}{b[1]}' for b in blocks)
        if r['status'] in ('UNSAT', 'UNKNOWN', 'ITERCAP', 'DEADLINE'):
            if r['status'] != 'UNSAT':
                unresolved += 1
            print(f'  {tag:12s} N={r["N"]:3d}  {r["status"]}  '
                  f'(iters={r.get("iters")}'
                  + (f', {r["elapsed_s"]}s' if 'elapsed_s' in r else '')
                  + ')', flush=True)
            continue
        g = r['geometry']
        cols = columns_of(g, r['assignment'])
        ok, d = verify(k, g.N, cols, target, dmax=4)
        print(f'  {tag:12s} N={r["N"]:3d}  n={r["n"]:4d}  '
              f'[[{r["n"]},{k},{d}]]  {r["status"]}  '
              f'iters={r["iters"]}  data_ok={ok}', flush=True)
        short = isinstance(d, int) and d < 4
        if not ok or short:
            unresolved += 1
            why = [] if ok else ['target parities are wrong']
            if short:
                why.append(f'verified distance {d} < 4')
            print(f'      FAILED independent verification: {"; ".join(why)}',
                  flush=True)
        elif r['status'] != 'OPTIMAL':
            unresolved += 1
            print(f'      NOT AN EXACT OPTIMUM: status {r["status"]} -- these '
                  f'columns are a verified d>=4 factory at n={r["n"]}, but the '
                  f'solve timed out before proving no smaller one exists',
                  flush=True)
    return unresolved


def main(argv=None):
    """Run exact distance-four CEGAR on one or more slot geometries."""
    from slot_search import parse_geometry

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--k", type=int, required=True)
    parser.add_argument("--target", choices=("T", "CS", "CCZ"), required=True)
    parser.add_argument(
        "--geometry", action="append", required=True,
        help="S/C block geometry such as C9 or S3+C4; repeatable",
    )
    parser.add_argument("--time", type=float, default=180,
                        help="CP-SAT limit for ONE CEGAR iteration")
    parser.add_argument("--deadline", type=float, default=None, help=(
        "wall-clock limit for the WHOLE search of each geometry, in seconds. "
        "Without it the worst case is --time x 4000 iterations, which can run "
        "for days; on expiry the geometry reports DEADLINE and the exit code "
        "is nonzero"))
    args = parser.parse_args(argv)
    try:
        geometries = [parse_geometry(spec) for spec in args.geometry]
    except ValueError as error:
        parser.error(str(error))
    try:
        unresolved = run_exact(args.k, args.target, geometries,
                               time_s=args.time, deadline_s=args.deadline)
    except ValueError as error:            # invalid target/width combination
        parser.error(str(error))
    return 1 if unresolved else 0


if __name__ == '__main__':
    raise SystemExit(main())
