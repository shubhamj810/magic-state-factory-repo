"""The unified-search import: the copy, the circuits, and what the master
catalogue does with them.

* the upstream files are the ones pinned here, byte for byte;
* every level-3 row of ``all_factories.csv`` and ``l3_k78_targets.csv``, and
  every one of ``large_sweep.csv`` up to ``n = 4095``, has a circuit -- or, for
  the last two tables, repeats one that does -- with the row's ``k``, ``n``,
  ``N`` and ``d``;
* every circuit is a borrowed identity, deposits the row's gate where the
  table spells it out, and has its distance witnessed (and, on small circuits,
  the absence below it proved by brute force), all re-checked here with loops
  that share nothing with the exporter;
* ``A_d`` is the literal count of harmful weight-``d`` faults on every
  circuit small enough to enumerate, and equals the upstream's own error
  coefficient on all seven level-3 targets it publishes;
* in the master catalogue, every class the merge added carries its circuit
  and is credited to the paper; no Clifford-padding circuit is held, and
  each of those has an output that is a combination of the others modulo the
  checks.

Regenerating the circuits from the upstream code takes about nine minutes
and is `export_unified.py --check`, not a test here.
"""
import csv
import hashlib
import itertools
import json
import sys
import unittest
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
FOLDER = HERE.parent
REPO = FOLDER.parent
UPSTREAM = FOLDER / "upstream_unified"
CIRCUITS = FOLDER / "circuits"
FILE = "borrowed_identities/circuits/unified_l3.json"

#: SHA-256 of every file copied from shraggy/Magic_state_factory_search at
#: commit 46270145dc77643672ee4afbc9ff9f4b48bab083.
UPSTREAM_SHA256 = {
    "CITATION.cff": "136c5534d8a4cd2a63ed85a85ce690f73a74705161416d4071325f74d7f1f9ce",
    "LICENSE": "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4",
    "README.md": "dd5004235e5b39294a12e3075754780a0db7c4fa49a74708f7fba54e9d4c44b4",
    "classification/README.md": "6457de51cd6778aac0f32e3163a8236846c4973a1279fabda869b967fffe9325",
    "classification/classify.py": "73b6be1c89c96868177d7f041296bda9766dc577581a9a880bb30484a1655987",
    "classification/export_circuit.py": "ee04c8397c2cb8cff97ee6274dc1e60404b523c6a30b01ad54f2fdede8e7e1b5",
    "classification/quirk.py": "1cba19eb1843b95916156631600d90c9166c5f866ee4c48aadd9e717d5b8e335",
    "classification/tcount.py": "6fe3540e73ba03b87a806b3c70e4af50ed48e750eb58551bb1419d28c04bcad9",
    "outputs/README.md": "0a98631ca6a5caafb6bebb6a95f30da215c7556dcccd1bb3bb4eea62606fafe5",
    "outputs/all_factories.csv": "11ef8c27be171e1075999d3f5e827b24385f98d7d2c484a8a9367582b271032c",
    "outputs/all_factories_with_quirk.csv.zip": "e486a5afdfdb53f69d0e856ad9b31ff905732ed2634e86e2bd24d106e0ad9a25",
    "outputs/error_coefficients.json": "7e8c62aa061aed3a5d19252e2ad4caae5e5a0f9f589e6022572a5907a4e60dd2",
    "outputs/l3_k78_targets.csv": "1232f8b69867f95a4c2f61c9bf4c9799ab37878d37706b962367d84c7ddb20fa",
    "outputs/large_sweep.csv": "416daa19bf28c158d7a7710256aac8ea2623adad46ceb0081ae20a363fbe4fce",
    "outputs/literature_refs.json": "cae44e84bc0d477db04ef3d24aab6dabac7b057134ee1e71e2d5bb3a02160e02",
    "outputs/smallest_per_class.csv": "fc2cb4c73fd28c51ce5d220faa233b2f158fc4396579462130bd729ee41580b3",
    "searches/README.md": "b1fbd01c7644b6310929bd0f67bdd4c9d559aa415afc57f11ce12c1036ce4ca1",
    "searches/Two_group.py": "10d4a630fe2063c2e74f0d98825cbb576f6506a7d97cc728b2c069ff442e63e0",
    "searches/coset_certify.py": "95bdebac4c1b124575184b366d2afb1df674c876dc21b27cbf16525648924df4",
    "searches/error_coefficients.py": "f347974edbc6e5cbe021c9eb1cf858f17823cd8c17d5932e72a0b90659c7faf9",
    "searches/large_k_sweep.py": "ae7db4ba56186159f092f77d47960165015fe55e56e51711543d1b16355a4279",
    "searches/large_sweep.py": "17da8a0d43824b4aea0f5f1902603efde710d660f31c6997e98a3e1aa22e4629",
    "searches/sat_certify.py": "3d677b1678a2ee5c4c3a0d69982e1cf2184b8239f2450eaf93fd18b410db8fd9",
    "searches/symfree_search.py": "19e841af92067f3919397c4be7cfbc27cc3606f8fae869c9817c0d76fd87b1bc",
    "searches/unified_search.py": "8ecbcdee77ff7fcf4c7c207919f90eaa2704404535aebf76770db6e25a888a53",
}
LARGE_SWEEP_MAX_N = 4095
BORROWED = "singh2026borrowed"
#: the non-padding circuits the catalogue refuses as pseudo-outputs: the
#: paper's [[8,4,2]], two k = 6 two-group circuits and one SAT circuit, each
#: of whose outputs includes one equal to others modulo the checks
REFUSED = {"af-0649", "af-1079", "af-1081", "af-1082"}
BRUTE_N = 40
LITERAL_CAP = 200_000


def load():
    return json.loads((CIRCUITS / "unified_l3.json").read_text())


def table(name):
    with (UPSTREAM / "outputs" / name).open(newline="", encoding="utf-8") as fh:
        return list(enumerate(csv.DictReader(fh), 2))


def harmful(columns, k, faults):
    checks, outputs = set(), set()
    for index in faults:
        for q in columns[index]:
            (outputs if q < k else checks).symmetric_difference_update({q})
    return not checks and bool(outputs)


def read_gate(columns, k):
    return {tuple(m) for size in (1, 2, 3)
            for m in itertools.combinations(range(k), size)
            if sum(1 for c in columns if set(m) <= set(c)) % 2}


def same_up_to_outputs(left, right, k):
    """Whether two column lists are equal after some permutation of the
    output wires 0..k-1 -- the catalogue stores a circuit in its canonical
    output frame.  Only wires with equal profiles (the check parts of the
    columns through them) are tried against each other."""
    if len(left) != len(right):
        return False
    target = {frozenset(c) for c in right}

    def profile(columns, q):
        return sorted(tuple(sorted(x for x in c if x >= k))
                      for c in columns if q in c)
    mine = [profile(left, q) for q in range(k)]
    theirs = [profile(right, q) for q in range(k)]
    options = [[q2 for q2 in range(k) if theirs[q2] == mine[q]] for q in range(k)]

    def search(q, image):
        if q == k:
            return {frozenset(image[x] if x < k else x for x in c)
                    for c in left} == target
        return any(search(q + 1, image + [q2]) for q2 in options[q]
                   if q2 not in image)
    return search(0, [])


def rank(vectors):
    basis = []
    for v in vectors:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return len(basis)


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

    def test_the_circuit_file_names_the_tables_it_was_built_from(self):
        source = load()["source"]
        self.assertEqual(source["commit"],
                         "46270145dc77643672ee4afbc9ff9f4b48bab083")
        for name, digest in source["files"].items():
            self.assertEqual(digest, UPSTREAM_SHA256[f"outputs/{name}"])


class TestCircuits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.circuits = load()["circuits"]

    def test_every_row_has_a_circuit(self):
        lines = {(c["table"], c["line"]) for c in self.circuits}
        main = [(line, r) for line, r in table("all_factories.csv") if r["l"] == "3"]
        self.assertEqual(len(main), 562)
        for line, _row in main:
            self.assertIn(("all_factories.csv", line), lines)
        # a large-sweep or k = 7, 8 row has its own circuit or repeats an
        # all_factories one with the same k, n, N and d
        shapes = {(c["k"], c["n"], c["wires"], c["d"]) for c in self.circuits}
        sweep = [(line, r) for line, r in table("large_sweep.csv")
                 if r["l"] == "3" and int(r["n"]) <= LARGE_SWEEP_MAX_N]
        for name, rows in (("large_sweep.csv", sweep),
                           ("l3_k78_targets.csv", table("l3_k78_targets.csv"))):
            for line, row in rows:
                with self.subTest(table=name, line=line):
                    self.assertTrue((name, line) in lines or (
                        int(row["k"]), int(row["n"]), int(row["N"]),
                        int(row["d"])) in shapes)

    def test_each_circuit_has_its_rows_parameters(self):
        rows = {name: dict(table(name)) for name in
                ("all_factories.csv", "large_sweep.csv", "l3_k78_targets.csv")}
        for c in self.circuits:
            row = rows[c["table"]][c["line"]]
            with self.subTest(id=c["id"]):
                self.assertEqual((c["k"], c["n"], c["wires"], c["d"]),
                                 tuple(int(row[f]) for f in ("k", "n", "N", "d")))
                odd = [s for s, coeff in c["gates"] if coeff % 2]
                self.assertEqual(c["columns"], odd)
                self.assertEqual(len(odd), c["n"])
                supports = [tuple(s) for s, _c in c["gates"]]
                self.assertEqual(len(set(supports)), len(supports))
                self.assertEqual(max(max(s) for s in supports) + 1, c["wires"])

    def test_every_circuit_is_a_borrowed_identity(self):
        """Every check-touching monomial of size t <= 3 gets coefficients
        summing to an even number -- the paper's Theorem 5 at level 3."""
        for c in self.circuits:
            k = c["k"]
            with self.subTest(id=c["id"]):
                for size in (1, 2, 3):
                    totals = {}
                    for support, coeff in c["gates"]:
                        for T in itertools.combinations(support, size):
                            if max(T) >= k:
                                totals[T] = totals.get(T, 0) + coeff
                    self.assertEqual([T for T, t in totals.items() if t % 2], [])

    def test_every_spelled_out_gate_is_the_rows(self):
        for c in self.circuits:
            if "text{terms}" in c["raw"]:
                continue
            want = set()
            for name, wires in __import__("re").findall(
                    r"\\mathrm\{(T|CS|CCZ)\}_\{(\d+)\}", c["raw"]):
                want.add(tuple(int(q) - 1 for q in wires))
            with self.subTest(id=c["id"]):
                self.assertEqual(read_gate(c["columns"], c["k"]), want)

    def test_every_distance_is_witnessed_and_small_ones_are_proved(self):
        for c in self.circuits:
            k, d, columns = c["k"], c["d"], c["columns"]
            with self.subTest(id=c["id"]):
                self.assertEqual(len(set(c["d_witness"])), d)
                self.assertTrue(harmful(columns, k, c["d_witness"]))
                if len(columns) <= BRUTE_N:
                    for weight in range(1, d):
                        self.assertFalse(any(
                            harmful(columns, k, faults) for faults in
                            itertools.combinations(range(len(columns)), weight)))

    def test_the_error_coefficient_is_the_literal_count(self):
        checked = 0
        for c in self.circuits:
            if comb(c["n"], c["d"]) > LITERAL_CAP:
                continue
            with self.subTest(id=c["id"]):
                self.assertEqual(c["A_d"], sum(
                    1 for faults in itertools.combinations(range(c["n"]), c["d"])
                    if harmful(c["columns"], c["k"], faults)))
            checked += 1
        self.assertGreater(checked, 400)

    def test_the_error_coefficients_agree_with_the_upstream(self):
        """All seven level-3 targets of ``outputs/error_coefficients.json``."""
        published = [e for e in json.loads(
            (UPSTREAM / "outputs" / "error_coefficients.json").read_text())
            if e["l"] == 3]
        self.assertEqual(len(published), 7)
        names = {"T": 1, "CS": 2, "CCZ": 3}
        for e in published:
            terms = e["target"].replace("T3...T7", "T3 T4 T5 T6 T7").split()
            gate = set()
            for t in terms:
                name = t.rstrip("0123456789")
                wires = t[len(name):]
                self.assertEqual(len(wires), names[name])
                gate.add(tuple(int(q) - 1 for q in wires))
            hits = [c for c in self.circuits if c["k"] == e["k"]
                    and c["n"] == e["n"] and read_gate(c["columns"], c["k"]) == gate]
            with self.subTest(target=e["target"]):
                self.assertTrue(hits)
                self.assertEqual({c["A_d"] for c in hits}, {e["c"]})


class TestMasterCatalogue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = json.loads((REPO / "master_catalog" / "master_catalog.json")
                              .read_text())["factories"]
        cls.circuits = {c["id"]: c for c in load()["circuits"]}
        cls.held = {}
        for row in cls.rows:
            for source in row["sources"]:
                if source["file"] == FILE:
                    cls.held.setdefault(source["label"], []).append(row)

    def test_each_class_the_merge_added_carries_its_circuit_and_the_paper(self):
        added = [row for row in self.rows if row["sources"][0]["file"] == FILE]
        self.assertEqual(len(added), 250)
        for row in added:
            circuit = self.circuits[row["sources"][0]["label"]]
            with self.subTest(label=row["catalog_label"]):
                self.assertEqual(row["citations"], [BORROWED])
                self.assertEqual(row["discovery"], "pre-existing")
                self.assertEqual((row["n"], row["k"], row["d"], row["N"]),
                                 (circuit["n"], circuit["k"], circuit["d"],
                                  circuit["wires"]))
                self.assertTrue(same_up_to_outputs(circuit["columns"],
                                                   row["columns"], row["k"]))
                self.assertEqual(row["A_d"], circuit["A_d"])

    def test_no_padding_or_pseudo_output_circuit_is_held(self):
        refused = {i for i, c in self.circuits.items()
                   if c["stage"] == "padding"} | REFUSED
        self.assertEqual(len(refused), 355)
        self.assertEqual(refused & set(self.held), set())
        for ident in refused:
            c = self.circuits[ident]
            k, wires = c["k"], c["wires"]
            rows = [sum(1 << j for j, col in enumerate(c["columns"]) if q in col)
                    for q in range(wires)]
            with self.subTest(id=ident):
                # the outputs are dependent modulo the check span
                self.assertLess(rank(rows) - rank(rows[k:]), k)


if __name__ == "__main__":
    unittest.main()
