#!/usr/bin/env python3
"""Checks for the n = 41 .. 48 classification directory.

  * the four input tables validate and have the advertised shape; the RM(3,7)
    cross-check of the m = 7 sectors reports exactly the two known missing
    length-48 classes and nothing else;
  * the sources list every representative at 2^m + 1 origins (tables) or one
    origin per stabiliser orbit plus the lift (RM(3,7)), and the workers'
    marking equals n40's ``marked_geometries`` origin for origin;
  * the sweep worker classifies a known geometry and every witness it writes
    passes the independent fault verifier; a shard round-trips and is
    recognised as done;
  * the builder's ``aggregate`` separates integrity problems from coverage
    gaps (a failed geometry or a missing shard is a gap, a histogram that does
    not add up is a problem), on a copy of the real length-42 shard;
  * the catalogue, if built, is self-consistent (a source with declared gaps
    accounts for every unclassified geometry) and every row's stored gate is
    the brute-force S_k canonical gate of its own columns.

Run:  python -m unittest discover -s classification/n48/tests -v
"""
import gzip
import itertools
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
for p in (HERE, HERE.parent / "n40", REPO):
    sys.path.insert(0, str(p))

import reps48                                              # noqa: E402
import sources48                                           # noqa: E402
from marking40 import marked_geometries                    # noqa: E402


class InputTables(unittest.TestCase):
    def test_validate_and_shape(self):
        for L in reps48.LENGTHS:
            table = reps48.read_table(L)
            self.assertEqual(reps48.validate(L, table), [], L)
            reps = reps48.load(L, table)
            self.assertEqual(len(reps), reps48.EXPECTED_COUNT[L])
            self.assertEqual(dict(Counter(r.m for r in reps)), reps48.EXPECTED_BY_M[L])
            self.assertEqual(reps48.sha256_of(L), reps48.EXPECTED_SHA256[L])

    def test_rm37_crosscheck_reports_the_two_missing_classes(self):
        cc = reps48.rm37_crosscheck(44)
        self.assertEqual((cc["catalogue_m7_representatives"], cc["rm37_rank7_classes"]), (35, 35))
        self.assertEqual(cc["rm37_classes_missing_from_catalogue"], [])
        self.assertEqual(cc["catalogue_representatives_not_in_rm37"], [])
        cc = reps48.rm37_crosscheck(48)
        self.assertEqual((cc["catalogue_m7_representatives"], cc["rm37_rank7_classes"]), (96, 98))
        self.assertEqual([c["class_index"] for c in cc["rm37_classes_missing_from_catalogue"]], [2164, 2867])
        self.assertEqual(cc["catalogue_representatives_not_in_rm37"], [])

    def test_missing_classes_are_genuine(self):
        """The two RM(3,7) classes absent from the length-48 table are weight-48,
        affine-rank-7, unital triorthogonal supports -- exactly what the table
        claims to list completely."""
        for index, anf, stab, S in reps48.rm37_rank7_classes(48):
            if index in (2164, 2867):
                self.assertEqual(len(S), 48)
                self.assertEqual(reps48.affine_rank(S), 7)
                self.assertTrue(reps48.is_unital_triorthogonal(7, S))


class Sources(unittest.TestCase):
    def test_counts(self):
        expect = {"length42": (86, 41558), "length44": (508, 239100), "length46": (1015, 326647),
                  "length48": (28776, 15566440), "rm37_w44": (35, 474), "rm37_w48": (98, 1870), "open_rank6": (1, 3)}
        for s, (n_reps, n_geo) in expect.items():
            reps = sources48.reps_of(s)
            self.assertEqual(len(reps), n_reps, s)
            self.assertEqual(sum(r.n_geometries for r in reps), n_geo, s)
            for r in reps:
                self.assertEqual(r.origins[-1], "lift")
                self.assertEqual(len(set(map(str, r.origins))), len(r.origins))
        self.assertTrue(all(r.m >= 8 for r in sources48.reps_of("length48")))
        self.assertTrue(all(r.m >= 8 for r in sources48.reps_of("length44")))
        self.assertTrue(all(r.m == 7 for r in sources48.reps_of("rm37_w48")))

    def test_marking_matches_n40(self):
        for L in (42, 44, 46):
            for rep in reps48.load(L)[:3]:
                got = {o: sources48.marking_of(rep.m, rep.support, o) for o in sources48.all_origins(rep.m)}
                exp = {o: (n, a, pts) for n, o, a, pts in marked_geometries(rep.m, rep.support)}
                self.assertEqual(got, exp, rep.id)
                self.assertEqual(len(got), (1 << rep.m) + 1)
                self.assertEqual(sum(1 for n, *_ in got.values() if n == L - 1), L)

    def test_rm37_sources_are_triorthogonal_supports_in_their_span(self):
        for s, L in (("rm37_w44", 44), ("rm37_w48", 48), ("open_rank6", 48)):
            for rep in sources48.reps_of(s)[:5]:
                self.assertEqual(len(rep.support), L)
                self.assertEqual(reps48.affine_rank(rep.support), rep.m)
                self.assertTrue(reps48.is_unital_triorthogonal(rep.m, rep.support), rep.id)
                for o in rep.origins:
                    n, a, pts = sources48.marking_of(rep.m, rep.support, o)
                    self.assertEqual(len(set(pts)), n)
                    self.assertNotIn(0, pts)
                    self.assertLess(max(pts), 1 << a)


class Sweep(unittest.TestCase):
    def test_worker_on_a_known_geometry(self):
        from classify48 import _job
        from factorylib.verification import verify
        rep = next(r for r in sources48.reps_of("length42") if r.id == "length42_m8_class_0001")
        part = _job((rep.id, rep.m, tuple(sorted(rep.support)), [0, "lift"], None))
        self.assertEqual(part["failed"], [])
        self.assertEqual(part["n_origins"], 2)
        self.assertEqual(sum(v for _, v in part["hist"]), 2)
        self.assertEqual({tuple(k[:3]) for k, _ in part["hist"]}, {(41, 8, 8), (42, 9, 9)})
        self.assertTrue(part["entries"])
        for e in part["entries"]:
            cols = [frozenset(c) for c in e["columns"]]
            mons = frozenset(frozenset(q) for q in e["wants"])
            ok, dist = verify(e["k"], e["N"], cols, mons, dmax=4)
            self.assertTrue(ok)
            self.assertEqual(dist, 3)
            self.assertEqual(e["distance"], 3)
            self.assertLessEqual(e["a3"], e["a3_max"])
            self.assertEqual(e["n"], len(cols))

    def test_orbit_memo_is_invisible(self):
        """The cross-parent GL-orbit memo changes speed only: a mixed sample of
        length-44 and length-48 parents classifies identically with it off,
        cold and warm."""
        import json
        import random
        import classify48
        rng = random.Random(7)
        jobs = []
        for src in ("length44", "length48"):
            for rep in rng.sample([r for r in sources48.reps_of(src) if r.m == 8], 3):
                origins = rng.sample(rep.origins[:-1], 3) + ["lift"]
                jobs.append((rep.id, rep.m, tuple(sorted(rep.support)), origins, None))

        def run():
            outs = [classify48._job(j) for j in jobs]
            return json.dumps([{k: v for k, v in o.items() if k not in ("seconds", "slowest")}
                               for o in outs], sort_keys=True)
        try:
            classify48.enable_orbit_memo(False)
            plain = run()
            classify48.enable_orbit_memo(True)
            cold = run()
            warm = run()
        finally:
            classify48.enable_orbit_memo(True)
        self.assertEqual(plain, cold)
        self.assertEqual(plain, warm)
        self.assertTrue(classify48._ORBIT_MEMO)
        self.assertNotIn("failed\": [\"", plain)

    def test_shard_round_trip(self):
        import classify48
        rep = next(r for r in sources48.reps_of("length42") if r.id == "length42_m8_class_0002")
        rec = classify48._new_record(rep)
        classify48._merge(rec, classify48._job((rep.id, rep.m, tuple(sorted(rep.support)), rep.origins[:3], None)))
        rec = classify48._finish(rec)
        self.assertFalse(rec["complete"])          # 3 of 257 origins
        self.assertEqual(rec["n_geometries"], 3)
        with tempfile.TemporaryDirectory() as d:
            path = classify48.shard_path(Path(d), 1)
            blob = {"complete": True, "input_sha256": "x", "kmax": None, "engine": classify48.ENGINE,
                    "rep_ids": [rep.id], "reps": [rec]}
            classify48.write_shard(path, blob)
            self.assertEqual(classify48.read_shard(path)["reps"][0]["n_geometries"], 3)
            self.assertTrue(classify48.shard_is_done(path, "x", None, [rep.id]))
            self.assertFalse(classify48.shard_is_done(path, "y", None, [rep.id]))
            self.assertFalse(classify48.shard_is_done(path, "x", 3, [rep.id]))

    def test_shard_plan_covers_every_representative_once(self):
        from classify48 import plan_shards
        reps = sources48.reps_of("length46")
        shards = plan_shards(reps)
        self.assertEqual([r.id for s in shards for r in s], [r.id for r in reps])
        self.assertTrue(all(sum(r.n_geometries for r in s) <= 50000 or len(s) == 1 for s in shards))


class Builder(unittest.TestCase):
    """``aggregate`` tells integrity problems (files not trustworthy) from
    coverage gaps (files sound, some geometries not classified), on a copy of
    the real length-42 result shard."""
    SHARD = HERE / "results" / "length42" / "shard_0001.json.gz"

    def setUp(self):
        if not self.SHARD.exists():
            self.skipTest("length42 not swept")
        import build_catalog48
        self.B = build_catalog48

    def _run(self, edit):
        with tempfile.TemporaryDirectory() as d:
            blob = self.B.read_shard(self.SHARD)
            edit(blob)
            import classify48
            classify48.write_shard(Path(d) / self.SHARD.name, blob)
            return self.B.aggregate("length42", results_dir=d)

    def test_clean_shard_has_no_problems_and_no_gaps(self):
        entries, cov, summary, problems, gaps = self._run(lambda b: None)
        self.assertEqual((problems, gaps), ([], []))
        self.assertTrue(summary["complete"])
        self.assertNotIn("coverage_gaps", summary)
        self.assertEqual(summary["n_geometries"], summary["n_geometries_expected"])

    def test_failed_geometry_is_a_gap_not_a_problem(self):
        def edit(b):
            rec = b["reps"][0]
            row = rec["histogram"][0]
            row[-1] -= 1
            rec["n_geometries"] -= 1
            rec["failed"] = [{"origin": 5, "n": row[0], "ambient_rank": row[1],
                              "error": "OrbitTooLarge: k=6 orbit of a 9-monomial gate exceeds 150000 members"}]
            rec["complete"] = False
            b["n_failed"], b["complete"] = 1, False
        entries, cov, summary, problems, gaps = self._run(edit)
        self.assertEqual(problems, [])
        self.assertTrue(gaps)
        self.assertFalse(summary["complete"])
        cg = summary["coverage_gaps"]
        self.assertEqual(cg["n_geometries_not_classified"], 1)
        self.assertEqual(cg["missing_shards"], [])
        self.assertEqual(cg["failed_geometries"][0]["origin"], 5)
        self.assertEqual(cg["failed_by_error"], {"OrbitTooLarge: k=6 orbit exceeds 150000 members": 1})
        self.assertEqual(summary["n_geometries"] + 1, summary["n_geometries_expected"])
        self.assertTrue(entries)                     # the swept geometries still count

    def test_short_histogram_without_a_failure_is_a_problem(self):
        def edit(b):
            rec = b["reps"][0]
            rec["histogram"][0][-1] -= 1
            rec["n_geometries"] -= 1
        entries, cov, summary, problems, gaps = self._run(edit)
        self.assertTrue(any("swept" in p for p in problems))
        self.assertEqual(gaps, [])

    def test_missing_shard_is_a_gap(self):
        with tempfile.TemporaryDirectory() as d:
            entries, cov, summary, problems, gaps = self.B.aggregate("length42", results_dir=d)
        self.assertEqual(problems, [])
        self.assertEqual(len(gaps), 1)
        self.assertEqual(summary["coverage_gaps"]["missing_shards"][0]["shard"], 1)
        self.assertEqual(summary["coverage_gaps"]["n_geometries_not_classified"], summary["n_geometries_expected"])
        self.assertEqual(entries, {})


def _sk_min(mons, k):
    best = None
    for p in itertools.permutations(range(k)):
        key = tuple(sorted(tuple(sorted(p[i] for i in m)) for m in mons))
        if best is None or key < best:
            best = key
    return best


class Catalogue(unittest.TestCase):
    PATH = HERE / "catalog" / "classification_n41_48.json"

    def setUp(self):
        if not self.PATH.exists():
            self.skipTest("catalogue not built")
        self.payload = json.loads(self.PATH.read_text(encoding="utf-8"))

    def test_self_consistent(self):
        p = self.payload
        self.assertEqual(p["n_classes"], len(p["factories"]))
        self.assertEqual([r["index"] for r in p["factories"]], list(range(1, p["n_classes"] + 1)))
        for L in reps48.LENGTHS:
            self.assertEqual(p["inputs"][f"length{L}"]["sha256"], reps48.sha256_of(L))
        for s, sm in p["sources"].items():
            gaps = sm.get("coverage_gaps")
            self.assertEqual(sm["complete"], not gaps, s)
            n_gap = gaps["n_geometries_not_classified"] if gaps else 0
            self.assertEqual(sm["n_geometries"] + n_gap, sm["n_geometries_expected"], s)
            if gaps:
                self.assertTrue(p["partial"])
                self.assertEqual(n_gap, sum(g["n_geometries"] for g in gaps["missing_shards"])
                                 + len(gaps["failed_geometries"]))
        if not p["partial"]:
            self.assertEqual(set(p["sources"]), set(sources48.SOURCES) - {"open_rank6"})

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
            self.assertEqual(tuple(sorted(mons)), _sk_min(mons, k), r["gate"])
            stored = {tuple(int(ch) for ch in tok) for tok in r["gate"].split("+")}
            self.assertEqual(set(mons), stored, r["gate"])


if __name__ == "__main__":
    unittest.main()
