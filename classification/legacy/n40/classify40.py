#!/usr/bin/env python3
"""THE SWEEP -- every S_k class of distance-3 factory carried by a family of
check parents, with, per class and per check rank, the witness of minimum
leading error coefficient.

Three families (``sources.py``):
  * ``weight40`` (default): the 110 representatives of ``length40_catalogue.json``
    at every marking -- n = 39, 40 at every check rank.  This directory's own
    classification.
  * ``n38``: the Kasami-Tokura / Nezami-Haah representatives behind the shipped
    ``n <= 38`` classification, at every marking -- the same parents that
    classification enumerated, re-swept here to recover the coefficient
    landscape it collapsed.
  * ``census``: the RM(3,7) orbits of the rank-7 census at one origin per
    stabiliser orbit -- every rank <= 7 parent with n <= 44.

For each marked geometry: build the check parent and its quotient V_3(C) with
the shared engine ``factorylib.parent.Parent`` (unchanged, imported) and run
``landscape.classify_landscape``: every compatible subspace at every width
(no cap by default), one witness per S_k class, the witness chosen to minimise
the p^3 coefficient a3 (undetected, harmful 3-sets of injections) among all
subspaces of the geometry that realise the class.  Nothing has a budget: a
geometry either finishes completely or the run aborts.

OUTPUT: ``results/<source>/rep_<id>.json`` per representative --
  * ``geometries``: one record per marking (n, origin, rank, kappa, t3, mu,
    subspaces, orbits, [class index, a3] pairs);
  * ``factories``: the representative's distinct (n, k, S_k class, check rank)
    entries, each with the minimum-a3 witness over the representative's
    geometries of that rank;
  * ``complete``: true iff every marking was swept.

Usage:
    classify40.py                              # weight40, everything (~20 min on 16 cores)
    classify40.py --source n38                 # the n <= 38 parents
    classify40.py --source census              # the rank-7 census parents (hours)
    classify40.py --rep length40_m6_001        # only this representative
    classify40.py --workers 8 --force          # re-run even where a file exists
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))

from landscape import Parent, classify_landscape                       # noqa: E402
from sources import SOURCES, input_digest, reps_of                     # noqa: E402

RESULTS = HERE / "results"
ENGINE = ("factorylib.parent (Parent.from_points at the parent's own ambient rank; "
          "compatible_subspaces uncapped) + orbit-memoised S_k classification with the "
          "minimum-a3 witness per class (landscape.classify_landscape)")


def _job(args):
    rep_id, n, origin, ambient, points, kmax = args
    t0 = time.time()
    parent = Parent.from_points(points, ambient_rank=ambient, distance=3)
    if parent.n != n:
        raise AssertionError(f"{rep_id} origin {origin}: parent has {parent.n} columns, marking says {n}")
    out = classify_landscape(parent, kmax=kmax)
    geometry = {
        "n": n, "origin": origin, "ambient_rank": ambient, "check_rank": parent.check_rank,
        "kappa": parent.kappa, "quadric_degeneracy": parent.quadric_degeneracy,
        "t3": out["t3"], "mu": out["mu"], "subspaces_visited": out["subspaces_visited"],
        "distinct_orbits": out["distinct_orbits"], "distinct_members": out["distinct_members"],
        "n_gates": out["n_gates"], "gate_search_complete": out["complete"],
        "seconds": round(time.time() - t0, 2),
    }
    return rep_id, geometry, out["gates"]


def sweep_rep(rep, pool, kmax, workers, digest, source):
    t0 = time.time()
    jobs = [(rep.id, n, origin, ambient, points, kmax) for n, origin, ambient, points in rep.geometries]
    geometries, classes, index_of = [], [], {}
    chunk = 1 if rep.m <= 7 or source == "census" else max(1, len(jobs) // (workers * 8))
    done = 0
    for rep_id, geometry, gates in pool.imap_unordered(_job, jobs, chunksize=chunk):
        idx = []
        for g in gates:
            key = (geometry["n"], g["k"], tuple(tuple(q) for q in g["canonical_key"]), geometry["check_rank"])
            if key not in index_of:
                index_of[key] = len(classes)
                classes.append({
                    "n": geometry["n"], "k": g["k"], "r": geometry["check_rank"],
                    "N": g["k"] + geometry["ambient_rank"], "distance": g["distance"],
                    "gate": g["gate"], "canonical_key": g["canonical_key"], "wants": g["wants"],
                    "a3": g["a3"], "a3_max": g["a3_max"], "n_subspaces": g["n_subspaces"],
                    "columns": g["columns"], "origin": geometry["origin"],
                    "ambient_rank": geometry["ambient_rank"], "n_geometries_carrying": 0,
                })
            c = classes[index_of[key]]
            c["n_geometries_carrying"] += 1
            c["a3_max"] = max(c["a3_max"], g["a3_max"])
            c["n_subspaces"] += 0 if c["origin"] == geometry["origin"] else g["n_subspaces"]
            if g["a3"] < c["a3"]:
                c.update(a3=g["a3"], columns=g["columns"], origin=geometry["origin"],
                         N=g["k"] + geometry["ambient_rank"], ambient_rank=geometry["ambient_rank"],
                         distance=g["distance"])
            idx.append([index_of[key], g["a3"]])
        geometry["classes"] = sorted(idx)
        geometries.append(geometry)
        done += 1
        if rep.m <= 7 or source == "census" or done % 500 == 0 or done == len(jobs):
            print(f"    {rep.id}: {done}/{len(jobs)} geometries, {len(classes)} (class, rank) entries so far, "
                  f"{time.time() - t0:.0f}s", flush=True)
    geometries.sort(key=lambda g: (g["n"], str(g["origin"]).rjust(8)))
    for i, c in enumerate(classes):
        c["index"] = i
    counts = Counter((c["n"], c["k"]) for c in classes)
    return {
        "source": source, "rep_id": rep.id, "m": rep.m, "note": rep.note,
        "input_sha256": digest,
        "engine": ENGINE, "dedup": "symmetric", "kmax": kmax, "distance": 3,
        "node_budget_per_parent": 0, "orbit_budget_per_gate": 0,
        "n_geometries_expected": rep.n_geometries, "n_geometries": len(geometries),
        "complete": len(geometries) == rep.n_geometries and all(g["gate_search_complete"] for g in geometries),
        "max_kappa": max(g["kappa"] for g in geometries),
        "max_mu": max(g["mu"] for g in geometries),
        "n_entries": len(classes),
        "n_classes": len({(c["n"], c["k"], tuple(map(tuple, c["canonical_key"]))) for c in classes}),
        "entries_by_n_k": {f"{n},{k}": v for (n, k), v in sorted(counts.items())},
        "geometries": geometries,
        "factories": classes,
        "seconds": round(time.time() - t0, 1),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--source", choices=SOURCES, default="weight40")
    ap.add_argument("--rep", action="append", help="representative id (repeatable)")
    ap.add_argument("--m", action="append", type=int, help="intrinsic dimension (repeatable; weight40 and n38)")
    ap.add_argument("--kmax", type=int, default=None,
                    help="cap the frame width (default: none; the catalogue builder refuses "
                         "a capped run whose cap was reached)")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--force", action="store_true", help="re-run representatives that have a result file")
    ap.add_argument("--output-dir", default=None, help="default results/<source>")
    a = ap.parse_args(argv)

    if a.source == "weight40":
        from reps40 import CATALOGUE, EXPECTED_SHA256, validate
        problems = validate()
        if problems:
            for p in problems:
                print("PROBLEM:", p)
            raise SystemExit("the input table did not validate; nothing was run")
    digest = input_digest(a.source)
    if a.source == "weight40" and digest != EXPECTED_SHA256:
        print(f"note: {CATALOGUE.name} has sha256 {digest}, not the one this directory was built from")
    reps = reps_of(a.source)
    if a.rep:
        reps = [r for r in reps if r.id in set(a.rep)]
    if a.m:
        reps = [r for r in reps if r.m in set(a.m)]
    reps.sort(key=lambda r: (r.m, r.id))          # the hard, low-m ones first
    out_dir = Path(a.output_dir) if a.output_dir else RESULTS / a.source
    out_dir.mkdir(parents=True, exist_ok=True)
    todo = []
    for r in reps:
        path = out_dir / f"rep_{r.id}.json"
        if path.exists() and not a.force:
            try:
                blob = json.loads(path.read_text(encoding="utf-8"))
                if blob.get("complete") and blob.get("input_sha256") == digest and blob.get("kmax") == a.kmax \
                        and blob.get("engine") == ENGINE:
                    continue
            except ValueError:
                pass
        todo.append(r)
    print(f"source {a.source}: {len(reps)} representative(s) selected, {len(todo)} to run, "
          f"{sum(r.n_geometries for r in todo)} geometries, {a.workers} workers, "
          f"kmax={'none' if a.kmax is None else a.kmax}", flush=True)
    t0 = time.time()
    with Pool(a.workers) as pool:
        for i, rep in enumerate(todo, 1):
            print(f"[{i}/{len(todo)}] {rep.id} (m={rep.m}, {rep.n_geometries} geometries)", flush=True)
            blob = sweep_rep(rep, pool, a.kmax, a.workers, digest, a.source)
            path = out_dir / f"rep_{rep.id}.json"
            tmp = path.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(blob, indent=1) + "\n", encoding="utf-8")
            os.replace(tmp, path)
            print(f"    wrote {path.name}: {blob['n_classes']} classes, {blob['n_entries']} (class, rank) entries "
                  f"{blob['entries_by_n_k']}, max kappa {blob['max_kappa']}, max mu {blob['max_mu']}, "
                  f"{blob['seconds']}s", flush=True)
    print(f"done: {len(todo)} representative(s) in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
