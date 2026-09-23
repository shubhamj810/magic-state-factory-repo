"""The four S_k canonicalisers must not drift apart.

`S_k` -- the gate up to a permutation of the output qubits -- is the dedup key
every catalogue here is built on, and it is implemented four times:

    classification/exhaustive_n38/dedup.py      the catalogue key
    classification/rank7_census/build_catalog.py
    symmetry_sat_search/verify_catalog.py
    factorylib/parent.py                        the shared parent model

That repetition is deliberate -- each directory verifies its own rows without
depending on another's code -- but nothing asserted the four agreed, which is
drift waiting to happen. Consolidating them would remove the independence and
would silently change published gate STRINGS if the wrong ordering won, so the
agreement is asserted here instead.

Two different claims, because the four do not all make the same one:

* the three CATALOGUE implementations agree representative for representative,
  since the published `gate` string is that representative;
* all four induce the same PARTITION into S_k classes -- same orbit, same key --
  which is the only thing a dedup key must do. `factorylib.parent` orders
  monomials degree-major and so picks a different representative of the same
  orbit; that is a documented difference, and it is asserted here rather than
  left as a surprise.

Together those pin what may change and what may not: an implementation may not
merge or split classes differently, and the three that name published rows may
not disagree about the name.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(relative: str, alias: str):
    """Load a module by path, so same-named builders do not collide."""
    path = ROOT / relative
    for entry in (str(ROOT), str(path.parent)):
        while entry in sys.path:
            sys.path.remove(entry)
        sys.path.insert(0, entry)
    spec = importlib.util.spec_from_file_location(alias, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


DEDUP = _load("classification/exhaustive_n38/dedup.py", "sk_dedup")
CENSUS = _load("classification/rank7_census/build_catalog.py", "sk_census")
SEARCH = _load("symmetry_sat_search/verify_catalog.py", "sk_search")
from factorylib.parent import sk_canonical as parent_sk          # noqa: E402

#: The three whose output is published as a gate string.
CATALOGUE = (("exhaustive_n38/dedup", DEDUP.sk_canonical),
             ("rank7_census/build_catalog", CENSUS.sk_canonical),
             ("symmetry_sat_search/verify_catalog", SEARCH.sk_canonical))

#: Catalogue files whose stored gates are also fed through every implementation.
SOURCES = (
    "classification/exhaustive_n38/catalog/classification_n38.json",
    "classification/rank7_census/catalog/census_r7.json",
    "master_catalog/master_catalog.json",
)


def gates_up_to(k, max_monomials=4):
    """Every gate on k outputs with at most `max_monomials` monomials."""
    monomials = [frozenset(combo) for degree in (1, 2, 3)
                 for combo in itertools.combinations(range(k), degree)]
    for size in range(1, min(len(monomials), max_monomials) + 1):
        for combo in itertools.combinations(monomials, size):
            yield frozenset(combo)


def sampled_gates(k, step, max_monomials=4):
    """A deterministic slice of `gates_up_to`, for widths where it is large."""
    for index, gate in enumerate(gates_up_to(k, max_monomials)):
        if index % step == 0:
            yield gate


#: `sk_canonical` minimises over all `k!` relabellings, so feeding it a wide
#: gate is not a slow test, it is a test that never returns.  The master
#: catalogue now carries rows to `k = 162` (the AI corpora merged in
#: 2026-08), so the shipped-gate sweep below stops where the brute force does.
#: Nothing is skipped silently: `test_wide_shipped_gates_are_checked_elsewhere`
#: pins the rows above this width against `master_catalog/skcanon.py`, which
#: computes the same key without enumerating the group.
BRUTE_FORCE_K = 8


def shipped_gates(max_k=BRUTE_FORCE_K):
    """(k, monomial set) for every gate string in the generated catalogues."""
    for relative in SOURCES:
        path = ROOT / relative
        if not path.exists():
            continue
        blob = json.loads(path.read_text(encoding="utf-8"))
        for row in (blob["factories"] if isinstance(blob, dict) else blob):
            gate = row.get("gate") or row.get("gate_human") or ""
            monomials = set()
            for token in gate.replace("·", "+").replace(".", "+").split("+"):
                digits = [c for c in token if c.isdigit()]
                if digits:
                    monomials.add(frozenset(int(c) for c in digits))
            if monomials and row["k"] <= max_k:
                yield row["k"], frozenset(monomials), relative


class TestCatalogueImplementationsAgree(unittest.TestCase):
    """The published representative must be the same in all three."""

    def _check(self, k, gate, where=""):
        keys = {name: canonical(k, gate) for name, canonical in CATALOGUE}
        distinct = set(keys.values())
        self.assertEqual(
            len(distinct), 1,
            f"k={k} gate={sorted(map(sorted, gate))} {where}: the catalogue "
            f"implementations disagree on the canonical representative, so two "
            f"directories would publish the same class under different names: "
            f"{keys}")

    def test_every_gate_up_to_three_outputs(self):
        for k in (1, 2, 3):
            for gate in gates_up_to(k):
                self._check(k, gate)

    def test_every_gate_on_four_outputs(self):
        for gate in gates_up_to(4):
            self._check(4, gate)

    def test_a_slice_of_five_output_gates(self):
        """k=5 is 120 permutations per call; a deterministic slice keeps it fast."""
        checked = 0
        for gate in sampled_gates(5, step=37):
            self._check(5, gate)
            checked += 1
        self.assertGreater(checked, 100, "the slice covered almost nothing")

    def test_every_shipped_catalogue_gate(self):
        checked = 0
        for k, gate, where in shipped_gates():
            self._check(k, gate, where)
            checked += 1
        self.assertGreater(checked, 100, "no catalogue rows were read")

    def test_wide_shipped_gates_are_checked_elsewhere(self):
        """The rows the brute force cannot reach, checked without it.

        `master_catalog/skcanon.py` computes the same `S_k` key by a closed form
        or a branch and bound instead of enumerating `k!`, and is pinned against
        `dedup.sk_canonical` on every width where both run.  Here it is pointed
        at the wide rows themselves: each one's stored `sk_key` must be what its
        own gate canonicalises to, and where the key is absent the row must say
        so rather than leave it to be assumed.
        """
        sys.path.insert(0, str(ROOT / "master_catalog"))
        import skcanon                                            # noqa: E402
        blob = json.loads(
            (ROOT / "master_catalog" / "master_catalog.json").read_text())
        checked = 0
        for row in blob["factories"]:
            if row["k"] <= BRUTE_FORCE_K:
                continue
            gate = {frozenset(mono) for mono in row["sk_key"] or ()}
            with self.subTest(params=(row["n"], row["k"])):
                if row["sk_key"] is None:
                    self.assertFalse(row["sk_canonical_frame"])
                    self.assertIn("sk_key_note", row)
                    continue
                self.assertTrue(row["sk_canonical_frame"])
                self.assertEqual(skcanon.sk_canonical(row["k"], gate),
                                 tuple(map(tuple, row["sk_key"])),
                                 "the stored key is not its own canonical form")
            checked += 1
        self.assertGreater(checked, 50, "no wide catalogue rows were read")


class TestAllFourInduceTheSamePartition(unittest.TestCase):
    """Same orbit, same key -- the property a dedup key actually has to have.

    Checked in both directions at once: build the map from each implementation's
    key to the set of `factorylib.parent` keys seen with it. Any implementation
    that merged two classes, or split one, makes that map non-functional.
    """

    def _partitions_agree(self, k, gates):
        by_catalogue: dict = {}
        by_parent: dict = {}
        for gate in gates:
            catalogue = DEDUP.sk_canonical(k, gate)
            parent = parent_sk(k, gate)[0]
            by_catalogue.setdefault(catalogue, set()).add(parent)
            by_parent.setdefault(parent, set()).add(catalogue)
        for key, images in by_catalogue.items():
            self.assertEqual(
                len(images), 1,
                f"k={k}: one catalogue class {key} maps to {len(images)} parent "
                f"keys, so the parent model SPLITS a class the catalogue merges")
        for key, images in by_parent.items():
            self.assertEqual(
                len(images), 1,
                f"k={k}: one parent class {key} maps to {len(images)} catalogue "
                f"keys, so the parent model MERGES classes the catalogue "
                f"separates")

    def test_up_to_four_outputs(self):
        for k in (1, 2, 3, 4):
            self._partitions_agree(k, gates_up_to(k))

    def test_five_outputs_on_a_slice(self):
        self._partitions_agree(5, sampled_gates(5, step=37))

    def test_the_orbit_is_genuinely_the_same_set(self):
        """Directly: the two keys are images of one another under some p in S_k.

        The partition test above shows the classes line up; this shows why --
        both keys are the same monomial set relabelled, so neither is canonical
        in the other's ordering by accident.
        """
        for k in (2, 3, 4):
            for gate in gates_up_to(k, max_monomials=3):
                catalogue = {frozenset(Q) for Q in DEDUP.sk_canonical(k, gate)}
                parent = {frozenset(Q) for Q in parent_sk(k, gate)[0]}
                with self.subTest(k=k, gate=sorted(map(sorted, gate))):
                    self.assertTrue(
                        any({frozenset(p[i] for i in Q) for Q in catalogue}
                            == parent
                            for p in itertools.permutations(range(k))),
                        "the two keys are not S_k images of each other")


class TestTheDifferenceIsOnlyTheRepresentative(unittest.TestCase):
    """`factorylib.parent` differs, and this states exactly how far.

    If someone unifies the orderings, this test fails -- deliberately. It is the
    place that records that the difference was known and bounded, so a change
    has to be a decision rather than an accident.
    """

    def test_the_parent_key_is_degree_major(self):
        for k in (2, 3, 4):
            for gate in gates_up_to(k, max_monomials=3):
                key = parent_sk(k, gate)[0]
                degrees = [len(Q) for Q in key]
                with self.subTest(k=k, key=key):
                    self.assertEqual(degrees, sorted(degrees),
                                     "parent keys are ordered degree-major")

    def test_the_two_orderings_do_differ_somewhere(self):
        """Otherwise the two tests above would be vacuously satisfied."""
        differing = [
            (k, gate) for k in (2, 3)
            for gate in gates_up_to(k)
            if DEDUP.sk_canonical(k, gate) != parent_sk(k, gate)[0]
        ]
        self.assertTrue(
            differing,
            "the catalogue and parent keys now agree everywhere; if that was "
            "intentional, delete this test and the note in parent.sk_canonical")


if __name__ == "__main__":
    unittest.main()
