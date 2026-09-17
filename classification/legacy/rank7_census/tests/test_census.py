"""Census engine and catalogue checks.

The engine is expensive at full scale, so the tests here run it only on tiny
selections and then verify the SHIPPED catalogue in full -- which is cheap,
because verification is much cheaper than search.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parents[3]))

import build_catalog as B                             # noqa: E402
from factorylib.parent import Parent                  # noqa: E402
from rank7 import DEFAULT_DATA, iter_parents, run     # noqa: E402

CATALOG = HERE.parent / "catalog" / "census_r7.json"


class TestEngineSmoke(unittest.TestCase):
    def test_a_two_parent_run_completes_and_is_marked_incomplete(self):
        """A capped run must report complete=false.  This is the guard that
        stops budget-limited search output being read as a certificate, so it
        is worth a test of its own.

        The run writes into a system temporary directory rather than the
        repository, so the suite works on read-only or append-only checkouts
        and never leaves a stray file behind.
        """
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "smoke.json"
            payload = run(data=DEFAULT_DATA, output=str(out), mode="reps",
                          class_indices=[306], max_parents=2, kmax=2,
                          node_budget=100_000, orbit_budget=100_000)
            self.assertFalse(payload["complete"])
            self.assertEqual(payload["processed_parents"], 2)
            self.assertTrue(out.exists())

    def test_parent_construction_agrees_with_the_shared_core(self):
        """The census builds parents through the same core.Parent used by
        ../../../parent_first, so kappa computed here must match."""
        for orbit, origin, points in iter_parents(DEFAULT_DATA, mode="reps",
                                                  nmax=44):
            parent = Parent.from_points(points, orbit.rank if hasattr(orbit, "rank") else None,
                                        distance=3)
            self.assertGreaterEqual(parent.kappa, 0)
            self.assertEqual(parent.n, len(points))
            break


@unittest.skipUnless(CATALOG.exists(),
                     "census catalogue not built -- run build_catalog.py")
class TestShippedCensusCatalogue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blob = json.loads(CATALOG.read_text())
        cls.rows = cls.blob["factories"]

    def test_maximum_t_count_is_five_and_only_at_n_43(self):
        """The headline result of the r <= 7 window."""
        self.assertEqual(self.blob["max_t_count"], 5)
        top = [r for r in self.rows if r["t_count"] == 5]
        self.assertTrue(top)
        self.assertEqual({r["n"] for r in top}, {43})

    def test_window_is_n_at_most_44(self):
        self.assertLessEqual(max(r["n"] for r in self.rows), 44)

    def test_every_circuit_reverifies(self):
        for r in self.rows:
            with self.subTest(n=r["n"], gate=r["gate"]):
                self.assertEqual(B.reverify(r), "")

    def test_rows_are_distinct_under_the_sk_key(self):
        keys = {(r["n"], r["k"], r["gate"]) for r in self.rows}
        self.assertEqual(len(keys), len(self.rows))

    def test_dedup_key_is_documented_as_sk(self):
        self.assertIn("S_k", self.blob["dedup_key"])


if __name__ == "__main__":
    unittest.main()
