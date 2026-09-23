"""`faultcore` against the routines it was written to replace.

`faultcore` exists because the reference implementations do not run at the scale
the two new directories reach: `C(162, 3)` monomials for a gate read-off,
`C(1023, 4)` subsets for a distance.  It answers the same questions with
transposed bitmasks and meet-in-the-middle joins, which is a different algorithm
and therefore a different set of ways to be wrong.

So it is pinned, on every circuit small enough for both to run, against:

  * `verify_catalog.derived_gate` / `.exact_distance` / `.effective_width`
    -- the literal enumerations, kept beside the verifier for exactly this
    purpose;
  * `factorylib.verification.verify` from the repository root, which shares no
    code with any search or catalogue here.

Plus the properties that do not need a second implementation: a witness has to
be a genuine harmful fault, and a fault below a proved floor has to not exist.
"""
import itertools
import json
import random
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE.parent
REPO = CATALOGUE.parent
sys.path.insert(0, str(CATALOGUE))
sys.path.insert(0, str(REPO))

import faultcore as FC                                          # noqa: E402
import verify_catalog as B                                      # noqa: E402
from factorylib.verification import verify as reference_verify  # noqa: E402

MASTER = CATALOGUE / "master_catalog.json"


def small_rows(limit_n=70, limit_k=8):
    """Catalogue rows both implementations can run on."""
    if not MASTER.exists():
        return []
    rows = json.loads(MASTER.read_text())["factories"]
    return [r for r in rows if r["n"] <= limit_n and r["k"] <= limit_k]


class TestAgainstTheReferenceImplementations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = small_rows()
        if not cls.rows:
            raise unittest.SkipTest("master_catalog.json is missing")

    def test_gate_read_off_matches_the_literal_enumeration(self):
        for row in self.rows:
            columns = [tuple(sorted(set(c))) for c in row["columns"]]
            k, N = row["k"], row["N"]
            with self.subTest(params=(row["n"], k, row["d"])):
                rows_ = FC.rows_over_columns(columns, N)
                self.assertEqual(set(FC.recover_gate(rows_, k)),
                                 set(B.derived_gate(columns, k)))

    def test_width_matches_the_literal_enumeration(self):
        for row in self.rows:
            columns = [tuple(sorted(set(c))) for c in row["columns"]]
            k, N = row["k"], row["N"]
            with self.subTest(params=(row["n"], k, row["d"])):
                rows_ = FC.rows_over_columns(columns, N)
                self.assertEqual(FC.output_report(rows_, k, N)["effective_width"],
                                 B.effective_width(columns, k, N))

    def test_distance_matches_both_references(self):
        """Exhaustive subset enumeration, and the standalone verifier."""
        for row in self.rows:
            columns = [tuple(sorted(set(c))) for c in row["columns"]]
            k, N = row["k"], row["N"]
            with self.subTest(params=(row["n"], k, row["d"])):
                report = FC.distance_report(columns, k, N)
                settled = (report["d_exact"] if report["d_exact"] is not None
                           else report["d_at_least"])
                literal = B.exact_distance(columns, k, cap=4)   # 5 means ">4"
                gate = FC.recover_gate(FC.rows_over_columns(columns, N), k)
                parity_ok, reference = reference_verify(
                    k, N, [frozenset(c) for c in columns], set(gate), dmax=4)
                self.assertTrue(parity_ok)
                floor = 5 if isinstance(reference, str) else reference
                if literal <= 4:
                    self.assertEqual(settled, literal)
                    self.assertEqual(floor, literal)
                else:
                    self.assertGreaterEqual(settled, 5)
                    self.assertEqual(floor, 5)

    def test_a_witness_is_a_genuine_harmful_fault(self):
        """The one property a distance claim rests on, checked directly.

        `d_exact` is only ever set when a witness was produced, so re-checking
        every witness -- syndromes XOR to zero, output parts do not -- verifies
        the presence half of every pinned distance in the catalogue without
        trusting a single line of the search that found it.
        """
        rows = json.loads(MASTER.read_text())["factories"]
        checked = 0
        for row in rows:
            if not row.get("d_witness"):
                continue
            columns = [tuple(sorted(set(c))) for c in row["columns"]]
            k = row["k"]
            syndrome = output = 0
            for index in row["d_witness"]:
                for q in columns[index]:
                    if q < k:
                        output ^= 1 << q
                    else:
                        syndrome ^= 1 << (q - k)
            with self.subTest(params=(row["n"], k, row["d"])):
                self.assertEqual(len(set(row["d_witness"])), len(row["d_witness"]))
                # The witness is the `d_upper` fault.  On an exact row
                # `d_upper == d`; on a floor row it may sit strictly above the
                # proved floor (`[[512,39,>=6]]` carries a weight-8 witness).
                self.assertEqual(len(row["d_witness"]),
                                 row["d_upper"] if row.get("d_upper") is not None
                                 else row["d"],
                                 "the witness must have exactly d_upper faults")
                self.assertEqual(syndrome, 0, "the syndromes must cancel")
                self.assertNotEqual(output, 0, "the output action must not")
            checked += 1
        self.assertGreater(checked, 0, "no witnesses to check")


class TestTheScanItself(unittest.TestCase):
    """Properties of `scan_weight` that hold on any circuit at all."""

    def _random_circuit(self, rng, n, N, k):
        columns = set()
        while len(columns) < n:
            support = tuple(sorted(rng.sample(range(N), rng.randint(1, N))))
            columns.add(support)
        return sorted(columns)

    def test_counts_match_brute_force_enumeration(self):
        """`A_d` at every weight, against `C(n, w)` subsets.

        The scans are meet-in-the-middle, so each harmful fault is visited
        several times and the tally is divided by how many.  That divisor is the
        easiest thing in the module to get wrong and the hardest to notice, so
        it is checked against the definition on random circuits rather than only
        on the well-behaved catalogue.
        """
        rng = random.Random(4242)
        for trial in range(12):
            N, k = rng.randint(5, 7), rng.randint(1, 3)
            n = rng.randint(6, 14)
            columns = self._random_circuit(rng, n, N, k)
            circuit = FC.Circuit(columns, k, N)
            masks = [sum(1 << q for q in c) for c in columns]
            outm = (1 << k) - 1
            for weight in range(1, 7):
                expected = 0
                for support in itertools.combinations(range(len(masks)), weight):
                    value = 0
                    for index in support:
                        value ^= masks[index]
                    if value and not value & ~outm:
                        expected += 1
                status, witness, count = FC.scan_weight(circuit, weight,
                                                        want_count=True)
                with self.subTest(trial=trial, weight=weight):
                    if status == "skipped":
                        continue
                    self.assertEqual(count, expected)
                    self.assertEqual(status, "found" if expected else "clean")
                    if witness is not None:
                        self.assertTrue(circuit.harmful(witness))

    def test_a_repeated_column_is_a_weight_two_fault(self):
        """The check that stops a distance-2 circuit calling itself distance 5."""
        columns = [(0, 2), (1, 2), (0, 2)]
        circuit = FC.Circuit(columns, 2, 3)
        status, witness, _count = FC.scan_weight(circuit, 2)
        self.assertEqual(status, "found")
        self.assertTrue(circuit.harmful(witness))

    def test_folding_wide_syndromes_has_no_false_negatives(self):
        """Above r = 64 syndromes are folded linearly; absence must survive it.

        A fold can only merge distinct syndromes, never split equal ones, so a
        fault set that truly cancels still cancels after folding.  That is the
        direction every proof of absence depends on, so it is tested rather than
        argued: a circuit wide enough to trigger the fold must report the same
        distance as the same circuit with its checks packed into 64 bits.
        """
        rng = random.Random(99)
        k, r = 2, 70
        columns = set()
        while len(columns) < 12:
            support = [rng.randrange(k)] + rng.sample(range(k, k + r),
                                                      rng.randint(1, 4))
            columns.add(tuple(sorted(set(support))))
        wide = sorted(columns)
        used = sorted({q for c in wide for c in [c] for q in c})
        remap = {q: i for i, q in enumerate(used)}
        narrow = sorted(tuple(sorted(remap[q] for q in c)) for c in wide)
        wide_report = FC.distance_report(wide, k, max(max(c) for c in wide) + 1)
        narrow_report = FC.distance_report(
            narrow, k, max(max(c) for c in narrow) + 1)
        self.assertEqual(wide_report["d_at_least"], narrow_report["d_at_least"])
        self.assertEqual(wide_report["d_exact"], narrow_report["d_exact"])


class TestTheTripwiresThemselves(unittest.TestCase):
    """Tests aimed at the checks, not at the answers they usually give.

    Mutation testing found these branches could be broken -- the fold made
    non-linear, the contamination sweep made to skip the first or last check
    wire, a budget-truncated sweep made to count as proof -- with the whole
    suite still green.  A check nothing would notice the loss of is not a check.
    """

    def test_the_fold_finds_a_fault_that_only_cancels_after_folding(self):
        """The r > 64 path, exercised by a fault instead of a comparison.

        The wide-vs-narrow test below compares two reports; when neither circuit
        has a low-weight fault it compares two "nothing found"s, and a fold that
        had stopped being linear would pass it.  So this plants one: three
        columns whose CHECK supports are ``A``, ``B`` and ``A xor B``, which
        cancel exactly, while only the first touches an output -- an undetectable
        weight-3 fault that damages.  Replacing the fold's ``^=`` with ``|=``
        makes the scan report weights 1-6 proven clean on this circuit.
        """
        k, N = 2, 72                            # r = 70, comfortably over 64
        A, B, AB = (2, 3), (4, 5), (2, 3, 4, 5)
        planted = [(0,) + A, B, AB]
        filler = [(1, 6 + i, 7 + i) for i in range(0, 40, 2)]
        columns = sorted(set(planted + filler))
        self.assertGreater(N - k, 64, "the fixture must reach the folded path")
        report = FC.distance_report([list(c) for c in columns], k, N)
        self.assertEqual(report["scanned"]["3"], "found")
        self.assertEqual(report["d_exact"], 3)
        witness = sorted(report["witness"])
        self.assertEqual(witness, sorted(columns.index(c) for c in planted))
        syn, out = FC._syndrome_output([list(c) for c in columns], k)
        cancels = harm = 0
        for i in witness:
            cancels ^= syn[i]
            harm ^= out[i]
        self.assertEqual(cancels, 0, "the witness must be undetectable")
        self.assertNotEqual(harm, 0, "and damaging")

    def test_contamination_matches_a_literal_sweep_over_every_boundary(self):
        """The bit-level sweep against the definition, at tiny N.

        `check_contamination` walks ``i >= k`` and ``range(i + 1, N)``; every
        one of those bounds can be moved by one and still pass a suite whose
        fixtures contaminate comfortably-interior wires.  This compares it with
        a literal enumeration on circuits small enough that the FIRST check wire
        and the LAST wire are the only ones there are.
        """
        rng = random.Random(20260901)
        for trial in range(400):
            N = rng.randint(2, 6)
            k = rng.randint(1, N - 1)
            n = rng.randint(1, 8)
            columns = sorted({tuple(sorted(rng.sample(range(N),
                                                      rng.randint(1, N))))
                              for _ in range(n)})
            rows = FC.rows_over_columns(columns, N)
            literal = set()
            for size in (1, 2, 3):
                for combo in itertools.combinations(range(N), size):
                    if max(combo) < k:
                        continue            # a pure OUTPUT monomial is the gate
                    overlap = rows[combo[0]]
                    for q in combo[1:]:
                        overlap &= rows[q]
                    if bin(overlap).count("1") % 2:
                        literal.add(combo)
            got = set(FC.check_contamination(rows, k, N, limit=10 ** 6))
            with self.subTest(trial=trial, k=k, N=N, columns=columns):
                self.assertEqual(got, literal)

    def test_a_starved_sweep_never_claims_a_distance_it_did_not_prove(self):
        """A budget that bites must produce a floor, never an exact value.

        Two mutations survived here: counting a skipped weight as proven clean,
        and accepting a witness ABOVE the floor as the exact distance.  Both
        publish a distance no sweep established, which is the single failure
        this module exists to make impossible.
        """
        rng = random.Random(4242)
        starved = FC.Budget(max_pairs=1, max_triples=1, max_triple_table=1,
                            max_candidates=1, witness_samples=50)
        for trial in range(40):
            k, N = 2, rng.randint(6, 10)
            columns = sorted({tuple(sorted(rng.sample(range(N),
                                                      rng.randint(1, 4))))
                              for _ in range(rng.randint(8, 16))})
            report = FC.distance_report([list(c) for c in columns], k, N,
                                        budget=starved)
            statuses = report["scanned"]
            skipped = [int(w) for w, s in statuses.items() if s == "skipped"]
            with self.subTest(trial=trial):
                if skipped:
                    self.assertIsNone(report["d_exact"],
                                      "a sweep the budget cut short proves "
                                      "nothing, so nothing may be exact")
                    self.assertLessEqual(report["d_at_least"], min(skipped),
                                         "the floor may not climb past the "
                                         "last weight actually swept")

    def test_a_sampled_witness_is_always_a_real_fault_of_the_asked_weight(self):
        """`sample_witness` returns a witness or nothing -- never a near miss.

        Above n = 260 the recount that would catch a malformed witness is itself
        skipped, so a witness of the wrong weight would publish a distance one
        below the truth in silence.
        """
        rng = random.Random(7)
        for trial in range(60):
            k, N = 2, rng.randint(5, 9)
            columns = sorted({tuple(sorted(rng.sample(range(N),
                                                      rng.randint(1, 4))))
                              for _ in range(rng.randint(10, 18))})
            circuit = FC.Circuit([list(c) for c in columns], k, N, FC.Budget())
            for weight in (2, 3, 4):
                found = FC.sample_witness(circuit, weight)
                if found is None:
                    continue
                with self.subTest(trial=trial, weight=weight):
                    self.assertEqual(len(set(found)), weight,
                                     "exactly w distinct columns")
                    self.assertTrue(circuit.harmful(found),
                                    "and genuinely harmful")

    def test_a_small_circuit_is_never_skipped_below_weight_seven(self):
        """The feasibility guards must not refuse work they can do.

        `test_counts_match_brute_force` tolerates "skipped", so inverting a
        feasibility comparison -- silently declining every weight-6 sweep -- left
        it green while five d = 7 rows rest on a clean weight-6 sweep.
        """
        rng = random.Random(11)
        for trial in range(25):
            k, N = 2, rng.randint(5, 8)
            columns = sorted({tuple(sorted(rng.sample(range(N),
                                                      rng.randint(1, 3))))
                              for _ in range(rng.randint(8, 13))})
            circuit = FC.Circuit([list(c) for c in columns], k, N, FC.Budget())
            for weight in range(1, 7):
                status, _count, _witness = FC.scan_weight(circuit, weight)
                with self.subTest(trial=trial, weight=weight):
                    self.assertNotEqual(status, "skipped",
                                        "a default budget must reach weight "
                                        f"{weight} on n={len(columns)}")


class TestOutputStructure(unittest.TestCase):
    """The pseudo-output check, on circuits built to fail it."""

    def test_a_duplicated_output_row_is_caught(self):
        # outputs 0 and 1 have identical rows: one logical qubit, twice
        columns = [(0, 1, 2), (0, 1, 3), (2, 3)]
        rows = FC.rows_over_columns(columns, 4)
        report = FC.output_report(rows, 2, 4)
        self.assertFalse(report["independent"])
        self.assertIn([0, 1], report["duplicate_rows"])

    def test_an_output_equal_to_another_plus_a_check_is_caught(self):
        """Outputs 0 and 1 differ by the check row: one logical qubit, two names.

        Rows are bitmasks over COLUMN indices, so with columns
        ``{0,1}, {1,2}`` output 0 sits in column 0 only, output 1 in both, and
        check 2 in column 1 -- which is exactly ``a_1 = a_0 + h``.
        """
        columns = [(0, 1), (1, 2)]
        rows = FC.rows_over_columns(columns, 3)
        self.assertEqual(rows[1], rows[0] ^ rows[2])
        report = FC.output_report(rows, 2, 3)
        self.assertFalse(report["independent"])
        self.assertEqual(report["equal_mod_checks"], [[0, 1]])
        self.assertEqual(report["duplicate_rows"], [],
                         "they are equal mod the checks, not identical")

    def test_an_output_inside_the_check_span_is_caught(self):
        columns = [(0, 1), (1,)]
        rows = FC.rows_over_columns(columns, 2)
        report = FC.output_report(rows, 1, 2)
        # output row 0 is not in the span of check row 1 here, so this must PASS
        self.assertTrue(report["independent"])
        columns = [(0, 1)]
        rows = FC.rows_over_columns(columns, 2)
        report = FC.output_report(rows, 1, 2)
        self.assertFalse(report["independent"])
        self.assertEqual(report["in_check_span"], [0])

    def test_an_independent_pair_passes(self):
        """The negative control: two outputs that really are two qubits."""
        columns = [(0, 2), (1, 2), (2,), (3,)]
        rows = FC.rows_over_columns(columns, 4)
        report = FC.output_report(rows, 2, 4)
        self.assertTrue(report["independent"])
        self.assertEqual(report["effective_width"], 2)
        self.assertEqual(report["duplicate_rows"], [])
        self.assertEqual(report["equal_mod_checks"], [])


class TestCheckStructure(unittest.TestCase):
    """The redundant-check test, on rows built to fail it.

    Rows are bitmasks over COLUMN indices, so these are written as columns and
    the resulting rows asserted, the same way the pseudo-output tests above are.
    """

    def test_a_duplicated_check_row_is_caught(self):
        """Two check wires touched by exactly the same columns."""
        columns = [(0, 1, 2), (0, 1, 2)][:1] + [(0, 1, 2), (0,)]
        rows = FC.rows_over_columns(columns, 3)
        self.assertEqual(rows[1], rows[2], "the fixture must duplicate the row")
        self.assertEqual(FC.redundant_checks(rows, 1, 3), [2],
                         "the LATER of the two is the redundant one")

    def test_a_check_row_in_the_span_of_the_others_is_caught(self):
        """Check 3's row is the XOR of check 1's and check 2's.

        With columns ``{0,1}, {0,2}`` and wire 3 in both, row 3 is the whole
        column set and rows 1 and 2 are one column each -- so 3 decides nothing
        1 and 2 have not already decided.
        """
        columns = [(0, 1, 3), (0, 2, 3)]
        rows = FC.rows_over_columns(columns, 4)
        self.assertEqual(rows[3], rows[1] ^ rows[2])
        self.assertEqual(FC.redundant_checks(rows, 1, 4), [3])

    def test_independent_checks_pass(self):
        """The negative control: checks that really are separate syndrome bits."""
        columns = [(0, 1), (0, 2), (1, 2)]
        rows = FC.rows_over_columns(columns, 3)
        self.assertEqual(FC.redundant_checks(rows, 1, 3), [])

    def test_a_dependent_OUTPUT_row_is_not_reported_here(self):
        """The two tests are twins, not duplicates: this one reads k..N-1 only.

        A dependent output is a pseudo-output and `output_report`'s business;
        reporting it here as well would make one defect produce two verdicts.

        The fixture has to be one where the output really IS dependent, or the
        test passes for every implementation and guards nothing.  One column on
        two wires gives both rows the same single bit, so output 0 lies in the
        check span -- `output_report` says so below -- while the one check row
        is nonzero and independent, so the correct answer here is the empty
        list.  An implementation that swept ``0..N-1`` instead of ``k..N-1``
        would find wire 1 already spanned by wire 0 and report ``[1]``.
        """
        columns = [(0, 1)]
        rows = FC.rows_over_columns(columns, 2)
        self.assertEqual(FC.output_report(rows, 1, 2)["in_check_span"], [0],
                         "the fixture must actually have a dependent output")
        self.assertEqual(FC.redundant_checks(rows, 1, 2), [])


class TestPrimitiveContracts(unittest.TestCase):
    """The raw-input promises of the public primitives, checked as promises.

    Every one of these was once a latent trap found by review, not by a
    failure: valid catalogue rows are normalised before they reach the
    primitives, so a wrong answer on raw input had no caller to bite -- until
    the next script reuses the helper without the same discipline.
    """

    def test_column_masks_is_a_bitset_not_a_sum(self):
        """A repeated wire must stay one bit; the old ``sum`` carried it.

        ``[[0, 0]]`` under addition became bit 1 -- a rotation on a wire the
        column never touches, a silently different circuit.
        """
        self.assertEqual(FC.column_masks([[0, 0]], 2), [0b01])
        self.assertEqual(FC.column_masks([[0, 1], [1]], 2), [0b11, 0b10])

    def test_the_mask_builders_refuse_labels_they_cannot_mean(self):
        """Negative indexes wrap in Python and booleans index as 0/1; both are
        a different circuit, not an error, unless the primitive refuses."""
        for bad in ([[-1]], [[4]], [[True]]):
            with self.subTest(columns=bad):
                with self.assertRaises(ValueError):
                    FC.column_masks(bad, 4)
                with self.assertRaises(ValueError):
                    FC.rows_over_columns(bad, 4)

    def test_a_circuit_refuses_wires_outside_its_register(self):
        """The scans fold ``q - k`` into a syndrome bit; an out-of-range wire
        would land in the WRONG bit and verify a circuit nobody wrote."""
        with self.assertRaises(ValueError):
            FC.Circuit([(0, 5)], 1, 3)
        with self.assertRaises(ValueError):
            FC.Circuit([(-1, 2)], 1, 3)

    def test_check_contamination_refuses_a_limit_below_one(self):
        """``limit=0`` would return [] for clean and contaminated alike -- the
        one conflation this module exists to prevent -- and the old code
        appended before testing the cap, so it held for no small limit."""
        rows = FC.rows_over_columns([(0, 1)], 2)
        with self.assertRaises(ValueError):
            FC.check_contamination(rows, 1, 2, limit=0)
        self.assertEqual(len(FC.check_contamination(rows, 1, 2, limit=1)), 1)

    def test_the_weight_two_scan_honours_the_candidate_budget(self):
        """Degenerate input collapses the syndrome buckets and the pair loop is
        C(n, 2); the budget that bounds every other weight bounds this one."""
        columns = [(0, 2), (1, 2)]              # equal syndromes: one candidate
        starved = FC.Circuit(columns, 2, 3, FC.Budget(max_candidates=0))
        self.assertEqual(FC.scan_weight(starved, 2), ("skipped", None, None))
        fed = FC.Circuit(columns, 2, 3)
        self.assertEqual(FC.scan_weight(fed, 2)[0], "found")

    def test_distance_report_takes_no_claim(self):
        """The sweep is claim-independent, and the signature must say so: a
        ``claimed`` parameter that read as steering steered nothing."""
        import inspect
        self.assertNotIn("claimed",
                         inspect.signature(FC.distance_report).parameters)


    def test_a_circuit_refuses_boolean_and_mixed_labels(self):
        """``sorted`` reads ``True`` as 1, so an ends-only check let
        ``[0, True]`` through as wires 0 and 1 -- and ``[0, "1"]`` crashed
        inside ``sorted`` with a TypeError instead of being refused.  Every
        raw label is validated before normalisation touches it."""
        for bad in ([[0, True]], [[True]], [[0, "1"]], [[0, 1.0]]):
            with self.subTest(columns=bad):
                with self.assertRaises(ValueError):
                    FC.Circuit(bad, 1, 2)
        FC.Circuit([[0, 1]], 1, 2)               # the valid shape still works

    def test_the_weight_two_budget_does_not_discard_an_immediate_witness(self):
        """Three equal-syndrome columns with distinct outputs: every pair is
        harmful, so a scan that pre-skipped the bucket threw away a witness
        that cost one comparison.  The budget is charged per pair examined."""
        columns = [(0, 3), (1, 3), (2, 3)]
        c = FC.Circuit(columns, 3, 4, FC.Budget(max_candidates=2))
        status, witness, _count = FC.scan_weight(c, 2)
        self.assertEqual(status, "found")
        self.assertTrue(c.harmful(witness))
        # and a flood of BENIGN pairs (duplicate columns) still gets bounded
        dup = FC.Circuit([(0, 2)] * 3, 1, 3, FC.Budget(max_candidates=2))
        self.assertEqual(FC.scan_weight(dup, 2), ("skipped", None, None))


if __name__ == "__main__":
    unittest.main()
