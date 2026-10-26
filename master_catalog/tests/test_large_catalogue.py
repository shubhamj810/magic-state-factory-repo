"""The large file: circuits given by a rule (`constructions.py`) and the layer
in `catalogfile.py` that stores them without their columns.

* **The rule** against its definition, on small cases by brute force over all
  subsets, and its shape checks;
* **the encoding** -- powers one digit per column, columns dropped and rebuilt
  -- round-tripped exactly, on synthetic rows and on every two-group row of
  the main file, and refused wherever it would lose information;
* **the files**: `write_all` then `load_all` gives back the same payload, the
  main file and the page are what they were, `write` refuses a large row,
  and `load_all` refuses a main-file row with a construction.
"""
from __future__ import annotations

import copy
import itertools
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE.parent
sys.path.insert(0, str(CATALOGUE))

import catalogfile as CF                                          # noqa: E402
import constructions as K                                         # noqa: E402
import merge_results as MR                                        # noqa: E402
import verify_catalog as VC                                       # noqa: E402

UNIFIED = "borrowed_identities/circuits/unified_l3.json"


def two_group_rows(payload):
    """``(row, construction)`` for the main file's large-sweep rows."""
    out = []
    for row in payload["factories"]:
        source = row["sources"][0]
        if source["file"] != UNIFIED or not source["label"].startswith("ls-"):
            continue
        match = re.search(r"s_total=(\d+),s_O=(\d+)", source["provenance"])
        out.append((row, {"family": "two-group", "k": row["k"], "N": row["N"],
                          "s_total": int(match.group(1)),
                          "s_O": int(match.group(2))}))
    return out


def as_large(row, construction):
    """``row`` as a materialised large row: the two fields after columns."""
    out = {}
    for key, value in row.items():
        out[key] = value
        if key == "columns":
            out["construction"] = construction
            out["columns_sha256"] = K.digest(value)
    return out


class TestRule(unittest.TestCase):
    def test_two_group_against_its_definition(self):
        """Every subset of the wires, by brute force, for small k, N, a, b."""
        for k, N, a, b in itertools.product((1, 2, 3), (4, 5, 6), (1, 2, 3),
                                            (1, 2)):
            if not k < N:
                continue
            want = []
            for size in range(1, N + 1):
                for S in itertools.combinations(range(N), size):
                    A = [q for q in S if q < k]
                    B = [q for q in S if q >= k]
                    if B and (not A or (len(A) - 1) % b == 0) \
                            and (len(S) - 1) % a == 0:
                        want.append(list(S))
            with self.subTest(k=k, N=N, s_total=a, s_O=b):
                self.assertEqual(K.columns({"family": "two-group", "k": k,
                                            "N": N, "s_total": a, "s_O": b}),
                                 sorted(want))

    def test_a_malformed_construction_is_named_not_expanded(self):
        good = {"family": "two-group", "k": 2, "N": 6, "s_total": 1, "s_O": 1}
        self.assertEqual(K.problems(good), [])
        for bad in ([1], {"family": "unknown"}, {**good, "extra": 1},
                    {k: v for k, v in good.items() if k != "s_O"},
                    {**good, "k": 0}, {**good, "N": 2, "k": 2},
                    {**good, "N": K.MAX_WIRES + 1}, {**good, "s_total": True},
                    {**good, "s_O": 1.0}):
            with self.subTest(bad=bad):
                self.assertTrue(K.problems(bad))
                with self.assertRaises(ValueError):
                    K.columns(bad)

    def test_the_digest_is_of_compact_json(self):
        self.assertEqual(K.canonical_text([[0, 1], [2]]), "[[0,1],[2]]")
        self.assertEqual(len(K.digest([[0]])), 64)


class TestEncoding(unittest.TestCase):
    def test_powers_round_trip(self):
        for powers, n in (([], 4), ([[0, 7], [3, 3]], 4), (None, 5),
                          ([[c, 7] for c in range(6)], 6)):
            with self.subTest(powers=powers):
                text = CF.encode_powers(powers, n)
                self.assertEqual(CF.decode_powers(text, n), powers)
        self.assertEqual(CF.encode_powers([[1, 5]], 3), "151")

    def test_powers_that_cannot_be_one_digit_each_are_refused(self):
        for powers in ([[1, 7], [0, 7]], [[0, 7], [0, 3]], [[0, 1]], [[0, 2]],
                       [[3, 7]], [[-1, 7]], [[0, 3.0]], [[True, 3]],
                       [[1.0, 3]], [[0, "3"]]):
            with self.subTest(powers=powers):
                with self.assertRaises(ValueError):
                    CF.encode_powers(powers, 3)
        for text in ("12", "1234", "17", 7, ["7"]):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    CF.decode_powers(text, 3 if text != "17" else 3)

    def test_every_two_group_row_of_the_main_file_round_trips(self):
        rows = two_group_rows(CF.load())
        self.assertGreater(len(rows), 200)
        for row, construction in rows:
            with self.subTest(label=row["catalog_label"]):
                self.assertEqual(row["columns"], K.columns(construction))
                large = as_large(row, construction)
                stored = CF.dematerialise(large, "test")
                self.assertNotIn("columns", stored)
                back = CF.materialise(stored, "test")
                self.assertEqual(back, large)
                self.assertEqual(list(back), list(large))

    def test_a_row_that_would_lose_information_is_not_written(self):
        row, construction = two_group_rows(CF.load())[0]
        large = as_large(row, construction)
        for name, change in (
                ("columns", lambda r: r["columns"].reverse()),
                ("digest", lambda r: r.update(columns_sha256="0" * 64)),
                ("rule", lambda r: r["construction"].update(
                    s_total=r["construction"]["s_total"] + 1))):
            broken = copy.deepcopy(large)
            change(broken)
            with self.subTest(change=name):
                with self.assertRaises(ValueError):
                    CF.dematerialise(broken, "test")

    def test_the_storage_fields_must_follow_columns(self):
        row, construction = two_group_rows(CF.load())[0]
        large = as_large(row, construction)
        moved = {key: value for key, value in large.items()
                 if key not in CF.STORAGE_FIELDS}
        moved.update({key: large[key] for key in CF.STORAGE_FIELDS})
        with self.assertRaises(ValueError):
            CF.dematerialise(moved, "test")
        other = copy.deepcopy(large)
        other["k"] += 1
        with self.assertRaises(ValueError):
            CF.dematerialise(other, "test")

    def test_an_undecodable_stored_row_is_refused(self):
        row, construction = two_group_rows(CF.load())[0]
        stored = CF.dematerialise(as_large(row, construction), "test")
        for name, change in (
                ("no rule", lambda r: r.pop("construction")),
                ("bad rule", lambda r: r["construction"].pop("s_O")),
                ("columns", lambda r: r.update(columns=[[0]])),
                ("powers", lambda r: r.update(rotation_powers="9"))):
            broken = copy.deepcopy(stored)
            change(broken)
            with self.subTest(change=name):
                with self.assertRaises(ValueError):
                    CF.materialise(broken, "test")


class TestVerifier(unittest.TestCase):
    """`verify_catalog.construction_problems`, through `verify_row`."""

    @classmethod
    def setUpClass(cls):
        row, construction = two_group_rows(CF.load())[0]
        cls.large = as_large(row, construction)

    def kinds(self, row):
        _facts, problems = VC.verify_row(row)
        return [kind for kind, _detail in problems]

    def test_a_large_row_verifies(self):
        self.assertEqual(self.kinds(copy.deepcopy(self.large)), [])

    def test_each_way_a_rule_can_disagree_is_caught(self):
        def other_rule(row):
            rule = row["construction"]
            rule["s_total"] += 1
        for name, change in (
                ("digest", lambda r: r.update(columns_sha256="0" * 64)),
                ("no digest", lambda r: r.pop("columns_sha256")),
                ("no rule", lambda r: r.pop("construction")),
                ("k", lambda r: r["construction"].update(
                    k=r["construction"]["k"] + 1)),
                ("rule", other_rule),
                ("shape", lambda r: r["construction"].update(family="other")),
                ("type", lambda r: r.update(construction=[1]))):
            row = copy.deepcopy(self.large)
            change(row)
            with self.subTest(change=name):
                kinds = self.kinds(row)
                self.assertTrue({"construction", "field-type"} & set(kinds),
                                kinds)

    def test_a_main_row_has_nothing_to_say(self):
        row = {key: value for key, value in self.large.items()
               if key not in ("construction", "columns_sha256")}
        self.assertEqual(VC.construction_problems(row), [])

    def test_the_large_files_own_header_is_checked(self):
        directory = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, directory)
        path = directory / "master_catalog_large.json"
        self.assertEqual(VC.large_file_problems(path), [])
        stored = CF.dematerialise(copy.deepcopy(self.large), "test")
        good = {**CF.large_header(1), "factories": [stored]}
        path.write_text(CF.serialise(good))
        self.assertEqual(VC.large_file_problems(path), [])
        for name, change in (("count", lambda b: b.update(n_classes=2)),
                             ("about", lambda b: b.update(about="x")),
                             ("extra", lambda b: b.update(extra=1)),
                             ("families", lambda b: b.update(families={}))):
            blob = copy.deepcopy(good)
            change(blob)
            path.write_text(CF.serialise(blob))
            with self.subTest(change=name):
                self.assertTrue(VC.large_file_problems(path))
        path.write_text("")
        self.assertTrue(VC.large_file_problems(path))

    def test_a_stored_row_out_of_order_is_caught(self):
        """A large file that decodes but is not what the writer writes would
        pass loading and then be refused by the next tool that writes it."""
        directory = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, directory)
        path = directory / "master_catalog_large.json"
        stored = CF.dematerialise(copy.deepcopy(self.large), "test")
        moved = {key: value for key, value in stored.items()
                 if key != "columns_sha256"}
        moved["columns_sha256"] = stored["columns_sha256"]
        path.write_text(CF.serialise({**CF.large_header(1), "factories": [moved]}))
        self.assertTrue(VC.large_file_problems(path))

    def test_a_baseline_beside_the_catalogue_does_not_hide_a_large_row(self):
        """``--baseline`` must not read the large file under test as the
        baseline's: every large row would then count as unchanged."""
        import contextlib
        import io
        directory = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, directory)
        payload = CF.load()
        payload["factories"] = payload["factories"][:3]
        payload["n_classes"] = 3
        payload["factories"].append(copy.deepcopy(self.large))
        main = directory / "master_catalog.json"
        large = directory / "master_catalog_large.json"
        CF.write_all(payload, main, large, directory / "MASTER_CATALOG.md")
        base = directory / "base.json"
        base.write_text(main.read_text())
        blob = json.loads(large.read_text())
        blob["factories"][0]["columns_sha256"] = "0" * 64
        large.write_text(CF.serialise(blob))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = VC.main(["--catalog", str(main), "--baseline", str(base),
                            "--quiet"])
        self.assertEqual(code, 1, out.getvalue())
        self.assertIn("1 of 4 rows differ", out.getvalue())

    def test_one_file_at_a_time(self):
        """``--file main`` and ``--file large`` verify every row of one file,
        and the checks across both files; an empty scope is refused."""
        import contextlib
        import io
        directory = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, directory)
        payload = CF.load()
        payload["factories"] = payload["factories"][:3]
        payload["n_classes"] = 3
        payload["factories"].append(copy.deepcopy(self.large))
        main = directory / "master_catalog.json"
        CF.write_all(payload, main, directory / "master_catalog_large.json",
                     directory / "MASTER_CATALOG.md")
        for scope, count in (("main", 3), ("large", 1)):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = VC.main(["--catalog", str(main), "--file", scope, "--quiet"])
            with self.subTest(scope=scope):
                self.assertEqual(code, 0, out.getvalue())
                self.assertIn(f"{count} of 4 rows are in the {scope} file", out.getvalue())
                self.assertIn(f"PASS: {count} rows", out.getvalue())
                self.assertIn("no two rows are the same GL(k,2) class", out.getvalue())
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stdout(io.StringIO()):
                VC.main(["--catalog", str(main), "--file", "main", "--rows", "1"])
        CF.write_all({**payload, "factories": payload["factories"][:3]}, main,
                     directory / "master_catalog_large.json",
                     directory / "MASTER_CATALOG.md")
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stdout(io.StringIO()):
                VC.main(["--catalog", str(main), "--file", "large"])

    def test_the_header_counts_the_main_file(self):
        payload = CF.load()
        payload["factories"] = payload["factories"] + [self.large]
        self.assertEqual(VC.header_problems(payload), [])
        payload["n_classes"] += 1
        self.assertTrue(VC.header_problems(payload))


class TestMerge(unittest.TestCase):
    """`merge_results` with a record that carries a construction."""

    @classmethod
    def setUpClass(cls):
        payload = CF.load()
        rows = two_group_rows(payload)
        # the smallest, to keep the merge quick
        cls.row, cls.rule = min(rows, key=lambda pair: pair[0]["n"])

    def record(self, **extra):
        return {"k": self.row["k"], "N": self.row["N"],
                "construction": dict(self.rule), "regime": self.row["regimes"][0],
                "discovery": "pre-existing", "citations": ["singh2026borrowed"],
                "label": "test", **extra}

    def test_a_held_class_is_a_duplicate(self):
        payload = CF.load_all()
        verdicts = MR.merge(payload, [self.record()], "test")
        self.assertEqual(verdicts[0][1], "duplicate")

    def test_a_new_class_goes_to_the_large_file(self):
        directory = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, directory)
        paths = (directory / "master_catalog.json",
                 directory / "master_catalog_large.json",
                 directory / "MASTER_CATALOG.md")
        payload = CF.load_all()
        payload["factories"] = [r for r in payload["factories"]
                                if r["catalog_label"] != self.row["catalog_label"]]
        payload["n_classes"] -= 1
        verdicts = MR.merge(payload, [self.record()], "test")
        self.assertEqual(verdicts[0][1], "accepted", verdicts[0][3])
        row = verdicts[0][2]
        self.assertEqual(row["columns"], K.columns(self.rule))
        self.assertEqual(row["construction"], self.rule)
        self.assertEqual(row["columns_sha256"], K.digest(row["columns"]))
        self.assertEqual(list(row)[list(row).index("columns") + 1:][:2],
                         ["construction", "columns_sha256"])
        # the same circuit, the same derived fields, as the stored row had
        for name in ("gate", "d", "d_witness", "A_d", "clifford_correction",
                     "rotation_powers", "t_count", "N", "n"):
            self.assertEqual(row[name], self.row[name], name)
        self.assertEqual(VC.header_problems(payload), [])
        CF.write_all(payload, *paths)
        main = json.loads(paths[0].read_text())
        self.assertNotIn(row["catalog_label"],
                         {r["catalog_label"] for r in main["factories"]})
        stored = json.loads(paths[1].read_text())["factories"]
        # the large file holds the new row with whatever rows it held already
        self.assertEqual([r["catalog_label"] for r in stored],
                         [r["catalog_label"] for r in payload["factories"]
                          if CF.is_large(r)])
        self.assertIn(row["catalog_label"], [r["catalog_label"] for r in stored])
        back = CF.load_all(paths[0], paths[1])
        # in memory the merge sorts all rows by class; on disk each file keeps
        # its rows in that order, and loading puts the main file's first
        expected = {**payload, "factories": CF.main_rows(payload["factories"])
                    + [r for r in payload["factories"] if CF.is_large(r)]}
        self.assertTrue(back == expected, "the payload does not round-trip")
        self.assertEqual(VC.verify_row(back["factories"][-1])[1], [])

    def test_an_improvement_puts_the_storage_fields_after_columns(self):
        incumbent = {key: value for key, value in self.row.items()}
        candidate = as_large(self.row, self.rule)
        MR.improve(incumbent, {**candidate, "citations": []},
                   CF.load()["regimes"])
        keys = list(incumbent)
        at = keys.index("columns")
        self.assertEqual(keys[at + 1:at + 3], list(CF.STORAGE_FIELDS))
        self.assertEqual(CF.materialise(CF.dematerialise(incumbent, "t"), "t"),
                         incumbent)
        # and a candidate with columns takes the class back to the main file
        MR.improve(incumbent, {**self.row, "citations": []},
                   CF.load()["regimes"])
        self.assertFalse(set(CF.STORAGE_FIELDS) & set(incumbent))

    def test_a_malformed_record_is_refused_before_expansion(self):
        for name, record in (
                ("both", self.record(columns=self.row["columns"])),
                ("neither", {k: v for k, v in self.record().items()
                             if k != "construction"}),
                ("k", self.record(k=self.row["k"] + 1)),
                ("shape", self.record(construction={"family": "two-group"})),
                ("huge", self.record(construction={**self.rule, "N": 99}))):
            with self.subTest(case=name):
                problems = MR.record_problems(record)
                self.assertTrue(any(kind == "schema" for kind, _d in problems),
                                problems)


class TestFiles(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir)
        self.paths = (self.dir / "master_catalog.json",
                      self.dir / "master_catalog_large.json",
                      self.dir / "MASTER_CATALOG.md")

    def payload_with_large_rows(self, count=3):
        """The shipped payload, with ``count`` two-group rows moved to the
        large file -- as a large row, and out of the main file."""
        payload = CF.load()
        moved = two_group_rows(payload)[:count]
        labels = {row["catalog_label"] for row, _c in moved}
        payload["factories"] = [row for row in payload["factories"]
                                if row["catalog_label"] not in labels] \
            + [as_large(row, c) for row, c in moved]
        # the main header counts the main file's rows
        payload["n_classes"] = len(CF.main_rows(payload["factories"]))
        return payload, labels

    def assertSamePayload(self, left, right):
        """Equality without unittest's diff, which on two 40 MB payloads
        takes longer than the whole suite."""
        self.assertTrue(left == right, "the payloads differ")
        self.assertEqual(list(left), list(right))

    def test_write_all_then_load_all_is_the_identity(self):
        payload, labels = self.payload_with_large_rows()
        CF.write_all(payload, *self.paths)
        back = CF.load_all(self.paths[0], self.paths[1])
        self.assertSamePayload(back, payload)
        main = json.loads(self.paths[0].read_text())
        self.assertEqual(main["n_classes"], len(main["factories"]))
        self.assertFalse(labels & {r["catalog_label"] for r in main["factories"]})
        large = json.loads(self.paths[1].read_text())
        self.assertEqual(large["n_classes"], 3)
        self.assertEqual(set(large), {"about", "families", "n_classes",
                                      "factories"})
        for stored in large["factories"]:
            self.assertNotIn("columns", stored)
            self.assertIsInstance(stored["rotation_powers"], (str, type(None)))
        # the page is the one the files give
        self.assertEqual(self.paths[2].read_text(), CF.render_markdown(back))

    def test_the_page_lists_large_rows_after_the_main_ones(self):
        payload, _labels = self.payload_with_large_rows()
        # a merge appends to the END, after rows of the large file
        payload["factories"].append(payload["factories"].pop(0))
        CF.write_all(payload, *self.paths)
        back = CF.load_all(self.paths[0], self.paths[1])
        self.assertEqual(self.paths[2].read_text(), CF.render_markdown(back))
        page = self.paths[2].read_text()
        self.assertIn("see `master_catalog_large.json`, `factories[0]`", page)
        self.assertIn("built by the two-group construction", page)

    def test_without_large_rows_no_large_file_is_written(self):
        payload = CF.load()
        CF.write_all(payload, *self.paths)
        self.assertEqual(self.paths[0].read_text(), CF.CATALOG_JSON.read_text())
        self.assertEqual(self.paths[2].read_text(), CF.render_markdown(payload))
        self.assertFalse(self.paths[1].exists())

    def test_writing_the_shipped_catalogue_reproduces_its_files(self):
        CF.write_all(CF.load_all(), *self.paths)
        for written, shipped in zip(self.paths, (CF.CATALOG_JSON,
                                                 CF.CATALOG_LARGE_JSON,
                                                 CF.CATALOG_MD)):
            with self.subTest(file=shipped.name):
                self.assertEqual(written.exists(), shipped.exists())
                if shipped.exists():
                    self.assertTrue(written.read_text() == shipped.read_text())

    def test_write_refuses_a_large_row(self):
        payload, _labels = self.payload_with_large_rows(1)
        with self.assertRaises(ValueError):
            CF.write(payload, self.paths[0], self.paths[2])
        self.assertFalse(self.paths[0].exists())

    def test_writing_the_main_file_alone_keeps_the_large_rows_on_the_page(self):
        payload, _labels = self.payload_with_large_rows()
        CF.write_all(payload, *self.paths)
        page = self.paths[2].read_text()
        main = CF.load(self.paths[0])
        CF.write(main, self.paths[0], self.paths[2])
        self.assertEqual(self.paths[2].read_text(), page)

    def test_load_all_refuses_a_construction_in_the_main_file(self):
        payload, _labels = self.payload_with_large_rows(1)
        self.paths[0].write_text(CF.serialise(
            {**payload, "factories": payload["factories"][-1:]}))
        with self.assertRaises(ValueError):
            CF.load_all(self.paths[0], self.paths[1])

    def test_the_three_paths_must_differ(self):
        payload = CF.load_all()
        with self.assertRaises(ValueError):
            CF.write_all(payload, self.paths[0], self.paths[0], self.paths[2])


if __name__ == "__main__":
    unittest.main()
