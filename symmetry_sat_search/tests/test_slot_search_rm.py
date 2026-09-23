#!/usr/bin/env python3
"""Regression tests for phase-support and Reed--Muller slot pruning."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# The search engines need OR-Tools CP-SAT.  Everything else in this directory
# (the catalogue build, the verifiers, the symmetry groups) runs without it, so
# a checkout with no solver installed should SKIP these rather than fail to
# import -- otherwise selfcheck.py reports a red suite for a missing optional
# dependency.  See requirements.txt.
try:
    import ortools  # noqa: F401
    HAVE_ORTOOLS = True
except ImportError:                                        # pragma: no cover
    HAVE_ORTOOLS = False

SKIP_REASON = "OR-Tools not installed (pip install -r ../requirements.txt)"


if HAVE_ORTOOLS:
    from slot_search import (
        canonical_phase_support,
        columns_of,
        rm_total_counts,
        rm_linear_slice_counts,
        rm_pair_slice_counts,
        solve,
        verify,
    )


@unittest.skipUnless(HAVE_ORTOOLS, SKIP_REASON)
class PhaseSupportTests(unittest.TestCase):
    """canonical_phase_support(k, target): the parity-vector support of a
    target, i.e. the XOR over each target monomial Q of all nonempty subsets
    of Q (so overlapping monomials can cancel shared subsets)."""

    def test_ccz_support_is_all_seven_nonzero_labels_plus_zero(self):
        self.assertEqual(
            set(canonical_phase_support(3, 'CCZ', include_zero=True)),
            {(), (0,), (1,), (2,), (0, 1), (0, 2), (1, 2), (0, 1, 2)},
        )

    def test_t3_ccz_cancellation(self):
        # T2 . CCZ012: the subset (2,) occurs in both monomials and cancels.
        target = {frozenset({2}), frozenset({0, 1, 2})}
        self.assertEqual(
            set(canonical_phase_support(3, target, include_zero=True)),
            {(), (0,), (1,), (0, 1), (0, 2), (1, 2), (0, 1, 2)},
        )

    def test_product_t_support(self):
        self.assertEqual(
            set(canonical_phase_support(5, 'T', include_zero=True)),
            {(), (0,), (1,), (2,), (3,), (4,)},
        )

    def test_disjoint_cs_ccz_support(self):
        target = {frozenset({0, 1}), frozenset({2, 3, 4})}
        support = set(canonical_phase_support(5, target, include_zero=True))
        self.assertEqual(len(support), 11)
        self.assertEqual(
            support,
            {(), (0,), (1,), (0, 1),
             (2,), (3,), (4,), (2, 3), (2, 4), (3, 4), (2, 3, 4)},
        )


@unittest.skipUnless(HAVE_ORTOOLS, SKIP_REASON)
class ReedMullerDomainTests(unittest.TestCase):
    """rm_*_counts: the column counts not excluded by the Reed--Muller weight
    spectra (the count augmented to even, w + (w mod 2), must be an allowed RM
    weight).  These domains are sound supersets: gaps prune the CP-SAT search
    but can never discard a factory."""

    def test_total_count_gap_and_small_widths(self):
        # r=5: augmented weight in {0,16,32}, so n in {0,15,16,31} below 32.
        self.assertEqual(set(rm_total_counts(5, 31)), {0, 15, 16, 31})
        allowed6 = set(rm_total_counts(6, 40))
        self.assertTrue({0, 15, 16, 23, 24, 27, 28, 31, 40}.issubset(allowed6))
        self.assertTrue({17, 22, 25, 26, 29, 30, 33, 34, 37, 38}.isdisjoint(allowed6))
        allowed7 = set(rm_total_counts(7, 46))
        self.assertTrue({31, 32, 35, 36, 39, 40, 43, 44}.issubset(allowed7))
        self.assertTrue({33, 34, 37, 38, 41, 42, 45, 46}.isdisjoint(allowed7))
        allowed8 = set(rm_total_counts(8, 46))
        self.assertTrue({15, 16, 23, 24, 27, 28, 31, 46}.issubset(allowed8))
        self.assertTrue({17, 22, 25, 26}.isdisjoint(allowed8))

    def test_rank_one_forbidden_gap(self):
        allowed = set(rm_linear_slice_counts(7, 20))
        self.assertTrue({0, 7, 8, 11, 12}.issubset(allowed))
        self.assertTrue({1, 2, 3, 4, 5, 6, 9, 10}.isdisjoint(allowed))

    def test_rank_two_forbidden_pair(self):
        allowed = set(rm_pair_slice_counts(7, 12))
        self.assertTrue({0, 3, 4, 7, 8, 11, 12}.issubset(allowed))
        self.assertTrue({1, 2}.isdisjoint(allowed))

    def test_small_factory_with_both_pruning_levels(self):
        """With phase-support restriction and both RM pruning levels active,
        the ('S',4) geometry must still reach the optimal 15-to-1 (n=15, d=3)
        -- regression that the pruning is not over-tight."""
        result = solve(
            1, [('S', 4)], 'T', time_s=10,
            phase_support_only=True, rm_pruning=2,
        )
        self.assertEqual(result['status'], 'OPTIMAL')
        self.assertEqual(result['n'], 15)
        cols = columns_of(result['geometry'], result['assignment'])
        data_ok, distance = verify(1, result['N'], cols, 'T')
        self.assertTrue(data_ok)
        self.assertEqual(distance, 3)


if __name__ == '__main__':
    unittest.main()
