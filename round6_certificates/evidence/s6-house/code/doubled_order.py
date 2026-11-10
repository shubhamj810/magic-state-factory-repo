#!/usr/bin/env python3
"""A column order of small cut rank for a doubled transversal-T row, built from its block structure.

The doubled rows (Jain and Albert, arXiv:2408.12752) store their columns as consecutive blocks: two copies
of a self-dual block (the same columns up to the doubling rows), then the inner code, itself doubled.  The
natural order walks through each self-dual block in its stored order, which for a quadratic-residue block
is a poor trellis order (cut rank 40 for [80,40,16]).  Here each block's own order is improved by local
search on its cut-rank profile (lexicographic: maximum, then sum), and the two copies of a pair are
interleaved in that order.

    python doubled_order.py ROWID SECONDS [SEED]    writes data/orders/ROWID.json and prints both cut ranks

The order only matters to the DP's memory and time: the distance is the same for every order.
"""
import json
import random
import sys
import time
from pathlib import Path

from cutrank import colvecs, prefix_ranks, profile

HERE = Path(__file__).resolve().parent


def blocks(row):
    """Consecutive pairs of equal-length blocks [(start, m, True)] plus singles, from the stored witness, whose
    columns are the first column of every block (0, 79, 158, ... for 599.1.6.a); each pair is checked to be
    two copies (the columns of the second block differ from the first's by the same wire set throughout)."""
    cols = row["columns"]
    starts = list(row["d_witness"]) + [len(cols)]
    lens = [starts[i + 1] - starts[i] for i in range(len(starts) - 1)]
    out, i = [], 0
    while i < len(lens):
        if i + 1 < len(lens) and lens[i] == lens[i + 1] and lens[i] > 1:
            a, m = starts[i], lens[i]
            diffs = {tuple(sorted(set(cols[a + t]) ^ set(cols[a + m + t]))) for t in range(m)}
            assert len(diffs) == 1, (a, m, list(diffs)[:3])
            out.append((a, m, True))
            i += 2
        else:
            out += [(starts[i] + t, 1, False) for t in range(lens[i])]
            i += 1
    return out


def score(vecs, order):
    prof = profile([vecs[i] for i in order])
    return (max(prof), sum(prof))


def improve(vecs, order, seconds, rng):
    best = list(order)
    bs = score(vecs, best)
    cur, cs = list(best), bs
    t0 = time.time()
    temp = 2.0
    it = 0
    while time.time() - t0 < seconds:
        it += 1
        cand = list(cur)
        i, j = rng.randrange(len(cand)), rng.randrange(len(cand))
        if rng.random() < 0.5:
            cand[i], cand[j] = cand[j], cand[i]
        else:
            x = cand.pop(i)
            cand.insert(j, x)
        s = score(vecs, cand)
        delta = (s[0] - cs[0]) * 50 + (s[1] - cs[1])
        if delta <= 0 or rng.random() < pow(2.718, -delta / temp):
            cur, cs = cand, s
            if s < bs:
                best, bs = list(cand), s
        temp = max(0.05, 2.0 * (1 - (time.time() - t0) / seconds))
    return best, bs, it


def main():
    rid, seconds = sys.argv[1], float(sys.argv[2])
    rng = random.Random(int(sys.argv[3]) if len(sys.argv) > 3 else 1)
    row = json.loads((HERE / "data" / "rows" / f"{rid}.json").read_text())
    cols = row["columns"]
    vecs = colvecs(row)
    bl = blocks(row)
    pairs = [b for b in bl if b[2] and b[1] > 2]
    budget = seconds / max(1, len(pairs))
    order = []
    cache = {}
    prev = HERE / "data" / "orders" / f"{rid}.json"
    warm = {}
    if prev.exists():                  # warm start: each pair's local order from the previous best
        po = json.loads(prev.read_text())
        pos = {c: i for i, c in enumerate(po)}
        for start, m, is_pair in bl:
            if is_pair and m > 2:
                warm[start] = sorted(range(m), key=lambda t: pos[start + t])
    for start, m, is_pair in bl:
        if not is_pair:
            order.append(start)
            continue
        if m <= 2:
            for t in range(m):
                order += [start + t, start + m + t]
            continue
        key = tuple(tuple(c) for c in cols[start:start + m])
        local = warm.get(start, list(range(m)))
        bvec = [vecs[start + t] for t in range(m)]
        if key in cache:
            local = cache[key]
        else:
            local, s, it = improve(bvec, local, budget, rng)
            cache[key] = local
            print(f"block of {m} at {start}: own cut rank {score(bvec, list(range(m)))} -> {s} ({it} moves)", flush=True)
        for t in local:
            order += [start + t, start + m + t]
    assert sorted(order) == list(range(len(cols)))
    nat = score(vecs, list(range(len(cols))))
    new = score(vecs, order)
    (HERE / "data" / "orders").mkdir(parents=True, exist_ok=True)
    if not prev.exists() or new < score(vecs, json.loads(prev.read_text())):
        prev.write_text(json.dumps(order))
    print(json.dumps({"id": rid, "blocks": [(s, m) for s, m, p in bl if p], "natural": nat, "new": new}))


if __name__ == "__main__":
    main()
