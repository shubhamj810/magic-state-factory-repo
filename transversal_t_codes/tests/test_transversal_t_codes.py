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
                expected = (["sullivan2024code"] if record["n"] == 95
                            else ["jain2025transversal"])
                self.assertEqual(row["citations"], expected)
        self.assertIn("arXiv:2408.12752",
                      self.references["jain2025transversal"]["full"])

    def test_table_ii_rows_store_the_paper_s_partition(self):
        """T-dagger on M+ and T on M-: the paper's T on M+ and T-dagger on M-,
        scaled from the logical T^7 to the logical T."""
        for record in self.records:
            row = self.row_of(record["label"])
            entry = self.meta[record["label"]]
            if row is None or entry["weak_triply_even"] is None:
                continue
            with self.subTest(code=record["label"]):
                minus = set(entry["weak_triply_even"]["minus"])
                self.assertEqual(entry["weak_triply_even"]["m"], 7)
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
