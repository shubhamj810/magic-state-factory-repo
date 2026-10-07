"""Independent re-derivation of the master catalogue.

`verify_catalog.py` re-derives every row of the shipped file from its columns.
This file does the same job a SECOND time and deliberately does not import the
verifier for the core checks: the parity read-off, the distance enumeration and
the width computation below are written out again here, so a mistake in one of
them has to be made twice to go unnoticed.  It also checks the things only a
consumer can check -- that the catalogue still contains every qualifying row of
the three classification catalogues it inherited and every Pareto point of the
length-54 classification, that no other class within that window beats the
frontier, that its filter is exactly "level 3, distance >= 2", that no class is
in it twice, and that the discovery tag and the citations mean what they say.

SCALE
-----
The catalogue now spans `n = 15..1023` and `k = 1..162`, and the literal
enumerations here do not run at that end of it: `C(1023, 4)` is 4.5e10 subsets
and the meet-in-the-middle shortcut sweeps all `2^k - 1` output targets.  So the
independent implementations are applied to every row they can reach, and the
wide rows are checked by the properties that need no enumeration at all -- a
distance witness is re-checked directly, which verifies the presence half of
every pinned distance without trusting any search.
"""
import itertools
import json
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE.parent
REPO = CATALOGUE.parents[0]
sys.path.insert(0, str(CATALOGUE))
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "classification" / "legacy" / "exhaustive_n38"))

from dedup import sk_canonical                                # noqa: E402
import skcanon as SK                                          # noqa: E402
import faultcore as FC                                        # noqa: E402
import glcanon as GC                                          # noqa: E402
import verify_catalog as VC                                   # noqa: E402

MASTER = CATALOGUE / "master_catalog.json"
#: The three catalogues the master catalogue INHERITED rather than found, all
#: still in this repository: the exhaustive n <= 38 stage and rank-7 census of
#: the length-54 classification, and the symmetry-SAT search.
CATALOGUE_FILES = {
    "exhaustive n<=38": REPO / "classification" / "legacy" / "exhaustive_n38" / "catalog" / "classification_n38.json",
    "census r<=7": REPO / "classification" / "legacy" / "rank7_census" / "catalog" / "census_r7.json",
    "symmetry-SAT search": REPO / "symmetry_sat_search" / "catalog" / "factories.json",
}
#: The length-54 classification's Pareto frontier, copied in unchanged.
FRONTIER = REPO / "classification" / "length54" / "pareto_frontier.json"
PARETO = "exhaustive classification n<=54 (Pareto point)"
SAT = "symmetry-SAT search"
#: Where a source that names a file in this repository points.  Every other
#: ``file`` a source carries is inert provenance -- history, not a path -- and
#: nothing here opens one.
LOCAL_SOURCE_DIRS = ("classification/", "symmetry_sat_search/",
                     "borrowed_identities/")
#: The Borrowed Identities circuits (Singh, Gidney and Jones), rebuilt from the
#: upstream catalogue by `borrowed_identities/export_circuits.py`.
BORROWED_CIRCUITS = REPO / "borrowed_identities" / "circuits" / "circuits_l3.json"
BORROWED = ("borrowed-identity search: two-group",
            "borrowed-identity search: symmetry-free")
#: The classification stages this repository ran itself -- every catalogue under
#: ``classification/`` but the copied length-54 frontier: a source from one of
#: them makes a class ``pre-existing``.
EARLY_STAGES = "classification/"
FRONTIER_DIR = "classification/length54/"
#: The regime `community_contributions/check_submission.py` merges under.
COMMUNITY = "community contribution"
#: Regimes that are not an AI search: the classification, the SAT search, the
#: borrowed-identity searches and a community contribution.
NOT_AI = (PARETO, "exhaustive classification n<=54", SAT, COMMUNITY) + BORROWED
#: The two reports the classification window is credited to: the length-54
#: classification (arXiv:2609.30860) and the symmetry-and-AI report
#: (arXiv:2610.06535).
WILLS, JAIN = "wills2026classification", "jain2026symmetry"
#: The Pareto points the classification's own table (Table tab:complete-pareto)
#: attributes to published protocols, by their index in the frontier file, with
#: the works: these, and only these, are credited to that literature alone.
PUBLISHED_PARETO = {
    0: ["bravyi2005universal"],             # 15T -> T
    5: ["nezami2022classification"],        # 35T -> 2T (restriction of 35T -> 3T)
    6: ["nezami2022classification"],        # 28T -> 2T
    7: ["nezami2022classification"],        # 35T -> CS (restriction of 35T -> 3T)
    9: ["nezami2022classification"],        # 35T -> 3T
    16: ["jacinto2026exploring"],           # 47T -> CCZ
    17: ["jacinto2026exploring"],           # 48T -> CCZ, d = 4
    40: ["gong2026magic"],                  # 48T -> U_5, from Construction 4.21
    64: ["gong2026magic"],                  # 48T -> U_6, from Construction 4.21
}

# the literal routines below are exponential in n and in k; these are the widest
# rows they can be pointed at without becoming the bottleneck of the suite
LITERAL_N = 70
LITERAL_K = 8


def parity(columns, subset):
    """Odd overlap parity of a qubit subset across the columns."""
    want = set(subset)
    return sum(1 for column in columns if want <= set(column)) & 1


def read_gate(columns, k):
    """The monomial set the columns deposit on the outputs."""
    return {frozenset(mono)
            for degree in (1, 2, 3)
            for mono in itertools.combinations(range(k), degree)
            if parity(columns, mono)}


def spectator_free(k, gate):
    """``(q, gate')``: the gate with its spectator outputs removed.

    A spectator direction ``u`` has ``tau(u, -, -) = 0``: the gate is Clifford
    along it, so the output is the gate restricted to a complement of those
    directions, up to CNOT+S -- the "intrinsic output" the length-54
    classification keys on.  Computed here from the phase function itself: the
    spectator directions from the gate's third finite difference, the Z_8
    phase on a complement, and its monomials read back off by Mobius inversion,
    so nothing below reuses `glcanon`'s tensor code.
    """
    def phase(x):
        return sum(1 << (len(m) - 1) for m in gate
                   if all(x >> q & 1 for q in m)) % 8

    def mobius(values, support):
        return sum((-1) ** (len(support) - bin(sub).count("1"))
                   * values[sum(1 << support[j] for j in range(len(support))
                                if sub >> j & 1)]
                   for sub in range(1 << len(support))) % 8

    def tau(u, v, w):
        # third finite difference of the phase, divided by 4
        total = 0
        for a, b, c in itertools.product((0, 1), repeat=3):
            total += (-1) ** (a + b + c) * phase((u if a else 0) ^ (v if b else 0)
                                                 ^ (w if c else 0))
        return ((-total) % 8) // 4

    spectators = [u for u in range(1, 1 << k)
                  if all(tau(u, 1 << b, 1 << c) == 0
                         for b in range(k) for c in range(k))]
    span, complement = [], []

    def independent(vectors, v):
        basis = []
        for w in vectors + [v]:
            for b in basis:
                w = min(w, w ^ b)
            if not w:
                return False
            basis.append(w)
        return True
    for u in spectators:
        if independent(span, u):
            span.append(u)
    for a in range(k):
        if independent(span, 1 << a):
            span.append(1 << a)
            complement.append(1 << a)
    q = len(complement)
    values = {}
    for y in range(1 << q):
        x = 0
        for i in range(q):
            if y >> i & 1:
                x ^= complement[i]
        values[y] = phase(x)
    reduced = set()
    for size in (1, 2, 3):
        for support in itertools.combinations(range(q), size):
            if mobius(values, support) >> (size - 1) & 1:
                reduced.add(frozenset(support))
    return q, reduced


def frontier_protocols():
    """``(protocol, columns, gate)`` for every Pareto point, read off its matrix."""
    data = json.loads(FRONTIER.read_text())
    out = []
    for protocol in data["protocols"]:
        rows = protocol["generator_matrix_rows"]
        columns = [[i for i in range(len(rows)) if rows[i][j] == "1"]
                   for j in range(len(rows[0]))]
        out.append((protocol, columns, read_gate(columns, protocol["q"])))
    return out


def gate_to_string(wants, k):
    by_degree = {1: [], 2: [], 3: []}
    joiner = "," if k > 10 else ""
    for mono in wants:
        by_degree[len(mono)].append(joiner.join(map(str, sorted(mono))))
    parts = []
    for degree in (1, 2, 3):
        parts += sorted(by_degree[degree], key=lambda s: [int(x) for x in
                                                          re.findall(r"\d+", s)]
                        if k > 10 else s)
    return "+".join(parts) if parts else "check-only"


def brute_distance(columns, k, cap=4):
    """Smallest undetectable damaging fault, by exhaustive ascending weight.

    Exhaustive subset enumeration is the least clever and most trustworthy way
    to do this, so it is used wherever it is affordable, and nowhere else.
    """
    masks = [sum(1 << q for q in column) for column in columns]
    output_mask = (1 << k) - 1
    for weight in range(1, cap + 1):
        for support in itertools.combinations(range(len(masks)), weight):
            value = 0
            for index in support:
                value ^= masks[index]
            if value and not value & ~output_mask:
                return weight
    return None


def width_mod_checks(columns, k, N):
    """Rank of the output rows modulo the check span."""
    rows = [sum(1 << j for j, column in enumerate(columns) if q in set(column))
            for q in range(N)]
    basis = []

    def insert(value):
        for element in basis:
            value = min(value, value ^ element)
        if value:
            basis.append(value)
            basis.sort(reverse=True)
            return True
        return False

    for check in rows[k:]:
        insert(check)
    return sum(1 for output in rows[:k] if insert(output))


@unittest.skipUnless(MASTER.exists(), "master_catalog.json is missing")
class TestMasterCatalogue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blob = json.loads(MASTER.read_text())
        cls.rows = cls.blob["factories"]
        cls.small = [r for r in cls.rows
                     if r["n"] <= LITERAL_N and r["k"] <= LITERAL_K]

    # ---------------------------------------------------------------- shape
    def test_every_row_reproduces_its_own_shape(self):
        """n, N, distinctness and the gate, from the columns, on every row."""
        for row in self.rows:
            columns = [sorted(set(c)) for c in row["columns"]]
            k, N = row["k"], row["N"]
            with self.subTest(params=(row["n"], k, row["d"])):
                self.assertEqual(len(columns), row["n"], "n")
                self.assertEqual(len({tuple(c) for c in columns}), len(columns),
                                 "columns must be distinct")
                self.assertTrue(all(columns), "no empty column")
                self.assertEqual(max(max(c) for c in columns) + 1, N, "N")
                wants = FC.recover_gate(FC.rows_over_columns(columns, N), k)
                self.assertEqual(SK.gate_string(wants, k), row["gate"],
                                 "the columns must deposit exactly the stored gate")
                self.assertEqual(set().union(*wants), set(range(k)),
                                 "no idle output")
                report = FC.output_report(FC.rows_over_columns(columns, N), k, N)
                self.assertTrue(report["independent"],
                                "outputs must be independent modulo the check "
                                "span -- no pseudo-outputs")
                self.assertEqual(report["effective_width"], k)
                self.assertGreaterEqual(row["d"], 2, "this catalogue is d >= 2")
                self.assertEqual(row["level"], 3)

    def test_verify_row_is_exercised_across_the_width_range(self):
        """The whole verifier, on one real row per k -- not only the tiny ones.

        `test_verify_catalog` runs `verify_row` on rows with n <= 40 and k <= 4,
        which in this file means six rows, all k <= 2.  Everything the verifier
        does above that width was therefore unexercised end to end: the metric
        cap could move, the gate-string format could change at k = 10, and the
        reference verifier's contradiction check could weaken, with the suite
        green.  One row per distinct k, cheapest first, keeps that honest
        without re-running the whole file.
        """
        by_k = {}
        for row in self.rows:
            if row["k"] not in by_k or row["n"] < by_k[row["k"]]["n"]:
                by_k[row["k"]] = row
        sample = [by_k[k] for k in sorted(by_k) if k <= 12]
        self.assertGreaterEqual(len(sample), 8, "the sample must span the range")
        for row in sample:
            with self.subTest(params=(row["n"], row["k"], row["d"])):
                self.assertEqual(VC.verify_row(row)[1], [])

    def test_an_exact_distance_of_five_is_verified_end_to_end(self):
        """The reference verifier reports ">= 5", so d = 5 is its boundary."""
        row = min((r for r in self.rows if r["d"] == 5 and r["d_is_exact"]),
                  key=lambda r: r["n"], default=None)
        if row is None:
            self.skipTest("no exact d = 5 row in this catalogue")
        self.assertEqual(VC.verify_row(row)[1], [])

    def test_every_shipped_circuit_is_a_source_s_or_says_it_is_not(self):
        """The shipped ``N`` is one a source published, or ``columns_note`` says why.

        Some rows ship a circuit reduced from what their sources hold -- a
        redundant check wire deleted -- and the rule is enforced in both
        directions so that neither an unexplained divergence nor a note
        explaining nothing can sit in the file.  How MANY such rows there are
        is data, not a rule: the GL(k,2) re-key folded one of them into another
        class, whose own circuit its sources do publish.
        """
        explained = 0
        for index, row in enumerate(self.rows):
            published = [s["N"] for s in row["sources"]]
            with self.subTest(row=index + 1,
                              params=(row["n"], row["k"], row["d"])):
                self.assertTrue(published, "every row cites at least one source")
                self.assertEqual("columns_note" in row,
                                 row["N"] not in published,
                                 "a columns_note appears exactly where the "
                                 "shipped circuit is not a source's")
            explained += "columns_note" in row
        self.assertEqual(explained,
                         sum(1 for row in self.rows
                             if row["N"] not in [s["N"] for s in row["sources"]]),
                         "a note exactly on the rows that need one")
        self.assertTrue(explained, "the reduced rows are still in the file")

    def test_no_row_carries_a_check_wire_that_decides_nothing(self):
        """Every row's ``r`` check rows are independent OF EACH OTHER.

        The check-side twin of the pseudo-output assertion above.  A check row
        inside the span of the others carries a syndrome bit that is an XOR of
        theirs for every fault, so it rejects nothing they accept and can be
        deleted with ``n``, ``k``, the gate and the distance all intact -- which
        makes the row's ``N``, the ambient-qubit cost this table is read for,
        one larger than its circuit needs.
        """
        for index, row in enumerate(self.rows):
            columns = [sorted(set(c)) for c in row["columns"]]
            rows_ = FC.rows_over_columns(columns, row["N"])
            with self.subTest(row=index + 1,
                              params=(row["n"], row["k"], row["d"])):
                self.assertEqual(FC.redundant_checks(rows_, row["k"],
                                                     row["N"]), [])

    def test_the_literal_routines_agree_on_every_row_they_can_reach(self):
        """The independent implementations, written out again in this file."""
        for row in self.small:
            columns = [sorted(set(c)) for c in row["columns"]]
            k, N = row["k"], row["N"]
            with self.subTest(params=(row["n"], k, row["d"])):
                wants = read_gate(columns, k)
                self.assertEqual(gate_to_string(wants, k), row["gate"])
                for degree in (1, 2, 3):
                    for mono in itertools.combinations(range(N), degree):
                        if mono[-1] >= k:
                            self.assertFalse(parity(columns, mono),
                                             f"check-touching parity at {mono}")
                self.assertEqual(width_mod_checks(columns, k, N), k)
                distance = brute_distance(columns, k)
                if row["d"] >= 5:
                    self.assertIsNone(distance,
                                      "d >= 5 means no fault of weight <= 4")
                else:
                    self.assertEqual(distance, row["d"], "distance")

    def test_no_check_touching_parity_anywhere(self):
        """The factory condition, on the wide rows too."""
        for row in self.rows:
            columns = [sorted(set(c)) for c in row["columns"]]
            k, N = row["k"], row["N"]
            with self.subTest(params=(row["n"], k, row["d"])):
                rows_ = FC.rows_over_columns(columns, N)
                self.assertEqual(FC.check_contamination(rows_, k, N), [])

    # ------------------------------------------------------------- distance
    def test_every_pinned_distance_carries_a_valid_witness(self):
        """`d_is_exact` means a fault of exactly that weight was exhibited.

        Re-checking it here -- the syndromes XOR to zero, the output parts do
        not, the indices are distinct and there are exactly `d` of them --
        verifies the presence half of every pinned distance in the file without
        trusting any search.  Absence below is what the enumeration above
        proves; together they are the distance.
        """
        pinned = [r for r in self.rows if r["d_is_exact"]]
        self.assertGreater(len(pinned), 0)
        for row in pinned:
            witness = row["d_witness"]
            with self.subTest(params=(row["n"], row["k"], row["d"])):
                self.assertIsNotNone(witness, "a pinned distance needs a witness")
                self.assertEqual(len(witness), row["d"])
                self.assertEqual(row["d_upper"], row["d"])
                self.assertEqual(len(set(witness)), len(witness))
                columns, k = row["columns"], row["k"]
                syndrome = output = 0
                for index in witness:
                    for q in columns[index]:
                        if q < k:
                            output ^= 1 << q
                        else:
                            syndrome ^= 1 << (q - k)
                self.assertEqual(syndrome, 0, "the syndromes must cancel")
                self.assertNotEqual(output, 0, "the output action must not")

    def test_an_unpinned_distance_is_never_dressed_as_a_measured_one(self):
        """A floor may carry a witness, but only ABOVE itself.

        `d = 6` with a weight-7 fault is the honest statement "the distance is
        6 or 7"; `d = 6` with a weight-6 fault would BE a pinned distance and
        would have been reported as one.  A witness at the floor's own weight on
        a row that calls itself unpinned is the one shape that cannot be true.
        """
        for row in self.rows:
            if row["d_is_exact"]:
                continue
            with self.subTest(params=(row["n"], row["k"], row["d"])):
                if row["d_witness"] is None:
                    self.assertIsNone(row["d_upper"])
                    continue
                self.assertEqual(len(row["d_witness"]), row["d_upper"])
                self.assertGreater(row["d_upper"], row["d"],
                                   "a witness at the floor's own weight pins it")

    # ------------------------------------------------------------------ key
    def test_rows_are_distinct_under_the_sk_key(self):
        """No two rows share `(n, k, d, S_k key)`.

        The distance belongs to the key: one gate can be realised at two
        distances, and those are two rows -- `[[176,3]]` `CCZ` at `d = 5` and at
        `d = 6`, for instance -- so without `d` this would report them as one.
        """
        keys = {(row["n"], row["k"], row["d"],
                 json.dumps(row["sk_key"]) if row["sk_key"] is not None
                 else f"fp:{row['sk_fingerprint']}")
                for row in self.rows}
        self.assertEqual(len(keys), len(self.rows))

    def test_no_two_rows_are_the_same_class_up_to_a_frame(self):
        """The class is the distance and the gate up to GL(k,2); this is the
        decision procedure.

        Every same-`(n, k, d)` pair is decided by `glcanon.gl_isomorphic` on the
        gates re-read from the columns here, and must come back a definite
        "different" -- an exhausted search is not a proof of distinctness.
        """
        by_shape = {}
        for row in self.rows:
            columns = [sorted(set(c)) for c in row["columns"]]
            gate = FC.recover_gate(
                FC.rows_over_columns(columns, row["N"]), row["k"])
            by_shape.setdefault((row["n"], row["k"], row["d"]), []).append(
                (row, gate))
        for (n, k, _d), group in by_shape.items():
            for (left, left_gate), (right, right_gate) in \
                    itertools.combinations(group, 2):
                with self.subTest(params=(n, k)):
                    self.assertIs(
                        GC.gl_isomorphic(k, left_gate, right_gate), False,
                        f"[[{n},{k}]] {left['gate']} and {right['gate']} are "
                        f"not proved to be different classes up to a frame")

    def test_the_stored_gate_is_the_canonical_representative(self):
        """Where a canonical form was proved, the row must be shown in it."""
        for row in self.rows:
            if not row["sk_canonical_frame"]:
                self.assertIsNone(row["sk_key"])
                self.assertIn("sk_key_note", row)
                continue
            columns = [sorted(set(c)) for c in row["columns"]]
            wants = FC.recover_gate(
                FC.rows_over_columns(columns, row["N"]), row["k"])
            with self.subTest(gate=row["gate"]):
                self.assertEqual(SK.encode(wants),
                                 tuple(map(tuple, row["sk_key"])))
                if row["k"] <= 7:
                    # the upstream definition, executed literally
                    self.assertEqual(SK.encode(wants),
                                     sk_canonical(row["k"], wants))

    # -------------------------------------------------------------- metrics
    def test_metrics_match_the_recomputation_where_they_exist(self):
        # `factorylib.metrics` memoises to a file inside `factorylib/`, and a
        # test that writes outside the directory it is testing is a test with a
        # side effect.  Point the cache at the copy this catalogue ships, which
        # already holds every gate here, so the check is a lookup and nothing
        # upstream is touched.
        import factorylib.metrics as metrics
        metrics._CACHE_PATH = CATALOGUE / "reduced_degree_cache.json"
        if metrics._CACHE_PATH.exists():
            metrics._DEG_CACHE.update(json.loads(metrics._CACHE_PATH.read_text()))
        from factorylib.metrics import metrics_from_monomials
        for row in self.rows:
            if row["t_count"] is None or row["k"] > 6:
                # exact minimisation over GL(k,2) and a punctured RM coset; both
                # stop being feasible past k = 6, and the build leaves them null
                self.assertTrue(row["k"] > 6 or row["t_count"] is not None)
                continue
            with self.subTest(gate=row["gate"]):
                t_count, _tn, degree, _dn = metrics_from_monomials(row["gate"])
                self.assertEqual(row["t_count"], t_count)
                self.assertEqual(row["poly_degree"], degree)

    def test_a_missing_metric_says_why(self):
        for row in self.rows:
            if row["t_count"] is None:
                with self.subTest(params=(row["n"], row["k"])):
                    self.assertIn("t_count_note", row)
                    self.assertGreater(row["k"], 6)

    # --------------------------------------------------------------- syncing
    def test_it_is_in_sync_with_the_three_original_catalogues(self):
        """Every qualifying row of the three original files is still in here.

        "In here" is up to a frame: the classification tables key on the finer
        S_k relation, so a row of theirs is held when some master row of the
        same `(n, k, d)` is the same GL(k,2) class.

        The reverse containment is not asserted, and must not be: the
        catalogue is the union of these three with every search corpus merged
        into it since, so it is a strict superset of them by construction.

        This is the one check that still reads outside the folder, and it can:
        the three classification catalogues are directories of this repository
        that survive.  Every OTHER source a row names is an inert provenance
        string -- history, not a path -- and nothing here opens one.
        """
        # Only the shapes a classification catalogue actually has, and only
        # then the gate: `read_gate` is the literal C(k,3) enumeration, which is
        # 690,000 monomials over 1,023 columns on the widest master rows and has
        # no business running on rows no classification can contain.
        wanted = set()
        blobs = {}
        for regime, path in CATALOGUE_FILES.items():
            blob = json.loads(path.read_text())
            blobs[regime] = blob["factories"] if isinstance(blob, dict) else blob
            wanted |= {(row["n"], row["k"], row["d"]) for row in blobs[regime]
                       if row.get("level", 3) == 3 and row["d"] >= 2}
        by_shape = {}
        for row in self.rows:
            shape = (row["n"], row["k"], row["d"])
            if shape not in wanted:
                continue
            columns = [sorted(set(c)) for c in row["columns"]]
            by_shape.setdefault(shape, []).append(read_gate(columns, row["k"]))
        for regime, rows in blobs.items():
            for row in rows:
                if row.get("level", 3) != 3 or row["d"] < 2:
                    continue
                columns = [sorted(set(c)) for c in row["columns"]]
                gate = read_gate(columns, row["k"])
                held = any(GC.gl_isomorphic(row["k"], gate, mine)
                           for mine in by_shape.get(
                               (row["n"], row["k"], row["d"]), []))
                with self.subTest(regime=regime, params=(row["n"], row["k"])):
                    self.assertTrue(held,
                                    "a qualifying row of a classification "
                                    "catalogue is missing from the master "
                                    "catalogue")

    # ------------------------------------------------------------- discovery
    def test_the_discovery_tag_is_exactly_what_the_sources_say(self):
        """`AI search` iff the only finders the sources record are AI searches.

        Any other recorded finder -- a classification stage this repository
        ran, the symmetry-SAT search, a borrowed-identity search, or a
        community contribution -- makes the class `pre-existing`.  The sources carry no dates, so this is a
        statement about who is on record, not who was first, and the sources
        answer it in both directions.  It is
        stated on the sources rather than on `regimes` because the length-54
        classification relabels a Pareto point's earlier classification sources
        as that Pareto point, which is right for the claim and wrong for the
        history: a class the n <= 38 stage had in 2025 was not an AI discovery,
        and a class an AI search found before the classification confirmed it
        still was.
        """
        for row in self.rows:
            # a finder other than an AI search: the SAT search, a community
            # contribution, or a classification stage this repository ran
            early = any(s["regime"] in (SAT, COMMUNITY) + BORROWED
                        or (s["file"].startswith(EARLY_STAGES)
                            and not s["file"].startswith(FRONTIER_DIR))
                        for s in row["sources"])
            found = any(s["regime"] not in NOT_AI for s in row["sources"])
            with self.subTest(params=(row["n"], row["k"], row["gate"])):
                self.assertEqual(row["discovery"],
                                 "AI search" if found and not early
                                 else "pre-existing",
                                 f"sources {[s['regime'] for s in row['sources']]}"
                                 f" and discovery {row['discovery']!r} disagree")

    def test_a_pareto_point_is_never_also_filed_as_dominated(self):
        """The two classification regimes contradict each other on one row."""
        for row in self.rows:
            with self.subTest(params=(row["n"], row["k"], row["gate"])):
                self.assertFalse({PARETO, "exhaustive classification n<=54"}
                                 <= set(row["regimes"]))

    def test_regimes_are_exactly_the_sources_regimes(self):
        """A row claims a regime exactly when one of its sources is from it."""
        for row in self.rows:
            with self.subTest(params=(row["n"], row["k"], row["gate"])):
                self.assertEqual(set(row["regimes"]),
                                 {s["regime"] for s in row["sources"]})

    def test_source_attribution_is_real(self):
        """Every `sources` entry must name a row that exists where it says."""
        frontier = {f"protocol {p['index']}": p
                    for p in json.loads(FRONTIER.read_text())["protocols"]}
        for row in self.rows:
            for source in row["sources"]:
                if not source["file"].startswith(LOCAL_SOURCE_DIRS):
                    self.assertIsNotNone(source["provenance"])
                    continue
                if REPO / source["file"] == BORROWED_CIRCUITS:
                    with self.subTest(label=source["label"]):
                        self.assert_borrowed_source(row, source)
                    continue
                if REPO / source["file"] == FRONTIER:
                    with self.subTest(label=source["label"]):
                        protocol = frontier[source["label"]]
                        self.assertEqual(
                            (protocol["n"], protocol["q"], protocol["S"],
                             protocol["d_Z"]),
                            (row["n"], row["k"], source["N"], source["d"]))
                    continue
                with self.subTest(label=source["label"]):
                    path = REPO / source["file"]
                    blob = json.loads(path.read_text())
                    rows = blob["factories"] if isinstance(blob, dict) else blob
                    # each catalogue names its gate under a different key, and
                    # the builder takes whichever one it finds; the label has to
                    # be one that file actually writes, not one particular key
                    labels = {row[key] for row in rows
                              for key in ("label", "gate_human", "gate",
                                          "gate_named", "output_gate")
                              if row.get(key)}
                    self.assertIn(source["label"], labels,
                                  f"{source['label']!r} is not in "
                                  f"{source['file']}")

    def assert_borrowed_source(self, row, source):
        """A Borrowed Identities source names a circuit of the exported file
        that IS this class: the same n, wires N, distance and gate up to a
        frame, read off the circuit's odd-coefficient gates here."""
        if not hasattr(self, "_borrowed"):
            blob = json.loads(BORROWED_CIRCUITS.read_text())
            type(self)._borrowed = {c["id"]: c for c in blob["circuits"]}
        circuit = self._borrowed[source["label"]]
        columns = [sorted(g) for g, c in circuit["gates"] if c % 2]
        self.assertEqual((len(columns), circuit["wires"], circuit["d"]),
                         (row["n"], source["N"], source["d"]))
        self.assertEqual(len(circuit["outputs"]), row["k"])
        self.assertEqual(source["d"], row["d"])
        self.assertTrue(GC.gl_isomorphic(
            row["k"], read_gate(columns, row["k"]),
            read_gate([sorted(set(c)) for c in row["columns"]], row["k"])))

    # ------------------------------------------------------------- citations
    def test_every_citation_resolves(self):
        references = json.loads(MASTER.read_text())["references"]
        for row in self.rows:
            with self.subTest(params=(row["n"], row["k"], row["gate"])):
                self.assertTrue(row["citations"])
                self.assertEqual(len(set(row["citations"])),
                                 len(row["citations"]))
                self.assertLessEqual(set(row["citations"]), set(references))

    def test_a_pareto_point_is_credited_by_who_found_it(self):
        """The 74 Pareto points, by the owner's rule.

        Published before: that work alone.  Otherwise found by this project's
        own searches too: the classification and the symmetry-and-AI report.
        Otherwise: the classification alone.
        """
        seen = set()
        for row in self.rows:
            if PARETO not in row["regimes"]:
                continue
            index, = [int(s["label"].split()[-1]) for s in row["sources"]
                      if REPO / s["file"] == FRONTIER]
            seen.add(index)
            ours = any(s["regime"] != PARETO for s in row["sources"])
            with self.subTest(index=index, params=(row["n"], row["k"])):
                if index in PUBLISHED_PARETO:
                    self.assertEqual(row["citations"], PUBLISHED_PARETO[index])
                elif ours:
                    self.assertEqual(row["citations"], [WILLS, JAIN])
                else:
                    self.assertEqual(row["citations"], [WILLS])
        self.assertEqual(seen, set(range(74)))

    def test_published_works_are_linked(self):
        """Every published work a row credits carries its link -- including the
        project's own two reports, both now on the arXiv.  A community
        contribution's entry may go either way -- linked when the contributor's
        work is published."""
        references = self.blob["references"]
        self.assertEqual(references[JAIN].get("url"),
                         "https://arxiv.org/abs/2610.06535")
        self.assertEqual(references[WILLS].get("url"),
                         "https://arxiv.org/abs/2609.30860")
        # a contributor's own work may be unpublished: exempt only the keys no
        # row credits except rows a community contribution brought or improved
        elsewhere = {key for row in self.rows if COMMUNITY not in row["regimes"]
                     for key in row["citations"]}
        for key, entry in references.items():
            if key not in elsewhere:
                continue
            with self.subTest(key=key):
                self.assertTrue(entry["url"].startswith("https://"))

    def test_the_rest_of_the_classification_window_cites_both_reports(self):
        """Every other class within the length-54 window cites that
        classification and the report this catalogue is published in -- except
        a class a community contribution brought, which is credited to the
        contributor's work.  The window is ``d >= 3``: a distance-2 class is
        outside it whatever its length, and never cites the classification."""
        for row in self.rows:
            if row["d"] < 3:
                with self.subTest(params=(row["n"], row["k"], row["gate"])):
                    self.assertNotIn(WILLS, row["citations"])
                continue
            brought = COMMUNITY in row["regimes"] and WILLS not in row["citations"]
            if row["n"] <= 54 and PARETO not in row["regimes"] and not brought:
                with self.subTest(params=(row["n"], row["k"], row["gate"])):
                    self.assertLessEqual({WILLS, JAIN}, set(row["citations"]))

    # ------------------------------------------------- length-54 classification
    def test_every_pareto_point_is_held_as_that_pareto_point(self):
        """All 74, each on its own row with its own (n, k, d, N) and class.

        Matched through this file's own parity read-off and `glcanon` -- the
        gate the matrix deposits, compared up to a CNOT frame -- and the rows
        tagged as Pareto points are exactly these 74.
        """
        tagged = [row for row in self.rows if PARETO in row["regimes"]]
        protocols = frontier_protocols()
        self.assertEqual(len(protocols), 74)
        self.assertEqual(len(tagged), 74)
        claimed = set()
        for protocol, _columns, gate in protocols:
            with self.subTest(index=protocol["index"]):
                shape = (protocol["n"], protocol["q"], protocol["d_Z"],
                         protocol["S"])
                holders = [
                    i for i, row in enumerate(tagged)
                    if (row["n"], row["k"], row["d"], row["N"]) == shape
                    and row["d_is_exact"]
                    and GC.gl_isomorphic(row["k"], read_gate(
                        [sorted(set(c)) for c in row["columns"]], row["k"]),
                        gate)]
                self.assertEqual(len(holders), 1)
                self.assertNotIn(holders[0], claimed)
                claimed.add(holders[0])

    def test_no_other_class_in_the_window_beats_the_frontier(self):
        """Every other row with n <= 54 is strictly dominated by a Pareto point.

        Dominated means: a Pareto point with the same exact distance and the
        same output once spectators are removed, and no more inputs and no
        more wires, one of them fewer.  A row this fails on would be a
        counterexample to the classification -- or a catalogue row that is
        not the circuit it says -- and either is worth stopping for.  This is
        also the claim the `exhaustive classification n<=54` regime makes.
        """
        protocols = frontier_protocols()
        for row in self.rows:
            # the classification covers d >= 3; a distance-2 row is outside it
            if row["n"] > 54 or row["d"] < 3 or PARETO in row["regimes"]:
                continue
            with self.subTest(params=(row["n"], row["k"], row["d"], row["N"])):
                self.assertTrue(row["d_is_exact"])
                gate = read_gate([sorted(set(c)) for c in row["columns"]],
                                 row["k"])
                q, reduced = spectator_free(row["k"], gate)
                dominating = [
                    p for p, _c, g in protocols
                    if p["q"] == q and p["d_Z"] == row["d"]
                    and p["n"] <= row["n"] and p["S"] <= row["N"]
                    and (p["n"], p["S"]) != (row["n"], row["N"])
                    and GC.gl_isomorphic(q, g, reduced)]
                self.assertTrue(dominating)

    def test_the_filter_admits_exactly_level_3_distance_at_least_2(self):
        """The one property a reader of this table relies on, on its own."""
        for row in self.rows:
            with self.subTest(params=(row["n"], row["k"], row["d"])):
                self.assertEqual(row["level"], 3)
                self.assertGreaterEqual(row["d"], 2)
        self.assertTrue(any(row["d"] == 2 for row in self.rows),
                        "the distance-2 rows are in the file")


if __name__ == "__main__":
    unittest.main()
