#!/usr/bin/env python3
r"""MAIN ENGINE -- exhaustive quotient-space classification of every
distance >= 3 factory with n <= 38 physical injections.

WHAT THIS COMPUTES
------------------
For every classified check-part support at physical length n (a *marked*
Nezami--Haah / KTA affine class representative, supplied by
``nezami_haah_reps.py``), enumerate **every** way of attaching k output rows
that yields a distance >= 3 factory, read off the logical gate, and deduplicate
by the S_k canonical gate (``dedup.sk_canonical`` -- see that module: the key
is S_k, output permutations only).  The answer is target-agnostic: it says
which gates exist *at all* at T count n and distance 3, rather than solving for
one requested gate.

THE QUOTIENT TRICK
------------------
Work not in the row code but in

    R(C) = { a in F_2^n : a . h_i = 0 and a . (h_i ^ h_j) = 0 for all checks }
    C    = span of the check rows h_i                    ( C subset R(C) )
    V    = R(C) / C

where ``a . b`` is the F_2 inner product and ``a ^ b`` the POINTWISE product
(AND) of row vectors, not XOR.  Every degree-<=3 logical parity (single |a|,
pair |a ^ b|, triple |a ^ b ^ c|) and the mixed output-output-check condition
|a ^ b ^ h_j| = 0 is invariant under a -> a + c for c in C, so the entire
classification descends to V.  Across the whole n <= 38 ladder dim V <= 11
(audited), against an unquotiented row-code dimension of up to 16 -- the
factor-2^r saving that makes the enumeration *complete*, with no node budget
consumed, on every parent but one.

WHAT A FACTORY IS, IN THESE COORDINATES
---------------------------------------
A k-output factory is a linearly independent k-subset (a *frame*) of V whose
every pair (a, b) is "compatible", meaning the r bilinear forms

    B_j(a, b) = < a, b ^ h_j >          (one per check qubit j)

all vanish.  Compatible frames are exactly the cliques of the compatibility
graph on V \ {0}.  The frame's logical gate is read off its degree-1/2/3
parities; its distance is then verified by exact fault enumeration in
``factorylib.verification``, which shares no enumeration code with this file.

THE ONE HARD PARENT
-------------------
n = 31 has a parent of exceptional symmetry -- the 31 nonzero points of F_2^5,
whose linear automorphism group is all of GL(5,2) (order 9,999,360).  Plain
frame enumeration does not finish there.  ``hard_parent_n31.py`` settles it by
collapsing the search along that automorphism group; the result is folded into
the shipped catalogue.  Every other parent completes here without a budget hit.

SCOPE -- WHAT "EXHAUSTIVE" COVERS, AND WHAT IT DOES NOT
-------------------------------------------------------
The enumeration is exhaustive over factories whose k output rows are linearly
independent **modulo the check span C**.  Frames whose rows collapse mod C are
not enumerated.  That sounds like a gap; it is not one, and the reason is worth
stating precisely, because the obvious first reaction -- "adding a check row to
an output cannot change anything, so who cares?" -- is right about the premise
and would be wrong about the conclusion if you stopped there.

The premise is exactly right.  Replacing a single output row a by a + c for
c in C changes nothing: |a + c| = |a| mod 2 since check rows have even weight,
and |(a + c) & b| = |a & b| mod 2 since R(C) lies in the dual of C.  That
invariance is the whole descent argument -- it is why gates are functions of V
at all.

The case this engine skips is different: it is a frame that uses BOTH a and
a + c as two SEPARATE output qubits.  That is a larger circuit on more qubits,
not a re-labelling, and its gate really is different: |a| odd, |a + c| odd, and
|a & (a + c)| = |a| - |a & c| odd, so the gate is `0+1+01`, i.e. T_0 . T_1 . CS_01.

THE OMISSION COSTS NO MAGIC.  One output CNOT sends the second row a + c to
(a + c) + a = c, which lies in C and therefore carries nothing at all: |c| is
even; |c & a'| is even for every a' in R(C); and |c & a' & a''| is even for
every compatible pair, because compatibility says |a' & a'' & h_j| is even for
each check row and that extends to all of C by the same parity argument.  So
after one Clifford the extra output is an idle |+> spectator and what remains is
precisely the lower-width factory this engine did enumerate.  The arithmetic
agrees: T_0 . T_1 . CS_01 has exact minimal T count 1, not 2, because
x0 + x1 + 2 x0 x1 = (x0 XOR x1) + 4 x0 x1 -- one T on the parity of the two
outputs, times a CZ.

So the catalogue is complete for magic CONTENT -- which gates are achievable at
each n, the largest genuine output width, the largest exact T count -- and
incomplete only for circuit REPRESENTATIONS in which some output is
Clifford-equivalent to an idle spectator.  Note that `record` below already
discards frames with a *manifestly* idle output (the `covered` check); skipping
lift-degenerate frames is the same policy one Clifford deeper, not a different
one.

Two honest caveats on top of that.  First, the quotient method could not include
these frames even if we wanted them: their gate depends on WHICH lift of a
quotient point is chosen, so it is not a function of V, and the descent argument
that removes the node budget is exactly the statement that gates are functions
of V.  Enumerating them needs the row space (`classify_rowspace.py`) or raw
column-level search.  Second, if you are counting distinct *circuits* rather
than distinct resources -- for instance because a spectator output is free in
your architecture and you would rather have the CZ than the CNOT -- then the
catalogue undercounts, and `classify_rowspace.py` is the tool.

A concrete example: ansatz-free column-level SAT finds a [[15,2,3]] with gate
`0+1+01` over the [[15,1,3]] check part, its second output row a verbatim copy
of the first -- 6 rows of rank 5, exact T count 1.  It is deliberately NOT in
the search catalogue: that builder rejects a declared width whose output rows
are dependent mod the check span, because the circuit is the [[15,1,3]] with a
spare wire (see ../../../symmetry_sat_search/examples/README.md).  The row-space
enumerator reaches these frames, and `tests/test_classification.py` builds them
at the small end of the ladder and proves both the characterisation and the
no-extra-magic theorem there.

OUTPUT
------
``results/quotient_catalog_<tag>.json``: one record per distinct
(n, k, S_k-canonical gate), keeping the largest distance seen among that
signature's first ``CAP`` witnesses (see ``CAP`` below), with explicit columns,
the GL(k,2) annotation, and per-n statistics.

Each stored circuit is written IN ITS CANONICAL OUTPUT FRAME: ``record`` applies
the permutation that canonicalises the gate to the output qubit labels before
building the columns, so the columns deposit exactly the ``gate`` string the
record is filed under.  Relabelling output wires touches nothing else -- n, N,
every check parity and the fault distance are unchanged -- and it means a reader
can read the gate off the shipped columns and get the printed string back,
rather than a permuted version of it that only agrees up to S_k.

Algorithm write-up: ``docs/ALGORITHM_STEP_BY_STEP.md``.
Completeness argument: ``docs/THEORY_EXHAUSTIVENESS.md``.
"""

import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))          # run from anywhere: siblings by bare name
sys.path.insert(0, str(HERE.parents[2]))  # shared factorylib package

from nezami_haah_reps import BY_WEIGHT, VALID_NS                  # noqa: E402
from marking import (support_of, row_space_rows, nullspace_basis,  # noqa: E402
                     marked_even, marked_odd)
from factorylib.verification import verify                        # noqa: E402
from dedup import (canonical_gate, sk_canonical_with_perm,        # noqa: E402
                   sk_name)

RESULTS = HERE / 'results'


# ------------------------------------------------------------------ parents
def marked_all(n):
    """Yield (class_index, r, check_tuple) for every marked support at length n."""
    weight = n + (n % 2)
    if weight not in BY_WEIGHT:
        raise ValueError(
            f'n={n} needs check-support weight {weight}, which is outside the '
            f'classified window of this directory (weights '
            f'{sorted(BY_WEIGHT)}, i.e. n <= 38).')
    reps = BY_WEIGHT[weight]
    marker = marked_even if (n % 2 == 0) else marked_odd
    for ci, (m, terms) in enumerate(reps):
        if len(support_of(m, terms)) != weight:
            raise ValueError(
                f"class {ci} of weight {weight} has support "
                f"{len(support_of(m, terms))}: the input table in "
                f"nezami_haah_reps.py does not say what this sweep assumes")
        for r, cs in marker(m, terms):
            yield ci, r, cs


# --------------------------------------------------------- linear-algebra
def rref_basis(vecs):
    """Reduced-row-echelon basis (pivot -> row) of the span of `vecs`.

    Fully reduced: each pivot bit occurs in exactly one basis row, so a
    single high-to-low pass in reduce_mod yields the unique coset
    representative that is zero at every pivot."""
    basis = {}
    for v in vecs:
        x = v
        for p in sorted(basis, reverse=True):
            if (x >> p) & 1:
                x ^= basis[p]
        if x:
            p = x.bit_length() - 1
            for q, row in list(basis.items()):
                if (row >> p) & 1:
                    basis[q] = row ^ x
            basis[p] = x
    return basis


def reduce_mod(v, rref):
    """Canonical representative of v mod the span of `rref` (pivots cleared)."""
    for p in sorted(rref, reverse=True):
        if (v >> p) & 1:
            v ^= rref[p]
    return v


def quotient_reps(check_tuple, r):
    """Return (Vreps, hlist) for one parent.

    Vreps[x] is the canonical F_2^n representative (zero in the C-pivot columns)
    of quotient element x in {0,..,2^dimV-1}; the coordinate of Vreps[x] is x.
    hlist is the list of the r deg-1 check rows h_j (as F_2^n ints).
    Also returns Qbasis (the C-reduced basis vectors of V, so x -> Vreps[x] is
    linear) and n.  Row ints are bit-packed with bit i = column i."""
    checks = tuple(check_tuple)
    n = len(checks)
    rows1 = row_space_rows(checks, r, 1)   # [all-ones, h_1..h_r]
    rows2 = row_space_rows(checks, r, 2)   # [all-ones, deg1, deg2]
    hlist = rows1[1:]
    Rbasis = nullspace_basis(rows2[1:], n)         # basis of R(C)
    Crref = rref_basis(hlist)                      # basis of C  (C subset R)
    # complement basis of C in R: reduce R generators mod C, keep independents
    qb_rref = {}
    Qbasis = []
    for v in Rbasis:
        w = reduce_mod(v, Crref)
        x = w
        for p in sorted(qb_rref, reverse=True):
            if (x >> p) & 1:
                x ^= qb_rref[p]
        if x:
            p = x.bit_length() - 1
            qb_rref[p] = x
            Qbasis.append(w)          # keep the actual (C-reduced) rep vector
    dimV = len(Qbasis)
    # enumerate span in coordinate order: Vreps[x] = XOR of Qbasis[b] for bit b in x
    Vreps = [0] * (1 << dimV)
    for x in range(1 << dimV):
        acc = 0
        xx = x
        while xx:
            b = (xx & -xx).bit_length() - 1
            acc ^= Qbasis[b]
            xx &= xx - 1
        Vreps[x] = acc
    return Vreps, hlist, Qbasis, n


# --------------------------------------------------------- compatibility
def compat_adjacency(Vreps, hlist, Qbasis):
    """Boolean numpy adjacency over the 2^dimV quotient points (0 excluded via
    caller).  compatible(x,y) iff < Vreps[x], Vreps[y] ^ h_j > = 0 for all j.

    Built from the r bilinear forms M_j[b][c] = parity(Qb & Qc & h_j) on the
    dimV basis coordinates, so cost is O(r * (2^dimV) * dimV^2) matmuls."""
    dimV = len(Qbasis)
    size = 1 << dimV
    # coordinate bit-matrix X: rows = points, cols = basis bits (vectorised)
    xs = np.arange(size, dtype=np.int64)
    # float64 so the matmuls hit BLAS; entries of X M X^T are integer sums of at
    # most dimV^2 <= ~170 zero/one products, exactly representable, so `% 2` is
    # bit-identical to the previous int64 `& 1`.  This is the hot path on the
    # largest parents in the ladder (int64 matmul is unaccelerated, ~100x slower).
    X = ((xs[:, None] >> np.arange(dimV, dtype=np.int64)[None, :]) & 1
         ).astype(np.float64)
    comp = np.ones((size, size), dtype=bool)
    for h in hlist:
        M = np.zeros((dimV, dimV), dtype=np.float64)
        for b in range(dimV):
            qb = Qbasis[b] & h
            for c in range(dimV):
                M[b, c] = (qb & Qbasis[c]).bit_count() & 1
        Bj = (X @ M) @ X.T              # exact integer values in float64
        comp &= (np.mod(Bj, 2.0) < 0.5)  # parity even <=> compatible
    return comp


# --------------------------------------------------------- gate + record
def frame_wants(Vreps, frame):
    """Logical gate of a frame of quotient coordinates: the set of output
    monomials {i}/{i,j}/{i,j,l} whose parity |a_i|, |a_i & a_j|,
    |a_i & a_j & a_l| is odd.  Well defined on cosets (gauge-invariant under
    a -> a+c, c in C): checks have even weight and the mixed terms vanish for
    rows in R(C) -- see ALGORITHM_STEP_BY_STEP.md, step 5."""
    k = len(frame)
    a = [Vreps[x] for x in frame]
    wants = set()
    for i in range(k):
        if a[i].bit_count() & 1:
            wants.add(frozenset((i,)))
    for i in range(k):
        for j in range(i + 1, k):
            if (a[i] & a[j]).bit_count() & 1:
                wants.add(frozenset((i, j)))
    for i in range(k):
        for j in range(i + 1, k):
            for l in range(j + 1, k):
                if (a[i] & a[j] & a[l]).bit_count() & 1:
                    wants.add(frozenset((i, j, l)))
    return wants


def build_columns(check_tuple, r, k, a_vectors):
    """Explicit factory columns: column idx carries output qubit q iff bit idx
    of row a_vectors[q] is set, and check qubit k+bit iff the parent point
    checks[idx] has that bit (outputs 0..k-1 first, then the r checks)."""
    checks = tuple(check_tuple)
    cols = []
    for idx, s in enumerate(checks):
        col = {q for q in range(k) if (a_vectors[q] >> idx) & 1}
        for bit in range(r):
            if (s >> bit) & 1:
                col.add(k + bit)
        cols.append(frozenset(col))
    return cols


def indep(basis_rref, x):
    """Reduce coordinate integer x by rref-basis dict; return residual (0 if dep)."""
    v = x
    for p in sorted(basis_rref, reverse=True):
        if (v >> p) & 1:
            v ^= basis_rref[p]
    return v


# --------------------------------------------------------- per-parent search
def classify_parent(check_tuple, r, kmax, seen, dist_calls, budget):
    """Enumerate compatible independent frames of size 2..kmax; update `seen`
    (sig -> best record).  Returns (nodes, hit_budget).

    (Singleton frames are recorded too -- see extend() -- so every size
    1..kmax is covered; frames are strictly increasing coordinate tuples, so
    each frame set is visited exactly once.)"""
    Vreps, hlist, Qbasis, n = quotient_reps(check_tuple, r)
    dimV = len(Qbasis)
    if dimV < 1:
        return 0, False              # no nonzero output possible
    comp = compat_adjacency(Vreps, hlist, Qbasis)
    size = 1 << dimV
    # neighbour bitmasks (exclude 0 and self), packed from the boolean rows
    verts = list(range(1, size))
    adj = [0] * size
    packed = np.packbits(comp, axis=1, bitorder='little')  # rows -> bytes
    for x in verts:
        m = int.from_bytes(packed[x].tobytes(), 'little')
        m &= ~1                       # drop vertex 0
        m &= ~(1 << x)                # drop self
        adj[x] = m

    nodes = [0]
    hit = [False]
    # Max distance-verify calls per signature.  It bounds runtime without
    # affecting WHICH signatures are found -- only the distance recorded for one:
    # a signature's stored distance is the best over its first <= CAP witnesses,
    # not over all of them.  Harmless here because every class in the shipped
    # window comes out at d = 3 (a marked parent forbids weight-1 and weight-2
    # faults, so d >= 3 always, and no row reaches 4).
    CAP = 60

    def record(frame):
        wants = frame_wants(Vreps, frame)
        if not wants:
            return
        k = len(frame)
        covered = set()
        for Q in wants:
            covered |= set(Q)
        if len(covered) != k:
            return                    # some logical qubit unused -> smaller gate
        pc, perm = sk_canonical_with_perm(k, wants)
        sig = (n, k, pc)
        rec = seen.get(sig)
        if rec is not None and dist_calls[sig] >= CAP:
            return
        # Store the witness IN THE CANONICAL FRAME: relabel output i -> perm[i]
        # so the stored columns deposit exactly `pc`, the gate string this row
        # is filed and printed under.  Without this the label would be the S_k
        # representative while the circuit realised whichever labelling the
        # enumeration happened to reach, and a reader checking one against the
        # other would find a mismatch on a perfectly good row.
        a_vectors = [0] * k
        for i, x in enumerate(frame):
            a_vectors[perm[i]] = Vreps[x]
        canonical_wants = {frozenset(perm[i] for i in Q) for Q in wants}
        cols = build_columns(check_tuple, r, k, a_vectors)
        # Marked-parent points are distinct and nonzero, so no two columns can
        # share a check part and repeated columns are impossible here; a repeat
        # would be a weight-2 logical fault, i.e. outside this distance >= 3
        # classification entirely (docs/ALGORITHM_STEP_BY_STEP.md, step 6).
        if len(set(cols)) != len(cols):
            raise AssertionError('repeated column from a marked parent')
        ok, dist = verify(k, k + r, cols, canonical_wants, dmax=4)
        if not ok:
            raise AssertionError('enumerated frame failed parity verify')
        dist_calls[sig] = dist_calls.get(sig, 0) + 1
        dval = dist if isinstance(dist, int) else 5   # ">4" -> treat as 5
        if rec is None or dval > rec['_dval']:
            seen[sig] = {
                'n': n, 'k': k, 'r': r, 'rows': k + r,
                'distance': dist, '_dval': dval,
                'gate': sk_name(pc),
                'gate_gl_canonical': canonical_gate(k, wants),
                'columns': [sorted(c) for c in cols],
                'class_index': None,
            }

    def extend(frame, cand_mask, basis_rref):
        # record current frame (singleton T gates included for validation)
        if len(frame) >= 1:
            record(frame)
        if len(frame) == kmax:
            return
        m = cand_mask
        while m:
            y = (m & -m).bit_length() - 1
            m &= m - 1
            if y <= frame[-1]:
                continue          # strictly increasing coords: each set once
            res = indep(basis_rref, y)
            if res == 0:
                continue              # dependent -> not a genuine new logical
            nodes[0] += 1
            if nodes[0] > budget:
                hit[0] = True
                return
            new_rref = dict(basis_rref)
            p = res.bit_length() - 1
            new_rref[p] = res
            extend(frame + (y,), cand_mask & adj[y], new_rref)
            if hit[0]:
                return

    for x in verts:
        nodes[0] += 1
        if nodes[0] > budget:
            hit[0] = True
            break
        extend((x,), adj[x], {x.bit_length() - 1: x})
        if hit[0]:
            break
    return nodes[0], hit[0]


# --------------------------------------------------------- driver
def run(ns, kmax, budget, skip_classes=()):
    """Classify every marked parent at each n in `ns`.

    skip_classes: class indices to defer (their parents are not enumerated
    here), recorded in `deferred[n]`.  Provided so a high-symmetry parent can be
    peeled off and handled by an automorphism collapse instead -- that is how
    n = 31's F_2^5 parent is treated (see hard_parent_n31.py)."""
    skip_classes = set(skip_classes)
    seen = {}
    dist_calls = {}
    partial = defaultdict(set)
    deferred = defaultdict(set)
    stats = {}
    for n in ns:
        t0 = time.monotonic()
        npar = 0
        for ci, r, cs in marked_all(n):
            if ci in skip_classes:
                deferred[n].add(ci)
                continue
            npar += 1
            before = dict(seen)  # noqa (kept for possible per-class attribution)
            nd, ph = classify_parent(cs, r, kmax, seen, dist_calls, budget)
            if ph:
                partial[n].add(ci)
            # attribute class_index to any signatures newly created at this n
            for sig, rec in seen.items():
                if sig[0] == n and rec['class_index'] is None:
                    rec['class_index'] = ci
        stats[n] = {'parents': npar, 'seconds': round(time.monotonic() - t0, 2),
                    'gates_le_n': sum(1 for s in seen if s[0] == n)}
        print(f'n={n:2d}: {npar:4d} parents, {stats[n]["gates_le_n"]:3d} distinct '
              f'gates(n), {stats[n]["seconds"]}s'
              f'{"  [PARTIAL:"+str(sorted(partial[n]))+"]" if n in partial else ""}'
              f'{"  [DEFERRED:"+str(sorted(deferred[n]))+"]" if n in deferred else ""}',
              flush=True)
    return seen, dict(partial), stats, dict(deferred)


def main():
    """CLI: classify --ns at --kmax and write
    results/quotient_catalog_<tag>.json."""
    ap = argparse.ArgumentParser()
    ap.add_argument('--ns', nargs='+', type=int, default=list(VALID_NS),
                help='physical lengths to classify (default: the whole n<=38 ladder)')
    ap.add_argument('--kmax', type=int, default=2)
    ap.add_argument('--budget', type=int, default=50_000_000)
    ap.add_argument('--tag', type=str, default=None)
    ap.add_argument('--skip-classes', nargs='*', type=int, default=[],
                    help='class indices to defer to a separate hard-parent run')
    args = ap.parse_args()

    seen, partial, stats, deferred = run(args.ns, args.kmax, args.budget,
                                         skip_classes=args.skip_classes)
    # strip private keys
    factories = []
    for rec in sorted(seen.values(), key=lambda r: (r['n'], r['k'], r['gate'])):
        rec = dict(rec)
        rec.pop('_dval', None)
        factories.append(rec)
    byk = Counter((r['n'], r['k']) for r in factories)
    RESULTS.mkdir(parents=True, exist_ok=True)
    tag = args.tag or f'k{args.kmax}'
    out = RESULTS / f'quotient_catalog_{tag}.json'
    nmax = max(args.ns) if args.ns else 38
    # A pass is `complete` only if no parent hit its node budget.  Deferred
    # classes do NOT spoil it -- deferring is how the n=31 parent is peeled off
    # for hard_parent_n31.py -- but they are listed so the consolidating builder
    # can insist that another input covers them.  Without this field the builder
    # had no way to tell an exhausted pass from a truncated one.
    ns_swept = sorted(args.ns)
    complete = not partial
    out.write_text(json.dumps({
        'scope': f'distance>=3 output-marked factories, quotient R(C)/C, n<={nmax}',
        'complete': complete,
        'ns_swept': ns_swept,
        'incomplete_reasons': (
            [] if complete else
            [f'node budget hit at n={n} for classes {sorted(v)}'
             for n, v in sorted(partial.items())]),
        'dedup_signature': '(n, k, S_k-canonical gate); largest distance seen '
                           'among the first 60 witnesses of a signature kept. '
                           'The key is S_k (output permutations only); the '
                           'coarser GL(k,2) class is stored per record as '
                           'gate_gl_canonical. See dedup.py.',
        'kmax': args.kmax,
        'partial_ns': {str(n): sorted(v) for n, v in partial.items()},
        'deferred_ns': {str(n): sorted(v) for n, v in deferred.items()},
        'distinct_factories': len(factories),
        'stats': {str(n): s for n, s in stats.items()},
        'factories': factories,
    }, indent=2) + '\n')
    print(f'\n{len(factories)} distinct (n,k,gate) factories -> {out.name}')
    if not complete:
        print('NOTE: complete=false -- a node budget was hit, so this pass is '
              'NOT exhaustive:', flush=True)
        for n, v in sorted(partial.items()):
            print(f'        - n={n}: classes {sorted(v)}')
    for (n, k) in sorted(byk):
        print(f'  n={n} k={k}: {byk[(n, k)]} gates')
    return 0 if complete else 1


if __name__ == '__main__':
    # main() returns 1 for a pass that hit a node budget.  Calling it bare threw
    # that away, so a truncated pass exited 0 and a `&&`-chained rebuild carried
    # on with `complete: false` input.
    raise SystemExit(main())
