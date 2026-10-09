"""`check_submission.py`: what it refuses to read, what it lets in, and where it writes.

Three edges, each tested from the command line the README documents
(`check_submission.main`, and the script itself for the exit status):

  * **the format.**  A malformed submission -- a missing contributor, an unknown
    or tool-owned field, both circuit forms in one protocol, a bad link, a
    reference key that clashes with the catalogue's -- exits 2 before anything
    is merged.
  * **the bar.**  A protocol that is not a factory is rejected (exit 1) by the
    master catalogue's own merge, and ``--write`` then writes nothing.
  * **the disk.**  Without ``--write`` nothing is written; with it, only the
    catalogue named by ``--catalog`` and the files beside it change.  No test
    here writes into ``master_catalog/``: every write goes to a temporary
    catalogue, and the runs against the real one patch the two writers to fail
    and compare the real files' bytes before and after.
"""
import contextlib
import hashlib
import io
import itertools
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
CONTRIB = HERE.parent
REPO = CONTRIB.parent
SCRIPT = CONTRIB / "check_submission.py"
EXAMPLE = CONTRIB / "examples" / "bravyi-kitaev_15-to-1.json"
TEMPLATE = CONTRIB / "TEMPLATE.json"
sys.path.insert(0, str(CONTRIB))

import check_submission as CS                                  # noqa: E402

CF, MR, VC = CS.CF, CS.MR, CS.VC
MASTER_FILES = (CF.CATALOG_JSON, CF.CATALOG_MD, VC.METRIC_CACHE)

#: The Bravyi-Kitaev generator matrix: one logical row, four stabiliser rows.
BK_ROWS = ["111111100000000", "101010101010101", "011001100110011",
           "000111100001111", "000000011111111"]
#: ... and the circuit it is: output 0, checks 1-4.
FIFTEEN_TO_ONE = [[0, 1], [0, 2], [0, 1, 2], [0, 3], [0, 1, 3], [0, 2, 3],
                  [0, 1, 2, 3], [4], [1, 4], [2, 4], [1, 2, 4], [3, 4],
                  [1, 3, 4], [2, 3, 4], [1, 2, 3, 4]]
#: One odd parity on check wires 1 and 4: not a factory.
BROKEN = [[0, 1, 4]] + FIFTEEN_TO_ONE[1:]


def subsets(wires, sizes):
    """Check-only padding: subsets of fresh check wires, every parity even."""
    return [sorted(s) for size in sizes
            for s in itertools.combinations(wires, size)]


def narrow_46():
    """``[[46,1,3]]``, gate ``T0``, on 10 wires (see master_catalog's tests)."""
    return FIFTEEN_TO_ONE + subsets([5, 6, 7, 8, 9], (1, 2, 3, 4, 5))


def wide_46():
    """The same class on 14 wires: a worse circuit for it."""
    return (FIFTEEN_TO_ONE + subsets([5, 6, 7, 8], (1, 2, 3, 4))
            + subsets([9, 10, 11, 12, 13], (1, 3, 5)))


REFERENCE = {"key": "doe2026fifteen", "short": "Doe (2026)",
             "full": "J. Doe, unpublished community contribution (2026)."}


def submission(*protocols, **overrides):
    """A well-formed submission of ``protocols`` (default: the 15-to-1)."""
    blob = {
        "contributor": {"name": "Jane Doe", "affiliation": "Nowhere University",
                        "contact": "jane@example.org"},
        "reference": dict(REFERENCE),
        "method": "by hand, from the quantum Reed-Muller code",
        "terms": "may be redistributed with the catalogue",
        "protocols": list(protocols) or [
            {"label": "BK", "generator_matrix_rows": BK_ROWS, "q": 1}],
    }
    blob.update(overrides)
    return blob


def digest(paths):
    return {path: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in paths if path.exists()}


class Case(unittest.TestCase):
    """A temporary directory holding an EMPTY catalogue with the real header."""

    @classmethod
    def setUpClass(cls):
        payload = CF.load()
        payload["factories"] = []
        payload["n_classes"] = 0
        cls.empty = payload

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir)
        self.catalog = self.dir / "master_catalog.json"
        CF.write(self.empty, self.catalog, self.dir / "MASTER_CATALOG.md")

    def write(self, blob, name="submission.json"):
        path = self.dir / name
        path.write_text(json.dumps(blob) if not isinstance(blob, str) else blob,
                        encoding="utf-8")
        return path

    def run_main(self, path, *extra, catalog=True):
        argv = [str(path), *(["--catalog", str(self.catalog)] if catalog else []),
                *extra]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = CS.main(argv)
        return code, out.getvalue()

    def temp_files(self):
        return {path.name: path.read_bytes() for path in sorted(self.dir.iterdir())
                if path.suffix in (".json", ".md") and path.name != "submission.json"}


class TestMalformedSubmissions(Case):
    """Exit 2, with the reason, and nothing merged."""

    def assertMalformed(self, blob, *phrases):
        before = self.temp_files()
        code, out = self.run_main(self.write(blob), "--write")
        self.assertEqual(code, 2, out)
        self.assertIn("MALFORMED SUBMISSION", out)
        for phrase in phrases:
            self.assertIn(phrase, out)
        self.assertEqual(self.temp_files(), before)

    def test_a_well_formed_submission_is_not_malformed(self):
        """Otherwise every test below would pass for the wrong reason."""
        self.assertEqual(CS.submission_problems(submission()), [])
        self.assertEqual(CS.submission_problems(CS.load_submission(EXAMPLE)), [])

    def test_missing_contributor(self):
        blob = submission()
        del blob["contributor"]
        self.assertMalformed(blob, "missing contributor")

    def test_missing_contributor_name(self):
        blob = submission()
        del blob["contributor"]["name"]
        self.assertMalformed(blob, "contributor is missing name")

    def test_unknown_top_level_field(self):
        self.assertMalformed(submission(licence="CC0"), "submission.licence")

    def test_unknown_protocol_field(self):
        self.assertMalformed(
            submission({"generator_matrix_rows": BK_ROWS, "q": 1, "d_Z": 3}),
            "protocols[0].d_Z is not a field")

    def test_a_field_the_tool_sets(self):
        for name, value in (("regime", "mine"), ("citations", ["x2026y"]),
                            ("discovery", "AI search"), ("provenance", "p")):
            with self.subTest(field=name):
                self.assertMalformed(
                    submission({"k": 1, "N": 5, "columns": FIFTEEN_TO_ONE,
                                name: value}),
                    f"protocols[0].{name} is set by check_submission.py")

    def test_both_circuit_forms_in_one_protocol(self):
        self.assertMalformed(
            submission({"k": 1, "N": 5, "columns": FIFTEEN_TO_ONE,
                        "generator_matrix_rows": BK_ROWS, "q": 1}),
            "mixes the two circuit forms")

    def test_no_circuit(self):
        self.assertMalformed(submission({"label": "nothing"}), "has no circuit")

    def test_a_ragged_or_non_binary_matrix(self):
        self.assertMalformed(
            submission({"generator_matrix_rows": BK_ROWS[:-1] + ["0001"],
                        "q": 1}), "different lengths")
        self.assertMalformed(
            submission({"generator_matrix_rows": ["1201"], "q": 1}),
            "strings of '0' and '1'")

    def test_q_out_of_range(self):
        self.assertMalformed(
            submission({"generator_matrix_rows": BK_ROWS, "q": 6}),
            "protocols[0].q must be an integer from 1")

    def test_an_all_zero_matrix_column(self):
        self.assertMalformed(
            submission({"generator_matrix_rows": [r + "0" for r in BK_ROWS],
                        "q": 1}), "all-zero column(s) [15]")

    def test_a_column_that_is_not_a_list_of_indices(self):
        self.assertMalformed(
            submission({"k": 1, "N": 5, "columns": [[0, "1"]]}),
            "column 0 is not a non-empty list")

    def test_bad_url(self):
        for url in ("http://doi.org/10.1103/PhysRevA.71.022316",
                    "https://doi.org/10.1103/Phys Rev",
                    "doi:10.1103/PhysRevA.71.022316"):
            with self.subTest(url=url):
                blob = submission()
                blob["reference"]["url"] = url
                self.assertMalformed(blob, "is not an https link")

    def test_bad_reference_key(self):
        blob = submission()
        blob["reference"]["key"] = "Doe 2026"
        self.assertMalformed(blob, "reference.key 'Doe 2026' must be")

    def test_reference_key_clash_with_different_content(self):
        blob = submission()
        blob["reference"] = {"key": "bravyi2005universal",
                             "short": "Bravyi and Kitaev (2005)",
                             "full": "S. Bravyi and A. Kitaev, PRA 71 (2005)."}
        self.assertMalformed(blob, "is already in the catalogue as")

    def test_the_same_work_under_another_key(self):
        entry = self.empty["references"]["bravyi2005universal"]
        blob = submission()
        blob["reference"] = {"key": "bk2005", **entry}
        self.assertMalformed(blob, "already in the catalogue under the key "
                                   "'bravyi2005universal'")

    def test_the_maintainers_reports_are_not_a_contribution_s_reference(self):
        blob = submission()
        blob["reference"] = {"key": "jain2026symmetry",
                             **MR.DEFAULT_REFERENCES["jain2026symmetry"]}
        self.assertMalformed(blob, "one of the maintainers' own reports")

    def test_text_the_rendered_catalogue_cannot_print(self):
        self.assertMalformed(submission(method="line one\nline two"),
                             "submission.method contains a line break")
        self.assertMalformed(submission(method="x" * 401),
                             "keep it to 400")

    def test_a_short_label_another_work_already_uses(self):
        reference = dict(REFERENCE, key="doe2026other",
                         short="Nezami & Haah (2022)")
        code, out = self.run_main(self.write(submission(reference=reference)),
                                  catalog=False)
        self.assertEqual(code, 2, out)
        self.assertIn("already the label", out)

    def test_angle_brackets_are_fine_in_the_method(self):
        code, out = self.run_main(self.write(submission(
            method="exhaustive search over n <= 54 and d >= 3")))
        self.assertEqual(code, 0, out)

    def test_raw_html_and_invisible_characters_are_refused(self):
        for bad in ("Doe <b>(2026)</b>", "Doe\u202e(2026)", "Doe\u200b(2026)",
                    "Doe\u2028(2026)"):
            with self.subTest(short=bad):
                reference = dict(REFERENCE, short=bad)
                code, out = self.run_main(self.write(submission(
                    reference=reference)))
                self.assertEqual(code, 2, out)

    def test_an_unreadable_catalogue_exits_2(self):
        code, out = self.run_main(self.write(submission()), "--catalog",
                                  str(self.dir / "missing.json"), catalog=False)
        self.assertEqual(code, 2, out)
        self.assertIn("CANNOT READ THE CATALOGUE", out)

    def test_not_json(self):
        self.assertMalformed("{not json", "is not valid JSON")
        self.assertMalformed("[1, 2]", "not one submission object")

    def test_the_template_is_refused_until_filled_in(self):
        code, out = self.run_main(TEMPLATE)
        self.assertEqual(code, 2, out)
        self.assertIn("still holds the template placeholder", out)

    def test_the_template_is_otherwise_well_formed(self):
        """Filled in -- placeholders replaced, optional ones deleted -- it passes."""
        blob = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        del blob["contributor"]["affiliation"], blob["contributor"]["contact"]
        del blob["reference"]["url"], blob["reference"]["date"]
        blob["contributor"]["name"] = "Jane Doe"
        blob["reference"].update(REFERENCE)
        blob["method"], blob["terms"] = "by hand", "may be redistributed"
        for protocol in blob["protocols"]:
            for name in ("label", "notes"):
                protocol.pop(name, None)
        self.assertEqual(CS.submission_problems(blob), [])

    def test_write_into_the_master_catalogue_needs_a_file_in_submissions(self):
        with mock.patch.object(CF, "write", side_effect=AssertionError), \
                mock.patch.object(VC, "persist_metric_cache",
                                  side_effect=AssertionError):
            code, out = self.run_main(EXAMPLE, "--write", catalog=False)
        self.assertEqual(code, 2, out)
        self.assertIn("community_contributions/submissions/", out)


class TestConversion(unittest.TestCase):
    """Submission protocols become `merge_results` records the tool owns."""

    def test_matrix_rows_become_columns(self):
        self.assertEqual(CS.matrix_columns(BK_ROWS), FIFTEEN_TO_ONE)

    def test_both_forms_give_the_same_circuit(self):
        records = CS.records(submission(
            {"generator_matrix_rows": BK_ROWS, "q": 1},
            {"k": 1, "N": 5, "columns": FIFTEEN_TO_ONE}), "s.json")
        circuit = [{name: r[name] for name in ("k", "N", "columns")}
                   for r in records]
        self.assertEqual(circuit[0], circuit[1])
        self.assertEqual(circuit[0], {"k": 1, "N": 5, "columns": FIFTEEN_TO_ONE})

    def test_the_tool_sets_the_provenance(self):
        record, unlabelled = CS.records(submission(
            {"generator_matrix_rows": BK_ROWS, "q": 1, "d": 3, "gate": "T0",
             "label": "BK", "notes": "a note"},
            {"k": 1, "N": 5, "columns": FIFTEEN_TO_ONE}), "s.json")
        self.assertEqual(record["regime"], "community contribution")
        self.assertEqual(record["discovery"], "pre-existing")
        self.assertEqual(record["citations"], ["doe2026fifteen"])
        self.assertEqual(record["file"], "s.json")
        self.assertEqual(record["origin"], "Jane Doe")
        self.assertEqual(record["provenance"],
                         "community contribution by Jane Doe (Nowhere "
                         "University): by hand, from the quantum Reed-Muller "
                         "code; protocol 'BK'")
        self.assertEqual((record["label"], record["notes"], record["d"],
                          record["gate"]), ("BK", "a note", 3, "T0"))
        self.assertIn("not a maximum", record["strength"])
        self.assertEqual(unlabelled["label"], "protocol 1")
        self.assertNotIn("jane@example.org", json.dumps([record, unlabelled]),
                         "the contact address is for the maintainers only")
        for rec in (record, unlabelled):
            self.assertEqual(MR.record_problems(rec), [])

    def test_the_file_is_named_relative_to_the_repository(self):
        self.assertEqual(CS.source_file(EXAMPLE),
                         "community_contributions/examples/"
                         "bravyi-kitaev_15-to-1.json")


class TestAgainstTheRealCatalogue(unittest.TestCase):
    """The shipped example: a duplicate, and nothing on disk changes."""

    def test_a_duplicate_credits_nobody_new(self):
        """A held class -- here the Bravyi-Kitaev Pareto point, credited to
        that paper alone -- gains neither a citation nor a reference entry."""
        payload = CF.load()
        text = CF.serialise(payload)
        merged, verdicts, residue, cited = CS.check(
            submission(), payload, "submission.json")
        self.assertEqual([v for _i, v, _r, _d in verdicts], ["duplicate"])
        self.assertEqual((residue, cited), ([], [False]))
        self.assertEqual(CF.serialise(merged), text)
        self.assertNotIn(REFERENCE["key"], merged["references"])

    def test_the_example_is_a_duplicate_and_writes_nothing(self):
        before = digest(MASTER_FILES)
        out = io.StringIO()
        with mock.patch.object(CF, "write", side_effect=AssertionError), \
                mock.patch.object(VC, "persist_metric_cache",
                                  side_effect=AssertionError), \
                contextlib.redirect_stdout(out):
            code = CS.main([str(EXAMPLE)])
        self.assertEqual(code, 0, out.getvalue())
        self.assertIn("duplicate  protocol 0 (15-to-1): [[15,1,3]] N=5 T0",
                      out.getvalue())
        self.assertIn("0 accepted, 0 improved, 1 duplicate, 0 rejected",
                      out.getvalue())
        self.assertIn("nothing written", out.getvalue())
        self.assertEqual(digest(MASTER_FILES), before)

    def test_the_check_leaves_the_loaded_payload_untouched(self):
        payload = CF.load()
        text = CF.serialise(payload)
        merged, verdicts, residue, cited = CS.check(
            CS.load_submission(EXAMPLE), payload, "example.json")
        self.assertEqual([v for _i, v, _r, _d in verdicts], ["duplicate"])
        self.assertEqual((residue, cited), ([], [False]))
        self.assertEqual(CF.serialise(payload), text)
        self.assertEqual(CF.serialise(merged), text)

    def test_the_script_exits_0_on_the_example(self):
        completed = subprocess.run([sys.executable, str(SCRIPT), str(EXAMPLE)],
                                   capture_output=True, text=True, check=False,
                                   cwd=REPO)
        self.assertEqual(completed.returncode, 0, completed.stdout
                         + completed.stderr)
        self.assertIn("1 duplicate", completed.stdout)


class TestAcceptedIntoAnEmptyCatalogue(Case):

    def test_check_accepts_and_writes_nothing(self):
        before = self.temp_files()
        code, out = self.run_main(self.write(submission()))
        self.assertEqual(code, 0, out)
        self.assertIn("accepted   protocol 0 (BK): [[15,1,3]] N=5 T0", out)
        self.assertIn("nothing written", out)
        self.assertEqual(self.temp_files(), before)
        self.assertFalse((self.dir / "reduced_degree_cache.json").exists())

    def test_write_merges_into_the_named_catalogue_only(self):
        master = digest(MASTER_FILES)
        path = self.write(submission())
        code, out = self.run_main(path, "--write")
        self.assertEqual(code, 0, out)
        self.assertEqual(digest(MASTER_FILES), master)
        self.assertTrue((self.dir / "reduced_degree_cache.json").exists())

        payload = CF.load(self.catalog)
        self.assertEqual(payload["n_classes"], 1)
        row, = payload["factories"]
        self.assertEqual((row["n"], row["k"], row["d"], row["N"], row["gate"]),
                         (15, 1, 3, 5, "0"))
        self.assertEqual(row["citations"], ["doe2026fifteen"])
        self.assertEqual(payload["references"]["doe2026fifteen"],
                         {"short": "Doe (2026)",
                          "full": "J. Doe, unpublished community contribution "
                                  "(2026)."})
        self.assertEqual(row["regimes"], ["community contribution"])
        self.assertEqual(list(payload["regimes"])[-1], "community contribution")
        self.assertEqual(row["strongest_claim"], CS.STRENGTH)
        self.assertEqual(row["discovery"], "pre-existing")
        source, = row["sources"]
        self.assertEqual((source["file"], source["label"], source["origin"]),
                         (str(path), "BK", "Jane Doe"))
        self.assertTrue(source["provenance"].startswith(
            "community contribution by Jane Doe"))
        # the file it wrote is one the catalogue's own verifier accepts
        self.assertEqual(VC.verify_row(row)[1], [])
        self.assertEqual(VC.provenance_problems(payload)
                         + VC.citation_problems(payload)
                         + VC.header_problems(payload), [])
        page = (self.dir / "MASTER_CATALOG.md").read_text(encoding="utf-8")
        self.assertIn("Doe (2026)", page)

        # merging the same file again is a duplicate and a byte-identical no-op
        written = self.temp_files()
        code, out = self.run_main(path, "--write")
        self.assertEqual(code, 0, out)
        self.assertIn("1 duplicate", out)
        self.assertEqual(self.temp_files(), written)

    def test_an_improvement_is_stored_but_keeps_the_class_s_credit(self):
        """A better circuit from outside is stored; the credit is not moved.

        The class keeps the citations it had.  Its discovery tag follows the
        header's glossary: a community contribution is one of the finders that
        make a class ``pre-existing`` rather than an AI discovery of this
        project, exactly as `master_catalog/tests` reads it off the sources.
        """
        payload = CF.load(self.catalog)
        verdicts = MR.merge(payload, [{"k": 1, "N": 14, "columns": wide_46(),
                                       "regime": "AI search"}], "ai.json")
        self.assertEqual([v for _i, v, _r, _d in verdicts], ["accepted"])
        CF.write(payload, self.catalog, self.dir / "MASTER_CATALOG.md")

        code, out = self.run_main(self.write(submission(
            {"k": 1, "N": 10, "columns": narrow_46()})), "--write")
        self.assertEqual(code, 0, out)
        self.assertIn("improved", out)
        row, = CF.rows(self.catalog)
        self.assertEqual(row["N"], 10)
        self.assertEqual(row["discovery"], "pre-existing")
        self.assertEqual(row["regimes"], ["AI search", "community contribution"])
        self.assertEqual(row["citations"],
                         ["wills2026classification", "jain2026symmetry"])
        self.assertNotIn("doe2026fifteen", CF.load(self.catalog)["references"])
        self.assertEqual(VC.verify_row(row)[1], [])

    def test_a_new_class_the_frontier_does_not_dominate_is_refused(self):
        """With the frontier present, an n <= 54 class no Pareto point
        dominates would contradict the length-54 classification."""
        payload = CF.load(self.catalog)
        MR.merge(payload, [{"k": 1, "N": 10, "columns": narrow_46(),
                            "regime": CS.PARETO}], "frontier.json")
        CF.write(payload, self.catalog, self.dir / "MASTER_CATALOG.md")
        before = self.temp_files()
        code, out = self.run_main(self.write(submission()), "--write")
        self.assertEqual(code, 1, out)
        self.assertIn("frontier-contradiction", out)
        self.assertEqual(self.temp_files(), before)

    def test_a_new_class_the_frontier_dominates_is_accepted(self):
        payload = CF.load(self.catalog)
        MR.merge(payload, [{"k": 1, "N": 5, "columns": FIFTEEN_TO_ONE,
                            "regime": CS.PARETO}], "frontier.json")
        CF.write(payload, self.catalog, self.dir / "MASTER_CATALOG.md")
        code, out = self.run_main(self.write(submission(
            {"k": 1, "N": 10, "columns": narrow_46()})), "--write")
        self.assertEqual(code, 0, out)
        self.assertIn("accepted", out)
        self.assertEqual(len(CF.rows(self.catalog)), 2)

    def test_a_tie_with_a_pareto_point_is_not_domination(self):
        """Same (n, N, d) and output as a Pareto point, but not that row (for
        instance a copy with spectator outputs): the frontier is not beaten,
        but it is not strictly dominated either, so it is refused."""
        payload = CF.load(self.catalog)
        MR.merge(payload, [{"k": 1, "N": 5, "columns": FIFTEEN_TO_ONE,
                            "regime": CS.PARETO}], "frontier.json")
        point, = payload["factories"]
        twin = dict(point, regimes=["community contribution"])
        problems = CS.frontier_problems(
            {"factories": [point, twin]}, [(0, "accepted", twin, None)])
        self.assertEqual([kind for kind, _d in problems],
                         ["frontier-contradiction"])

    def test_the_spectator_free_output_is_the_gate_restricted_to_a_complement(self):
        """``T0.T1.CS01`` is ``T`` on ``x0 + x1`` times a ``CZ``: one output."""
        q, output = CS.intrinsic_output(2, {frozenset({0}), frozenset({1}),
                                            frozenset({0, 1})})
        self.assertEqual(q, 1)
        self.assertEqual(output, {frozenset({0})})
        q, output = CS.intrinsic_output(2, {frozenset({0, 1})})
        self.assertEqual((q, output), (2, {frozenset({0, 1})}))

    def test_a_circuit_improving_a_pareto_point_is_refused(self):
        """It would contradict the length-54 classification: stop and look."""
        payload = CF.load(self.catalog)
        verdicts = MR.merge(payload, [{"k": 1, "N": 14, "columns": wide_46(),
                                       "regime": CS.PARETO}], "frontier.json")
        self.assertEqual([v for _i, v, _r, _d in verdicts], ["accepted"])
        CF.write(payload, self.catalog, self.dir / "MASTER_CATALOG.md")
        before = self.temp_files()
        code, out = self.run_main(self.write(submission(
            {"k": 1, "N": 10, "columns": narrow_46()})), "--write")
        self.assertEqual(code, 1, out)
        self.assertIn("pareto-improvement", out)
        self.assertIn("NOT WRITTEN", out)
        self.assertEqual(self.temp_files(), before)


class TestRejected(Case):

    def test_a_broken_protocol_is_rejected(self):
        code, out = self.run_main(self.write(submission(
            {"k": 1, "N": 5, "columns": BROKEN})))
        self.assertEqual(code, 1, out)
        self.assertIn("rejected   protocol 0:", out)
        self.assertIn("check-contamination", out)

    def test_write_writes_nothing_when_any_protocol_is_rejected(self):
        before = self.temp_files()
        code, out = self.run_main(self.write(submission(
            {"generator_matrix_rows": BK_ROWS, "q": 1},
            {"k": 1, "N": 5, "columns": BROKEN})), "--write")
        self.assertEqual(code, 1, out)
        self.assertIn("1 accepted, 0 improved, 0 duplicate, 1 rejected", out)
        self.assertIn("NOT WRITTEN", out)
        self.assertEqual(self.temp_files(), before)
        self.assertFalse((self.dir / "reduced_degree_cache.json").exists())


if __name__ == "__main__":
    unittest.main()
