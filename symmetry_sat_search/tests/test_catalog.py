"""Catalogue-level checks for the search directory.

`build_catalog.py` verifies every circuit as it builds; `verify_catalog.py`
re-verifies the shipped file along an independent path; `rebuild_from_groups.py`
regenerates every factory from its symmetry group.  These tests assert the
headline numbers those three produce, so a silent change shows up here.
"""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import verify_catalog as V                             # noqa: E402
import rebuild_from_groups as R                        # noqa: E402

CATALOG = HERE.parent / "catalog" / "factories.json"
GROUPS = HERE.parent / "catalog" / "symmetry_groups.json"


@unittest.skipUnless(CATALOG.exists(), "run build_catalog.py first")
class TestFactoryCatalogue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = json.loads(CATALOG.read_text())["factories"]

    def test_expected_size(self):
        self.assertEqual(len(self.rows), 57)

    def test_every_row_reverifies_independently(self):
        """The full check: shape, check parities, gate, distance, metrics."""
        for r in self.rows:
            with self.subTest(label=r["label"], params=(r["n"], r["k"], r["d"])):
                fails, _shown, _gate = V.verify_row(r)
                self.assertEqual(fails, [])

    def test_columns_are_distinct_and_nonempty(self):
        for r in self.rows:
            cols = [tuple(sorted(c)) for c in r["columns"]]
            with self.subTest(label=r["label"]):
                self.assertEqual(len(set(cols)), len(cols))
                self.assertTrue(all(cols))

    def test_records_the_distance_convention(self):
        """d >= 5 rows are lower bounds: the enumerator is exact only to
        weight 4.  Assert the catalogue never claims an exact 5."""
        for r in self.rows:
            if r["d"] >= 5:
                masks = [sum(1 << q for q in c) for c in r["columns"]]
                from evaluator import _distance
                self.assertEqual(_distance(masks, r["k"], 4), 5,
                                 "a d>=5 row must have no fault of weight <= 4")


@unittest.skipUnless(GROUPS.exists(), "run symmetry_groups.py first")
class TestSymmetryGroups(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blob = json.loads(GROUPS.read_text())
        cls.catalog = json.loads(CATALOG.read_text())["factories"]

    def test_every_factory_regenerates_from_its_group(self):
        """The property that makes the stored groups meaningful: closing the
        orbit representatives under the generators returns the factory."""
        self.assertTrue(self.blob["all_regenerate"])
        for record, catalogued in zip(self.blob["factories"], self.catalog):
            with self.subTest(label=record["label"]):
                fails, _shown, _order, _orbits = R.check(record, catalogued)
                self.assertEqual(fails, [])

    def test_known_group_orders(self):
        """Spot-check against the design geometries the search used: the C7
        slot ansatz really does leave a group of order 7 x 6 = 42 acting, and
        the S4 single block leaves 4! = 24."""
        by_label = {r["label"]: r for r in self.blob["factories"]}
        self.assertEqual(by_label["T on C7"]["group"]["order"], 42)
        self.assertEqual(by_label["T on S4"]["group"]["order"], 24)

    def test_generators_are_permutations_fixing_the_output_block(self):
        for record in self.blob["factories"]:
            k, N = record["params"][1], record["N"]
            for g in record["group"]["generators"]:
                with self.subTest(label=record["label"]):
                    self.assertEqual(sorted(g), list(range(N)))
                    self.assertEqual({g[q] for q in range(k)}, set(range(k)))

    def test_the_shipped_groups_are_all_complete(self):
        """`order` is published as |Aut(F)|, so a capped enumeration is a lie."""
        self.assertTrue(self.blob["all_groups_complete"])
        for record in self.blob["factories"]:
            with self.subTest(label=record["label"]):
                self.assertTrue(record["group"]["complete"])
                self.assertLess(record["group"]["order"], self.blob["group_cap"])

    def test_a_capped_enumeration_fails_the_build(self):
        """Regenerating the circuit is not evidence that the group is the group.

        A PROPER SUBGROUP can regenerate the columns perfectly well, so
        `regenerates_factory` cannot catch a truncated enumeration -- and it used
        to be the only condition that could fail this build.  Forcing the cap to
        2 gives exactly that state: every row still regenerates, every group is a
        subgroup, and the build must refuse it.
        """
        import symmetry_groups as SG
        with tempfile.TemporaryDirectory() as tmp:
            out = str(Path(tmp) / "symmetry_groups.json")
            with contextlib.redirect_stdout(io.StringIO()):
                code = SG.build(out_path=out, cap=2)
            # a failed run writes the partial result beside the catalogue, never
            # over it -- see test_a_capped_run_does_not_replace_the_catalogue
            written = json.loads(Path(out + ".incomplete.json").read_text())
        self.assertEqual(code, 1, "a capped enumeration must not exit 0")
        self.assertFalse(written["all_groups_complete"])
        self.assertTrue(written["all_regenerate"],
                        "the point of the test: regeneration still succeeds")

    def test_a_capped_run_does_not_replace_the_catalogue(self):
        """Exiting nonzero is not enough if the bad file is already on disk.

        The write used to happen before the check, so a capped run left an
        incomplete symmetry_groups.json where every downstream reader would find
        it, and only a caller who inspected the exit code was protected.
        """
        import symmetry_groups as SG
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "symmetry_groups.json"
            out.write_text('{"sentinel": true}', encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                code = SG.build(out_path=str(out), cap=1)
            self.assertEqual(code, 1)
            self.assertEqual(json.loads(out.read_text()), {"sentinel": True},
                             "the published file was overwritten by a capped run")
            sidecar = Path(str(out) + ".incomplete.json")
            self.assertTrue(sidecar.exists(),
                            "the partial result should still be inspectable")
            self.assertFalse(json.loads(sidecar.read_text())
                             ["all_groups_complete"])

    def test_rebuilding_from_identity_subgroups_is_rejected(self):
        """The `cap=1` case: every group truncated to the identity.

        Each orbit is then a singleton, so closing the representatives trivially
        returns the column set and all 57 rows "rebuild" -- which is exactly why
        regeneration cannot be the only check.  rebuild_from_groups.py must
        refuse the file on its `complete` flags, before rebuilding anything.
        """
        import symmetry_groups as SG
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "symmetry_groups.json"
            with contextlib.redirect_stdout(io.StringIO()):
                SG.build(out_path=str(out), cap=1)
            capped = json.loads(Path(str(out) + ".incomplete.json").read_text())
        self.assertTrue(capped["all_regenerate"],
                        "the premise: identity subgroups still regenerate")
        self.assertEqual([r["group"]["order"] for r in capped["factories"]],
                         [1] * len(capped["factories"]))
        with contextlib.redirect_stdout(io.StringIO()) as printed:
            code = R.main(groups=capped)
        self.assertEqual(code, 1, "a truncated group file must be refused")
        self.assertIn("truncated", printed.getvalue())

    def test_compression_is_reported_honestly(self):
        for record in self.blob["factories"]:
            n = record["params"][0]
            total = sum(o["orbit_size"] for o in record["column_orbits"])
            with self.subTest(label=record["label"]):
                self.assertEqual(total, n)
                self.assertEqual(record["n_orbits"], len(record["column_orbits"]))


if __name__ == "__main__":
    unittest.main()
