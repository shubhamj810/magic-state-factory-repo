"""The Reed-Muller-type construction families of `construction_rm.py`.

* **Research circuits** rebuild to the SHA-256 the research recorded, in the
  research's own column order, and to a pinned digest in the order
  `constructions.py` fixes; every recorded witness, mapped to that order, is
  harmful by `faultcore` and by the literal XOR of the wire masks.
* **Shapes**: `problems` names every malformed object without building it,
  and a dependent puncture set raises instead of building something else.
* **The CCZ frame**: `packing_check` accepts the 55-packing and refuses a
  family with a designated triple that does not partition the coordinates,
  or with an undesignated triple that does; `frame_check` accepts the built
  [[4096,165,16]] circuit and refuses a relabelled one.

The research tree is not part of this repository, so the cases below carry
the construction objects and digests themselves.  Set
``CONSTRUCTION_RM_RESEARCH`` to the research folder (the one holding
``search`` and ``search2``) to also compare full column lists with the files
the research wrote (`SlowResearchColumnsTest`, about 15 s).

Run from ``master_catalog/``:
    python -m unittest discover -s tests -p test_construction_rm.py
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import unittest
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE.parent
sys.path.insert(0, str(CATALOGUE))

import construction_rm as R                                       # noqa: E402
import faultcore as FC                                            # noqa: E402

_BUILT = {}


def built(case):
    """``(native, sorted)`` columns of a case, built once per run."""
    if case["name"] not in _BUILT:
        native = R.native_columns(case["construction"])
        _BUILT[case["name"]] = (native, R.columns(case["construction"]))
    return _BUILT[case["name"]]


def research_digest(native, serialisation):
    if serialisation == "compact":
        return R.digest(native)
    return hashlib.sha256(json.dumps(native).encode()).hexdigest()


class ResearchRebuildTest(unittest.TestCase):
    def test_every_case_rebuilds_to_both_digests(self):
        for case in CASES:
            with self.subTest(case["name"]):
                con = case["construction"]
                self.assertEqual(R.problems(con), [])
                native, cols = built(case)
                self.assertEqual(len(cols), case["n"])
                self.assertEqual(
                    research_digest(native, case["serialisation"]),
                    case["research_digest"])
                # assertTrue, not assertEqual: a diff of 4,096 columns
                # would take minutes to print.
                self.assertTrue(cols == sorted(native), "not the sorted order")
                self.assertEqual(R.digest(cols), case["sorted_digest"])
                self.assertTrue(all(c == sorted(c) for c in cols))
                self.assertTrue(all(0 <= w < con["N"] for c in cols
                                    for w in c))

    def test_every_witness_is_harmful_in_the_sorted_order(self):
        for case in CASES:
            if not case["witnesses"]:
                continue
            con = case["construction"]
            native, cols = built(case)
            k, N = con["k"], con["N"]
            circ = FC.Circuit(cols, k, N)
            pos = R.sorted_position(native)
            for w in case["witnesses"]:
                with self.subTest(case["name"], witness=w["native"]):
                    mapped = sorted(pos[j] for j in w["native"])
                    self.assertEqual(mapped, w["sorted"])
                    self.assertTrue(circ.harmful(mapped))
                    acc = 0
                    for j in mapped:
                        for q in cols[j]:
                            acc ^= 1 << q
                    self.assertNotEqual(acc, 0)
                    self.assertEqual(acc >> k, 0, "touches a check")
                    self.assertEqual(len(mapped), case["d"])

    def test_sorted_position_is_a_bijection(self):
        native = [[2], [0, 1], [0], [2]]
        pos = R.sorted_position(native)
        self.assertEqual(sorted(pos), [0, 1, 2, 3])
        self.assertEqual([sorted(native)[p] for p in pos], native)


def _base(family):
    for case in CASES:
        if case["construction"]["family"] == family:
            return json.loads(json.dumps(case["construction"]))
    raise AssertionError(family)


def _with(family, **changes):
    con = _base(family)
    for key, value in changes.items():
        if value is _DROP:
            del con[key]
        else:
            con[key] = value
    return con


_DROP = object()


class ProblemsTest(unittest.TestCase):
    def bad(self, con, fragment):
        t = time.time()
        got = R.problems(con)
        self.assertLess(time.time() - t, 2.0, "problems must not build")
        self.assertTrue(got, f"accepted {str(con)[:120]}")
        self.assertIn(fragment, "; ".join(got))
        with self.assertRaises(ValueError):
            R.columns(con)

    def test_tables_agree(self):
        self.assertEqual(set(R.FAMILIES), set(R.DESCRIPTIONS))
        for family, fields in R.FAMILIES.items():
            self.assertIn("k", fields)
            self.assertIn("N", fields)
            self.assertEqual(R.problems(_base(family)), [])

    def test_general(self):
        self.bad([1, 2], "not an object")
        self.bad({"family": "rm"}, "unknown construction family")
        self.bad(_with("punctured-rm", N=_DROP), "has the fields")
        self.bad(_with("punctured-rm", extra=1), "has the fields")
        self.bad(_with("punctured-rm", k=True), "k must be")
        self.bad(_with("ccz-frame", N=0), "N must be")

    def test_punctured_rm(self):
        rm = "punctured-rm"
        P = _base(rm)["punctures"]
        self.bad(_with(rm, m=13), "m must be")
        self.bad(_with(rm, m=10 ** 9), "m must be")
        self.bad(_with(rm, m=10.0), "m must be")
        self.bad(_with(rm, r=4), "r must be")
        self.bad(_with(rm, r=-1), "r must be")
        self.bad(_with(rm, punctures=list(reversed(P))), "strictly increasing")
        self.bad(_with(rm, punctures=P[:-1] + [1024]), "outside 0..1023")
        self.bad(_with(rm, punctures=[P[0]] + P[:-1]), "strictly increasing")
        self.bad(_with(rm, punctures=[]), "punctures")
        self.bad(_with(rm, punctures=list(range(177))), "punctures")
        self.bad(_with(rm, punctures="0 1 2"), "list of whole numbers")
        self.bad(_with(rm, k=len(P) + 1), "k=")
        self.bad(_with(rm, N=175), "N=175")

    def test_punctured_weighted_rm(self):
        wr = "punctured-weighted-rm"
        base = _base(wr)
        m, P = base["m"], base["punctures"]
        self.bad(_with(wr, weights=base["weights"][:-1]), "weights must be")
        self.bad(_with(wr, weights=[0] + base["weights"][1:]), "weights must be")
        self.bad(_with(wr, weights=[17] + base["weights"][1:]), "weights must be")
        self.bad(_with(wr, weights=[True] * m), "weights must be")
        self.bad(_with(wr, cutoff=-1), "cutoff must be")
        self.bad(_with(wr, cutoff=10 ** 6), "cutoff must be")
        self.bad(_with(wr, punctures=P[:-1] + [P[0]]), "punctured twice")
        self.bad(_with(wr, punctures=P[:-1] + [1 << m]), "outside")
        self.bad(_with(wr, N=base["N"] + 1), "N=")
        self.bad(_with(wr, m=0), "m must be")

    def test_ccz_frame(self):
        cz = "ccz-frame"
        T = _base(cz)["triples"]
        self.bad(_with(cz, q=5), "q must be")
        self.bad(_with(cz, q=0), "q must be")
        self.bad(_with(cz, triples=[]), "non-empty")
        self.bad(_with(cz, triples=T + [T[0]] * 111), "distinct 4-sets")
        self.bad(_with(cz, triples=[T[0][:2]] + T[1:]), "list of three")
        self.bad(_with(cz, triples=[[[0, 1, 2], T[0][1], T[0][2]]] + T[1:]),
                 "strictly increasing list of 4")
        self.bad(_with(cz, triples=[[[1, 0, 2, 3], T[0][1], T[0][2]]] + T[1:]),
                 "strictly increasing list of 4")
        self.bad(_with(cz, triples=[[[0, 1, 2, 12], T[0][1], T[0][2]]] + T[1:]),
                 "coordinates in 0..11")
        self.bad(_with(cz, triples=[[T[1][0], T[0][1], T[0][2]]] + T[1:]),
                 "occurs twice")
        self.bad(_with(cz, k=164), "k=164")
        self.bad(_with(cz, N=465), "N=465")

    def test_four_block(self):
        fb = "four-block"
        P = _base(fb)["punctures"]
        self.bad(_with(fb, L=13), "L must be")
        self.bad(_with(fb, L=3), "L must be")
        self.bad(_with(fb, removed_flats=[[0, 1, 2, 3, 4]]), "not 4-dimensional")
        self.bad(_with(fb, removed_flats=[[0, 1, 2, 4, 8], [1, 2, 4, 8, 16]]),
                 "meets an earlier one")
        self.bad(_with(fb, removed_flats=[[0, 1, 2, 4, 256]]), "entries in")
        self.bad(_with(fb, removed_flats=[[0, 1, 2, 4]]), "not [offset")
        self.bad(_with(fb, removed_flats="none"), "removed_flats must be")
        self.bad(_with(fb, punctures=P[:-1] + [4 * 256]), "outside 0..1023")
        self.bad(_with(fb, N=238), "N=238")


class DependentPuncturesTest(unittest.TestCase):
    """A puncture set containing the support of a dual word is dependent."""

    def test_rm_and_weighted_on_a_2_flat(self):
        # {0, 1, 2, 3} is a 2-flat, a weight-4 word of RM(1,4)'s dual RM(2,4).
        rm = {"family": "punctured-rm", "m": 4, "r": 1,
              "punctures": [0, 1, 2, 3], "k": 4, "N": 5}
        wr = {"family": "punctured-weighted-rm", "m": 4, "weights": [1] * 4,
              "cutoff": 1, "punctures": [0, 1, 2, 3], "k": 4, "N": 5}
        for con in (rm, wr):
            with self.subTest(con["family"]):
                self.assertEqual(R.problems(con), [])
                with self.assertRaises(ValueError):
                    R.columns(con)

    def test_four_block_on_one_point_in_all_blocks(self):
        # strategy REPORT.md 3.1: a point s in all four blocks is a dual word.
        con = {"family": "four-block", "L": 4, "removed_flats": [],
               "punctures": [5, 16 + 5, 32 + 5, 48 + 5], "k": 4, "N": 15}
        self.assertEqual(R.problems(con), [])
        with self.assertRaises(ValueError):
            R.columns(con)

    def test_two_reductions_differ(self):
        # The same parent RM(3,10) and puncture set through the other family's
        # reduction is a different circuit, so the family name matters.
        case = next(c for c in CASES
                    if c["construction"]["family"] == "punctured-rm")
        con = case["construction"]
        other = {"family": "punctured-weighted-rm", "m": con["m"],
                 "weights": [1] * con["m"], "cutoff": con["r"],
                 "punctures": con["punctures"], "k": con["k"], "N": con["N"]}
        self.assertEqual(R.problems(other), [])
        self.assertNotEqual(R.digest(R.columns(other)), case["sorted_digest"])
        self.assertNotEqual(R.digest(R.native_columns(other)),
                            case["research_digest"])


def _frobenius_orbit():
    """F_55 = {x -> ax + b : a in {1,3,4,5,9}, b in F_11}, fixing 11 (infinity)."""
    base = [[0, 1, 2, 3], [5, 7, 8, 9], [4, 6, 10, 11]]
    orbit = set()
    for a in (1, 3, 4, 5, 9):
        for b in range(11):
            img = frozenset(frozenset(11 if x == 11 else (a * x + b) % 11
                                      for x in s) for s in base)
            orbit.add(img)
    return orbit


class PackingCheckTest(unittest.TestCase):
    def setUp(self):
        self.con = _base("ccz-frame")
        self.triples = self.con["triples"]

    def test_passes_on_the_55_packing(self):
        self.assertEqual(R.packing_check(self.con), [])

    def test_the_packing_is_the_frobenius_orbit(self):
        orbit = _frobenius_orbit()
        self.assertEqual(len(orbit), 55)
        stored = {frozenset(frozenset(s) for s in t) for t in self.triples}
        self.assertEqual(stored, orbit)

    def test_fails_when_a_designated_triple_does_not_partition(self):
        family = {tuple(s) for t in self.triples for s in t}
        new = next(list(s) for s in combinations(range(12), 4)
                   if s not in family)
        triples = [[new] + self.triples[0][1:]] + self.triples[1:]
        con = dict(self.con, triples=triples)
        self.assertEqual(R.problems(con), [])
        got = R.packing_check(con)
        self.assertTrue(any("designated triple 0 does not partition" in p
                            for p in got), got)

    def test_fails_when_another_triple_partitions(self):
        # Replace one designated triple by a new partition {X, Y, Z} whose X
        # completes two remaining members of the family to a partition.
        full = set(range(12))
        family = [tuple(s) for t in self.triples for s in t]
        members = set(family)
        for i in range(len(self.triples)):
            mine = {tuple(s) for s in self.triples[i]}
            keep = [s for s in family if s not in mine]
            hit = None
            for a, b in combinations(keep, 2):
                if set(a) & set(b):
                    continue
                X = tuple(sorted(full - set(a) - set(b)))
                if X in members:
                    continue
                rest = sorted(full - set(X))
                for Y in combinations(rest, 4):
                    Z = tuple(sorted(set(rest) - set(Y)))
                    if Y < Z and Y not in members and Z not in members:
                        hit = (X, Y, Z)
                        break
                if hit:
                    break
            if hit:
                break
        self.assertIsNotNone(hit)
        triples = list(self.triples)
        triples[i] = [list(s) for s in hit]
        con = dict(self.con, triples=triples)
        self.assertEqual(R.problems(con), [])
        got = R.packing_check(con)
        self.assertFalse(any("does not partition" in p for p in got), got)
        self.assertTrue(any("undesignated" in p for p in got), got)

    def test_refuses_another_family(self):
        self.assertTrue(R.packing_check(_base("punctured-rm")))


class FrameCheckTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = next(c for c in CASES
                        if c["construction"]["family"] == "ccz-frame")
        cls.con = cls.case["construction"]
        cls.cols = built(cls.case)[1]

    def test_passes_on_the_built_circuit(self):
        self.assertEqual(R.frame_check(self.cols, self.con["k"],
                                       self.con["N"], self.con), [])

    def test_fails_on_swapped_outputs(self):
        swap = {0: 3, 3: 0}
        cols = sorted(sorted(swap.get(w, w) for w in c) for c in self.cols)
        got = R.frame_check(cols, self.con["k"], self.con["N"], self.con)
        self.assertTrue(any("output sets differ" in p for p in got), got)
        self.assertTrue(any("recovered gate" in p for p in got), got)

    def test_fails_on_a_missing_column(self):
        got = R.frame_check(self.cols[1:], self.con["k"], self.con["N"],
                            self.con)
        self.assertTrue(got)


@unittest.skipUnless(os.environ.get("CONSTRUCTION_RM_RESEARCH"),
                     "set CONSTRUCTION_RM_RESEARCH to the research folder")
class SlowResearchColumnsTest(unittest.TestCase):
    """Full column lists against the files the research wrote."""

    def test_full_columns(self):
        root = Path(os.environ["CONSTRUCTION_RM_RESEARCH"])
        for case in CASES:
            if not case["file"]:
                continue
            path = root / case["file"]
            if not path.exists():
                continue
            with self.subTest(case["name"]):
                data = json.loads(path.read_text())
                if case["key"]:
                    data = data[case["key"]]
                self.assertTrue(built(case)[0] == data["columns"])


# One case per research circuit: the construction object, the research's
# digest of its own column order (``serialisation`` says which JSON text it
# hashed), the digest in the contract's order, and every recorded witness as
# research (native) indices and as indices into the sorted order.  ``file``
# and ``key`` locate the research's column list, relative to the research
# folder.  The four-block cases are the strategy report's [[813,211,3]] pilot
# and one circuit of the four-block search in progress (removed flats), which
# test the builder only; neither is a row to import.
CASES = [json.loads(line) for line in r"""
{"name":"930.94.7.8edc44a935","construction":{"family":"punctured-rm","m":10,"r":3,"punctures":[0,11,27,28,30,57,65,70,92,96,108,119,134,137,145,147,158,161,162,164,168,174,180,189,199,206,231,261,264,281,308,309,311,333,352,359,360,363,373,377,384,387,393,400,403,417,427,455,468,488,489,498,500,519,520,522,524,526,538,557,564,570,577,580,586,601,615,623,631,635,639,653,655,683,707,718,721,725,761,769,785,812,821,837,855,875,903,914,925,945,960,982,983,985],"k":94,"N":176},"n":930,"d":7,"research_digest":"8edc44a9350ca9b4c0df21dfab4aaa0ec4e768a87376b802d29208dc74f35474","serialisation":"compact","sorted_digest":"9838ec3857c3a5b34c4353baa1a6005fb11408a3c8c2bfd7eb37bbb2a512ac4e","file":"search/lift/data/certified/930.94.7.8edc44a935.t94_b712810aa9.json","key":null,"witnesses":[{"native":[0,34,55,110,384,390,414],"sorted":[291,301,345,490,679,786,888]}]}
{"name":"930.94.7.41eb2a9cef","construction":{"family":"punctured-rm","m":10,"r":3,"punctures":[0,27,28,30,47,49,52,57,98,119,145,147,161,168,199,221,231,237,255,261,264,280,311,333,338,350,351,352,355,359,360,377,384,397,416,417,427,469,488,489,498,520,526,537,538,549,554,557,563,564,570,577,580,586,599,601,615,623,627,631,635,639,651,653,654,655,668,696,707,718,725,749,758,761,767,769,782,785,808,810,812,820,831,837,848,875,880,903,914,925,926,982,985,1022],"k":94,"N":176},"n":930,"d":7,"research_digest":"41eb2a9cefa5cebf0267607ce381313eab21a6cb563ebbd9f27d1878bec7bf43","serialisation":"compact","sorted_digest":"80a80ce8a50be1f856ff5137431b791b0f4b54d7943d06a220c10d0b858a560d","file":"search/lift/data/certified/930.94.7.41eb2a9cef.json","key":null,"witnesses":[{"native":[0,4,39,306,549,711,745],"sorted":[393,402,562,577,684,823,904]}]}
{"name":"930.94.7.f34845ed1a","construction":{"family":"punctured-rm","m":10,"r":3,"punctures":[0,10,28,47,49,52,108,119,132,137,159,161,162,164,168,180,181,189,196,201,221,231,249,261,264,266,271,311,333,338,350,352,359,377,384,387,395,400,403,417,426,463,468,469,477,488,500,520,524,526,537,554,558,564,577,580,586,590,601,615,623,631,639,651,653,654,655,668,677,683,692,696,709,718,725,749,758,761,808,812,820,843,875,903,914,925,926,971,981,982,983,985,1018,1023],"k":94,"N":176},"n":930,"d":7,"research_digest":"f34845ed1a187fcb28d46b3bfb5832965e7ceeb4d3b02f02ca00f6609fc45e4e","serialisation":"compact","sorted_digest":"d9d35447831b06b28cae5a80ea19313a85796240b9360a2ce50db3457c7a0ce4","file":"search/lift/data/certified/930.94.7.f34845ed1a.json","key":null,"witnesses":[{"native":[0,6,30,36,122,501,615],"sorted":[62,118,522,790,803,846,855]}]}
{"name":"931.93.7.83a91c80c5","construction":{"family":"punctured-rm","m":10,"r":3,"punctures":[0,10,11,22,27,30,47,52,57,70,98,118,119,145,147,161,164,168,180,189,196,199,231,237,255,264,266,271,280,309,333,338,350,352,359,360,377,384,387,399,400,403,406,427,468,477,498,500,520,524,526,537,549,557,558,563,564,570,577,580,586,631,635,639,651,653,654,655,668,669,673,683,696,718,725,749,758,761,782,785,808,820,821,825,855,880,903,925,960,974,981,982,983],"k":93,"N":176},"n":931,"d":7,"research_digest":"83a91c80c53823b27ec5aac9eb84fd1ebe564989ae4fcb3ade90553ac77e807d","serialisation":"compact","sorted_digest":"e5496ed6eb7200d463e2f0b66a9c7d362f580f0ce0e2f6e41ec89369eaf1d7c5","file":"search/lift/data/certified/931.93.7.83a91c80c5.lns_a_t93.json","key":null,"witnesses":[{"native":[0,27,46,119,161,512,627],"sorted":[223,230,412,547,600,730,835]}]}
{"name":"932.92.7.0f5a3a3102","construction":{"family":"punctured-rm","m":10,"r":3,"punctures":[0,10,11,27,30,47,52,57,70,98,119,145,147,161,164,168,180,189,196,199,231,237,255,261,264,266,271,280,309,333,338,350,352,359,360,377,384,387,399,400,403,417,427,468,477,498,500,520,524,526,537,549,557,558,563,564,570,577,580,586,601,631,635,639,651,653,654,655,668,673,683,696,718,725,749,758,761,782,785,808,820,821,855,875,880,903,925,960,981,982,983,985],"k":92,"N":176},"n":932,"d":7,"research_digest":"0f5a3a310223b3d6fe9a720959ecc226feacaecefbd783b9a5d98859326bda6f","serialisation":"compact","sorted_digest":"8a053282356e2747f8849240f45cdd9a38fc7784347d9b216034b16d04f56006","file":"search/lift/data/certified/932.92.7.0f5a3a3102.json","key":null,"witnesses":[{"native":[0,51,131,442,681,707,848],"sorted":[302,355,395,625,766,769,898]}]}
{"name":"933.91.7.6a25de9b43","construction":{"family":"punctured-rm","m":10,"r":3,"punctures":[0,11,27,28,30,47,52,57,70,98,108,145,147,158,161,162,164,168,180,189,199,221,231,237,255,261,264,266,271,280,309,338,350,352,360,377,384,387,400,403,455,468,469,477,488,489,498,520,537,549,554,555,557,558,563,564,570,580,586,590,601,615,635,651,653,654,655,668,683,692,696,718,725,749,758,761,782,808,812,820,821,855,875,880,903,914,925,926,981,982,985],"k":91,"N":176},"n":933,"d":7,"research_digest":"6a25de9b4305908eda17b5e40744008bbb0e79e8631d954d35f07782efd79016","serialisation":"compact","sorted_digest":"bc7e36767197f207938fb040bb9d8ef59b2d119f2de66f6a00a7ed9ebdd87e36","file":"search/lift/data/certified/933.91.7.6a25de9b43.json","key":null,"witnesses":[{"native":[0,1,88,173,174,530,676],"sorted":[14,205,256,334,488,631,780]}]}
{"name":"954.70.8.ff92d26dfe","construction":{"family":"punctured-rm","m":10,"r":3,"punctures":[27,47,70,92,108,119,134,144,145,147,158,162,164,176,189,196,199,209,237,261,271,280,309,338,352,353,359,373,377,384,387,399,400,403,417,470,477,481,488,498,524,526,530,549,554,555,558,570,577,586,592,596,649,651,654,655,661,678,709,739,749,783,805,812,837,880,914,926,955,982],"k":70,"N":176},"n":954,"d":8,"research_digest":"ff92d26dfec9fb2b7910a8fb98e3096c5b2f77a52eb6d825bc82b93d361ec9b0","serialisation":"compact","sorted_digest":"c1007e22f538cf1467d9da3c257395ee8b97ca0eacf7fd93968f5bc011918cf9","file":"search/lift/data/certified/954.70.8.ff92d26dfe.json","key":null,"witnesses":[{"native":[0,158,202,526,536,543,679,700],"sorted":[211,368,434,479,581,691,700,726]}]}
{"name":"955.69.8.6627c613e4","construction":{"family":"punctured-rm","m":10,"r":3,"punctures":[22,27,47,52,56,61,100,106,108,173,176,182,237,240,279,280,291,306,360,399,408,429,434,448,468,471,477,498,525,533,537,541,546,556,563,577,596,600,609,653,668,673,695,709,722,738,741,742,748,758,784,786,801,819,839,840,844,852,875,880,881,887,906,946,950,960,977,980,985],"k":69,"N":176},"n":955,"d":8,"research_digest":"6627c613e4143b5ad7f678f339e9970638820da86c716f0bbe07d60ca90688de","serialisation":"compact","sorted_digest":"8bb4bcea05d8c47d0642f338187c6f3551d38f634e7c85858089a0a0dfd1e8aa","file":"search/lift/data/certified/955.69.8.6627c613e4.json","key":null,"witnesses":[{"native":[0,105,399,445,678,723,735,807],"sorted":[82,217,234,298,439,485,538,821]}]}
{"name":"4096.165.16.ccz-frame","construction":{"family":"ccz-frame","q":4,"triples":[[[0,1,2,3],[5,7,8,9],[4,6,10,11]],[[0,2,3,4],[6,7,8,9],[1,5,10,11]],[[1,2,3,4],[6,8,9,10],[0,5,7,11]],[[1,3,4,5],[7,8,9,10],[0,2,6,11]],[[2,3,4,5],[0,7,9,10],[1,6,8,11]],[[0,1,2,6],[3,4,9,10],[5,7,8,11]],[[0,2,4,6],[1,3,7,10],[5,8,9,11]],[[0,1,5,6],[2,3,4,8],[7,9,10,11]],[[0,3,5,6],[1,4,7,10],[2,8,9,11]],[[2,4,5,6],[0,8,9,10],[1,3,7,11]],[[3,4,5,6],[0,1,8,10],[2,7,9,11]],[[1,2,3,7],[0,4,5,10],[6,8,9,11]],[[0,3,4,7],[1,2,6,9],[5,8,10,11]],[[0,3,5,7],[4,6,8,10],[1,2,9,11]],[[1,3,5,7],[0,2,4,8],[6,9,10,11]],[[0,1,6,7],[3,8,9,10],[2,4,5,11]],[[1,2,6,7],[3,4,5,9],[0,8,10,11]],[[0,3,6,7],[1,5,8,9],[2,4,10,11]],[[1,4,6,7],[0,2,5,8],[3,9,10,11]],[[0,5,6,7],[3,4,8,9],[1,2,10,11]],[[3,5,6,7],[0,1,9,10],[2,4,8,11]],[[4,5,6,7],[0,1,2,9],[3,8,10,11]],[[0,2,3,8],[1,4,7,9],[5,6,10,11]],[[0,1,4,8],[3,6,9,10],[2,5,7,11]],[[0,3,4,8],[2,5,6,9],[1,7,10,11]],[[0,1,5,8],[2,3,6,10],[4,7,9,11]],[[0,3,5,8],[4,7,9,10],[1,2,6,11]],[[1,4,5,8],[2,3,7,10],[0,6,9,11]],[[0,3,6,8],[1,2,7,10],[4,5,9,11]],[[1,4,6,8],[0,5,7,9],[2,3,10,11]],[[2,4,6,8],[1,3,5,9],[0,7,10,11]],[[1,2,7,8],[0,4,9,10],[3,5,6,11]],[[2,3,7,8],[4,5,6,10],[0,1,9,11]],[[0,4,7,8],[2,5,6,10],[1,3,9,11]],[[1,4,7,8],[2,6,9,10],[0,3,5,11]],[[2,5,7,8],[1,3,6,9],[0,4,10,11]],[[1,6,7,8],[4,5,9,10],[0,2,3,11]],[[4,6,7,8],[0,1,2,10],[3,5,9,11]],[[5,6,7,8],[1,2,3,10],[0,4,9,11]],[[0,2,4,9],[1,5,8,10],[3,6,7,11]],[[1,3,4,9],[2,5,8,10],[0,6,7,11]],[[1,2,5,9],[0,4,7,10],[3,6,8,11]],[[1,4,5,9],[3,6,7,10],[0,2,8,11]],[[0,1,6,9],[2,5,7,10],[3,4,8,11]],[[0,2,6,9],[1,3,5,10],[4,7,8,11]],[[0,3,6,9],[2,4,5,10],[1,7,8,11]],[[1,4,6,9],[0,5,8,10],[2,3,7,11]],[[0,2,7,9],[3,6,8,10],[1,4,5,11]],[[0,4,7,9],[1,3,8,10],[2,5,6,11]],[[2,5,7,9],[1,6,8,10],[0,3,4,11]],[[3,5,7,9],[2,4,6,10],[0,1,8,11]],[[2,3,8,9],[0,1,5,10],[4,6,7,11]],[[2,5,8,9],[0,3,7,10],[1,4,6,11]],[[3,6,8,9],[2,4,7,10],[0,1,5,11]],[[2,7,8,9],[0,5,6,10],[1,3,4,11]]],"k":165,"N":464},"n":4096,"d":16,"research_digest":"dfdeb2d998949ff38f7b90e2218628effc25207d4b2aa612259a10336124ab7d","serialisation":"default","sorted_digest":"fc716035a631f14dfccf01f84aa6ee3fb4fb3ce3f03e3f715e2761dd2c06cf21","file":"search/parents/data/ccz/frame_q4_c55_f55.json","key":null,"witnesses":[{"native":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],"sorted":[255,3324,3325,3338,3358,3389,3399,3440,3474,3563,3576,3614,3645,3737,3778,3860]}]}
{"name":"1842.206.7.5d387ef445","construction":{"family":"punctured-weighted-rm","m":11,"weights":[2,2,2,2,2,2,2,2,1,1,1],"cutoff":6,"punctures":[0,8,34,39,45,53,57,77,84,100,110,111,115,125,127,135,145,152,170,175,179,181,208,211,230,243,272,277,279,298,308,325,331,336,341,354,365,366,375,376,382,402,413,415,419,439,451,456,475,494,504,508,526,534,546,554,560,574,584,586,588,594,597,600,604,635,657,666,678,689,723,735,737,745,746,747,748,750,778,791,799,806,808,819,826,827,831,848,863,873,875,881,886,900,901,910,917,924,950,977,986,987,1001,1009,1029,1035,1037,1039,1042,1056,1067,1070,1075,1095,1109,1110,1116,1153,1157,1202,1214,1224,1235,1242,1252,1259,1266,1278,1279,1299,1309,1314,1338,1369,1372,1392,1395,1397,1401,1420,1425,1426,1438,1446,1450,1456,1457,1462,1471,1485,1489,1498,1507,1509,1515,1540,1557,1570,1576,1601,1612,1627,1630,1634,1653,1665,1669,1681,1689,1701,1712,1715,1716,1726,1728,1729,1735,1752,1755,1768,1821,1829,1830,1831,1838,1848,1854,1864,1867,1869,1879,1894,1926,1929,1935,1948,1963,1964,1978,1981,1983,1986,2014,2016,2029,2040],"k":206,"N":324},"n":1842,"d":7,"research_digest":"5d387ef445ef7101fd5f91f1a283dd6f6939914cf86d3e41b8e7625e37583e25","serialisation":"compact","sorted_digest":"f5eafa0b1d1011e15ae3fe9e08af3e4aca6312c6fc297e22303aba8f7261978a","file":"search2/weighted/data/claimed_factories.json","key":"5d387ef445ef7101fd5f91f1a283dd6f6939914cf86d3e41b8e7625e37583e25","witnesses":[{"native":[526,527,671,1647,1732,1733,1734],"sorted":[1045,1210,1285,1352,1763,1779,1815]},{"native":[526,528,673,744,823,824,827],"sorted":[62,171,288,415,1169,1285,1740]}]}
{"name":"1893.155.8.188c0f5df2","construction":{"family":"punctured-weighted-rm","m":11,"weights":[2,2,2,2,2,2,2,2,1,1,1],"cutoff":6,"punctures":[7,51,60,67,83,105,123,143,161,165,166,184,195,197,201,204,208,210,223,270,296,341,357,366,373,384,398,412,429,434,450,452,453,467,490,494,503,507,559,567,571,583,593,620,638,643,664,666,668,669,670,698,703,708,716,726,732,779,790,808,815,827,838,840,879,901,915,917,932,935,942,965,985,1002,1007,1023,1025,1033,1060,1062,1075,1080,1086,1099,1130,1150,1158,1166,1167,1184,1188,1194,1198,1259,1266,1277,1303,1305,1306,1319,1326,1353,1381,1413,1421,1427,1438,1446,1462,1463,1477,1488,1490,1495,1521,1546,1547,1562,1581,1591,1598,1649,1651,1680,1689,1706,1711,1731,1736,1741,1744,1751,1754,1773,1784,1814,1822,1834,1868,1878,1885,1893,1902,1904,1907,1914,1939,1951,1953,1957,1966,1977,1984,2028,2032],"k":155,"N":324},"n":1893,"d":8,"research_digest":"188c0f5df278b001950795365494870f5f7120044cf6962c11d4d31f1b31fc43","serialisation":"compact","sorted_digest":"fbe766b2bbc11e722fffb329983ad16a544920c99b4657240a3b6c60b9e3dd27","file":"search2/weighted/data/claimed_factories.json","key":"188c0f5df278b001950795365494870f5f7120044cf6962c11d4d31f1b31fc43","witnesses":[{"native":[152,153,154,155,156,618,619,620],"sorted":[353,488,607,620,1260,1482,1768,1812]},{"native":[525,526,527,620,982,983,1077,1078],"sorted":[275,282,351,469,488,647,930,1378]}]}
{"name":"1894.154.8.a6e3040381","construction":{"family":"punctured-weighted-rm","m":11,"weights":[2,2,2,2,2,2,2,2,1,1,1],"cutoff":6,"punctures":[2,10,27,31,56,66,90,100,103,107,129,132,143,153,184,203,212,224,246,256,268,272,287,296,312,332,335,340,345,378,429,436,439,465,477,479,496,506,539,552,575,578,587,591,596,599,622,628,634,640,658,664,665,677,688,718,766,779,795,801,813,821,856,857,884,904,917,929,936,939,945,948,954,978,986,997,1045,1047,1077,1080,1090,1094,1107,1119,1141,1146,1158,1167,1176,1200,1206,1219,1222,1258,1277,1314,1321,1327,1341,1353,1356,1381,1386,1411,1419,1426,1428,1461,1468,1469,1471,1501,1505,1519,1541,1582,1619,1622,1652,1661,1672,1673,1687,1719,1720,1725,1729,1730,1738,1744,1748,1750,1778,1785,1793,1798,1801,1815,1848,1897,1909,1911,1933,1940,1952,1955,1966,1991,1994,1997,2008,2027,2040,2047],"k":154,"N":324},"n":1894,"d":8,"research_digest":"a6e3040381c9e5b41ab04682b88ffc5a0b54c9123db19863a86edb7b327f1cdc","serialisation":"compact","sorted_digest":"76d7d8704667683a1a19278343be698ffd8c961216afce1e6e6affb5fd22590e","file":"search2/weighted/data/claimed_factories.json","key":"a6e3040381c9e5b41ab04682b88ffc5a0b54c9123db19863a86edb7b327f1cdc","witnesses":[{"native":[1360,1392,1393,1394,1552,1553,1618,1619],"sorted":[38,208,580,807,1348,1389,1416,1455]},{"native":[307,308,442,443,1227,1228,1229,1360],"sorted":[124,591,862,878,1063,1389,1438,1794]}]}
{"name":"1845.203.7.f5a5422722","construction":{"family":"punctured-weighted-rm","m":11,"weights":[2,2,2,2,2,2,2,2,1,1,1],"cutoff":6,"punctures":[9,14,56,68,72,79,83,86,87,89,96,128,133,144,146,170,176,179,180,208,217,224,230,240,243,253,259,281,292,302,306,318,320,325,342,344,346,347,356,361,369,373,387,389,394,425,427,432,466,472,500,518,530,539,558,559,561,570,580,581,609,612,613,615,623,627,629,637,652,679,681,692,702,725,733,753,754,755,770,775,787,798,800,808,819,834,842,844,859,861,867,907,917,926,944,953,955,956,976,991,995,1004,1005,1029,1034,1051,1058,1069,1072,1074,1079,1085,1086,1116,1117,1138,1158,1182,1203,1206,1231,1236,1244,1247,1250,1251,1275,1279,1293,1319,1326,1361,1371,1374,1375,1377,1386,1403,1418,1436,1444,1457,1463,1473,1476,1478,1496,1498,1500,1510,1519,1529,1534,1539,1577,1579,1594,1601,1612,1615,1630,1651,1659,1663,1672,1697,1708,1717,1718,1721,1732,1750,1751,1759,1764,1770,1778,1780,1791,1794,1812,1815,1821,1842,1846,1853,1863,1872,1884,1893,1900,1906,1914,1923,1927,1976,1982,1989,1991,2019,2024,2032,2045],"k":203,"N":324},"n":1845,"d":7,"research_digest":"f5a5422722d4df361dde5d3f701cf270974d3777f84e5f8f43a250f477423650","serialisation":"compact","sorted_digest":"31c6bb263fd4e0288a9d8ae2b2c8c769e6ff0600267513f408478437ceb10208","file":"search2/weighted/data/problems/f5a542.json","key":null,"witnesses":[{"native":[131,132,160,161,522,523,551],"sorted":[54,732,908,1316,1341,1373,1427]},{"native":[285,286,287,379,380,551,677],"sorted":[92,677,678,732,935,1309,1403]},{"native":[309,345,346,347,502,503,677],"sorted":[92,641,973,1038,1102,1334,1363]}]}
{"name":"480.32.6.b73acb8dfa","construction":{"family":"punctured-weighted-rm","m":9,"weights":[1,1,1,1,1,2,2,2,2],"cutoff":4,"punctures":[0,1,2,3,4,5,6,39,8,9,10,11,12,13,78,111,16,17,18,19,20,21,22,55,24,281,26,283,156,413,222,511],"k":32,"N":101},"n":480,"d":6,"research_digest":"b73acb8dfa16382a42f66b6d49a4c25bc71df63787ecbeb4f46638430e22c687","serialisation":"compact","sorted_digest":"5e311f796c1e13e5fba847d0fd459f61c91d19b160fbeb586ae9f7012028b2ca","file":"search/sparse/data/candidates/480_32_6.json","key":null,"witnesses":[{"native":[0,1,23,47,78,85],"sorted":[169,170,177,274,278,282]}]}
{"name":"479.33.5.97eab4ef52","construction":{"family":"punctured-weighted-rm","m":9,"weights":[1,1,1,1,1,2,2,2,2],"cutoff":4,"punctures":[137,292,463,453,447,39,160,80,340,321,350,507,311,181,86,467,28,488,490,242,294,451,2,409,273,428,157,491,110,218,24,13,15],"k":33,"N":101},"n":479,"d":5,"research_digest":"97eab4ef52701f370325c5936a9c7d151d0ebf36a89557342483197639d61aa0","serialisation":"compact","sorted_digest":"9578d363d7cdc9c61fc6b1a8622e2e60a546fa92a1b6544c366675f9785a35f2","file":"search/sparse/data/candidates/479_33_5.json","key":null,"witnesses":[{"native":[0,163,330,345,423],"sorted":[3,67,175,181,346]}]}
{"name":"813.211.3.four-block-pilot","construction":{"family":"four-block","L":8,"removed_flats":[],"punctures":[237,175,75,183,107,62,241,70,80,242,181,200,60,3,96,114,58,232,104,172,221,52,43,73,5,144,206,179,195,227,165,201,108,220,87,102,42,127,38,164,24,249,50,92,85,245,67,95,124,233,57,4,129,159,9,219,113,204,169,168,149,122,23,254,202,17,145,111,143,251,223,207,157,66,8,146,28,97,255,238,45,235,248,106,184,191,103,6,139,138,136,205,84,214,27,31,246,250,240,151,182,118,120,15,187,29,34,33,185,211,244,203,247,130,99,37,91,194,135,69,158,36,115,128,208,213,40,231,71,32,193,217,63,46,210,100,199,19,147,54,150,39,25,160,198,186,30,152,154,153,230,12,112,126,229,2,18,141,78,177,61,171,123,215,98,225,79,77,64,51,176,88,134,53,20,94,48,209,133,7,216,83,236,137,82,81,253,189,26,196,212,49,218,234,142,101,155,56,174,109,16,35,1,74,41,228,10,68,86,156,222],"k":211,"N":237},"n":813,"d":3,"research_digest":"69017c1ca84cd425bae0ff451ed28769ad61e6f0c6511f55a2e2dc34c53cbe8c","serialisation":"compact","sorted_digest":"ce4a4b38851defd0867e952e402c3b227f4752f83285aca06990d82d32b3da67","file":"search2/strategy/data/circuit_813_211_3_block1.json","key":"69017c1ca84cd425bae0ff451ed28769ad61e6f0c6511f55a2e2dc34c53cbe8c","witnesses":[{"native":[0,4,14],"sorted":[72,99,111]}]}
{"name":"1199.337.fourblock-removed-flats","construction":{"family":"four-block","L":9,"removed_flats":[[0,1,2,4,8],[16,1,2,4,8],[32,1,2,4,8],[48,1,2,4,8],[64,1,2,4,8],[80,1,2,4,8],[128,1,2,4,8],[256,1,2,4,8]],"punctures":[0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,18,19,20,21,22,23,25,26,29,30,31,32,33,34,37,38,40,41,43,45,46,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,80,81,82,83,84,85,86,88,90,91,92,93,94,95,96,97,98,99,100,101,102,104,105,106,107,108,109,110,114,115,116,118,120,121,123,125,126,127,128,129,130,131,132,133,134,135,137,139,140,141,142,143,144,145,146,148,149,151,152,153,154,155,156,157,158,159,160,161,163,164,165,166,167,168,169,171,172,173,175,176,177,178,180,181,182,183,184,185,186,187,188,189,190,191,192,193,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,215,216,218,219,220,221,223,224,225,228,229,230,231,232,234,235,236,237,238,239,241,242,243,244,245,246,247,248,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,272,273,274,277,278,279,281,282,283,284,285,286,287,288,289,291,292,293,294,295,296,297,298,299,301,303,304,305,306,307,308,310,311,312,313,314,316,317,319,320,321,322,323,324,325,326,327,328,329,330,331,332,333,334,335,336,337,340,342,343,344,345,346,347,348,349,350,351,352,353,355,356,357,358,359,360,361,362,363,364,365,366,367,368,369,371,372,373,375,376,377,378,379,383,386,401,497,546,792,807,880,1196,1322,1401,1490],"k":337,"N":358},"n":1199,"d":3,"research_digest":"cb9aff7a7f0e875d39ba05e8f54e6bfd3d54235641749a90a767e5eb1ff27977","serialisation":"compact","sorted_digest":"3983ff3cd21589af6592384fa5590c084302fe3aee6e2fed1c89ab2cf0098b33","file":null,"key":null,"witnesses":[]}
""".strip().splitlines()]
