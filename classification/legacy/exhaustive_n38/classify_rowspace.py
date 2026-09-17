#!/usr/bin/env python3
"""Classify all distance-3 factories with T-count n<=38, over the triorthogonal
(KTA / Nezami-Haah) classification of check parts.

For each classified check-part support S (weights 16/24/28/30/32/34/36/38 ->
n in {15,16,23,24,27,28,29,30,31,...,38}), the valid output rows are exactly
a_q in R' = nullspace(deg-1,2 check rows) [mixed output-check terms vanish],
with each pairwise a_q & a_q' in Q' = nullspace(deg-1 rows).  Any such tuple of
up to K linearly-independent nonzero rows is a genuine distance >= 3 factory; its
logical action is read off from the output-only monomial parities.

INDEPENDENT CROSS-CHECK.  This is the earlier enumerator, working in the full
row space instead of the quotient V = R(C)/C used by `classify.py`.  It is kept
because it reaches the same answer by a different route, so agreement between
the two is real evidence rather than a re-run of one code path.
`tests/test_classification.py` runs both on the small n and asserts they agree.
It is slower than the quotient engine by roughly the factor 2^r the quotient
saves, so the full-ladder cross-check is worth splitting into chunks -- hence
the manifest/task/merge subcommands below.  No shipped artifact comes from this
file; the catalogue is built by `classify.py` plus `hard_parent_n31.py`.

Factories are deduplicated here by the signature
    (n, k, canonical-gate-under-GL(k,2))
so a gate reachable many ways at fixed (n,k) is recorded once (the first
representative, with its verified [[N,k,d]] and explicit columns).  NOTE the
difference from `classify.py`, whose shipped catalogue keys on the finer S_k
form (see dedup.py): this file's GL key is coarser, so its row counts are a
lower bound on the shipped counts.  The cross-check compares the two after
mapping both to the same key.  Distance is
computed only for a new signature.  A per-support node budget bounds runtime;
budget-exceeded supports are flagged partial.

Subcommands:
  manifest  -- print the list of (n, class_index, chunk) shard tasks
  task      -- run one shard, write results/shards/shard_n<n>_c<i>of<N>_k<k>.json
  merge     -- merge all shards, global dedup, write
              results/factory_catalog_n38.json

Chunked runs: one `task` per manifest line, then `merge` once.  Sizing, cost and
scheduler notes are in `docs/SHARDING.md`; no scheduler-specific driver ships
here, because a correct one depends on the cluster.
"""

import argparse
import itertools
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2]))

from nezami_haah_reps import BY_WEIGHT, VALID_NS
from marking import (support_of, row_space_rows, nullspace_basis, marked_even,
                     marked_odd)
from dedup import canonical_gate, gate_name
from factorylib.verification import verify

# Shards land in results/shards/ (gitignored -- regenerate on a cluster); the
# merged catalogue is written to results/, beside the shipped catalogues.
RESULTS = HERE / 'results'
SHARDS = RESULTS / 'shards'


# ----------------------------------------------------------- enumeration
def _span(basis):
    """All 2^len(basis) XOR combinations of `basis`, in subset order."""
    words = [0]
    for v in basis:
        words += [w ^ v for w in words]
    return words


def classify_support(check_set, r, kmax, budget, seen):
    """Enumerate factories on one support, updating `seen` (sig -> record).
    Returns (nodes_used, hit_budget)."""
    checks = tuple(check_set)
    n = len(checks)
    rows2 = row_space_rows(checks, r, 2)
    rows1 = row_space_rows(checks, r, 1)
    # R' : mixed deg-1,2 vanish (drop the |T|=0 all-ones row -> free total parity)
    Rp = sorted(_span(nullspace_basis(rows2[1:], n)))
    q_rows = rows1[1:]                    # deg-1 (exclude all-ones) define Q'

    def in_qp(x):
        for rho in q_rows:
            if (x & rho).bit_count() & 1:
                return False
        return True

    outs = []
    ospan = [0]                           # current span of outs (for independence)
    nodes = [0]
    budget_hit = [False]

    def record():
        k = len(outs)
        wants = set()
        for i in range(k):
            if outs[i].bit_count() & 1:
                wants.add(frozenset((i,)))
        for i in range(k):
            for j in range(i + 1, k):
                if (outs[i] & outs[j]).bit_count() & 1:
                    wants.add(frozenset((i, j)))
        for i in range(k):
            for j in range(i + 1, k):
                for l in range(j + 1, k):
                    if (outs[i] & outs[j] & outs[l]).bit_count() & 1:
                        wants.add(frozenset((i, j, l)))
        # non-degeneracy: must implement a non-trivial gate (not identity /
        # check-only) and every logical qubit must participate in some wanted
        # monomial (else it is an unused qubit padding a smaller factory).
        if not wants:
            return
        covered = set()
        for Q in wants:
            covered |= set(Q)
        if len(covered) != k:
            return
        cg = canonical_gate(k, wants)
        sig = (n, k, cg)
        if sig in seen:
            return
        # first time this (n,k,gate) is seen anywhere in this task: verify + store
        columns = []
        for idx, s in enumerate(checks):
            col = {qq for qq in range(k) if (outs[qq] >> idx) & 1}
            for bit in range(r):
                if (s >> bit) & 1:
                    col.add(k + bit)
            columns.append(frozenset(col))
        ok, dist = verify(k, k + r, columns, wants, dmax=4)
        if not ok:
            raise AssertionError('enumerated factory failed parity verify')
        seen[sig] = {
            'n': n, 'k': k, 'r': r, 'N': k + r,
            # '>4' is floored to 4 here (classify.py keeps the string and
            # ranks it as 5) -- so this field is a lower bound at 4.
            'distance': dist if isinstance(dist, int) else 4,
            'gate': gate_name(k, wants),
            'gate_canonical': cg,
            'columns': [sorted(c) for c in columns],
        }

    def rec():
        if len(outs) >= 1:
            record()
        if len(outs) == kmax:
            return
        start = (outs[-1] + 1) if outs else 1
        for a in Rp:
            if a < start or a == 0:
                continue
            # Independence: `a` must not lie in the span of the outputs chosen
            # so far.  `ospan` is maintained as the FULL span (all 2^|outs|
            # combinations, at most 32 elements since kmax <= 5), so membership
            # is an exact test rather than a reduction heuristic.
            #
            # An earlier version reduced `a` by a single greedy pass over this
            # unreduced list, which is one-sided: it proves membership when the
            # residue is 0, but a dependent `a` can end nonzero (outs = [2,3,6],
            # a = 7 ends at 2).  That let frames with linearly dependent outputs
            # into the enumeration -- they are not genuine k-output factories,
            # and they showed up as spurious extra gate classes when this file
            # was compared against the quotient engine.  tests/
            # test_classification.py::test_agrees_with_the_quotient_engine is
            # the regression that pins the fix.
            if a in ospan:
                continue
            ok = True
            for b in outs:
                if not in_qp(a & b):
                    ok = False
                    break
            if not ok:
                continue
            nodes[0] += 1
            if nodes[0] > budget:
                budget_hit[0] = True
                return
            new_span = ospan + [w ^ a for w in ospan]
            outs.append(a)
            ospan_saved = ospan[:]
            ospan[:] = new_span
            rec()
            ospan[:] = ospan_saved
            outs.pop()
            if budget_hit[0]:
                return

    rec()
    return nodes[0], budget_hit[0]


# ----------------------------------------------------------- support source
# This enumerator covers exactly the weights tabulated in nezami_haah_reps,
# i.e. the whole n <= 38 window of this directory -- the same window as
# classify.py, which is what makes the two comparable.
ROWSPACE_NS = tuple(n for n in VALID_NS if (n + n % 2) in BY_WEIGHT)


def support_chunks(n, nchunks):
    """All marked supports for T-count n, split into nchunks contiguous lists."""
    weight = n + (n % 2)
    if weight not in BY_WEIGHT:
        raise SystemExit(
            f'n={n} needs the weight-{weight} classification, which this '
            f'row-space enumerator does not carry.  Supported: '
            f'{list(ROWSPACE_NS)}.')
    reps = BY_WEIGHT[weight]
    marker = marked_even if (n % 2 == 0) else marked_odd
    allm = []
    for ci, (m, terms) in enumerate(reps):
        for r, cs in marker(m, terms):
            allm.append((ci, r, cs))
    chunks = [[] for _ in range(nchunks)]
    for i, item in enumerate(allm):
        chunks[i % nchunks].append(item)
    return chunks


# ----------------------------------------------------------- subcommands
def manifest_tasks(ns, nchunks):
    """The (n, chunk, nchunks) tasks a sweep of `ns` consists of.

    Chunks that came out EMPTY are not tasks: at small n there are fewer marked
    supports than chunks (n=16 has one, so 7 of 8 chunks are empty).  `manifest`
    and `merge` both call this, which is the point -- they used to disagree, the
    manifest printing 121 tasks while merge demanded all 128 and reported the
    seven that can never exist as missing.  Following the documented workflow
    exactly then produced `complete: false`.
    """
    tasks = []
    for n in ns:
        chunks = support_chunks(n, nchunks)
        for c, chunk in enumerate(chunks):
            if chunk:
                tasks.append((n, c, nchunks))
    return tasks


def cmd_manifest(args):
    tasks = manifest_tasks(args.ns, args.nchunks)
    print('\n'.join(f'{n} {c} {nc}' for n, c, nc in tasks))
    print(f'# {len(tasks)} shard tasks', flush=True)


def cmd_task(args):
    chunks = support_chunks(args.n, args.nchunks)
    supports = chunks[args.chunk]
    seen = {}
    start = time.monotonic()
    total_nodes = 0
    partial = []
    for ci, r, cs in supports:
        nd, hit = classify_support(cs, r, args.kmax, args.budget, seen)
        total_nodes += nd
        if hit:
            partial.append(ci)
    out = {
        'n': args.n, 'chunk': args.chunk, 'nchunks': args.nchunks,
        'kmax': args.kmax, 'budget': args.budget,
        'supports': len(supports), 'nodes': total_nodes,
        'partial_class_indices': sorted(set(partial)),
        'distinct_factories': len(seen),
        'factories': list(seen.values()),
        'elapsed_seconds': round(time.monotonic() - start, 2),
    }
    SHARDS.mkdir(parents=True, exist_ok=True)
    path = SHARDS / f'shard_n{args.n}_c{args.chunk}of{args.nchunks}_k{args.kmax}.json'
    path.write_text(json.dumps(out, indent=2) + '\n')
    print(f'n={args.n} chunk {args.chunk}/{args.nchunks}: '
          f'{len(supports)} supports, {len(seen)} distinct factories, '
          f'{total_nodes} nodes, {out["elapsed_seconds"]}s '
          f'{"[PARTIAL]" if partial else ""} -> {path.name}', flush=True)


def _shard_problems(name, shard):
    """Why this shard file is not usable ([] if it is).

    A shard is written by `cmd_task` on a cluster, which means the realistic
    failure is a truncated or half-written file rather than a malicious one --
    and the merge used to index straight into it, so a corrupt shard ended a
    multi-hour job with a `KeyError` from inside the loop instead of a line
    saying which file to re-run.  `False` is rejected for the integer fields on
    purpose: it equals 0, so a shard with `chunk: false` silently occupied
    chunk 0's place in the coverage audit.
    """
    if not isinstance(shard, dict):
        return [f'{name}: holds a {type(shard).__name__}, not an object']
    problems = []
    for field in ('n', 'chunk', 'nchunks', 'kmax'):
        value = shard.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            problems.append(f'{name}: {field}={value!r} is not a non-negative '
                            f'integer')
    rows = shard.get('factories')
    if not isinstance(rows, list):
        problems.append(f'{name}: factories is not a list')
    else:
        # The merge keys on these four fields, so a row missing one takes the
        # whole job down rather than just being unmergeable.
        for index, rec in enumerate(rows):
            if not isinstance(rec, dict) or not {
                    'n', 'k', 'gate_canonical', 'distance'} <= rec.keys():
                problems.append(f'{name}: factory {index} is not a record with '
                                f'n, k, gate_canonical and distance: {rec!r}')
                break
    if not isinstance(shard.get('partial_class_indices'), list):
        problems.append(f'{name}: partial_class_indices is not a list')
    return problems


def cmd_merge(args):
    """Merge every shard, with a coverage audit of the shard set itself.

    A merge used to accept whatever shards happened to be on disk: a missing
    chunk, a duplicated one, or a set produced at mixed --kmax/--nchunks all
    merged silently into a result whose `question` field claims the whole
    n<=38 sweep.  The audit below reports exactly which (n, chunk) tasks are
    absent and refuses to describe the output as complete unless every task in
    `manifest_tasks` is present exactly once at one consistent kmax.

    An EMPTY shard directory is the sharpest case and used to be the one that
    got through: no shards means no --nchunks to compare against, so no task was
    ever reported missing, and the merge wrote `complete: true` over zero
    factories and exited 0.  It now refuses to write at all.
    """
    shards = sorted(SHARDS.glob('shard_*.json'))
    if not shards:
        # Not merely incomplete: a zero-factory merge would OVERWRITE a real
        # merged catalogue with an empty one.  Refuse before writing anything.
        print(f'no shards in {SHARDS}: nothing to merge (run the `manifest` '
              f'tasks first; see docs/SHARDING.md)')
        return 1
    seen = {}
    partial = {}
    coverage = {}                        # (n, chunk, nchunks) -> [kmax, ...]
    kmaxes, nchunkses = set(), set()
    unusable = []
    for sp in shards:
        d = json.loads(sp.read_text())
        bad = _shard_problems(sp.name, d)
        if bad:
            unusable += bad
            continue
        coverage.setdefault((d['n'], d['chunk'], d['nchunks']), []).append(d['kmax'])
        kmaxes.add(d['kmax'])
        nchunkses.add(d['nchunks'])
        for rec in d['factories']:
            sig = (rec['n'], rec['k'], rec['gate_canonical'])
            cur = seen.get(sig)
            if cur is None or rec['distance'] > cur['distance']:
                seen[sig] = rec          # keep highest-distance representative
        if d['partial_class_indices']:
            partial.setdefault(d['n'], set()).update(d['partial_class_indices'])
    factories = sorted(seen.values(), key=lambda r: (r['n'], r['k'], r['gate']))

    # ---- audit the shard SET, not just its contents ----------------------
    problems = list(unusable)
    if len(kmaxes) > 1:
        problems.append(f'shards were produced at mixed --kmax {sorted(kmaxes)}; '
                        f'the merged set is only as wide as the smallest')
    if len(nchunkses) > 1:
        problems.append(f'shards were produced at mixed --nchunks '
                        f'{sorted(nchunkses)}, so chunk indices are not comparable')
    duplicated = sorted(task for task, ks in coverage.items() if len(ks) > 1)
    if duplicated:
        problems.append(f'{len(duplicated)} shard task(s) appear more than once: '
                        f'{duplicated[:5]}')
    missing = []
    if len(nchunkses) == 1:
        nchunks = next(iter(nchunkses))
        expected = set(manifest_tasks(sorted(ROWSPACE_NS), nchunks))
        for n, chunk, _nc in sorted(expected):
            if (n, chunk, nchunks) not in coverage:
                missing.append(f'n={n} chunk={chunk}')
        if missing:
            problems.append(f'{len(missing)} of {len(expected)} shard task(s) '
                            f'missing, e.g. {missing[:5]}')
        unexpected = sorted(set(coverage) - expected)
        if unexpected:
            problems.append(f'{len(unexpected)} shard(s) are not manifest '
                            f'tasks: {unexpected[:5]}')
    else:
        problems.append('shards do not agree on --nchunks, so coverage against '
                        'the manifest cannot be audited')
    if partial:
        problems.append(f'node budget hit at n={sorted(partial)}')
    complete = not problems

    result = {
        'question': 'all distance-3 factories with T-count n<=38 over the '
                    'triorthogonal check-part classification',
        'dedup_signature': '(n, k, canonical gate under GL(k,2))',
        'shards_merged': len(shards),
        'complete': complete,
        'incomplete_reasons': problems,
        'kmax': sorted(kmaxes),
        'distinct_factories': len(factories),
        'partial_ns': {str(n): sorted(v) for n, v in partial.items()},
        'factories': factories,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = RESULTS / 'factory_catalog_n38.json'
    out.write_text(json.dumps(result, indent=2) + '\n')
    # compact summary by (n,k)
    from collections import Counter
    byk = Counter((r['n'], r['k']) for r in factories)
    print(f'{len(factories)} distinct factories from {len(shards)} shards '
          f'(complete={complete})')
    for (n, k) in sorted(byk):
        print(f'  n={n} k={k}: {byk[(n, k)]} gates')
    print(f'saved {out}')
    if problems:
        print('NOTE: this merge is NOT a complete n<=38 sweep:')
        for problem in problems:
            print(f'        - {problem}')
    return 0 if complete else 1


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)

    m = sub.add_parser('manifest')
    m.add_argument('--ns', nargs='+', type=int, default=list(ROWSPACE_NS))
    m.add_argument('--nchunks', type=int, default=8)
    m.set_defaults(func=cmd_manifest)

    t = sub.add_parser('task')
    t.add_argument('--n', type=int, required=True)
    t.add_argument('--chunk', type=int, required=True)
    t.add_argument('--nchunks', type=int, required=True)
    t.add_argument('--kmax', type=int, default=2)
    t.add_argument('--budget', type=int, default=20_000_000)
    t.set_defaults(func=cmd_task)

    g = sub.add_parser('merge')
    g.set_defaults(func=cmd_merge)

    args = ap.parse_args()
    return args.func(args) or 0


if __name__ == '__main__':
    # cmd_merge returns 1 for an incomplete merge; calling main() bare discarded
    # that, so an audit that had found missing shards still exited 0.
    raise SystemExit(main())
