"""`verify_catalog.py` and `catalogfile.py`, on good rows and on broken ones.

A verifier is only worth what its REJECTIONS are worth.  That a true row passes
says almost nothing -- a function that returns "fine" unconditionally passes
every true row -- so most of this file takes a shipped row, breaks it in one
specific way, and insists on the specific reason coming back.  The mutations are
the ones that actually threaten this catalogue:

  * a parity broken so the circuit deposits phase on a postselected wire,
  * a distance inflated above what the columns support,
  * a gate label that no longer matches the columns,
  * a second output that is the first one wearing a different label,
  * a column written twice,
  * a class present under two rows,

plus the malformed inputs a validator has to REJECT rather than crash on, since
a validator that raises on bad input has not rejected it.

The good-row half is kept deliberately small: the full 444-row run is
`verify_catalog.py` itself, which takes minutes, and duplicating it here would
make the suite too slow to run often enough to matter.
"""
import copy
import itertools
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE.parent
REPO = CATALOGUE.parent
sys.path.insert(0, str(CATALOGUE))
sys.path.insert(0, str(REPO))

import catalogfile as CF                                        # noqa: E402
import faultcore as FC                                          # noqa: E402
import glcanon as GC                                            # noqa: E402
import skcanon as SK                                            # noqa: E402
import verify_catalog as VC                                     # noqa: E402

#: The mutation rows are re-verified from scratch every time, so they have to be
#: cheap: these caps keep every one of them under a second.
SMALL_N, SMALL_K = 40, 4


def payload():
    return CF.load()


def small_rows(rows, limit=6):
    """A few shipped rows small enough to mutate and re-verify quickly."""
    return [r for r in rows if r["n"] <= SMALL_N and r["k"] <= SMALL_K][:limit]


def payload_with(row, **changes):
    """A one-row payload carrying the shipped header, for the file-level passes."""
    row = copy.deepcopy(row)
    row.update(changes)
    blob = payload()
    blob["factories"] = [row]
    blob["n_classes"] = 1
    return blob


def kinds(problems):
    return {kind for kind, _detail in problems}


def check_only_gadget(wires):
    """All 15 non-empty subsets of four wires: every degree-<=3 parity even.

    A block that deposits nothing anywhere and contaminates no check, so it can
    be bolted onto a real circuit to manufacture one specific defect at a time
    without accidentally manufacturing another.
    """
    return [sorted(subset) for size in (1, 2, 3, 4)
            for subset in itertools.combinations(wires, size)]


class TestCatalogFile(unittest.TestCase):
    """The file layer: the two files must be two views of one thing."""

    @classmethod
    def setUpClass(cls):
        cls.payload = payload()

    def test_json_round_trips_byte_for_byte(self):
        """Rewriting an unchanged catalogue must not touch a single byte.

        This is what makes a merge's diff readable: were the serialiser to
        re-indent, every merge would rewrite all 9 MB and the one row that
        changed would be invisible in it.
        """
        shipped = CF.CATALOG_JSON.read_text(encoding="utf-8")
        self.assertEqual(CF.serialise(self.payload), shipped)

    def test_serialiser_leaves_bracketed_numbers_in_strings_alone(self):
        """The collapse pattern is anchored to a newline after ``[``, which a
        JSON string cannot contain.  Without the anchor it matched INSIDE
        strings and rewrote a provenance note -- "iteration [ 12 ] of the
        search" came back as "iteration [12] of the search", a formatter
        silently editing payload content."""
        for note in ("iteration [ 12 ] of the search", "budget[  7  ]",
                     "weights [ 5 ] and [ 6 ]"):
            payload = {"factories": [], "note": note}
            with self.subTest(note=note):
                self.assertEqual(json.loads(CF.serialise(payload)), payload)

    def test_serialiser_does_not_corrupt_the_columns(self):
        """The collapsed integer lists must still parse back to the same data."""
        self.assertEqual(json.loads(CF.serialise(self.payload)), self.payload)

    def test_markdown_is_generated_not_edited(self):
        """The shipped Markdown must be exactly what the generator produces."""
        self.assertEqual(CF.render_markdown(self.payload),
                         CF.CATALOG_MD.read_text(encoding="utf-8"))

    def test_markdown_is_deterministic(self):
        self.assertEqual(CF.render_markdown(self.payload),
                         CF.render_markdown(CF.load()))

    def test_every_row_carries_exactly_the_documented_fields(self):
        allowed = set(CF.REQUIRED_FIELDS + CF.OPTIONAL_FIELDS)
        for index, row in enumerate(self.payload["factories"], 1):
            with self.subTest(row=index):
                self.assertFalse(set(CF.REQUIRED_FIELDS) - set(row))
                self.assertFalse(set(row) - allowed)


class TestGoodRows(unittest.TestCase):
    """A sample of shipped rows, re-derived from their columns."""

    @classmethod
    def setUpClass(cls):
        cls.rows = payload()["factories"]
        cls.sample = small_rows(cls.rows)

    def test_sample_verifies(self):
        for row in self.sample:
            with self.subTest(gate=row["gate"], n=row["n"]):
                _facts, problems = VC.verify_row(row)
                self.assertEqual(problems, [])

    def test_the_shipped_catalogue_has_no_duplicate_classes(self):
        """The whole file, both passes: the dedup key and the decision procedure."""
        self.assertEqual(VC.duplicate_class_problems(self.rows), [])

    def test_understating_a_distance_is_not_an_error(self):
        """A row may publish a floor where an exact value existed.

        The asymmetry is deliberate and documented in `confirm_distance`: what
        such a row claims is TRUE, and the failure this catalogue exists to
        prevent is the other direction.  Pinned here so it cannot be "tidied
        away" by a later reading of the spec.  The row has to have ``d >= 4``
        for there to be room to understate it and stay inside this catalogue.
        """
        row = copy.deepcopy(next(r for r in self.rows if r["d_is_exact"]
                                 and r["d"] >= 4 and r["n"] <= 64))
        row["d_is_exact"] = False
        row["d_upper"] = row["d"]
        row["d"] -= 1
        _facts, problems = VC.verify_row(row)
        self.assertEqual(problems, [])


class TestBrokenRows(unittest.TestCase):
    """One mutation at a time, each with the reason it must produce."""

    @classmethod
    def setUpClass(cls):
        rows = payload()["factories"]
        # a small exact-distance row with room to break: several columns, a
        # gate a mislabelling can contradict, and checks to contaminate
        cls.good = copy.deepcopy(next(r for r in small_rows(rows)
                                      if r["d_is_exact"] and r["N"] > r["k"]))

    def broken(self, **changes):
        row = copy.deepcopy(self.good)
        row.update(changes)
        _facts, problems = VC.verify_row(row)
        return problems

    def test_the_unmutated_row_passes(self):
        """Otherwise every test below would pass for the wrong reason."""
        self.assertEqual(self.broken(), [])

    def test_inflated_distance(self):
        problems = self.broken(d=self.good["d"] + 2,
                               d_upper=self.good["d"] + 2)
        self.assertIn("distance-inflated", kinds(problems))

    def test_a_floor_may_not_be_printed_as_a_measurement(self):
        """``d_is_exact`` with no genuine witness at ``d`` is the cardinal sin."""
        self.assertIn("distance-witness", kinds(self.broken(d_witness=[0])))
        self.assertIn("distance-witness", kinds(self.broken(d_witness=None)))

    def test_a_floor_may_not_carry_a_witness_at_itself(self):
        """A fault AT the floor would have made the distance exact."""
        row = copy.deepcopy(self.good)
        row["d_is_exact"] = False
        problems = VC.verify_row(row)[1]
        self.assertIn("distance", kinds(problems))

    def test_wrong_gate_label(self):
        problems = self.broken(gate="0+1+01")
        self.assertIn("gate-mismatch", kinds(problems))

    def test_stale_human_gate_label(self):
        """A field no computation reads is still a lie to a reader."""
        self.assertIn("gate_human-mismatch", kinds(self.broken(gate_human="T9")))

    def test_broken_check_parity(self):
        """Phase on a postselected wire: not a factory at all."""
        columns = [list(c) for c in self.good["columns"]]
        columns[0] = sorted(set(columns[0]) ^ {self.good["N"] - 1})
        problems = self.broken(columns=columns)
        self.assertIn("check-contamination", kinds(problems))

    def test_repeated_column(self):
        columns = [list(c) for c in self.good["columns"]]
        columns[1] = list(columns[0])
        problems = self.broken(columns=columns)
        self.assertIn("repeated-column", kinds(problems))

    def test_pseudo_output(self):
        """A second output that is the first one modulo the check span.

        Built by splitting one output wire into two that every column touches
        together: their rows are then identical, so ``k = 2`` counts one
        logical qubit twice.
        """
        row = copy.deepcopy(self.good)
        k = row["k"]
        columns = [sorted({q + 1 if q >= k else q for q in column}
                          | ({k} if any(q < k for q in column) else set()))
                   for column in row["columns"]]
        row.update(k=k + 1, N=row["N"] + 1, columns=columns)
        problems = VC.verify_row(row)[1]
        self.assertIn("pseudo-output", kinds(problems))

    def test_spectator_output(self):
        """An output the gate never touches is padding, and ``k`` is a lie.

        Built by bolting a check-only gadget onto a real circuit and then
        DECLARING one of the gadget's wires an output.  The gadget deposits
        nothing, so the gate is exactly the original one and the new output
        appears in none of its monomials -- which is precisely a spectator, and
        nothing else is wrong with the parities.
        """
        row = copy.deepcopy(self.good)
        k = row["k"]
        shifted = [sorted(q if q < k else q + 1 for q in column)
                   for column in row["columns"]]
        top = row["N"] + 1
        columns = shifted + check_only_gadget([k, top, top + 1, top + 2])
        _facts, problems = VC.derive(columns, k + 1, top + 3)
        self.assertIn("spectator-output", kinds(problems))
        self.assertNotIn("check-contamination", kinds(problems))
        self.assertNotIn("not-level-3", kinds(problems))

    def test_a_duplicated_check_wire_is_refused(self):
        """A check wire repeating another's support decides nothing, so N lies.

        Duplicating check wire ``c`` as a new top wire is the cleanest way to
        build this defect ALONE: every monomial involving the new wire reduces
        to the same monomial with ``c``, so the factory condition still holds,
        and the gate, the outputs and the distance are all untouched.  The only
        thing wrong with the circuit is that the new wire's syndrome bit repeats
        ``c``'s and can never reject anything ``c`` accepts -- which is why the
        assertion is that this is the ONLY problem reported.
        """
        row = copy.deepcopy(self.good)
        k, N = row["k"], row["N"]
        c = N - 1                            # a check wire, since k < N
        columns = [sorted(column + [N]) if c in column else sorted(column)
                   for column in row["columns"]]
        _facts, problems = VC.derive(columns, k, N + 1)
        self.assertEqual(kinds(problems), {"redundant-check"})

    def test_an_absurd_register_is_refused_by_BOTH_shape_paths(self):
        """The idle-wire branch must not build ``range(N)`` to name the wires.

        The existing absurd-register test states ``N`` larger than the top wire
        index, which the first branch answers without looking at ``N`` at all.
        The second branch is reached only when the TOP wire is present and one
        below it is missing, and it used to name the idle wires with
        ``set(range(N)) - touched`` -- an out-of-memory kill at this ``N``,
        which is not a rejection.
        """
        started = time.time()
        problems = VC.structural_problems(1, 2 ** 63, [[0, 2 ** 63 - 1]])
        self.assertIn("shape", kinds(problems))
        self.assertLess(time.time() - started, 1.0,
                        "it must answer, not enumerate the register")

    def test_a_fingerprint_collision_is_not_convicted_by_the_key(self):
        """A hash match is a suspicion; only the second pass may convict.

        The hexagon ``01+05+12+23+34+45`` and the two triangles
        ``01+02+12+34+35+45`` are both ``[[6,6]]``, share a fingerprint, and are
        NOT isomorphic -- deposited by columns that are just the edges of each
        graph, since every vertex has even degree and no column holds three
        wires.  Reporting them as a duplicate would block a legitimate
        catalogue.
        """
        hexagon = [[0, 1], [0, 5], [1, 2], [2, 3], [3, 4], [4, 5]]
        triangles = [[0, 1], [0, 2], [1, 2], [3, 4], [3, 5], [4, 5]]
        self.assertEqual(self.unproved(hexagon)["sk_fingerprint"],
                         self.unproved(triangles)["sk_fingerprint"],
                         "the fixture must actually collide")
        self.assertEqual(
            VC.duplicate_class_problems([self.unproved(hexagon),
                                         self.unproved(triangles)]), [])
        self.assertIn("duplicate-class",
                      kinds(VC.duplicate_class_problems(
                          [self.unproved(hexagon), self.unproved(hexagon)])),
                      "a real duplicate must still be caught")

    def test_an_undecided_pair_must_be_documented_but_may_be_kept(self):
        """The prohibition is on silence, not on not knowing.

        A pair the isomorphism search could not separate is a failure while
        nothing says so -- the file would be claiming a distinctness it has not
        shown.  A row that RECORDS the gap in ``dedup_note`` is admitted, the
        way an unproved canonical frame is admitted with ``sk_key_note``:
        refusing it instead would discard a verified factory at exactly the
        widths where new ones are hardest to find.
        """
        hexagon = [[0, 1], [0, 5], [1, 2], [2, 3], [3, 4], [4, 5]]
        triangles = [[0, 1], [0, 2], [1, 2], [3, 4], [3, 5], [4, 5]]
        original = GC.gl_isomorphic
        try:
            GC.gl_isomorphic = lambda *a, **k: None
            silent = [self.unproved(hexagon), self.unproved(triangles)]
            self.assertIn("undecided-class",
                          kinds(VC.duplicate_class_problems(silent)))
            documented = [self.unproved(hexagon), self.unproved(triangles)]
            documented[1]["dedup_note"] = "distinctness was not decided"
            self.assertEqual(VC.duplicate_class_problems(documented), [],
                             "a recorded uncertainty is not a failure")
        finally:
            GC.gl_isomorphic = original

    def test_a_dedup_note_is_judged_on_the_verdicts_of_its_pairs(self):
        """A note is spurious exactly when every pair its row is in was decided.

        Alone in its shape group, or in a group whose searches all finished, a
        row has nothing for its distinctness to be undecided against, so a note
        there says nothing.  The same note on a row one of whose searches ran
        out is the documentation the file requires.
        """
        alone = copy.deepcopy(self.good)
        alone["dedup_note"] = "distinctness was not decided"
        self.assertIn("schema", kinds(VC.duplicate_class_problems([alone])),
                      "no pair at all, so the note says nothing")
        hexagon = [[0, 1], [0, 5], [1, 2], [2, 3], [3, 4], [4, 5]]
        triangles = [[0, 1], [0, 2], [1, 2], [3, 4], [3, 5], [4, 5]]
        decided = [self.unproved(hexagon), self.unproved(triangles)]
        decided[0]["dedup_note"] = "distinctness was not decided"
        self.assertIn("schema", kinds(VC.duplicate_class_problems(decided)),
                      "the search decided the pair, so the note is stale")
        original = GC.gl_isomorphic
        try:
            GC.gl_isomorphic = lambda *a, **k: None
            self.assertEqual(VC.duplicate_class_problems(decided), [],
                             "with the pair undecided the note is real")
        finally:
            GC.gl_isomorphic = original

    def test_an_exhausted_search_never_deadlocks_the_file(self):
        """Demanding a note and refusing it must never both fire.

        Two rows whose proved S_k keys differ may still be one GL(k,2) class,
        so an exhausted search between them is a real open question: it must
        ask for a note, and the note it asks for must then be accepted.
        """
        rows = [copy.deepcopy(self.good), copy.deepcopy(self.good)]
        rows[1]["sk_key"] = [[0, 1]]
        rows[1]["gate"] = "01"
        original = GC.gl_isomorphic
        try:
            GC.gl_isomorphic = lambda *a, **k: None
            self.assertIn("undecided-class",
                          kinds(VC.duplicate_class_problems(rows)))
            rows[1]["dedup_note"] = "distinctness was not decided"
            self.assertEqual(VC.duplicate_class_problems(rows), [])
        finally:
            GC.gl_isomorphic = original

    def test_a_row_citing_no_source_at_all(self):
        """An empty sources list silently disabled the N-vs-sources check."""
        row = copy.deepcopy(self.good)
        row["sources"] = []
        self.assertIn("provenance", kinds(VC.verify_row(row)[1]))

    def test_a_metric_nothing_could_recompute_is_refused(self):
        """Above the cap the minimisations are infeasible -- so the field must
        be null.  The loop handled stored-null-but-recomputes, both-recomputed-
        and-disagree, and both-null-with-no-note, and missed the fourth case:
        a stored NUMBER where the recomputation returns nothing.  That is the
        one place in this file where a published field rested on nothing, and
        it is exactly where no other check could catch it.
        """
        wide = copy.deepcopy(next(r for r in payload()["factories"]
                                  if r["k"] > 6))
        self.assertIsNone(wide["t_count"], "the fixture must be above the cap")
        wide["t_count"] = 999999
        self.assertIn("t_count-mismatch", kinds(VC.verify_row(wide)[1]))
        wide["t_count"] = None
        wide["poly_degree"] = 424242
        self.assertIn("poly_degree-mismatch", kinds(VC.verify_row(wide)[1]))

    def test_a_null_row_count_is_refused_like_a_missing_one(self):
        blob = payload()
        blob["n_classes"] = None
        self.assertIn("header", kinds(VC.header_problems(blob)))

    def test_a_header_missing_its_row_count(self):
        """A wrong n_classes failed; an absent one passed."""
        blob = payload()
        blob.pop("n_classes")
        self.assertIn("header", kinds(VC.header_problems(blob)))

    def test_the_idle_wire_elision_marker_tells_the_truth(self):
        """Exactly six idle wires is not "six and more"."""
        six = VC.structural_problems(1, 8, [[0, 7]])[0][1]
        self.assertNotIn("...", six)
        many = VC.structural_problems(1, 20, [[0, 19]])[0][1]
        self.assertIn("...", many)

    def unproved(self, columns):
        """A readable row for ``columns`` keyed on its fingerprint alone."""
        row = copy.deepcopy(self.good)
        gate = FC.recover_gate(
            FC.rows_over_columns([tuple(c) for c in columns], 6), 6)
        row.update(n=len(columns), k=6, N=6, columns=columns, sk_key=None,
                   sk_canonical_frame=False, sk_key_note="unproved (fixture)",
                   gate=SK.gate_string(gate, 6),
                   sk_fingerprint=SK.sk_fingerprint(6, gate))
        return row

    def test_a_discovery_value_the_header_never_defined(self):
        """merge already refuses it; the re-verifier is the final bar, not less.

        ``discovery`` is what `catalogfile.render_markdown` counts rows BY, so
        an undefined value drops silently out of the rendered split and the
        page stops adding up while the file reports clean.
        """
        payload = payload_with(copy.deepcopy(self.good), discovery="a hunch")
        self.assertIn("discovery-mismatch",
                      kinds(VC.provenance_problems(payload)))

    def test_a_circuit_no_source_published_must_say_it_is_not_theirs(self):
        """A row citing files that hold a DIFFERENT circuit owes an explanation.

        Every source entry records the ``N`` its own file published, and merge
        keeps them equal by construction -- it appends a source for the circuit
        it retains.  A row where they differ is one whose shipped circuit exists
        verbatim in none of the files it credits, so a reader who follows the
        citation finds something else.  That is allowed, and must be said.
        """
        row = copy.deepcopy(self.good)
        for source in row["sources"]:
            source["N"] = row["N"] + 1
        self.assertIn("provenance", kinds(VC.verify_row(row)[1]))
        row["columns_note"] = "one redundant check wire deleted from theirs"
        self.assertEqual(VC.verify_row(row)[1], [],
                         "the note is the only thing that was missing")

    def test_a_note_explaining_a_circuit_nobody_changed_is_refused(self):
        """The sk_key_note rule: a note only where there is something to note."""
        row = copy.deepcopy(self.good)
        row["columns_note"] = "reduced from something"
        self.assertIn("schema", kinds(VC.verify_row(row)[1]))

    def test_wrong_metrics(self):
        self.assertIn("t_count-mismatch", kinds(self.broken(t_count=99)))
        self.assertIn("poly_degree-mismatch", kinds(self.broken(poly_degree=99)))

    def test_wrong_sk_key(self):
        self.assertIn("sk_key-mismatch", kinds(self.broken(sk_key=[[1]])))

    def test_wrong_effective_width(self):
        self.assertIn("effective_width-mismatch",
                      kinds(self.broken(effective_width=99)))


class TestTheTypeGrammarKeepsBoolApart(unittest.TestCase):
    """`catalogfile`'s stated point, tested as a claim rather than assumed.

    Its comment says "``bool`` is deliberately NOT a subtype of int here, which
    is the whole point" -- because ``True == 1`` in Python and not in JSON, so a
    row publishing ``"t_count": true`` compares EQUAL to a recomputed T-count of
    1 and sails through.  Both directions of that distinction could be removed
    with the whole suite green, which made the promise untested.
    """

    def test_a_boolean_is_not_an_integer(self):
        for field in ("n", "k", "N", "d", "level", "t_count", "effective_width"):
            with self.subTest(field=field):
                self.assertTrue(CF.type_problems({field: True}),
                                f"{field}=true must be refused, not read as 1")
                self.assertTrue(CF.type_problems({field: False}))

    def test_an_integer_is_not_a_boolean(self):
        for field in ("d_is_exact", "sk_canonical_frame",
                      "relabelled_into_canonical_frame"):
            with self.subTest(field=field):
                self.assertTrue(CF.type_problems({field: 1}),
                                f"{field}=1 must be refused, not read as true")
                self.assertTrue(CF.type_problems({field: 0}))

    def test_the_honest_values_still_pass(self):
        self.assertEqual(CF.type_problems({"n": 15, "d_is_exact": True}), [])
        self.assertEqual(CF.type_problems({"t_count": None}), [],
                         "t_count is nullable")

    def test_a_boolean_inside_a_list_is_refused_too(self):
        """``sk_key``'s leading 0 written as ``false`` would still compare equal."""
        self.assertTrue(CF.type_problems({"sk_key": [[False]]}))
        self.assertTrue(CF.type_problems({"d_witness": [0, True, 2]}))
        self.assertEqual(CF.type_problems({"sk_key": [[0]],
                                           "d_witness": [0, 1, 2]}), [])


class TestTheTripwiresThemselves(unittest.TestCase):
    """The checks, tested as checks -- not as things that happen to pass.

    Mutation testing showed several of these could be switched off entirely
    with the whole suite still green: the sweep could skip weight 1 or stop a
    weight early, a budget-truncated sweep could count as proof, an overweight
    witness could pass, and the literal cross-implementation tripwires could be
    deleted.  Each is a way for a WRONG catalogue to verify clean, so each is
    now pinned by a test that fails when the check stops working.
    """

    @classmethod
    def setUpClass(cls):
        rows = payload()["factories"]
        cls.good = copy.deepcopy(next(r for r in small_rows(rows)
                                      if r["d_is_exact"] and r["N"] > r["k"]))
        # n = 48 is the smallest shape whose weight-3 sweep a starved budget
        # actually cuts short; the tiny rows finish whatever they are given.
        cls.starvable = copy.deepcopy(next(r for r in rows
                                           if r["d"] >= 4 and r["n"] <= 60))

    def columns(self, row):
        return [list(c) for c in row["columns"]]

    def test_the_sweep_covers_every_weight_below_the_claim(self):
        """A distance inflated by ONE must be caught, not only by two.

        `test_inflated_distance` inflates by 2, which survives a sweep that
        stops a weight early -- so it does not pin the sweep's upper end.
        """
        row = self.good
        problems = VC.confirm_distance(self.columns(row), row["k"], row["N"],
                                       row["d"] + 1, False, None, None,
                                       FC.Budget())
        self.assertIn("distance-inflated", kinds(problems))

    def test_the_sweep_starts_at_weight_one(self):
        """A single column that is undetectable and damaging is a distance-1
        circuit, and a sweep beginning at weight 2 would never see it."""
        columns = [[0], [0, 1], [1]]        # column 0: no check, one output
        problems = VC.confirm_distance(columns, 1, 2, 3, False, None, None,
                                       FC.Budget())
        self.assertIn("distance-inflated", kinds(problems))

    def test_a_witness_of_the_wrong_weight_is_refused(self):
        """``exact`` means a fault AT d; one above it proves a different thing."""
        row = self.good
        spare = next(i for i in range(row["n"]) if i not in row["d_witness"])
        overweight = sorted(row["d_witness"] + [spare])
        problems = VC.confirm_distance(self.columns(row), row["k"], row["N"],
                                       row["d"], True, overweight,
                                       row["d_upper"], FC.Budget())
        self.assertIn("distance-witness", kinds(problems))

    def test_a_sweep_the_budget_cut_short_fails_the_row(self):
        """The failure this file says it exists to prevent.

        An unproved floor published as a floor is exactly what a starved sweep
        produces, so ``distance-unproved`` must fire -- a row is not allowed to
        pass merely because nobody could afford to check it.
        """
        row = self.starvable
        starved = FC.Budget(max_pairs=1, max_triples=1, max_triple_table=1,
                            max_candidates=1)
        problems = VC.confirm_distance(self.columns(row), row["k"], row["N"],
                                       row["d"], row["d_is_exact"],
                                       row["d_witness"], row["d_upper"],
                                       starved)
        self.assertIn("distance-unproved", kinds(problems))
        self.assertEqual(VC.confirm_distance(
            self.columns(row), row["k"], row["N"], row["d"], row["d_is_exact"],
            row["d_witness"], row["d_upper"], FC.Budget()), [],
            "and the same row passes when the sweep can finish")

    def test_the_two_implementations_are_actually_compared(self):
        """`derive` cross-checks the bit-level read-off against the literal one.

        `test_faultcore` pins the two against each other, but nothing asserted
        that the VERIFIER would report it if they disagreed -- so deleting the
        comparison changed no test.
        """
        row = self.good
        real = VC.derived_gate
        try:
            # an empty gate is unequal to any real one, and the bit-level
            # read-off is what the not-level-3 check reads, so this isolates
            # the comparison being tested
            VC.derived_gate = lambda columns, k: frozenset()
            _facts, problems = VC.derive(self.columns(row), row["k"], row["N"])
            self.assertIn("implementation-disagreement", kinds(problems))
        finally:
            VC.derived_gate = real

    def test_the_width_implementations_are_actually_compared(self):
        row = self.good
        real = VC.effective_width
        try:
            VC.effective_width = lambda columns, k, N: 99
            _facts, problems = VC.derive(self.columns(row), row["k"], row["N"])
            self.assertIn("implementation-disagreement", kinds(problems))
        finally:
            VC.effective_width = real


class TestWritingTheFilesSafely(unittest.TestCase):
    """`catalogfile.write` must not be able to destroy what it writes."""

    def test_the_page_may_not_be_written_over_the_catalogue(self):
        with tempfile.TemporaryDirectory() as d:
            same = Path(d) / "catalogue.json"
            with self.assertRaises(ValueError):
                CF.write(payload(), same, same)

    def test_a_failed_render_leaves_both_files_as_they_were(self):
        """They are written to say the same thing; a half-written pair does not.

        The JSON used to be truncated and rewritten BEFORE the page was
        rendered, so a renderer that raised left an updated catalogue beside a
        stale page -- the drift the docstring promises cannot happen.
        """
        with tempfile.TemporaryDirectory() as d:
            js, md = Path(d) / "c.json", Path(d) / "c.md"
            CF.write(payload(), js, md)
            before_json, before_md = js.read_text(), md.read_text()
            real = CF.render_markdown
            try:
                CF.render_markdown = lambda _p: 1 / 0
                with self.assertRaises(ZeroDivisionError):
                    CF.write(payload(), js, md)
            finally:
                CF.render_markdown = real
            self.assertEqual(js.read_text(), before_json)
            self.assertEqual(md.read_text(), before_md)
            self.assertEqual([p for p in Path(d).iterdir()
                              if p.suffix == ".tmp"], [])


class TestMalformedRows(unittest.TestCase):
    """Inputs a verifier must REJECT rather than crash or hang on."""

    @classmethod
    def setUpClass(cls):
        cls.good = copy.deepcopy(small_rows(payload()["factories"])[0])

    def broken(self, **changes):
        row = copy.deepcopy(self.good)
        row.update(changes)
        return VC.verify_row(row)[1]

    def test_a_missing_field_is_a_schema_failure_not_a_key_error(self):
        row = copy.deepcopy(self.good)
        del row["d_is_exact"]
        self.assertIn("schema", kinds(VC.verify_row(row)[1]))

    def test_an_undocumented_field_is_reported(self):
        """A field nobody documented is how a stale value survives a refactor."""
        self.assertIn("schema", kinds(self.broken(notes="hello")))

    def test_an_absurd_register_is_rejected_quickly_not_looped_over(self):
        problems = VC.structural_problems(1, 2 ** 63, [[0], [0, 1]])
        self.assertIn("shape", kinds(problems))

    def test_a_register_larger_than_the_circuit_is_rejected(self):
        """Including an idle wire in the MIDDLE, not only past the end.

        ``N`` is the headline ambient-qubit cost and the tie-break the merge
        tool retains on, so a padded one is a misstatement rather than an
        untidiness.
        """
        self.assertIn("shape",
                      kinds(VC.structural_problems(1, 4, [[0, 1], [0, 3]])))
        self.assertIn("shape",
                      kinds(VC.structural_problems(1, 9, [[0, 1], [0, 2]])))

    def test_non_integers_are_rejected(self):
        self.assertIn("schema", kinds(VC.structural_problems("1", 5, [[0]])))
        self.assertIn("schema", kinds(VC.structural_problems(1, 5, "columns")))
        self.assertIn("schema", kinds(VC.structural_problems(1, 5, [[0], []])))
        self.assertIn("schema", kinds(VC.structural_problems(1, 5, [[0.5]])))

    def test_a_row_that_is_not_an_object(self):
        self.assertIn("schema", kinds(VC.verify_row(["not", "a", "row"])[1]))


class TestDuplicateClasses(unittest.TestCase):
    """Both passes of the file-level uniqueness check."""

    @classmethod
    def setUpClass(cls):
        cls.rows = small_rows(payload()["factories"], limit=3)

    def test_the_same_row_twice_is_caught(self):
        problems = VC.duplicate_class_problems(self.rows + [self.rows[0]])
        self.assertIn("duplicate-class", kinds(problems))
        # once by the dedup key, once by the explicit isomorphism test: the key
        # is a hash and the isomorphism is the decision procedure, and the
        # claim rests on the second one
        self.assertEqual(len(problems), 2)

    def test_a_relabelled_copy_is_caught_by_the_isomorphism_test(self):
        """Two labellings of one class, keyed apart, caught by the real test.

        Constructed so the dedup key CANNOT see it: the copy's ``sk_key`` is
        blanked the way the six wide rows' keys are, which drops it onto the
        fingerprint -- and then only `skcanon.sk_isomorphic` can still tell that
        it is the same class.
        """
        twin = copy.deepcopy(self.rows[0])
        twin["sk_key"] = None
        problems = VC.duplicate_class_problems([self.rows[0], twin])
        self.assertIn("duplicate-class", kinds(problems))

    def test_distinct_classes_are_left_alone(self):
        self.assertEqual(VC.duplicate_class_problems(self.rows), [])

    def test_the_same_gate_at_another_distance_is_another_class(self):
        """Distance is part of the class, so a higher-distance circuit for a
        gate the file already holds is never reported as its duplicate."""
        twin = copy.deepcopy(self.rows[0])
        twin["d"] = self.rows[0]["d"] + 1
        self.assertEqual(VC.duplicate_class_problems([self.rows[0], twin]), [])

    def test_a_copy_in_another_cnot_frame_is_the_same_class(self):
        """The case the S_k key cannot see at all, caught by the GL(k,2) test.

        Built by replacing output row 0 with row 0 XOR row 1 -- a CNOT on the
        outputs.  It is still a factory with the same distance, and it deposits
        a DIFFERENT monomial set (so no permutation relates the two), yet it is
        the same gate up to an invertible change of the output basis.
        """
        base = next(r for r in payload()["factories"]
                    if r["k"] == 2 and r["gate"] == "0+1" and r["n"] <= SMALL_N)
        moved = [sorted(({1} if (0 in c) != (1 in c) else set())
                        | {q for q in c if q != 1}) for c in base["columns"]]
        twin = copy.deepcopy(base)
        twin.update(columns=moved, sk_key=None)
        left = VC.row_monomials(base)
        right = VC.row_monomials(twin)
        self.assertNotEqual(set(left), set(right),
                            "the fixture must change the monomial set")
        self.assertIn("duplicate-class",
                      kinds(VC.duplicate_class_problems([base, twin])))


class TestProvenanceLabels(unittest.TestCase):
    """The one published field a row cannot check alone.

    `strongest_claim` is the sentence `MASTER_CATALOG.md` prints beside a row to
    say how strong its claim is, and it is the header's definition of the row's
    strongest regime -- so it is derivable, from the row's regime NAMES plus the
    header, and nothing derivable is left uncompared.  It needs both halves,
    which is why it is a file-level check and not part of `verify_row`.
    """

    def setUp(self):
        full = payload()
        self.payload = {**full, "factories": small_rows(full["factories"],
                                                        limit=3)}

    def test_the_shipped_catalogue_resolves(self):
        self.assertEqual(VC.provenance_problems(payload()), [])

    def test_a_regime_the_header_does_not_define_is_caught(self):
        """A claim the file cannot explain, which is what registering does."""
        self.payload["factories"][0]["regimes"] = ["a corpus nobody has"]
        self.assertIn("regime-mismatch",
                      kinds(VC.provenance_problems(self.payload)))

    def test_a_stale_strongest_claim_is_caught(self):
        """The mutation that matters: a search witness reading as classified."""
        header = list(self.payload["regimes"].values())
        row = self.payload["factories"][0]
        row["strongest_claim"] = next(claim for claim in header
                                      if claim != row["strongest_claim"])
        problems = VC.provenance_problems(self.payload)
        self.assertIn("strongest_claim-mismatch", kinds(problems))

    def test_regimes_listed_out_of_the_headers_order_are_caught(self):
        """``regimes[0]`` is only the strongest claim if the order holds."""
        row = next(r for r in self.payload["factories"] if len(r["regimes"]) > 1)
        row["regimes"] = list(reversed(row["regimes"]))
        self.assertIn("regime-mismatch",
                      kinds(VC.provenance_problems(self.payload)))

    def test_a_row_with_no_regime_at_all_is_caught(self):
        self.payload["factories"][0]["regimes"] = []
        self.assertIn("regime-mismatch",
                      kinds(VC.provenance_problems(self.payload)))

    def test_a_header_with_no_regimes_is_caught_once(self):
        """Not 444 identical complaints: the header is one thing being wrong."""
        self.payload["regimes"] = {}
        problems = VC.provenance_problems(self.payload)
        self.assertEqual(kinds(problems), {"regime-header"})
        self.assertEqual(len(problems), 1)


class TestFileLevelRobustness(unittest.TestCase):
    """A rejected row must stay a REJECTION all the way to the exit status.

    The failure mode these pin down: `verify_row` correctly diagnoses a
    malformed row, and then the file-level passes -- which run over ALL rows --
    re-derive a gate from the very columns that were just refused and crash.
    A verifier that crashes on input it already rejected has not finished
    rejecting it, and a crash reports one problem where the run had found many.
    """

    def test_row_monomials_refuses_what_it_cannot_index(self):
        self.assertIsNone(VC.row_monomials(
            {"k": 1, "N": 2, "columns": [[7]]}))
        self.assertIsNone(VC.row_monomials(
            {"k": 1, "N": 2, "columns": "garbage"}))

    def test_duplicate_detection_skips_rows_with_no_readable_circuit(self):
        sane = {"n": 3, "k": 1, "N": 2, "sk_key": [[0]], "sk_fingerprint": "x",
                "gate": "0", "columns": [[0, 1], [0], [1]]}
        mangled = {"n": 3, "k": 1, "N": 2, "sk_key": None,
                   "sk_fingerprint": "y", "gate": "?", "columns": [[9]]}
        self.assertEqual(
            VC.duplicate_class_problems([sane, mangled, "not a row"]), [])

    def test_a_malformed_row_fails_the_catalogue_without_crashing_it(self):
        """End to end: the whole-file entry point, wire label off the register."""
        payload = CF.load()
        rows = [copy.deepcopy(payload["factories"][0]) for _ in range(2)]
        rows[1]["columns"] = [[rows[1]["N"] + 3]]
        broken = {**{key: payload[key] for key in CF.HEADER_KEYS},
                  "n_classes": 2, "factories": rows}
        failures, checked = VC.verify_catalog(broken, verbose=False)
        self.assertEqual(checked, 2)
        self.assertTrue(any(index == 2 for index, _row, _p in failures))

    def test_duplicate_detection_skips_rows_with_malformed_sk_key(self):
        """A readable circuit under an untyped key: the pass indexed
        ``sk_key`` as nested lists and turned the row's recorded field-type
        failure into a TypeError."""
        sane = {"n": 3, "k": 1, "N": 2, "sk_key": [[0]], "sk_fingerprint": "x",
                "gate": "0", "columns": [[0, 1], [0], [1]]}
        for bad_key in (True, [1, 2, 3], "0"):
            mangled = {**sane, "sk_key": bad_key, "sk_fingerprint": "y"}
            with self.subTest(sk_key=bad_key):
                self.assertEqual(
                    VC.duplicate_class_problems([sane, mangled]), [])

    def test_provenance_survives_unhashable_regime_entries(self):
        """``regimes: [["x"]]`` failed row typing and then crashed the
        membership test with an unhashable list."""
        payload = CF.load()
        broken = {**{key: payload[key] for key in CF.HEADER_KEYS},
                  "n_classes": 1,
                  "factories": [{"regimes": [["not-a-string"]]}]}
        self.assertEqual(VC.provenance_problems(broken), [])


    def test_a_non_object_row_fails_without_crashing(self):
        payload = CF.load()
        broken = {**{key: payload[key] for key in CF.HEADER_KEYS},
                  "n_classes": 1, "factories": ["not a row"]}
        failures, checked = VC.verify_catalog(broken, verbose=False)
        self.assertEqual(checked, 1)
        self.assertEqual(len(failures), 1)


class TestHeaderProblems(unittest.TestCase):
    """`HEADER_KEYS` was a promise with no test; now it is a check."""

    def setUp(self):
        payload = CF.load()
        self.payload = {**{key: payload[key] for key in CF.HEADER_KEYS},
                        "n_classes": 1,
                        "factories": [payload["factories"][0]]}

    def test_the_shipped_header_passes(self):
        self.assertEqual(VC.header_problems(CF.load()), [])

    def test_a_missing_header_key_is_named(self):
        del self.payload["caveat"]
        self.assertTrue(any("caveat" in detail
                            for _k, detail in VC.header_problems(self.payload)))

    def test_a_boolean_row_count_is_not_a_count(self):
        """``True == 1`` in Python and not in JSON, so a boolean n_classes
        compared EQUAL to a one-row file and passed."""
        self.payload["n_classes"] = True
        self.assertTrue(any("n_classes" in detail
                            for _k, detail in VC.header_problems(self.payload)))

    def test_a_header_map_must_map_names_to_sentences(self):
        self.payload["regimes"] = {"a regime": 3}
        self.assertTrue(any("regimes" in detail
                            for _k, detail in VC.header_problems(self.payload)))

    def test_a_stale_row_count_is_caught(self):
        """``n_classes`` is the one header value a reader can check, so it is
        checked: a count that disagrees with the rows is a stale published
        number, the exact species every other check here hunts."""
        self.payload["n_classes"] = 425
        self.assertTrue(any("n_classes" in detail
                            for _k, detail in VC.header_problems(self.payload)))


class TestCitations(unittest.TestCase):
    """Every row credits a work, and every credit resolves in the header."""

    def setUp(self):
        self.payload = payload_with(CF.load()["factories"][0])

    def test_the_shipped_catalogue_passes(self):
        self.assertEqual(VC.citation_problems(CF.load()), [])

    def test_an_unknown_key_is_named(self):
        self.payload["factories"][0]["citations"] = ["nobody2099"]
        problems = VC.citation_problems(self.payload)
        self.assertIn("citation-mismatch", kinds(problems))
        self.assertTrue(any("nobody2099" in d for _k, d in problems))

    def test_a_row_crediting_nothing(self):
        self.payload["factories"][0]["citations"] = []
        self.assertIn("citation-mismatch",
                      kinds(VC.citation_problems(self.payload)))

    def test_a_work_credited_twice(self):
        key = next(iter(self.payload["references"]))
        self.payload["factories"][0]["citations"] = [key, key]
        self.assertIn("citation-mismatch",
                      kinds(VC.citation_problems(self.payload)))

    def test_no_references_map_at_all(self):
        del self.payload["references"]
        self.assertIn("citation-header",
                      kinds(VC.citation_problems(self.payload)))

    def test_a_reference_entry_must_have_a_label_and_a_line(self):
        key = next(iter(self.payload["references"]))
        self.payload["references"][key] = {"short": "X"}
        self.assertTrue(any("references" in detail
                            for _k, detail in VC.header_problems(self.payload)))

    def test_citations_are_typed_like_every_other_field(self):
        row = copy.deepcopy(CF.load()["factories"][0])
        row["citations"] = "jain2026symmetry"
        self.assertIn("field-type", kinds(VC.verify_row(row)[1]))


class TestSourceEntrySchema(unittest.TestCase):
    """``sources: [dict]`` admitted ``[{}]``, and the renderer then read four
    keys out of it unconditionally -- a KeyError three tools after every
    mathematical check had passed.  The inner keys are typed now."""

    GOOD = {"regime": "r", "label": "l", "provenance": "p", "file": "f",
            "N": 5, "d": 3, "d_is_exact": True, "origin": None}

    def test_the_shipped_entries_all_pass(self):
        for row in CF.load()["factories"]:
            for entry in row["sources"]:
                self.assertIsNone(CF._source_entry_problem(entry))

    def test_an_empty_entry_is_named_with_its_position(self):
        problems = CF.type_problems({"sources": [dict(self.GOOD), {}]})
        self.assertTrue(any("sources[1]" in detail
                            for _kind, detail in problems))

    def test_notes_may_be_a_string_or_lines_and_nothing_else(self):
        self.assertIsNone(
            CF._source_entry_problem({**self.GOOD, "notes": "one line"}))
        self.assertIsNone(
            CF._source_entry_problem({**self.GOOD, "notes": ["a", "b"]}))
        self.assertIsNotNone(
            CF._source_entry_problem({**self.GOOD, "notes": 7}))

    def test_an_undocumented_inner_key_is_refused(self):
        self.assertIsNotNone(
            CF._source_entry_problem({**self.GOOD, "surprise": 1}))


class TestExactDistanceLiteral(unittest.TestCase):
    def test_masks_are_bitsets_not_sums(self):
        """``[[0, 0]]`` is a rotation on wire 0 and a weight-1 fault; the old
        ``sum`` carried the repeat into bit 1 and reported no fault at all."""
        self.assertEqual(VC.exact_distance([[0, 0]], 1), 1)
        self.assertEqual(VC.exact_distance([[0, 0]], 1),
                         VC.exact_distance([[0]], 1))




if __name__ == "__main__":
    unittest.main()
