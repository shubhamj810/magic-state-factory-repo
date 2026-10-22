"""`errorcoeff.py` and the catalogue's ``A_d`` field.

* **The meaning**, on factories whose coefficient is in print: the 15-to-1
  has ``A_3 = 35`` (Bravyi and Kitaev's ``35 p^3``), the 8-``T`` ``CCZ``
  factory ``A_2 = 28``, and ``[[14, 2, 2]]`` ``A_2 = 7``, the ``3k + 1`` of
  Bravyi and Haah's ``[[3k+8, k, 2]]`` family at ``k = 2``.  ``A_d`` belongs
  to the stored CIRCUIT, not to its class: at ``k = 4, 6`` the catalogue
  stores the borrowed-identity circuits, with three check wires, and they
  have ``A_2 = 22`` and ``49`` where Bravyi and Haah's codes have 13 and 19.
* **The count against the definition**: on every catalogue row whose
  ``C(n, d)`` weight-``d`` subsets number at most 200,000, each subset is
  tested here by a plain loop -- XOR its columns' check bits and output bits --
  and the harmful ones are counted.  Both the stored ``A_d`` and the MacWilliams
  difference must equal that count.
* **The two methods against each other**: on rows where both run, the
  MacWilliams count of accepted faults equals the enumerated one.
* **The rejections**: a row whose ``A_d`` is wrong, or present on a floor.
"""
from __future__ import annotations

import copy
import itertools
import sys
import unittest
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE.parent
sys.path.insert(0, str(CATALOGUE))
sys.path.insert(0, str(CATALOGUE.parent))

import catalogfile as CF                                          # noqa: E402
import errorcoeff as EC                                           # noqa: E402
import verify_catalog as VC                                       # noqa: E402

LITERAL_CAP = 200_000


def literal_count(columns, k, w):
    """Harmful accepted faults of weight ``w``, one subset at a time."""
    count = 0
    for subset in itertools.combinations(columns, w):
        checks, outputs = set(), set()
        for column in subset:
            for q in column:
                (outputs if q < k else checks).symmetric_difference_update({q})
        if not checks and outputs:
            count += 1
    return count


class Fixtures:
    payload = None

    @classmethod
    def rows(cls):
        if cls.payload is None:
            cls.payload = CF.load()
        return cls.payload["factories"]

    @classmethod
    def row(cls, label):
        return next(r for r in cls.rows() if r["catalog_label"] == label)


class TestMeaning(unittest.TestCase):
    def test_fifteen_to_one(self):
        row = Fixtures.row("15.1.3.a")
        self.assertEqual(row["A_d"], 35)
        self.assertEqual(literal_count(row["columns"], 1, 3), 35)

    def test_eight_t_ccz(self):
        row = Fixtures.row("8.3.2.a")
        self.assertEqual(row["A_d"], 28)
        self.assertEqual(comb(8, 2), 28)

    def test_the_same_class_from_a_different_circuit(self):
        self.assertEqual(Fixtures.row("14.2.2.a")["A_d"], 3 * 2 + 1)
        for label, k, a_d in (("20.4.2.a", 4, 22), ("26.6.2.a", 6, 49)):
            row = Fixtures.row(label)
            self.assertEqual((row["N"], row["A_d"]), (k + 3, a_d), label)
            self.assertGreater(a_d, 3 * k + 1)


class TestAgainstDefinition(unittest.TestCase):
    def test_every_small_row(self):
        checked = 0
        for row in Fixtures.rows():
            if not row["d_is_exact"] or comb(row["n"], row["d"]) > LITERAL_CAP:
                continue
            want = literal_count(row["columns"], row["k"], row["d"])
            self.assertEqual(row["A_d"], want, row["catalog_label"])
            got = EC.error_coefficient(row["columns"], row["k"], row["N"],
                                       row["d"])
            self.assertEqual(got["count"], want, row["catalog_label"])
            checked += 1
        self.assertGreater(checked, 300)

    def test_methods_agree(self):
        """Accepted faults by MacWilliams and by enumeration, both ways."""
        checked = 0
        for row in Fixtures.rows():
            if not row["d_is_exact"] or row["N"] > EC.MACWILLIAMS_FIRST \
                    or row["n"] > 300:
                continue
            for k in (row["k"], 0):
                n = row["n"]
                basis = EC._basis(EC.FC.rows_over_columns(
                    row["columns"], row["N"])[k:])
                by_algebra = EC.dual_count(EC.span_weights(basis, n), n,
                                           row["d"])
                by_sweep = EC._enumerated(row["columns"], k, row["N"],
                                          row["d"])
                if by_sweep is not None:
                    self.assertEqual(by_algebra, by_sweep, row["catalog_label"])
                    checked += 1
        self.assertGreater(checked, 500)

    def test_macwilliams_on_a_known_code(self):
        """The [7,4,3] Hamming code: 7 words of weight 3, 7 of weight 4."""
        generator = [0b1110000, 0b1001100, 0b0101010, 0b1101001]
        parity = [0b0001111, 0b0110011, 0b1010101]
        dist = EC.span_weights(EC._basis(parity), 7)
        self.assertEqual(dist, [1, 0, 0, 0, 7, 0, 0, 0])
        self.assertEqual([EC.dual_count(dist, 7, w) for w in range(8)],
                         [1, 0, 0, 7, 7, 0, 0, 1])
        self.assertEqual(EC.span_weights(EC._basis(generator), 7),
                         [1, 0, 0, 7, 7, 0, 0, 1])


class TestRejections(unittest.TestCase):
    def test_wrong_count(self):
        row = copy.deepcopy(Fixtures.row("15.1.3.a"))
        row["A_d"] = 34
        _facts, problems = VC.verify_row(row)
        self.assertIn("A_d-mismatch", [kind for kind, _ in problems])

    def test_count_on_a_floor(self):
        row = copy.deepcopy(next(r for r in Fixtures.rows()
                                 if not r["d_is_exact"]))
        row["A_d"] = 1
        _facts, problems = VC.verify_row(row)
        self.assertIn("A_d-mismatch", [kind for kind, _ in problems])

    def test_missing_count(self):
        row = copy.deepcopy(Fixtures.row("8.3.2.a"))
        row["A_d"] = None
        _facts, problems = VC.verify_row(row)
        self.assertIn("A_d-mismatch", [kind for kind, _ in problems])


if __name__ == "__main__":
    unittest.main()
