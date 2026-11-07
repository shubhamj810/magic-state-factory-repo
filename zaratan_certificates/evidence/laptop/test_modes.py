#!/usr/bin/env python3
"""Brute-force checks of the two tropidist search modes the plan relies on.

1. One threshold.  search(K) started cold at K (no lower thresholds run first) returns "found" with a
   solution of weight <= K exactly when the true distance is <= K, and "exhausted" otherwise.  The
   repository's own tests (tests/test_search.py) check iterative deepening from K = 1, not a cold
   start above or below the distance.
2. Anchored, equal rank, under the precondition K <= d.  With anchors = [v] and every rank equal,
   search(K) returns "found" exactly when some solution of weight <= K contains column v, and every
   solution it returns contains v.  The precondition matters: the kernel only adds columns that fix
   an unsatisfied row, so it never extends a zero-syndrome, zero-logical prefix through v by a
   disjoint logical elsewhere (seed 11, trial 53: h = [1,5,4,3,2,0], l = [0,1,1,0,0,1], v = 3 has
   the solution {0,3,4,5} = stabiliser {0,3,4} + logical {5}, and the anchored run misses it).  When
   no solution is lighter than K, every solution of weight <= K is minimal and is reached.  The ladder
   and lift tests of the plan always run with K equal to the certified distance, so they are in this
   regime.  Pair exclusions are sound there too.

Both are run labelled and label-free, with and without the covering bound and the pair exclusions,
with completion tables of depth 1 to 3, on random problems small enough for brute force.

usage: <tropidist venv python> test_modes.py [trials] [seed]
"""
from __future__ import annotations

import itertools
import random
import sys
from pathlib import Path

sys.path.insert(0, "/Users/shubhamjain/Documents/IBM internship/Shraddha (Magic states)/tropidist-src")
from cdist import search                     # noqa: E402
from cdist.problem import Problem, dedupe    # noqa: E402


def brute(h, l, must=None):
    n = len(h)
    for w in range(1, n + 1):
        for sup in itertools.combinations(range(n), w):
            if must is not None and must not in sup:
                continue
            s = lg = 0
            for j in sup:
                s ^= h[j]
                lg ^= l[j]
            if s == 0 and lg != 0:
                return w
    return None


def run(p, K, kt, labelfree, cover, ex, anchors=None, rank=None):
    S = search.Searcher(p, rank=rank, anchors=anchors, labelfree=labelfree)
    if ex:
        S.build_exclusions()
    tab = search.Table(p, kt, labelfree=S.labelfree)
    S.add_table(tab, exact=True)
    try:
        return S.search(K, task_depth=1, exclusions=ex, cover=cover)
    finally:
        tab.free()


def main(trials=600, seed=11):
    rng = random.Random(seed)
    checked = {"threshold": 0, "anchored": 0, "anchored_found": 0, "found": 0, "exhausted": 0}
    for t in range(trials):
        m = rng.randint(3, 9)
        n = rng.randint(4, 15)
        k = rng.randint(1, 3)
        h = [sum(1 << i for i in range(m) if rng.random() < rng.choice([0.25, 0.4])) for _ in range(n)]
        l = [sum(1 << i for i in range(k) if rng.random() < 0.35) for _ in range(n)]
        h, l, _ = dedupe(h, l)
        if len(h) < 3:
            continue
        p = Problem("rand", m, k, h, l, [()] * m)
        d = brute(h, l)
        for K in range(1, min(len(h), 8) + 1):
            for kt in (1, 2, 3):
                lf = rng.random() < 0.5
                cover = rng.random() < 0.5
                ex = rng.random() < 0.5
                r = run(p, K, kt, lf, cover, ex)
                expect = d is not None and d <= K
                assert r["status"] in ("found", "exhausted"), r["status"]
                assert (r["status"] == "found") == expect, (t, K, kt, lf, cover, ex, d, r["status"])
                if expect:
                    assert r["best"] is not None and r["best"] <= K
                    for s in r["solutions"]:
                        assert search.verify(p, s) and len(s) <= K
                checked["threshold"] += 1
                checked["found" if expect else "exhausted"] += 1
            if d is not None and K > d:
                continue                  # the anchored mode is specified only for K <= d
            v = rng.randrange(len(h))
            dv = brute(h, l, must=v)
            for kt in (1, 2, 3):
                ex = rng.random() < 0.5
                r = run(p, K, kt, rng.random() < 0.5, rng.random() < 0.5, ex,
                        anchors=[v], rank=[0] * len(h))
                expect = dv is not None and dv <= K
                assert (r["status"] == "found") == expect, ("anchored", t, K, kt, v, dv, r["status"])
                for s in r["solutions"]:
                    assert v in s and search.verify(p, s) and len(s) <= K
                checked["anchored"] += 1
                checked["anchored_found"] += expect
    print(f"ok: {checked}")


if __name__ == "__main__":
    main(*(int(x) for x in sys.argv[1:3]))
