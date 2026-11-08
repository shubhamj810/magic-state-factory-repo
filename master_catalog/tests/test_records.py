"""records.py: the record rule with direct sums, on hand-made rows and against
a brute-force enumeration of sums."""
from __future__ import annotations

import itertools
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import records as R                                               # noqa: E402


def row(label, n, k, d, gate="T"):
    human = "·".join(f"{gate}{i}" if gate == "T" else f"{gate}{i}{i + 1}"
                     for i in range(k)) if gate in ("T", "CS") else gate
    return {"catalog_label": label, "n": n, "k": k, "d": d, "gate_human": human}


def verdict(rows, label, cls="T"):
    return R.status(rows)[label][cls]


class TestRule(unittest.TestCase):
    def test_a_lone_row_is_a_record(self):
        self.assertTrue(verdict([row("a", 15, 1, 3)], "a")["record"])

    def test_a_sum_that_equals_the_row_takes_the_record(self):
        rows = [row("one", 15, 1, 3), row("two", 30, 2, 3)]
        self.assertTrue(verdict(rows, "one")["record"])
        v = verdict(rows, "two")
        self.assertFalse(v["record"])
        self.assertEqual(v["sum_reaches"], 2)

    def test_a_sum_with_more_inputs_does_not(self):
        rows = [row("one", 15, 1, 3), row("two", 29, 2, 3)]
        self.assertTrue(verdict(rows, "two")["record"])

    def test_a_row_at_a_higher_distance_dominates(self):
        rows = [row("lo", 100, 10, 4), row("hi", 100, 10, 5)]
        v = verdict(rows, "lo")
        self.assertFalse(v["record"])
        self.assertEqual(v["dominated_by"], "hi")
        self.assertTrue(verdict(rows, "hi")["record"])

    def test_a_sum_has_the_least_distance_of_its_parts(self):
        rows = [row("a", 15, 1, 3), row("b", 20, 2, 5), row("c", 35, 3, 3),
                row("e", 35, 3, 4)]
        self.assertFalse(verdict(rows, "c")["record"])   # 15 + 20 at d = 3
        self.assertTrue(verdict(rows, "e")["record"])    # needs both parts at d >= 4

    def test_a_tie_keeps_both(self):
        rows = [row("x", 50, 4, 3), row("y", 50, 4, 3)]
        self.assertTrue(verdict(rows, "x")["record"])
        self.assertTrue(verdict(rows, "y")["record"])

    def test_classes_are_kept_apart_and_all_gates_mixes_them(self):
        rows = [row("t", 15, 1, 3), row("ccz", 30, 2, 3, gate="CCZ012")]
        self.assertTrue(verdict(rows, "ccz", "CCZ")["record"])
        self.assertFalse(verdict(rows, "ccz", "all")["record"])

    def test_the_gate_classes(self):
        self.assertEqual(R.gate_class("T0·T1"), "T")
        self.assertEqual(R.gate_class("CS01"), "CS")
        self.assertEqual(R.gate_class("CCZ012·CCZ013"), "CCZ")
        self.assertEqual(R.gate_class("T1·CS01·CS02"), "mixed")
        with self.assertRaises(ValueError):
            R.gate_class("X0")


class TestAgainstBruteForce(unittest.TestCase):
    def test_random_catalogues(self):
        """Every verdict against an enumeration of every multiset of up to
        five rows (the instances are small enough that no sum of six fits)."""
        rng = random.Random(20261107)
        for trial in range(200):
            rows = [row(f"r{i}", rng.randint(8, 40), rng.randint(1, 6), rng.randint(2, 5))
                    for i in range(rng.randint(1, 7))]
            got = R.status(rows)
            for r in rows:
                n, k, d = r["n"], r["k"], r["d"]
                single = any(s is not r and s["n"] <= n and s["k"] >= k and s["d"] >= d
                             and (s["n"], s["k"], s["d"]) != (n, k, d) for s in rows)
                summed = False
                for size in range(2, 6):
                    for combo in itertools.combinations_with_replacement(rows, size):
                        if sum(c["n"] for c in combo) <= n \
                                and sum(c["k"] for c in combo) >= k \
                                and min(c["d"] for c in combo) >= d:
                            summed = True
                            break
                    if summed:
                        break
                with self.subTest(trial=trial, row=(n, k, d)):
                    self.assertEqual(got[r["catalog_label"]]["T"]["record"],
                                     not single and not summed)


if __name__ == "__main__":
    unittest.main()
