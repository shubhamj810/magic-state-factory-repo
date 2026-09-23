#!/usr/bin/env python3
"""The three families of check parents the landscape sweep runs over.

Each source yields ``(rep_id, n, origin, ambient_rank, points)`` per marked
geometry, grouped by a representative id, together with the number of
geometries each representative must contribute (so a builder can prove
coverage without believing the run files).

  ``weight40``   the 110 length-40 representatives of ``length40_catalogue.json``
                 at every marking: n = 39, 40, every check rank.  (This
                 directory's own classification.)
  ``n38``        the Kasami-Tokura / Nezami-Haah representatives of
                 ``../exhaustive_n38/nezami_haah_reps.py`` (imported unchanged)
                 at every marking: n <= 38, every check rank.  The same parents
                 the shipped n <= 38 classification enumerated.
  ``census``     the RM(3,7) affine orbits of the Gillot-Langevin table, via
                 ``../rank7_census/rank7.iter_parents`` (imported unchanged), at
                 one origin per stabiliser orbit of origins: r <= 7, n <= 44.
                 Origins in one stabiliser orbit give the same code up to a
                 change of check basis, which moves no frame, no gate and no
                 fault set, so one origin per orbit sees every class and every
                 coefficient the class has.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

from marking40 import marked_geometries              # noqa: E402

SOURCES = ("weight40", "n38", "census")


class Rep:
    __slots__ = ("id", "m", "n_geometries", "geometries", "note")

    def __init__(self, id, m, geometries, note=""):
        self.id, self.m, self.geometries, self.note = id, m, list(geometries), note
        self.n_geometries = len(self.geometries)


def weight40():
    import reps40
    for rep in reps40.load():
        yield Rep(rep.id, rep.m, marked_geometries(rep.m, rep.support), rep.indicator)


def n38():
    sys.path.insert(0, str(REPO / "classification" / "exhaustive_n38"))
    from nezami_haah_reps import BY_WEIGHT       # noqa: E402  the shipped input table, unchanged
    from marking import support_of               # noqa: E402
    for weight in sorted(BY_WEIGHT):
        for ci, (m, terms) in enumerate(BY_WEIGHT[weight]):
            S = support_of(m, terms)
            if len(S) != weight:
                raise AssertionError(f"weight {weight} class {ci}: support has {len(S)} points")
            yield Rep(f"w{weight}_c{ci}_m{m}", m, marked_geometries(m, S), repr(terms))


def census():
    sys.path.insert(0, str(REPO / "classification" / "rank7_census"))
    from rank7 import iter_parents, WINDOW_NMAX  # noqa: E402  the census engine's own iterator, unchanged
    by_class = {}
    for orbit, origin, points in iter_parents(mode="reps", nmax=WINDOW_NMAX):
        by_class.setdefault(orbit.index, []).append((len(points), origin, 7, tuple(points)))
    for index in sorted(by_class):
        yield Rep(f"rm37_class_{index}", 7, by_class[index],
                  f"RM(3,7) affine orbit class {index}, one origin per stabiliser orbit")


def reps_of(source):
    if source not in SOURCES:
        raise ValueError(f"unknown source {source!r}; one of {SOURCES}")
    return list({"weight40": weight40, "n38": n38, "census": census}[source]())


def expected_geometries(source):
    """{rep_id: n_geometries}, recomputed from the inputs, for coverage proofs."""
    return {rep.id: rep.n_geometries for rep in reps_of(source)}


def input_digest(source):
    """Digest of the source's input table, written into every result file."""
    import hashlib
    if source == "weight40":
        import reps40
        return reps40.sha256_of()
    if source == "n38":
        return hashlib.sha256((REPO / "classification" / "exhaustive_n38" / "nezami_haah_reps.py").read_bytes()).hexdigest()
    sys.path.insert(0, str(REPO / "classification" / "rank7_census"))
    from rank7 import DEFAULT_DATA, data_digest   # noqa: E402
    return data_digest(DEFAULT_DATA)
