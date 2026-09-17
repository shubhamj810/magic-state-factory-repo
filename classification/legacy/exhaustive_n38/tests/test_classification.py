"""End-to-end checks on the classifier itself.

Two independent enumerators live in this directory -- `classify.py`, which works
in the quotient V = R(C)/C, and `classify_rowspace.py`, which works in the full
row space.  They were written at different times and share only the F_2
primitives and the verifier.  Agreement between them on the small end of the
ladder is the strongest evidence available that the enumeration is right, so it
is a test rather than a footnote.
"""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parents[3]))

import classify                                      # noqa: E402
from dedup import canonical_gate, sk_canonical, sk_name   # noqa: E402
from factorylib.verification import verify           # noqa: E402


def run_small(ns, kmax=3):
    """Classify a few small lengths and return {(n, k, gate): record}."""
    seen, partial, _stats, _deferred = classify.run(ns, kmax, budget=50_000_000)
    assert not partial, f"unexpected budget hit at {sorted(partial)}"
    return seen


class TestSmallLadder(unittest.TestCase):
    """n <= 30 is cheap enough to classify inside a test (about a second)."""

    @classmethod
    def setUpClass(cls):
        cls.seen = run_small([15, 23, 27, 28, 29, 30], kmax=3)

    def test_known_gate_counts(self):
        """These are the published numbers for the bottom of the ladder."""
        by_n = {}
        for (n, k, _pc) in self.seen:
            by_n[n] = by_n.get(n, 0) + 1
        self.assertEqual(by_n, {15: 1, 23: 1, 27: 1, 28: 3, 29: 1, 30: 3})

    def test_the_15_1_3_class_is_the_single_T(self):
        """[[15,1,3]] is the punctured Reed-Muller factory; the only gate the
        n=15 window realises is one T."""
        gates = {rec["gate"] for (n, _k, _pc), rec in self.seen.items() if n == 15}
        self.assertEqual(gates, {"0"})

    def test_no_pure_ccz_below_39(self):
        """The witness behind the CCZ >= 39 distance-3 lower bound: the monomial
        `012` never appears alone anywhere in the window."""
        for (_n, k, _pc), rec in self.seen.items():
            if k == 3:
                self.assertNotEqual(rec["gate"], "012")

    def test_every_record_reverifies_from_its_columns(self):
        """The engine already calls verify() while enumerating; re-run it here
        on the stored columns so the test fails if the record and its circuit
        ever drift apart."""
        for (n, k, _pc), rec in self.seen.items():
            with self.subTest(n=n, k=k, gate=rec["gate"]):
                cols = [frozenset(c) for c in rec["columns"]]
                self.assertEqual(len(cols), n)
                self.assertEqual(len(set(cols)), n)
                wants = {frozenset(int(ch) for ch in tok)
                         for tok in rec["gate"].split("+") if tok}
                ok, dist = verify(k, rec["rows"], cols, wants, dmax=4)
                self.assertTrue(ok, "parity check failed")
                self.assertEqual(dist, rec["distance"])

    def test_stored_labels_are_sk_canonical(self):
        for (_n, k, _pc), rec in self.seen.items():
            wants = {frozenset(int(ch) for ch in tok)
                     for tok in rec["gate"].split("+") if tok}
            self.assertEqual(sk_name(sk_canonical(k, wants)), rec["gate"])

    def test_gl_annotation_is_consistent(self):
        for (_n, k, _pc), rec in self.seen.items():
            wants = {frozenset(int(ch) for ch in tok)
                     for tok in rec["gate"].split("+") if tok}
            self.assertEqual(canonical_gate(k, wants), rec["gate_gl_canonical"])


class TestIndependentRowspaceEnumerator(unittest.TestCase):
    """Cross-check against the pre-quotient enumerator, and pin down the ONE
    place where the two deliberately disagree.

    `classify_rowspace.py` enumerates output frames that are independent inside
    R(C).  `classify.py` enumerates frames that are independent inside the
    QUOTIENT V = R(C)/C.  The second condition is strictly stronger, so the
    quotient engine sees a subset of what the row-space engine sees, and the
    difference is exactly the frames whose outputs become dependent once you
    reduce modulo the check span.

    Those "lift-degenerate" frames are real circuits -- ansatz-free SAT finds
    one at [[15,2,3]] with gate `0+1+01`, and the tests below construct them
    directly -- but the quotient method cannot represent them, because their gate
    depends on WHICH lift of a quotient point you pick and so is not a function
    of V at all.  (They are also kept out of the search catalogue, which rejects
    a declared width whose outputs are dependent mod the check span: such a
    circuit is a narrower factory on a spare wire.)  See
    classify.py's "Scope" section.

    This test asserts both halves: containment, and that every extra class is
    lift-degenerate with the predicted gate.
    """

    NS = [15, 23, 27, 28, 29, 30]

    @staticmethod
    def _rowspace_classes(n, kmax):
        import classify_rowspace as rowspace
        seen = {}
        for _ci, r, cs in classify.marked_all(n):
            _nodes, hit = rowspace.classify_support(cs, r, kmax, 5_000_000, seen)
            assert not hit, f"row-space enumerator hit its budget at n={n}"
        return seen

    @staticmethod
    def _output_rank_mod_checks(rec):
        """dim of span(outputs) modulo span(check rows) -- k for a genuine
        k-output frame, less for a lift-degenerate one."""
        cols = [set(c) for c in rec["columns"]]
        k, r = rec["k"], rec["r"]
        rows = [sum(1 << j for j, c in enumerate(cols) if q in c)
                for q in range(k + r)]
        basis = []

        def add(v):
            for b in basis:
                v = min(v, v ^ b)
            if v:
                basis.append(v)
                basis.sort(reverse=True)

        for v in rows[k:]:
            add(v)
        before = len(basis)
        for v in rows[:k]:
            add(v)
        return len(basis) - before

    def test_quotient_classes_are_contained_in_rowspace_classes(self):
        for n in self.NS:
            with self.subTest(n=n):
                quotient, partial, _s, _d = classify.run([n], 2, budget=50_000_000)
                self.assertFalse(partial)
                q_keys = {(nn, k, rec["gate_gl_canonical"])
                          for (nn, k, _pc), rec in quotient.items()}
                r_keys = set(self._rowspace_classes(n, 2))
                self.assertTrue(q_keys <= r_keys,
                                f"quotient found classes the row-space "
                                f"enumerator missed at n={n}: {q_keys - r_keys}")

    def test_every_extra_rowspace_class_is_lift_degenerate(self):
        """The only classes the quotient engine omits are the ones whose output
        rows collapse modulo C -- and their gate is forced to be `0+1+01`,
        because lifting one odd-weight quotient point two ways gives
        |a| odd, |a+c| odd, |a & (a+c)| = |a| - |a & c| odd."""
        for n in self.NS:
            with self.subTest(n=n):
                quotient, _p, _s, _d = classify.run([n], 2, budget=50_000_000)
                q_keys = {(nn, k, rec["gate_gl_canonical"])
                          for (nn, k, _pc), rec in quotient.items()}
                rowspace = self._rowspace_classes(n, 2)
                for sig in set(rowspace) - q_keys:
                    rec = rowspace[sig]
                    self.assertLess(self._output_rank_mod_checks(rec), rec["k"],
                                    f"{sig} is NOT lift-degenerate -- the "
                                    f"quotient engine has a genuine gap")
                    self.assertEqual(rec["gate"], "0+1+01")

    def test_lift_degenerate_frames_carry_no_extra_magic(self):
        """THE REASON THE OMISSION IS HARMLESS.

        A lift-degenerate frame is not a new resource.  If two output rows
        differ by an element of the check span, one output CNOT turns the
        second into an IDLE SPECTATOR -- a qubit carrying no monomial at all --
        leaving exactly the lower-width factory the quotient engine already
        enumerated.

        Proof, checked here on every omitted class.  Replace output row `b` by
        `b + a`, which is what a physical CNOT between the two output qubits
        does.  When `b = a + c` with `c` in C, the new row IS `c`, and:

          * |c| is even, because every check row has even weight and weights
            add mod 2 under XOR;
          * |c & a'| is even for every a' in R(C), because R(C) is contained in
            the dual of C;
          * |c & a' & a''| is even for every compatible pair in R(C), because
            pairwise compatibility says |a' & a'' & h_j| is even for each check
            row h_j, and that extends to all of C by the same parity argument.

        So the new output carries no T, no CS and no CCZ.  The consequence is
        that the classification is complete for magic CONTENT -- which gates are
        achievable, the largest genuine output width, the largest T count --
        and incomplete only for circuit REPRESENTATIONS in which some outputs
        are Clifford-equivalent to idle spectators.  Note that `classify.py`
        already discards frames with a manifestly idle output (the `covered`
        check in `record`), so excluding these is the same policy applied one
        Clifford deeper.
        """
        for n in self.NS:
            with self.subTest(n=n):
                quotient, _p, _s, _d = classify.run([n], 2, budget=50_000_000)
                q_keys = {(nn, k, rec["gate_gl_canonical"])
                          for (nn, k, _pc), rec in quotient.items()}
                rowspace = self._rowspace_classes(n, 2)
                omitted = set(rowspace) - q_keys
                self.assertTrue(omitted, f"expected omitted classes at n={n}")
                for sig in omitted:
                    rec = rowspace[sig]
                    cols = [set(c) for c in rec["columns"]]
                    k, r = rec["k"], rec["r"]
                    rows = [sum(1 << j for j, c in enumerate(cols) if q in c)
                            for q in range(k + r)]
                    outs, checks = rows[:k], rows[k:]

                    # the output CNOT: row b becomes b XOR a
                    new = outs[1] ^ outs[0]

                    # it lands in the check span C ...
                    basis = []
                    for h in checks:
                        v = h
                        for b in basis:
                            v = min(v, v ^ b)
                        if v:
                            basis.append(v)
                            basis.sort(reverse=True)
                    probe = new
                    for b in basis:
                        probe = min(probe, probe ^ b)
                    self.assertEqual(probe, 0,
                                     "the CNOT'd row should lie in span(checks)")

                    # ... and therefore carries no monomial of any degree
                    self.assertEqual(new.bit_count() % 2, 0, "spurious T")
                    self.assertEqual((new & outs[0]).bit_count() % 2, 0,
                                     "spurious CS")
                    for h in checks:
                        self.assertEqual((new & outs[0] & h).bit_count() % 2, 0,
                                         "spurious check-touching triple")

    def test_the_omitted_gate_is_one_T_in_disguise(self):
        """`T0.T1.CS01` has exact minimal T-count 1, not 2 or 3.

        Over Z_8 its phase polynomial is x0 + x1 + 2*x0*x1, and
        x0 XOR x1 = x0 + x1 - 2*x0*x1, so the polynomial equals
        (x0 XOR x1) + 4*x0*x1 -- one T on the parity of the two outputs, times
        a CZ, which is Clifford.  So the omitted class delivers exactly the
        same resource as the [[n,1,3]] factory it was lifted from, on one extra
        qubit.  This is the arithmetic behind the previous test.
        """
        from factorylib import metrics
        t_count, _note, degree, _dnote = metrics.metrics_from_named(
            "T0 . T1 . CS01")
        self.assertEqual(t_count, 1)
        self.assertEqual(degree, 1)
        # ... whereas two genuinely independent T outputs cost 2
        self.assertEqual(metrics.metrics_from_named("T0 . T1")[0], 2)


if __name__ == "__main__":
    unittest.main()
