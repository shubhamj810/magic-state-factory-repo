"""The Borrowed Identities import: the copy, the circuits, and what the master
catalogue does with them.

* the upstream files are the ones pinned here, byte for byte;
* every row of the three upstream catalogues has an explicit circuit, and
  every circuit is a borrowed identity with the row's gate count -- checked by
  a phase computation written out again here, not imported from the exporter;
* every recorded distance is witnessed, and on every circuit small enough the
  absence below it is re-proved by brute force;
* the upstream distance claims the measurement contradicts are exactly the
  ten listed in the README;
* every level-3 circuit's class is in the master catalogue, except the one
  pseudo-output the catalogue refuses, and the classes are credited as the
  README says.

Regenerating the circuits from the upstream code takes about half a minute
and is `export_circuits.py --check`, not a test here.
"""
import hashlib
import itertools
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
FOLDER = HERE.parent
REPO = FOLDER.parent
UPSTREAM = FOLDER / "upstream"
CIRCUITS = FOLDER / "circuits"
sys.path.insert(0, str(REPO / "master_catalog"))
sys.path.insert(0, str(FOLDER))

import glcanon as GC                                              # noqa: E402

#: SHA-256 of every file copied from shraggy/Magic_state_factory_search at
#: commit cae49828ed9ab9c1079c7cdf66c5bd337b027515.
UPSTREAM_SHA256 = {
    "README.md": "c2823538dba3a55bcc8c55b362990dfd5d3d7c4fbe41e055ddeacddb091277fa",
    "classification/README.md": "3cccfc877769641f773941adba17005add0440278fc98dfe9e1eb2ad60a6579c",
    "classification/classify.py": "73b6be1c89c96868177d7f041296bda9766dc577581a9a880bb30484a1655987",
    "classification/degree.py": "041c3d6d0e62b5f260675133c65d0028546a9afbb7735ecb65331ccf58cf2fa2",
    "classification/export_circuit.py": "10f2f9f10a11ea281ec10a911375d28d28ddbf8435a69340198135a794293806",
    "classification/metrics.py": "a5da0b6486e4b77510de1dd23a09858ac7cc3d7d4893a0eaa5cc6d0328a88cf6",
    "classification/quirk.py": "e2a8469f83c97f45ec32b02680c715cb4433116e16aebb27a91d6d5687b5a8ea",
    "classification/tcount.py": "6fe3540e73ba03b87a806b3c70e4af50ed48e750eb58551bb1419d28c04bcad9",
    "outputs/README.md": "b5845d0d2045989471d58724fd6693e3c8500123acabdd52d94fa35acd4751a8",
    "outputs/factory_catalogue_l2.csv": "7ba5ee86b2bf5fbd735199fe04ef97ea444c09eb219519de518530facfbc44a6",
    "outputs/factory_catalogue_l3.csv": "2844ae223b6146ed6d34e8da47b19109682d61cc0c8259db01f28a1dc4a1b87b",
    "outputs/factory_catalogue_l4.csv": "49ae8717324c3ec39d43b36939b42f78c4b58e94be15580efd297f4a90cd3c80",
    "searches/README.md": "194267475e26c3164c973b3da84e359327b37cc807110ed3c5096f844aa2eb95",
    "searches/Two_group.py": "31c1f3448bd2772ddab2557a99ecc4259cbe71a6506c12b105caedc73bce1913",
    "searches/distance_check.py": "596997cf5e03a4f860b96e93a2c5164167151c928ed9cefc07a9ccc1a13173f4",
    "searches/symfree_search.py": "8cc539ef3dcbec59bf63ce611d6f346e38d37cd945b5cea6a7731243f7187b5e",
}

#: Rows whose printed distance the circuit contradicts: (level, row) -> (the
#: CSV's d, the measured d).  The README lists them.
UPSTREAM_DISTANCE_ERRATA = {
    (2, 5): (7, 3), (2, 6): (5, 3), (2, 11): (5, 3), (2, 14): (5, 3),
    (2, 17): (5, 3), (2, 20): (5, 3),
    (3, 9): (5, 3), (3, 12): (5, 3), (3, 15): (5, 3),
    (4, 11): (5, 3),
}

#: The one level-3 circuit the master catalogue refuses: the paper's
#: [[8,4,2]], whose fourth output is the others modulo the check span.
REFUSED = {"l3-row083-two-group"}
BORROWED = "singh2026borrowed"
#: Classes the searches found that an earlier work had published: credited to
#: that work alone.
EARLIER = {
    "8.3.2.a": ["eastin2013distilling", "jones2013novel"],
    "12.2.2.a": ["webster2023transversal"],
    "14.2.2.a": ["bravyi2012magic"],
    "20.4.2.a": ["bravyi2012magic"],
    "26.6.2.a": ["bravyi2012magic"],
    "14.6.2.a": ["campbell2017unified"],
    "18.4.2.b": ["campbell2017unified"],
    "15.1.3.a": ["bravyi2005universal"],
}

#: The widest circuits on which a brute-force sweep below d is affordable.
BRUTE_N = 40


def load(level):
    return json.loads((CIRCUITS / f"circuits_l{level}.json").read_text())


def odd_columns(circuit):
    return [support for support, coeff in circuit["gates"] if coeff % 2]


def harmful(columns, k, faults):
    checks, outputs = set(), set()
    for index in faults:
        for q in columns[index]:
            (outputs if q < k else checks).symmetric_difference_update({q})
    return not checks and bool(outputs)


def read_gate(columns, k):
    return {frozenset(m) for size in (1, 2, 3)
            for m in itertools.combinations(range(k), size)
            if sum(1 for c in columns if set(m) <= set(c)) % 2}


class TestUpstreamCopy(unittest.TestCase):
    def test_every_copied_file_is_byte_identical_to_the_pinned_one(self):
        found = {path.relative_to(UPSTREAM).as_posix()
                 for path in UPSTREAM.rglob("*")
                 if path.is_file() and "__pycache__" not in path.parts}
        self.assertEqual(found, set(UPSTREAM_SHA256))
        for name, digest in UPSTREAM_SHA256.items():
            with self.subTest(file=name):
                self.assertEqual(hashlib.sha256(
                    (UPSTREAM / name).read_bytes()).hexdigest(), digest)

    def test_each_circuit_file_names_the_catalogue_it_was_built_from(self):
        for level in (2, 3, 4):
            head = load(level)["source"]
            with self.subTest(level=level):
                self.assertEqual(head["commit"],
                                 "cae49828ed9ab9c1079c7cdf66c5bd337b027515")
                self.assertEqual(head["sha256"], UPSTREAM_SHA256[
                    f"outputs/factory_catalogue_l{level}.csv"])


class TestCircuits(unittest.TestCase):
    def test_every_row_has_a_circuit_with_its_parameters(self):
        for level in (2, 3, 4):
            blob = load(level)
            rows = {c["row"] for c in blob["circuits"]}
            self.assertEqual(rows, set(range(1, blob["rows"] + 1)))
            for circuit in blob["circuits"]:
                with self.subTest(id=circuit["id"]):
                    row = circuit["csv"]
                    self.assertEqual(circuit["N"], int(row["N"]))
                    self.assertEqual(len(odd_columns(circuit)), int(row["N"]))
                    self.assertEqual(len(circuit["outputs"]), int(row["k"]))
                    self.assertEqual(circuit["d_upstream"], int(row["d"]))
                    supports = [tuple(s) for s, _c in circuit["gates"]]
                    self.assertEqual(len(set(supports)), len(supports))
                    self.assertEqual(max(max(s) for s in supports) + 1,
                                     circuit["wires"])

    def test_every_circuit_is_a_borrowed_identity(self):
        """No genuine level-l phase on any monomial that touches a check.

        A parity gate on ``g`` with coefficient ``c`` puts ``(-2)^(t-1) c`` on
        each ``t``-subset of ``g``; on a check-touching subset that must vanish
        modulo ``2^t``, i.e. the coefficients summed over the gates containing
        it must be even.  For ``t <= l`` that is the paper's Theorem 5; above
        ``l`` the prefactor alone makes it vanish.
        """
        for level in (2, 3, 4):
            for circuit in load(level)["circuits"]:
                k = len(circuit["outputs"])
                with self.subTest(id=circuit["id"]):
                    for size in range(1, level + 1):
                        totals = {}
                        for support, coeff in circuit["gates"]:
                            for T in itertools.combinations(support, size):
                                if max(T) >= k:
                                    totals[T] = totals.get(T, 0) + coeff
                        bad = [T for T, total in totals.items() if total % 2]
                        self.assertEqual(bad, [], f"size {size}")

    def test_every_distance_is_witnessed_and_small_ones_are_proved(self):
        for level in (2, 3, 4):
            for circuit in load(level)["circuits"]:
                k, d = len(circuit["outputs"]), circuit["d"]
                odd = [i for i, (_s, c) in enumerate(circuit["gates"]) if c % 2]
                columns = odd_columns(circuit)
                with self.subTest(id=circuit["id"]):
                    witness = circuit["d_witness"]
                    self.assertEqual(len(set(witness)), d)
                    self.assertTrue(set(witness) <= set(odd))
                    self.assertTrue(harmful(
                        columns, k, [odd.index(i) for i in witness]))
                    if len(columns) <= BRUTE_N:
                        for weight in range(1, d):
                            self.assertFalse(any(
                                harmful(columns, k, faults) for faults in
                                itertools.combinations(range(len(columns)),
                                                       weight)))

    def test_the_upstream_distance_errata_are_exactly_the_listed_ones(self):
        found = {(level, c["row"]): (c["d_upstream"], c["d"])
                 for level in (2, 3, 4) for c in load(level)["circuits"]
                 if c["d_upstream"] != c["d"]}
        self.assertEqual(found, UPSTREAM_DISTANCE_ERRATA)


class TestMergeInput(unittest.TestCase):
    def test_each_record_is_the_odd_gates_of_its_circuit(self):
        circuits = {c["id"]: c for c in load(3)["circuits"]}
        records = json.loads(
            (CIRCUITS / "factories_l3.json").read_text())["results"]
        self.assertEqual([r["label"] for r in records], list(circuits))
        for record in records:
            circuit = circuits[record["label"]]
            with self.subTest(id=record["label"]):
                self.assertEqual(record["columns"], odd_columns(circuit))
                self.assertEqual((record["k"], record["N"], record["n"]),
                                 (len(circuit["outputs"]), circuit["wires"],
                                  circuit["N"]))
                # a claim the measurement disproves is not carried
                self.assertEqual(record.get("d"), None
                                 if circuit["d_upstream"] > circuit["d"]
                                 else circuit["d_upstream"])


class TestMasterCatalogue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = json.loads((REPO / "master_catalog" / "master_catalog.json")
                              .read_text())["factories"]
        cls.by_label = {row["catalog_label"]: row for row in cls.rows}

    def holders(self, circuit):
        k, d = len(circuit["outputs"]), circuit["d"]
        columns = odd_columns(circuit)
        gate = read_gate(columns, k)
        return [row for row in self.rows
                if (row["n"], row["k"], row["d"]) == (len(columns), k, d)
                and GC.gl_isomorphic(k, read_gate(row["columns"], k), gate)]

    def test_every_level_3_circuit_is_held_but_the_pseudo_output(self):
        for circuit in load(3)["circuits"]:
            with self.subTest(id=circuit["id"]):
                held = self.holders(circuit)
                self.assertEqual(len(held), 0 if circuit["id"] in REFUSED else 1)

    def test_the_paper_is_credited_where_no_earlier_work_was(self):
        """On exactly the classes the searches found that no earlier
        publication states."""
        found = {row["catalog_label"] for circuit in load(3)["circuits"]
                 for row in self.holders(circuit)}
        self.assertLessEqual(set(EARLIER), found)
        cites = {row["catalog_label"] for row in self.rows
                 if BORROWED in row["citations"]}
        self.assertEqual(cites, found - set(EARLIER))

    def test_an_earlier_publication_is_credited_alone(self):
        for label, keys in EARLIER.items():
            with self.subTest(label=label):
                self.assertEqual(self.by_label[label]["citations"], keys)

    def test_a_class_only_the_imported_circuits_hold_is_filed_under_them(self):
        files = {"borrowed_identities/circuits/circuits_l3.json"}
        for row in self.rows:
            ours = [s for s in row["sources"] if s["file"] in files]
            if not ours:
                continue
            with self.subTest(label=row["catalog_label"]):
                self.assertTrue(set(row["regimes"]) & {
                    "borrowed-identity search: two-group",
                    "borrowed-identity search: symmetry-free"})
                self.assertEqual(row["discovery"], "pre-existing")
                self.assertTrue(all(s["origin"].startswith(
                    "https://github.com/shraggy/Magic_state_factory_search at cae4982")
                    for s in ours))


if __name__ == "__main__":
    unittest.main()
