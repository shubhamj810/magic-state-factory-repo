"""The 72 T -> 1 CCZ circuit of Gong, Pattison, Rall and Wills, re-checked.

    .venv/bin/python -m unittest discover -s literature_imports/ccz72_d6/tests

`build_ccz72.py` checks the F_8 algebra before it writes anything.  These tests
rebuild the circuit and check it again: with the master catalogue's own
primitives (`verify_catalog.derive`, `faultcore`, `errorcoeff`,
`merge_results`), and with three checks that share no code with them -- the
circuit's phase on all 2^18 inputs, the weight-6 count from the outer code's
syndromes, and the paper's Table 5 recomputed from the binarised outer code.
"""
from __future__ import annotations

import itertools
import json
import sys
import unittest
from fractions import Fraction
from math import comb, log10
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
FOLDER = HERE.parent
REPO = FOLDER.parent.parent
sys.path.insert(0, str(FOLDER))
sys.path.insert(0, str(REPO / "master_catalog"))

import build_ccz72 as B                                            # noqa: E402
import catalogfile as CF                                           # noqa: E402
import errorcoeff as EC                                            # noqa: E402
import faultcore as FC                                             # noqa: E402
import merge_results as MR                                         # noqa: E402
import verify_catalog as VC                                        # noqa: E402

K, N, N_COLUMNS, D, A6 = 3, 18, 72, 6, 37632


class Rebuild(unittest.TestCase):
    """The committed files are what the builder makes, deterministically."""

    @classmethod
    def setUpClass(cls):
        cls.H, cls.columns = B.build()

    def test_deterministic(self):
        self.assertEqual(B.build(), (self.H, self.columns))

    def test_shape(self):
        self.assertEqual(len(self.columns), N_COLUMNS)
        self.assertEqual(max(max(c) for c in self.columns) + 1, N)
        self.assertEqual(len(self.H), 9)
        self.assertEqual(len(self.H[0]), 27)

    def test_record_matches(self):
        records = json.loads(B.FACTORIES_JSON.read_text(encoding="utf-8"))
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual((record["k"], record["N"], record["n"], record["d"]),
                         (K, N, N_COLUMNS, D))
        self.assertEqual(record["columns"], self.columns)
        self.assertEqual(record["citations"], ["gong2026magic"])
        self.assertEqual(record["discovery"], "pre-existing")

    def test_files_up_to_date(self):
        self.assertEqual(B.main(["--check"]), 0)

    def test_algebra(self):
        B.check()


class Factory(unittest.TestCase):
    """The catalogue's own bar: factory condition, gate, width, distance."""

    @classmethod
    def setUpClass(cls):
        cls.H, cls.columns = B.build()

    def test_derive_clean(self):
        facts, problems = VC.derive(self.columns, K, N)
        self.assertEqual(problems, [])
        self.assertEqual(facts["n"], N_COLUMNS)
        self.assertEqual(facts["gate"], "012")
        self.assertEqual(facts["gate_human"], "CCZ012")
        self.assertEqual(facts["effective_width"], K)
        self.assertEqual(facts["clifford_correction"],
                         {"S": [[0, 2], [1, 2], [2, 2]],
                          "CZ": [[0, 1], [0, 2], [1, 2]]})

    def test_factory_condition(self):
        rows = FC.rows_over_columns(self.columns, N)
        self.assertEqual(FC.check_contamination(rows, K, N), [])
        self.assertEqual(FC.recover_gate(rows, K), {frozenset({0, 1, 2})})
        self.assertEqual(FC.redundant_checks(rows, K, N), [])

    def test_phase_on_every_input(self):
        """With every rotation a T, the phase is 4 [u != 0] mod 8 for every
        value of the 18 wires: (-1)^OR(u) on the outputs u, whatever the
        checks hold.  That is CCZ times CZ on each pair and Z on each output,
        and no check wire appears."""
        z = np.arange(1 << N, dtype=np.int64)
        phase = np.zeros(1 << N, dtype=np.int64)
        for column in self.columns:
            mask = sum(1 << q for q in column)
            v = z & mask
            parity = np.zeros_like(v)
            while v.any():
                parity ^= v & 1
                v >>= 1
            phase += parity
        outputs = z & 0b111
        np.testing.assert_array_equal(phase % 8, 4 * (outputs != 0))

    def test_distance_six(self):
        report = FC.distance_report(self.columns, K, N)
        self.assertEqual(report["d_exact"], D)
        self.assertEqual(report["scanned"],
                         {"1": "clean", "2": "clean", "3": "clean",
                          "4": "clean", "5": "clean", "6": "found"})
        witness = report["witness"]
        self.assertEqual(len(set(witness)), D)
        masks = FC.column_masks(self.columns, N)
        total = 0
        for index in witness:
            total ^= masks[index]
        self.assertEqual(total >> K, 0, "witness is detected")
        self.assertNotEqual(total & ((1 << K) - 1), 0, "witness is harmless")

    def test_leading_coefficient(self):
        result = EC.error_coefficient(self.columns, K, N, D)
        self.assertEqual(result["count"], A6)
        self.assertEqual(result["direct"], A6)


class PaperNumbers(unittest.TestCase):
    """The circuit against the numbers the paper prints."""

    @classmethod
    def setUpClass(cls):
        cls.H, _columns = B.build()
        H = np.array(cls.H, dtype=np.int64)

        def syndrome(i, v):
            """Rows hit by Z error v (bits on qubits (i, 0..2))."""
            out = np.zeros(9, dtype=np.int64)
            for j in range(3):
                if v >> (2 - j) & 1:
                    out ^= H[:, 3 * i + j]
            return out
        cls.syn = {(i, v): syndrome(i, v) for i in range(9) for v in range(1, 8)}

    def outer_failures(self, positions, errors):
        s = np.zeros(9, dtype=np.int64)
        for i, v in zip(positions, errors):
            s ^= self.syn[(i, v)]
        return not s[3:].any() and s[:3].any()

    def test_outer_count(self):
        """No qudit error of weight 1 or 2 is accepted and harmful, and 588
        of weight 3 are.  Each inner copy turns a Z error v != 0 out of
        exactly 4 of its 28 weight-2 faults, so A_6 = 4^3 * 588."""
        for w in (1, 2):
            for positions in itertools.combinations(range(9), w):
                for errors in itertools.product(range(1, 8), repeat=w):
                    self.assertFalse(self.outer_failures(positions, errors))
        count = sum(self.outer_failures(positions, errors)
                    for positions in itertools.combinations(range(9), 3)
                    for errors in itertools.product(range(1, 8), repeat=3))
        self.assertEqual(count, 588)
        self.assertEqual(4 ** 3 * count, A6)

    def test_table5(self):
        """The paper's Table 5, K(a, b, c), recomputed from the binarised
        outer code: confirms this is the paper's code in the paper's basis."""
        weight = {v: bin(v).count("1") for v in range(1, 8)}
        hits, totals = {}, {}
        for positions in itertools.permutations(range(9), 3):
            for errors in itertools.product(range(1, 8), repeat=3):
                key = tuple(sorted(weight[v] for v in errors))
                totals[key] = totals.get(key, 0) + 1
                hits[key] = hits.get(key, 0) + self.outer_failures(positions, errors)
        got = {key: Fraction(hits[key], totals[key]) for key in totals}
        self.assertEqual(got, B.TABLE5)

    def test_table7_coefficient(self):
        """10^{4.58} p^6 of Table 7 is the exact 37632 of Table 5."""
        self.assertEqual(B.table5_coefficient(), A6)
        self.assertEqual(round(log10(A6), 2), 4.58)
        self.assertEqual(comb(8, 2), 28)


class Merge(unittest.TestCase):
    """A dry merge into the shipped catalogue: a new class, or (once merged)
    the class already held."""

    def test_merge_verdict(self):
        payload = CF.load(CF.CATALOG_JSON)
        records = MR.read_records(B.FACTORIES_JSON)
        verdicts = MR.merge(payload, records, B.RELATIVE)
        (_index, verdict, row, _detail), = verdicts
        self.assertIn(verdict, ("accepted", "duplicate"))
        self.assertEqual((row["n"], row["k"], row["d"], row["N"]),
                         (N_COLUMNS, K, D, N))
        self.assertTrue(row["d_is_exact"])
        self.assertEqual(row["gate"], "012")
        self.assertEqual(row["A_d"], A6)
        self.assertEqual(row["catalog_label"], "72.3.6.a")
        self.assertIn("gong2026magic", row["citations"])


if __name__ == "__main__":
    unittest.main()
