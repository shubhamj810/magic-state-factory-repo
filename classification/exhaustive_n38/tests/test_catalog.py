"""The shipped catalogue must agree with the code that claims to produce it.

These tests read `catalog/classification_n38.json` as a black box and check the
properties this repository quotes.  They fail if someone edits the catalogue by hand,
if a build is run with a stale input, or if a headline number drifts.
"""
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parents[2]))

import build_catalog as B                             # noqa: E402
from dedup import sk_canonical, sk_name               # noqa: E402
from factorylib.verification import verify            # noqa: E402

CATALOG = HERE.parent / "catalog" / "classification_n38.json"


@unittest.skipUnless(CATALOG.exists(),
                     "catalogue not built yet -- run build_catalog.py")
class TestShippedCatalogue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blob = json.loads(CATALOG.read_text())
        cls.rows = cls.blob["factories"]

    def test_headline_numbers(self):
        """74 classes, all with explicit circuits, maximum output width 5."""
        self.assertEqual(len(self.rows), 74)
        self.assertEqual(sum(1 for r in self.rows if r["has_circuit"]), 74)
        self.assertEqual(max(r["k"] for r in self.rows), 5)

    def test_window_is_n_at_most_38(self):
        self.assertLessEqual(max(r["n"] for r in self.rows), 38)

    def test_no_pure_ccz(self):
        """The witness for the CCZ >= 39 distance-3 lower bound."""
        self.assertNotIn("012", {r["gate"] for r in self.rows})

    def test_the_31_5_3_class_exists_and_is_unique(self):
        k5 = [r for r in self.rows if r["k"] == 5]
        self.assertEqual(len(k5), 1)
        self.assertEqual((k5[0]["n"], k5[0]["d"]), (31, 3))
        self.assertTrue(k5[0]["has_circuit"],
                        "the [[31,5,3]] witness must ship with its circuit")

    def test_no_k6_class(self):
        self.assertEqual([r for r in self.rows if r["k"] >= 6], [])

    def test_every_gate_label_is_sk_canonical(self):
        for r in self.rows:
            mons = {frozenset(int(c) for c in tok)
                    for tok in r["gate"].split("+") if tok}
            with self.subTest(n=r["n"], gate=r["gate"]):
                self.assertEqual(sk_name(sk_canonical(r["k"], mons)), r["gate"])

    def test_rows_are_pairwise_distinct_under_the_key(self):
        keys = {(r["n"], r["k"], r["gate"]) for r in self.rows}
        self.assertEqual(len(keys), len(self.rows))

    def test_every_circuit_reverifies(self):
        """Independent parity + fault-distance check on every stored circuit."""
        for r in self.rows:
            if not r["has_circuit"]:
                continue
            with self.subTest(n=r["n"], k=r["k"], gate=r["gate"]):
                self.assertEqual(B.reverify(r), "")

    def test_scope_limitation_is_recorded(self):
        """The mod-C caveat must survive into the shipped file, not just the
        source comments -- someone reading only the JSON has to see it."""
        self.assertIn("modulo", self.blob["scope_limitation"].lower())
        self.assertIn("S_k", self.blob["dedup_key"])


if __name__ == "__main__":
    unittest.main()
