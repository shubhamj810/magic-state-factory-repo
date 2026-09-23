#!/usr/bin/env python3
"""BUILD THE r <= 7 CENSUS CATALOGUE.

Consolidates the census results in ``results/`` into

  * ``catalog/census_r7.json`` -- machine-readable, one record per class
  * ``catalog/CENSUS_R7.md``   -- the same for humans, with explicit circuits

WHAT GOES IN
------------
1. ``results/high_tcount_subframes_REPS.json`` -- the representatives that
   realise the census MAXIMUM exact T count.  These are the headline result of
   the r <= 7 window: across every check code of effective rank at most 7 and
   every n <= 44, the largest exact minimal T count any factory deposits is 5,
   and it is attained only at n = 43.  Each representative carries explicit
   columns.
2. Any ``results/census_*.json`` produced by ``cli.py census``.  A run is folded
   in only if it is a certificate for the whole window: untruncated, unrestricted,
   swept to ``--kmax 4`` at ``--dedup symmetric`` over every one of the 9,088
   marked geometries (recounted here from the orbit table, not read from the
   file).  Anything else is reported and skipped, because merging budget-limited
   or coarsely deduplicated search output into a catalogue labelled "census" is
   exactly the misreading this repository tries to make impossible.  See
   ``_certificate_problems``.

DEDUPLICATION
-------------
Rows collapse on ``(n, k, gate up to a permutation of the output qubits)`` --
the same S_k key as the sibling n <= 38 catalogue, so the two tables can be
compared row for row.  See ``../exhaustive_n38/dedup.py`` for why S_k.

VERIFICATION
------------
Every circuit-bearing row is re-checked from its raw columns by
``factorylib.verification`` (exact fault enumeration, no shared code with the
census engine) and its exact T count is recomputed by ``factorylib.metrics``.
The build aborts if any row fails.

Run:  python build_catalog.py            (from anywhere; seconds)
"""
import glob
import json
import os
import sys
from collections import defaultdict
from itertools import permutations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))          # run from anywhere: siblings by bare name
sys.path.insert(0, str(HERE.parents[1]))  # shared factorylib package

from factorylib.metrics import metrics_from_named             # noqa: E402
from factorylib.verification import verify as exact_verify    # noqa: E402
# The census window and the marked-geometry count come from the engine itself, so
# the validator below cannot drift away from what `cli.py census` sweeps.
from rank7 import (DEFAULT_DATA, WINDOW_NMAX, count_parents,    # noqa: E402
                   data_digest, window_scope_problems)

RESULTS = HERE / "results"
CATALOG = HERE / "catalog"

LEVEL_GATE = {1: "T", 2: "CS", 3: "CCZ"}


# ---------------------------------------------------------------- gate algebra
def named_to_monomials(named):
    """``'T2 . CS12 . CCZ012'`` -> ``{frozenset({2}), frozenset({1,2}), ...}``."""
    if not named or named.startswith("identity"):
        return frozenset()
    out = set()
    for tok in named.split("."):
        digits = [ch for ch in tok.strip() if ch.isdigit()]
        if digits:
            out.add(frozenset(int(ch) for ch in digits))
    return frozenset(out)


def sk_canonical_with_perm(k, mons):
    """``(S_k-canonical encoding, a permutation attaining it)``.

    The permutation is what lets a witness circuit be relabelled INTO the
    canonical frame, so that its published columns deposit exactly the published
    ``gate`` instead of an S_k-equivalent labelling of it.  Same contract as the
    sibling n <= 38 catalogue (see ``../exhaustive_n38/build_catalog.py``,
    ``canonicalise_columns``).
    """
    best, best_perm = None, tuple(range(k))
    for p in permutations(range(k)):
        e = tuple(sorted(tuple(sorted(p[i] for i in Q)) for Q in mons))
        if best is None or e < best:
            best, best_perm = e, p
    return best, best_perm


def sk_canonical(k, mons):
    """S_k-canonical encoding (output permutations only) -- the dedup key."""
    return sk_canonical_with_perm(k, mons)[0]


def sk_name(canon):
    """Readable, degree-major label of an sk_canonical encoding."""
    by_deg = defaultdict(list)
    for Q in canon:
        by_deg[len(Q)].append("".join(map(str, Q)))
    parts = []
    for deg in sorted(by_deg):
        parts += sorted(by_deg[deg])
    return "+".join(parts) if parts else "check-only"


def gate_human(canon):
    """``((2,),(1,2))`` -> ``'T2·CS12'``."""
    parts = []
    for Q in sorted(canon, key=lambda Q: (len(Q), Q)):
        parts.append(LEVEL_GATE.get(len(Q), f"deg{len(Q)}")
                     + "".join(str(i) for i in Q))
    return "·".join(parts) if parts else "(identity)"


def named_from_monomials(mons):
    """Monomial set -> the '.'-joined named form gate_metrics expects."""
    return " . ".join(
        LEVEL_GATE[len(Q)] + "".join(map(str, sorted(Q)))
        for Q in sorted(mons, key=lambda Q: (len(Q), sorted(Q)))) or "identity"


# -------------------------------------------------------------------- loading
def _t5_source(r):
    """Provenance string for one stored T = 5 witness.

    Two kinds of record live in the file, and both name where they came from:
    the census sweep records the ``RM(3,7)`` orbit class and marked origin they
    were found at, while the witnesses transcribed from
    ``docs/HIGH_TCOUNT_FACTORY_WITNESSES.md`` carry the run label of the
    completed all-origin census instead.  Neither is invented: a record without
    orbit coordinates says so rather than borrowing someone else's.
    """
    if "class_index" in r and "origin" in r:
        return (f"RM(3,7) orbit class {r['class_index']}, origin {r['origin']}; "
                f"high_tcount_subframes_REPS.json")
    if r.get("provenance"):
        return f"{r['provenance']}; high_tcount_subframes_REPS.json"
    raise ValueError(
        f"T=5 witness [[{r.get('n')},{r.get('k')},3]] has no provenance: give it "
        f"either class_index+origin or a provenance string")


def load_t5_representatives():
    """The census-maximum (T = 5) witnesses."""
    path = RESULTS / "high_tcount_subframes_REPS.json"
    if not path.exists():
        return []
    out = []
    for r in json.loads(path.read_text(encoding="utf-8")):
        mons = named_to_monomials(r["gate"])
        out.append({
            "n": r["n"], "k": r["k"], "d": 3,
            "k_essential": r.get("k_essential"),
            "monomials": mons,
            "columns": r["columns"],
            "stored_tcount": r.get("tcount"),
            "source": _t5_source(r),
        })
    return out


#: A census run may only be folded in if it swept the whole window at least
#: this wide.  The published frontier rests on the documented full-census
#: command, which uses --kmax 4; a narrower complete run is complete only for
#: the widths it enumerated, and silently mixing it in would understate the
#: frontier at k > kmax.
REQUIRED_KMAX = 4

#: The dedup key a census run must have used.  This catalogue's key is S_k, and
#: GL(k,2) is strictly COARSER: a gl-deduped run keeps one representative per GL
#: orbit, so distinct S_k classes inside one orbit never reach the file at all.
#: Folding such a run in loses rows silently -- exactly how the frontier came to
#: list 10 classes where the S_k count is 21.  `cli.py census --dedup gl` is a
#: fine exploratory mode; it is not an input for this table.
REQUIRED_DEDUP = "symmetric"


def _certificate_problems(blob):
    """Why this census file may NOT be folded into the catalogue ([] if it may).

    ``complete`` alone is not enough to trust a file with.  Before this check a
    one-parent run -- ``--class-index 306 --origin 0`` -- wrote ``complete:
    true`` with a scope string naming the whole window, and the builder took it,
    so a restricted run could rewrite the published frontier.  ``rank7.py`` now
    records what it actually swept; this validates those fields rather than a
    single boolean.
    """
    problems = []
    if not isinstance(blob, dict):
        return [f"the file holds a {type(blob).__name__}, not an object"]
    if blob.get("dedup") != REQUIRED_DEDUP:
        problems.append(
            f"dedup={blob.get('dedup')!r}, not {REQUIRED_DEDUP!r}: GL(k,2) is "
            f"coarser than this catalogue's S_k key, so such a run cannot have "
            f"recorded every S_k class it saw")
    # `is not True`, not falsiness: these are the flags the whole certificate
    # turns on, so `1`, `"yes"` or a missing value are schema errors rather than
    # things to interpret generously.
    if blob.get("complete") is not True:
        reasons = blob.get("incomplete_reasons")
        problems.append(f"complete={blob.get('complete')!r}, not true"
                        + (f" ({'; '.join(str(r) for r in reasons)})"
                           if isinstance(reasons, list) and reasons else ""))
    # A run records WHY it finished as well as that it did.  Both of these are
    # written by rank7.py and neither was read here, so a file could claim
    # complete=true while its own fields recorded a truncated or capped sweep.
    # Absence is not consent, here as in the n<=38 builder: a file that does not
    # say it finished untruncated has not said it, and every producer since the
    # completeness fix writes both fields.
    if blob.get("untruncated") is not True:
        problems.append(f"untruncated={blob.get('untruncated')!r}, not true: "
                        f"the sweep did not record finishing without hitting a "
                        f"budget, whatever `complete` says")
    if blob.get("stopped_by_max_parents") is not False:
        problems.append(f"stopped_by_max_parents="
                        f"{blob.get('stopped_by_max_parents')!r}, not false: "
                        f"the sweep did not record running to the end of the "
                        f"geometry list")
    if blob.get("incomplete_reasons"):
        problems.append(f"complete=true but incomplete_reasons is non-empty "
                        f"({blob['incomplete_reasons']}): the file contradicts "
                        f"itself")
    # The scope is RECOMPUTED from what the run recorded about itself, with the
    # same function the producer used to set the flag.  Reading
    # `covers_full_window` was believing a boolean: a file could declare true
    # while its own restrictions said class_indices=[306], origins=[0],
    # max_parents=1, mode='reps' or a narrower nmax, and all five of those
    # contradictions were accepted as full-window certificates.
    restrictions = blob.get("restrictions")
    scope = window_scope_problems(restrictions)
    problems += scope
    if not isinstance(restrictions, dict):
        # window_scope_problems has already said what is wrong with it; this
        # keeps the lookups below total, so a list or a string in that field
        # cannot turn a clean rejection into an AttributeError.
        restrictions = {}
    else:
        if "covers_full_window" not in blob:
            problems.append("no `covers_full_window` field: written by a "
                            "rank7.py predating the scope fix")
        elif not isinstance(blob["covers_full_window"], bool):
            problems.append(f"covers_full_window="
                            f"{blob['covers_full_window']!r} is not a boolean")
        elif not blob["covers_full_window"] and not scope:
            problems.append("covers_full_window=false, though the recorded "
                            "restrictions do cover the window: the file "
                            "contradicts itself")
        # Duplicated fields must agree, or the file tells two stories and only
        # the weaker one can be trusted.
        for field in ("mode", "nmax", "kmax"):
            if field in blob and field in restrictions \
                    and blob[field] != restrictions[field]:
                problems.append(
                    f"{field}={blob[field]!r} at top level but "
                    f"{restrictions[field]!r} under restrictions")
    kmax = restrictions.get("kmax", blob.get("kmax"))
    if not isinstance(kmax, int) or isinstance(kmax, bool):
        problems.append(f"kmax={kmax!r} is not an integer")
    elif kmax < REQUIRED_KMAX:
        problems.append(f"kmax={kmax}, below the documented full census's "
                        f"{REQUIRED_KMAX}")
    integrity = blob.get("data_integrity")
    if not isinstance(integrity, dict) or integrity.get("valid") is not True:
        problems.append(
            f"data_integrity.valid is not true "
            f"({integrity.get('valid')!r})" if isinstance(integrity, dict)
            else f"data_integrity is {type(integrity).__name__}, not an object")
    # A run may sweep WIDER than the window and still certify it; its extra rows
    # are dropped in load_census_runs, because the scope string says n <= 44 and
    # has to stay true.  A run that swept NARROWER cannot certify the window.
    nmax = restrictions.get("nmax", blob.get("nmax"))
    if not isinstance(nmax, int) or isinstance(nmax, bool):
        nmax = None                        # window_scope_problems said why
    elif nmax < WINDOW_NMAX:
        problems.append(f"nmax={nmax}, below the window's {WINDOW_NMAX}")
    # The geometry count is not taken on the file's word: it is recomputed here
    # from the bundled orbit table (a fifth of a second) and must match what the
    # run says it visited.  A file with `geometries_expected: null` used to skip
    # this check entirely, which is the one check that catches a restricted run
    # whose other fields were edited to look unrestricted.
    expected = blob.get("geometries_expected")
    processed = blob.get("processed_parents")
    # The table is identified by content.  A census is cluster-scale, so its
    # certificate is written on one machine and read in a checkout on another,
    # and an absolute path recorded there resolves to nothing here -- the
    # recount would fail on a certificate that is perfectly good.  The digest
    # travels, and it is the stronger check anyway: it pins WHICH table was
    # swept, which a path never did.
    digest = blob.get("data_sha256")
    if digest is None:
        problems.append("no `data_sha256` field: written by a rank7.py "
                        "predating the portable-certificate fix, so which orbit "
                        "table it swept is unknown")
    elif not isinstance(digest, str) or len(digest) != 64 \
            or any(c not in "0123456789abcdef" for c in digest.lower()):
        # Slicing a non-string to build the message below crashed the validator
        # instead of rejecting the file.  Every field here is untrusted input.
        problems.append(f"data_sha256 is not a SHA-256 hex digest "
                        f"({type(digest).__name__})")
    elif digest.lower() != data_digest(DEFAULT_DATA):
        problems.append(
            f"data_sha256={digest[:16]}... is not the bundled orbit table "
            f"({blob.get('data_name')}); see data/README.md")
    try:
        recomputed = count_parents(DEFAULT_DATA, nmax) \
            if isinstance(nmax, int) else None
    except (OSError, ValueError) as error:
        recomputed = None
        problems.append(f"cannot recount marked geometries: {error}")
    if recomputed is not None:
        if expected != recomputed:
            problems.append(
                f"geometries_expected={expected}, but the orbit table gives "
                f"{recomputed} marked geometries at nmax={nmax}")
        if processed != recomputed:
            problems.append(f"visited {processed} of {recomputed} marked "
                            f"geometries")
    elif expected is None or processed != expected:
        problems.append(f"visited {processed} of {expected} marked geometries")
    return problems


def load_census_runs():
    """Full-window `cli.py census` certificates; anything else is skipped loudly."""
    out = []
    for path in sorted(glob.glob(str(RESULTS / "census_*.json"))):
        blob = json.loads(Path(path).read_text(encoding="utf-8"))
        name = os.path.basename(path)
        problems = _certificate_problems(blob)
        if problems:
            print(f"  SKIP {name}: not a full-window certificate")
            for problem in problems:
                print(f"        - {problem}")
            continue
        beyond = 0
        for f in blob.get("factories", []):
            cols = f.get("columns")
            if cols is None:
                continue
            if f["n"] > WINDOW_NMAX:
                beyond += 1        # a wider sweep certifies this window, but
                continue           # its extra rows belong to a wider table

            out.append({
                "n": f["n"], "k": f["k"], "d": f.get("distance", 3),
                "k_essential": f.get("k_essential"),
                "monomials": named_to_monomials(f.get("gate", "")),
                "columns": cols,
                "stored_tcount": f.get("tcount"),
                "source": name,
            })
        if beyond:
            print(f"  {name}: {beyond} row(s) with n > {WINDOW_NMAX} set aside "
                  f"(this table's window is n <= {WINDOW_NMAX})")
    return out


# ------------------------------------------------------------------ the build
def enrich(rec):
    """Add derived fields and recompute the metrics from the gate.

    The witness is relabelled into its canonical output frame first, so the
    published ``columns`` deposit exactly the published ``gate``.  Relabelling
    output wires leaves n, N, every check parity and the fault distance alone.
    """
    k = rec["k"]
    canon, perm = sk_canonical_with_perm(k, rec["monomials"])
    columns = [sorted(perm[q] if q < k else q for q in column)
               for column in rec["columns"]]
    monomials = frozenset(frozenset(perm[i] for i in Q) for Q in rec["monomials"])
    named = named_from_monomials(monomials)
    if sk_name(tuple(sorted(tuple(sorted(Q)) for Q in monomials))) != sk_name(canon):
        raise SystemExit(f"canonical relabelling failed on {named}")
    t_count, t_note, poly_deg, deg_note = metrics_from_named(named)
    out = {
        "n": rec["n"], "k": k, "d": rec["d"],
        "N": max(max(c) for c in columns) + 1,
        "gate": sk_name(canon),
        "gate_human": gate_human(canon),
        "gate_named": named,
        "k_essential": rec.get("k_essential"),
        "t_count": t_count,
        "poly_degree": poly_deg,
        "columns": columns,
        "source": rec["source"],
    }
    out["r_checks"] = out["N"] - k
    if t_note:
        out["t_count_note"] = t_note
    if deg_note:
        out["poly_degree_note"] = deg_note
    if rec.get("stored_tcount") is not None and t_count != rec["stored_tcount"]:
        raise SystemExit(f"T-count mismatch on {named}: recomputed {t_count} "
                         f"vs stored {rec['stored_tcount']}")
    return out


def reverify(row):
    """Exact parity + fault-distance re-check from the raw columns."""
    cols = [frozenset(c) for c in row["columns"]]
    mons = named_to_monomials(row["gate_named"])
    ok, dist = exact_verify(row["k"], row["N"], cols, mons, dmax=4)
    if not ok:
        return "parity check failed"
    dval = dist if isinstance(dist, int) else 5
    if dval != row["d"]:
        return f"distance {dist} != stored {row['d']}"
    return ""


def build():
    print("inputs:")
    raw = load_t5_representatives()
    print(f"  high_tcount_subframes_REPS.json: {len(raw)} representatives")
    runs = load_census_runs()
    if runs:
        print(f"  census_*.json: {len(runs)} circuit-bearing records")
    raw += runs
    if not raw:
        raise SystemExit(f"no census results in {RESULTS}")

    best = {}
    for rec in raw:
        row = enrich(rec)
        key = (row["n"], row["k"], row["gate"])
        if key not in best or row["N"] < best[key]["N"]:
            best[key] = row

    # This catalogue is the census MAXIMUM-T frontier, so it holds the classes
    # attaining that maximum and nothing else.  A full census run reports every
    # gate it found, most of them far below the maximum, and folding those in
    # unfiltered would put low-T rows in a table titled "maximum-T witnesses".
    # The maximum is taken from the data rather than hardcoded: if a genuine
    # full-window certificate ever exceeds the stored witnesses' T = 5, that is
    # a new result and it is announced, not silently averaged in.
    everything = sorted(best.values(), key=lambda r: (r["k"], r["n"], r["gate"]))
    tmax = max(r["t_count"] for r in everything)
    stored_max = max((r["stored_tcount"] for r in raw
                      if r.get("stored_tcount") is not None), default=None)
    if stored_max is not None and tmax > stored_max:
        print(f"\n*** the census maximum exact T-count is {tmax}, above the "
              f"{stored_max} of the stored witnesses: a NEW frontier. The "
              f"headline claim and its documentation need updating. ***")
    rows = [r for r in everything if r["t_count"] == tmax]
    dropped = len(everything) - len(rows)
    print(f"\n{len(raw)} records read -> {len(everything)} distinct "
          f"(n, k, S_k gate) classes")
    if dropped:
        print(f"  {dropped} below the census maximum T = {tmax} and therefore "
              f"not part of this frontier catalogue")
    print(f"  {len(rows)} classes attain T = {tmax}")

    fails = [(r, reverify(r)) for r in rows]
    bad = [(r, m) for r, m in fails if m]
    print(f"{len(rows) - len(bad)}/{len(rows)} circuits independently re-verified")
    if bad:
        for r, m in bad:
            print(f"  FAIL [[{r['n']},{r['k']},{r['d']}]] {r['gate']}: {m}")
        raise SystemExit("census catalogue build aborted")
    return rows


def render_markdown(rows):
    lines = []
    A = lines.append
    tmax = max(r["t_count"] for r in rows)
    A("# The `r ≤ 7`, `n ≤ 44` census — maximum-T witnesses")
    A("")
    A("Generated by [`build_catalog.py`](../build_catalog.py) from")
    A("[`../results/`](../results/) — **do not edit by hand**. Machine-readable")
    A("companion: [`census_r7.json`](census_r7.json).")
    A("")
    A("## The window")
    A("")
    A("This catalogue closes a window cut by the number of **check qubits**, not")
    A("by the T-count: every factory whose check code has effective rank `r ≤ 7`,")
    A("for any `n ≤ 44`. The sibling directory")
    A("[`../../exhaustive_n38/`](../../exhaustive_n38/) closes the complementary")
    A("window — *every* rank, but only `n ≤ 38`.")
    A("")
    A("The outer enumeration is complete because the rank-≤7 triorthogonal check")
    A("supports are exactly the codewords of `RM(3,7)`, and Gillot–Langevin")
    A("classified those: 3,486 `AGL(7,2)` orbit representatives, of which 71 have")
    A("nonzero weight ≤ 44. Sweeping all 128 markings of each covers effective")
    A("ranks 4–7 in one pass.")
    A("")
    A("## Headline")
    A("")
    A(f"- Across the whole window the **maximum exact minimal T-count is "
      f"T = {tmax}**, and it is attained only at `n = 43`.")
    A(f"- **{len(rows)} distinct `(n, k, S_k gate)` classes** realise it, every")
    A("  one with an explicit verified circuit. This is every T-count-5 class the")
    A("  census produced: the sweep's own representatives and the witnesses")
    A("  written out in [`../docs/HIGH_TCOUNT_FACTORY_WITNESSES.md`](../docs/HIGH_TCOUNT_FACTORY_WITNESSES.md)")
    A("  are both folded in here and deduplicated under the same `S_k` key as the")
    A("  rest of the repository, so no witness we found is left unaccounted for.")
    A("")
    A("The two halves of that statement have different provenance. That")
    A(f"T = {tmax} **is reached** is certified by the explicit circuits below:")
    A("every one is re-derived from its columns by this builder and by the")
    A("tests. That it is **never exceeded** rests on a completed all-origin")
    A("census run whose output is too large to ship; it is recorded by")
    A("SHA-256, with its geometry count and mode, in")
    A("[`../../exhaustive_n38/results/n38_k56_certificate.json`](../../exhaustive_n38/results/n38_k56_certificate.json)")
    A("(`proof_partition.rank_le_7.completed_run_provenance`). What is local")
    A("and cheap is the outer enumeration: the `2^64` orbit-size identity and")
    A("the 9,088 marked geometries, both covered by the tests. See")
    A("[`../README.md`](../README.md), \"What ships, and what the headline")
    A("rests on\".")
    A("")
    A("## Deduplication")
    A("")
    A("Rows collapse on `(n, k, gate up to a permutation of the output qubits)` —")
    A("the same **S_k** key as the `n ≤ 38` catalogue, so the two tables are")
    A("directly comparable. See")
    A("[`../../exhaustive_n38/dedup.py`](../../exhaustive_n38/dedup.py).")
    A("")
    A("## Table")
    A("")
    A("| `[[n,k,d]]` | N | gate | human | T | deg | source |")
    A("|---|---|---|---|---|---|---|")
    for r in rows:
        A(f"| [[{r['n']},{r['k']},{r['d']}]] | {r['N']} | `{r['gate']}` | "
          f"`{r['gate_human']}` | {r['t_count']} | {r['poly_degree']} | "
          f"{r['source']} |")
    A("")
    A("## Circuits")
    A("")
    A("Columns are the qubit supports of each parity-`T` rotation; qubits")
    A("`0..k-1` are the outputs, the rest are postselected checks.")
    A("")
    for i, r in enumerate(rows, 1):
        A(f"### {i}. `[[{r['n']},{r['k']},{r['d']}]]` — {r['gate_human']}")
        A("")
        A(f"- output gate (phase polynomial): `{r['gate']}`")
        A(f"- exact minimal T-count = {r['t_count']}, reduced degree = "
          f"{r['poly_degree']}")
        A(f"- N = {r['N']}, checks = {r['r_checks']}")
        if r.get("k_essential") is not None and r["k_essential"] != r["k"]:
            A(f"- essential output width = {r['k_essential']}")
        A(f"- source: {r['source']}")
        A("")
        A("```")
        A("[" + ", ".join("{" + ",".join(str(i) for i in sorted(c)) + "}"
                          for c in r["columns"]) + "]")
        A("```")
        A("")
    return "\n".join(lines)


def main():
    rows = build()
    CATALOG.mkdir(parents=True, exist_ok=True)
    payload = {
        "scope": "r <= 7, n <= 44 check-parent census: the classes realising "
                 "the census maximum exact minimal T-count",
        "dedup_key": "(n, k, S_k-canonical gate) -- output-qubit PERMUTATIONS "
                     "only, matching ../exhaustive_n38",
        "outer_enumeration": "all 3,486 AGL(7,2) orbit representatives of "
                             "RM(3,7) (Gillot-Langevin), 71 of nonzero weight "
                             "<= 44, all 128 markings each",
        "max_t_count": max(r["t_count"] for r in rows),
        "n_classes": len(rows),
        "factories": rows,
    }
    out_json = CATALOG / "census_r7.json"
    with open(out_json, "w") as fh:
        json.dump(payload, fh, indent=1)
        fh.write("\n")
    out_md = CATALOG / "CENSUS_R7.md"
    out_md.write_text(render_markdown(rows))
    print(f"\n  -> {out_json.relative_to(HERE)}")
    print(f"  -> {out_md.relative_to(HERE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
