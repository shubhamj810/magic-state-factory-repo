#!/usr/bin/env python3
"""Does any landscape sweep find a (n, k, d, S_k gate) that the shipped tables
do not have?  It should not: the sweeps re-enumerate known parent families
with a classifier whose class set is the plain one's.  This script checks
that from the RAW run files -- every (class, rank) entry of every
representative, not just the aggregated best witnesses -- against

  * ``weight40`` (n = 39, 40, every rank)  vs  the rank-7 census table
    ``../rank7_census/catalog/sk_classes_r7.json`` restricted to n = 39, 40
  * ``n38`` (n <= 38, every rank)          vs  ``../exhaustive_n38/catalog/classification_n38.json``
  * ``census`` (r <= 7, n <= 44)           vs  ``sk_classes_r7.json``

and, for all three, against the master catalogue ``master_catalog/master_catalog.json``.

For each family it reports: entries checked; distinct (n, k, d, gate) here;
any here that the shipped table lacks (a NEW result -- none expected); any
shipped the sweep did not find (a MISSING class -- none expected, and a
completeness failure if the sweep is complete); any witness whose verified
distance is not 3 (a new (n, k, d) -- none expected); and the same against the
master catalogue.  A family whose sweep is still incomplete is reported as
partial: 'missing' is then not evidence.

Exit status 1 if anything new, missing (from a complete sweep) or off-distance
turns up.

Run:  python crosscheck_new_results.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

from build_landscape import monomials_of_columns, sk_canonical, sk_name   # noqa: E402
from sources import SOURCES, reps_of                                      # noqa: E402

RESULTS = HERE / "results"
CENSUS = REPO / "classification" / "rank7_census" / "catalog" / "sk_classes_r7.json"
N38 = REPO / "classification" / "exhaustive_n38" / "catalog" / "classification_n38.json"
MASTER = REPO / "master_catalog" / "master_catalog.json"


_CANON = {}


def key_of(n, k, d, columns):
    """(n, k, d, S_k canonical gate) read off explicit columns -- representation-free.
    The k! canonicalisation is memoised on the monomial set (a k = 7 gate costs
    5040 permutations and recurs across ranks and representatives)."""
    cols = [sorted(set(c)) for c in columns]
    mons = monomials_of_columns(cols, k)
    canon = _CANON.get((k, mons))
    if canon is None:
        canon = _CANON[(k, mons)] = sk_canonical(k, mons)
    return (n, k, d, canon)


def label(key):
    return f"[[{key[0]},{key[1]},{key[2]}]] {sk_name(key[3])}"


def best_d(keys):
    """{(n, k, gate): best distance} -- a class counts once, at its best distance;
    a lower-distance realisation of a known class is not a result."""
    out = {}
    for n, k, d, gate in keys:
        out[(n, k, gate)] = max(d, out.get((n, k, gate), 0))
    return out


def new_or_better(here, shipped):
    """Classes here that the shipped table lacks, or has only at a lower distance."""
    return {c: d for c, d in here.items() if d > shipped.get(c, 0)}


def shipped_keys(path, n_filter=None):
    rows = json.loads(path.read_text(encoding="utf-8"))["factories"]
    out = set()
    for r in rows:
        if n_filter and r["n"] not in n_filter:
            continue
        out.add(key_of(r["n"], r["k"], r["d"], r["columns"]))
    return out


def sweep_keys(source):
    """Every (n, k, d, gate) of every entry in the raw run files, plus coverage."""
    reps = reps_of(source)
    keys = Counter()
    off_distance = []
    present = complete = 0
    for rep in reps:
        path = RESULTS / source / f"rep_{rep.id}.json"
        if not path.exists():
            continue
        blob = json.loads(path.read_text(encoding="utf-8"))
        present += 1
        complete += bool(blob.get("complete"))
        for f in blob["factories"]:
            d = f["distance"]
            if d != 3:
                off_distance.append((rep.id, f["n"], f["k"], f["gate"], d))
            keys[key_of(f["n"], f["k"], d if isinstance(d, int) else 5, f["columns"])] += 1
    return keys, off_distance, present, complete, len(reps)


def main():
    master = json.loads(MASTER.read_text(encoding="utf-8"))["factories"]
    # every sweep stops at n = 44 (the census window), so rows beyond it cannot match anything here
    master_keys = {key_of(r["n"], r["k"], r["d"], r["columns"]) for r in master if r["n"] <= 44}
    targets = {
        "weight40": (CENSUS, (39, 40), "sk_classes_r7.json at n = 39, 40"),
        "n38": (N38, None, "classification_n38.json"),
        "census": (CENSUS, None, "sk_classes_r7.json"),
    }
    bad = False
    for source in SOURCES:
        keys, off, present, complete, total = sweep_keys(source)
        path, nf, name = targets[source]
        shipped = best_d(shipped_keys(path, nf))
        here = best_d(keys)
        new = new_or_better(here, shipped)
        missing = new_or_better(shipped, here)
        new_master = new_or_better(here, best_d(master_keys))
        full = present == total == complete
        status = "complete" if full else f"PARTIAL ({present}/{total} representatives present, {complete} complete)"
        print(f"{source}: {status}; {sum(keys.values())} (class, rank) entries checked, "
              f"{len(here)} distinct (n, k, gate) at best distance {sorted(set(here.values()))}")
        print(f"  vs {name} ({len(shipped)} classes): {len(new)} new or better-distance here, "
              f"{len(missing)} shipped not found" + ("" if full else " (sweep partial: not evidence)"))
        print(f"  vs master catalogue: {len(new_master)} (n, k, gate) here that the master catalogue lacks "
              f"or has only at a lower distance")
        print(f"  witnesses with distance != 3: {len(off)}")
        for c, d in sorted(new.items(), key=str)[:10]:
            print("    NEW:", label((c[0], c[1], d, c[2])))
        for c, d in sorted(new_master.items(), key=str)[:10]:
            print("    NOT IN MASTER:", label((c[0], c[1], d, c[2])))
        if full:
            for c, d in sorted(missing.items(), key=str)[:10]:
                print("    MISSING:", label((c[0], c[1], d, c[2])))
        for o in off[:10]:
            print("    OFF-DISTANCE:", o)
        if new or new_master or off or (full and missing):
            bad = True
    print("\nRESULT:", "no new (n, k, d, gate) anywhere" if not bad else "SOMETHING NEW, MISSING OR OFF-DISTANCE -- see above")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
