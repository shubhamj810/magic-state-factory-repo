"""gatefamily.py: the family of a gate over all CNOT frames, against a literal
enumeration of GL(k,2) for small k, and on catalogue gates the lead checked."""
from __future__ import annotations

import itertools
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import gatefamily as GF                                           # noqa: E402
import glcanon as G                                               # noqa: E402


def invertible(k):
    """Every basis of F_2^k, as a list of k bitmasks."""
    for cols in itertools.product(range(1, 1 << k), repeat=k):
        if GF._rank(cols) == k:
            yield list(cols)


def kind_in(k, monos, frame):
    """The gate's kind in ``frame``, by glcanon.evaluate (not gatefamily's code)."""
    T = G.tensor(k, monos)
    sizes = set()
    for i in range(k):
        if G.evaluate(T, frame[i], frame[i], frame[i]):
            sizes.add(1)
    for i, j in itertools.combinations(range(k), 2):
        if G.evaluate(T, frame[i], frame[i], frame[j]):
            sizes.add(2)
    for i, j, l in itertools.combinations(range(k), 3):
        if G.evaluate(T, frame[i], frame[j], frame[l]):
            sizes.add(3)
    return {frozenset({1}): "T", frozenset({2}): "CS", frozenset({3}): "CCZ"}.get(
        frozenset(sizes), "mixed" if sizes else "none")


def brute_family(k, monos, frames):
    kinds = {kind_in(k, monos, f) for f in frames}
    for fam in ("T", "CS", "CCZ"):
        if fam in kinds:
            return fam
    return "mixed"


def random_gate(rng, k):
    pool = [(i,) for i in range(k)] + list(itertools.combinations(range(k), 2)) \
        + list(itertools.combinations(range(k), 3))
    while True:
        monos = [m for m in pool if rng.random() < 0.35]
        if monos:
            return monos


class TestAgainstEnumeration(unittest.TestCase):
    def test_every_frame_for_k_up_to_3_and_random_gates_at_4(self):
        rng = random.Random(20261109)
        for k in (2, 3, 4):
            frames = list(invertible(k))
            gates = ([list(m) for r in range(1, 4)
                      for m in itertools.combinations(
                          [(i,) for i in range(k)] + list(itertools.combinations(range(k), 2))
                          + list(itertools.combinations(range(k), 3)), r)]
                     if k <= 3 else [random_gate(rng, k) for _ in range(15)])
            for monos in gates:
                if not G.intrinsic_width(k, monos):
                    continue
                got = GF.decide(k, monos)
                want = brute_family(k, monos, frames)
                self.assertEqual(got["family"], want, (k, monos))
                if got["frame"] is not None:
                    self.assertEqual(kind_in(k, monos, got["frame"]), want, (k, monos))
                    self.assertEqual(GF.check_frame(k, monos, got["frame"], want), [])


class TestCatalogueGates(unittest.TestCase):
    def test_48_5_3_d_is_cs_in_another_frame(self):
        # stored CS01·CS34·CCZ012·CCZ234; the lead checked the CS frame by hand
        monos = [(0, 1), (3, 4), (0, 1, 2), (2, 3, 4)]
        got = GF.decide(5, monos)
        self.assertEqual(got["family"], "CS")
        self.assertEqual(GF.kind_of(got["gate"]), "CS")
        self.assertTrue(G.gl_isomorphic(5, monos, got["gate"]))

    def test_a_hidden_spectator_t_row(self):
        # T0·T1·CS01 is T on one output: in the frame (e0, e0+e1) it is T0
        got = GF.decide(2, [(0,), (1,), (0, 1)])
        self.assertEqual(got["family"], "T")
        self.assertEqual(got["gate"], [(0,)])

    def test_stored_families_need_no_frame(self):
        for monos, fam in (([(0,), (1,)], "T"), ([(0, 1), (1, 2)], "CS"),
                           ([(0, 1, 2)], "CCZ")):
            self.assertEqual(GF.decide(3, monos), {"family": fam, "frame": None, "gate": None})

    def test_check_frame_rejects_a_wrong_claim(self):
        monos = [(0, 1), (3, 4), (0, 1, 2), (2, 3, 4)]
        self.assertTrue(GF.check_frame(5, monos, [1, 2, 4, 8, 16], "CS"))
        self.assertTrue(GF.check_frame(5, monos, [1, 1, 4, 8, 16], "CS"))

    def test_large_t_family_by_algebra(self):
        # T on 20 outputs, moved into a random frame, is found again
        rng = random.Random(7)
        k = 20
        while True:
            A = [rng.randrange(1, 1 << k) for _ in range(k)]
            if GF._rank(A) == k:
                break
        diag = [(i,) for i in range(k)]
        moved = GF.gate_in_frame(k, G.tensor(k, diag), A)
        got = GF.decide(k, moved)
        self.assertEqual(got["family"], "T")
        self.assertEqual(sorted(got["gate"]), diag)


if __name__ == "__main__":
    unittest.main()
