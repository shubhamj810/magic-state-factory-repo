"""`construction_sanjose`: the San José builder and its hypothesis check.

* **The catalogue rows.**  742.36.8.a and 756.32.6.a came from the
  gamma-frontier release's San José records ``sj_m6_L62_deg15_P9`` and
  ``..._P8``.  The builder gives their columns exactly, in the stored order
  too (the catalogue keeps them in build order, with no relabelling of
  outputs), and `hypothesis_check` proves d >= 8 and d >= 9 on the stored
  columns.
* **Corrupted circuits** fail the check: a flipped bit, a dropped or added
  column, a wrong construction, and, with the alignment step bypassed,
  circuits whose algebra is wrong.
* **Shapes** that `problems` must refuse.
* **Research rows** rebuilt byte for byte: the research's own digest of the
  build-order columns, and the digest of the sorted columns pinned here.
* **A curve row** (``cv_t2_a130_P102`` of the sanjose2 search) rebuilt to
  the research's digest, its bound proved and its fault re-checked.
"""
from __future__ import annotations

import copy
import functools
import sys
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE.parent
sys.path.insert(0, str(CATALOGUE))

import catalogfile as CF                                          # noqa: E402
import construction_sanjose as SJ                                 # noqa: E402
import constructions as K                                         # noqa: E402
import faultcore as FC                                            # noqa: E402

#: The release's field data, shared by all its records of one field degree
#: (gamma_frontier_release/sources/pass4/san_jose/normalized.json).
FIELD = {
    4: (19, [1, 3, 5, 6, 8, 14, 15], [15, 13, 11]),
    6: (67, [1, 4, 7, 8, 10, 11, 12, 27, 29, 34, 43, 44, 50, 54],
        [63, 61, 41, 37]),
    7: (131, [4, 10, 16, 23, 34, 42, 61, 63, 73, 76, 81, 88, 98, 104, 113,
              114, 122, 125], [127, 125, 57, 9]),
    8: (283, [2, 10, 14, 18, 32, 57, 68, 69, 72, 85, 91, 96, 107, 124, 140,
              160, 187, 205, 207, 208, 216], [223, 218, 208, 198, 115]),
}


def grs(m, L, D, R, echelon):
    mod, emb, U = FIELD[m]
    k = len(R) * len(U)
    return {"family": "san-jose-grs", "k": k, "N": k + m * (D + 1 - len(R)),
            "field_degree": m, "field_modulus": mod,
            "embedding_columns": list(emb), "compatible_elements": list(U),
            "outer_length": L, "outer_degree": D, "punctures": list(R),
            "echelon": echelon}


ROW_742 = grs(6, 62, 15, range(9), "reduced")
ROW_756 = grs(6, 62, 15, range(8), "reduced")

#: (research id, construction, research digest of the BUILD-order columns,
#: digest of the sorted columns as this builder gives them).
FIXTURE = [
    ("sparse sj_evidence.json sj_m4_L14_deg3_P1",
     grs(4, 14, 3, range(1), "reduced"),
     "e62febfbfde70a60a9059e9c753f55df2a6a8a090896fcb5630101be6e43df7f",
     "89c78d351b1b29e83412b4d7bfc130269172a901ece4b8eaef4b1c1f31e1161d"),
    ("sparse sjl_evidence.json sjL_m7_L126_deg31_P26",
     grs(7, 126, 31, range(26), "reduced"),
     "fe1e69d343520e68470a84ee0c960854357ba4d06ccc10504520466aca1e24f5",
     "a319ad4601191b3df2e304a13608e6b864fd4f71ca6543d2528168b80f22c169"),
    ("sparse sjl_evidence.json sjL_m8_L254_deg63_P55",
     grs(8, 254, 63, range(55), "reduced"),
     "4f041708df4d8648e4e6e9dac7e9d74ec6a566dd0cbaa8b3c4114e8ef201bfa5",
     "cb2537b12ce7f4b1904f2bfb83d5c9dfd3bad9fd7bcd33852fc91437db51a726"),
    ("sanjose2 factories.json fr_m7_L98_deg24_P17",
     grs(7, 98, 24, [59, 87, 85, 34, 32, 94, 33, 91, 65, 67, 61, 8, 81, 10,
                     83, 46, 57], "punctures"),
     "176ab77b5e8fe520d5315bacd9a455bb983deec8f6bc88d0062018bea3bfe332",
     "0591f4871889a35f43dc7ea0799228c92d979a19747a663a315bc3c22e3b1167"),
    ("sanjose2 factories.json ff_m8_L256_deg62_P54",
     grs(8, 256, 62, range(54), "punctures"),
     "933c71ba36cbccec0cd9b15b1935f153504c7d8ab6643cbcf97ba7723dfca7d6",
     "c1a7156ce9711bc27b08c76b71fef43e7a376a0348575035de69ca5371868eca"),
]


@functools.lru_cache(maxsize=1)
def stored_rows():
    rows = {}
    for r in CF.load_all()["factories"]:          # by label and by former label
        for name in [r["catalog_label"]] + (r.get("former_labels") or []):
            rows[name] = r
    return rows["742.36.8.a"], rows["756.32.9.a"]


class CatalogueRows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r742, cls.r756 = stored_rows()

    def test_filed_under_san_jose(self):
        """Both rows are San-Jose GRS codes of the gamma frontier release, and
        are filed under that regime (provenance_742_756_2026_11_07.py), not
        under Wills's parent codes."""
        for row in (self.r742, self.r756):
            self.assertEqual(row["regimes"],
                             ["AI search (gamma frontier): San José GRS construction"])
            self.assertIn("san_jose_grs", row["sources"][0]["origin"])

    def test_parameters(self):
        for row, c, d in ((self.r742, ROW_742, 8), (self.r756, ROW_756, 9)):
            built = SJ.build(c)
            self.assertEqual((built["n"], built["k"], built["N"]),
                             (row["n"], row["k"], row["N"]))
            self.assertEqual(SJ.bound(c), d)

    def test_columns_equal_sorted_stored(self):
        for row, c in ((self.r742, ROW_742), (self.r756, ROW_756)):
            self.assertEqual(SJ.columns(c), sorted(row["columns"]))
            self.assertEqual(SJ.digest(SJ.columns(c)),
                             K.digest(sorted(row["columns"])))

    def test_stored_order_is_build_order(self):
        # So no relabelling of outputs or checks: the catalogue keeps the
        # release's wire labels and column order.
        for row, c in ((self.r742, ROW_742), (self.r756, ROW_756)):
            self.assertEqual(SJ.build(c)["columns"], row["columns"])

    def test_hypothesis_check_proves_8_and_9(self):
        for row, c, d in ((self.r742, ROW_742, 8), (self.r756, ROW_756, 9)):
            for cols in (row["columns"], sorted(row["columns"])):
                out = SJ.hypothesis_check(cols, row["k"], row["N"], c)
                self.assertEqual(out["bound"], d)
                self.assertTrue(all(out["factory_side_conditions"].values()))
        # The bound does not exceed what the catalogue knows: 742.36.8.a is
        # exact at 8, and 756.32.6.a has a certified 9.
        self.assertEqual(self.r742["d_certified"], 8)
        self.assertEqual(self.r756["d_certified"], 9)

    def test_catalogue_witness_meets_the_bound(self):
        row = self.r742
        wit = list(row["d_witness"])
        self.assertEqual(len(wit), SJ.bound(ROW_742))
        circ = FC.Circuit(row["columns"], row["k"], row["N"])
        self.assertTrue(circ.harmful(wit))
        pos = SJ.sorted_positions(row["columns"])
        cols = SJ.columns(ROW_742)
        moved = [pos[j] for j in wit]
        self.assertTrue(FC.Circuit(cols, row["k"], row["N"]).harmful(moved))


class Corrupted(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.row = stored_rows()[0]
        cls.cols = SJ.columns(ROW_742)

    def fails(self, cols, k=None, N=None, c=None):
        with self.assertRaises(AssertionError):
            SJ.hypothesis_check(cols, self.row["k"] if k is None else k,
                                self.row["N"] if N is None else N,
                                ROW_742 if c is None else c)

    def test_flipped_bits(self):
        for j, wire in ((0, 0), (17, 40), (400, 77), (741, 5)):
            cols = copy.deepcopy(self.cols)
            col = set(cols[j]) ^ {wire}
            cols[j] = sorted(col)
            self.fails(cols)

    def test_dropped_added_and_repeated_columns(self):
        self.fails(self.cols[1:])
        self.fails(self.cols + [[0, 40]])
        self.fails(self.cols[:-1] + [self.cols[0]])

    def test_malformed_columns(self):
        cols = copy.deepcopy(self.cols)
        cols[3] = list(reversed(cols[3]))
        self.fails(cols)
        cols = copy.deepcopy(self.cols)
        cols[3] = cols[3] + [self.row["N"]]
        self.fails(cols)

    def test_wrong_construction(self):
        wrong = [grs(6, 62, 15, range(8), "reduced"),          # P = 8
                 grs(6, 62, 15, range(9), "punctures"),        # echelon
                 grs(6, 62, 15, [1, 0] + list(range(2, 9)), "reduced"),
                 grs(6, 62, 14, range(9), "reduced")]          # degree
        swapped = grs(6, 62, 15, range(9), "reduced")
        swapped["compatible_elements"] = [61, 63, 41, 37]
        wrong.append(swapped)
        for c in wrong:
            with self.assertRaises(AssertionError):
                SJ.hypothesis_check(self.cols, c["k"], c["N"], c)
        self.fails(self.cols, k=35)

    def test_algebra_is_checked_after_alignment(self):
        # Bypass the alignment with the builder: make `build` return the
        # corrupted columns, so only the decoding and the outer-code checks
        # stand between them and a pass.
        def fake(cols):
            return lambda c: {"columns": [list(x) for x in cols]}

        base = SJ.build(ROW_742)["columns"]
        # a flipped bit inside one block
        cols = copy.deepcopy(base)
        cols[5] = sorted(set(cols[5]) ^ {50})
        # two check wires exchanged
        swap = {40: 41, 41: 40}
        cols2 = [sorted(swap.get(w, w) for w in col) for col in base]
        # puncture order changed: wires of puncture 0 belong to coordinate 1
        other = SJ.build(grs(6, 62, 15, [1, 0] + list(range(2, 9)),
                             "reduced"))["columns"]
        # output wires with the compatible list in another order
        cU = grs(6, 62, 15, range(9), "reduced")
        cU["compatible_elements"] = [61, 63, 41, 37]
        cols4 = SJ.build(cU)["columns"]
        for bad, why in ((cols, "decode"), (cols2, "check wire"),
                         (other, "outer code"), (cols4, "output wire")):
            with mock.patch.object(SJ, "build", fake(bad)):
                with self.assertRaises(AssertionError) as err:
                    SJ.hypothesis_check(bad, 36, 78, ROW_742)
            self.assertNotIn("is not a column of this construction",
                             str(err.exception), why)
        # and the genuine columns pass the same path
        with mock.patch.object(SJ, "build", fake(base)):
            self.assertEqual(SJ.hypothesis_check(base, 36, 78,
                                                 ROW_742)["bound"], 8)


class Shapes(unittest.TestCase):
    def test_good(self):
        self.assertEqual(SJ.problems(ROW_742), [])
        for _, c, _, _ in FIXTURE:
            self.assertEqual(SJ.problems(c), [])

    def test_bad(self):
        def edit(**kw):
            c = copy.deepcopy(ROW_742)
            for key, value in kw.items():
                if value is KeyError:
                    del c[key]
                else:
                    c[key] = value
            return c

        bad = [
            None, [], "san-jose-grs",
            edit(family="two-group"), edit(family=None),
            edit(echelon=KeyError), edit(extra=1),
            edit(k=True), edit(k=35), edit(N=79), edit(field_degree=2),
            edit(field_degree=11), edit(field_degree=6.0),
            edit(field_modulus=65),            # x^6 + 1, reducible
            edit(field_modulus=67 + 128),      # degree 7, not 6
            edit(embedding_columns=[]), edit(embedding_columns=[1, 1, 4]),
            edit(embedding_columns=[0, 4]), edit(embedding_columns=[64]),
            edit(embedding_columns=list(range(1, 64))),
            edit(compatible_elements=[63, 63, 41, 37]),
            edit(compatible_elements=[1, 2, 3, 4, 5, 6, 7]),
            edit(outer_length=65), edit(outer_length=61),
            edit(outer_degree=0), edit(punctures=[]),
            edit(punctures=[0, 0, 1, 2, 3, 4, 5, 6, 7]),
            edit(punctures=[62] + list(range(8))),
            edit(punctures=[-1] + list(range(8))),
            edit(punctures=list(range(16)), k=64, N=64),
            edit(echelon="rref"), edit(echelon=None),
        ]
        for c in bad:
            self.assertTrue(SJ.problems(c), c)
            with self.assertRaises(ValueError):
                SJ.columns(c)

    def test_size_bound(self):
        c = grs(8, 256, 62, range(54), "punctures")
        self.assertEqual(SJ.problems(c), [])
        with mock.patch.object(SJ, "MAX_CELLS", 1000):
            self.assertTrue(any("cells" in p for p in SJ.problems(c)))


class ResearchRows(unittest.TestCase):
    def test_rebuild_byte_for_byte(self):
        for name, c, research, pinned in FIXTURE:
            built = SJ.build(c)
            self.assertEqual(SJ.digest(built["columns"]), research, name)
            cols = SJ.columns(c)
            self.assertEqual(cols, sorted(built["columns"]))
            self.assertTrue(all(col == sorted(col) for col in cols))
            self.assertEqual(SJ.digest(cols), pinned, name)
            self.assertEqual(SJ.digest(cols), K.digest(cols))
            self.assertEqual(SJ.canonical_text(cols), K.canonical_text(cols))

    def test_hypothesis_check_on_research_rows(self):
        for name, c, _, _ in FIXTURE:
            cols = SJ.columns(c)
            out = SJ.hypothesis_check(cols, c["k"], c["N"], c)
            self.assertEqual(out["bound"], SJ.bound(c), name)
            self.assertTrue(all(out["factory_side_conditions"].values()),
                            name)

    def test_chosen_puncture_witness(self):
        # fr_m7_L98_deg24_P17: the research's fault at the bound, given in
        # build order, moved to the sorted order and re-checked.
        _, c, _, _ = FIXTURE[3]
        built = SJ.build(c)
        wit = [311, 379, 622, 722, 1058, 1072, 1197, 1269, 1401]
        self.assertEqual(len(wit), SJ.bound(c))
        pos = SJ.sorted_positions(built["columns"])
        cols = SJ.columns(c)
        moved = [pos[j] for j in wit]
        self.assertTrue(FC.Circuit(cols, c["k"], c["N"]).harmful(moved))
        acc = 0
        for j in moved:
            for w in cols[j]:
                acc ^= 1 << w
        self.assertEqual(acc >> c["k"], 0)
        self.assertNotEqual(acc, 0)


#: sanjose2 factories.json cv_t2_a130_P102: the curve y^2 + y = x^17 over
#: GF(256) (K = {0, 1}), pole order 130, 102 chosen punctures.
CURVE_R = [356, 357, 164, 165, 434, 435, 488, 489, 376, 377, 138, 139, 496,
           497, 418, 419, 472, 473, 74, 75, 242, 243, 94, 95, 256, 257, 118,
           119, 268, 269, 72, 73, 422, 423, 38, 39, 276, 277, 208, 209, 354,
           355, 504, 505, 400, 401, 190, 191, 136, 137, 378, 379, 440, 441,
           170, 171, 42, 43, 204, 205, 158, 159, 450, 451, 292, 293, 306,
           307, 484, 485, 122, 123, 416, 417, 502, 503, 486, 487, 360, 361,
           90, 91, 414, 415, 420, 421, 86, 87, 232, 233, 76, 77, 348, 349,
           278, 279, 152, 153, 16, 17, 172, 173]
CURVE_DIGEST = ("60641603e540dc5fc6b5f1760d9c24f116eeb8700846d9cf55a43716"
                "192abd1f")
CURVE_FAULT = [1690, 1711, 4000, 4021, 4799, 4820, 6724, 6745, 7233, 7254,
               7312, 7333, 7855, 7876]


def curve(t_subspace, A, R, echelon="punctures"):
    mod, emb, U = FIELD[8]
    t = len(t_subspace)
    g = (t - 1) * 8
    k = len(R) * len(U)
    return {"family": "san-jose-curve", "k": k,
            "N": k + 8 * (A - g + 1 - len(R)), "field_degree": 8,
            "field_modulus": mod, "embedding_columns": list(emb),
            "compatible_elements": list(U), "curve_subspace": list(t_subspace),
            "curve_exponent": 17, "pole_order": A, "punctures": list(R),
            "echelon": echelon}


class CurveRows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = curve([0, 1], 130, CURVE_R)
        cls.built = SJ.build(cls.c)
        cls.cols = sorted(cls.built["columns"])

    def test_rebuild_and_bound(self):
        b = self.built
        self.assertEqual((b["n"], b["k"], b["N"]), (8610, 510, 678))
        self.assertEqual(SJ.digest(b["columns"]), CURVE_DIGEST)
        self.assertEqual(SJ.columns(self.c), self.cols)
        self.assertEqual(SJ.bound(self.c), 130 - 16 + 2 - 102)

    def test_hypothesis_check(self):
        out = SJ.hypothesis_check(self.cols, 510, 678, self.c)
        self.assertEqual(out["bound"], 14)
        self.assertEqual(out["dual_distance"], 116)
        self.assertTrue(all(out["factory_side_conditions"].values()))

    def test_fault_at_the_bound(self):
        pos = SJ.sorted_positions(self.built["columns"])
        moved = [pos[j] for j in CURVE_FAULT]
        self.assertEqual(len(set(moved)), 14)
        self.assertTrue(FC.Circuit(self.cols, 510, 678).harmful(moved))

    def test_corrupted(self):
        cols = copy.deepcopy(self.cols)
        cols[100] = sorted(set(cols[100]) ^ {600})
        with self.assertRaises(AssertionError):
            SJ.hypothesis_check(cols, 510, 678, self.c)
        with self.assertRaises(AssertionError):
            SJ.hypothesis_check(self.cols[:-1], 510, 678, self.c)
        other = curve([0, 1], 130, CURVE_R[1:] + CURVE_R[:1])
        with self.assertRaises(AssertionError):
            SJ.hypothesis_check(self.cols, 510, 678, other)
        # algebra after the alignment: the same circuit with the punctures
        # of the claimed construction in another order
        bad = SJ.build(other)["columns"]
        with mock.patch.object(SJ, "build", lambda c: {"columns": bad}):
            with self.assertRaises(AssertionError) as err:
                SJ.hypothesis_check(sorted(bad), 510, 678, self.c)
        self.assertIn("not in the outer code", str(err.exception))

    def test_bad_shapes(self):
        def edit(**kw):
            c = copy.deepcopy(self.c)
            c.update(kw)
            return c

        for c in (edit(curve_subspace=[0, 1, 2]),          # not 2^r elements
                  edit(curve_subspace=[1, 2]),             # no 0
                  edit(curve_subspace=[0, 1, 2, 4]),       # not closed
                  edit(curve_subspace=[0, 0]),
                  edit(curve_exponent=16),                 # gcd(16, 2) = 2
                  edit(curve_exponent=256),
                  edit(pole_order=14),                     # below 2g - 1
                  edit(pole_order=200),                    # 4A > ell + 2g - 2
                  edit(punctures=CURVE_R + [512]),
                  edit(punctures=list(range(116)), k=580, N=636),
                  edit(outer_length=10),
                  edit(k=505)):
            self.assertTrue(SJ.problems(c), c)
        # A t = 8 row of the size of cv_t8_a534_P404 (n = 34,524, N =
        # 2,620) is refused for size, and for nothing else.
        big = curve(list(range(8)), 534, list(range(404)))
        self.assertEqual((big["k"], big["N"]), (2020, 2620))
        found = SJ.problems(big)
        self.assertEqual(len(found), 1)
        self.assertIn("cells", found[0])


if __name__ == "__main__":
    unittest.main()
