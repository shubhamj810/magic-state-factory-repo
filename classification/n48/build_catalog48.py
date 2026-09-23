#!/usr/bin/env python3
"""THE CATALOGUE -- ``catalog/classification_n41_48.{json,md}``: every
(n, k, S_k gate) class of distance-3 factory with 41 <= n <= 48 injections
at every check rank the sweep covers, with the witness of minimum a3 per
class and per rank; and ``catalog/classification_upto_n48.{json,md}``: the
shipped n <= 40 table (``../n40/catalog/classification_upto_n40.json``,
verbatim) followed by the new rows.

Nothing here is trusted from the run files.  For every source the builder
recomputes the shard plan and the representative list from the inputs
(``sources48``), checks every shard is present, complete, unbudgeted,
uncapped, built from the current input digest and the current engine, that
every representative has exactly its 2^m + 1 geometries (the histogram sums
to that count), and only then reads the entries.  Every witness (primary and
per rank) is relabelled into its canonical S_k frame, re-checked by
``factorylib.verification.verify`` (gate parities, check-touching parities
even, distance exact to weight 4) and its a3 recounted from the columns --
the same helpers ``../n40/build_landscape.py`` uses, imported unchanged.
T-count is recomputed by ``factorylib.metrics`` for k <= 6 (exact, fast).  The
CNOT-frame-reduced degree is the master catalogue's bar too, but at k = 5 it
is an exact walk over |GL(5,2)| = 10^7 frames (~20 min per degree->=2 gate)
and at k = 6 a 2,000,000-frame bounded search (~7 min), so the builder does
not compute it: it reads this directory's ``reduced_degree_cache.json`` and
leaves ``poly_degree`` null, with a note, for a gate not yet in it.
``metrics48.py`` fills the cache (resumable, low priority) and a rebuild picks
the values up; ``factorylib.metrics``'s memo is redirected to that file so
building here writes nothing outside ``classification/n48``.

WHAT THE CATALOGUE COVERS, SECTOR BY SECTOR (``SECTORS`` below; the JSON
carries the same statement under ``scope_by_sector``):

    n = 41, 42   every check rank      length-42 table, every marking
    n = 43, 44   check rank >= 8       length-44 table (m >= 8), every marking,
                                       plus the rank-8 lifts of the 35 affine-
                                       rank-7 RM(3,7) words of weight 44
    n = 43, 44   check rank 7          those 35 words at every origin (up to
                                       the stabiliser): unconditional
    n = 45, 46   every check rank      length-46 table, every marking
    n = 47, 48   check rank >= 8       length-48 table (m >= 8), every marking,
                                       plus the rank-8 lifts of every affine-
                                       rank-7 RM(3,7) word of weight 48
    n = 47, 48   check rank 7          every affine-rank-7 weight-48 word of
                                       RM(3,7) at every origin (up to the
                                       stabiliser): unconditional, and
                                       independent of the length-48 table
                                       (which is missing two of these words)
    n = 47, 48   parents of the unique affine-rank-6 weight-48 word (check
                 rank 6, and its rank-7 lift at n = 48): OPEN, not swept
                 (``docs/OPEN_RANK6.md``); frames up to width 15 could live there.

"Complete" for the table sectors means: relative to the input tables, which
are validated (``reps48.validate``) but cannot be independently re-derived
here; the RM(3,7) sector needs no such assumption.

INTEGRITY PROBLEMS VERSUS COVERAGE GAPS.  ``aggregate`` reports two kinds of
defect.  An *integrity problem* (wrong digest or engine, a budget or cap, a
histogram that does not add up, a witness that fails verification) means the
files cannot be trusted and the source is refused.  A *coverage gap* (a shard
with no result file yet, or a geometry the engine gave up on -- ``failed``
entries, in practice ``OrbitTooLarge``: a k = 6 gate whose GL(6,2) orbit
exceeds the cap) means the files are sound but do not cover the whole sector.
Each geometry is classified independently, so the swept ones are exact; with
``--partial`` such a source is INCLUDED, its gaps are listed geometry by
geometry under ``sources[<source>].coverage_gaps`` in the JSON, and the sector
line says "partial" with the exclusions.  Without ``--partial`` any gap is fatal.

Run:  python build_catalog48.py            (after every source has been swept)
      python build_catalog48.py --partial  (include sources with coverage gaps,
                                            listing every excluded geometry;
                                            sources with integrity problems are skipped)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for p in (HERE, HERE.parent / "n40", REPO):
    sys.path.insert(0, str(p))

from factorylib import metrics as _metrics                    # noqa: E402
_metrics._CACHE_PATH = HERE / "reduced_degree_cache.json"     # never write outside this directory
try:
    _metrics._DEG_CACHE = json.loads(_metrics._CACHE_PATH.read_text(encoding="utf-8"))
except (OSError, ValueError):
    _metrics._DEG_CACHE = {}
from factorylib.metrics import metrics_from_named             # noqa: E402
from factorylib.metrics import _build_P, _remap0, _tcount_from_P   # noqa: E402
from factorylib.metrics import NotLevel3Error, poly_from_decomp    # noqa: E402
from build_landscape import (A3_DOC, canonical_witness, check_witness, compact_columns,   # noqa: E402
                             gate_human, named_from_monomials, sk_name)
import reps48                                                  # noqa: E402
from sources48 import input_digest, reps_of                    # noqa: E402
from classify48 import ENGINE, plan_shards, read_shard, shard_path, RESULTS   # noqa: E402

CATALOG = HERE / "catalog"
UPTO40 = HERE.parent / "n40" / "catalog" / "classification_upto_n40.json"
OUT_JSON = CATALOG / "classification_n41_48.json"
OUT_MD = CATALOG / "CLASSIFICATION_N41_48.md"
ALL_JSON = CATALOG / "classification_upto_n48.json"
ALL_MD = CATALOG / "CLASSIFICATION_UPTO_N48.md"
METRICS_K_CAP = 6          # matches master_catalog/verify_catalog.py

#: source -> (injection counts, admissible check ranks, what completeness means)
SECTORS = {
    "length42": ((41, 42), None, "every check rank; relative to the length-42 table"),
    "length44": ((43, 44), (8, None), "check rank >= 8; relative to the length-44 table (m >= 8 sector)"),
    "rm37_w44": ((43, 44), (7, 8), "check rank 7 (every origin of every affine-rank-7 weight-44 RM(3,7) "
                                   "word) and the rank-8 lifts of those words; unconditional"),
    "length46": ((45, 46), None, "every check rank; relative to the length-46 table"),
    "length48": ((47, 48), (8, None), "check rank >= 8; relative to the length-48 table (m >= 8 sector)"),
    "rm37_w48": ((47, 48), (7, 8), "check rank 7 (every origin of every affine-rank-7 weight-48 RM(3,7) "
                                   "word) and the rank-8 lifts of those words; unconditional"),
}
OPEN_SECTOR = ("n = 47, 48 from the unique affine-rank-6 weight-48 word (RM(3,7) class 3470, a+abc): "
               "check rank 6 at n = 47 and 48, and its rank-7 lift at n = 48.  Not swept: kappa = 20, 21, "
               "frames up to width 15 possible.  See docs/OPEN_RANK6.md.")


# ------------------------------------------------------------------ per source
def _error_kind(msg):
    """'OrbitTooLarge: k=6 orbit of a 13-monomial gate exceeds 150000 members'
    -> 'OrbitTooLarge: k=6 orbit exceeds 150000 members' (one bucket per cause)."""
    return re.sub(r" of a \d+-monomial gate", "", msg or "")


def aggregate(source, results_dir=None):
    """(entries, coverage, summary, problems, gaps) for one source.  ``entries``
    maps (n, k, canonical S_k key) -> rank -> best witness; ``coverage`` is the
    per-representative proof of what was swept; ``problems`` are integrity
    defects (the files cannot be trusted), ``gaps`` are coverage defects (the
    files are sound but some geometries were not classified); the summary
    carries the gaps geometry by geometry under ``coverage_gaps``."""
    results_dir = Path(results_dir) if results_dir else RESULTS / source
    (n_lo, n_hi), ranks, _ = SECTORS[source]
    reps = reps_of(source)
    digest = input_digest(source)
    shards = plan_shards(reps)
    problems, gaps, coverage = [], [], {}
    missing_shards, failed_geometries = [], []
    entries = defaultdict(dict)
    hist_total = Counter()
    for i, shard in enumerate(shards, 1):
        path = shard_path(results_dir, i)
        if not path.exists():
            gaps.append(f"{source}: shard {i}/{len(shards)} ({shard[0].id} .. {shard[-1].id}, "
                        f"{sum(r.n_geometries for r in shard)} geometries) has no result file")
            missing_shards.append({"shard": i, "rep_ids": [r.id for r in shard],
                                   "n_geometries": sum(r.n_geometries for r in shard),
                                   "representatives_by_m": dict(sorted(Counter(r.m for r in shard).items()))})
            continue
        blob = read_shard(path)
        name = path.name
        if blob.get("source") != source:
            problems.append(f"{name}: source={blob.get('source')!r}, not {source!r}")
        if blob.get("input_sha256") != digest:
            problems.append(f"{name}: built from an input with sha256 {blob.get('input_sha256')}, "
                            f"the current one is {digest}")
        if blob.get("engine") != ENGINE:
            problems.append(f"{name}: built by a different engine")
        if blob.get("rep_ids") != [r.id for r in shard]:
            problems.append(f"{name}: holds different representatives than the plan")
            continue
        if blob.get("dedup") != "symmetric" or blob.get("distance") != 3:
            problems.append(f"{name}: dedup={blob.get('dedup')!r}, distance={blob.get('distance')!r}")
        if blob.get("node_budget_per_parent") not in (0, None) or blob.get("orbit_budget_per_gate") not in (0, None):
            problems.append(f"{name}: a node or orbit budget was set")
        if blob.get("kmax") is not None:
            problems.append(f"{name}: frame width was capped at {blob['kmax']}; the catalogue needs an uncapped run")
        if blob.get("complete") is not True:
            # a shard is incomplete exactly when some geometry failed; that is a
            # gap, and the per-representative checks below verify the accounting
            (gaps if blob.get("n_failed") else problems).append(f"{name}: complete={blob.get('complete')!r}")
        by_id = {r["rep_id"]: r for r in blob.get("reps", [])}
        for rep in shard:
            rec = by_id.get(rep.id)
            if rec is None:
                problems.append(f"{name}: no record for {rep.id}")
                continue
            hist = rec.get("histogram", [])
            n_hist = sum(row[-1] for row in hist)
            failed = rec.get("failed") or []
            n_swept = rep.n_geometries - len(failed)
            if rec.get("n_geometries") != n_swept or n_hist != n_swept:
                problems.append(f"{name}: {rep.id} swept {rec.get('n_geometries')} geometries "
                                f"(histogram {n_hist}), the representative has {rep.n_geometries}"
                                + (f" of which {len(failed)} failed" if failed else ""))
            if failed:
                gaps.append(f"{name}: {rep.id} has {len(failed)} failed geometries: {failed[0]['error']}")
                for f in failed:
                    failed_geometries.append({"rep_id": rep.id, "m": rep.m, "origin": f.get("origin"),
                                              "n": f.get("n"), "ambient_rank": f.get("ambient_rank"),
                                              "error": f.get("error"), "shard": i})
            if rec.get("complete") is not True:
                (gaps if failed else problems).append(f"{name}: {rep.id} complete={rec.get('complete')!r}")
            for n, amb, rank, kappa, mu, ng, count in hist:
                if not n_lo <= n <= n_hi:
                    problems.append(f"{name}: {rep.id} swept a geometry with n = {n}")
                if ranks and not (ranks[0] <= rank <= (ranks[1] or 99)):
                    problems.append(f"{name}: {rep.id} swept a geometry of check rank {rank}")
                hist_total[(n, rank, kappa, mu)] += count
            for f in rec.get("factories", []):
                k = f["k"]
                mons = frozenset(frozenset(q) for q in f["wants"])
                if len({q for Q in mons for q in Q}) != k:
                    problems.append(f"{name}: {rep.id}: a stored class leaves an output idle")
                    continue
                columns = compact_columns(f["columns"], k)
                columns, canon = canonical_witness(columns, k, mons)
                key = (f["n"], k, canon)
                r = f["r"]
                N = max(max(c) for c in columns) + 1
                if N - k != r:
                    problems.append(f"{name}: {rep.id}: witness has {N - k} used check wires but rank {r}")
                w = {"rank": r, "N": N, "a3": f["a3"], "a3_max_seen": f["a3_max"],
                     "columns": columns, "d": f["distance"],
                     "source": f"{rep.id}, origin {f['origin']}; {source}/{name}",
                     "n_geometries_carrying": f["n_geometries_carrying"], "n_subspaces": f["n_subspaces"]}
                cur = entries[key].get(r)
                if cur is None or w["a3"] < cur["a3"]:
                    if cur is not None:
                        w["a3_max_seen"] = max(w["a3_max_seen"], cur["a3_max_seen"])
                        w["n_geometries_carrying"] += cur["n_geometries_carrying"]
                        w["n_subspaces"] += cur["n_subspaces"]
                    entries[key][r] = w
                else:
                    cur["a3_max_seen"] = max(cur["a3_max_seen"], w["a3_max_seen"])
                    cur["n_geometries_carrying"] += w["n_geometries_carrying"]
                    cur["n_subspaces"] += w["n_subspaces"]
            coverage[rep.id] = {
                "m": rep.m, "geometries": rec.get("n_geometries"), "expected": rep.n_geometries,
                "failed": len(failed),
                "max_kappa": rec.get("max_kappa"), "max_mu": rec.get("max_mu"),
                "n_classes": rec.get("n_classes"), "n_entries": rec.get("n_entries"),
                "subspaces_visited": rec.get("subspaces_visited"), "seconds": rec.get("seconds"),
            }
    summary = {
        "source": source, "input_sha256": digest, "sector": SECTORS[source][2],
        "n": list(SECTORS[source][0]),
        "n_representatives": len(reps), "n_shards": len(shards),
        "n_geometries": sum(c["geometries"] or 0 for c in coverage.values()),
        "n_geometries_expected": sum(r.n_geometries for r in reps),
        "representatives_by_m": dict(sorted(Counter(r.m for r in reps).items())),
        "max_kappa": max((c["max_kappa"] or 0 for c in coverage.values()), default=None),
        "max_frame_width_met": max((c["max_mu"] or 0 for c in coverage.values()), default=None),
        "cpu_seconds": round(sum(c["seconds"] or 0 for c in coverage.values())),
        "geometries_by_n_rank_kappa_mu": [[*k, v] for k, v in sorted(hist_total.items())],
        "complete": not problems and not gaps,
    }
    if gaps:
        n_missing = sum(g["n_geometries"] for g in missing_shards)
        summary["coverage_gaps"] = {
            "statement": (f"{n_missing + len(failed_geometries)} of {summary['n_geometries_expected']} geometries "
                          f"are NOT classified: {n_missing} in {len(missing_shards)} shard(s) with no result "
                          f"file ({sum(len(g['rep_ids']) for g in missing_shards)} representatives) and "
                          f"{len(failed_geometries)} geometries the engine gave up on (listed).  Every other "
                          f"geometry is classified completely; the catalogue is exact on those and silent on these."),
            "n_geometries_not_classified": n_missing + len(failed_geometries),
            "missing_shards": missing_shards,
            "failed_geometries": failed_geometries,
            "failed_by_error": dict(Counter(_error_kind(f["error"]) for f in failed_geometries)),
            "failed_by_n_rank": {f"n={n}, rank {r}": c for (n, r), c in sorted(Counter(
                (f["n"], f["ambient_rank"]) for f in failed_geometries).items())},
        }
    return entries, coverage, summary, problems, gaps


def rows_from_entries(entries):
    """One row per (n, k, class) with the per-rank landscape; witnesses verified."""
    problems, rows = [], []
    for (n, k, canon), by_rank in entries.items():
        mons = frozenset(frozenset(Q) for Q in canon)
        # The class is (n, k, gate); the distance is a property of the witness.
        # a3 = 0 exactly when d >= 4, so the minimum-a3 witness has the largest
        # distance, and that is the row's d; a rank whose best witness has
        # smaller d keeps its own d in the landscape (it happens at n = 48:
        # the T class has d = 4 at ranks 10-12 and d = 3 at ranks 8, 9).
        d = max(w["d"] for w in by_rank.values())
        for r, w in by_rank.items():
            if (w["d"] >= 4) != (w["a3"] == 0):
                problems.append(f"[[{n},{k}]] {sk_name(canon)} rank {r}: d = {w['d']} but a3 = {w['a3']}")
            msg = check_witness(w, k, w["d"], mons)
            if msg:
                problems.append(f"[[{n},{k},{d}]] {sk_name(canon)} rank {r}: {msg}")
        ranks = sorted(by_rank)
        best_rank = min(ranks, key=lambda r: (by_rank[r]["a3"], r))
        if by_rank[best_rank]["d"] != d:
            problems.append(f"[[{n},{k}]] {sk_name(canon)}: the minimum-a3 witness does not have the largest d")
        rows.append({
            "n": n, "k": k, "d": d, "gate": sk_name(canon), "gate_human": gate_human(canon),
            "gate_named": named_from_monomials(mons), "monomials": mons,
            "ranks": ranks,
            "best_rank": best_rank, "a3_best": by_rank[best_rank]["a3"],
            "fewest_checks_rank": ranks[0], "a3_at_fewest_checks": by_rank[ranks[0]]["a3"],
            "landscape": {str(r): by_rank[r] for r in ranks},
        })
    rows.sort(key=lambda r: (r["n"], r["k"], r["gate"]))
    for i, r in enumerate(rows, 1):
        r["index"] = i
    return rows, problems


DEG_PENDING = "not yet computed: run metrics48.py (fills reduced_degree_cache.json), then rebuild"


def degree_cache_key(gate_named, level=3):
    """The key ``factorylib.metrics.reduced_poly_degree`` memoises a gate under,
    so the builder can read the cache without triggering the computation."""
    supports = []
    for tok in gate_named.replace(".", " ").split():
        supports.append(tuple(int(ch) for ch in tok if ch.isdigit()))
    supports = [tuple(sorted(s)) for s in supports if s]
    if not supports:
        return None
    L = max(level, max(len(s) for s in supports), 1)
    P = _build_P(supports, L)
    if not P:
        return None
    Pr, _ = _remap0(P)
    return f"{L}|" + repr(sorted(tuple(sorted(S)) for S in Pr))


def metrics_cached(gate_named):
    """(t_count, t_note, poly_degree, deg_note): the exact T-count now, the
    reduced degree only if ``reduced_degree_cache.json`` already holds it."""
    if not gate_named:
        return 0, None, 0, None
    key = degree_cache_key(gate_named)
    if key is None:
        poly_deg, deg_note = 0, None
    elif key in _metrics._DEG_CACHE:
        e = _metrics._DEG_CACHE[key]
        poly_deg, deg_note = e["deg"], e.get("note")
    else:
        poly_deg, deg_note = None, DEG_PENDING
    try:
        P, _ = poly_from_decomp(gate_named)
    except NotLevel3Error:
        return None, _metrics._NOTE_PI8, poly_deg, deg_note
    tc, note = _tcount_from_P(P)
    return tc, note, poly_deg, deg_note


def enrich(row):
    """Metrics from the gate, and the flat fields of the primary witness."""
    k = row["k"]
    if k <= METRICS_K_CAP:
        t_count, t_note, poly_deg, deg_note = metrics_cached(row["gate_named"])
    else:
        note = (f"not computed: exact minimisation is over GL({k},2) and a punctured "
                f"RM({k}-4,{k}) coset, neither feasible at k={k}")
        t_count, t_note, poly_deg, deg_note = None, note, None, note
    best = row["landscape"][str(row["best_rank"])]
    out = {
        "n": row["n"], "k": k, "d": row["d"], "N": best["N"], "r_checks": best["rank"],
        "gate": row["gate"], "gate_human": row["gate_human"], "gate_named": row["gate_named"],
        "t_count": t_count, "poly_degree": poly_deg,
        "a3": best["a3"], "best_rank": row["best_rank"],
        "fewest_checks_rank": row["fewest_checks_rank"], "a3_at_fewest_checks": row["a3_at_fewest_checks"],
        "ranks": row["ranks"],
        "columns": best["columns"], "source": best["source"],
        "landscape": row["landscape"],
        "index": row["index"],
    }
    if t_note:
        out["t_count_note"] = t_note
    if deg_note:
        out["poly_degree_note"] = deg_note
    return out


def build(sources, allow_partial=False):
    for L in (42, 44, 46, 48):
        problems = reps48.validate(L)
        if problems:
            for p in problems:
                print("  -", p)
            raise SystemExit(f"the length-{L} input table did not validate")
    entries = defaultdict(dict)
    summaries, coverages, skipped = {}, {}, []
    for source in sources:
        t0 = time.time()
        ent, cov, summary, problems, gaps = aggregate(source)
        if problems:
            for p in problems[:20]:
                print("  -", p)
            if not allow_partial:
                raise SystemExit(f"{source}: {len(problems)} problem(s): the result files do not add up to one "
                                 f"complete, verified sweep")
            print(f"  {source}: {len(problems)} integrity problem(s); SKIPPED (partial build)")
            skipped.append(source)
            continue
        if gaps:
            for g in gaps[:20]:
                print("  -", g)
            if not allow_partial:
                raise SystemExit(f"{source}: {len(gaps)} coverage gap(s): the sweep is not finished "
                                 f"(use --partial to build with the gaps listed)")
            if not ent:
                print(f"  {source}: nothing swept yet; SKIPPED (partial build)")
                skipped.append(source)
                continue
            print(f"  {source}: INCLUDED WITH COVERAGE GAPS -- {summary['coverage_gaps']['statement']}")
        for key, by_rank in ent.items():
            for r, w in by_rank.items():
                cur = entries[key].get(r)
                if cur is None or w["a3"] < cur["a3"]:
                    if cur is not None:
                        w["a3_max_seen"] = max(w["a3_max_seen"], cur["a3_max_seen"])
                    entries[key][r] = w
                elif w["a3_max_seen"] > cur["a3_max_seen"]:
                    cur["a3_max_seen"] = w["a3_max_seen"]
        summaries[source], coverages[source] = summary, cov
        print(f"  {source}: {summary['n_representatives']} representatives, {summary['n_geometries']} geometries "
              f"{'classified, ' + str(summary['coverage_gaps']['n_geometries_not_classified']) + ' not' if gaps else 'all complete'}; "
              f"max kappa {summary['max_kappa']}, max frame width {summary['max_frame_width_met']}, "
              f"{len(ent)} classes, {sum(len(v) for v in ent.values())} (class, rank) entries "
              f"[{time.time() - t0:.0f}s]")
    rows, problems = rows_from_entries(entries)
    if problems:
        for p in problems[:20]:
            print("  -", p)
        raise SystemExit(f"{len(problems)} witness problem(s)")
    t0 = time.time()
    rows = [enrich(r) for r in rows]
    pending = sum(1 for r in rows if r.get("poly_degree_note") == DEG_PENDING)
    print(f"{len(rows)} distinct (n, k, S_k gate) classes: "
          + ", ".join(f"n={n}: {v}" for n, v in sorted(Counter(r['n'] for r in rows).items()))
          + f"; {sum(len(r['ranks']) for r in rows)} (class, rank) witnesses, every one re-verified "
            f"(factorylib.verification, distance exact to weight 4; a3 recounted) [metrics {time.time() - t0:.0f}s]"
          + (f"; reduced degree pending for {pending} classes (metrics48.py)" if pending else ""))
    return rows, summaries, coverages, skipped


def combined_rows(rows):
    """The shipped n <= 40 rows verbatim, then ours, on a common field set."""
    blob = json.loads(UPTO40.read_text(encoding="utf-8"))
    old = blob["factories"]
    if len(old) != blob["n_classes"]:
        raise SystemExit("classification_upto_n40.json disagrees with itself on its row count")
    if any(r["n"] > 40 for r in old):
        raise SystemExit("classification_upto_n40.json holds a row above n = 40")
    out = []
    for r in old:
        out.append({key: r[key] for key in ("n", "k", "d", "N", "r_checks", "gate", "gate_human",
                                             "t_count", "poly_degree", "a3", "columns", "source", "table")})
    for r in rows:
        out.append({
            "n": r["n"], "k": r["k"], "d": r["d"], "N": r["N"], "r_checks": r["r_checks"],
            "gate": r["gate"], "gate_human": r["gate_human"],
            "t_count": r["t_count"], "poly_degree": r["poly_degree"],
            "a3": r["a3"],
            "columns": r["columns"], "source": r["source"],
            "table": "classification/n48/catalog/classification_n41_48.json",
        })
    out.sort(key=lambda r: (r["n"], r["k"], r["gate"]))
    for i, r in enumerate(out, 1):
        r["index"] = i
    return out, len(old)


# ----------------------------------------------------------------- rendering
def _counts_table(rows, with_ranks=True):
    by_n = defaultdict(list)
    for r in rows:
        by_n[r["n"]].append(r)
    L = ["| n | classes | by k | check rank of the best witness | max T |", "|---|---|---|---|---|"]
    for n in sorted(by_n):
        ks = Counter(r["k"] for r in by_n[n])
        rs = Counter(r["r_checks"] for r in by_n[n])
        ts = [r["t_count"] for r in by_n[n] if r["t_count"] is not None]
        L.append(f"| {n} | {len(by_n[n])} | " + ", ".join(f"k={k}: {v}" for k, v in sorted(ks.items()))
                 + " | " + ", ".join(f"r={k}: {v}" for k, v in sorted(rs.items()))
                 + f" | {max(ts) if ts else '—'} |")
    return L


def _class_tables(rows, landscape=True):
    by_n = defaultdict(list)
    for r in rows:
        by_n[r["n"]].append(r)
    L = []
    for n in sorted(by_n):
        if landscape:
            L += [f"### n = {n}", "", "| # | [[n,k,d]] | N | gate | T | deg | a3 (rank) | a3 by rank |",
                  "|---|---|---|---|---|---|---|---|"]
        else:
            L += [f"### n = {n}", "", "| # | [[n,k,d]] | N | gate | T | deg | a3 |", "|---|---|---|---|---|---|---|"]
        for r in by_n[n]:
            t = "—" if r["t_count"] is None else r["t_count"]
            dg = "—" if r["poly_degree"] is None else r["poly_degree"]
            line = (f"| {r['index']} | `[[{r['n']},{r['k']},{r['d']}]]` | {r['N']} | "
                    f"`{r['gate_human']}` | {t} | {dg} | ")
            if landscape:
                line += (f"{r['a3']} (r={r['r_checks']}) | "
                         + ", ".join(f"r={rk}: {r['landscape'][str(rk)]['a3']}"
                                     + (f" (d={r['landscape'][str(rk)]['d']})"
                                        if r['landscape'][str(rk)]['d'] != r['d'] else "")
                                     for rk in r["ranks"]) + " |")
            else:
                line += f"{r['a3']} |"
            L.append(line)
        L.append("")
    return L


def _circuit(columns):
    return "[" + ", ".join("{" + ",".join(map(str, c)) + "}" for c in columns) + "]"


def _witnesses(rows, landscape=True):
    L = []
    for r in rows:
        L.append(f"### {r['index']}. `[[{r['n']},{r['k']},{r['d']}]]` — {r['gate_human']}")
        L.append("")
        L.append(f"- gate `{r['gate']}`, `N = {r['N']}` ({r['k']} outputs + {r['r_checks']} checks), "
                 f"T-count {r['t_count'] if r['t_count'] is not None else '—'}, "
                 f"reduced degree {r['poly_degree'] if r['poly_degree'] is not None else '—'}, "
                 f"a3 = {r['a3']}")
        L.append(f"- source: {r['source']}")
        L.append("")
        L.append("```text")
        L.append(_circuit(r["columns"]))
        L.append("```")
        L.append("")
        if landscape and len(r["ranks"]) > 1:
            L.append("Best witness at each other check rank:")
            L.append("")
            for rk in r["ranks"]:
                if rk == r["r_checks"]:
                    continue
                w = r["landscape"][str(rk)]
                L.append(f"- rank {rk} (`N = {w['N']}`), a3 = {w['a3']}"
                         + (f", d = {w['d']}" if w["d"] != r["d"] else "") + f"; {w['source']}")
                L.append("")
                L.append("  ```text")
                L.append("  " + _circuit(w["columns"]))
                L.append("  ```")
                L.append("")
    return L


def _sector_lines(summaries, skipped):
    L = ["| source | n | check ranks | representatives | geometries | max kappa | max width | classes | status |",
         "|---|---|---|---|---|---|---|---|---|"]
    for s, (ns, ranks, what) in SECTORS.items():
        rk = "all" if ranks is None else (f">= {ranks[0]}" if ranks[1] is None else f"{ranks[0]}, {ranks[1]}")
        if s in summaries:
            sm = summaries[s]
            if sm.get("coverage_gaps"):
                cg = sm["coverage_gaps"]
                n_miss = sum(g["n_geometries"] for g in cg["missing_shards"])
                status = (f"**partial**: {cg['n_geometries_not_classified']} of {sm['n_geometries_expected']} "
                          f"geometries not classified ({n_miss} in {len(cg['missing_shards'])} unswept shard(s), "
                          f"{len(cg['failed_geometries'])} orbit-cap failures; listed in the JSON)")
            else:
                status = "complete"
            L.append(f"| `{s}` | {ns[0]}, {ns[1]} | {rk} | {sm['n_representatives']} | {sm['n_geometries']} | "
                     f"{sm['max_kappa']} | {sm['max_frame_width_met']} | {sm.get('n_classes', '')} | {status} |")
        else:
            L.append(f"| `{s}` | {ns[0]}, {ns[1]} | {rk} | | | | | | **not swept** |")
    L.append("| *(open)* | 47, 48 | 6, and the rank-7 lift at n = 48 | 1 | 3 | 20–21 | <= 15 | ? | **open** |")
    return L


def render_new(rows, summaries, skipped):
    tmax = max((r["t_count"] for r in rows if r["t_count"] is not None), default=None)
    multi = sum(1 for r in rows if len(r["ranks"]) > 1)
    improved = sum(1 for r in rows if r["a3"] < r["a3_at_fewest_checks"])
    n_geoms = sum(s["n_geometries"] for s in summaries.values())
    gapped = [s for s in summaries if summaries[s].get("coverage_gaps")]
    L = ["# Classification at `41 <= n <= 48`: every `S_k` class, every covered check rank", ""]
    if skipped or gapped:
        L.append("**PARTIAL BUILD** -- "
                 + (f"sources not yet swept: {', '.join(f'`{s}`' for s in skipped)}" if skipped else "")
                 + ("; " if skipped and gapped else "")
                 + (f"sources included with coverage gaps: {', '.join(f'`{s}`' for s in gapped)}" if gapped else "")
                 + ".")
        L.append("")
        for s in gapped:
            cg = summaries[s]["coverage_gaps"]
            L.append(f"- `{s}`: {cg['statement']}")
            for g in cg["missing_shards"]:
                L.append(f"  - shard {g['shard']}: {len(g['rep_ids'])} representatives "
                         f"(`{g['rep_ids'][0]}` .. `{g['rep_ids'][-1]}`), {g['n_geometries']} geometries, not run")
            if cg["failed_geometries"]:
                L.append(f"  - {len(cg['failed_geometries'])} failed geometries, by (n, check rank): "
                         + ", ".join(f"{k}: {v}" for k, v in cg["failed_by_n_rank"].items())
                         + "; by error: " + "; ".join(f"{v} x `{k}`" for k, v in cg["failed_by_error"].items()))
        L.append("")
    L.append(f"**{len(rows)} distinct `(n, k, S_k gate)` classes** of distance-3 factory with 41 to 48 "
             f"injections, each with the witness circuit of smallest leading error coefficient and the best "
             f"witness at every check rank the class occurs at.  "
             f"`a3` is the number of 3-sets of injections that pass every check and act on the outputs: "
             f"`P_fail ~ a3 p^3`; `a3 = 0` means the witness has distance 4 (`P_fail = O(p^4)`), and the "
             f"`[[n,k,d]]` label carries the distance of the primary witness, the largest over its ranks "
             f"(a rank whose best witness has a smaller distance is marked in the last column).  "
             f"{multi} classes occur at more than one check rank; for {improved} of the "
             f"{len(rows)} the best circuit is not the fewest-check one.")
    L.append("")
    L.append("## What is covered")
    L.append("")
    L.append("A distance-3 factory with n injections has a check parent of some rank r; the parent's "
             "columns plus (n odd) the origin form a no-repeated-column unital triorthogonal space of "
             "length n + (n mod 2).  The complete affine classifications of those spaces at lengths 42, 44, "
             "46, 48 (`length*_catalogue.json`) marked at every origin give every parent -- except that the "
             "length-48 table's affine-rank-7 sector is missing two classes (`docs/INPUT_DEFECT_M7.md`), so "
             "the whole rank-7 sector at n = 47, 48 is taken from the RM(3,7) orbit table instead "
             "(unconditional), and the one affine-rank-6 word of weight 48 gives parents no brute-force "
             "engine can enumerate (`docs/OPEN_RANK6.md`).")
    L.append("")
    L += _sector_lines(summaries, skipped)
    L.append("")
    L.append(f"In total {n_geoms} check parents were classified completely (every compatible subspace at "
             f"every width, no budget, no cap; `classify48.py`)"
             + ("; the sources marked partial above have further parents that are not classified, and a "
                "class carried only by those parents would be absent here" if gapped else "")
             + ".  " + OPEN_SECTOR)
    L.append("")
    L.append("## Counts")
    L.append("")
    L += _counts_table(rows)
    L.append("")
    L.append("## The classes")
    L.append("")
    L += _class_tables(rows)
    L.append("Witness circuits (one per class and per rank) are in `witnesses/WITNESSES_N<n>.md` and in the JSON.")
    L.append("")
    return "\n".join(L) + "\n"


def render_all(rows, n_old):
    L = ["# Every distance-3 factory class with at most 48 injections", ""]
    L.append(f"**{len(rows)} distinct `(n, k, S_k gate)` classes**, one verified witness circuit each: the "
             f"{n_old} rows of `../../n40/catalog/classification_upto_n40.json` (n <= 40, copied verbatim) "
             f"followed by the {len(rows) - n_old} rows of `classification_n41_48.json` (best-a3 witnesses).")
    L.append("")
    L.append("At n = 47, 48 the parents of the unique affine-rank-6 weight-48 word (check rank 6, and its "
             "rank-7 lift at n = 48) are not classified; every other check rank is.  See "
             "`CLASSIFICATION_N41_48.md` for the sector-by-sector statement.")
    L.append("")
    L.append("## Counts")
    L.append("")
    L += _counts_table(rows)
    L.append("")
    L.append("## The classes")
    L.append("")
    L += _class_tables(rows, landscape=False)
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--partial", action="store_true",
                    help="build from whatever is swept: sources with coverage gaps are included with every "
                         "unclassified geometry listed; sources with integrity problems are skipped")
    a = ap.parse_args(argv)
    rows, summaries, coverages, skipped = build(list(SECTORS), allow_partial=a.partial)
    for s in summaries:
        summaries[s]["n_classes"] = len({(r["n"], r["k"], r["gate"]) for r in rows
                                         if any(w["source"].split("; ")[-1].startswith(s + "/")
                                                for w in r["landscape"].values())})
    CATALOG.mkdir(exist_ok=True)
    (CATALOG / "witnesses").mkdir(exist_ok=True)
    tmax = max((r["t_count"] for r in rows if r["t_count"] is not None), default=None)
    payload = {
        "scope": "every (n, k, S_k gate) class of distance-3 factory with 41 <= n <= 48 injections at "
                 "every covered check rank (see scope_by_sector); per class the witness of minimum a3 "
                 "over all ranks, and the best witness at every rank the class occurs at",
        "scope_by_sector": {s: {"n": list(v[0]), "check_ranks": ("all" if v[1] is None else list(v[1])),
                                "completeness": v[2],
                                "swept": (False if s not in summaries else
                                          ("partial" if summaries[s].get("coverage_gaps") else True)),
                                **({"coverage_gaps": summaries[s]["coverage_gaps"]["statement"]}
                                   if s in summaries and summaries[s].get("coverage_gaps") else {})}
                            for s, v in SECTORS.items()},
        "open_sector": OPEN_SECTOR,
        "partial": bool(skipped) or any(s.get("coverage_gaps") for s in summaries.values()),
        "sources_not_swept": skipped,
        "sources_with_coverage_gaps": [s for s in summaries if summaries[s].get("coverage_gaps")],
        "dedup_key": "S_k: output permutations only (GL(k,2) is coarser and not used)",
        "a3": A3_DOC,
        "inputs": {f"length{L}": {"file": reps48.FILES[L].name, "sha256": reps48.sha256_of(L),
                                  "representatives": reps48.EXPECTED_COUNT[L]} for L in reps48.LENGTHS},
        "engine": "classify48.py (factorylib.parent + n40/landscape orbit-memoised S_k classification with "
                  "the minimum-a3 witness per class), no budget, no width cap",
        "sources": summaries,
        "coverage": coverages,
        "n_geometries": sum(s["n_geometries"] for s in summaries.values()),
        "n_classes": len(rows),
        "n_reduced_degree_pending": sum(1 for r in rows if r.get("poly_degree_note") == DEG_PENDING),
        "n_class_rank_witnesses": sum(len(r["ranks"]) for r in rows),
        "classes_at_more_than_one_rank": sum(1 for r in rows if len(r["ranks"]) > 1),
        "classes_whose_best_is_not_fewest_checks": sum(1 for r in rows if r["a3"] < r["a3_at_fewest_checks"]),
        "max_k": max(r["k"] for r in rows),
        "t_max": tmax,
        "factories": rows,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_new(rows, summaries, skipped), encoding="utf-8")
    by_n = defaultdict(list)
    for r in rows:
        by_n[r["n"]].append(r)
    for n, rs in sorted(by_n.items()):
        (CATALOG / "witnesses" / f"WITNESSES_N{n}.md").write_text(
            "\n".join([f"# Witness circuits at n = {n}", "",
                       f"{len(rs)} classes; the primary witness (minimum a3 over all ranks) and the best "
                       f"witness at every other rank.  Columns are sets of wire indices: outputs 0..k-1, "
                       f"checks k..N-1.", ""] + _witnesses(rs)) + "\n", encoding="utf-8")
    print(f"wrote {OUT_JSON.name}, {OUT_MD.name}, witnesses/: {len(rows)} classes, "
          f"{payload['classes_at_more_than_one_rank']} at more than one rank, "
          f"{payload['classes_whose_best_is_not_fewest_checks']} whose best circuit is not the fewest-check one")

    all_rows, n_old = combined_rows(rows)
    all_payload = {
        "scope": "every (n, k, S_k gate) class of distance-3 factory with n <= 48 injections at every "
                 "covered check rank: the shipped n <= 40 table followed by the n = 41 .. 48 one",
        "open_sector": OPEN_SECTOR,
        "partial": payload["partial"],
        "sources_not_swept": skipped,
        "sources_with_coverage_gaps": payload["sources_with_coverage_gaps"],
        "dedup_key": payload["dedup_key"],
        "a3": A3_DOC,
        "tables": [str(UPTO40.relative_to(REPO)), str(OUT_JSON.relative_to(REPO))],
        "n_classes": len(all_rows), "n_from_upto_n40": n_old, "n_from_n41_48": len(rows),
        "max_k": max(r["k"] for r in all_rows),
        "t_max": max(r["t_count"] for r in all_rows if r["t_count"] is not None),
        "factories": all_rows,
    }
    ALL_JSON.write_text(json.dumps(all_payload, indent=1) + "\n", encoding="utf-8")
    ALL_MD.write_text(render_all(all_rows, n_old), encoding="utf-8")
    print(f"wrote {ALL_JSON.name} and {ALL_MD.name}: {len(all_rows)} classes ({n_old} from n <= 40)")


if __name__ == "__main__":
    main()
