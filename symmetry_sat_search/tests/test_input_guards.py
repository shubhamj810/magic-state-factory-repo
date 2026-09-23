"""Search requests that must be refused, and statuses that must not exit 0.

A solver answers the question it was given.  Every case here is a question that
looks like a factory search, gets a confident answer, and is not the search the
caller meant:

  * a width-w gate on fewer than w output wires, so a CHECK qubit stands in for
    an output and `target_ok=True` describes a different circuit;
  * a custom target naming a check qubit, the same mistake by another route;
  * `k > N`, which used to die with a bare KeyError inside the model;
  * `exact_d4` with an unnamed target, which its `_tbit` reads as the all-zero
    target and would "prove" a distance-four optimum for the empty gate.

And one status: `UNKNOWN` is not an answer, so a run that ends there does not
exit 0.  (`exact_d4` treats a `FEASIBLE` incumbent the same way, for the same
reason -- its claim is exactness, and a timed-out solve proved no minimality --
but that needs a solve that gives up at exactly the wrong moment, so it is not
reproducible as a test.)
"""
import contextlib
import io
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parents[1]))

import exact_d4                                          # noqa: E402
import slot_search                                       # noqa: E402
from sat_search import (parse_target_monomials, search,   # noqa: E402
                        target_D)


class TestNamedTargets(unittest.TestCase):

    def test_a_width_2_gate_needs_two_outputs(self):
        with self.assertRaises(ValueError) as caught:
            target_D("CS", k=1, N=12, level=3)
        self.assertIn("k >= 2", str(caught.exception))

    def test_a_level_mismatch_is_refused(self):
        with self.assertRaises(ValueError) as caught:
            target_D("T", k=1, N=12, level=2)
        self.assertIn("level-3", str(caught.exception))

    def test_a_named_target_that_fits_is_accepted(self):
        self.assertEqual(target_D("CS", k=2, N=12, level=3), {(0, 1)})
        self.assertEqual(target_D("T", k=3, N=12, level=3),
                         {(0,), (1,), (2,)})


class TestCustomTargets(unittest.TestCase):

    def test_a_monomial_on_a_check_qubit_is_refused(self):
        with self.assertRaises(ValueError) as caught:
            target_D({2: [(0, 1)]}, k=1, N=12, level=3)
        self.assertIn("CHECK qubit", str(caught.exception))

    def test_a_degree_above_the_level_is_refused(self):
        with self.assertRaises(ValueError) as caught:
            target_D({3: [(0, 1, 2)]}, k=3, N=12, level=2)
        self.assertIn("degree 3", str(caught.exception))

    def test_an_empty_monomial_is_refused(self):
        with self.assertRaises(ValueError):
            target_D({0: [()]}, k=2, N=12, level=3)

    def test_a_mislabelled_degree_is_refused(self):
        with self.assertRaises(ValueError):
            target_D({3: [(0, 1)]}, k=2, N=12, level=3)

    def test_a_negative_qubit_index_is_refused(self):
        """-1 sorts to the front, where the upper-bound check never sees it."""
        with self.assertRaises(ValueError) as caught:
            target_D({1: [(-1,)]}, k=2, N=6, level=3)
        self.assertIn("negative", str(caught.exception))

    def test_a_non_integer_qubit_index_is_refused(self):
        """A ValueError naming the problem, not a TypeError from `sorted`."""
        for mon in ((0, "1"), (None,), (1.5,)):
            with self.subTest(mon=mon), self.assertRaises(ValueError):
                target_D({len(mon): [mon]}, k=3, N=6, level=3)

    def test_a_non_integer_degree_key_is_refused(self):
        """The key IS the degree, so `'2'` is not a synonym for 2.

        The length check only fired for int keys, so a string or boolean key
        skipped it entirely and the target was filed under a degree that says
        nothing about its contents.
        """
        for key in ("2", "garbage", True, 2.0):
            with self.subTest(key=key), self.assertRaises(ValueError):
                target_D({key: [(0, 1)]}, k=2, N=6, level=3)

    def test_a_custom_target_on_outputs_is_accepted(self):
        self.assertEqual(target_D({1: [(0,)], 2: [(0, 1)]}, k=2, N=6, level=3),
                         {(0,), (0, 1)})

    def test_catalogue_notation_round_trips(self):
        self.assertEqual(parse_target_monomials("0+01+012"),
                         {1: [(0,)], 2: [(0, 1)], 3: [(0, 1, 2)]})
        self.assertEqual(target_D(parse_target_monomials("01+02"), k=3, N=6,
                                  level=3),
                         {(0, 1), (0, 2)})

    def test_unreadable_notation_is_refused(self):
        for spec in ("", "CS01", "0+x", "+"):
            with self.subTest(spec=spec), self.assertRaises(ValueError):
                parse_target_monomials(spec)


class TestGeometryBounds(unittest.TestCase):

    def test_more_outputs_than_qubits_is_refused(self):
        with self.assertRaises(ValueError) as caught:
            search(k=5, N=3, target="T")
        self.assertIn("1 <= k <= N", str(caught.exception))

    def test_a_slot_search_width_mismatch_is_refused(self):
        with self.assertRaises(ValueError) as caught:
            slot_search.run(1, "CCZ", [[("S", 4)]], d_target=3, time_s=1)
        self.assertIn("k >= 3", str(caught.exception))

    def test_exact_d4_refuses_an_unnamed_target(self):
        with self.assertRaises(ValueError) as caught:
            exact_d4.exact_solve(1, [("C", 9)], {1: [(0,)]}, time_s=1)
        self.assertIn("named targets", str(caught.exception))

    def test_exact_d4_refuses_a_width_mismatch(self):
        with self.assertRaises(ValueError) as caught:
            exact_d4.exact_solve(1, [("C", 9)], "CCZ", time_s=1)
        self.assertIn("k >= 3", str(caught.exception))


class TestUnresolvedIsNotSuccess(unittest.TestCase):
    """`run` counts what it did not settle; the CLI turns that into its exit."""

    @staticmethod
    def _quiet_run(*args, **kwargs):
        """slot_search.run prints a per-geometry report; keep it out of the log."""
        with contextlib.redirect_stdout(io.StringIO()):
            return slot_search.run(*args, **kwargs)

    def test_a_timed_out_slot_search_counts_as_unresolved(self):
        """`--time 0` reports UNKNOWN for every geometry; that is not success."""
        self.assertEqual(
            self._quiet_run(1, "T", [[("S", 4), ("C", 7)]], d_target=3, time_s=0),
            1)

    def test_an_unsat_geometry_is_a_real_answer(self):
        """UNSAT means "no factory here", which is an answer and exits 0.

        k=1 T at distance 3 on a single S3 block has no solution, and the solver
        proves it in milliseconds.
        """
        self.assertEqual(
            self._quiet_run(1, "T", [[("S", 3)]], d_target=3, time_s=30), 0)


if __name__ == "__main__":
    unittest.main()
