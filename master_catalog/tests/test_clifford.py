"""`clifford.py` and the verifier's Clifford checks.

Three things are pinned here.

* **The correction** against the definition: on every catalogue row with at
  most 12 wires, the phase of the corrected circuit is computed on every input
  by a separate loop here, and must be the gate's.  Plus the worked examples
  -- the 15-to-1 deposits ``T-dagger`` and needs an ``S``; the ``[[3,1,1]]``
  code of Jain and Albert (arXiv:2408.12752, Sec. II.B) needs ``S-dagger`` on
  its second qubit, which on the wires is ``S-dagger`` on both and a ``CZ``.
* **The solver** against brute force: on random small systems, feasible and
  infeasible, `clifford.rotation_powers` finds a solution exactly when one of
  the ``4^n`` power assignments works.
* **The rejections**: a shipped row with its correction or powers broken in
  each way the verifier must catch.
"""
from __future__ import annotations

import copy
import itertools
import json
import random
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE.parent
sys.path.insert(0, str(CATALOGUE))
sys.path.insert(0, str(CATALOGUE.parent))

import catalogfile as CF                                          # noqa: E402
import clifford as CL                                             # noqa: E402
import faultcore as FC                                            # noqa: E402
import verify_catalog as VC                                       # noqa: E402

T_GATE = frozenset({frozenset({0})})


def gate_of(columns, k, N):
    return FC.recover_gate(FC.rows_over_columns(columns, N), k)


def phase_table(columns, N, powers=None):
    """``sum_c p_c |c . v|`` for every input ``v``, by a plain loop."""
    full = CL.powers_list(powers, len(columns))
    out = {}
    for v in itertools.product((0, 1), repeat=N):
        out[v] = sum(p * (sum(v[q] for q in c) % 2)
                     for c, p in zip(columns, full)) % 8
    return out


def gate_phase(gate, v):
    return sum({1: 1, 2: 2, 3: 4}[len(m)] for m in gate if all(v[q] for q in m))


def correction_phase(corr, v):
    return (sum(2 * p * v[q] for q, p in corr["S"])
            + sum(4 * v[q] * v[r] for q, r in corr["CZ"]))


def brute_force_powers(columns, N, corr):
    """Does any ``s`` in ``Z_4^n`` give ``sum s_c 2|c.v| = correction(v)``?"""
    V = np.array(list(itertools.product((0, 1), repeat=N)), dtype=np.int64)
    M = np.zeros((N, len(columns)), dtype=np.int64)
    for j, c in enumerate(columns):
        M[list(c), j] = 1
    parity = (V @ M) % 2
    want = np.array([correction_phase(corr, v) % 8 for v in V])
    sigma = np.array(list(itertools.product(range(4), repeat=len(columns))),
                     dtype=np.int64)
    return bool(np.any(np.all((2 * parity @ sigma.T) % 8 == want[:, None], axis=0)))


class TheCorrection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = CF.load()["factories"]

    def test_the_15_to_1_needs_an_s_or_t_dagger_everywhere(self):
        row, = [r for r in self.rows if r["catalog_label"] == "15.1.3.a"]
        self.assertEqual(row["clifford_correction"], {"S": [[0, 1]], "CZ": []})
        self.assertEqual(row["rotation_powers"], [[c, 7] for c in range(15)])

    def test_the_paper_s_three_qubit_example(self):
        """Jain and Albert's [[3,1,1]] code, rows 111 and 110: T on every qubit
        needs S-dagger on qubit 3 (their Sec. II.B).  Qubit 3 carries the parity
        of both wires, so on the wires that is S-dagger, S-dagger and a CZ."""
        columns = [[0, 1], [0, 1], [0]]
        rows = FC.rows_over_columns(columns, 2)
        corr = CL.correction(rows, 1, 2, T_GATE)
        self.assertEqual(corr, {"S": [[0, 3], [1, 3]], "CZ": [[0, 1]]})
        failures, scope = CL.logical_action(columns, 1, 2, T_GATE, corr=corr)
        self.assertEqual((failures, scope), ([], "every input"))

    def test_every_small_row_is_exactly_its_gate_once_corrected(self):
        """The definition, by a loop that shares nothing with `clifford`."""
        checked = 0
        for row in self.rows:
            if row["N"] > 12:
                continue
            columns, k, N = row["columns"], row["k"], row["N"]
            gate = gate_of(columns, k, N)
            corr = row["clifford_correction"]
            rotations = phase_table(columns, N)
            with self.subTest(label=row["catalog_label"]):
                for v, phase in rotations.items():
                    self.assertEqual((phase + correction_phase(corr, v)
                                      - gate_phase(gate, v)) % 8, 0, v)
                if row["rotation_powers"]:
                    powered = phase_table(columns, N, row["rotation_powers"])
                    for v, phase in powered.items():
                        self.assertEqual((phase - gate_phase(gate, v)) % 8, 0, v)
            checked += 1
        self.assertGreater(checked, 250)

    def test_uncorrected_circuits_fail_exactly_when_a_correction_is_listed(self):
        for row in self.rows[:300]:
            columns, k, N = row["columns"], row["k"], row["N"]
            failures, _scope = CL.logical_action(columns, k, N, gate_of(columns, k, N))
            with self.subTest(label=row["catalog_label"]):
                self.assertEqual(bool(failures),
                                 not CL.is_trivial(row["clifford_correction"]))

    def test_the_statevector_agrees_with_the_evaluation(self):
        """The gate-by-gate simulation accepts the stored correction, and
        rejects the circuit when the correction is left off."""
        seen = 0
        for row in self.rows:
            columns, k, N = row["columns"], row["k"], row["N"]
            if not VC.statevector_fits(N, k) or N > 8:
                continue
            gate = gate_of(columns, k, N)
            corr = row["clifford_correction"]
            with self.subTest(label=row["catalog_label"]):
                self.assertEqual(VC.statevector_problems(columns, k, N, gate, corr, None), [])
                if not CL.is_trivial(corr):
                    self.assertTrue(VC.statevector_problems(columns, k, N, gate, None, None))
            seen += 1
            if seen >= 60:
                break
        self.assertEqual(seen, 60)


class TheSolver(unittest.TestCase):
    def test_against_brute_force_on_random_systems(self):
        """Random column sets and random corrections (half of them made from a
        random power assignment, so feasible): the solver says feasible exactly
        when brute force finds powers, and its powers work."""
        rng = random.Random(11)
        feasible = infeasible = 0
        for _trial in range(400):
            N = rng.randint(1, 4)
            subsets = [c for r in range(1, N + 1)
                       for c in itertools.combinations(range(N), r)]
            n = rng.randint(1, min(6, len(subsets)))
            columns = [list(c) for c in rng.sample(subsets, n)]
            rows = FC.rows_over_columns(columns, N)
            if rng.random() < 0.5:
                sigma = [rng.randrange(4) for _ in range(n)]
                S = [[q, sum(sigma[j] for j in range(n) if q in columns[j]) % 4]
                     for q in range(N)]
                CZ = [[q, r] for q, r in itertools.combinations(range(N), 2)
                      if sum(sigma[j] for j in range(n)
                             if q in columns[j] and r in columns[j]) % 2]
                corr = {"S": [e for e in S if e[1]], "CZ": CZ}
            else:
                corr = {"S": [[q, rng.randint(1, 3)] for q in range(N)
                              if rng.random() < 0.5],
                        "CZ": [[q, r] for q, r in itertools.combinations(range(N), 2)
                               if rng.random() < 0.3]}
            found = CL.rotation_powers(rows, n, N, corr)
            with self.subTest(columns=columns, corr=corr):
                self.assertEqual(found is not None, brute_force_powers(columns, N, corr))
                if found:
                    full = CL.powers_list(found, n)
                    for v in itertools.product((0, 1), repeat=N):
                        extra = sum((p - 1) * (sum(v[q] for q in c) % 2)
                                    for c, p in zip(columns, full))
                        self.assertEqual((extra - correction_phase(corr, v)) % 8, 0)
            if found is None:
                infeasible += 1
            else:
                feasible += 1
        self.assertGreater(feasible, 100)
        self.assertGreater(infeasible, 50)


class TheRejections(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows = CF.load()["factories"]
        cls.powers_row, = [r for r in rows if r["catalog_label"] == "15.1.3.a"]
        cls.required_row = next(r for r in rows if r["rotation_powers"] is None
                                and r["n"] <= 40 and r["k"] <= 4)
        cls.none_row = next(r for r in rows
                            if CL.is_trivial(r["clifford_correction"]))

    def problems(self, row, **changes):
        row = copy.deepcopy(row)
        row.update(changes)
        _facts, problems = VC.verify_row(row, reference=False)
        return {kind for kind, _detail in problems}

    def test_the_shipped_rows_pass(self):
        for row in (self.powers_row, self.required_row, self.none_row):
            with self.subTest(label=row["catalog_label"]):
                self.assertEqual(self.problems(row), set())

    def test_a_wrong_correction(self):
        self.assertIn("clifford-correction", self.problems(
            self.powers_row, clifford_correction={"S": [[0, 3]], "CZ": []}))
        self.assertIn("clifford-correction", self.problems(
            self.powers_row, clifford_correction={"S": [], "CZ": []}))

    def test_a_correction_of_the_wrong_shape(self):
        self.assertIn("clifford-correction", self.problems(
            self.powers_row, clifford_correction={"S": [[0, True]], "CZ": []}))
        self.assertIn("clifford-correction", self.problems(
            self.powers_row, clifford_correction={"S": [[0, 1]]}))

    def test_powers_that_do_not_work(self):
        self.assertIn("rotation-powers", self.problems(
            self.powers_row, rotation_powers=[[0, 7]]))
        self.assertIn("rotation-powers", self.problems(
            self.powers_row, rotation_powers=[[c, 3] for c in range(15)]))

    def test_powers_of_the_wrong_shape(self):
        self.assertIn("rotation-powers", self.problems(
            self.powers_row, rotation_powers=[[c, 7] for c in reversed(range(15))]))
        self.assertIn("rotation-powers", self.problems(
            self.powers_row, rotation_powers=[[0, 1]]))
        self.assertIn("rotation-powers", self.problems(
            self.powers_row, rotation_powers=[[99, 7]]))

    def test_a_null_where_powers_exist(self):
        self.assertIn("rotation-powers", self.problems(
            self.powers_row, rotation_powers=None))

    def test_an_empty_list_for_a_real_correction(self):
        self.assertIn("rotation-powers", self.problems(
            self.powers_row, rotation_powers=[]))
        self.assertIn("rotation-powers", self.problems(
            self.required_row, rotation_powers=[]))

    def test_a_trivial_correction_takes_the_empty_list_only(self):
        self.assertIn("rotation-powers", self.problems(
            self.none_row, rotation_powers=None))
        self.assertIn("rotation-powers", self.problems(
            self.none_row, rotation_powers=[[0, 7]]))

    def test_the_fields_are_required(self):
        row = copy.deepcopy(self.powers_row)
        del row["clifford_correction"]
        _facts, problems = VC.verify_row(row, reference=False)
        self.assertIn("schema", {kind for kind, _d in problems})


if __name__ == "__main__":
    unittest.main()
