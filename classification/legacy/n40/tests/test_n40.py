#!/usr/bin/env python3
"""Checks for the n = 39, 40 classification directory.

  * the input table validates and has the advertised shape;
  * marking enumerates exactly the 2^m + 1 cases of the theory note;
  * the classifier reproduces a known geometry (rank 7, kappa 7) and every
    witness it writes passes the independent fault verifier;
  * if the catalogue has been built, it is self-consistent and every row's
    stored gate is the brute-force S_k canonical gate of its own columns.

Run:  python -m unittest discover -s classification/legacy/n40/tests -v
"""
import itertools
import json
import sys
import unittest
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))

import reps40                                              # noqa: E402
from marking40 import geometry_count, marked_geometries    # noqa: E402


class InputTable(unittest.TestCase):
    def test_validates(self):
        self.assertEqual(reps40.validate(), [])

    def test_shape(self):
        reps = reps40.load()
        self.assertEqual(len(reps), 110)
        self.assertEqual(dict(Counter(r.m for r in reps)), {6: 1, 7: 18, 8: 46, 9: 32, 10: 12, 11: 1})
        self.assertEqual(reps40.sha256_of(), reps40.EXPECTED_SHA256)


class Marking(unittest.TestCase):
    def test_counts_and_cases(self):
        for rep in [r for r in reps40.load() if r.m in (6, 8, 11)][:3]:
            geoms = list(marked_geometries(rep.m, rep.support))
            self.assertEqual(len(geoms), geometry_count(rep.m))
            self.assertEqual(sum(1 for n, *_ in geoms if n == 39), 40)
            self.assertEqual(sum(1 for n, *_ in geoms if n == 40), (1 << rep.m) - 40 + 1)
            for n, origin, r, pts in geoms:
                self.assertEqual(len(pts), n)
                self.assertEqual(len(set(pts)), n)
                self.assertNotIn(0, pts)
                self.assertLess(max(pts), 1 << r)
                if origin == "lift":
                    self.assertEqual(r, rep.m + 1)
                    self.assertTrue(all((p >> rep.m) & 1 for p in pts))
                else:
                    self.assertEqual(r, rep.m)


class Classifier(unittest.TestCase):
    def test_known_geometry(self):
        from landscape import Parent, classify_landscape, inverse_rows
        from factorylib.parent import _matmul_rows
        from factorylib.verification import verify
        rep = next(r for r in reps40.load() if r.id == "length40_m7_002")
        n, origin, r, pts = next(g for g in marked_geometries(rep.m, rep.support) if g[0] == 40 and g[1] == 0)
        parent = Parent.from_points(pts, ambient_rank=r, distance=3)
        self.assertEqual((parent.check_rank, parent.kappa), (7, 7))
        out = classify_landscape(parent)
        self.assertTrue(out["complete"])
        self.assertEqual(dict(Counter(g["k"] for g in out["gates"])), {1: 1, 2: 3, 3: 5, 4: 7})
        # a 5-dimensional compatible subspace exists, but every gate on it leaves an
        # output idle, so it is not a k = 5 class: recorded as mu = 5, classes to k = 4
        self.assertEqual(out["mu"], 5)
        for g in out["gates"]:
            cols = [frozenset(c) for c in g["columns"]]
            mons = frozenset(frozenset(q) for q in g["wants"])
            ok, dist = verify(g["k"], g["k"] + r, cols, mons, dmax=4)
            self.assertTrue(ok)
            self.assertEqual(dist, 3)
            # the minimum-a3 witness: a direct 3-set count agrees, and no larger than the worst seen
            direct = 0
            rows = [0] * (g["k"] + r)
            for j, c in enumerate(g["columns"]):
                for i in c:
                    rows[i] |= 1 << j
            for X in itertools.combinations(range(n), 3):
                m = sum(1 << j for j in X)
                if all((rows[i] & m).bit_count() % 2 == 0 for i in range(g["k"], g["k"] + r)) and \
                        any((rows[i] & m).bit_count() % 2 for i in range(g["k"])):
                    direct += 1
            self.assertEqual(direct, g["a3"])
            self.assertLessEqual(g["a3"], g["a3_max"])
            self.assertLessEqual(g["a3_max"], out["t3"])
        M = (0b011, 0b101, 0b100)
        self.assertEqual(_matmul_rows(M, inverse_rows(M, 3)), (1, 2, 4))


def _sk_min(mons, k):
    best = None
    for p in itertools.permutations(range(k)):
        key = tuple(sorted(tuple(sorted(p[i] for i in m)) for m in mons))
        if best is None or key < best:
            best = key
    return best


class Catalogue(unittest.TestCase):
    PATH = HERE / "catalog" / "classification_n3940.json"

    def setUp(self):
        if not self.PATH.exists():
            self.skipTest("catalogue not built")
        self.payload = json.loads(self.PATH.read_text(encoding="utf-8"))

    def test_self_consistent(self):
        p = self.payload
        self.assertTrue(p["complete"])
        self.assertEqual(p["n_classes"], len(p["factories"]))
        self.assertEqual(p["n_representatives"], 110)
        self.assertEqual(p["n_geometries"], 44974)
        self.assertEqual(p["input"]["sha256"], reps40.sha256_of())
        self.assertEqual([r["index"] for r in p["factories"]], list(range(1, p["n_classes"] + 1)))

    def test_gates_are_canonical_from_columns(self):
        for r in self.payload["factories"]:
            n, k, N = r["n"], r["k"], r["N"]
            rows = [0] * N
            for j, c in enumerate(r["columns"]):
                for i in c:
                    rows[i] |= 1 << j
            mons = []
            for d in (1, 2, 3):
                for T in itertools.combinations(range(k), d):
                    acc = (1 << n) - 1
                    for i in T:
                        acc &= rows[i]
                    if acc.bit_count() & 1:
                        mons.append(T)
            # the columns are in the canonical frame, and the stored string is that gate
            self.assertEqual(tuple(sorted(mons)), _sk_min(mons, k), r["gate"])
            stored = {tuple(int(ch) for ch in tok) for tok in r["gate"].split("+")}
            self.assertEqual(set(mons), stored, r["gate"])


if __name__ == "__main__":
    unittest.main()
