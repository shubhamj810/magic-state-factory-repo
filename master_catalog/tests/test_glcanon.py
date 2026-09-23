"""`glcanon` against the definition it claims to decide, executed literally.

The definition: two gates on ``k`` outputs are one class iff some invertible
``A`` makes ``f(Ax)`` equal to the other phase modulo diagonal Cliffords.  The
literal reading tabulates ``f`` on all of ``F_2^k``, substitutes every ``A`` in
``GL(k,2)``, Moebius-transforms the result to ``Z_8`` coefficients and reduces
them modulo Clifford.  Nothing below imports the tensor to do that, so the
tensor, its labels and the search are checked against a separate
implementation of the same statement.
"""
import itertools
import random
import sys
import time
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import glcanon as GC                                           # noqa: E402

WEIGHT = {1: 1, 2: 2, 3: 4}


def phase_table(k, monomials):
    table = []
    for x in range(1 << k):
        value = 0
        for mono in monomials:
            if all(x >> i & 1 for i in mono):
                value += WEIGHT[len(mono)]
        table.append(value % 8)
    return table


def reduce_mod_clifford(k, table):
    """The monomial set of a ``Z_8`` phase table modulo diagonal Cliffords."""
    out = set()
    for S in range(1, 1 << k):
        coefficient = 0
        T = S
        while True:
            sign = -1 if (S.bit_count() - T.bit_count()) & 1 else 1
            coefficient += sign * table[T]
            if T == 0:
                break
            T = (T - 1) & S
        coefficient %= 8
        size = S.bit_count()
        mono = frozenset(i for i in range(k) if S >> i & 1)
        # A level-3 phase has coefficients 2^(|S|-1) Z mod 8: anything else is
        # a bug upstream of this function, and dropping it silently would let
        # the covariance test pass on garbage.
        if size == 1 and coefficient % 2:
            out.add(mono)
        elif size == 2:
            assert coefficient % 2 == 0, "odd quadratic coefficient"
            if coefficient % 4 == 2:
                out.add(mono)
        elif size == 3:
            assert coefficient in (0, 4), "cubic coefficient not in {0, 4}"
            if coefficient == 4:
                out.add(mono)
        elif size >= 4:
            assert coefficient == 0, "a level-3 phase has no degree-4 term"
    return frozenset(out)


def all_gl(k):
    """Every invertible ``A``, as the images of the basis vectors."""
    for images in itertools.product(range(1, 1 << k), repeat=k):
        span = {0}
        ok = True
        for v in images:
            if v in span:
                ok = False
                break
            span |= {s ^ v for s in span}
        if ok:
            yield images


def apply_frame(k, table, images):
    """``x -> f(Ax)`` where ``A e_i = images[i]``."""
    out = []
    for x in range(1 << k):
        y = 0
        for i in range(k):
            if x >> i & 1:
                y ^= images[i]
        out.append(table[y])
    return out


def all_gates(k):
    monos = [frozenset(m) for size in (1, 2, 3)
             for m in itertools.combinations(range(k), size)]
    for bits in range(1 << len(monos)):
        yield frozenset(m for i, m in enumerate(monos) if bits >> i & 1)


def random_gate(k, rng, density=0.3):
    return frozenset(frozenset(m) for size in (1, 2, 3)
                     for m in itertools.combinations(range(k), size)
                     if rng.random() < density)


def random_frame(k, rng):
    while True:
        images = [rng.randrange(1, 1 << k) for _ in range(k)]
        span = {0}
        for v in images:
            if v in span:
                break
            span |= {s ^ v for s in span}
        else:
            return images


def all_gl_small_check(k, frame):
    """``[frame]`` if its images are independent, else ``[]`` (a fixture guard)."""
    span = {0}
    for v in frame:
        if v in span:
            return []
        span |= {s ^ v for s in span}
    return [tuple(frame)]


def _gate_of(row):
    """The monomial set a catalogue row's columns deposit, read here rather
    than imported, so this file stays independent of the verifier."""
    k, N = row["k"], row["N"]
    rows = [0] * N
    for j, column in enumerate(row["columns"]):
        for q in column:
            rows[q] |= 1 << j
    out = []
    for i in range(k):
        if bin(rows[i]).count("1") % 2:
            out.append((i,))
        for j in range(i + 1, k):
            if bin(rows[i] & rows[j]).count("1") % 2:
                out.append((i, j))
            for l in range(j + 1, k):
                if bin(rows[i] & rows[j] & rows[l]).count("1") % 2:
                    out.append((i, j, l))
    return out


def literal_orbit_contains(k, gate, targets, chunk=500_000):
    """For each target: is it in the GL(k,2)-orbit of ``gate`` modulo Clifford?

    Every invertible frame is enumerated (vectorised), applied to the Z_8 truth
    table, Moebius-reduced and compared -- the definition, with no tensor.
    """
    size = 1 << k
    frames = np.arange(1, size, dtype=np.int64).reshape(-1, 1)
    spans = np.array([1 | (1 << int(v)) for v in frames[:, 0]], dtype=np.uint64)
    for _depth in range(1, k):
        grown_frames, grown_spans = [], []
        for v in range(1, size):
            ok = ((spans >> np.uint64(v)) & np.uint64(1)) == 0
            f, sp = frames[ok], spans[ok]
            new = sp.copy()
            for p in range(size):
                has = ((sp >> np.uint64(p)) & np.uint64(1)).astype(bool)
                new[has] |= np.uint64(1) << np.uint64(p ^ v)
            grown_frames.append(np.hstack([f, np.full((len(f), 1), v)]))
            grown_spans.append(new)
        frames, spans = np.vstack(grown_frames), np.concatenate(grown_spans)

    def keys(tables):
        m = tables.astype(np.int16).copy()
        for i in range(k):
            bit = 1 << i
            idx = np.array([x for x in range(size) if x & bit])
            m[:, idx] -= m[:, idx ^ bit]
        m %= 8
        out = np.zeros(len(m), dtype=np.int64)
        position = 0
        for S in range(1, size):
            degree = bin(S).count("1")
            if degree == 1:
                bits = m[:, S] % 2
            elif degree == 2:
                bits = (m[:, S] % 4) == 2
            elif degree == 3:
                bits = m[:, S] == 4
            else:
                continue
            out |= bits.astype(np.int64) << position
            position += 1
        return out

    source = np.array(phase_table(k, gate), dtype=np.int16)
    wanted = [int(keys(np.array([phase_table(k, t)], dtype=np.int16))[0])
              for t in targets]
    found = [False] * len(targets)
    xs = np.arange(size)
    for start in range(0, len(frames), chunk):
        block = frames[start:start + chunk]
        images = np.zeros((len(block), size), dtype=np.int64)
        for i in range(k):
            images ^= ((xs >> i) & 1)[None, :] * block[:, i][:, None]
        got = set(np.unique(keys(source[images])).tolist())
        found = [f or (w in got) for f, w in zip(found, wanted)]
    return found


class TensorIsTheRightInvariant(unittest.TestCase):
    def test_the_tensor_is_the_third_difference(self):
        """Built from monomials, it equals (D_u D_v D_w f)/4 on a truth table."""
        rng = random.Random(1)
        for k in (1, 2, 3, 4, 5, 6):
            for _ in range(20):
                gate = random_gate(k, rng)
                table = phase_table(k, gate)
                T = GC.tensor(k, gate)
                for _ in range(30):
                    u, v, w = (rng.randrange(1 << k) for _ in range(3))
                    total = 0
                    for su, sv, sw in itertools.product((0, 1), repeat=3):
                        x = (u if su else 0) ^ (v if sv else 0) ^ (w if sw else 0)
                        total += (-1) ** (3 - su - sv - sw) * table[x]
                    total %= 8
                    self.assertEqual(total % 4, 0)
                    self.assertEqual(GC.evaluate(T, u, v, w), total // 4,
                                     f"k={k} gate={sorted(map(sorted, gate))}")

    def test_monomial_sets_and_tensors_correspond_one_to_one(self):
        """Distinct gates mod Clifford have distinct tensors; only the empty
        gate has the zero tensor."""
        for k in (1, 2, 3):
            seen = {}
            zero = GC.tensor(k, [])
            for gate in all_gates(k):
                key = GC.tensor(k, gate)
                self.assertNotIn(key, seen)
                self.assertEqual(key == zero, not gate)
                seen[key] = gate

    def test_the_reduction_round_trips_and_ignores_cliffords(self):
        """The literal reduction used below: a gate's own table reduces back to
        it, and S, Z, CZ, a global phase and an X-shift of the input leave the
        reduction unchanged -- so affine frames are covered by linear ones."""
        rng = random.Random(6)
        for k in (2, 3, 4, 5):
            for _ in range(40):
                gate = random_gate(k, rng)
                table = phase_table(k, gate)
                self.assertEqual(reduce_mod_clifford(k, table), gate)
                a, b = rng.sample(range(k), 2)
                shift = rng.randrange(1 << k)
                clifford = [(table[x ^ shift]
                             + 2 * (x >> a & 1) + 4 * (x >> b & 1)
                             + 4 * (x >> a & 1) * (x >> b & 1) + 3) % 8
                            for x in range(1 << k)]
                self.assertEqual(reduce_mod_clifford(k, clifford), gate)

    def test_a_frame_change_transforms_the_tensor_covariantly(self):
        rng = random.Random(2)
        for k in (2, 3, 4, 5, 6):
            for _ in range(15):
                gate = random_gate(k, rng)
                images = random_frame(k, rng)
                moved = reduce_mod_clifford(
                    k, apply_frame(k, phase_table(k, gate), images))
                T, TM = GC.tensor(k, gate), GC.tensor(k, moved)
                image = lambda u: _apply(images, u)
                for _ in range(30):
                    u, v, w = (rng.randrange(1 << k) for _ in range(3))
                    self.assertEqual(GC.evaluate(TM, u, v, w),
                                     GC.evaluate(T, image(u), image(v), image(w)))


def _apply(images, u):
    y = 0
    for i, v in enumerate(images):
        if u >> i & 1:
            y ^= v
    return y


class DecisionAgreesWithTheLiteralDefinition(unittest.TestCase):
    def literal_classes(self, k, gates):
        """Class id of each gate: the orbit under every A, taken literally."""
        canon = {}
        frames = list(all_gl(k))
        for gate in gates:
            table = phase_table(k, gate)
            orbit = {reduce_mod_clifford(k, apply_frame(k, table, A))
                     for A in frames}
            canon[gate] = min(sorted(tuple(sorted(tuple(sorted(m)) for m in g))
                                     for g in orbit))
        return canon

    def test_every_pair_at_k_2_and_3(self):
        for k in (2, 3):
            gates = list(all_gates(k))
            canon = self.literal_classes(k, gates)
            for left, right in itertools.combinations(gates, 2):
                self.assertEqual(GC.gl_isomorphic(k, left, right),
                                 canon[left] == canon[right],
                                 f"k={k} {sorted(map(sorted, left))} vs "
                                 f"{sorted(map(sorted, right))}")

    def test_random_pairs_at_k_4(self):
        rng = random.Random(3)
        k = 4
        gates = [random_gate(k, rng, density=rng.choice((0.15, 0.3, 0.5)))
                 for _ in range(40)]
        canon = self.literal_classes(k, gates)
        for left, right in itertools.combinations(gates, 2):
            self.assertEqual(GC.gl_isomorphic(k, left, right),
                             canon[left] == canon[right])

    def test_a_relabelled_gate_is_found_and_the_witness_checks_out(self):
        rng = random.Random(4)
        for k in (5, 6, 7, 8, 9, 10):
            for _ in range(4):
                gate = random_gate(k, rng, density=0.2)
                images = random_frame(k, rng)
                moved = reduce_mod_clifford(
                    k, apply_frame(k, phase_table(k, gate), images))
                found = GC.gl_transform(k, gate, moved)
                self.assertNotIn(found, (None, False), f"k={k}")
                basis, witness = found
                TL, TR = GC.tensor(k, gate), GC.tensor(k, moved)
                self.assertEqual(GC._rank(witness), k)
                for i, j, l in itertools.product(range(k), repeat=3):
                    self.assertEqual(
                        GC.evaluate(TL, witness[i], witness[j], witness[l]),
                        GC.evaluate(TR, basis[i], basis[j], basis[l]))
                self.assertEqual(GC.gl_fingerprint(k, gate),
                                 GC.gl_fingerprint(k, moved))

    def test_labels_can_agree_on_gates_that_are_not_one_class(self):
        """The verdict that keeps duplicates out when every invariant agrees.

        ``A`` and ``B`` share the full label multiset (so the label pass cannot
        separate them) and the search must finish with ``False``.  That is
        certified here against the definition itself: every one of the
        9,999,360 elements of GL(5,2) is applied to ``A``'s Z_8 truth table,
        reduced modulo Clifford, and none reproduces ``B``.  A positive control
        -- ``A`` in a random frame -- must be found by the same enumeration, so
        the ``False`` is not an enumeration that finds nothing.
        """
        k = 5
        mono = lambda *m: frozenset(frozenset(x) for x in m)
        A = mono((0, 1), (0, 1, 2), (0, 2, 4), (0, 3, 4), (1, 2), (1, 2, 3),
                 (2, 3), (3, 4), (4,))
        B = mono((0, 1, 3), (0, 2), (0, 2, 4), (0, 3), (1,), (1, 3), (2,),
                 (3, 4))
        self.assertEqual(GC.gl_fingerprint(k, A), GC.gl_fingerprint(k, B))
        self.assertIs(GC.gl_isomorphic(k, A, B), False)
        frame = random_frame(k, random.Random(9))
        self.assertIn(tuple(frame), set(all_gl_small_check(k, frame)))
        control = reduce_mod_clifford(
            k, apply_frame(k, phase_table(k, A), frame))
        self.assertIs(GC.gl_isomorphic(k, A, control), True)
        orbit_hits = literal_orbit_contains(k, A, [B, control])
        self.assertEqual(orbit_hits, [False, True])

    def test_a_permutation_is_decided_above_the_label_cap(self):
        """Wide rows are T on every output or disjoint CCZs: a relabelling of
        one must be decided, with a checkable witness, and fast."""
        rng = random.Random(7)
        k = GC.LABEL_K_CAP + 6
        gate = random_gate(k, rng, density=0.02)
        perm = list(range(k))
        rng.shuffle(perm)
        moved = frozenset(frozenset(perm[q] for q in m) for m in gate)
        started = time.time()
        found = GC.gl_transform(k, gate, moved)
        self.assertLess(time.time() - started, 5.0)
        self.assertNotIn(found, (None, False))
        basis, images = found
        TL, TR = GC.tensor(k, gate), GC.tensor(k, moved)
        for _ in range(3000):
            i, j, l = (rng.randrange(k) for _ in range(3))
            self.assertEqual(GC.evaluate(TL, images[i], images[j], images[l]),
                             GC.evaluate(TR, basis[i], basis[j], basis[l]))

    def test_a_wide_gate_with_no_canonical_frame_is_decided(self):
        """The six catalogue rows whose k! minimisation was never proved must
        still be recognised in another labelling: `skcanon.sk_isomorphism`
        supplies the permutation, since they have no canonical form to compare.
        """
        import json
        from pathlib import Path
        catalogue = json.loads(
            (HERE.parent / "master_catalog.json").read_text())
        wide = [r for r in catalogue["factories"] if r["sk_key"] is None]
        self.assertTrue(wide, "the fixture rows must exist")
        rng = random.Random(11)
        for row in wide:
            k = row["k"]
            gate = frozenset(
                frozenset(m) for m in _gate_of(row))
            perm = list(range(k))
            rng.shuffle(perm)
            moved = frozenset(frozenset(perm[q] for q in m) for m in gate)
            started = time.time()
            self.assertIs(GC.gl_isomorphic(k, gate, moved), True,
                          f"[[{row['n']},{k}]] in another labelling")
            self.assertLess(time.time() - started, 30.0)

    def test_above_the_label_cap_an_unsettled_pair_is_none_at_once(self):
        """No 2^k enumeration: a CNOT-frame copy of a wide gate is not proved
        either way, and saying so must be immediate, not an out-of-memory."""
        rng = random.Random(8)
        k = GC.LABEL_K_CAP + 14
        gate = frozenset(frozenset((q,)) for q in range(k)) | {
            frozenset((0, 1, 2))}
        # substitute x0 -> x0 + x1 symbolically: T0 becomes T0.T1.CS01, and
        # CCZ012 becomes CCZ012 + CCZ112 = CCZ012 (x1^2 = x1: CS12 terms)
        moved = (gate - {frozenset((0,))}) | {frozenset((0, 1))}
        started = time.time()
        verdict = GC.gl_isomorphic(k, gate, moved)
        self.assertLess(time.time() - started, 5.0)
        self.assertIsNone(verdict, "an undecided pair is None, never False")
        self.assertIs(GC.gl_isomorphic(k, gate, gate), True)

    def test_known_pairs(self):
        t = lambda *m: frozenset(frozenset(x) for x in m)
        # T0.T1 = T0.CS01 up to x1 -> x0 + x1 and an S
        self.assertTrue(GC.gl_isomorphic(2, t((0,), (1,)), t((0,), (0, 1))))
        # but not the same as a lone CS, whose tensor has no T on any vector
        self.assertFalse(GC.gl_isomorphic(2, t((0,), (1,)), t((0, 1))))
        # T x CCZ is not T0.T1.T2.T3
        self.assertFalse(GC.gl_isomorphic(
            4, t((0,), (1, 2, 3)), t((0,), (1,), (2,), (3,))))
        # the empty gate is only equivalent to itself
        self.assertTrue(GC.gl_isomorphic(3, t(), t()))
        self.assertFalse(GC.gl_isomorphic(3, t(), t((0,))))

    def test_the_search_reports_exhaustion_as_none_not_false(self):
        rng = random.Random(5)
        k = 8
        gate = random_gate(k, rng, density=0.25)
        moved = reduce_mod_clifford(
            k, apply_frame(k, phase_table(k, gate), random_frame(k, rng)))
        self.assertIsNone(GC.gl_isomorphic(k, gate, moved, node_budget=1))

    def test_malformed_monomials_are_refused(self):
        with self.assertRaises(ValueError):
            GC.tensor(3, [frozenset((0, 3))])
        with self.assertRaises(ValueError):
            GC.tensor(4, [frozenset((0, 1, 2, 3))])


if __name__ == "__main__":
    unittest.main()
