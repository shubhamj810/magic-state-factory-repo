#!/usr/bin/env python3
"""AGGREGATE a landscape sweep into per-class, per-rank best witnesses; and,
for the two re-swept shipped classifications, publish what their one-witness
catalogues collapsed.

``aggregate(source)`` is shared with ``build_catalog40.py`` (the weight-40
catalogue).  Run as a script it builds

  * ``catalog/landscape_n38.json`` / ``LANDSCAPE_N38.md``      (``--source n38``)
  * ``catalog/landscape_census_r7.json`` / ``LANDSCAPE_CENSUS_R7.md``  (``--source census``)

each holding, per (n, k, S_k gate) class, the minimum p^3 coefficient a3 at
every check rank the class occurs at, with a verified witness per rank, and
comparing that with the single witness the shipped table kept.

COVERAGE PROOF (``aggregate``), before any row is used
  * every representative of the source has a result file built from the
    source's current input (digest), with ``complete`` true;
  * the file holds exactly the representative's markings, recomputed here
    from the input, each once, each with a complete gate search;
  * no budget; no width cap, or a cap no geometry reached.

VERIFICATION, per published witness (primary and per rank)
  * relabelled into the canonical S_k frame; untouched check wires dropped;
  * ``factorylib.verification.verify`` from the raw columns: gate parities,
    check-touching parities even, distance exact to weight 4;
  * a3 recounted directly from the columns (``landscape.a3_of_columns``).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from itertools import permutations
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))

from factorylib.verification import verify as exact_verify    # noqa: E402
from landscape import a3_of_columns                            # noqa: E402
from sources import SOURCES, input_digest, reps_of             # noqa: E402

RESULTS = HERE / "results"
CATALOG = HERE / "catalog"
N38 = REPO / "classification" / "legacy" / "exhaustive_n38" / "catalog" / "classification_n38.json"
CENSUS = REPO / "classification" / "legacy" / "rank7_census" / "catalog" / "sk_classes_r7.json"
LEVEL_GATE = {1: "T", 2: "CS", 3: "CCZ"}
A3_DOC = ("a3: number of 3-sets of injections that pass every check and act on the outputs; "
          "the leading coefficient of the logical error rate, P_fail ~ a3 p^3")


# ---------------------------------------------------------------- gate algebra
def sk_canonical_with_perm(k, mons):
    best, best_perm = None, tuple(range(k))
    for p in permutations(range(k)):
        e = tuple(sorted(tuple(sorted(p[i] for i in Q)) for Q in mons))
        if best is None or e < best:
            best, best_perm = e, p
    return best, best_perm


def sk_canonical(k, mons):
    return sk_canonical_with_perm(k, mons)[0]


def sk_name(canon):
    by_deg = defaultdict(list)
    for Q in canon:
        by_deg[len(Q)].append("".join(map(str, Q)))
    parts = []
    for deg in sorted(by_deg):
        parts += sorted(by_deg[deg])
    return "+".join(parts) if parts else "check-only"


def gate_human(canon):
    parts = []
    for Q in sorted(canon, key=lambda Q: (len(Q), Q)):
        parts.append(LEVEL_GATE.get(len(Q), f"deg{len(Q)}") + "".join(str(i) for i in Q))
    return "·".join(parts) if parts else "(identity)"


def named_from_monomials(mons):
    return " . ".join(
        LEVEL_GATE[len(Q)] + "".join(map(str, sorted(Q)))
        for Q in sorted(mons, key=lambda Q: (len(Q), sorted(Q)))) or "identity"


def monomials_of_columns(columns, k):
    """Odd degree-<=3 output parities of explicit columns."""
    n = len(columns)
    rows = [0] * k
    for j, col in enumerate(columns):
        for i in col:
            if i < k:
                rows[i] |= 1 << j
    from itertools import combinations
    mons = set()
    for d in (1, 2, 3):
        for T in combinations(range(k), d):
            acc = (1 << n) - 1
            for i in T:
                acc &= rows[i]
            if acc.bit_count() & 1:
                mons.add(frozenset(T))
    return frozenset(mons)


# ------------------------------------------------------------------ witnesses
def compact_columns(columns, k):
    """Drop check wires no column touches; outputs keep their labels."""
    used = sorted({q for col in columns for q in col if q >= k})
    remap = {q: k + i for i, q in enumerate(used)}
    return [sorted(q if q < k else remap[q] for q in col) for col in columns]


def canonical_witness(columns, k, mons):
    """Columns relabelled into the canonical S_k output frame."""
    canon, perm = sk_canonical_with_perm(k, mons)
    out = [sorted(perm[q] if q < k else q for q in col) for col in columns]
    if monomials_of_columns(out, k) != frozenset(frozenset(Q) for Q in canon):
        raise SystemExit("canonical relabelling failed")
    return out, canon


def check_witness(w, k, d, mons):
    """'' if the witness is what it claims, else why not."""
    cols = [frozenset(c) for c in w["columns"]]
    if len(set(cols)) != len(cols):
        return "repeated column"
    ok, dist = exact_verify(k, w["N"], cols, mons, dmax=4)
    if not ok:
        return "parity check failed"
    if dist != d:
        return f"distance {dist} != stored {d}"
    if a3_of_columns(w["columns"], k, w["N"]) != w["a3"]:
        return f"a3 recount {a3_of_columns(w['columns'], k, w['N'])} != stored {w['a3']}"
    return ""


# ------------------------------------------------------------------ aggregate
def aggregate(source, results_dir=None):
    """(rows, coverage, digest, problems): one row per class with the per-rank
    landscape of minimum-a3 witnesses; coverage proved, witnesses verified."""
    results_dir = Path(results_dir) if results_dir else RESULTS / source
    reps = reps_of(source)
    digest = input_digest(source)
    problems, coverage = [], {}
    entries = defaultdict(dict)        # (n, k, canon) -> rank -> best entry
    for rep in reps:
        path = results_dir / f"rep_{rep.id}.json"
        if not path.exists():
            problems.append(f"{rep.id}: no result file {path.name}")
            continue
        blob = json.loads(path.read_text(encoding="utf-8"))
        name = path.name
        if blob.get("source") != source:
            problems.append(f"{name}: source={blob.get('source')!r}, not {source!r}")
        if blob.get("input_sha256") != digest:
            problems.append(f"{name}: built from an input with sha256 {blob.get('input_sha256')}, "
                            f"the current one is {digest}")
        if blob.get("rep_id") != rep.id:
            problems.append(f"{name}: is for {blob.get('rep_id')}, not {rep.id}")
        if blob.get("dedup") != "symmetric" or blob.get("distance") != 3:
            problems.append(f"{name}: dedup={blob.get('dedup')!r}, distance={blob.get('distance')!r}")
        if blob.get("node_budget_per_parent") not in (0, None) or blob.get("orbit_budget_per_gate") not in (0, None):
            problems.append(f"{name}: a node or orbit budget was set")
        if blob.get("complete") is not True:
            problems.append(f"{name}: complete={blob.get('complete')!r}")
        geoms = blob.get("geometries", [])
        expected = {(n, origin) for n, origin, _r, _pts in rep.geometries}
        seen = Counter((g["n"], g["origin"]) for g in geoms)
        if set(seen) != expected or any(v != 1 for v in seen.values()):
            problems.append(f"{name}: swept {len(seen)} distinct markings, the representative has "
                            f"{len(expected)} ({len(expected - set(seen))} missing, "
                            f"{len(set(seen) - expected)} foreign, "
                            f"{sum(1 for v in seen.values() if v > 1)} repeated)")
        for g in geoms:
            if g.get("gate_search_complete") is not True:
                problems.append(f"{name}: n={g['n']} origin {g['origin']}: gate search incomplete")
        kmax = blob.get("kmax")
        if kmax is not None:
            hit = [g for g in geoms if g.get("mu", 0) >= kmax]
            if hit:
                problems.append(f"{name}: frame width was capped at {kmax} and {len(hit)} geometries "
                                f"reached the cap, so wider frames may exist")
        for f in blob.get("factories", []):
            k = f["k"]
            mons = frozenset(frozenset(q) for q in f["wants"])
            if len({q for Q in mons for q in Q}) != k:
                problems.append(f"{name}: a stored class leaves an output idle")
                continue
            columns = compact_columns(f["columns"], k)
            columns, canon = canonical_witness(columns, k, mons)
            key = (f["n"], k, canon)
            r = f["r"]
            N = max(max(c) for c in columns) + 1
            if N - k != r:
                problems.append(f"{name}: witness has {N - k} used check wires but rank {r}")
            w = {"rank": r, "N": N, "a3": f["a3"], "a3_max_seen": f["a3_max"],
                 "columns": columns, "d": f["distance"],
                 "source": f"{rep.id}, origin {f['origin']}; {name}"}
            cur = entries[key].get(r)
            if cur is None or w["a3"] < cur["a3"]:
                entries[key][r] = w
            elif w["a3_max_seen"] > cur["a3_max_seen"]:
                cur["a3_max_seen"] = w["a3_max_seen"]
        coverage[rep.id] = {
            "m": rep.m, "geometries": len(geoms), "expected": rep.n_geometries,
            "max_kappa": blob.get("max_kappa"), "max_mu": blob.get("max_mu"),
            "n_classes": blob.get("n_classes"), "seconds": blob.get("seconds"),
        }
    if problems:
        return [], coverage, digest, problems

    rows = []
    for (n, k, canon), by_rank in entries.items():
        mons = frozenset(frozenset(Q) for Q in canon)
        d = min(w["d"] for w in by_rank.values())
        for r, w in by_rank.items():
            if w["d"] != d:
                problems.append(f"[[{n},{k}]] {sk_name(canon)}: distance differs between ranks")
            msg = check_witness(w, k, d, mons)
            if msg:
                problems.append(f"[[{n},{k},{d}]] {sk_name(canon)} rank {r}: {msg}")
        ranks = sorted(by_rank)
        best_rank = min(ranks, key=lambda r: (by_rank[r]["a3"], r))
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
    return rows, coverage, digest, problems


# ------------------------------------------------- comparison with a shipped table
def shipped_rows(source):
    path = N38 if source == "n38" else CENSUS
    blob = json.loads(path.read_text(encoding="utf-8"))
    return path, blob["factories"]


def compare_with_shipped(rows, source):
    """Per class: what the shipped one-witness table kept, against the landscape."""
    path, shipped = shipped_rows(source)
    ours = {(r["n"], r["k"], sk_canonical(r["k"], r["monomials"])): r for r in rows}
    report = {"table": str(path.relative_to(REPO)), "shipped_classes": len(shipped), "here": len(rows),
              "missing_here": [], "extra_here": [], "per_class": []}
    seen = set()
    for s in shipped:
        cols = [sorted(set(c)) for c in s["columns"]]
        k = s["k"]
        mons = monomials_of_columns(cols, k)
        key = (s["n"], k, sk_canonical(k, mons))
        seen.add(key)
        r = ours.get(key)
        if r is None:
            report["missing_here"].append(f"[[{s['n']},{k}]] {s['gate']}")
            continue
        N = max(max(c) for c in cols) + 1
        rank = N - k
        a3 = a3_of_columns(cols, k, N)
        entry = r["landscape"].get(str(rank))
        report["per_class"].append({
            "index": r["index"], "n": s["n"], "k": k, "gate": r["gate"],
            "shipped_rank": rank, "shipped_a3": a3,
            "min_a3_at_shipped_rank": entry["a3"] if entry else None,
            "best_rank": r["best_rank"], "best_a3": r["a3_best"],
            "ranks": r["ranks"],
            "a3_by_rank": {str(k2): v["a3"] for k2, v in sorted(r["landscape"].items(), key=lambda kv: int(kv[0]))},
        })
    for key, r in ours.items():
        if key not in seen:
            report["extra_here"].append(f"[[{r['n']},{r['k']}]] {r['gate']}")
    pc = report["per_class"]
    report["summary"] = {
        "classes_compared": len(pc),
        "shipped_witness_not_min_at_its_rank": sum(1 for c in pc if c["min_a3_at_shipped_rank"] is not None
                                                   and c["shipped_a3"] > c["min_a3_at_shipped_rank"]),
        "shipped_rank_not_in_landscape": sum(1 for c in pc if c["min_a3_at_shipped_rank"] is None),
        "better_a3_at_another_rank": sum(1 for c in pc if c["best_a3"] < c["shipped_a3"] and c["best_rank"] != c["shipped_rank"]),
        "better_a3_anywhere": sum(1 for c in pc if c["best_a3"] < c["shipped_a3"]),
        "classes_at_more_than_one_rank": sum(1 for c in pc if len(c["ranks"]) > 1),
        "best_rank_is_higher_than_shipped": sum(1 for c in pc if c["best_a3"] < c["shipped_a3"] and c["best_rank"] > c["shipped_rank"]),
        "best_rank_is_lower_than_shipped": sum(1 for c in pc if c["best_a3"] < c["shipped_a3"] and c["best_rank"] < c["shipped_rank"]),
    }
    return report


# ------------------------------------------------------------------ rendering
def render(source, rows, coverage, report):
    title = {"n38": "the `n <= 38` classification", "census": "the rank-7 census (`r <= 7`, `n <= 44`)"}[source]
    s = report["summary"]
    L = [f"# Error-coefficient landscape of {title}", ""]
    L.append(f"The shipped table keeps one witness per `(n, k, S_k gate)` class.  This one re-sweeps the "
             f"same parents and keeps, per class and per **check rank**, the witness with the smallest "
             f"leading error coefficient `a3` (undetected, harmful 3-sets of injections: "
             f"`P_fail ~ a3 p^3`).  {len(rows)} classes; every witness re-verified from its columns.")
    L.append("")
    L.append("## What the one-witness table hid")
    L.append("")
    L.append(f"* classes compared with `{report['table']}`: {s['classes_compared']} "
             f"({len(report['missing_here'])} shipped classes missing here, {len(report['extra_here'])} here but not there)")
    L.append(f"* classes occurring at more than one check rank: {s['classes_at_more_than_one_rank']}")
    L.append(f"* classes whose shipped witness is NOT the minimum-`a3` circuit at its own rank: "
             f"{s['shipped_witness_not_min_at_its_rank']}")
    L.append(f"* classes with a strictly smaller `a3` at a different rank: {s['better_a3_at_another_rank']} "
             f"(higher rank: {s['best_rank_is_higher_than_shipped']}, lower rank: {s['best_rank_is_lower_than_shipped']})")
    L.append(f"* classes with a strictly smaller `a3` anywhere: {s['better_a3_anywhere']}")
    L.append("")
    L.append("## Per class")
    L.append("")
    L.append("`a3` by rank lists the minimum coefficient at each check rank the class occurs at; "
             "`shipped` is the rank and coefficient of the witness the shipped table kept.")
    L.append("")
    L.append("| # | [[n,k,d]] | gate | shipped (rank: a3) | best (rank: a3) | a3 by rank |")
    L.append("|---|---|---|---|---|---|")
    for c in report["per_class"]:
        flag = " **<**" if c["best_a3"] < c["shipped_a3"] else ""
        L.append(f"| {c['index']} | `[[{c['n']},{c['k']},3]]` | `{c['gate']}` | {c['shipped_rank']}: {c['shipped_a3']} | "
                 f"{c['best_rank']}: {c['best_a3']}{flag} | "
                 + ", ".join(f"r={r}: {v}" for r, v in c["a3_by_rank"].items()) + " |")
    L.append("")
    L.append("## Coverage")
    L.append("")
    L.append(f"{len(coverage)} representatives, {sum(c['geometries'] for c in coverage.values())} marked "
             f"geometries, all complete, no budget, no width cap (widest frame met "
             f"{max(c['max_mu'] for c in coverage.values())}, largest quotient "
             f"{max(c['max_kappa'] for c in coverage.values())}).")
    L.append("")
    L.append("## Best witness per class and rank")
    L.append("")
    L.append("Output labels first, check labels after; columns in the canonical `S_k` frame.")
    L.append("")
    for r in rows:
        L.append(f"### {r['index']}. `[[{r['n']},{r['k']},{r['d']}]]` — {r['gate_human']}")
        L.append("")
        for rk in r["ranks"]:
            w = r["landscape"][str(rk)]
            L.append(f"- rank {rk} (`N = {w['N']}`): a3 = {w['a3']} (largest seen on this class at this rank: "
                     f"{w['a3_max_seen']}); {w['source']}")
            L.append("")
            L.append("  ```text")
            L.append("  [" + ", ".join("{" + ",".join(map(str, c)) + "}" for c in w["columns"]) + "]")
            L.append("  ```")
            L.append("")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=[s for s in SOURCES if s != "weight40"], required=True)
    a = ap.parse_args()
    rows, coverage, digest, problems = aggregate(a.source)
    if problems:
        for p in problems[:40]:
            print("  -", p)
        raise SystemExit(f"{len(problems)} problem(s) in the {a.source} results")
    n_geoms = sum(c["geometries"] for c in coverage.values())
    print(f"{a.source}: {len(coverage)} representatives, {n_geoms} geometries, all complete; "
          f"{len(rows)} classes, {sum(len(r['ranks']) for r in rows)} (class, rank) witnesses verified")
    report = compare_with_shipped(rows, a.source)
    if report["missing_here"] or report["extra_here"]:
        raise SystemExit(f"class set differs from {report['table']}: missing here {report['missing_here'][:5]}, "
                         f"extra here {report['extra_here'][:5]}")
    print(f"identical class set to {report['table']} ({report['shipped_classes']} classes); "
          f"summary: {report['summary']}")
    name = {"n38": "n38", "census": "census_r7"}[a.source]
    CATALOG.mkdir(exist_ok=True)
    out_json = CATALOG / f"landscape_{name}.json"
    out_md = CATALOG / f"LANDSCAPE_{name.upper()}.md"
    payload = {
        "scope": f"per (n, k, S_k gate) class and per check rank, the minimum-a3 witness over every parent of "
                 f"the {a.source} family; {A3_DOC}",
        "source": a.source, "input_sha256": digest,
        "n_representatives": len(coverage), "n_geometries": n_geoms, "complete": True,
        "coverage": coverage,
        "n_classes": len(rows),
        "comparison_with_shipped": {k: v for k, v in report.items() if k != "per_class"},
        "per_class_comparison": report["per_class"],
        "factories": [{k: v for k, v in r.items() if k != "monomials"} for r in rows],
    }
    out_json.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    out_md.write_text(render(a.source, rows, coverage, report), encoding="utf-8")
    print(f"wrote {out_json.relative_to(HERE)} and {out_md.relative_to(HERE)}")


if __name__ == "__main__":
    main()
