"""The bundled Gillot--Langevin orbit table is third-party input that the whole
census rests on.  If it is truncated, corrupted, or silently replaced, every
downstream "complete" claim is void -- so it is checked here structurally
(3,486 classes, degree <= 3), by content (SHA-256), and by the one property
that actually proves completeness: the orbit sizes must sum to 2^64 = |RM(3,7)|.
"""
import hashlib
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from gillot_langevin import integrity_report          # noqa: E402
from rank7 import DEFAULT_DATA, iter_parents          # noqa: E402

EXPECTED_SHA256 = ("07ead6fb7809c4f249b3a6b6e4f895b5d1"
                   "d43fbbc3606cccbe0c3bcb3fa75846")


class TestBundledData(unittest.TestCase):
    def test_file_is_present_and_unmodified(self):
        self.assertTrue(DEFAULT_DATA.exists(), f"missing {DEFAULT_DATA}")
        digest = hashlib.sha256(DEFAULT_DATA.read_bytes()).hexdigest()
        self.assertEqual(digest, EXPECTED_SHA256,
                         "B-0-3-7.dat differs from the shipped file; see "
                         "data/README.md for provenance")

    def test_orbit_sizes_sum_to_the_whole_code(self):
        """The completeness certificate for the outer enumeration.

        Every codeword of RM(3,7) lies in exactly one AGL(7,2) orbit, so the
        orbit sizes must sum to |RM(3,7)| = 2^64.  Anything less means the
        table -- or the parser -- is missing something.
        """
        report = integrity_report(DEFAULT_DATA)
        self.assertTrue(report["valid"])
        self.assertEqual(report["classes"], 3486)
        self.assertEqual(report["max_degree"], 3)
        self.assertEqual(report["orbit_size_sum"], 2 ** 64)

    def test_the_one_documented_correction_is_applied_in_memory(self):
        """Class 3485 reports a stabiliser size that would make its orbit a
        singleton; the true orbit is the 254 nonconstant affine functions.  The
        file is left untouched and the parser corrects it while checking.  Its
        weight is 64, outside the n <= 44 census, so no enumerated parent moves.
        """
        report = integrity_report(DEFAULT_DATA)
        self.assertEqual(report["corrected_class_indices"], [3485])


class TestParentEnumeration(unittest.TestCase):
    def test_relevant_orbits_are_the_expected_71(self):
        """Only nonzero orbits of weight <= 44 can be check parts in this
        window; there are 71 of them."""
        classes = {orbit.index for orbit, _origin, _pts
                   in iter_parents(DEFAULT_DATA, mode="reps", nmax=44)}
        self.assertEqual(len(classes), 71)

    def test_marked_parents_are_reduced(self):
        """Distinct nonzero syndromes: a repeat would be a weight-2 fault."""
        seen = 0
        for _orbit, _origin, points in iter_parents(DEFAULT_DATA, mode="reps",
                                                    nmax=44):
            self.assertEqual(len(set(points)), len(points))
            self.assertNotIn(0, points)
            seen += 1
            if seen >= 40:
                break
        self.assertGreater(seen, 0)


if __name__ == "__main__":
    unittest.main()
