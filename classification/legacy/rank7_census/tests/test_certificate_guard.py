"""Which census files may become the published frontier, and which may not.

`_certificate_problems` is the only thing standing between a local search run and
the shipped catalogue, and every case below once got through it:

  * `--dedup gl`, which keeps one representative per GL(k,2) orbit -- coarser
    than this catalogue's S_k key, so distinct S_k classes never reach the file.
    This is not hypothetical: it is how the frontier came to list 10 classes
    where the S_k count is 21.
  * `geometries_expected: null`, which used to skip the geometry-count check
    entirely -- the one check that catches a restricted run whose other fields
    were edited to look unrestricted.
  * a sweep wider than the window, whose extra rows are not this table's
    subject.

The count is recomputed here from the bundled orbit table rather than read from
the file, which is why forging the field does not help.  The table itself is
identified by SHA-256 rather than by path, so a certificate stays valid when it
is carried from the cluster that spent the core-hours to the checkout that reads
it -- and says WHICH table it swept, which a path never did.
"""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parents[3]))

import build_catalog as B                                    # noqa: E402
from rank7 import (DEFAULT_DATA, WINDOW_NMAX, count_parents,  # noqa: E402
                   data_digest)

GEOMETRIES = count_parents()


def certificate(**overrides):
    """A file shaped like the documented full census, with fields overridden.

    Hand-built, so it can fall behind what `rank7.py` actually writes; the
    root-level `tests/` sweep works from a real run for exactly that reason.
    `test_the_documented_full_census_shape_is_accepted` is what catches the drift
    -- if a newly required field is missing here, that test fails first.
    """
    blob = {
        "scope": "the whole window",
        "mode": "all",
        "dedup": "symmetric",
        "kmax": B.REQUIRED_KMAX,
        "restrictions": {"mode": "all", "nmax": WINDOW_NMAX,
                         "kmax": B.REQUIRED_KMAX, "class_indices": None,
                         "origins": None, "max_parents": None},
        "covers_full_window": True,
        "geometries_expected": GEOMETRIES,
        "processed_parents": GEOMETRIES,
        "data_name": DEFAULT_DATA.name,
        "data_sha256": data_digest(DEFAULT_DATA),
        "data_integrity": {"valid": True},
        "complete": True,
        "untruncated": True,
        "stopped_by_max_parents": False,
        "incomplete_reasons": [],
        "factories": [],
    }
    blob.update(overrides)
    return blob


class TestCertificateGuard(unittest.TestCase):

    def test_the_documented_full_census_shape_is_accepted(self):
        """Or every rejection below would prove nothing."""
        self.assertEqual(B._certificate_problems(certificate()), [])

    def test_a_gl_deduped_run_is_refused(self):
        problems = B._certificate_problems(certificate(dedup="gl"))
        self.assertTrue(any("dedup" in p for p in problems), problems)

    def test_a_run_with_no_dedup_field_is_refused(self):
        problems = B._certificate_problems(certificate(dedup=None))
        self.assertTrue(any("dedup" in p for p in problems), problems)

    def test_a_missing_geometry_count_is_refused(self):
        problems = B._certificate_problems(certificate(geometries_expected=None))
        self.assertTrue(any("geometries_expected" in p for p in problems), problems)

    def test_a_forged_geometry_count_is_refused(self):
        """The count is recomputed, so agreeing with itself is not enough."""
        problems = B._certificate_problems(
            certificate(geometries_expected=7, processed_parents=7))
        self.assertTrue(any(str(GEOMETRIES) in p for p in problems), problems)

    def test_an_unfinished_sweep_is_refused(self):
        problems = B._certificate_problems(
            certificate(processed_parents=GEOMETRIES - 1))
        self.assertTrue(any("visited" in p for p in problems), problems)

    def test_a_restricted_run_is_refused(self):
        problems = B._certificate_problems(certificate(
            covers_full_window=False,
            restrictions={"mode": "all", "nmax": WINDOW_NMAX, "kmax": 4,
                          "class_indices": [306], "origins": None,
                          "max_parents": None}))
        self.assertTrue(any("class_indices" in p for p in problems), problems)

    def test_a_narrow_width_is_refused(self):
        problems = B._certificate_problems(
            certificate(kmax=B.REQUIRED_KMAX - 1))
        self.assertTrue(any("kmax" in p for p in problems), problems)

    def test_a_representative_sweep_is_refused(self):
        problems = B._certificate_problems(certificate(mode="reps"))
        self.assertTrue(any("'all'" in p for p in problems), problems)

    def test_a_restricted_sweep_declaring_itself_complete_is_refused(self):
        """The boolean is recomputed from the restrictions, not believed.

        Each of these files says `covers_full_window: true` and carries a
        consistent geometry count, while its own `restrictions` record a sweep
        that cannot possibly have covered the window.  All five were accepted.
        """
        for field, value in (("class_indices", [306]), ("origins", [0]),
                             ("max_parents", 1), ("mode", "reps"),
                             ("nmax", WINDOW_NMAX - 1)):
            blob = certificate()
            blob["restrictions"][field] = value
            with self.subTest(restriction=f"{field}={value!r}"):
                problems = B._certificate_problems(blob)
                self.assertTrue(any(field in p for p in problems), problems)

    def test_contradicting_top_level_and_restriction_fields_is_refused(self):
        """A file with two stories is not a certificate for the better one."""
        for field, value in (("mode", "reps"), ("kmax", 1), ("nmax", 12)):
            blob = certificate()
            blob["restrictions"][field] = value
            with self.subTest(field=field):
                problems = B._certificate_problems(blob)
                self.assertTrue(problems, f"{field} mismatch accepted")

    def test_a_self_contradicting_boolean_is_refused(self):
        """Unrestricted restrictions with covers_full_window=false: which is it?"""
        problems = B._certificate_problems(certificate(covers_full_window=False))
        self.assertTrue(any("contradicts itself" in p for p in problems), problems)

    def test_malformed_fields_are_rejected_not_crashed(self):
        """Every field is untrusted input; the validator must not raise."""
        for blob in (certificate(data_sha256=7),
                     certificate(data_sha256={}),
                     certificate(data_sha256="not hex" * 8),
                     certificate(kmax="four"),
                     certificate(restrictions=None),
                     certificate(restrictions=[1, 2, 3]),
                     []):
            with self.subTest(blob=str(blob)[:40]):
                problems = B._certificate_problems(blob)   # must not raise
                self.assertTrue(problems)

    def test_a_certificate_from_another_machine_is_accepted(self):
        """Nothing in the file may name a location: that is the portable case.

        The census runs on a cluster and is read in a checkout elsewhere, so a
        recorded absolute path would resolve to nothing here.  The digest is what
        travels; no path field is consulted at all.
        """
        elsewhere = certificate(
            data_name="B-0-3-7.dat",
            data="/scratch/somebody-elses-cluster/rank7/data/B-0-3-7.dat")
        self.assertEqual(B._certificate_problems(elsewhere), [])

    def test_a_certificate_with_no_digest_is_refused(self):
        problems = B._certificate_problems(certificate(data_sha256=None))
        self.assertTrue(any("data_sha256" in p for p in problems), problems)

    def test_a_different_orbit_table_is_refused(self):
        problems = B._certificate_problems(certificate(data_sha256="00" * 32))
        self.assertTrue(any("not the bundled orbit table" in p
                            for p in problems), problems)

    def test_an_unverified_orbit_table_is_refused(self):
        problems = B._certificate_problems(
            certificate(data_integrity={"valid": False}))
        self.assertTrue(any("data_integrity" in p for p in problems), problems)

    def test_a_narrower_window_is_refused(self):
        problems = B._certificate_problems(certificate(
            restrictions={"mode": "all", "nmax": WINDOW_NMAX - 1, "kmax": 4,
                          "class_indices": None, "origins": None,
                          "max_parents": None}))
        self.assertTrue(any("nmax" in p for p in problems), problems)


if __name__ == "__main__":
    unittest.main()
