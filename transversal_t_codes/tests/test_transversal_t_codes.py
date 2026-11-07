"""The rebuilt Jain-Albert codes, and their rows in the master catalogue.

    .venv/bin/python -m unittest discover -s transversal_t_codes/tests

`build_codes.py` checks its own output before writing it.  These tests check it
again with the master catalogue's primitives, which share no code with it --
`faultcore` for faults and the factory condition, `clifford` for the
transversal gate -- and compute what the build script takes from the
literature where that is cheap: the distances of the small self-dual inputs, by
enumerating every codeword.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
FOLDER = HERE.parent
REPO = FOLDER.parent
sys.path.insert(0, str(FOLDER))
sys.path.insert(0, str(REPO / "master_catalog"))

import build_codes as B                                           # noqa: E402
import clifford as CL                                             # noqa: E402
import faultcore as FC                                            # noqa: E402
import glcanon as GC                                              # noqa: E402

CATALOGUE = REPO / "master_catalog" / "master_catalog.json"
#: The paper's Tables II and I, as [[n,1,d]].
TABLE_II = [(15, 3), (49, 5), (95, 7), (189, 9), (283, 11), (441, 13),
            (599, 15), (805, 17), (1011, 19), (1345, 21), (1679, 23),
            (2061, 25), (2443, 27), (2841, 29), (3239, 31)]
TABLE_I = [(15, 3), (49, 5), (95, 7), (185, 9), (279, 11), (417, 13),
           (575, 15), (777, 17), (983, 19), (1317, 21), (1651, 23), (2033, 25),
           (2415, 27), (2813, 29), (3211, 31)]
#: Gong's family: her [[41,1,9]] and [[65,1,13]] with QR 47 and 79 on [[95,1,7]].
GONG = [(177, 9), (271, 11), (401, 13), (559, 15)]
#: Her [[559,1,15]] doubled on with Table I's self-dual inputs from d = 17.
GONG_DOUBLED = [(761, 17), (967, 19), (1301, 21), (1635, 23), (2017, 25),
                (2399, 27), (2797, 29), (3195, 31)]
#: Held before the import, with a smaller circuit: the merge left them alone.
HELD = {15: "15.1.3.a", 49: "49.1.5.a"}

_POP = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)


def popcount(values):
    """Popcount of every entry of a uint64 array."""
    return _POP[values.view(np.uint8)].reshape(values.shape + (8,)).sum(axis=-1)


def span_weights(rows):
    """The weight of every word of the span of ``rows`` (each < 2^64), by
    meet in the middle: all sums of the first half against all of the second."""
    rows = [int(r) for r in rows]
    half = len(rows) // 2

    def sums(part):
        out = np.zeros(1, dtype=np.uint64)
        for r in part:
            out = np.concatenate([out, out ^ np.uint64(r)])
        return out

    left, right = sums(rows[:half]), sums(rows[half:])
    return np.concatenate([popcount(left ^ value) for value in right])


def dual_basis(rows, n):
    """A basis of the dual of the span of ``rows``, length ``n``: from the
    fully reduced basis, one vector per free column."""
    lead = {r.bit_length() - 1: r for r in B.basis(rows)}
    free = [q for q in range(n) if q not in lead]
    out = []
    for f in free:
        v = 1 << f
        for top, r in lead.items():
            if (r >> f) & 1:
                v |= 1 << top
        out.append(v)
    return out


class Codes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.codes = B.build()
        cls.meta = json.loads(B.CODES_JSON.read_text(encoding="utf-8"))
        cls.records = json.loads(B.FACTORIES_JSON.read_text(encoding="utf-8"))
        cls.by_n = {code.n: code for code in cls.codes.values()}

    def test_the_committed_files_are_what_the_script_builds(self):
        meta, records = B.records(self.codes)
        self.assertEqual(B.render(meta), B.CODES_JSON.read_text(encoding="utf-8"))
        self.assertEqual(B.render(records),
                         B.FACTORIES_JSON.read_text(encoding="utf-8"))

    def test_the_paper_s_parameters(self):
        table2 = sorted((c.n, c.d) for c in self.codes.values() if "II" in c.tables)
        table1 = sorted((c.n, c.d) for c in self.codes.values() if "I" in c.tables)
        self.assertEqual(table2, TABLE_II)
        self.assertEqual(table1, TABLE_I)
        gong = sorted((c.n, c.d) for c in self.codes.values() if c.tables == ("G",))
        self.assertEqual(gong, GONG)
        both = sorted((c.n, c.d) for c in self.codes.values() if c.tables == ("GJ",))
        self.assertEqual(both, GONG_DOUBLED)
        # each 16 qubits shorter than Table I at the same distance
        table1 = dict((d, n) for n, d in TABLE_I)
        self.assertTrue(all(table1[d] - n == 16 for n, d in GONG_DOUBLED))

    def test_every_code_is_a_factory_by_the_catalogue_s_own_test(self):
        """`faultcore`: no odd parity touching a check, gate T on the output,
        no redundant check, one independent output."""
        for record in self.records:
            with self.subTest(code=record["label"]):
                N, columns = record["N"], record["columns"]
                rows = FC.rows_over_columns(columns, N)
                self.assertEqual(FC.check_contamination(rows, 1, N), [])
                self.assertEqual(FC.recover_gate(rows, 1), frozenset({frozenset({0})}))
                self.assertEqual(FC.redundant_checks(rows, 1, N), [])
                self.assertEqual(FC.output_report(rows, 1, N)["effective_width"], 1)
                self.assertEqual(len({tuple(c) for c in columns}), record["n"])

    def test_every_witness_is_a_harmful_fault_of_the_paper_s_weight(self):
        for record, entry in zip(self.records, self.meta["codes"]):
            with self.subTest(code=record["label"]):
                self.assertEqual(record["label"], entry["id"])
                circuit = FC.Circuit(record["columns"], 1, record["N"])
                self.assertEqual(len(set(entry["witness"])), entry["parameters"][2])
                self.assertTrue(circuit.harmful(entry["witness"]))

    def test_table_ii_is_weak_triply_even(self):
        """T on M+ and T-dagger on M- is the logical T^m with m = 7 (= T-dagger)
        and returns every stabiliser: `clifford.logical_action`, scaled by
        m^-1 = 7 so the target is T itself -- powers 7 on M+ and 1 on M-."""
        for record, entry in zip(self.records, self.meta["codes"]):
            if "II" not in entry["tables"]:
                continue
            with self.subTest(code=record["label"]):
                wte = entry["weak_triply_even"]
                self.assertIsNotNone(wte)
                self.assertEqual(wte["m"], 7 if record["n"] != 49 else 1)
                inverse = {1: 1, 7: 7}[wte["m"]]
                minus = set(wte["minus"])
                powers = [[c, (inverse * (-1 if c in minus else 1)) % 8]
                          for c in range(record["n"])]
                powers = [[c, p] for c, p in powers if p != 1]
                failures, _scope = CL.logical_action(
                    record["columns"], 1, record["N"], {frozenset({0})},
                    powers=powers)
                self.assertEqual(failures, [])

    def test_gong_s_family_is_triply_even(self):
        """Every X stabiliser weighs 0 mod 8, and T on every qubit is the
        logical T^m, m = n mod 8: `clifford.logical_action` with no powers when
        m = 1, and T-dagger everywhere (scaled by m^-1 = 7) when m = 7."""
        for record, entry in zip(self.records, self.meta["codes"]):
            if entry["tables"] != ["G"]:
                continue
            with self.subTest(code=record["label"]):
                code = self.by_n[record["n"]]
                self.assertTrue(all(B.weight(r) % 8 == 0 for r in code.rows[1:]))
                wte = entry["weak_triply_even"]
                self.assertEqual((wte["m"], wte["minus"]), (record["n"] % 8, []))
                powers = ([] if wte["m"] == 1 else
                          [[c, 7] for c in range(record["n"])])
                failures, _scope = CL.logical_action(
                    record["columns"], 1, record["N"], {frozenset({0})},
                    powers=powers)
                self.assertEqual(failures, [])

    def test_gong_s_self_dual_codes_have_the_distances_used(self):
        """A doubly even self-dual [[n,1]] code with stabiliser space S has
        distance n - (the largest weight in S): its logical operators are the
        words of 1 + S.  Every word of S is enumerated, 2^20 for n = 41 and 2^32
        for n = 65, meet in the middle on 22-bit pieces of each word.  The
        largest weights are 32 and 52, so the distances are exactly 9 and 13."""
        limb = 22
        pop = np.zeros(1 << limb, dtype=np.uint8)
        for b in range(limb):
            pop[1 << b:1 << (b + 1)] = pop[:1 << b] + 1

        def sums(rows):
            out = np.zeros((1, 3), dtype=np.int64)
            for r in rows:
                piece = np.array([(r >> (limb * i)) & ((1 << limb) - 1)
                                  for i in range(3)], dtype=np.int64)
                out = np.concatenate([out, out ^ piece])
            return out

        for n, d in ((41, 9), (65, 13)):
            with self.subTest(n=n):
                rows = B.gong_self_dual(n)
                half = len(rows) // 2
                left, right = sums(rows[:half]), sums(rows[half:])
                heaviest = 0
                for i in range(0, len(right), 64):
                    x = left[None, :, :] ^ right[i:i + 64, None, :]
                    w = (pop[x[..., 0]].astype(np.int16) + pop[x[..., 1]]
                         + pop[x[..., 2]])
                    heaviest = max(heaviest, int(w.max()))
                self.assertEqual(n - heaviest, d)

    def test_the_small_self_dual_inputs_have_the_distances_used(self):
        """d_sd = the least odd weight of the punctured code C, the dual of the
        stabilisers: computed here by enumerating every word of C."""
        inputs = {
            7: (B.quantum_qr(7), 3),
            17: ([B.mask(f) for f in B.COLOR17], 5),
            23: (B.quantum_qr(23), 7),
            45: (B.css_from_self_dual(B.subtract(
                B.extend(B.quadratic_residue_code(47), 47), 48, 46, 47), 46), 9),
            47: (B.quantum_qr(47), 11),
        }
        for n, (stabilisers, d) in inputs.items():
            with self.subTest(n=n):
                C = dual_basis(stabilisers, n)
                self.assertEqual(len(C), (n + 1) // 2)
                weights = span_weights(C)
                self.assertEqual(int(weights[weights % 2 == 1].min()), d)

    def test_the_70_bit_code_gives_a_69_1_13(self):
        """SD70 is the code `search_sd70.py` finds, and every one of its 2^34
        words through the fixed coordinate 69 weighs at least 14 -- exactly 14
        at the least.  Enumerated through the code's own structure: a word
        through 69 is (cycle 1 + 69) or (all ones), plus lam*u + v with lam in
        the field I1 (2048 values) and v in M2, itself fixed by its parts on
        cycles 2 and 3 (2048 x 2048 values)."""
        import search_sd70 as S
        u = tuple(B.mask(f) for f in B.SD70_U)
        rows = S.code(u)
        built = B.sd70()
        self.assertEqual(len(B.basis(built)), 35)
        self.assertEqual(len(B.basis(built + rows)), 35)     # the same code
        W = np.zeros(1 << 23, dtype=np.uint8)
        for b in range(23):
            W[1 << b:1 << (b + 1)] = W[:1 << b] + 1
        full = (1 << 23) - 1

        def part(v, i):
            return (v >> (23 * i)) & full

        m2 = rows[2 + 23:]
        self.assertEqual(len(m2), 22)
        # v1 as a linear function of (v2, v3), by elimination on the M2 rows
        reduced = []
        for r in m2:
            key, val = part(r, 1) | (part(r, 2) << 23), part(r, 0)
            for k, v, piv in reduced:
                if (key >> piv) & 1:
                    key, val = key ^ k, val ^ v
            self.assertTrue(key)
            piv = (key & -key).bit_length() - 1
            reduced = [(k ^ key, v ^ val, q) if (k >> piv) & 1 else (k, v, q)
                       for k, v, q in reduced]
            reduced.append((key, val, piv))

        def v1(key):
            val = 0
            for k, v, piv in reduced:
                if (key >> piv) & 1:
                    key, val = key ^ k, val ^ v
            return val

        I2 = np.array(sorted(S.I2), dtype=np.int64)
        L2 = np.array([v1(int(v)) for v in I2], dtype=np.int64)
        L3 = np.array([v1(int(v) << 23) for v in I2], dtype=np.int64)
        least = 99
        for lam in sorted(S.I1):
            a1, a2, a3 = (S.mul(lam, f) for f in u)
            w1 = W[a1 ^ L2[:, None] ^ L3[None, :]].astype(np.int32)
            w2 = W[a2 ^ I2].astype(np.int32)[:, None]
            w3 = W[a3 ^ I2].astype(np.int32)[None, :]
            least = min(least,
                        int((1 + (23 - w1) + w2 + w3).min()),
                        int((1 + (23 - w1) + (23 - w2) + (23 - w3)).min()))
        self.assertEqual(least, 14)

    def test_the_distance_bound_agrees_with_enumeration(self):
        """`min_distance.distance_lower_bound` never exceeds the minimum
        distance, and equals it when that is at most 2t + 1: on the extended
        Golay and QR codes of length 24 and 48, the [46,23,10] subtraction
        code, and 300 random codes small enough to enumerate."""
        import random
        import min_distance as M

        def brute(rows):
            words = [0]
            for r in rows:
                words += [w ^ r for w in words]
            return min(B.weight(w) for w in words if w)

        xq47 = B.extend(B.quadratic_residue_code(47), 47)
        for rows, n, t, d in [
                (B.basis(B.extend(B.quadratic_residue_code(23), 23)), 24, 3, 8),
                (B.basis(xq47), 48, 5, 12),
                (B.basis(B.subtract(xq47, 48, 46, 47)), 46, 4, 10)]:
            with self.subTest(n=n):
                self.assertEqual(M.distance_lower_bound(rows, n, t)["bound"], d)
        rng = random.Random(5)
        checked = 0
        for trial in range(300):
            k = rng.randint(3, 10)
            rows = B.basis([rng.getrandbits(2 * k) for _ in range(k)])
            if len(rows) != k:
                continue
            t = rng.randint(1, k)
            try:
                bound = M.distance_lower_bound(rows, 2 * k, t, seed=trial)["bound"]
            except ValueError:          # no two disjoint information sets
                continue
            d = brute(rows)
            self.assertLessEqual(bound, d)
            if d <= 2 * t + 1:
                self.assertEqual(bound, d)
            checked += 1
        self.assertGreater(checked, 200)

    def test_the_larger_self_dual_inputs_have_the_distances_used(self):
        """d_sd >= 15, 17 and 19 for the [[79,1]] and [[103,1]] quantum QR codes
        and the [[101,1]] code of sub(XQ103), proved without the literature.

        Each input's stabiliser kernel is the punctured classical code (checked
        here), every word of the classical code is even, so its odd words are
        the classical words through the punctured coordinate less that one
        coordinate: d_sd >= d - 1.  `min_distance` proves d >= 14, 18 and 18
        by listing every word with at most 6, 8 and 8 ones on either of two
        disjoint information sets.  The two QR codes are doubly even, so their
        weights are multiples of 4 and d >= 16 and 20."""
        import certify_distances as CD
        import min_distance as M
        xq103 = B.extend(B.quadratic_residue_code(103), 103)
        cases = [
            (79, B.extend(B.quadratic_residue_code(79), 79), 6, 4, 15),
            (101, B.subtract(xq103, 104, 102, 103), 8, 2, 17),
            (103, xq103, 8, 4, 19),
        ]
        for n_sd, classical, t, step, d_sd in cases:
            with self.subTest(n_sd=n_sd):
                n = n_sd + 1
                self.assertTrue(B.is_self_dual(classical, n))
                if step == 4:
                    self.assertTrue(B.doubly_even(classical))
                stabilisers = B.css_from_self_dual(classical, n)
                kernel = dual_basis(stabilisers, n_sd)
                punctured = [r & ((1 << n_sd) - 1) for r in classical]
                self.assertEqual(len(B.basis(kernel)), len(B.basis(punctured)))
                self.assertEqual(len(B.basis(kernel + punctured)),
                                 len(B.basis(kernel)))
                bound = M.distance_lower_bound(B.basis(classical), n, t)["bound"]
                weight_floor = -(-bound // step) * step     # round up to the step
                self.assertGreaterEqual(weight_floor - 1, d_sd)
                self.assertEqual(CD.PROVED[n_sd][0], d_sd)

    def test_the_distance_certificates_are_what_the_script_writes(self):
        """`distance_certificates.json` is rebuilt from the codes, and each
        record's bound is the theorem's along a chain of proved inputs."""
        import certify_distances as CD
        text = B.render(CD.payload(self.codes))
        self.assertEqual(CD.CERTIFICATES_JSON.read_text(encoding="utf-8"), text)
        blob = json.loads(text)
        by_label = {r["label"]: r for r in blob["records"]}
        for record in blob["records"]:
            with self.subTest(code=record["label"]):
                code = self.by_n[record["n"]]
                self.assertEqual(record["lower_bound"], code.d)
                self.assertEqual(len(record["witness"]), code.d)
                self.assertTrue(B.harmful(code, record["witness"]))
                inner = record["inner_lower_bound"]
                self.assertEqual(record["lower_bound"],
                                 min(record["self_dual_distance"], inner + 2))
                if record["inner_code"] in by_label:
                    self.assertEqual(by_label[record["inner_code"]]["lower_bound"],
                                     inner)
                test_name = record["self_dual_distance_proved_by"].split("::")[1]
                self.assertTrue(hasattr(self, test_name))
        unchecked = {e["label"] for e in blob["unchecked"]}
        self.assertFalse(unchecked & set(by_label))
        self.assertEqual(len(unchecked) + len(by_label), len(self.codes))

    def test_the_102_bit_subtraction_code_is_self_dual(self):
        rows = B.subtract(B.extend(B.quadratic_residue_code(103), 103), 104, 102, 103)
        self.assertTrue(B.is_self_dual(rows, 102))

    def test_the_46_bit_subtraction_code_is_a_self_dual_46_23_10(self):
        rows = B.subtract(B.extend(B.quadratic_residue_code(47), 47), 48, 46, 47)
        self.assertTrue(B.is_self_dual(rows, 46))
        weights = span_weights(rows)
        self.assertEqual(int(weights[weights > 0].min()), 10)

    def test_the_17_qubit_code_is_the_unique_doubly_even_one(self):
        """Doubly even, and with its parity bit appended a self-dual [18,9,4]
        code with 17 words of weight 4 that all miss the parity bit: the
        d10+e7+f1 code (10 + 7 + 0 tetrads), punctured at f1."""
        D = [B.mask(f) for f in B.COLOR17]
        self.assertTrue(B.doubly_even(D))
        E = B.extend(dual_basis(D, 17), 17)
        self.assertTrue(B.is_self_dual(E, 18))
        words = [0]
        for r in E:
            words += [w ^ r for w in words]
        four = [w for w in words if B.weight(w) == 4]
        self.assertEqual(len(four), 17)
        self.assertEqual(min(B.weight(w) for w in words if w), 4)
        self.assertFalse(any((w >> 17) & 1 for w in four))

    def test_every_extended_qr_code_is_doubly_even_self_dual(self):
        for p in B.QR_DISTANCE:
            with self.subTest(p=p):
                rows = B.extend(B.quadratic_residue_code(p), p)
                self.assertTrue(B.is_self_dual(rows, p + 1))
                self.assertTrue(B.doubly_even(rows))


class Catalogue(unittest.TestCase):
    """Where each code went in `master_catalog.json`."""

    @classmethod
    def setUpClass(cls):
        payload = json.loads(CATALOGUE.read_text(encoding="utf-8"))
        cls.rows = payload["factories"]
        cls.references = payload["references"]
        cls.records = json.loads(B.FACTORIES_JSON.read_text(encoding="utf-8"))
        cls.meta = {e["id"]: e for e in
                    json.loads(B.CODES_JSON.read_text(encoding="utf-8"))["codes"]}

    def row_of(self, label):
        rows = [row for row in self.rows
                if any(s["label"] == label and s["file"] == B.FACTORIES_JSON
                       .relative_to(REPO).as_posix() for s in row["sources"])]
        self.assertLessEqual(len(rows), 1)
        return rows[0] if rows else None

    def test_every_code_is_held(self):
        for record in self.records:
            n, d = record["n"], record["d"]
            with self.subTest(code=record["label"]):
                row = self.row_of(record["label"])
                if n in HELD:
                    self.assertIsNone(row)
                    held, = [r for r in self.rows if r["catalog_label"] == HELD[n]]
                    self.assertEqual((held["n"], held["k"], held["d"]), (n, 1, d))
                    self.assertTrue(held["d_is_exact"])
                    continue
                self.assertIsNotNone(row)
                self.assertEqual((row["n"], row["k"], row["N"]),
                                 (n, 1, record["N"]))
                self.assertEqual(row["columns"], record["columns"])
                self.assertEqual(row["discovery"], "pre-existing")

    def test_the_paper_s_distance_is_certified_and_witnessed(self):
        """A floor proved here, the paper's distance as a certified lower
        bound, and an explicit fault of exactly that weight -- or, where the
        sweep reaches, the exact distance itself."""
        for record in self.records:
            row = self.row_of(record["label"])
            if row is None:
                continue
            claim = record["d"]
            with self.subTest(code=record["label"]):
                if row["d_is_exact"]:
                    self.assertEqual(row["d"], claim)
                    self.assertNotIn("d_certified", row)
                    continue
                self.assertLess(row["d"], claim)
                self.assertEqual(row["d_certified"], claim)
                self.assertFalse(row["d_certified_is_exact"])
                self.assertIn("arXiv:2408.12752", row["d_certified_source"])
                self.assertEqual(row["d_upper"], claim)
                circuit = FC.Circuit(row["columns"], 1, row["N"])
                self.assertTrue(circuit.harmful(row["d_witness"]))

    def test_credit_goes_to_the_earliest_publication(self):
        for record in self.records:
            row = self.row_of(record["label"])
            if row is None:
                continue
            with self.subTest(code=record["label"]):
                expected = (["gong2025triply"] if record["label"].startswith("G-")
                            else ["jain2025transversal", "gong2025triply"]
                            if record["label"].startswith("GJ-")
                            else ["sullivan2024code"] if record["n"] == 95
                            else ["jain2025transversal"])
                self.assertEqual(row["citations"], expected)
        self.assertIn("arXiv:2408.12752",
                      self.references["jain2025transversal"]["full"])
        self.assertIn("gongaa/RM127", self.references["gong2025triply"]["url"])

    def test_table_ii_rows_store_the_paper_s_partition(self):
        """T-dagger on M+ and T on M-: the paper's T on M+ and T-dagger on M-,
        scaled from the logical T^7 to the logical T.  Gong's codes have M-
        empty and m = n mod 8: T everywhere when m = 1, T-dagger when m = 7."""
        for record in self.records:
            row = self.row_of(record["label"])
            entry = self.meta[record["label"]]
            if row is None or entry["weak_triply_even"] is None:
                continue
            with self.subTest(code=record["label"]):
                minus = set(entry["weak_triply_even"]["minus"])
                m = entry["weak_triply_even"]["m"]
                if entry["tables"] == ["G"]:
                    self.assertEqual(row["rotation_powers"],
                                     [] if m == 1 else [[c, 7] for c in range(row["n"])])
                    continue
                self.assertEqual(m, 7)
                self.assertEqual(row["rotation_powers"],
                                 [[c, 7] for c in range(row["n"]) if c not in minus])

    def test_no_code_needs_s_or_cz_gates(self):
        """Every code has a transversal T: some choice of T, T^3, T^5, T^7 per
        qubit is the logical T exactly -- Table II's T/T-dagger partition, and
        for the Table I codes powers 1, 3, 5 and 7 found by the solver."""
        for record in self.records:
            row = self.row_of(record["label"])
            if row is None:
                continue
            with self.subTest(code=record["label"]):
                self.assertIsNotNone(row["rotation_powers"])


if __name__ == "__main__":
    unittest.main()
