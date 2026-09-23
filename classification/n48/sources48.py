#!/usr/bin/env python3
"""The families of check parents the n = 41 .. 48 sweep runs over.

A *source* is a list of representatives; each representative is an affine
class of even-weight point set S in F_2^m and stands for its 2^m + 1 marked
geometries (``../n40/marking40.marked_geometries``, imported unchanged):

    origin on S      -> n = |S| - 1, check rank m      (|S| of these)
    origin off S     -> n = |S|,     check rank m      (2^m - |S|)
    hyperplane miss  -> n = |S|,     check rank m + 1  (1, the "lift")

Unlike ``../n40/sources.py`` a source here does not materialise its
geometries: the length-48 table alone has 15.6 million markings, so a
representative carries (m, support) and the workers mark it themselves,
origin chunk by origin chunk (``marking_of``; ``tests/test_n48.py`` checks it
against ``marked_geometries`` marking for marking).

  ``length42``  the 86 length-42 representatives, every marking:   n = 41, 42
  ``length44``  the 508 length-44 representatives of intrinsic dimension
                m >= 8, every marking:  n = 43, 44 at check rank >= 8
  ``length46``  the 1015 length-46 representatives, every marking: n = 45, 46
  ``length48``  the 28,776 length-48 representatives of intrinsic dimension
                m >= 8, every marking:  n = 47, 48 at check rank >= 8.
  ``rm37_w44``  the 35 affine-rank-7 weight-44 classes of RM(3,7) at one origin
                per stabiliser orbit (n = 43, 44 at check rank 7) plus the rank-8
                lift of each -- the rank-7 sector at n = 43, 44 and the rank-8
                lifts of the length-44 table's m = 7 sector (which the RM(3,7)
                table matches class for class, ``reps48.rm37_crosscheck``).
                Sweeping the 35 classes at all 128 origins would cost ~10x
                more for the same classes and the same coefficients.
  ``rm37_w48``  the 98 affine-rank-7 weight-48 classes of RM(3,7), from the
                Gillot-Langevin table behind ``../rank7_census`` (imported
                unchanged), at one origin per stabiliser orbit of origins
                (n = 47, 48 at check rank 7) plus the rank-8 lift of each:
                the ENTIRE rank-7 sector at n = 47, 48, and the rank-8 lifts
                of the length-48 table's m = 7 sector.  This replaces the
                table's m = 7 sector, which is missing two classes
                (``reps48.rm37_crosscheck``, ``docs/INPUT_DEFECT_M7.md``).
                Origins in one stabiliser orbit give the same code up to a
                change of check basis, which moves no frame, no gate and no
                fault set, so one origin per orbit sees every class and every
                coefficient the class has.  (The rank-8 lift does not depend
                on the origin at all.)
  ``open_rank6``  the single m = 6 length-48 representative (RM(3,7) class
                3470, a+abc, the weight-48 word of affine rank 6): 2 stabiliser
                orbits of origins at rank 6 plus the rank-7 lift.  Its parents
                have kappa = 20, 21 and mu <= 15 and are NOT swept: the
                brute-force engine cannot enumerate them (``docs/OPEN_RANK6.md``).
                Listed so the catalogue can state exactly what is open.

Coverage of a run is proved from these lists (every representative id, every
one of its 2^m + 1 origins), never from the run's own files.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for p in (HERE, HERE.parent / "n40", HERE.parent / "rank7_census"):
    sys.path.insert(0, str(p))

import reps48                                        # noqa: E402
from marking40 import marked_geometries              # noqa: E402  (n40's marking, unchanged)

SOURCES = ("length42", "length44", "length46", "length48", "rm37_w44", "rm37_w48", "open_rank6")
LENGTH_OF = {"length42": 42, "length44": 44, "length46": 46, "length48": 48}


class Rep:
    """One affine class and the list of origins its geometries come from.

    ``origins`` is a list of ints (points of F_2^m) and/or the string
    ``"lift"``; ``marking_of(m, support, origin)`` turns each into a
    geometry.  For the table sources it is every point of F_2^m plus the
    lift; for the RM(3,7) sources one point per stabiliser orbit plus the
    lift.
    """
    __slots__ = ("id", "m", "support", "origins", "note", "n_geometries")

    def __init__(self, id, m, support, origins, note=""):
        self.id, self.m, self.support, self.note = id, m, frozenset(support), note
        self.origins = list(origins)
        self.n_geometries = len(self.origins)


def marking_of(m, S, origin):
    """``(n, ambient_rank, points)`` of one marking; the same geometry, point
    for point, that ``marked_geometries(m, S)`` yields for this origin."""
    if origin == "lift":
        return len(S), m + 1, tuple(sorted(p | (1 << m) for p in S))
    if origin in S:
        return len(S) - 1, m, tuple(sorted(p ^ origin for p in S if p != origin))
    return len(S), m, tuple(sorted(p ^ origin for p in S))


def all_origins(m):
    return list(range(1 << m)) + ["lift"]


def _table_source(length, min_m=0):
    for rep in reps48.load(length):
        if rep.m >= min_m:
            yield Rep(rep.id, rep.m, rep.support, all_origins(rep.m), rep.indicator or "")


def _span_coordinates(S):
    """Coordinates in a basis of the affine span of S (base point min S):
    returns ``(rank, coord)`` with ``coord(p)`` the int coordinates of a span
    point p, so that {coord(p) : p in S} is S inside its own F_2^rank."""
    pts = sorted(S)
    base = pts[0]
    basis = []
    for p in pts[1:]:
        v = p ^ base
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    basis.sort(reverse=True)                  # echelon: leading bits distinct, reduce greedily

    def coord(p):
        v, c = p ^ base, 0
        for i, b in enumerate(basis):
            if v ^ b < v:
                v ^= b
                c |= 1 << i
        if v:
            raise ValueError("point outside the affine span")
        return c
    return len(basis), coord


def _rm37_source(weight, rank):
    """RM(3,7) classes of this weight and affine rank, each expressed inside
    its own affine span F_2^rank, at one origin per stabiliser orbit of
    origins (the census's ``origin_orbits``, restricted to the span -- the
    stabiliser of a word fixes its span), plus the lift."""
    from gillot_langevin import parse_file, origin_orbits   # noqa: E402  the census's parser, unchanged
    from rank7 import DEFAULT_DATA                          # noqa: E402
    for orbit in parse_file(DEFAULT_DATA, 7):
        if orbit.weight != weight:
            continue
        S = frozenset(p for p in range(128) if (orbit.table >> p) & 1)
        m, coord = _span_coordinates(S)
        if m != rank:
            continue
        origins = set()
        for group in origin_orbits(orbit):
            in_span = []
            for p in group:
                try:
                    in_span.append(coord(p))
                except ValueError:
                    pass
            if in_span:
                origins.add(min(in_span))
        yield Rep(f"rm37_class_{orbit.index}", m, {coord(p) for p in S}, sorted(origins) + ["lift"],
                  f"RM(3,7) affine orbit class {orbit.index}: {orbit.anf}; stabiliser order {orbit.stabilizer}; "
                  f"one origin per stabiliser orbit of origins")


def length42(): return _table_source(42)
def length44(): return _table_source(44, min_m=8)
def length46(): return _table_source(46)
def length48(): return _table_source(48, min_m=8)
def rm37_w44(): return _rm37_source(44, 7)
def rm37_w48(): return _rm37_source(48, 7)


def open_rank6(): return _rm37_source(48, 6)


def reps_of(source):
    if source not in SOURCES:
        raise ValueError(f"unknown source {source!r}; one of {SOURCES}")
    fn = {"length42": length42, "length44": length44, "length46": length46, "length48": length48,
          "rm37_w44": rm37_w44, "rm37_w48": rm37_w48, "open_rank6": open_rank6}[source]
    reps = list(fn())
    if source in ORDER_BY_KAPPA:
        k0 = kappa_at_origin0(source, reps)
        reps.sort(key=lambda r: (k0[r.id], r.m, r.id))
    else:
        reps.sort(key=lambda r: (r.m, r.id))
    return reps


# The cost of a parent grows ~2-3x per unit of kappa = dim V_3(C) (measured:
# ~1 ms at kappa <= 4, ~0.1 s at 7-8, seconds at 10, minutes to hours at 12+).
# The length-48 table has a heavy tail (59 reps with kappa >= 11 at origin 0,
# 11 with kappa >= 13), so that source is swept in increasing kappa: the cheap
# 99 % lands first and the tail is a well-defined trailing set of shards that
# can be run elsewhere or reported as pending.  kappa is taken at origin 0 as
# an ordering key only (it varies by +-1 with the origin); it is deterministic,
# so classify48 and build_catalog48 recompute the same shard plan.
ORDER_BY_KAPPA = {"length48"}


def kappa_at_origin0(source, reps):
    """{rep_id: kappa of the origin-0 marking}, cached in results/<source>_kappa0.json."""
    import json
    cache = HERE / "results" / f"{source}_kappa0.json"
    if cache.exists():
        k0 = json.load(open(cache))
        if set(k0) == {r.id for r in reps}:
            return k0
    sys.path.insert(0, str(HERE.parent / "n40"))
    from landscape import Parent                     # noqa: E402  n40's, unchanged
    k0 = {}
    for r in reps:
        n, rank, pts = marking_of(r.m, r.support, 0)
        k0[r.id] = Parent.from_points(pts, rank, 3, 64).kappa
    cache.parent.mkdir(exist_ok=True)
    json.dump(k0, open(cache, "w"), indent=0, sort_keys=True)
    return k0


def expected_geometries(source):
    """{rep_id: n_geometries}, recomputed from the inputs, for coverage proofs."""
    return {rep.id: rep.n_geometries for rep in reps_of(source)}


def input_digest(source):
    """Digest of the source's input table, written into every result file."""
    if source in LENGTH_OF:
        return reps48.sha256_of(LENGTH_OF[source])
    from rank7 import DEFAULT_DATA, data_digest   # noqa: E402
    return data_digest(DEFAULT_DATA)


def n_of(source):
    """The injection counts a source decides."""
    L = LENGTH_OF.get(source) or int(source[-2:])
    return (L - 1, L)


if __name__ == "__main__":
    for s in SOURCES:
        reps = reps_of(s)
        from collections import Counter
        by_m = Counter(r.m for r in reps)
        print(f"{s:10s} {len(reps):6d} reps, {sum(r.n_geometries for r in reps):10d} geometries, "
              f"by m {dict(sorted(by_m.items()))}, sha256 {input_digest(s)[:12]}..")
