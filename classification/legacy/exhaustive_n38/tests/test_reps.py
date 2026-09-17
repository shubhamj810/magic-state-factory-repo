"""The input data is the one place a silent error could enter this pipeline.

`nezami_haah_reps.py` holds hand-transcribed Kasami--Tokura / Nezami--Haah
affine class representatives.  Everything else in this directory is computed
from them, so a dropped monomial or a mistyped variable index would propagate
into the catalogue without ever raising.  These tests close that off by
checking the tables against properties they must satisfy mathematically,
independently of how they were typed in.
"""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import classify                                     # noqa: E402
import nezami_haah_reps as reps                      # noqa: E402
from marking import support_of                       # noqa: E402


class TestClassTables(unittest.TestCase):
    def test_class_counts_match_the_published_classification(self):
        """A dropped or duplicated representative changes these counts."""
        got = {w: len(reps.BY_WEIGHT[w]) for w in sorted(reps.BY_WEIGHT)}
        self.assertEqual(got, reps.EXPECTED_CLASS_COUNTS)

    def test_every_representative_has_its_advertised_weight(self):
        """The support of the class indicator must have exactly `weight` points."""
        for weight, table in reps.BY_WEIGHT.items():
            for idx, (m, terms) in enumerate(table):
                with self.subTest(weight=weight, cls=idx):
                    self.assertEqual(len(support_of(m, terms)), weight)

    def test_window_stops_at_n_38(self):
        """The exhaustive claim of this directory is n <= 38, and the code must
        refuse anything beyond it rather than answer partially."""
        self.assertEqual(max(reps.VALID_NS), 38)
        with self.assertRaises(ValueError):
            list(reps.marked_all(39))
        with self.assertRaises(ValueError):
            list(classify.marked_all(40))


class TestMarkedParents(unittest.TestCase):
    """A marked support must be a legal check part: its rows must be
    triorthogonal, i.e. every pairwise and every triple overlap is even.  This
    is the condition that makes the postselected checks deposit nothing, and it
    is a property of the marking, not something the classifier imposes later.
    """

    def _rows(self, check_tuple, r):
        """Row j = the n-bit indicator of which columns contain check qubit j."""
        n = len(check_tuple)
        rows = []
        for j in range(r):
            rows.append(sum(1 << i for i, p in enumerate(check_tuple)
                            if (p >> j) & 1))
        return rows, n

    def test_marked_supports_are_triorthogonal(self):
        for n in (15, 23, 27, 28, 29, 30, 31, 32):
            for ci, r, cs in classify.marked_all(n):
                rows, _ = self._rows(cs, r)
                with self.subTest(n=n, cls=ci):
                    for a in range(r):
                        for b in range(a + 1, r):
                            self.assertEqual((rows[a] & rows[b]).bit_count() % 2, 0)
                            for c in range(b + 1, r):
                                self.assertEqual(
                                    (rows[a] & rows[b] & rows[c]).bit_count() % 2, 0)

    def test_parent_points_are_distinct_and_nonzero(self):
        """Reduced factories have distinct nonzero syndromes; a repeat would be
        a weight-2 undetectable fault and a zero point an unchecked column."""
        for n in (15, 23, 28, 31, 35):
            for ci, r, cs in classify.marked_all(n):
                with self.subTest(n=n, cls=ci):
                    self.assertEqual(len(set(cs)), len(cs))
                    self.assertNotIn(0, cs)
                    self.assertEqual(len(cs), n)

    def test_numpy_free_generator_agrees_with_the_engine(self):
        """nezami_haah_reps.marked_all and classify.marked_all must agree --
        the first is the dependency-free reference, the second is what runs."""
        for n in reps.VALID_NS:
            with self.subTest(n=n):
                self.assertEqual(list(reps.marked_all(n)),
                                 list(classify.marked_all(n)))


if __name__ == "__main__":
    unittest.main()
