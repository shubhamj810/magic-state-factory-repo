"""`merge_results.py`: what it lets in, what it turns away, and what it rewrites.

A merge tool has two ways to ruin a catalogue -- admitting something false, and
disturbing something true -- so this file tests both edges:

  * **the bar.**  Every negative case the verifier has, submitted as a new
    result instead of a shipped row: a broken check parity, a gate label that
    contradicts the columns, a distance claim the columns disprove, a
    pseudo-output, a repeated column.  All must come back ``rejected`` with the
    reason, and none may reach the catalogue.
  * **the rewrite.**  Merging nothing must change nothing, byte for byte, and
    re-merging what is already in must be a no-op the second time.  A merge
    that reformats 9 MB hides the one row it really changed.

THE TEST CIRCUITS
-----------------
The lifecycle tests need two genuinely different circuits for ONE class -- same
``n``, same gate, different ambient width -- and there is no such pair sitting
in the catalogue to borrow, since the catalogue only ever kept the better one.
So they are built:

    the 15-to-1 (output 0, checks 1-4)  +  two blocks of check-only padding

A check-only block is a set of columns on fresh CHECK wires whose every
degree-<=3 parity is even.  It therefore deposits nothing, contaminates no
check, and cannot lower the distance -- its wires are disjoint from everything
else, so a fault in it can never cancel a syndrome elsewhere.  Two shapes of it,
both 15 columns wide:

    ``check_only_15_on_4``  all 15 non-empty subsets of four wires
    ``check_only_16_on_5``  the 16 odd-size subsets of five wires
    ``check_only_31_on_5``  all 31 non-empty subsets of five wires
    ``check_only_15_on_5``  the 15 even-size subsets of five wires -- PADDED,
                            and kept only as a fixture that must be REFUSED

The 15-to-1 plus all 31 subsets of five wires is ``[[46,1,3]]`` on ``N = 10``;
the same class on ``N = 14`` is the 15-to-1 plus a four-wire gadget plus a
five-wire one.  Merge must accept the wide one, then keep the narrow one when
it arrives.

``check_only_15_on_5`` is the cautionary one.  Its five rows XOR to zero --
every column has even size, so every column contributes 0 to that sum -- which
makes one of its five wires carry a syndrome bit the other four already
determine.  Deleting that wire turns it into ``check_only_15_on_4`` EXACTLY, so
it was never a five-wire gadget at all; it was the four-wire one wearing an
extra ambient qubit.  That is what `faultcore.redundant_checks` exists to catch,
and no 15-column check-only gadget on five wires escapes it -- an exhaustive
sweep of the 25 parity conditions over all 31 subsets returns 26 such gadgets
and every one is dependent, while the 16-column ones are all independent.
"""
import copy
import itertools
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE.parent
REPO = CATALOGUE.parent
sys.path.insert(0, str(CATALOGUE))
sys.path.insert(0, str(REPO))

import catalogfile as CF                                        # noqa: E402
import merge_results as MR                                      # noqa: E402
import verify_catalog as VC                                     # noqa: E402

#: The 15-to-1 distillation circuit: output 0, postselected checks 1-4.
FIFTEEN_TO_ONE = [[0, 1], [0, 2], [0, 1, 2], [0, 3], [0, 1, 3], [0, 2, 3],
                  [0, 1, 2, 3], [4], [1, 4], [2, 4], [1, 2, 4], [3, 4],
                  [1, 3, 4], [2, 3, 4], [1, 2, 3, 4]]


def check_only_15_on_4(wires):
    """All 15 non-empty subsets of four wires; every degree-<=3 parity even."""
    return [sorted(s) for size in (1, 2, 3, 4)
            for s in itertools.combinations(wires, size)]


def check_only_16_on_5(wires):
    """The 16 odd-size subsets of five wires; parities even, rows independent.

    Independent because the five singletons are among the columns, which puts an
    identity block in the rows -- the property `check_only_15_on_5` lacks.
    """
    return [sorted(s) for size in (1, 3, 5)
            for s in itertools.combinations(wires, size)]


def check_only_31_on_5(wires):
    """All 31 non-empty subsets of five wires; parities even, rows independent."""
    return [sorted(s) for size in (1, 2, 3, 4, 5)
            for s in itertools.combinations(wires, size)]


def check_only_15_on_5(wires):
    """The 15 even-size subsets of five wires -- PADDED; see the module docstring.

    Kept because a fixture that must be refused is worth as much as one that
    must be accepted, not because anything here may merge it.
    """
    return [sorted(s) for size in (2, 4)
            for s in itertools.combinations(wires, size)]


def narrow_46():
    """``[[46,1,3]]``, gate ``0``, on 10 wires."""
    return FIFTEEN_TO_ONE + check_only_31_on_5([5, 6, 7, 8, 9])


def wide_46():
    """The SAME class on 14 wires: four extra ambient qubits, nothing gained.

    Same 46 columns' worth of work, spread over two gadgets instead of one, so
    the two circuits differ in ``N`` alone -- which is the tie-break merge is
    supposed to minimise on.
    """
    return (FIFTEEN_TO_ONE + check_only_15_on_4([5, 6, 7, 8])
            + check_only_16_on_5([9, 10, 11, 12, 13]))


def empty_catalogue():
    """The shipped header with no rows: a catalogue to merge into from scratch."""
    payload = CF.load()
    payload["factories"] = []
    payload["n_classes"] = 0
    return payload


def kinds(problems):
    return {kind for kind, _detail in problems}


def verdicts_of(verdicts):
    return [verdict for _index, verdict, _row, _detail in verdicts]


class TestReadRecords(unittest.TestCase):
    """The four accepted layouts, and the two that are not layouts at all."""

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir)

    def written(self, text):
        path = self.dir / "results.json"
        path.write_text(text, encoding="utf-8")
        return MR.read_records(path)

    def test_a_json_array(self):
        self.assertEqual(self.written('[{"k": 1}, {"k": 2}]'),
                         [{"k": 1}, {"k": 2}])

    def test_a_wrapper_object(self):
        for name in ("results", "factories", "rows"):
            with self.subTest(key=name):
                self.assertEqual(self.written('{"%s": [{"k": 1}]}' % name),
                                 [{"k": 1}])

    def test_a_single_bare_object(self):
        self.assertEqual(self.written('{"k": 1}'), [{"k": 1}])

    def test_json_lines_with_comments(self):
        self.assertEqual(
            self.written('# a note\n{"k": 1}\n\n{"k": 2}\n'),
            [{"k": 1}, {"k": 2}])

    def test_an_empty_file_is_no_results_not_an_error(self):
        """"Nothing new to merge" has to be a thing the tool can be told."""
        self.assertEqual(self.written(""), [])
        self.assertEqual(self.written("   \n\n"), [])

    def test_nonsense_is_refused(self):
        with self.assertRaises(ValueError):
            self.written("this is not json at all")
        with self.assertRaises(ValueError):
            self.written("[1, 2, 3]\nnot json\n")


class TestMergingIntoTheShippedCatalogue(unittest.TestCase):
    """The two no-ops that have to be exact no-ops."""

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir)
        self.json_path = self.dir / "master_catalog.json"
        shutil.copy(CF.CATALOG_JSON, self.json_path)
        self.shipped = CF.CATALOG_JSON.read_text(encoding="utf-8")

    def run_merge(self, records, *extra):
        results = self.dir / "results.json"
        results.write_text(json.dumps(records), encoding="utf-8")
        return MR.main([str(results), "--catalog", str(self.json_path), *extra])

    def test_merging_nothing_rewrites_the_file_byte_for_byte(self):
        self.assertEqual(self.run_merge([]), 0)
        self.assertEqual(self.json_path.read_text(encoding="utf-8"),
                         self.shipped)

    def test_merging_nothing_regenerates_the_markdown_from_the_json(self):
        self.run_merge([])
        self.assertEqual((self.dir / "MASTER_CATALOG.md").read_text("utf-8"),
                         CF.render_markdown(CF.load()))

    def test_a_copy_of_an_existing_row_is_a_duplicate_and_changes_nothing(self):
        row = next(r for r in CF.rows() if r["n"] == 15 and r["k"] == 1)
        payload = CF.load()
        verdicts = MR.merge(payload, [{"k": row["k"], "N": row["N"],
                                       "columns": row["columns"]}], "test")
        self.assertEqual(verdicts_of(verdicts), ["duplicate"])
        self.assertEqual(CF.serialise(payload), self.shipped)

    def test_a_duplicate_does_not_register_its_regime_in_the_header(self):
        """A regime that only ever arrived on a discarded circuit is not one
        the catalogue has rows from, and an empty line in the rendered regime
        table would say otherwise."""
        row = next(r for r in CF.rows() if r["n"] == 15 and r["k"] == 1)
        payload = CF.load()
        MR.merge(payload, [{"k": row["k"], "N": row["N"],
                            "columns": row["columns"],
                            "regime": "a regime nobody has"}], "test")
        self.assertNotIn("a regime nobody has", payload["regimes"])


class TestLifecycle(unittest.TestCase):
    """Accepted, then improved, then duplicate -- and verified at every step."""

    def setUp(self):
        self.payload = empty_catalogue()

    def merge(self, *records):
        return MR.merge(self.payload, list(records), "test-results.json")

    def rows(self):
        return self.payload["factories"]

    def test_a_new_class_is_accepted(self):
        verdicts = self.merge({"k": 1, "N": 14, "columns": wide_46()})
        self.assertEqual(verdicts_of(verdicts), ["accepted"])
        row, = self.rows()
        self.assertEqual((row["n"], row["k"], row["d"], row["N"]),
                         (46, 1, 3, 14))
        self.assertEqual(row["gate"], "0")
        self.assertTrue(row["d_is_exact"])
        self.assertEqual(self.payload["n_classes"], 1)

    def test_an_accepted_row_verifies(self):
        """The whole point of merge importing the verifier."""
        self.merge({"k": 1, "N": 14, "columns": wide_46()})
        _facts, problems = VC.verify_row(self.rows()[0])
        self.assertEqual(problems, [])
        self.assertEqual(VC.duplicate_class_problems(self.rows()), [])

    def test_a_better_circuit_for_a_held_class_improves_it(self):
        self.merge({"k": 1, "N": 14, "columns": wide_46(),
                    "regime": "first pass"})
        verdicts = self.merge({"k": 1, "N": 10, "columns": narrow_46(),
                               "regime": "second pass"})
        self.assertEqual(verdicts_of(verdicts), ["improved"])
        row, = self.rows()
        self.assertEqual(row["N"], 10)
        self.assertEqual(row["columns"], [sorted(c) for c in narrow_46()])
        self.assertEqual(VC.verify_row(row)[1], [])

    def test_an_improvement_keeps_the_class_history(self):
        """The discarded circuit's provenance survives in ``sources``."""
        self.merge({"k": 1, "N": 14, "columns": wide_46(),
                    "regime": "first pass", "label": "the wide one"})
        self.merge({"k": 1, "N": 10, "columns": narrow_46(),
                    "regime": "second pass", "label": "the narrow one"})
        row, = self.rows()
        self.assertEqual([s["label"] for s in row["sources"]],
                         ["the wide one", "the narrow one"])
        self.assertEqual([s["N"] for s in row["sources"]], [14, 10])
        self.assertEqual(set(row["regimes"]), {"first pass", "second pass"})
        self.assertEqual(row["strongest_claim"],
                         self.payload["regimes"][row["regimes"][0]])

    def test_a_worse_circuit_for_a_held_class_is_a_duplicate(self):
        self.merge({"k": 1, "N": 10, "columns": narrow_46()})
        before = copy.deepcopy(self.payload)
        verdicts = self.merge({"k": 1, "N": 14, "columns": wide_46()})
        self.assertEqual(verdicts_of(verdicts), ["duplicate"])
        self.assertEqual(self.payload, before)

    def test_a_circuit_padded_with_a_dead_check_wire_is_refused(self):
        """The fixture this suite used to call "the wide one", now rejected.

        Two ``check_only_15_on_5`` gadgets is a valid factory by every other
        measure -- the parities are even, the gate is right, the distance is 3 --
        and merge took it for a legitimately wider circuit for the class.  It is
        not one: each gadget's fifth wire carries a syndrome bit its other four
        already determine, and deleting both recovers the narrower circuit
        exactly.  Accepting it published an ``N`` two larger than the circuit
        needed, in the field this table is read for.
        """
        padded = (FIFTEEN_TO_ONE + check_only_15_on_5([5, 6, 7, 8, 9])
                  + check_only_15_on_5([10, 11, 12, 13, 14]))
        verdicts = self.merge({"k": 1, "N": 15, "columns": padded})
        self.assertEqual(verdicts_of(verdicts), ["rejected"])
        _index, _verdict, _row, problems = verdicts[0]
        self.assertEqual(kinds(problems), {"redundant-check"},
                         "the padding must be the ONLY thing wrong with it")
        self.assertEqual(self.rows(), [], "nothing may be stored")

    def test_a_measured_FLOOR_is_stored_as_a_floor(self):
        """No fixture here has ever reached the floor branch.

        Every circuit in this suite pins its distance exactly, so the branch
        that stores an unproved floor was never executed: flipping its
        ``exact`` to ``True`` -- publishing every floor as a measured value,
        the one thing this catalogue says it never does -- changed no test.
        The measurement is stubbed because a circuit whose sweep genuinely runs
        out is far too large to keep in a unit test.
        """
        # The floor must be one the circuit really meets -- narrow_46 is d = 3 --
        # or the row is rejected for overstating its distance, which is a
        # different check and not the one under test here.
        floor_report = {"d_at_least": 3, "d_exact": None, "d_upper": None,
                        "witness": None, "A_d": None, "A_d_at_weight": None,
                        "scanned": {"1": "clean", "2": "clean",
                                    "3": "skipped"}}
        real = MR.VC.measure_distance
        try:
            MR.VC.measure_distance = lambda *a, **k: floor_report
            verdicts = self.merge({"k": 1, "N": 10, "columns": narrow_46()})
        finally:
            MR.VC.measure_distance = real
        self.assertEqual(verdicts_of(verdicts), ["accepted"])
        row, = self.rows()
        self.assertEqual(row["d"], 3)
        self.assertIs(row["d_is_exact"], False,
                      "a floor may never be stored as a measured distance")
        self.assertIsNone(row["d_upper"])
        self.assertIsNone(row["d_witness"])

    def test_the_final_verify_bar_is_load_bearing(self):
        """`candidate_row` ends by running the row through `verify_row`.

        Every rejection this suite exercises is caught by an earlier check, so
        that last bar could be deleted with the suite green -- and it is the one
        that makes "what merge admits is what verify_catalog confirms" true by
        construction rather than by coincidence.
        """
        real = MR.VC.verify_row
        try:
            MR.VC.verify_row = lambda *a, **k: ({}, [("invented", "a problem "
                                                      "only verify_row sees")])
            verdicts = self.merge({"k": 1, "N": 10, "columns": narrow_46()})
        finally:
            MR.VC.verify_row = real
        self.assertEqual(verdicts_of(verdicts), ["rejected"])
        self.assertEqual(self.rows(), [], "nothing may reach the catalogue")

    def test_retention_prefers_the_tighter_circuit_on_every_tie_break(self):
        """N, then n, then the stronger distance, then a proved frame.

        The suite only ever exercised the N comparison, so the later tie-breaks
        could be reordered or dropped unnoticed -- and each of them decides
        which circuit a class publishes.
        """
        def row(**changes):
            base = {"N": 10, "n": 46, "d": 3, "sk_key": [[0]]}
            base.update(changes)
            return base
        self.assertLess(MR.retention_key(row(N=9)), MR.retention_key(row()),
                        "fewer ambient qubits wins")
        self.assertLess(MR.retention_key(row(n=45)), MR.retention_key(row()),
                        "then fewer columns")
        self.assertLess(MR.retention_key(row(d=4)), MR.retention_key(row()),
                        "then the stronger proved distance")
        self.assertLess(MR.retention_key(row()),
                        MR.retention_key(row(sk_key=None)),
                        "then a proved canonical frame over an as-found one")

    def test_improve_clears_every_note_it_does_not_carry_over(self):
        """A note left behind by an improvement describes a circuit that is gone.

        The ten reduced rows each carry a ``columns_note`` saying their N is not
        one their sources published.  An improvement appends a source publishing
        the NEW N, so a stranded note becomes a statement the row contradicts --
        and `verify_catalog` rightly refuses it.  `NOTE_FIELDS` must therefore
        list every optional note, not the three it happened to start with.
        """
        self.assertEqual(set(MR.NOTE_FIELDS),
                         {f for f in CF.OPTIONAL_FIELDS},
                         "NOTE_FIELDS must cover every optional note field")
        self.merge({"k": 1, "N": 10, "columns": narrow_46()})
        incumbent, = self.rows()
        incumbent["columns_note"] = "one redundant check wire deleted"
        incumbent["N"] = 14
        self.merge({"k": 1, "N": 10, "columns": narrow_46()})
        kept, = self.rows()
        self.assertNotIn("columns_note", kept,
                         "the improvement must clear the stale note")
        self.assertEqual(VC.verify_row(kept)[1], [])

    def test_an_undecided_candidate_is_KEPT_and_says_what_is_unproved(self):
        """A verified factory is not thrown away over a bookkeeping question.

        When the isomorphism search runs out, the circuit itself has still been
        re-derived and its distance proved like every other row's; the only
        open question is whether some existing row of the same ``(n, k)`` is the
        same class up to a relabelling.  At the widths where the search gives up
        -- ``k`` in the tens, gates of thousands of monomials -- those are the
        results least easily found again, so the row is admitted and records
        what is unproved about it rather than being refused.

        What is forbidden is silence: `verify_catalog.duplicate_class_problems`
        fails such a pair unless one of the two carries the note.
        """
        self.merge({"k": 1, "N": 10, "columns": narrow_46()})
        held, = self.rows()
        held.update(sk_key=None, sk_canonical_frame=False,
                    sk_key_note="unproved frame (fixture)")
        original = MR.GC.gl_isomorphic
        try:
            MR.GC.gl_isomorphic = lambda *a, **k: None
            verdicts = self.merge({"k": 1, "N": 14, "columns": wide_46()})
        finally:
            MR.GC.gl_isomorphic = original
        self.assertEqual(verdicts_of(verdicts), ["accepted"],
                         "the factory must reach the catalogue")
        self.assertEqual(len(self.rows()), 2, "as a class of its own")
        noted = [r for r in self.rows() if "dedup_note" in r]
        self.assertEqual(len(noted), 1, "exactly the admitted row says so")
        self.assertIn("was not decided", noted[0]["dedup_note"])
        self.assertIn(held["sk_fingerprint"], noted[0]["dedup_note"],
                      "the note must name the row it could not be told from")

    def test_an_accepted_row_is_credited_by_default(self):
        """Within the length-54 window: the classification and the report."""
        self.merge({"k": 1, "N": 10, "columns": narrow_46()})
        row, = self.rows()
        self.assertEqual(row["citations"], MR.default_citations(46))
        self.assertEqual(row["citations"],
                         ["wills2026classification", "jain2026symmetry"])
        self.assertLessEqual(set(row["citations"]),
                             set(self.payload["references"]))
        self.assertEqual(VC.citation_problems(self.payload), [])

    def test_a_record_may_name_its_own_citations(self):
        key = next(iter(self.payload["references"]))
        self.merge({"k": 1, "N": 10, "columns": narrow_46(),
                    "citations": [key]})
        row, = self.rows()
        self.assertEqual(row["citations"], [key])

    def test_a_citation_the_header_cannot_resolve_is_refused(self):
        verdicts = self.merge({"k": 1, "N": 10, "columns": narrow_46(),
                               "citations": ["nobody2099"]})
        self.assertEqual(verdicts_of(verdicts), ["rejected"])
        self.assertEqual(self.rows(), [])

    def test_the_default_works_are_registered_when_the_header_lacks_them(self):
        self.payload["references"] = {}
        self.merge({"k": 1, "N": 10, "columns": narrow_46()})
        self.assertEqual(set(self.payload["references"]),
                         {"wills2026classification", "jain2026symmetry"})
        self.assertEqual(VC.citation_problems(self.payload), [])

    def test_an_improvement_adds_its_citations_to_the_class(self):
        key = next(k for k in self.payload["references"]
                   if k not in MR.default_citations(46))
        self.merge({"k": 1, "N": 14, "columns": wide_46()})
        self.merge({"k": 1, "N": 10, "columns": narrow_46(),
                    "citations": [key]})
        row, = self.rows()
        self.assertEqual(row["citations"], MR.default_citations(46) + [key])

    def test_a_class_credited_to_the_literature_alone_stays_so(self):
        """Neither a better circuit nor a copy re-credits it to the defaults.

        A class a published work stated before is credited to that work alone;
        a search that finds it again, or finds it on fewer wires, has not made
        the classification or the report its source.
        """
        key = next(k for k in self.payload["references"]
                   if k not in MR.default_citations(46))
        self.merge({"k": 1, "N": 14, "columns": wide_46(), "citations": [key]})
        self.merge({"k": 1, "N": 14, "columns": wide_46()})
        row, = self.rows()
        self.assertEqual(row["citations"], [key], "a duplicate")
        self.merge({"k": 1, "N": 10, "columns": narrow_46()})
        row, = self.rows()
        self.assertEqual(row["N"], 10)
        self.assertEqual(row["citations"], [key], "an improvement")

    def test_merging_the_same_result_twice_is_a_no_op_the_second_time(self):
        self.merge({"k": 1, "N": 10, "columns": narrow_46()})
        before = copy.deepcopy(self.payload)
        verdicts = self.merge({"k": 1, "N": 10, "columns": narrow_46()})
        self.assertEqual(verdicts_of(verdicts), ["duplicate"])
        self.assertEqual(self.payload, before)

    def test_two_copies_in_one_file_behave_as_two_files(self):
        verdicts = self.merge({"k": 1, "N": 10, "columns": narrow_46()},
                              {"k": 1, "N": 10, "columns": narrow_46()})
        self.assertEqual(verdicts_of(verdicts), ["accepted", "duplicate"])
        self.assertEqual(len(self.rows()), 1)

    def test_rows_stay_in_the_catalogue_s_sort_order(self):
        self.merge({"k": 1, "N": 10, "columns": narrow_46()},
                   {"k": 1, "N": 5, "columns": FIFTEEN_TO_ONE})
        self.assertEqual([r["n"] for r in self.rows()], [15, 46])
        self.assertEqual([MR.sort_key(r) for r in self.rows()],
                         sorted(MR.sort_key(r) for r in self.rows()))

    def test_a_new_regime_is_registered_at_the_weakest_end(self):
        self.merge({"k": 1, "N": 10, "columns": narrow_46(),
                    "regime": "a fresh corpus",
                    "strength": "found by a new search; a witness, not a bound"})
        self.assertEqual(list(self.payload["regimes"])[-1], "a fresh corpus")
        self.assertEqual(self.payload["regimes"]["a fresh corpus"],
                         "found by a new search; a witness, not a bound")

    def test_the_output_frame_is_canonicalised_on_the_way_in(self):
        """A circuit submitted in a permuted output frame is stored in the
        canonical one, so its stored columns deposit literally its stored gate.

        Taken from a shipped row whose gate is ``0+01`` -- ``T`` on output 0 and
        ``CS`` across both -- with the two outputs swapped.  The submitted
        circuit deposits ``1+01``, which is the same class in a worse frame, and
        merge has to put it back and say that it did.
        """
        original = next(r for r in CF.rows()
                        if r["k"] == 2 and r["gate"] == "0+01")
        swapped = [sorted({0: 1, 1: 0}.get(q, q) for q in column)
                   for column in original["columns"]]
        self.merge({"k": 2, "N": original["N"], "columns": swapped})
        row, = self.rows()
        self.assertTrue(row["sk_canonical_frame"])
        self.assertTrue(row["relabelled_into_canonical_frame"])
        self.assertEqual(row["gate"], "0+01")
        self.assertEqual(row["columns"],
                         [sorted(c) for c in original["columns"]])
        self.assertEqual(VC.verify_row(row)[1], [])


class TestFindClass(unittest.TestCase):
    """Dedup decides; it does not trust a hash.

    Two rows are the same class when one gate is a CNOT frame change of the
    other, and `find_class` may only shortcut that question where the shortcut
    is exact.  Equal PROVED S_k keys are: they mean equal gates up to a
    permutation, and a permutation is a frame change.  The permutation-
    invariant FINGERPRINT that stands in for a key on gates too wide to
    minimise is not: it is a hash, and a hash match is a suspicion.

    The consequence of getting that wrong is quiet, which is why it is pinned
    here: a collision would report a genuinely new class as a ``duplicate``,
    change nothing, print one reassuring line, and lose the result.
    """

    def setUp(self):
        self.payload = empty_catalogue()
        MR.merge(self.payload, [{"k": 1, "N": 10, "columns": narrow_46()}], "t")
        self.rows = self.payload["factories"]
        self.held, = self.rows

    def candidate(self, columns, k=1, N=None):
        row, problems = MR.candidate_row(
            {"k": k, "N": N or 10, "columns": columns}, empty_catalogue(),
            "t", 0)
        self.assertEqual(problems, [], "the fixture itself must verify")
        return row

    def test_the_same_class_is_found(self):
        """The baseline: without this the two tests below are vacuous."""
        self.assertEqual(
            MR.find_class(self.rows, self.candidate(narrow_46())), 0)

    def test_a_fingerprint_collision_is_decided_not_believed(self):
        """A forged collision: same (n, k) and fingerprint, different gate.

        A real collision is not constructible on demand -- that is what makes a
        fingerprint useful -- so it is forged, which tests exactly the branch a
        real one would take.  Both sides are marked as having no proved
        canonical form, so the key is the fingerprint for both and it MATCHES.
        The gates differ (``0`` against ``0+01`` on two outputs, not one class
        even up to a frame), so `glcanon.gl_isomorphic` must overrule the
        match and the candidate must come back as a class the catalogue does
        not have.
        """
        other = next(r for r in CF.rows() if r["k"] == 2 and r["gate"] == "0+01")
        incumbent = copy.deepcopy(self.held)
        incumbent["n"], incumbent["k"] = other["n"], other["k"]
        incumbent["columns"], incumbent["N"] = other["columns"], other["N"]
        incumbent["sk_key"] = None
        collider = self.candidate(FIFTEEN_TO_ONE, N=5)
        collider["n"], collider["k"] = other["n"], other["k"]
        collider["sk_key"] = None
        collider["sk_fingerprint"] = incumbent["sk_fingerprint"]

        self.assertEqual(MR.class_key(collider), MR.class_key(incumbent),
                         "the forged collision must actually collide")
        self.assertIsNone(MR.find_class([incumbent], collider),
                          "a fingerprint match is a suspicion, not a verdict: "
                          "these two gates are not the same class")

    def test_a_gate_in_another_cnot_frame_is_found(self):
        """Different S_k key, same GL(k,2) class: the case the class exists for.

        The shipped ``0+01`` circuit with output row 1 replaced by row 0 XOR
        row 1 deposits ``0+1``, a different monomial set that no output
        permutation relates to the original, and must still be found as the
        held class.  (Moving row 0 instead would leave ``0+01`` unchanged:
        ``x0 -> x0 + x1`` sends ``x0 + 2 x0 x1`` back to itself modulo
        Clifford.)
        """
        original = next(r for r in CF.rows()
                        if r["k"] == 2 and r["gate"] == "0+01")
        payload = empty_catalogue()
        MR.merge(payload, [{"k": 2, "N": original["N"],
                            "columns": original["columns"]}], "t")
        moved = [sorted(({1} if (0 in c) != (1 in c) else set())
                        | {q for q in c if q != 1})
                 for c in original["columns"]]
        candidate, problems = MR.candidate_row(
            {"k": 2, "N": original["N"], "columns": moved}, payload, "t", 0)
        self.assertEqual(problems, [])
        self.assertEqual(candidate["gate"], "0+1")
        self.assertNotEqual(candidate["gate"], payload["factories"][0]["gate"],
                            "the fixture must be a different S_k class")
        self.assertEqual(MR.find_class(payload["factories"], candidate), 0)

    def test_the_same_gate_at_another_distance_is_not_found(self):
        """A circuit at a different distance is a different class: finding it
        would let the retention rule discard a higher-distance circuit."""
        candidate = self.candidate(narrow_46())
        candidate["d"] = self.held["d"] + 1
        self.assertIsNone(MR.find_class(self.rows, candidate))

    def test_an_unproved_row_is_still_matched_by_isomorphism(self):
        """And the collision test above must not be passing by refusing everything.

        The same forgery with the gates genuinely equal has to be FOUND, which
        is the half that keeps a wide class from being catalogued twice.
        """
        incumbent = copy.deepcopy(self.held)
        incumbent["sk_key"] = None
        candidate = self.candidate(narrow_46())
        candidate["sk_key"] = None
        candidate["sk_fingerprint"] = "not the incumbent's fingerprint"
        self.assertEqual(MR.find_class([incumbent], candidate), 0)


class TestRejections(unittest.TestCase):
    """Every negative case, submitted as a new result."""

    def setUp(self):
        self.payload = empty_catalogue()

    def reject(self, record):
        verdicts = MR.merge(self.payload, [record], "test-results.json")
        _index, verdict, _row, problems = verdicts[0]
        self.assertEqual(verdict, "rejected")
        self.assertEqual(self.payload["factories"], [],
                         "a rejected result must not reach the catalogue")
        return kinds(problems)

    def test_a_good_result_is_not_rejected(self):
        """Otherwise every test below would pass for the wrong reason."""
        verdicts = MR.merge(self.payload,
                            [{"k": 1, "N": 10, "columns": narrow_46()}], "t")
        self.assertEqual(verdicts_of(verdicts), ["accepted"])

    def test_broken_check_parity(self):
        columns = [list(c) for c in narrow_46()]
        columns[0] = [0, 1, 4]           # an odd parity on check wires 1 and 4
        self.assertIn("check-contamination",
                      self.reject({"k": 1, "N": 10, "columns": columns}))

    def test_repeated_column(self):
        columns = [list(c) for c in narrow_46()]
        columns[1] = list(columns[0])
        self.assertIn("repeated-column",
                      self.reject({"k": 1, "N": 10, "columns": columns}))

    def test_a_gate_label_the_columns_contradict(self):
        """Readable, and wrong: the circuit deposits ``0+1``, not ``CS``."""
        problems = self.reject({"k": 2, "N": 10, "gate": "01",
                                "columns": two_output_30()})
        self.assertIn("gate-claim", problems)

    def test_a_gate_label_that_cannot_be_read_is_not_guessed_at(self):
        self.assertIn("gate-claim",
                      self.reject({"k": 1, "N": 10, "gate": "a T gate, sort of",
                                   "columns": narrow_46()}))

    def test_an_inflated_distance_claim(self):
        self.assertIn("distance-claim",
                      self.reject({"k": 1, "N": 10, "d": 7,
                                   "columns": narrow_46()}))

    def test_an_understated_distance_claim_is_accepted_at_the_true_value(self):
        """Claims are checked, not believed; understating is not an error."""
        MR.merge(self.payload, [{"k": 1, "N": 10, "d": 3,
                                 "columns": narrow_46()}], "t")
        self.assertEqual(self.payload["factories"][0]["d"], 3)

    def test_a_pseudo_output(self):
        """Two labels on one logical qubit: outputs 0 and 1 share every column."""
        columns = [sorted({0, 1} | {q + 1 for q in column if q})
                   if 0 in column else sorted(q + 1 for q in column)
                   for column in FIFTEEN_TO_ONE]
        self.assertIn("pseudo-output",
                      self.reject({"k": 2, "N": 6, "columns": columns}))

    def test_a_spectator_output(self):
        columns = [sorted(q + 1 if q else 0 for q in column)
                   for column in FIFTEEN_TO_ONE]
        columns += check_only_15_on_4([1, 6, 7, 8])
        self.assertIn("spectator-output",
                      self.reject({"k": 2, "N": 9, "columns": columns}))

    def test_a_level_2_circuit_is_out_of_scope(self):
        """Sound, and in the wrong table: it must say so and not be merged.

        A check-only block is a perfectly good Clifford circuit; it just
        deposits no non-Clifford gate, so it is not a level-3 factory and this
        catalogue makes no claim about it.
        """
        self.assertIn("not-level-3",
                      self.reject({"k": 1, "N": 4,
                                   "columns": check_only_15_on_4([0, 1, 2, 3])}))

    def test_a_wrong_metric_claim(self):
        self.assertIn("t_count-claim",
                      self.reject({"k": 1, "N": 10, "t_count": 9,
                                   "columns": narrow_46()}))
        self.assertIn("poly_degree-claim",
                      self.reject({"k": 1, "N": 10, "poly_degree": 3,
                                   "columns": narrow_46()}))

    def test_a_misspelt_field_is_not_silently_ignored(self):
        """A circuit merged from a field nobody read is the quiet disaster."""
        self.assertIn("schema",
                      self.reject({"k": 1, "N": 10, "colums": narrow_46(),
                                   "columns": narrow_46()}))

    def test_a_missing_field(self):
        self.assertIn("schema", self.reject({"k": 1, "columns": narrow_46()}))

    def test_a_mis_stated_register(self):
        self.assertIn("shape",
                      self.reject({"k": 1, "N": 14, "columns": narrow_46()}))
        self.assertIn("shape",
                      self.reject({"k": 1, "N": 10, "n": 44,
                                   "columns": narrow_46()}))

    def test_an_absurd_register_is_rejected_not_looped_over(self):
        """Rejected on the shape, in milliseconds, rather than iterated over."""
        self.assertIn("shape",
                      self.reject({"k": 1, "N": 2 ** 63,
                                   "columns": narrow_46()}))

    def test_an_undefined_discovery_value(self):
        self.assertIn("schema",
                      self.reject({"k": 1, "N": 10, "discovery": "a hunch",
                                   "columns": narrow_46()}))

    def test_a_result_may_not_redefine_an_existing_regime(self):
        self.assertIn("schema",
                      self.reject({"k": 1, "N": 10,
                                   "regime": "symmetry-SAT search",
                                   "strength": "something else entirely",
                                   "columns": narrow_46()}))


class TestExitStatus(unittest.TestCase):
    """The status a script driving this tool has to be able to trust."""

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir)
        self.json_path = self.dir / "master_catalog.json"
        CF.write(empty_catalogue(), self.json_path,
                 self.dir / "MASTER_CATALOG.md")

    def run_merge(self, records, *extra):
        results = self.dir / "results.json"
        results.write_text(json.dumps(records), encoding="utf-8")
        return MR.main([str(results), "--catalog", str(self.json_path), *extra])

    def test_a_clean_merge_exits_zero(self):
        self.assertEqual(
            self.run_merge([{"k": 1, "N": 10, "columns": narrow_46()}]), 0)
        self.assertEqual(len(CF.rows(self.json_path)), 1)

    def test_a_rejection_exits_non_zero(self):
        self.assertEqual(
            self.run_merge([{"k": 1, "N": 99, "columns": narrow_46()}]), 1)
        self.assertEqual(CF.rows(self.json_path), [])

    def test_dry_run_writes_nothing(self):
        self.run_merge([{"k": 1, "N": 10, "columns": narrow_46()}],
                       "--dry-run")
        self.assertEqual(CF.rows(self.json_path), [])


def two_output_30():
    """``[[30,2,3]]`` with gate ``0+1``: two 15-to-1s side by side."""
    first = [sorted({0: 0, 1: 2, 2: 3, 3: 4, 4: 5}[q] for q in column)
             for column in FIFTEEN_TO_ONE]
    second = [sorted({0: 1, 1: 6, 2: 7, 3: 8, 4: 9}[q] for q in column)
              for column in FIFTEEN_TO_ONE]
    return first + second


class TestGateLabelGrammar(unittest.TestCase):
    """`gatelabels.parse` vets the claims this tool compares, so its grammar
    is part of the acceptance bar."""

    def test_a_repeated_factor_is_unreadable_not_merged(self):
        """``T0.T0`` is ``S0`` -- Clifford -- and a monomial set cannot say
        that.  The old parser deduplicated, so a Clifford-equivalent label
        compared EQUAL to a genuine ``T0`` circuit's derived gate and the
        claim check waved it through.  A parser that never guesses refuses.
        """
        import gatelabels as GL
        for label, k in (("T0.T0", 1), ("T^2.T0", 2), ("CS.CS01", 2),
                         ("012.012", 3), ("CS01.CS01", 2)):
            with self.subTest(label=label):
                kind, monomials, note = GL.parse(label, k)
                self.assertEqual(kind, "unreadable")
                self.assertTrue("more than once" in note
                                or "on its own" in note,
                                f"the reason must name the repeat: {note!r}")

    def test_legitimate_labels_still_read(self):
        import gatelabels as GL
        kind, monomials, _note = GL.parse("T0.CS01.CCZ012", 3)
        self.assertEqual(kind, "monomials")
        self.assertEqual(len(monomials), 3)
        kind, monomials, _note = GL.parse("T^3", 3)
        self.assertEqual(kind, "ambiguous")
        self.assertEqual(monomials,
                         frozenset({frozenset({0}), frozenset({1}),
                                    frozenset({2})}))


    def test_indices_inside_one_factor_must_be_distinct(self):
        """``CS00`` passed the arity-length test and then collapsed to the
        degree-one monomial {0}, so an invalid two-qubit label compared equal
        to a genuine T0 circuit's gate.  Distinctness is part of the name."""
        import gatelabels as GL
        for label, k in (("CS00", 3), ("CCZ001", 3), ("0,0", 3), ("00", 3)):
            with self.subTest(label=label):
                self.assertEqual(GL.parse(label, k)[0], "unreadable")

    def test_a_leading_zero_index_is_refused_not_guessed_at(self):
        """``T01`` read as T1 -- and ``T012`` at wide k read as T12 -- dropped
        the zero silently; this catalogue never writes indices that way, so
        the likelier truth is a mangled ``T0.T1`` or ``CCZ012``.  Refused."""
        import gatelabels as GL
        for label, k in (("T01", 3), ("T012", 15), ("T00", 2), ("0,01", 3),
                         ("CS0,01", 3)):
            with self.subTest(label=label):
                self.assertEqual(GL.parse(label, k)[0], "unreadable")
        # multi-digit indices without the zero stay readable where legitimate
        self.assertEqual(GL.parse("T10", 12)[1], frozenset({frozenset({10})}))

    def test_an_unnamed_monomial_above_degree_three_is_unreadable(self):
        """Level-3 gates carry degrees 1..3 only; ``0123`` names nothing this
        catalogue can hold, so it is refused rather than carried."""
        import gatelabels as GL
        for label, k in (("0123", 5), ("0,1,2,3", 5)):
            with self.subTest(label=label):
                self.assertEqual(GL.parse(label, k)[0], "unreadable")


class TestSourceFrameClaims(unittest.TestCase):
    """A gate label describes the circuit AS SUBMITTED; the canonical frame is
    this catalogue's presentation choice, not the submitter's error."""

    def setUp(self):
        rows = CF.load()["factories"]
        pick = next(r for r in rows if r["k"] == 2 and r["gate"] == "0+01")
        swap = {0: 1, 1: 0}
        self.columns = [sorted(swap.get(q, q) for q in c)
                        for c in pick["columns"]]
        self.N = pick["N"]
        self.payload = empty_catalogue()

    def test_a_truthful_source_frame_label_is_accepted(self):
        """The swapped circuit deposits ``1+01`` in its own frame; ``T1.CS01``
        is the truth about it, and the old ordering rejected the truth
        because the STORED frame calls the class ``0+01``."""
        verdicts = MR.merge(self.payload,
                            [{"k": 2, "N": self.N, "columns": self.columns,
                              "gate": "T1.CS01"}], "t")
        self.assertEqual(verdicts_of(verdicts), ["accepted"])
        self.assertEqual(self.payload["factories"][0]["gate"], "0+01",
                         "stored canonically all the same")

    def test_a_wrong_label_is_still_refused(self):
        verdicts = MR.merge(self.payload,
                            [{"k": 2, "N": self.N, "columns": self.columns,
                              "gate": "T0.T1"}], "t")
        _i, verdict, _row, problems = verdicts[0]
        self.assertEqual(verdict, "rejected")
        self.assertIn("gate-claim", kinds(problems))


if __name__ == "__main__":
    unittest.main()
