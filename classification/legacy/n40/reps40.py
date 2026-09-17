#!/usr/bin/env python3
"""THE INPUT DATA -- the complete affine classification of length-40
no-repeated-column unital triorthogonal spaces, ``length40_catalogue.json``.

This module is the entire external input to the ``n = 39, 40`` classification.
Everything else in this directory is derived from it by computation, exactly
as ``../exhaustive_n38/nezami_haah_reps.py`` is the entire input to the
``n <= 38`` one.

WHY WEIGHT 40 DECIDES n = 39 AND n = 40
---------------------------------------
A reduced distance >= 3 factory with n physical injections has check columns
forming n distinct nonzero points of F_2^r; adjoining the origin when n is odd
gives a set W of even size c = n + (n mod 2) whose indicator lies in
RM(r-4, r), i.e. the augmented check space (check rows plus the all-ones row)
is a unital triorthogonal space of length c with no repeated column
(``../exhaustive_n38/docs/THEORY_EXHAUSTIVENESS.md``, section 4).  The
Kasami-Tokura / Nezami-Haah tables classify every such space of weight < 40
and close ``n <= 38``.  ``length40_catalogue.json`` classifies weight exactly
40, so it decides the two remaining T-counts below 41:

    weight 40 -> covers n = 39 (origin on the support) and n = 40 (origin off it)

REPRESENTATIVE FORMAT
---------------------
Each of the 110 records carries its support as a list of length-m bit strings
over F_2^m ("x_1 .. x_m left to right"), plus the generator matrix
(rows 1, x_1, ..., x_m restricted to the support), the indicator polynomial and
the provenance of its classification.  Only the support set is used here; it is
turned into integers with x_j -> bit j-1, the convention of
``../exhaustive_n38/marking.py``.  Bit order is a global GL(m,2) coordinate
choice and cannot affect the classification, since every origin is marked and
the engine keys on the gate.

WHAT IS CHECKED BEFORE THE TABLE IS TRUSTED (``validate``, run by
``tests/test_n40.py`` and at use time by ``classify40.py``)
  1. the file's own status: classification complete, no intrinsic dimension
     left, no provisional representative;
  2. 110 representatives with distinct ids, 1/18/46/32/12/1 at
     m = 6/7/8/9/10/11, matching the file's ``decomposition_classification``;
  3. every support has exactly 40 distinct points and affine rank m (it is
     given in its intrinsic affine span, as the marking argument assumes);
  4. every augmented space is unital triorthogonal: all pairwise and triple
     overlaps of the rows {1, x_1, ..., x_m} restricted to the support are
     even, i.e. the indicator lies in RM(m-4, m).
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter, namedtuple
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE / "length40_catalogue.json"
#: Digest of the table this directory was built from.  A different file is
#: not refused (the format may be re-exported), but the digest of what was
#: actually read is written into every result and catalogue file.
EXPECTED_SHA256 = "8f942ad1645b15e5abc28f43196d3d04c4476f96dc9792d7edf3cf4d03055eed"
WEIGHT = 40
EXPECTED_COUNT = 110
EXPECTED_BY_M = {6: 1, 7: 18, 8: 46, 9: 32, 10: 12, 11: 1}
#: The two T-counts this table decides.
VALID_NS = (39, 40)

Rep = namedtuple("Rep", "id m support indicator")


def sha256_of(path=CATALOGUE) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def support_ints(bitstrings) -> frozenset:
    """Bit strings 'x_1..x_m' -> ints with x_j at bit j-1."""
    out = set()
    for s in bitstrings:
        v = 0
        for j, ch in enumerate(s):
            if ch == "1":
                v |= 1 << j
            elif ch != "0":
                raise ValueError(f"not a bit string: {s!r}")
        out.add(v)
    return frozenset(out)


def load(path=CATALOGUE) -> list[Rep]:
    """The 110 representatives, in file order."""
    blob = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Rep(rec["id"], int(rec["m"]), support_ints(rec["support"]),
                rec.get("indicator_polynomial")) for rec in blob["representatives"]]


def affine_rank(points) -> int:
    pts = list(points)
    base = pts[0]
    basis = []
    for p in pts[1:]:
        v = p ^ base
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return len(basis)


def is_unital_triorthogonal(m, support) -> bool:
    """All pair and triple overlaps of the rows {1, x_1..x_m}|S are even
    (the all-ones row makes single-row weights a pair with itself)."""
    pts = sorted(support)
    rows = [(1 << len(pts)) - 1]
    rows += [sum(1 << i for i, p in enumerate(pts) if (p >> b) & 1) for b in range(m)]
    for a in range(len(rows)):
        for b in range(a, len(rows)):
            if (rows[a] & rows[b]).bit_count() & 1:
                return False
            for c in range(b, len(rows)):
                if (rows[a] & rows[b] & rows[c]).bit_count() & 1:
                    return False
    return True


def validate(path=CATALOGUE) -> list[str]:
    """Everything that must hold before the table is used; [] if it all does."""
    problems = []
    blob = json.loads(Path(path).read_text(encoding="utf-8"))
    if blob.get("status") != "complete":
        problems.append(f"status={blob.get('status')!r}, not 'complete'")
    if blob.get("remaining_intrinsic_dimensions"):
        problems.append(f"remaining_intrinsic_dimensions={blob['remaining_intrinsic_dimensions']}")
    if blob.get("provisional_representatives"):
        problems.append(f"{len(blob['provisional_representatives'])} provisional representatives")
    if blob.get("in_progress_branches"):
        problems.append(f"{len(blob['in_progress_branches'])} branches in progress")
    scope = blob.get("classification_scope", "")
    if "length exactly 40" not in scope or "unital triorthogonal" not in scope:
        problems.append(f"classification_scope={scope!r} is not the length-40 unital triorthogonal one")
    dc = blob.get("decomposition_classification", {})
    if dc.get("representative_count") != EXPECTED_COUNT:
        problems.append(f"decomposition_classification.representative_count={dc.get('representative_count')}")
    reps = load(path)
    if len(reps) != EXPECTED_COUNT:
        problems.append(f"{len(reps)} representatives, expected {EXPECTED_COUNT}")
    ids = Counter(r.id for r in reps)
    if any(v > 1 for v in ids.values()):
        problems.append(f"repeated ids: {[i for i, v in ids.items() if v > 1]}")
    by_m = Counter(r.m for r in reps)
    if dict(by_m) != EXPECTED_BY_M:
        problems.append(f"per-m counts {dict(sorted(by_m.items()))} != {EXPECTED_BY_M}")
    for r in reps:
        if len(r.support) != WEIGHT:
            problems.append(f"{r.id}: {len(r.support)} distinct support points, not {WEIGHT}")
            continue
        if max(r.support) >= (1 << r.m):
            problems.append(f"{r.id}: a support point does not fit in F_2^{r.m}")
            continue
        if affine_rank(r.support) != r.m:
            problems.append(f"{r.id}: affine rank {affine_rank(r.support)} != m = {r.m}")
        if not is_unital_triorthogonal(r.m, r.support):
            problems.append(f"{r.id}: rows 1, x_1..x_{r.m} on the support are not triorthogonal")
    return problems


if __name__ == "__main__":
    probs = validate()
    reps = load()
    print(f"{CATALOGUE.name}: sha256 {sha256_of()}"
          + ("" if sha256_of() == EXPECTED_SHA256 else "  (NOT the digest this directory was built from)"))
    print(f"{len(reps)} representatives; by m: {dict(sorted(Counter(r.m for r in reps).items()))}")
    for p in probs:
        print("PROBLEM:", p)
    print("input table:", "OK" if not probs else f"{len(probs)} problem(s)")
    raise SystemExit(1 if probs else 0)
