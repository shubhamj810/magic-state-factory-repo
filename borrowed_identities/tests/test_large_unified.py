"""The larger unified search: the copy, the circuits, and the catalogue.

* the upstream files are the ones pinned here, byte for byte;
* every row of ``large_unified_factories_l3.csv`` has an entry with the row's
  ``k``, ``n``, ``N``, stage and parameters: the 1,254 at distance 2 in
  ``large_unified_l3.json``, the 37 at distance 3 or more in
  ``large_unified_l3_d3.json``, each at the row's distance or, where the table
  gives only a floor, at least it;
* a two-group entry's construction builds columns with the pinned digest, and
  on every row the upstream gate-list file stores, exactly the upstream's
  gates; a gluing entry's gates are a borrowed identity with ``n`` odd ones;
* wherever the circuit is short enough to check here, with loops that share
  nothing with the exporter: every distance is witnessed by a harmful fault of
  its weight, no single fault is harmful, and at distance 3 no pair is; the gate is the row's where the table spells it out,
  and has the row's number of terms where it does not; and ``A_2`` is the
  literal count of harmful pairs;
* in the master catalogue, every class the merges added carries the entry's
  circuit (as columns up to 1,023 inputs, as its construction in the large
  file above that) and is credited to the paper.

Rebuilding the entries from the upstream code takes about 9 minutes with 6
workers and is `export_large_unified.py --check`, not a test here.
"""
import csv
import hashlib
import io
import itertools
import json
import sys
import unittest
import zipfile
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
FOLDER = HERE.parent
REPO = FOLDER.parent
UPSTREAM = FOLDER / "upstream_large_unified"
CIRCUITS = FOLDER / "circuits" / "large_unified_l3.json"
CIRCUITS_D3 = FOLDER / "circuits" / "large_unified_l3_d3.json"
FILE = "borrowed_identities/circuits/large_unified_l3.json"
FILE_D3 = "borrowed_identities/circuits/large_unified_l3_d3.json"
sys.path.insert(0, str(REPO / "master_catalog"))

import constructions as K                                         # noqa: E402

#: SHA-256 of every file copied from shraggy/Magic_state_factory_search at
#: commit ae9fbf895e2993568f731b22e785e1e1fcb93655.
UPSTREAM_SHA256 = {
    "CITATION.cff": "053096764e8d0dd5d11ee416566ce6a052aa45f0e95cd144dea17d9008642936",
    "LICENSE": "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4",
    "README.md": "f36184a156f578b5869c6d51bdcc63b93bbf4b21d65f5e361f65505b2b71e94d",
    "classification/README.md": "6457de51cd6778aac0f32e3163a8236846c4973a1279fabda869b967fffe9325",
    "classification/classify.py": "73b6be1c89c96868177d7f041296bda9766dc577581a9a880bb30484a1655987",
    "classification/tcount.py": "6fe3540e73ba03b87a806b3c70e4af50ed48e750eb58551bb1419d28c04bcad9",
    "outputs/README.md": "20daed356cc4fb0e83182d0c84510500f417c5779f7fb4c6e03f32776d72cac9",
    "outputs/large_unified_factories_l3.csv": "f031ee23ebe9cfc971782db89a8c7d189a0ac383abb74b82dcc2978fef65b06d",
    "outputs/large_unified_l3_circuits.txt.zip": "a05e9829706bd091284748cf4ad0ed9112a794148dcf76e15b0767b1add3f3ae",
    "searches/README.md": "af008467cddf732f2814d866bbddf76411d200009ac785cf17d35eab2d19edf8",
    "searches/Two_group.py": "10d4a630fe2063c2e74f0d98825cbb576f6506a7d97cc728b2c069ff442e63e0",
    "searches/large_unified.py": "a25b146536a02b4cd2d3c164117da5896ff206d7cdc9163ceec0ef1cfc1b7159",
    "searches/merge_large_unified.py": "fcd0d7f8fd0298766e6970d3966b21c7adbca4ab2b140f5bb3dc131025f3116e",
    "searches/symfree_search.py": "19e841af92067f3919397c4be7cfbc27cc3606f8fae869c9817c0d76fd87b1bc",
    "searches/unified_search.py": "d08496782a4a1fe56cb582e393795f69dca4c6cd19c4a5ca8df5ad1e54cbad44",
}
COMMIT = "ae9fbf895e2993568f731b22e785e1e1fcb93655"
TABLE = "large_unified_factories_l3.csv"
BORROWED = "singh2026borrowed"
STORE_MAX_N = 1023
#: The merge of the 1,254 entries: 684 new classes, 214 stored as columns and
#: 470 as constructions; 559 already held; 11 refused as pseudo-outputs.
ADDED_MAIN = 214
ADDED_LARGE = 470
#: The merge of the 37 entries at distance 3: 13 new classes, 5 stored as
#: columns and 8 as constructions; 24 already held.
ADDED_D3_MAIN = 5
ADDED_D3_LARGE = 8
#: circuits up to this many columns are checked here column by column
CHECK_N = 4095
#: and up to this many, pair by pair
PAIR_N = 300
LITERAL_CAP = 200_000


def load(path=CIRCUITS):
    return json.loads(path.read_text())


def every_circuit():
    return load()["circuits"] + load(CIRCUITS_D3)["circuits"]


def table():
    csv.field_size_limit(sys.maxsize)
    with (UPSTREAM / "outputs" / TABLE).open(newline="", encoding="utf-8") as fh:
        return list(enumerate(csv.DictReader(fh), 2))


def columns_of(entry):
    if "construction" in entry:
        return K.columns(entry["construction"])
    return [s for s, c in entry["gates"] if c % 2]


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


def borrowed_identity_violations(gates, k):
    """Check-touching monomials of size t <= 3 whose coefficients sum odd --
    the paper's Theorem 5 at level 3."""
    bad = []
    for size in (1, 2, 3):
        totals = {}
        for support, coeff in gates:
            for T in itertools.combinations(support, size):
                if max(T) >= k:
                    totals[T] = totals.get(T, 0) + coeff
        bad += [T for T, t in totals.items() if t % 2]
    return bad


def same_up_to_outputs(left, right, k):
    """Whether two column lists are equal after some permutation of the
    output wires 0..k-1; only wires with equal profiles are tried."""
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

    def test_the_circuit_files_name_the_files_they_were_built_from(self):
        for path in (CIRCUITS, CIRCUITS_D3):
            source = load(path)["source"]
            with self.subTest(file=path.name):
                self.assertEqual(source["commit"], COMMIT)
                self.assertEqual(set(source["files"]),
                                 {TABLE, "large_unified_l3_circuits.txt.zip"})
                for name, digest in source["files"].items():
                    self.assertEqual(digest,
                                     UPSTREAM_SHA256[f"outputs/{name}"])


class TestCircuits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.circuits = every_circuit()
        cls.rows = dict(table())

    def test_every_row_has_an_entry_in_the_file_for_its_distance(self):
        self.assertEqual(len(self.rows), 1291)
        two = {line for line, row in self.rows.items() if row["d"] == "2"}
        self.assertEqual(len(two), 1254)
        self.assertEqual([c["line"] for c in load()["circuits"]], sorted(two))
        more = load(CIRCUITS_D3)["circuits"]
        self.assertEqual([c["line"] for c in more],
                         sorted(set(self.rows) - two))
        self.assertTrue(all(c["k"] == 1 and c["d"] == 3 for c in more))
        self.assertEqual(sum("d_table" in c for c in more), 25)

    def test_each_entry_has_its_rows_parameters(self):
        for c in self.circuits:
            row = self.rows[c["line"]]
            with self.subTest(id=c["id"]):
                self.assertEqual(c["id"], f"lu-{c['line']:04d}")
                self.assertEqual((c["k"], c["n"], c["wires"]),
                                 tuple(int(row[f]) for f in ("k", "n", "N")))
                if row["d"].startswith(">="):
                    self.assertEqual(c["d_table"], row["d"])
                    self.assertGreaterEqual(c["d"], int(row["d"][2:]))
                else:
                    self.assertNotIn("d_table", c)
                    self.assertEqual(c["d"], int(row["d"]))
                self.assertEqual((c["stage"], c["params"], c["raw"]),
                                 (row["search_stage"], row["params"], row["raw"]))
                if c["stage"] == "two-group":
                    a, b = (int(p.split("=")[1]) for p in c["params"].split(","))
                    self.assertEqual(c["construction"], {
                        "family": "two-group", "k": c["k"], "N": c["wires"],
                        "s_total": a, "s_O": b})
                    self.assertNotIn("gates", c)
                else:
                    self.assertEqual(c["stage"], "gluing")
                    self.assertNotIn("construction", c)

    def test_every_circuit_has_its_digest_size_and_wires(self):
        for c in self.circuits:
            columns = columns_of(c)
            with self.subTest(id=c["id"]):
                self.assertEqual(len(columns), c["n"])
                self.assertEqual(max(max(s) for s in columns) + 1, c["wires"])
                if "construction" in c:
                    self.assertEqual(K.digest(columns), c["columns_sha256"])
                else:
                    supports = [tuple(s) for s, _c in c["gates"]]
                    self.assertEqual(len(set(supports)), len(supports))

    def test_the_rule_is_the_upstream_gate_list(self):
        """Every two-group row the upstream gate-list file stores (those on at
        most 14 wires): the construction's columns are its rotations, each
        with coefficient 1."""
        with zipfile.ZipFile(UPSTREAM / "outputs" /
                             "large_unified_l3_circuits.txt.zip") as archive:
            name, = archive.namelist()
            text = io.TextIOWrapper(archive.open(name), encoding="ascii").read()
        blocks = {}
        for block in text.split("# ")[1:]:
            head, *lines = block.strip("\n").split("\n")
            blocks[int(head.split()[0]) + 2] = [
                (sorted(int(q) for q in s.split(",")), int(c) % 8)
                for s, c in (line.split(":") for line in lines)]
        compared = 0
        for c in self.circuits:
            if c["stage"] != "two-group" or c["wires"] > 14:
                continue
            with self.subTest(id=c["id"]):
                self.assertEqual(sorted(blocks[c["line"]]),
                                 [(s, 1) for s in K.columns(c["construction"])])
            compared += 1
        self.assertGreater(compared, 450)
        for c in self.circuits:
            if c["stage"] == "gluing":
                with self.subTest(id=c["id"]):
                    self.assertEqual(sorted(blocks[c["line"]]),
                                     sorted((s, coeff) for s, coeff in c["gates"]))

    def test_every_short_circuit_is_a_borrowed_identity(self):
        for c in self.circuits:
            if c["n"] > CHECK_N:
                continue
            gates = c["gates"] if "gates" in c else [
                (s, 1) for s in K.columns(c["construction"])]
            with self.subTest(id=c["id"]):
                self.assertEqual(borrowed_identity_violations(gates, c["k"]), [])

    def test_every_spelled_out_gate_is_the_rows(self):
        for c in self.circuits:
            if "text{terms}" in c["raw"] or c["n"] > CHECK_N:
                continue
            want = {tuple(int(q) - 1 for q in wires)
                    for _name, wires in __import__("re").findall(
                        r"\\mathrm\{(T|CS|CCZ)\}_\{(\d+)\}", c["raw"])}
            with self.subTest(id=c["id"]):
                self.assertEqual(read_gate(columns_of(c), c["k"]), want)

    def test_every_abbreviated_gate_has_the_rows_number_of_terms(self):
        counted = 0
        for c in self.circuits:
            if "text{terms}" not in c["raw"] or c["n"] > CHECK_N:
                continue
            terms = int(c["raw"].split("\\")[0])
            with self.subTest(id=c["id"]):
                self.assertEqual(len(read_gate(columns_of(c), c["k"])), terms)
            counted += 1
        self.assertGreater(counted, 300)

    def test_every_distance_is_witnessed_and_no_lighter_fault_is_harmful(self):
        paired = 0
        for c in self.circuits:
            if c["n"] > CHECK_N:
                continue
            columns = columns_of(c)
            with self.subTest(id=c["id"]):
                self.assertEqual(len(set(c["d_witness"])), c["d"])
                self.assertTrue(harmful(columns, c["k"], c["d_witness"]))
                # no single fault is harmful, so the distance is at least 2
                self.assertFalse(any(harmful(columns, c["k"], [i])
                                     for i in range(len(columns))))
                if c["d"] == 3 and c["n"] <= PAIR_N:
                    self.assertFalse(any(
                        harmful(columns, c["k"], pair)
                        for pair in itertools.combinations(range(c["n"]), 2)))
                    paired += 1
        self.assertEqual(paired, 12)

    def test_the_error_coefficient_is_the_literal_count(self):
        checked = 0
        for c in self.circuits:
            if comb(c["n"], c["d"]) > LITERAL_CAP:
                continue
            columns = columns_of(c)
            with self.subTest(id=c["id"]):
                self.assertEqual(c["A_d"], sum(
                    1 for faults in itertools.combinations(range(c["n"]), c["d"])
                    if harmful(columns, c["k"], faults)))
            checked += 1
        self.assertGreater(checked, 300)


class TestMasterCatalogue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = REPO / "master_catalog"
        cls.main = json.loads((folder / "master_catalog.json")
                              .read_text())["factories"]
        cls.large = json.loads((folder / "master_catalog_large.json")
                               .read_text())["factories"]
        cls.circuits = {c["id"]: c for c in every_circuit()}

    def added(self, rows, file=FILE):
        return [row for row in rows if row["sources"][0]["file"] == file]

    def test_each_added_class_carries_its_circuit_and_the_paper(self):
        for rows, stored in ((self.main, "columns"), (self.large, "construction")):
            for row in self.added(rows) + self.added(rows, FILE_D3):
                circuit = self.circuits[row["sources"][0]["label"]]
                with self.subTest(label=row["catalog_label"]):
                    self.assertEqual(row["citations"], [BORROWED])
                    self.assertEqual(row["discovery"], "pre-existing")
                    self.assertEqual(
                        (row["n"], row["k"], row["d"], row["N"], row["A_d"]),
                        (circuit["n"], circuit["k"], circuit["d"],
                         circuit["wires"], circuit["A_d"]))
                    self.assertIn(stored, row)
                    if stored == "construction":
                        self.assertGreater(row["n"], STORE_MAX_N)
                        self.assertEqual(row["construction"],
                                         circuit["construction"])
                        self.assertEqual(row["columns_sha256"],
                                         circuit["columns_sha256"])
                    else:
                        self.assertTrue(circuit["stage"] == "gluing"
                                        or row["n"] <= STORE_MAX_N)
                        self.assertTrue(same_up_to_outputs(
                            columns_of(circuit), row["columns"], row["k"]))

    def test_the_merge_added_new_classes_to_both_files(self):
        self.assertEqual(len(self.added(self.main)), ADDED_MAIN)
        self.assertEqual(len(self.added(self.large)), ADDED_LARGE)
        self.assertEqual(len(self.added(self.main, FILE_D3)), ADDED_D3_MAIN)
        self.assertEqual(len(self.added(self.large, FILE_D3)), ADDED_D3_LARGE)


if __name__ == "__main__":
    unittest.main()
