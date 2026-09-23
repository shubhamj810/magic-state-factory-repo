#!/usr/bin/env python3
"""THE INPUT DATA -- the complete affine classifications of no-repeated-column
unital triorthogonal spaces of lengths 42, 44, 46 and 48
(``length{42,44,46,48}_catalogue.json``; the length-48 file is shipped
gzipped, 136 MB raw, and is read from the ``.gz``).

This module is the entire external input of the ``n = 41 .. 48`` factory
classification, exactly as ``../n40/reps40.py`` is for ``n = 39, 40``.

WHY LENGTH 2j DECIDES n = 2j - 1 AND n = 2j
-------------------------------------------
A reduced distance >= 3 factory with n injections has check columns forming
n distinct nonzero points of F_2^r; adjoining the origin when n is odd gives
a set W of even size c = n + (n mod 2) whose indicator lies in RM(r-4, r):
the augmented check space is a unital triorthogonal space of length c with no
repeated column (``../exhaustive_n38/docs/THEORY_EXHAUSTIVENESS.md`` s.4).
So

    length 42 -> n = 41, 42      length 46 -> n = 45, 46
    length 44 -> n = 43, 44      length 48 -> n = 47, 48

and the four tables together decide every T-count from 41 to 48.

REPRESENTATIVE FORMAT
---------------------
Each record carries ``m`` (intrinsic affine dimension) and its ``support`` as
a list of length-m bit strings over F_2^m, "x_1 .. x_m left to right", plus a
generator matrix and provenance.  Only ``m`` and the support are used; the
support is turned into ints with x_j -> bit j-1 (the convention of
``../exhaustive_n38/marking.py``).

WHAT IS CHECKED BEFORE A TABLE IS TRUSTED (``validate``)
  1. the file's own status: complete, no dimension left, no provisional or
     in-progress branch;
  2. the advertised representative count, and the per-m counts this
     directory was built against (``EXPECTED_BY_M``);
  3. every support has exactly ``length`` distinct points inside F_2^m and
     affine rank m (given in its intrinsic affine span, which the marking
     argument assumes);
  4. every augmented space is unital triorthogonal: all pair and triple
     overlaps of the rows {1, x_1, .., x_m} restricted to the support are
     even.

WHAT IS CHECKED AGAINST AN INDEPENDENT SOURCE (``rm37_crosscheck``)
  The m = 7 sector of each table is exactly the set of affine-rank-7 words
  of that weight in RM(3,7), which the Gillot-Langevin orbit table behind
  ``../rank7_census`` lists completely (its class sizes sum to |AGL(7,2)| =
  2^64).  Matching the two by a three-level affine invariant (see
  ``affine_signature``) finds

      length 40: 18 = 18     length 44: 35 = 35     length 42, 46: 0 = 0
      length 48: catalogue 96, RM(3,7) 98  --  classes 2164 and 2867 MISSING

  Because of that defect the rank-7 sector at n = 47, 48 is NOT taken from
  the length-48 table but from the RM(3,7) table directly (``sources48.py``,
  source ``rm37_w48``), and the tables' completeness at m >= 8 -- which no
  independent source can check -- is recorded as the assumption it is.
  See ``docs/INPUT_DEFECT_M7.md``.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from collections import Counter, namedtuple
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
LENGTHS = (42, 44, 46, 48)
FILES = {
    42: HERE / "length42_catalogue.json",
    44: HERE / "length44_catalogue.json",
    46: HERE / "length46_catalogue.json",
    48: HERE / "length48_catalogue.json.gz",
}
#: Digests of the tables this directory was built from (of the file as
#: shipped, so of the .gz for length 48).  A different file is not refused;
#: the digest actually read is written into every result and catalogue file.
EXPECTED_SHA256 = {
    42: "36db2fd08cb345145cb9a8e57fe64a8ec04fb14a675234f1cb003e19c75ec460",
    44: "dc0c36005f127f314deabf61915030d616d4b065ac58604f06a14c66df66847e",
    46: "8b09212590d336b692ad4e5b883dc5494b61ca5566fa086a89c19d9f9ed34eaa",
    48: "f06153406d27128f89221d2c54dc53395e4e2e518e7ecbb1bf1f716a6c2213f1",
}
EXPECTED_COUNT = {42: 86, 44: 543, 46: 1015, 48: 28873}
EXPECTED_BY_M = {
    42: {8: 44, 9: 29, 10: 11, 11: 2},
    44: {7: 35, 8: 346, 9: 89, 10: 48, 11: 23, 12: 2},
    46: {8: 980, 9: 2, 10: 8, 11: 20, 12: 4, 13: 1},
    48: {6: 1, 7: 96, 8: 9868, 9: 14293, 10: 3890, 11: 633, 12: 85, 13: 6, 14: 1},
}
#: Number of RM(3,7) affine classes of full affine rank 7 at each weight, from
#: the Gillot-Langevin table (``rm37_crosscheck`` recomputes these).
RM37_RANK7_CLASSES = {40: 18, 42: 0, 44: 35, 46: 0, 48: 98}

Rep = namedtuple("Rep", "id length m support indicator")


def sha256_of(length) -> str:
    return hashlib.sha256(FILES[length].read_bytes()).hexdigest()


def read_table(length) -> dict:
    path = FILES[length]
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return json.load(f)
    return json.loads(path.read_text(encoding="utf-8"))


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


def load(length, table=None) -> list[Rep]:
    """The representatives of one table, in file order."""
    blob = table if table is not None else read_table(length)
    return [Rep(rec["id"], length, int(rec["m"]), support_ints(rec["support"]),
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
    """All pair and triple overlaps of the rows {1, x_1..x_m}|S are even."""
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


def validate(length, table=None) -> list[str]:
    """Everything that must hold before a table is used; [] if it all does."""
    problems = []
    blob = table if table is not None else read_table(length)
    status = str(blob.get("status", ""))
    if not status.startswith("complete"):
        problems.append(f"length {length}: status={status!r}, not complete")
    for key in ("remaining_intrinsic_dimensions", "remaining_affine_dimensions",
                "provisional_representatives", "in_progress_branches"):
        if blob.get(key):
            problems.append(f"length {length}: {key}={blob[key]}")
    scope = blob.get("classification_scope", "")
    if str(length) not in scope or "triorthogonal" not in scope:
        problems.append(f"length {length}: classification_scope={scope!r} is not the length-{length} "
                        f"unital triorthogonal one")
    reps = load(length, blob)
    if len(reps) != EXPECTED_COUNT[length]:
        problems.append(f"length {length}: {len(reps)} representatives, expected {EXPECTED_COUNT[length]}")
    ids = Counter(r.id for r in reps)
    if any(v > 1 for v in ids.values()):
        problems.append(f"length {length}: repeated ids {[i for i, v in ids.items() if v > 1][:5]}")
    by_m = Counter(r.m for r in reps)
    if dict(by_m) != EXPECTED_BY_M[length]:
        problems.append(f"length {length}: per-m counts {dict(sorted(by_m.items()))} != {EXPECTED_BY_M[length]}")
    for r in reps:
        if len(r.support) != length:
            problems.append(f"{r.id}: {len(r.support)} distinct support points, not {length}")
            continue
        if max(r.support) >= (1 << r.m):
            problems.append(f"{r.id}: a support point does not fit in F_2^{r.m}")
            continue
        if affine_rank(r.support) != r.m:
            problems.append(f"{r.id}: affine rank {affine_rank(r.support)} != m = {r.m}")
        if not is_unital_triorthogonal(r.m, r.support):
            problems.append(f"{r.id}: rows 1, x_1..x_{r.m} on the support are not triorthogonal")
    return problems


# --------------------------------------------------- the RM(3,7) cross-check
def affine_signature(m, S):
    """A three-level AGL(m,2) invariant of a point set S in F_2^m: the sorted
    derivative profile |S & (S+a)| over nonzero a; the sorted hyperplane
    profile min(|S & H|, |S| - |S & H|) over linear hyperplanes H; and the
    histogram of second derivatives |S & (S+a) & (S+b) & (S+a+b)| over pairs.
    Equal signatures do not prove equivalence; different ones prove
    inequivalence, which is what the cross-check needs."""
    S = frozenset(S)
    size = 1 << m
    der = sorted(len(S & {p ^ a for p in S}) for a in range(1, size))
    hyp = sorted(min(h, len(S) - h) for h in
                 (sum(1 for p in S if ((p & f).bit_count() & 1) == 0) for f in range(1, size)))
    d2 = Counter()
    for a in range(1, size):
        Sa = S & {p ^ a for p in S}
        for b in range(a + 1, size):
            d2[len(Sa & {p ^ b for p in Sa})] += 1
    return (tuple(der), tuple(hyp), tuple(sorted(d2.items())))


def rm37_rank7_classes(weight):
    """(class index, ANF, stabiliser order, support) of every affine-rank-7
    word of that weight in RM(3,7), from the census's orbit table."""
    import sys
    sys.path.insert(0, str(HERE.parent / "rank7_census"))
    from gillot_langevin import parse_file          # noqa: E402  the census's parser, unchanged
    from rank7 import DEFAULT_DATA                  # noqa: E402
    out = []
    for orbit in parse_file(DEFAULT_DATA, 7):
        if orbit.weight != weight:
            continue
        S = [p for p in range(128) if (orbit.table >> p) & 1]
        if affine_rank(S) == 7:
            out.append((orbit.index, orbit.anf, orbit.stabilizer, frozenset(S)))
    return out


def rm37_crosscheck(length, reps=None) -> dict:
    """Match the m = 7 representatives of a table against the affine-rank-7
    RM(3,7) classes of the same weight by ``affine_signature``.  Returns the
    counts and the unmatched classes on either side."""
    reps = [r for r in (reps if reps is not None else load(length)) if r.m == 7]
    table = {}
    for r in reps:
        table.setdefault(affine_signature(7, r.support), []).append(r.id)
    rm = {}
    for index, anf, stab, S in rm37_rank7_classes(length):
        rm.setdefault(affine_signature(7, S), []).append((index, anf, stab))
    missing = [c for sig, cs in rm.items() if sig not in table for c in cs]
    for sig, cs in rm.items():
        if sig in table and len(cs) > len(table[sig]):
            missing += cs[len(table[sig]):]          # more classes than reps under one signature
    foreign = [rid for sig, ids in table.items() if sig not in rm for rid in ids]
    return {
        "length": length,
        "catalogue_m7_representatives": len(reps),
        "rm37_rank7_classes": sum(len(v) for v in rm.values()),
        "distinct_signatures_catalogue": len(table),
        "distinct_signatures_rm37": len(rm),
        "rm37_classes_missing_from_catalogue": [
            {"class_index": i, "anf": a, "stabilizer_order": s} for i, a, s in sorted(missing)],
        "catalogue_representatives_not_in_rm37": sorted(foreign),
    }


if __name__ == "__main__":
    import sys
    bad = 0
    for L in LENGTHS:
        table = read_table(L)
        probs = validate(L, table)
        reps = load(L, table)
        digest = sha256_of(L)
        print(f"{FILES[L].name}: sha256 {digest}"
              + ("" if digest == EXPECTED_SHA256[L] else "  (NOT the digest this directory was built from)"))
        print(f"  {len(reps)} representatives; by m: {dict(sorted(Counter(r.m for r in reps).items()))}")
        for p in probs:
            print("  PROBLEM:", p)
        bad += len(probs)
        if "--no-crosscheck" not in sys.argv:
            cc = rm37_crosscheck(L, reps)
            print(f"  m = 7 sector vs RM(3,7): catalogue {cc['catalogue_m7_representatives']}, "
                  f"RM(3,7) rank-7 classes {cc['rm37_rank7_classes']}"
                  + (f"; MISSING from the catalogue: "
                     f"{[c['class_index'] for c in cc['rm37_classes_missing_from_catalogue']]}"
                     if cc["rm37_classes_missing_from_catalogue"] else "; identical")
                  + (f"; NOT in RM(3,7): {cc['catalogue_representatives_not_in_rm37']}"
                     if cc["catalogue_representatives_not_in_rm37"] else ""))
    print("input tables:", "OK" if not bad else f"{bad} problem(s)")
    raise SystemExit(1 if bad else 0)
