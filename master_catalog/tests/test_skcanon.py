"""`skcanon` against the upstream `S_k` key it has to reproduce.

The dedup key is defined in `classification/legacy/exhaustive_n38/dedup.py` as the
lexicographic minimum over all `k!` relabellings of the gate's monomial set.
`skcanon` computes the same thing three ways -- a closed form for disjoint
covers, brute force through `k = 9`, and a branch and bound above it -- because
`162!` is not a loop.  Every one of those routes has to agree with the
definition, so each is tested against it directly on the widths where the
definition can actually be evaluated.

The last route is allowed to give up, and that is tested too: when it does it
must return `None` rather than a guess, because a wrong canonical form silently
merges two different gates into one catalogue row.
"""
import itertools
import random
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE.parent
REPO = CATALOGUE.parent
sys.path.insert(0, str(CATALOGUE))
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "classification" / "legacy" / "exhaustive_n38"))

import skcanon as SK                                            # noqa: E402
from dedup import sk_canonical as upstream_key, sk_name         # noqa: E402


def random_gates(rng, k, count, max_size=8):
    """Gates shaped like catalogue ones: no output the gate never touches."""
    universe = [frozenset(c) for degree in (1, 2, 3)
                for c in itertools.combinations(range(k), degree)]
    out = []
    while len(out) < count:
        gate = set(rng.sample(universe, rng.randint(1, min(len(universe),
                                                           max_size))))
        if set().union(*gate) == set(range(k)):
            out.append(gate)
    return out


class TestIsomorphismBacktracks(unittest.TestCase):
    """The search must be able to UNDO a wrong guess.

    Every isomorphism fixture in this suite is a gate against its own
    relabelling, and refinement usually walks those straight to an answer
    without ever retracting a candidate.  So the backtrack's bookkeeping was
    unpinned: corrupting the undo (releasing the wrong label on the way back
    up) left the whole suite green while `sk_isomorphic` returned False for a
    genuinely isomorphic pair -- which is exactly how a duplicate class enters
    a catalogue that promises it has none.
    """

    #: Found by searching for a pair whose verdict changes when the undo is
    #: corrupted: the search must commit, fail, release the label it took, and
    #: succeed on a later branch.
    LEFT = [(0, 1, 2), (0, 2, 4), (1, 3, 5), (3, 4, 5)]
    RIGHT = [(0, 2, 5), (0, 3, 4), (1, 2, 5), (1, 3, 4)]

    def test_a_pair_that_needs_a_retracted_guess(self):
        left = {frozenset(Q) for Q in self.LEFT}
        right = {frozenset(Q) for Q in self.RIGHT}
        self.assertIs(SK.sk_isomorphic(6, left, right), True)
        self.assertIs(SK.sk_isomorphic(6, right, left), True,
                      "and the same in the other direction")

    def test_the_permutation_it_finds_really_carries_one_onto_the_other(self):
        """A True is only worth what its witness is worth."""
        rng = random.Random(20260901)
        for trial in range(200):
            k = rng.randint(4, 7)
            universe = [frozenset(c) for degree in (2, 3)
                        for c in itertools.combinations(range(k), degree)]
            gate = set(rng.sample(universe,
                                  rng.randint(3, min(8, len(universe)))))
            perm = list(range(k))
            rng.shuffle(perm)
            other = {frozenset(Q)
                     for Q in SK.apply_perm(sorted(gate, key=sorted), perm)}
            with self.subTest(trial=trial):
                self.assertIs(SK.sk_isomorphic(k, gate, other), True,
                              "a relabelling is always an isomorphism")

    def test_a_gate_one_monomial_away_is_refused(self):
        """The negative control: near-symmetry must not read as sameness."""
        rng = random.Random(5)
        for trial in range(200):
            k = rng.randint(4, 7)
            universe = [frozenset(c) for degree in (2, 3)
                        for c in itertools.combinations(range(k), degree)]
            gate = set(rng.sample(universe,
                                  rng.randint(3, min(7, len(universe)))))
            spare = [Q for Q in universe if Q not in gate]
            if not spare:
                continue
            nudged = set(gate)
            nudged.discard(sorted(gate, key=sorted)[0])
            nudged.add(rng.choice(spare))
            if len(nudged) != len(gate):
                continue
            verdict = SK.sk_isomorphic(k, gate, nudged)
            if verdict is None:
                continue
            with self.subTest(trial=trial):
                self.assertEqual(verdict, SK.sk_canonical(k, gate)
                                 == SK.sk_canonical(k, nudged),
                                 "the verdict must match the canonical forms")


class TestIsomorphismIsBounded(unittest.TestCase):
    """``sk_isomorphic`` may run out, and must say so rather than say "no"."""

    def test_exhaustion_returns_None_and_never_False(self):
        gate = {frozenset((0, 1, q)) for q in range(2, 9)}
        rotated = {frozenset(SK.apply_perm([gate], list(range(9)))[0])} if False else gate
        self.assertIsNone(SK.sk_isomorphic(9, gate, gate, node_budget=1),
                          "a budget of one node cannot decide this")

    def test_a_generous_budget_still_decides(self):
        gate = {frozenset((0, 1, q)) for q in range(2, 9)}
        self.assertIs(SK.sk_isomorphic(9, gate, gate), True)

    def test_non_isomorphic_gates_are_still_False_not_None(self):
        """The cheap invariants settle these before any search happens."""
        left = {frozenset((0, 1)), frozenset((2, 3))}
        right = {frozenset((0, 1)), frozenset((1, 2))}
        self.assertIs(SK.sk_isomorphic(4, left, right), False)


class TestTheKeyMatchesUpstream(unittest.TestCase):
    def test_canonical_form_equals_the_k_factorial_minimum(self):
        rng = random.Random(20260827)
        checked = 0
        for k in range(1, 8):
            for gate in random_gates(rng, k, 120):
                key, perm = SK.sk_canonical_with_perm(k, gate)
                with self.subTest(k=k, gate=sorted(map(sorted, gate))):
                    self.assertEqual(key, upstream_key(k, gate))
                    self.assertIsNotNone(perm)
                    self.assertEqual(SK.apply_perm(gate, perm), key,
                                     "the permutation must realise the key")
                checked += 1
        self.assertGreater(checked, 500)

    def test_the_gate_string_is_byte_for_byte_sk_name(self):
        """Master-catalogue rows must keep the exact strings they have."""
        rng = random.Random(11)
        for k in range(1, 7):
            for gate in random_gates(rng, k, 60):
                key = upstream_key(k, gate)
                with self.subTest(k=k, key=key):
                    self.assertEqual(
                        SK.gate_string([frozenset(Q) for Q in key], k),
                        sk_name(key))


class TestEachRoute(unittest.TestCase):
    def test_the_disjoint_cover_closed_form_is_the_minimum(self):
        """Blocks of consecutive labels, smallest monomial first."""
        rng = random.Random(5)
        for k in range(2, 9):
            for _ in range(60):
                rest = list(range(k))
                rng.shuffle(rest)
                parts = []
                while rest:
                    take = min(rng.choice([1, 2, 3]), len(rest))
                    parts.append(frozenset(rest[:take]))
                    rest = rest[take:]
                self.assertIsNotNone(SK._disjoint_cover_perm(k, parts))
                closed = SK.sk_canonical(k, parts)
                brute = min(SK.apply_perm(parts, p)
                            for p in itertools.permutations(range(k)))
                with self.subTest(k=k, parts=sorted(map(sorted, parts))):
                    self.assertEqual(closed, brute)

    def test_the_branch_and_bound_finds_the_true_minimum(self):
        """Run it on gates the brute force can still check, bypassing the
        `k <= 9` shortcut that would otherwise handle them."""
        rng = random.Random(13)
        checked = 0
        for k in (7, 8):
            universe = [frozenset(c) for c in itertools.combinations(range(k), 3)]
            for _ in range(40):
                gate = set(rng.sample(universe, rng.randint(4, 12)))
                if set().union(*gate) != set(range(k)):
                    continue
                if SK._disjoint_cover_perm(k, gate) is not None:
                    continue
                found, perm = SK._branch_and_bound(k, gate, 20_000_000)
                brute = min(SK.apply_perm(gate, p)
                            for p in itertools.permutations(range(k)))
                with self.subTest(k=k, gate=sorted(map(sorted, gate))):
                    self.assertEqual(found, brute)
                    self.assertEqual(SK.apply_perm(gate, perm), found)
                checked += 1
        self.assertGreater(checked, 10)

    def test_running_out_of_budget_returns_none_not_a_guess(self):
        """A wrong canonical form merges two gates into one row; no answer
        cannot."""
        gate = {frozenset((0, 1, q)) for q in range(2, 12)}
        key, perm = SK.sk_canonical_with_perm(12, gate, node_budget=50)
        self.assertIsNone(key)
        self.assertIsNone(perm)


class TestTheFallbackKey(unittest.TestCase):
    """What the six rows too wide to canonicalise are deduplicated by."""

    def test_the_fingerprint_is_permutation_invariant(self):
        rng = random.Random(77)
        for k in range(3, 9):
            for gate in random_gates(rng, k, 40):
                perm = list(range(k))
                rng.shuffle(perm)
                twin = {frozenset(perm[q] for q in Q) for Q in gate}
                with self.subTest(k=k):
                    self.assertEqual(SK.sk_fingerprint(k, gate),
                                     SK.sk_fingerprint(k, twin))

    def test_the_fingerprint_never_splits_a_class(self):
        """It may merge classes -- that is what the isomorphism test is for --
        but it must never separate two gates that ARE the same class."""
        rng = random.Random(78)
        for k in range(3, 8):
            gates = random_gates(rng, k, 30)
            for left, right in itertools.combinations(gates, 2):
                if upstream_key(k, left) == upstream_key(k, right):
                    with self.subTest(k=k):
                        self.assertEqual(SK.sk_fingerprint(k, left),
                                         SK.sk_fingerprint(k, right))

    def test_the_isomorphism_test_decides_exactly_what_the_key_does(self):
        rng = random.Random(79)
        checked = 0
        for k in range(3, 8):
            gates = random_gates(rng, k, 26)
            for left, right in itertools.combinations(gates, 2):
                same = upstream_key(k, left) == upstream_key(k, right)
                with self.subTest(k=k):
                    self.assertEqual(SK.sk_isomorphic(k, left, right), same)
                checked += 1
        self.assertGreater(checked, 500)

    def test_a_relabelled_gate_is_always_isomorphic_to_itself(self):
        rng = random.Random(80)
        for k in range(3, 10):
            for gate in random_gates(rng, k, 25):
                perm = list(range(k))
                rng.shuffle(perm)
                twin = {frozenset(perm[q] for q in Q) for Q in gate}
                with self.subTest(k=k):
                    self.assertTrue(SK.sk_isomorphic(k, gate, twin))


if __name__ == "__main__":
    unittest.main()
