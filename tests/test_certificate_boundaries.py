"""Mutation sweep over every acceptance boundary in the repository.

Each `TestCase` below names one decision -- "this census may be published", "this
row may enter the master catalogue" -- states the claim that decision makes, and
hands `mutation.sweep` an artifact the boundary really does accept.  The sweep
mutates every field through the battery in `mutation.SUBSTITUTES` and requires
every mutation to be rejected, or declared benign here with a reason.

Read the `benign` maps as documentation: they are the exhaustive list of fields
that do NOT hold up a published claim, and each one had to be argued for.

See `mutation.py` for why the sweep is shaped this way.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))

from mutation import (DELETE, Boundary, get_path,              # noqa: E402
                      rejects_by_raising, sweep, with_mutation)


#: Workflow directories `_module` has put on `sys.path`.  See `_module`.
_INJECTED: set[Path] = set()


def _module(directory: str, name: str):
    """Import a workflow module the way its own CLI does, from its directory.

    By FILE, under a name qualified by its directory: two workflows both call
    their builder `build_catalog`, so a plain import gave whichever one loaded
    first to every boundary that asked for either.  The directory still goes on
    `sys.path` first, because these modules import their siblings by bare name.

    Qualifying the name is not enough on its own, because those sibling imports
    are NOT qualified.  `master_catalog/merge_results.py` says
    `import verify_catalog`, and `symmetry_sat_search/rebuild_from_groups.py`
    says `from verify_catalog import ...` -- two different files, one bare
    name, and whichever ran first left its answer in `sys.modules` for the
    other to find.  So each call also EVICTS the bare-named modules that were
    loaded out of some other workflow's directory, and the next boundary
    re-imports its own sibling from the `sys.path` this call just re-ordered.
    Only directories this helper injected are eligible for eviction, so
    `tests/mutation.py` and the installed packages are never touched.
    """
    path = ROOT / directory
    _INJECTED.add(path)
    for entry in (str(ROOT), str(path)):
        while entry in sys.path:
            sys.path.remove(entry)
        sys.path.insert(0, entry)
    for loaded in [n for n in sys.modules if "." not in n and "__" not in n]:
        origin = getattr(sys.modules[loaded], "__file__", None)
        if origin and Path(origin).parent in _INJECTED - {path}:
            del sys.modules[loaded]
    qualified = f"{directory.replace('/', '_')}__{name}"
    if qualified in sys.modules:
        return sys.modules[qualified]
    spec = importlib.util.spec_from_file_location(qualified, path / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[qualified] = module
    spec.loader.exec_module(module)
    return module


# ============================================================ r <= 7 census
class TestCensusCertificate(unittest.TestCase):
    """Which census runs may be folded into the published frontier.

    The baseline is a REAL run -- one geometry, small width -- with its scope
    fields raised to the full window.  Working from a real payload is the point:
    a hand-written baseline only covers the fields whoever wrote it remembered,
    and this boundary has already been past two audits for fields nobody was
    looking at (`restrictions`, then `untruncated`).
    """

    @classmethod
    def setUpClass(cls):
        rank7 = _module("classification/legacy/rank7_census", "rank7")
        cls.build_catalog = _module("classification/legacy/rank7_census", "build_catalog")
        cls.window = rank7.WINDOW_NMAX
        cls.count_parents = staticmethod(rank7.count_parents)
        with tempfile.TemporaryDirectory() as tmp:
            real = rank7.run(
                output=str(Path(tmp) / "census.json"), mode="reps", nmax=44,
                kmax=2, dedup="gl", class_indices=[306], origins=[0],
                max_parents=1, node_budget=10_000, orbit_budget=10_000,
            )
        geometries = rank7.count_parents()
        # Raise the real run's scope to what a full census would have recorded.
        # Everything else -- data_integrity, the budgets, the geometry and
        # factory records, rank_counts -- is left exactly as the producer wrote
        # it, so the sweep covers the real schema and not a summary of it.
        cls.baseline = {
            **real,
            "mode": "all",
            "dedup": "symmetric",
            "kmax": 4,
            "restrictions": {"mode": "all", "nmax": 44, "kmax": 4,
                             "class_indices": None, "origins": None,
                             "max_parents": None},
            "covers_full_window": True,
            "geometries_expected": geometries,
            "processed_parents": geometries,
            "complete": True,
            "untruncated": True,
            "stopped_by_max_parents": False,
            "incomplete_reasons": [],
        }

    def _tolerates(self, path, value):
        """Mutations that leave the claim true, and why each one does."""
        # `mode` and `kmax` appear twice: once at top level for a reader, once
        # under `restrictions` as the record of what ran.  Dropping the
        # convenience copy loses nothing -- the validator falls back to the
        # authoritative one -- but a copy that DISAGREES is rejected, which is
        # what the sweep's other mutations of these paths check.
        if path in ("mode", "kmax", "restrictions.kmax") and value is DELETE:
            return True
        # A file may record no reasons at all; only a non-empty list contradicts
        # `complete`.
        if path == "incomplete_reasons":
            return value is DELETE or not value
        # A sweep WIDER than the window certifies the window too -- but only if
        # it really visited the geometries that wider window contains.  Raising
        # `nmax` alone leaves the file claiming a larger sweep than the count it
        # reports, which is why this asks the orbit table rather than comparing
        # against 44.
        if path == "restrictions.nmax":
            if not isinstance(value, int) or isinstance(value, bool) \
                    or value < self.window:
                return False
            return self.count_parents(nmax=value) == self.baseline[
                "geometries_expected"]
        return False

    def test_no_field_may_be_weakened_unnoticed(self):
        boundary = Boundary(
            name="census certificate",
            claim="Accepting it publishes it as a complete classification of "
                  "every marked geometry in the r<=7, n<=44 window.",
            baseline=self.baseline,
            validate=self.build_catalog._certificate_problems,
            skip=("factories", "geometries", "rank_counts"),
            benign={
                "scope": "a human-readable summary; every claim it states is "
                         "re-derived from the structured fields",
                "data_name": "the table is identified by data_sha256; the name "
                             "is for the reader",
                "factories": "the certificate gate decides whether the RUN is "
                             "authoritative; each row is then re-derived from "
                             "its own columns by enrich() and exact_verify",
                "geometries": "a record of what was visited; the count that "
                              "matters is recomputed from the orbit table",
                "rank_counts": "a summary of the geometries actually swept, "
                               "already covered by the geometry count",
                "node_budget_per_parent": "a budget being SET is not a budget "
                                          "being hit; `untruncated` records the "
                                          "latter and is required to be true",
                "orbit_budget_per_gate": "as node_budget_per_parent",
                "data_integrity.classes": "data_sha256 pins the exact table "
                                          "byte for byte, which is strictly "
                                          "stronger than any count taken from it",
                "data_integrity.expected_classes": "as data_integrity.classes",
                "data_integrity.max_degree": "as data_integrity.classes",
                "data_integrity.orbit_size_sum": "as data_integrity.classes",
                "data_integrity.expected_orbit_size_sum": "as above",
                "data_integrity.corrected_class_indices":
                    "the audited in-memory correction is a property of the "
                    "parser, tested in tests/test_data.py",
            },
            tolerates=self._tolerates,
        )
        counts = sweep(self, boundary)
        self.assertGreater(counts["rejected"], 100, counts)


# ======================================================= n <= 38 input passes
class TestExhaustiveInputPasses(unittest.TestCase):
    """Whether the shipped result passes really cover the n <= 38 window.

    The baseline is the SHIPPED set of passes, so this sweep runs against the
    files the published catalogue was actually built from.
    """

    @classmethod
    def setUpClass(cls):
        cls.build_catalog = _module("classification/legacy/exhaustive_n38", "build_catalog")
        files = sorted(p for p in cls.build_catalog.RESULTS.glob("*.json")
                       if "certificate" not in p.name)
        assert files, "no result passes in classification/legacy/exhaustive_n38/results"
        # `factories` is emptied rather than carried: validate_inputs never reads
        # the rows (build_catalog re-derives each one later), and deep-copying
        # tens of thousands of them once per mutation would dominate the runtime.
        # Keyed by STEM, not filename: the sweep's paths are dotted, so a key
        # like "hard_parent_n31.json" would read as two path segments.  The
        # filename is restored in _validate, and it matters -- validate_inputs
        # recognises the n=31 hand-off by name.
        cls.passes = {}
        for path in files:
            blob = json.loads(path.read_text(encoding="utf-8"))
            blob["factories"] = []
            cls.passes[path.stem] = blob
        # The k=3 pass is left OUT of the baseline: a width-4 pass enumerates
        # every frame up to width 4, so the two k=4 passes plus the n=31 hand-off
        # already cover the window, and the k=3 pass contributes no row they lack
        # (test_the_k3_pass_is_redundant states both halves).  Including it would
        # make its own fields unfalsifiable here -- mutating a redundant pass's
        # coverage changes nothing -- and the sweep's whole value is that every
        # field in the baseline is load-bearing.
        cls.baseline = {stem: blob for stem, blob in cls.passes.items()
                        if "k3" not in stem}

    def _validate(self, artifact):
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for stem, blob in artifact.items():
                target = Path(tmp) / f"{stem}.json"
                target.write_text(json.dumps(blob), encoding="utf-8")
                paths.append(str(target))
            return self.build_catalog.validate_inputs(paths)

    def test_no_pass_may_be_narrowed_unnoticed(self):
        boundary = Boundary(
            name="n<=38 input passes",
            claim="Accepting them publishes the catalogue as every distance-3 "
                  "factory in the window, at every width it admits.",
            baseline=self.baseline,
            validate=self._validate,
            skip=("hard_parent_n31.factories",),
            benign={
                # Named per file, because a benign field in one producer's output
                # is not automatically benign in another's.
                "hard_parent_n31.scope": "a human-readable summary",
                "hard_parent_n31.method": "a human-readable summary",
                "hard_parent_n31.automorphism_group": "prose describing "
                    "the collapse; the classification it produced is verified "
                    "row by row in build_catalog",
                "hard_parent_n31.dedup_signature": "prose; the key is "
                    "re-applied by build_catalog's own sk_canonical",
                "hard_parent_n31.distinct_factories": "a count of rows that "
                    "are each re-derived from their columns downstream",
                "hard_parent_n31.factories": "as distinct_factories",
                "hard_parent_n31.incomplete_reasons": "a message list; "
                    "`complete` and `kmax` are the fields that decide",
            } | {
                f"{name}.{field}": reason
                for name in ("quotient_catalog_k4_easy",
                             "quotient_catalog_k4_n31_rest")
                for field, reason in (
                    ("scope", "a human-readable summary"),
                    ("dedup_signature", "prose; the key is re-applied by "
                                        "build_catalog"),

                    ("partial_ns", "a per-n breakdown of the truncation that "
                                   "`complete` already reports"),
                    ("distinct_factories", "a count of rows each re-derived "
                                           "downstream"),
                    ("factories", "as distinct_factories"),
                    ("stats", "per-n counters; coverage is decided by ns_swept"),
                    ("incomplete_reasons", "a message list; `complete` decides"),
                )
            },
            tolerates=self._tolerates,
            overstates=self._overstates,
        )
        counts = sweep(self, boundary)
        self.assertGreater(counts["rejected"], 40, counts)

    def _tolerates(self, path, value):
        """Mutations that leave the coverage claim true."""
        B = self.build_catalog
        # Sweeping WIDER than the catalogue needs still covers it.
        if path.endswith(".kmax"):
            floor = (B.HARD_PARENT_KMAX if path.startswith("hard_parent")
                     else B.LADDER_KMAX)
            return (isinstance(value, int) and not isinstance(value, bool)
                    and value >= floor)
        # A pass that deferred nothing may say so by omission.
        if path.endswith(".deferred_ns"):
            return ((value is DELETE or not value)
                    and not get_path(self.baseline, path))
        return False

    def _overstates(self, path, value):
        """Mutations by which a pass claims MORE than it recorded.

        `--skip-classes 0` at n=31 is recorded by the producer, and editing that
        record makes the pass claim it swept the class it skipped.  Nothing here
        can refute that: coverage is read from what the passes SAY, and only
        re-running the pass shows what it did.  That is the boundary's limit, and
        it is why the deferral is written by `classify.py` rather than inferred.
        """
        if not path.startswith("quotient_catalog_k4_n31_rest.deferred_ns"):
            return False
        mutated = with_mutation(self.baseline, path, value)
        recorded = (mutated["quotient_catalog_k4_n31_rest"]
                    .get("deferred_ns") or {})
        try:
            deferred = {int(c) for c in recorded.get("31", [])}
        except (AttributeError, TypeError, ValueError):
            return False       # unreadable, so the validator rejects it outright
        # Strictly fewer deferrals than the pass recorded: it now claims the
        # class it skipped.  A mutation that swaps WHICH class was deferred is
        # not this case -- it leaves another class uncovered and is rejected.
        return deferred < {0}

    def test_the_k3_pass_is_redundant(self):
        """Why the shipped k=3 pass is not part of the baseline above.

        A pass run at `--kmax 4` enumerates every output frame up to width 4, so
        the k=3 sweep is a subset of it.  Both halves are checked here, because
        the claim is load-bearing for the sweep's design: the input set still
        validates without it, and it contributes no (n, k, gate) row the others
        lack.  It ships as provenance for the cheap pass that ran first, not as
        part of the coverage argument.
        """
        self.assertEqual(self._validate(self.baseline), [],
                         "the k=4 passes plus the n=31 hand-off must cover the "
                         "window on their own")
        rows = {stem: {(f["n"], f["k"], f["gate"])
                       for f in json.loads(path.read_text(encoding="utf-8"))
                       ["factories"]}
                for stem, path in ((p.stem, p) for p in sorted(
                    self.build_catalog.RESULTS.glob("*.json"))
                    if "certificate" not in p.name)}
        k3 = set().union(*(v for k, v in rows.items() if "k3" in k))
        others = set().union(*(v for k, v in rows.items() if "k3" not in k))
        self.assertEqual(k3 - others, set(),
                         "the k=3 pass contributes rows nothing else covers, so "
                         "it belongs in the coverage argument and in the sweep")


# ==================================================== master catalogue rows
class TestMasterCatalogueRow(unittest.TestCase):
    """Whether a SHIPPED catalogue row may stand as a level-3, d>=3 factory.

    The boundary moved when the catalogue stopped being built from source
    corpora and became a permanent file that is re-verified in place: the
    decision is no longer "may this source record be admitted?" but "does this
    row still follow from its own columns?", and `verify_catalog.verify_row`
    is the whole of it.  So the baseline is a REAL SHIPPED ROW, which is a
    stronger place to sweep from than a source record ever was -- every field
    the catalogue publishes is present in it, in the shape a reader actually
    reads.
    """

    @classmethod
    def setUpClass(cls):
        cls.verifier = _module("master_catalog", "verify_catalog")
        rows = json.loads(
            (ROOT / "master_catalog" / "master_catalog.json").read_text(
                encoding="utf-8"))["factories"]
        # A row with three outputs and monomials of every degree 1-3, so every
        # check in verify_row is live -- and the SMALLEST such row, because the
        # checks are per-field and identical for every row while their cost is
        # not: the distance sweep is O(n^4) and the k=6 T-count decoder is
        # another fifty times that, which would make this sweep minutes long
        # for no extra coverage.  Every shipped row is verified in full by
        # master_catalog/tests and by verify_catalog.py itself.
        wide = [row for row in rows
                if row["k"] == 3
                and {len(Q) for Q in cls.verifier.derived_gate(row["columns"], 3)}
                == {1, 2, 3}]
        cls.baseline = min(wide, key=lambda row: (row["n"], row["N"]))

    def _validate(self, row):
        _facts, problems = self.verifier.verify_row(row)
        return problems

    def test_no_published_parameter_may_disagree_with_the_columns(self):
        boundary = Boundary(
            name="master catalogue row",
            claim="Publishing it asserts [[n,k,d]], the gate, the T-count and "
                  "the degree as facts about those columns.",
            baseline=self.baseline,
            skip=("columns", "sources"),
            validate=self._validate,
            benign={
                "regimes": "which corpus the class was found in; the STRENGTH "
                           "of the claim (classified window vs. search "
                           "witness), not the claim's content, and nothing "
                           "derivable from columns can confirm or refute it",
                "strongest_claim": "the sentence spelling out the strongest "
                                   "regime above; as regime",
                "discovery": "whether a classification catalogue already had "
                             "the class; provenance, and checked against the "
                             "regimes by master_catalog/tests instead",
                "citations": "which papers credit the class: a curation "
                             "decision nothing derivable from columns can "
                             "confirm or refute; that every key resolves "
                             "against the header is a FILE-level check "
                             "(verify_catalog.citation_problems), and the "
                             "crediting rules are pinned by master_catalog/tests",
                "sources": "where the circuit came from -- inert history, not "
                           "paths: nothing in the folder opens one, and a row "
                           "is true or false on its columns alone",
                "relabelled_into_canonical_frame": "whether the columns were "
                    "MOVED into the canonical output frame on the way in. That "
                    "is a fact about the row's history, not about the circuit: "
                    "the frame itself IS checked (sk_canonical_frame, below, "
                    "is re-derived and rejected when wrong), and no reading of "
                    "the stored columns can say what labelling they arrived "
                    "in. It is recorded so a reader comparing this row with "
                    "its source knows why the columns differ",
            },
        )
        counts = sweep(self, boundary)
        self.assertGreater(counts["rejected"], 30, counts)

    def test_understating_a_distance_is_allowed_of_a_COHERENT_row(self):
        """The one direction the catalogue permits -- and why it is not benign.

        A row may publish `d >= 3` for a circuit whose distance is 4: what it
        claims is true, and the failure this catalogue exists to prevent is the
        other direction.  So the sweep above rejecting `d_is_exact = false` is
        not that rule being broken.  It is the difference between a coherent
        floor and a one-field edit: flipping only the flag leaves `d_upper`
        equal to `d`, and a harmful fault AT the floor is exactly what makes a
        distance exact, so the edited row contradicts itself.  Demoting the row
        coherently -- flag, upper bound and witness together -- is accepted,
        which is asserted here so the rule is pinned somewhere rather than
        merely permitted by an omission.
        """
        floor = copy.deepcopy(self.baseline)
        floor["d_is_exact"] = False
        floor["d_upper"] = None
        floor["d_witness"] = None
        self.assertEqual(self._validate(floor), [],
                         "a row that honestly says only 'nothing lighter than "
                         "d is harmful' must be accepted")
        self.assertTrue(self._validate({**floor, "d": self.baseline["d"] + 1}),
                        "but a floor RAISED above the proved sweep must not be")

    def test_the_metrics_are_checked_in_both_directions(self):
        """Null is not a way out: an omitted metric is rejected too.

        `t_count` and `poly_degree` are exactly recomputable at this width, so
        a row may not decline to publish them -- `None` where the
        recomputation succeeds is a missing fact, not a modest one, and it is
        the mutation a reader would never notice.
        """
        for field_name in ("t_count", "poly_degree"):
            for value in (None, 0, 1, 99, -1):
                row = dict(self.baseline)
                if row[field_name] == value:
                    continue
                row[field_name] = value
                with self.subTest(field=field_name, value=value):
                    self.assertTrue(self._validate(row),
                                    f"a wrong {field_name} must be rejected")


class TestMasterCatalogueFilter(unittest.TestCase):
    """The scope filter itself: level 3 and d >= 3, nothing else.

    The two halves are applied in different places, on purpose.  LEVEL is the
    rotation angle of the injected states, which no reading of the columns
    recovers: it can only be DECLARED, so it is checked as a declaration --
    `verify_catalog.verify_row` requires the row to say 3 and nothing else.
    DISTANCE is derivable, so it is never taken from a claim at all:
    `merge_results` MEASURES it from the columns and applies the filter to the
    measurement, which is what stops a circuit that claims 5 and is 2 from
    being sorted on a number nobody checked.
    """

    @classmethod
    def setUpClass(cls):
        cls.verifier = _module("master_catalog", "verify_catalog")
        cls.merger = _module("master_catalog", "merge_results")
        cls.payload = json.loads(
            (ROOT / "master_catalog" / "master_catalog.json").read_text(
                encoding="utf-8"))
        cls.narrow = min((row for row in cls.payload["factories"]
                          if row["k"] == 1),
                         key=lambda row: (row["n"], row["N"]))

    def test_the_level_filter_is_applied_to_the_declaration(self):
        for level in (1, 2, 4, None, "3"):
            row = copy.deepcopy(self.narrow)
            row["level"] = level
            with self.subTest(level=level):
                _facts, problems = self.verifier.verify_row(row)
                self.assertTrue(problems, f"level={level!r} must be rejected")

    def _record(self, columns):
        """The smallest k=1 row, re-offered to the merger as a new result."""
        return {"k": 1, "N": self.narrow["N"], "columns": columns}

    def test_the_distance_filter_rejects_a_distance_two_circuit(self):
        """Applied to the MEASURED distance, not to the claimed one.

        The witness is a repeated column: it makes the circuit distance 2
        whatever any field says -- the two columns XOR to zero, an undetectable
        fault of weight 2 -- so a record carrying one has to be rejected on the
        distance even when it claims a larger one.
        """
        record = self._record(list(self.narrow["columns"])
                              + [self.narrow["columns"][0]])
        record["d"] = 5
        _row, problems = self.merger.candidate_row(
            record, copy.deepcopy(self.payload), "test", 0)
        self.assertTrue(problems, "a repeated column must be rejected")
        self.assertTrue(any("column" in kind or "column" in detail
                            for kind, detail in problems), problems)

    def test_an_honest_record_for_a_row_already_here_is_a_duplicate(self):
        """The baseline of the two rejections above: it really is acceptable.

        Without this the tests above prove nothing -- a `candidate_row` that
        rejected everything would pass them both.
        """
        payload = copy.deepcopy(self.payload)
        record = self._record([list(c) for c in self.narrow["columns"]])
        row, problems = self.merger.candidate_row(record, payload, "test", 0)
        self.assertEqual(problems, [], "the shipped row must re-verify")
        self.assertIsNotNone(self.merger.find_class(payload["factories"], row),
                             "and must be recognised as a class already held")


# ================================================== symmetry group records
class TestSymmetryGroupFile(unittest.TestCase):
    """Whether a stored group file may be used to certify Aut(F).

    `rebuild_from_groups` reconstructs each circuit from the stored generators.
    That check is only meaningful if the groups are the COMPLETE automorphism
    groups: with every group truncated to the identity, each orbit is a
    singleton and every row rebuilds trivially.
    """

    @classmethod
    def setUpClass(cls):
        cls.rebuild = _module("symmetry_sat_search", "rebuild_from_groups")
        groups_path = ROOT / "symmetry_sat_search" / "catalog" / "symmetry_groups.json"
        catalog_path = ROOT / "symmetry_sat_search" / "catalog" / "factories.json"
        if not groups_path.exists():
            raise unittest.SkipTest("run symmetry_groups.py first")
        groups = json.loads(groups_path.read_text(encoding="utf-8"))
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))["factories"]
        # Two rows: the boundary is per-row, and rebuilding all 57 for every
        # mutation would trade minutes of runtime for no extra coverage.
        keep = 2
        cls.catalog = catalog[:keep]
        cls.baseline = {**groups, "n_factories": keep,
                        "factories": groups["factories"][:keep]}

    def _validate(self, groups):
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()) as printed:
            code = self.rebuild.main(groups=groups, catalog=self.catalog)
        return [printed.getvalue().strip()] if code else []

    def test_a_group_file_may_not_understate_its_own_groups(self):
        boundary = Boundary(
            name="symmetry group file",
            claim="Accepting it publishes each `order` as |Aut(F)| and each "
                  "generating set as generating that whole group.",
            baseline=self.baseline,
            validate=self._validate,
            skip=("factories[0].column_orbits", "factories[0].group.generators",
                  "factories[0].group.generator_cycle_types"),
            benign={
                "description": "a human-readable summary",
                "group_definition": "prose stating the definition the code "
                                    "implements",
                "all_regenerate": "recomputed here from the columns, not read",
                "group_cap": "the cap a run used; what matters is whether any "
                             "group HIT it, which is each group's `complete`",
                "factories[0].source": "provenance",
                "factories[0].output_gate": "re-derived from the rebuilt "
                                            "columns by check()",
                "factories[0].label": "the display name",
                "factories[0].regenerates_factory": "the producer's own report "
                    "of the property; check() recomputes it here from the "
                    "generators and the catalogued columns",
                "factories[0].compression": "a reported ratio, recomputed by "
                                            "check() from the orbits",
                "factories[0].n_orbits": "as compression",
                "factories[0].group.description": "prose",
                "factories[0].group.order": "recomputed from the generators by "
                                            "check(); the stored value is not "
                                            "trusted",
                "factories[0].group.generator_cycle_types":
                    "a readable fingerprint of the generators, which are "
                    "themselves re-applied by check()",
            },
            tolerates=self._tolerates,
        )
        counts = sweep(self, boundary)
        self.assertGreater(counts["rejected"], 20, counts)

    def _tolerates(self, path, value):
        """Redundant descriptions of the same group are still true ones.

        Listing a generator twice, or an orbit representative twice, describes
        the same group and the same column set: `regenerate` closes the
        representatives under the generated group either way, so the order and
        the columns come out identical.  A generator that changes the group is
        still rejected, because the regenerated order and columns then differ
        from the catalogue's.
        """
        if path in ("factories[0].group.generators",
                    "factories[0].column_orbits"):
            original = get_path(self.baseline, path)
            return value == original + original
        return False


# ================================================== row-space shard coverage
class TestShardCoverage(unittest.TestCase):
    """Whether a set of row-space shards covers the documented sweep.

    Synthesised, unlike the other baselines: shard files are gitignored and
    regenerated on a cluster, so there is no shipped set to work from. The shapes
    come from `cmd_task`'s own writer.
    """

    @classmethod
    def setUpClass(cls):
        cls.rowspace = _module("classification/legacy/exhaustive_n38", "classify_rowspace")
        tasks = cls.rowspace.manifest_tasks(sorted(cls.rowspace.ROWSPACE_NS), 8)
        cls.tasks = tasks
        cls.baseline = {
            "shards": [
                {"n": n, "chunk": c, "nchunks": nc, "kmax": 2, "budget": 0,
                 "supports": 1, "nodes": 0, "partial_class_indices": [],
                 "distinct_factories": 0, "factories": [],
                 "elapsed_seconds": 0.0}
                for n, c, nc in tasks
            ]
        }

    def _validate(self, artifact):
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as tmp:
            shards = Path(tmp) / "shards"
            shards.mkdir()
            for shard in artifact["shards"]:
                name = (f"shard_n{shard.get('n')}_c{shard.get('chunk')}"
                        f"of{shard.get('nchunks')}_k{shard.get('kmax')}.json")
                (shards / name).write_text(json.dumps(shard), encoding="utf-8")
            original_shards, original_results = (self.rowspace.SHARDS,
                                                 self.rowspace.RESULTS)
            self.rowspace.SHARDS, self.rowspace.RESULTS = shards, Path(tmp)
            try:
                with contextlib.redirect_stdout(io.StringIO()) as printed:
                    code = self.rowspace.cmd_merge(None)
            finally:
                self.rowspace.SHARDS = original_shards
                self.rowspace.RESULTS = original_results
        return [printed.getvalue().strip()] if code else []

    def test_the_shard_set_must_match_the_manifest(self):
        boundary = Boundary(
            name="row-space shard set",
            claim="Accepting it describes the merged file as the whole n<=38 "
                  "row-space sweep.",
            baseline=self.baseline,
            validate=self._validate,
            skip=("shards[0].factories",),
            benign={
                "shards[0].supports": "a count of what one shard visited; "
                                      "coverage is decided by the (n, chunk) "
                                      "task set",
                "shards[0].nodes": "a cost counter",
                "shards[0].elapsed_seconds": "a cost counter",
                "shards[0].budget": "a budget being set is not a budget being "
                                    "hit; partial_class_indices records that",
                "shards[0].distinct_factories": "a count of rows that are each "
                                                "re-derived on merge",
                "shards[0].factories": "as distinct_factories",
            },
            # Nothing is tolerated here: every field the merge reads is either
            # the shard's identity in the task set or its truncation report, and
            # `partial_class_indices` is required to be a list precisely because
            # `0`, `False` and `""` are not honest ways to say "none".
        )
        counts = sweep(self, boundary)
        self.assertGreater(counts["rejected"], 20, counts)


# ============================================== curated search-catalogue rows
class TestSearchCatalogueRow(unittest.TestCase):
    """Whether a curated example may enter the search catalogue.

    This boundary signals rejection by raising, which the harness adapts: only
    `ValueError` counts as a rejection, so a mutation that produces any other
    exception fails the sweep as a crash.
    """

    @classmethod
    def setUpClass(cls):
        cls.builder = _module("symmetry_sat_search", "build_catalog")
        payload = json.loads(cls.builder.SOURCE.read_text(encoding="utf-8"))
        rows = payload["factories"]
        # Three outputs and a degree-3 monomial keep every check live; smallest
        # such row, for the reason given in TestMasterCatalogueRow.
        wide = [r for r in rows
                if r["level"] == 3 and r["k"] == 3 and "CCZ" in r["output_gate"]]
        cls.baseline = min(wide, key=lambda r: (r["n"], r["N"]))

    def test_no_declared_parameter_may_disagree_with_the_circuit(self):
        boundary = Boundary(
            name="search catalogue row",
            claim="Accepting it publishes [[n,k,d]] and the output gate as "
                  "independently verified facts about those columns.",
            baseline=self.baseline,
            skip=("columns",),
            validate=rejects_by_raising(self.builder._verify_record, ValueError),
            benign={
                "provenance": "how the circuit was found, which no verification "
                              "depends on",
                "origin": "which campaign inside a new corpus the circuit came "
                          "from; provenance, like the field above",
                "group": "the symmetry family it was searched in; "
                         "symmetry_groups.py recomputes the actual group",
                "label": "the display name, required to be present and unique "
                         "but free-form",
                "kind": "a coarse grouping for the human catalogue",
                "target": "what was ASKED for; `output_gate` is what was found "
                          "and is re-derived from the columns",
                "note": "prose emitted by the builder itself",
                "t_count": "recomputed from the derived gate, not read",
                "poly_degree": "as t_count",
                "trivial_outputs": "recomputed; idle outputs are rejected",
                "parity_verified": "recomputed",
                "distance_verified": "recomputed",
            },
        )
        counts = sweep(self, boundary)
        self.assertGreater(counts["rejected"], 40, counts)


if __name__ == "__main__":
    unittest.main()
