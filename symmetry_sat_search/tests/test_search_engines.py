"""Do the two search engines actually find the factories they claim to?

Both engines are re-run here on the smallest cases, from scratch, and their
answers checked against the known optima.  These are fast (well under a second
each) because the small end of the problem is genuinely small -- the point is
that they exercise the real solve path, not a cached result.
"""

# The search engines need OR-Tools CP-SAT.  Everything else in this directory
# (the catalogue build, the verifiers, the symmetry groups) runs without it, so
# a checkout with no solver installed should SKIP these rather than fail to
# import -- otherwise `selfcheck.py` reports a red suite for a missing optional
# dependency.  See requirements.txt.
try:
    import ortools  # noqa: F401
    HAVE_ORTOOLS = True
except ImportError:                                        # pragma: no cover
    HAVE_ORTOOLS = False

SKIP_REASON = "OR-Tools not installed (pip install -r ../requirements.txt)"

import io
import contextlib
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from evaluator import _distance, describe_output       # noqa: E402

if HAVE_ORTOOLS:
    import sat_search                                  # noqa: E402
    import slot_search                                 # noqa: E402


def quiet(fn, *args, **kwargs):
    """Run a noisy engine and keep its stdout out of the test report."""
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


@unittest.skipUnless(HAVE_ORTOOLS, SKIP_REASON)
class TestExhaustiveSat(unittest.TestCase):
    """`sat_search` searches the WHOLE circuit space at fixed N, so a returned
    optimum is a certified global minimum T count -- not a record."""

    def test_reproduces_the_14_1_2_optimum(self):
        res = quiet(sat_search.run, 1, 4, "T", d=2)
        self.assertEqual(res["status"], "OPTIMAL")
        self.assertEqual((res["n"], res["d"]), (14, 2))
        self.assertTrue(res["verified"]["target_ok"])

    def test_reproduces_the_15_1_3_optimum(self):
        """The punctured Reed-Muller factory: 15 T states in, one out, and no
        circuit on 5 qubits does it with fewer."""
        res = quiet(sat_search.run, 1, 5, "T", d=3)
        self.assertEqual(res["status"], "OPTIMAL")
        self.assertEqual((res["n"], res["d"]), (15, 3))
        self.assertTrue(res["verified"]["target_ok"])

    def test_unsat_is_reported_as_unsat(self):
        """A distance-3 two-output T factory does not fit on 6 qubits.  UNSAT
        here is a proof of nonexistence at that N, not a failure to find."""
        res = quiet(sat_search.run, 2, 6, "T", d=3)
        self.assertEqual(res["status"], "UNSAT")


@unittest.skipUnless(HAVE_ORTOOLS, SKIP_REASON)
class TestSlotAnsatz(unittest.TestCase):
    """`slot_search` restricts to a symmetry ansatz, so its optimum is optimal
    WITHIN the ansatz.  On the small cases the ansatz happens to contain the
    true optimum, which is what makes this a meaningful cross-check."""

    def _solve_c5(self):
        res = quiet(slot_search.solve, 1, [("C", 5)], "T", d_target=3)
        self.assertEqual(res["status"], "OPTIMAL")
        return res, slot_search.columns_of(res["geometry"], res["assignment"])

    def test_c5_geometry_gives_the_15_1_3_factory(self):
        """One cyclic block of 5 checks reaches the same 15-column optimum the
        exhaustive search certifies -- the ansatz contains the true optimum
        here, which is why the two engines can be compared at all."""
        res, cols = self._solve_c5()
        self.assertEqual(len(cols), 15)
        ok, dist = slot_search.verify(1, res["geometry"].N, cols, "T", dmax=4)
        self.assertTrue(ok)
        self.assertEqual(dist, 3)

    def test_rebuilt_circuit_matches_the_evaluator(self):
        """slot_search.verify and evaluator._distance are separate
        implementations of the same fault enumeration; they must agree."""
        _res, cols = self._solve_c5()
        masks = [sum(1 << q for q in c) for c in cols]
        self.assertEqual(_distance(masks, 1, 4), 3)
        self.assertEqual(describe_output([tuple(sorted(c)) for c in cols], 1)[0],
                         "T0")

    def test_the_stored_slot_assignment_rebuilds_deterministically(self):
        """Stored slot-search factories are rebuilt from their saved
        assignments, with no solver in the loop. Check that path here on
        the smallest geometry: same geometry + same assignment => same columns.
        """
        res, cols = self._solve_c5()
        again = slot_search.columns_of(slot_search.Geometry(1, [("C", 5)]),
                                       res["assignment"])
        self.assertEqual([sorted(c) for c in cols], [sorted(c) for c in again])


if __name__ == "__main__":
    unittest.main()
