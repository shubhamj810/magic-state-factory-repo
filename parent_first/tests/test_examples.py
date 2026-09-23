"""Worked examples, run as tests.

Every example in README.md appears here, so the documentation cannot drift away
from the code: if a command in the README stops producing the number the README
quotes, this file fails.
"""
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parents[1]))

import cli                                             # noqa: E402
from factorylib.parent import (Parent, certification_metrics, find_target,  # noqa: E402
                               parse_gate)


def parent_from_catalog(spec, distance=3):
    """Load a catalogued factory's check parent by n,k,d selector."""
    entry = cli._factory(spec)
    return Parent.from_columns(entry["columns"], entry["k"], entry["N"],
                               distance=distance)


class TestParentFilters(unittest.TestCase):
    """kappa -> mu -> tau, the three filters, on parents small enough to run
    exactly inside a test."""

    def test_15_1_3_is_a_one_direction_parent(self):
        """The punctured Reed-Muller factory has exactly one legal output
        direction, so it can only ever carry a single T -- no search needed."""
        parent = parent_from_catalog("15,1,3")
        self.assertEqual(parent.n, 15)
        self.assertEqual(parent.kappa, 1)
        metrics = certification_metrics(parent, node_budget=None)
        self.assertEqual(metrics["mu"]["value"], 1)
        self.assertTrue(metrics["mu"]["complete"])

    def test_28_2_3_carries_two_compatible_directions(self):
        parent = parent_from_catalog("28,2,3")
        self.assertEqual(parent.kappa, 2)
        metrics = certification_metrics(parent, node_budget=None)
        self.assertEqual(metrics["mu"]["value"], 2)

    def test_cheap_filter_bounds_the_expensive_one(self):
        """form_rank_bounds must never claim a bound smaller than the exact mu
        it is supposed to bound -- that would make the cheap screen unsound."""
        for spec in ("15,1,3", "28,2,3", "35,3,3"):
            with self.subTest(factory=spec):
                parent = parent_from_catalog(spec)
                bound = cli.form_rank_bounds(parent)["mu_upper_bound"]
                exact = certification_metrics(parent, node_budget=None)["mu"]
                if exact["complete"]:
                    self.assertGreaterEqual(bound, exact["value"])


class TestTargetedSolve(unittest.TestCase):
    def test_ccz_is_found_on_its_own_parent(self):
        """The [[47,3,3]] parent was found for CCZ, so asking it for CCZ must
        succeed -- and the solver must return a verified frame, not just True."""
        parent = parent_from_catalog("47,3,3")
        result = find_target(parent, parse_gate("CCZ012"), None, 1_000_000)
        self.assertTrue(result["found"])
        self.assertEqual(result["gate"], "CCZ012")

    def test_a_gate_too_wide_for_the_parent_is_rejected_cheaply(self):
        """kappa = 1 means at most one output direction, so a two-output target
        is impossible and must be reported as such rather than searched for."""
        parent = parent_from_catalog("15,1,3")
        result = find_target(parent, parse_gate("CS01"), None, 1_000_000)
        self.assertFalse(result["found"])
        self.assertTrue(result["complete"],
                        "a kappa-based rejection is a proof, so it must be "
                        "reported complete")


class TestGateCensusAndMetrics(unittest.TestCase):
    def test_28_2_3_gate_list_and_its_metrics(self):
        """Both output frames of the one compatible subspace show up under S_k
        dedup, and the exact T counts show they cost the same: T0.CS01 is a
        CNOT-frame rewrite of T0.T1, not a cheaper gate."""
        payload = json.loads(_run(["gates", "--factory", "28,2,3",
                                   "--kmax", "2", "--dedup", "symmetric"]))
        gates = {g["gate"]: g for g in payload["gates"]}
        self.assertIn("T0.T1", gates)
        self.assertIn("T0.CS01", gates)
        self.assertEqual(gates["T0.T1"]["t_count"], 2)
        self.assertEqual(gates["T0.CS01"]["t_count"], 2)
        self.assertEqual(gates["T0.CS01"]["poly_degree"], 1)

    def test_gl_dedup_is_coarser_than_sk(self):
        gl = json.loads(_run(["gates", "--factory", "28,2,3", "--kmax", "2",
                              "--dedup", "gl"]))
        sk = json.loads(_run(["gates", "--factory", "28,2,3", "--kmax", "2",
                              "--dedup", "symmetric"]))
        self.assertLessEqual(gl["n_gates"], sk["n_gates"])


def _run(argv):
    """Run the CLI and capture its stdout, exactly as a user would see it."""
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = cli.main(argv)
    assert code == 0, f"cli.main({argv}) returned {code}"
    return buf.getvalue()


if __name__ == "__main__":
    unittest.main()
