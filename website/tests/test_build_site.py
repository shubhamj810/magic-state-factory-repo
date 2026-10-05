"""The website build: what it reads from the master catalogue, and what it writes.

Standard library only, so it runs inside `verify_repo.py`.  The browser-level
checks (does each page actually render?) are `website/verify_site.py`.
"""
from __future__ import annotations

import csv
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import build_site  # noqa: E402


class GateParsing(unittest.TestCase):
    def test_concatenated_digits_below_eleven_outputs(self):
        self.assertEqual(build_site.monomials("0+1+01", 2), [(0,), (1,), (0, 1)])
        self.assertEqual(build_site.monomials("012", 3), [(0, 1, 2)])

    def test_commas_above_ten_outputs(self):
        terms = build_site.monomials("0+8,9+10,11,12", 13)
        self.assertEqual(terms, [(0,), (8, 9), (10, 11, 12)])

    def test_a_bare_two_digit_token_is_one_wire_when_k_exceeds_ten(self):
        self.assertEqual(build_site.monomials("10", 12), [(10,)])
        self.assertEqual(build_site.monomials("10", 4), [(1, 0)])

    def test_rejects_what_it_cannot_read(self):
        for gate, k in (("0123", 4), ("CS01", 2), ("5", 3), ("00", 2)):
            with self.subTest(gate=gate):
                with self.assertRaises(ValueError):
                    build_site.monomials(gate, k)

    def test_human_spelling_round_trips(self):
        self.assertEqual(build_site.human([(0,), (0, 1), (0, 1, 2)], 3), "T0·CS01·CCZ012")
        self.assertEqual(build_site.human([(8, 9), (10,)], 11), "CS8,9·T10")


class ExtractableT(unittest.TestCase):
    def test_disjoint_terms_count(self):
        self.assertEqual(build_site.extractable_t([(0,), (1,)]), 2)
        self.assertEqual(build_site.extractable_t([(0, 1)]), 1)
        self.assertEqual(build_site.extractable_t([(0, 1, 2), (3,)]), 3)

    def test_overlapping_terms_have_no_count(self):
        self.assertIsNone(build_site.extractable_t([(0,), (0, 1)]))

    def test_exponent(self):
        self.assertAlmostEqual(build_site.exponent(15, 1, 3), 2.4649735207, places=9)
        self.assertIsNone(build_site.exponent(15, None, 3))
        self.assertIsNone(build_site.exponent(15, 1, 1))


class TheBuiltSite(unittest.TestCase):
    """Build once from the real catalogue and check what lands on disk."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name) / "site"
        cls.index = build_site.build(cls.out)
        cls.catalog = json.loads(build_site.CATALOG.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_one_factory_per_catalogue_row(self):
        rows = self.catalog["factories"]
        self.assertEqual(self.index["counts"]["factories"], len(rows))
        self.assertEqual(sorted(f["row"] for f in self.index["factories"]), list(range(len(rows))))
        ids = [f["id"] for f in self.index["factories"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_factory_file_carries_its_columns(self):
        for summary in self.index["factories"]:
            path = self.out / "data" / "factories" / f"{summary['id']}.json"
            record = json.loads(path.read_text(encoding="utf-8"))
            row = self.catalog["factories"][summary["row"]]
            self.assertEqual(record["circuit"]["columns"], row["columns"])
            self.assertEqual(record["parameters"]["n"], len(row["columns"]))

    def test_the_index_never_ships_columns(self):
        self.assertNotIn('"columns"', (self.out / "data" / "index.json").read_text())

    def test_numbers_are_copied_not_recomputed(self):
        for summary in self.index["factories"]:
            row = self.catalog["factories"][summary["row"]]
            for key in ("n", "k", "d", "N", "t_count", "poly_degree", "d_is_exact"):
                self.assertEqual(summary[key], row[key], (summary["id"], key))

    def test_every_citation_resolves(self):
        for summary in self.index["factories"]:
            for key in summary["citations"]:
                self.assertIn(key, self.index["references"])
        self.assertTrue(all(f["citations"] for f in self.index["factories"]),
                        "every catalogue row cites at least one paper")

    def test_parameter_groups_partition_the_factories(self):
        grouped = sorted(i for p in self.index["parameters"] for i in p["ids"])
        self.assertEqual(grouped, sorted(f["id"] for f in self.index["factories"]))

    def test_csv_has_one_line_per_factory(self):
        with (self.out / "data" / "factories.csv").open(encoding="utf-8") as handle:
            lines = list(csv.reader(handle))
        self.assertEqual(len(lines) - 1, len(self.index["factories"]))

    def test_pages_only_reference_files_that_exist(self):
        local = re.compile(r'(?:src|href)="([^"#?:]+\.(?:js|css|svg|html|json|csv))"')
        for page in self.out.glob("*.html"):
            for target in local.findall(page.read_text(encoding="utf-8")):
                if target.startswith("/"):
                    continue          # 404.html uses absolute Pages paths
                self.assertTrue((self.out / target).exists(), f"{page.name} -> {target}")

    def test_every_page_has_the_shared_chrome(self):
        current = {"search.html": "Search", "params.html": "Browse", "factory.html": "Browse"}
        for page in self.out.glob("*.html"):
            if page.name == "404.html":
                continue                  # standalone: served at any depth
            text = page.read_text(encoding="utf-8")
            with self.subTest(page=page.name):
                self.assertNotIn("<!--#", text)
                self.assertEqual(text.count('<header class="site">'), 1)
                self.assertEqual(text.count('<footer class="site">'), 1)
                self.assertIn('href="css/style.css"', text)
                self.assertNotIn("data-page=", text)
                marked = re.findall(r'aria-current="page">([^<]+)<', text)
                self.assertEqual(marked, [current[page.name]] if page.name in current else [])

    def test_the_footer_names_the_catalogue_commit(self):
        stamp = self.index["source"]
        if stamp.get("commit"):
            self.assertIn(stamp["commit"], (self.out / "index.html").read_text(encoding="utf-8"))

    def test_nojekyll(self):
        self.assertTrue((self.out / ".nojekyll").exists())


if __name__ == "__main__":
    unittest.main()
