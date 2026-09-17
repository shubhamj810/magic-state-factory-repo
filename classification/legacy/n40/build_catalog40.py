#!/usr/bin/env python3
"""BUILD THE ``n = 39, 40`` CATALOGUE, and the combined ``n <= 40`` one.

Consolidates ``results/weight40/rep_*.json`` (one per weight-40
representative, from ``classify40.py``) into

  * ``catalog/classification_n3940.json``  -- one record per (n, k, S_k gate)
    class at n = 39, 40, every check rank, with the best-coefficient witness
    circuit and the per-rank landscape of best witnesses
  * ``catalog/CLASSIFICATION_N3940.md``     -- the same for humans
  * ``catalog/classification_upto_n40.json`` / ``CLASSIFICATION_UPTO_N40.md``
    -- the shipped ``n <= 38`` classification (``../exhaustive_n38/catalog``,
    74 rows, copied verbatim) followed by the new rows: every distance-3
    factory class with at most 40 injections

WHICH WITNESS A ROW CARRIES
---------------------------
Rows collapse on ``(n, k, gate up to a permutation of the output qubits)``,
the S_k key of both sibling catalogues.  A class typically occurs on parents
of several check ranks, and on many output subspaces of each; those circuits
differ in their leading error coefficient ``a3`` (undetected, harmful 3-sets
of injections; ``P_fail ~ a3 p^3``).  The sweep records, per class and per
rank, the subspace of minimum ``a3``.  The row's ``columns`` is the witness of
minimum ``a3`` over all ranks (ties to the lower rank); ``landscape`` holds
the best witness at every rank the class occurs at, so the fewest-check
circuit is there too (``fewest_checks_rank``).

COVERAGE AND VERIFICATION are ``build_landscape.aggregate``'s: every
representative present with all its markings, complete, no budget, no cap
that bit; every published witness (primary and per rank) relabelled into its
canonical S_k frame, re-checked by ``factorylib.verification.verify`` (gate
parities, check-touching parities even, distance exact to weight 4) and its
``a3`` recounted from the columns.  T-count and reduced degree are recomputed
by ``factorylib.metrics`` for ``k <= 6``; the reduced-degree memo is
redirected to this directory's ``reduced_degree_cache.json`` so building here
writes nothing outside ``classification/legacy/n40``.

Run:  python build_catalog40.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))

from factorylib import metrics as _metrics                    # noqa: E402
_metrics._CACHE_PATH = HERE / "reduced_degree_cache.json"     # never write outside this directory
try:
    _metrics._DEG_CACHE = json.loads(_metrics._CACHE_PATH.read_text(encoding="utf-8"))
except (OSError, ValueError):
    _metrics._DEG_CACHE = {}
from factorylib.metrics import metrics_from_named             # noqa: E402
from build_landscape import A3_DOC, aggregate                 # noqa: E402
from landscape import a3_of_columns                           # noqa: E402
from reps40 import CATALOGUE, EXPECTED_COUNT, validate        # noqa: E402

CATALOG = HERE / "catalog"
N38 = REPO / "classification" / "legacy" / "exhaustive_n38" / "catalog" / "classification_n38.json"
OUT_JSON = CATALOG / "classification_n3940.json"
OUT_MD = CATALOG / "CLASSIFICATION_N3940.md"
ALL_JSON = CATALOG / "classification_upto_n40.json"
ALL_MD = CATALOG / "CLASSIFICATION_UPTO_N40.md"
METRICS_K_CAP = 6          # matches master_catalog/verify_catalog.py


def enrich(row):
    """Metrics from the gate, and the flat fields of the primary witness."""
    k = row["k"]
    if k <= METRICS_K_CAP:
        t_count, t_note, poly_deg, deg_note = metrics_from_named(row["gate_named"])
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


def build():
    problems = validate()
    if problems:
        for p in problems:
            print("  -", p)
        raise SystemExit("the input table did not validate")
    rows, coverage, digest, problems = aggregate("weight40")
    if problems:
        for p in problems[:40]:
            print("  -", p)
        raise SystemExit(f"{len(problems)} problem(s): the result files do not add up to one "
                         f"complete, verified sweep of the 110 representatives")
    n_geoms = sum(c["geometries"] for c in coverage.values())
    print(f"input: {len(coverage)} representatives, {n_geoms} marked geometries, all complete; "
          f"max kappa {max(c['max_kappa'] for c in coverage.values())}, "
          f"max frame width {max(c['max_mu'] for c in coverage.values())}")
    rows = [enrich(r) for r in rows]
    print(f"{len(rows)} distinct (n, k, S_k gate) classes: "
          + ", ".join(f"n={n}: {v}" for n, v in sorted(Counter(r['n'] for r in rows).items()))
          + f"; {sum(len(r['ranks']) for r in rows)} (class, rank) witnesses, every one re-verified "
            f"(factorylib.verification, distance exact to weight 4; a3 recounted)")
    return rows, coverage, digest, n_geoms


def combined_rows(rows):
    """The shipped n <= 38 rows verbatim, then ours, on a common field set."""
    blob = json.loads(N38.read_text(encoding="utf-8"))
    n38 = blob["factories"]
    if len(n38) != blob["n_classes"]:
        raise SystemExit("classification_n38.json disagrees with itself on its row count")
    if any(r["n"] > 38 for r in n38):
        raise SystemExit("classification_n38.json holds a row above n = 38")
    out = []
    for r in n38:
        cols = [sorted(c) for c in r["columns"]]
        out.append({
            "n": r["n"], "k": r["k"], "d": r["d"], "N": r["N"], "r_checks": r["r_checks"],
            "gate": r["gate"], "gate_human": r["gate_human"],
            "t_count": r.get("t_count"), "poly_degree": r.get("poly_degree"),
            "a3": a3_of_columns(cols, r["k"], r["N"]),
            "columns": cols,
            "source": f"exhaustive_n38 ({r.get('source')})",
            "table": "classification/legacy/exhaustive_n38/catalog/classification_n38.json",
        })
    for r in rows:
        out.append({
            "n": r["n"], "k": r["k"], "d": r["d"], "N": r["N"], "r_checks": r["r_checks"],
            "gate": r["gate"], "gate_human": r["gate_human"],
            "t_count": r["t_count"], "poly_degree": r["poly_degree"],
            "a3": r["a3"],
            "columns": r["columns"], "source": r["source"],
            "table": "classification/legacy/n40/catalog/classification_n3940.json",
        })
    out.sort(key=lambda r: (r["n"], r["k"], r["gate"]))
    for i, r in enumerate(out, 1):
        r["index"] = i
    return out, len(n38)


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
                         + ", ".join(f"r={rk}: {r['landscape'][str(rk)]['a3']}" for rk in r["ranks"]) + " |")
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
                L.append(f"- rank {rk} (`N = {w['N']}`), a3 = {w['a3']}; {w['source']}")
                L.append("")
                L.append("  ```text")
                L.append("  " + _circuit(w["columns"]))
                L.append("  ```")
                L.append("")
    return L


def render_n3940(rows, coverage, digest, n_geoms):
    tmax = max(r["t_count"] for r in rows if r["t_count"] is not None)
    multi = sum(1 for r in rows if len(r["ranks"]) > 1)
    improved = sum(1 for r in rows if r["a3"] < r["a3_at_fewest_checks"])
    L = ["# Complete classification at `n = 39` and `n = 40`: every `S_k` class, every check rank", ""]
    L.append(f"**{len(rows)} distinct `(n, k, S_k gate)` classes** of distance-3 factory with 39 or 40 "
             f"injections, at every check rank, each with the witness circuit of smallest leading error "
             f"coefficient and the best witness at every check rank the class occurs at.")
    L.append("")
    L.append(f"`a3` is the number of 3-sets of injections that pass every check and act on the outputs: "
             f"`P_fail ~ a3 p^3` for independent injection errors of rate `p`.  {multi} classes occur at "
             f"more than one check rank; for {improved} of the {len(rows)} the best circuit is not the "
             f"fewest-check one.")
    L.append("")
    L.append("## How it was produced")
    L.append("")
    L.append(f"From the complete affine classification of length-40 no-repeated-column unital "
             f"triorthogonal spaces (`length40_catalogue.json`, sha256 `{digest[:16]}…`, 110 "
             f"representatives): every representative marked at every origin -- 40 on the support "
             f"(n = 39), 2^m - 40 off it (n = 40) and the hyperplane-miss lift (n = 40, rank m + 1) -- "
             f"giving {n_geoms} check parents, each classified completely by `classify40.py` "
             f"(`factorylib.parent` quotient V_3(C), every compatible subspace at every width, one "
             f"witness per S_k class of every GL(k,2) output basis, the witness chosen on the subspace "
             f"of minimum a3).  No budget, no width cap: the widest compatible subspace met was "
             f"k = {max(c['max_mu'] for c in coverage.values())}, the largest quotient dimension "
             f"{max(c['max_kappa'] for c in coverage.values())}.")
    L.append("")
    L.append("## How it was verified")
    L.append("")
    L.append("* `build_catalog40.py` (via `build_landscape.aggregate`) proves the result files sweep every "
             "marking of every representative exactly once, completely; every witness -- the primary one "
             "and the best one at every rank -- is relabelled into its canonical `S_k` frame, re-checked "
             "from its raw columns by `factorylib.verification.verify` (gate parities, all check-touching "
             "parities even, distance exact by enumeration to weight 4) and has its a3 recounted; T-count "
             "and reduced degree recomputed by `factorylib.metrics` for `k <= 6`;")
    L.append("* `verify40.py` re-derives every witness with code sharing nothing with the engine and with "
             "the master catalogue's own bar, and checks completeness: the `r <= 7` slice equals the "
             "rank-7 census table at `n = 39, 40` (both directions), every class of the earlier "
             "quotient-search catalogue (`reference/`) is here, every master-catalogue row at `n = 39, 40` "
             "is here, and -- when the census landscape has been built -- the per-rank minimum a3 at "
             "`r <= 7` agrees with the census parents' exactly.")
    L.append("")
    L.append("## Counts")
    L.append("")
    L += _counts_table(rows)
    L.append("")
    tc = Counter(r["t_count"] for r in rows)
    L.append("T-count histogram: " + ", ".join(
        f"T={t}: {v}" for t, v in sorted(tc.items(), key=lambda x: (x[0] is None, x[0] or 0)))
        + f".  Maximum exact T-count {tmax}.")
    L.append("")
    L.append("## Coverage, per representative")
    L.append("")
    L.append("| representative | m | geometries | max kappa | widest frame | classes | seconds |")
    L.append("|---|---|---|---|---|---|---|")
    for rid, c in sorted(coverage.items(), key=lambda kv: (kv[1]["m"], kv[0])):
        L.append(f"| `{rid}` | {c['m']} | {c['geometries']} | {c['max_kappa']} | {c['max_mu']} | "
                 f"{c['n_classes']} | {c['seconds']} |")
    L.append("")
    L.append("## The classes")
    L.append("")
    L.append("Output labels come first, check labels follow; the columns are in the canonical "
             "`S_k` output frame, so they deposit exactly the gate shown.  `a3 (rank)` is the best "
             "coefficient and the rank of the circuit attaining it; `a3 by rank` the best at each rank.")
    L.append("")
    L += _class_tables(rows)
    L.append("## Witness circuits")
    L.append("")
    L += _witnesses(rows)
    return "\n".join(L) + "\n"


def render_all(rows, n_from_38):
    L = ["# Every distance-3 factory class with at most 40 injections", ""]
    L.append(f"**{len(rows)} distinct `(n, k, S_k gate)` classes**, every check rank, one verified "
             f"witness circuit each: the {n_from_38} rows of the shipped `n <= 38` classification "
             f"(`../../exhaustive_n38/catalog/classification_n38.json`, copied verbatim, a3 computed "
             f"from their columns) followed by the {len(rows) - n_from_38} rows of "
             f"`classification_n3940.json` (best-a3 witnesses).")
    L.append("")
    L.append("No factory exists at n in {17..22, 25, 26}: those lengths host no unital triorthogonal "
             "class (see `../../exhaustive_n38/docs/THEORY_EXHAUSTIVENESS.md`), and none at n = 16 or 24.")
    L.append("")
    L.append("## Counts")
    L.append("")
    L += _counts_table(rows)
    L.append("")
    L.append("## The classes")
    L.append("")
    L += _class_tables(rows, landscape=False)
    L.append("## Witness circuits")
    L.append("")
    L += _witnesses(rows, landscape=False)
    return "\n".join(L) + "\n"


def main():
    rows, coverage, digest, n_geoms = build()
    CATALOG.mkdir(exist_ok=True)
    tmax = max(r["t_count"] for r in rows if r["t_count"] is not None)
    payload = {
        "scope": "every (n, k, S_k gate) class of distance-3 factory with n = 39 or n = 40 injections, "
                 "at every check rank; per class the witness of minimum a3 over all ranks, and the best "
                 "witness at every rank the class occurs at",
        "dedup_key": "S_k: output permutations only (GL(k,2) is coarser and not used)",
        "a3": A3_DOC,
        "input": {"file": CATALOGUE.name, "sha256": digest, "representatives": EXPECTED_COUNT},
        "engine": "classify40.py (factorylib.parent + orbit-memoised S_k classification with the "
                  "minimum-a3 witness per class), no budget, no width cap",
        "n_representatives": len(coverage),
        "n_geometries": n_geoms,
        "max_kappa": max(c["max_kappa"] for c in coverage.values()),
        "max_frame_width_met": max(c["max_mu"] for c in coverage.values()),
        "coverage": coverage,
        "complete": True,
        "n_classes": len(rows),
        "n_class_rank_witnesses": sum(len(r["ranks"]) for r in rows),
        "classes_at_more_than_one_rank": sum(1 for r in rows if len(r["ranks"]) > 1),
        "classes_whose_best_is_not_fewest_checks": sum(1 for r in rows if r["a3"] < r["a3_at_fewest_checks"]),
        "max_k": max(r["k"] for r in rows),
        "t_max": tmax,
        "factories": rows,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_n3940(rows, coverage, digest, n_geoms), encoding="utf-8")
    print(f"wrote {OUT_JSON.relative_to(HERE)} and {OUT_MD.relative_to(HERE)}: {len(rows)} classes, "
          f"{payload['classes_at_more_than_one_rank']} at more than one rank, "
          f"{payload['classes_whose_best_is_not_fewest_checks']} whose best circuit is not the fewest-check one")

    all_rows, n_from_38 = combined_rows(rows)
    all_payload = {
        "scope": "every (n, k, S_k gate) class of distance-3 factory with n <= 40 injections, at every "
                 "check rank: the shipped n <= 38 classification followed by the n = 39, 40 one",
        "dedup_key": payload["dedup_key"],
        "a3": A3_DOC,
        "tables": [str(N38.relative_to(REPO)), str(OUT_JSON.relative_to(REPO))],
        "n_classes": len(all_rows),
        "n_from_n38": n_from_38,
        "n_from_n3940": len(rows),
        "max_k": max(r["k"] for r in all_rows),
        "t_max": max(r["t_count"] for r in all_rows if r["t_count"] is not None),
        "factories": all_rows,
    }
    ALL_JSON.write_text(json.dumps(all_payload, indent=1) + "\n", encoding="utf-8")
    ALL_MD.write_text(render_all(all_rows, n_from_38), encoding="utf-8")
    print(f"wrote {ALL_JSON.relative_to(HERE)} and {ALL_MD.relative_to(HERE)}: {len(all_rows)} classes "
          f"({n_from_38} from n <= 38, {len(rows)} new)")


if __name__ == "__main__":
    main()
