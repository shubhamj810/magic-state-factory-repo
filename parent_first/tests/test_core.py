import itertools
import unittest

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parents[1]))

from factorylib.parent import (  # noqa: E402
    Parent,
    certification_metrics,
    classify_gates,
    gate_key,
    gate_of_rows,
    gl_orbit,
    parse_gate,
    transform_frame,
    transform_gate,
)


class ParentCheckTests(unittest.TestCase):
    """Unit tests for the shared parent model on the 15-point simplex parent (the
    check code behind the 15-to-1 factory), plus frame/phase-tensor algebra."""

    def setUp(self):
        # The punctured RM(1,4) parent: all nonzero points of F_2^4.
        self.parent = Parent.from_points(range(1, 16), ambient_rank=4, distance=3)

    def test_simplex_metrics(self):
        """kappa = mu = tau = 1 on the simplex parent: the legal quotient
        V_3(C) is one-dimensional, so a single T output (15-to-1) is all it
        supports -- and the exact searches report complete=True."""
        result = certification_metrics(self.parent, max_width=2, node_budget=None)
        self.assertEqual(result["kappa"], 1)
        self.assertEqual(result["mu"]["value"], 1)
        self.assertTrue(result["mu"]["complete"])
        self.assertEqual(result["tau"]["value"], 1)
        self.assertTrue(result["tau"]["complete"])

    def test_invalid_distance_three_parent(self):
        """A distance-3 parent must reject repeated or zero check columns
        (those are weight-<=2 undetectable faults)."""
        with self.assertRaisesRegex(ValueError, "distinct"):
            Parent.from_points([1, 1, 2], ambient_rank=2, distance=3)
        with self.assertRaisesRegex(ValueError, "nonzero"):
            Parent.from_points([0, 1, 2], ambient_rank=2, distance=3)

    def test_column_order_is_preserved_for_seed_witness(self):
        """from_columns must keep the caller's column order: the recovered
        seed_frame has to reproduce the witness gate (T0) even when the
        columns arrive reversed."""
        columns = list(reversed(self.parent.columns((1,))))
        rebuilt = Parent.from_columns(columns, outputs=1, total_rows=5, distance=3)
        self.assertIsNotNone(rebuilt.seed_frame)
        self.assertEqual(rebuilt.gate(rebuilt.seed_frame), parse_gate("T0"))

    def test_phase_tensor_action_matches_transformed_rows(self):
        """The GL(k,2) action on the phase tensor (transform_gate) must agree
        with transforming the row frame first and reading the gate off it."""
        rows = (0b1011011, 0b0111100, 0b1100101)
        wants = gate_of_rows(rows)
        for matrix in (
            (0b001, 0b010, 0b100),
            (0b011, 0b010, 0b100),
            (0b101, 0b011, 0b001),
        ):
            self.assertEqual(
                transform_gate(3, wants, matrix),
                gate_of_rows(transform_frame(rows, matrix)),
            )

    def test_product_t_does_not_collapse_to_one_t(self):
        """T0.T1 is not GL(2,2)-equivalent to a single T: its full orbit is
        {T0.T1, T0.CS01, T1.CS01} (CNOT frames trade T's against CS terms
        but never reduce the pair to one T)."""
        wants = parse_gate("T0.T1")
        orbit, complete = gl_orbit(2, wants)
        self.assertTrue(complete)
        self.assertNotIn(parse_gate("T0"), orbit)
        self.assertEqual(
            {gate_key(gate) for gate in orbit},
            {gate_key(parse_gate("T0.T1")), gate_key(parse_gate("T0.CS01")),
             gate_key(parse_gate("T1.CS01"))},
        )

    def test_gl_and_symmetric_gate_lists_verify_witness_label(self):
        """classify_gates at kmax=1 finds exactly one gate (T) under both
        dedup modes, and its witness columns must reproduce the stored
        `wants` label when the output row is read back off them."""
        for dedup in ("gl", "symmetric"):
            result = classify_gates(self.parent, kmax=1, dedup=dedup)
            self.assertTrue(result["complete"])
            self.assertEqual(result["n_gates"], 1)
            record = result["gates"][0]
            columns = record["columns"]
            output_row = sum(1 << j for j, column in enumerate(columns) if 0 in column)
            self.assertEqual(gate_key(gate_of_rows((output_row,))), tuple(map(tuple, record["wants"])))


if __name__ == "__main__":
    unittest.main()
