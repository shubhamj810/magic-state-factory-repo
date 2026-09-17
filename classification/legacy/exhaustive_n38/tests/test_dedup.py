"""The deduplication key is S_k.  These tests pin down exactly what that means,
because the difference between S_k and GL(k,2) is the single most misreadable
thing about this catalogue.

Read `dedup.py`'s module docstring first; every claim it makes is asserted here.
"""
import sys
import unittest
from itertools import combinations, permutations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from dedup import (canonical_gate, gate_truth_table, sk_canonical,  # noqa: E402
                   sk_name)


def mons(*groups):
    """Convenience: mons((0,), (0, 1)) -> {frozenset({0}), frozenset({0,1})}."""
    return {frozenset(g) for g in groups}


class TestSkKey(unittest.TestCase):
    def test_invariant_under_output_permutations(self):
        """Permuting outputs must not change the key -- that is the definition."""
        g = mons((0,), (2,), (1, 2), (0, 1, 2))
        base = sk_canonical(3, g)
        for p in permutations(range(3)):
            img = {frozenset(p[i] for i in Q) for Q in g}
            self.assertEqual(sk_canonical(3, img), base)

    def test_separates_genuinely_different_gates(self):
        """T0.T1 and T0.CS01 are different S_k classes (see the [[28,2,3]] case)."""
        self.assertNotEqual(sk_canonical(2, mons((0,), (1,))),
                            sk_canonical(2, mons((0,), (0, 1))))

    def test_name_round_trips(self):
        self.assertEqual(sk_name(sk_canonical(2, mons((0,), (1,)))), "0+1")
        self.assertEqual(sk_name(sk_canonical(2, mons((1,), (0, 1)))), "0+01")
        self.assertEqual(sk_name(sk_canonical(3, mons((0, 1, 2)))), "012")
        self.assertEqual(sk_name(sk_canonical(1, set())), "check-only")

    def test_labels_produced_by_the_engine_are_already_canonical(self):
        """sk_name(sk_canonical(...)) is idempotent, which is what lets
        build_catalog.py re-canonicalise on load without changing good input."""
        for k in (1, 2, 3):
            allQ = [frozenset(c) for d in (1, 2, 3)
                    for c in combinations(range(k), d)]
            for r in range(1, min(len(allQ), 4) + 1):
                for sub in combinations(allQ, r):
                    name = sk_name(sk_canonical(k, set(sub)))
                    remons = {frozenset(int(ch) for ch in tok)
                              for tok in name.split("+") if tok != "check-only"}
                    self.assertEqual(sk_name(sk_canonical(k, remons)), name)


class TestGlAnnotation(unittest.TestCase):
    def test_gl_is_coarser_than_sk(self):
        """Permutation matrices lie in GL(k,2), so every S_k class sits inside a
        single GL(k,2) class: equal S_k key => equal GL class."""
        k = 3
        allQ = [frozenset(c) for d in (1, 2, 3) for c in combinations(range(k), d)]
        seen = {}
        for r in range(1, 4):
            for sub in combinations(allQ, r):
                g = set(sub)
                key = sk_canonical(k, g)
                gl = canonical_gate(k, g)
                if key in seen:
                    self.assertEqual(seen[key], gl)
                else:
                    seen[key] = gl
        # and strictly coarser: fewer GL classes than S_k classes
        self.assertLess(len(set(seen.values())), len(seen))

    def test_the_28_2_3_pair_is_two_gl_classes(self):
        """`0+1` and `0+01` come from ONE subspace read in two output frames,
        but they are NOT in the same GL(k,2)-substitution class.  The catalogue
        lists both rows; dedup.py explains why these are three different
        relations and not one."""
        self.assertEqual(canonical_gate(2, mons((0,), (1,))), 6)
        self.assertEqual(canonical_gate(2, mons((0,), (0, 1))), 2)

    def test_one_subspace_two_rows(self):
        """Construct the [[28,2,3]] situation directly: take rows a, b with |a|
        and |b| odd and |a & b| even, so the gate is `0+1`; re-read the same
        subspace in the basis (a, a+b) and the gate becomes `0+01`."""
        a = 0b110111          # weight 5, odd
        b = 0b011101          # weight 4 -> adjust below
        b = 0b011111          # weight 5, odd
        self.assertEqual(a.bit_count() % 2, 1)
        self.assertEqual(b.bit_count() % 2, 1)
        self.assertEqual((a & b).bit_count() % 2, 0)

        def gate_of(x, y):
            g = set()
            if x.bit_count() % 2:
                g.add(frozenset({0}))
            if y.bit_count() % 2:
                g.add(frozenset({1}))
            if (x & y).bit_count() % 2:
                g.add(frozenset({0, 1}))
            return sk_name(sk_canonical(2, g))

        self.assertEqual(gate_of(a, b), "0+1")
        self.assertEqual(gate_of(a, a ^ b), "0+01")


class TestTruthTable(unittest.TestCase):
    def test_truth_table_matches_direct_evaluation(self):
        g = mons((0,), (1, 2))
        tt = gate_truth_table(3, g)
        for x in range(8):
            want = ((x >> 0) & 1) ^ (((x >> 1) & 1) & ((x >> 2) & 1))
            self.assertEqual((tt >> x) & 1, want)


if __name__ == "__main__":
    unittest.main()
