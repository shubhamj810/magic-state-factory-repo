#!/usr/bin/env python3
"""Rebuild the explicit circuit of every level-3 row of the unified search.

    .venv/bin/python borrowed_identities/export_unified.py          # write circuits/
    .venv/bin/python borrowed_identities/export_unified.py --check  # rebuild, compare, write nothing

In October 2026 the Borrowed Identities repository (S. Singh, C. Gidney and
C. Jones, arXiv:2606.28518) replaced its three per-level catalogues with the
output of one unified distance-2 search, copied byte for byte into
``upstream_unified/``.  Three of its tables are read here, level 3 only:

* ``outputs/all_factories.csv`` -- every distinct factory of four stages:
  two-group circuits, shared-check gluing (the earlier symmetry-free search),
  Clifford padding (a CNOT relabelling that spreads the output over more
  wires) and SAT recovery;
* ``outputs/large_sweep.csv`` -- the two-group stage alone, up to 16 circuit
  qubits, one factory per ``(l, k, n)``.  Only rows with ``n <= 4095`` inputs
  are taken (`LARGE_SWEEP_MAX_N`); above that the table reaches ``n = 65534``,
  and the whole of it would take ``master_catalog.json`` past GitHub's 100 MB
  limit on a single file;
* ``outputs/l3_k78_targets.csv`` -- shared-check gluing for every target on
  ``k = 7`` and ``8`` outputs, beyond the main table's ``k``.

Like the earlier catalogues, these list each factory by the parameters that
make it, so the circuits are rebuilt by running the upstream code unmodified:

* every two-group, gluing and padding row of ``all_factories.csv`` comes out of
  ``unified_search.run`` with the parameters the upstream README gives
  (``--kmax 6 --nmax 11 --rmax 4 --relabel 4``).  The function writes a Quirk
  link per row from the row's gates; its ``quirk_url`` hook is pointed at a
  recorder for the run, which is how the gates are kept.  The rows the run
  writes must be exactly the published ones, field for field;
* the three SAT rows need z3, so their circuits are read back from the
  published Quirk links in ``all_factories_with_quirk.csv.zip``.  A link draws
  the factory's rotations and then the Clifford corrections, which use the same
  gates, so the split between the two is found by regenerating the link with
  the upstream ``quirk_url`` for each candidate split: exactly one reproduces
  the published link character for character;
* every large-sweep row is rebuilt as ``large_sweep.py`` builds it at level 3:
  ``Two_group.build_gate_set`` with every sign ``+1``, expanded by
  ``unified_search.two_group_gates``;
* every ``k = 7, 8`` row is rebuilt as ``large_k_sweep.py`` builds it:
  ``symfree_search.solve_binding`` on the row's blocks, with the smallest check
  register (1 to 4) that has a solution.  Its upstream classification must
  give the row's ``n``, ``N``, ``d`` and reduced gate.

Each circuit is then checked against its row by code independent of the
search: its wire count ``N``, its count ``n`` of odd-coefficient rotations
(the ``T`` states it consumes; even ones are Clifford), the borrowed-identity
condition (`bicheck`), the output gate read off the rotations against the
row's ``raw`` column, and the distance, measured by the master catalogue's
fault search.  Any mismatch stops the script.  The error coefficient ``A_d``
is counted too (`errorcoeff`), for comparison with the upstream's own.

OUTPUT
------
``circuits/unified_l3.json``: one entry per distinct circuit -- the gates, the
table and row it reproduces, the stage and parameters, and the measured ``d``,
witness and ``A_d``.  A large-sweep circuit identical to one already listed is
not repeated.

``circuits/factories_unified_l3.json``: the same circuits in the input format
of ``master_catalog/merge_results.py``, credited to the paper (see
``README.md`` for how the merge treats classes already held).

The output is deterministic: ``--check`` rebuilds everything (about two
minutes, most of it the upstream search) and fails if a committed file
differs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import urllib.parse
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
UPSTREAM = HERE / "upstream_unified"
OUT = HERE / "circuits"
sys.path.insert(0, str(UPSTREAM / "searches"))
sys.path.insert(0, str(UPSTREAM / "classification"))
sys.path.insert(0, str(REPO / "master_catalog"))

import unified_search as US                                       # noqa: E402
from Two_group import build_gate_set                              # noqa: E402
from symfree_search import solve_binding                          # noqa: E402
import errorcoeff as EC                                           # noqa: E402
import faultcore as FC                                            # noqa: E402
from bicheck import borrowed_identity_violation, magic            # noqa: E402

LEVEL = 3
REPOSITORY = "https://github.com/shraggy/Magic_state_factory_search"
COMMIT = "46270145dc77643672ee4afbc9ff9f4b48bab083"
CITATION = ("S. Singh, C. Gidney and C. Jones, \"Borrowed Identities: "
            "Malleable Distillation Factories and a Unified Numerical Search,\" "
            "arXiv:2606.28518 (2026)")
BORROWED = "singh2026borrowed"
#: the unified run, as ``outputs/README.md`` gives it (without the SAT stage)
RUN = dict(k_max=6, n_max=11, r_max=4, relabel_max=4)
LARGE_SWEEP_MAX_N = 4095
TABLE_TAGS = {"all_factories.csv": "af", "large_sweep.csv": "ls",
              "l3_k78_targets.csv": "k78"}
#: the columns of ``all_factories.csv`` a rebuilt row must reproduce
COMPARED = ("clifford_class", "l", "k", "n", "N", "d", "search_stage",
            "padded_from", "params", "reduced", "raw", "zcount",
            "essential_dim", "clifford_padded", "masks", "reference")

REGIMES = {
    "two-group": "borrowed-identity search: two-group",
    "gluing": "borrowed-identity search: symmetry-free",
    "padding": "borrowed-identity search: Clifford padding",
    "SAT": "borrowed-identity search: SAT recovery",
}
STRENGTHS = {
    "borrowed-identity search: Clifford padding": (
        "found by the Clifford-padding stage of the unified borrowed-identity "
        "search of Singh, Gidney and Jones (arXiv:2606.28518; "
        "borrowed_identities/): a smaller factory's outputs spread over more "
        "wires by a CNOT relabelling; a verified witness, not a maximum"),
    "borrowed-identity search: SAT recovery": (
        "found by the SAT stage of the unified borrowed-identity search of "
        "Singh, Gidney and Jones (arXiv:2606.28518; borrowed_identities/), "
        "asked for a factory below the circuit size the other stages reach; a "
        "verified witness, not a maximum"),
}


# ------------------------------------------------------------------ tables
def read_table(name):
    with (UPSTREAM / "outputs" / name).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def read_links():
    """The Quirk link of every level-3 SAT row, keyed like `row_key`."""
    csv.field_size_limit(sys.maxsize)
    with zipfile.ZipFile(UPSTREAM / "outputs" /
                         "all_factories_with_quirk.csv.zip") as archive:
        with archive.open("all_factories_with_quirk.csv") as fh:
            rows = list(csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8")))
    return {row_key(r): r["quirk"] for r in rows
            if r["l"] == str(LEVEL) and r["search_stage"] == "SAT"}


def row_key(row):
    return tuple(str(row[name]) for name in COMPARED)


# ---------------------------------------------------- the unified search
def unified_circuits():
    """``{row_key: gates}`` for every row ``unified_search.run`` writes."""
    original = US.quirk_url
    US.quirk_url = lambda gates, n, L, k=None: json.dumps(
        [[sorted(S), int(c)] for S, c in gates])
    try:
        rows = US.run(LEVEL, RUN["k_max"], RUN["n_max"], RUN["r_max"],
                      RUN["relabel_max"], log=lambda *_: None)
    finally:
        US.quirk_url = original
    out = {}
    for row in US.catalogue_rows(rows):
        # the class labels are numbered over every row, the SAT ones included,
        # so they are compared below through the published row instead
        out[row_key({**row, "clifford_class": ""})] = [
            (tuple(S), c) for S, c in json.loads(row["quirk"])]
    return out


# ------------------------------------------------------- SAT, from Quirk
PHASE_UNITS = {"i": (4, 1), "-i": (4, -1), "√i": (8, 1), "√-i": (8, -1)}


def _gates_of_columns(cols, wires):
    """Rotations from Quirk parity columns: consecutive columns on the same
    support are the units of one rotation, ``sign * 2^L / d`` each."""
    gates = []
    for col in cols:
        support = tuple(q for q in range(wires) if col[q] == "zpar")
        gid = col[wires]
        if gid in PHASE_UNITS:
            d, sign = PHASE_UNITS[gid]
        else:
            match = re.fullmatch(r"~ph(\d+)([pm])", gid)
            d, sign = int(match.group(1)), 1 if match.group(2) == "p" else -1
        unit = sign * (1 << LEVEL) // d
        if gates and gates[-1][0] == support:
            gates[-1] = (support, (gates[-1][1] + unit) % (1 << LEVEL))
        else:
            gates.append((support, unit % (1 << LEVEL)))
    return gates


def sat_circuit(link, wires, k):
    """The factory's rotations, recovered from its published Quirk link."""
    spec = json.loads(urllib.parse.unquote(link.split("#circuit=", 1)[1]))
    cols = spec["cols"]
    if cols[0] != ["H"] * wires:
        raise SystemExit("a Quirk link does not open with H on every wire")
    end = cols.index(["Bloch"] * wires)
    found = []
    for split in range(2, end + 1):
        gates = _gates_of_columns(cols[1:split], wires)
        if US.quirk_url([(frozenset(S), c) for S, c in gates],
                        wires, LEVEL, k=k) == link:
            found.append(gates)
    # A correction column moved into the factory regenerates the same link --
    # its monomial is then no longer left over to correct -- so several splits
    # can reproduce it.  Corrections are Clifford: they differ only in
    # even-coefficient rotations, and the T rotations must be the same in all.
    odd = {json.dumps(sorted(S for S, c in gates if c % 2)) for gates in found}
    if not found or len(odd) != 1:
        raise SystemExit(f"{len(found)} splits reproduce the Quirk link, with "
                         f"{len(odd)} different sets of T rotations")
    return found[0]


# ---------------------------------------------------------- large sweep
def large_sweep_circuit(row):
    k, wires = int(row["k"]), int(row["N"])
    pairs, _, _ = build_gate_set(k, wires - k, int(row["s_total"]),
                                 int(row["s_O"]))
    return [(tuple(sorted(S)), c) for S, c in
            US.two_group_gates(k, wires - k, {p: 1 for p in pairs})]


# ------------------------------------------------- k = 7, 8 gluing
def k78_circuit(row):
    parts = [int(p) for p in row["params"].removeprefix("blocks=").split("+")]
    for checks in range(1, 5):
        solution = solve_binding(parts, checks, LEVEL)
        if solution is not None:
            break
    else:
        raise SystemExit(f"blocks {parts}: no check register up to 4 works")
    k = int(row["k"])
    gates = [(tuple(sorted(S)), c % (1 << LEVEL)) for S, c in solution["gates"]]
    info = US.classify_factory(dict(stage="gluing", k=k, r=checks,
                                    gates=[(frozenset(S), c) for S, c in gates],
                                    params=row["params"]), LEVEL)
    got = (info["N"], info["n"], info["d"], info["reduced"])
    want = (int(row["n"]), int(row["N"]), int(row["d"]), row["reduced"])
    if got != want:
        raise SystemExit(f"blocks {parts}: the upstream classification gives "
                         f"{got}, the row says {want}")
    return gates


# ------------------------------------------------------------ the checks
_NAMES = {"T": 1, "CS": 2, "CCZ": 3}


def raw_gate(raw):
    """``\\mathrm{CS}_{12}\\mathrm{T}_{3}`` -> ``{(0, 1), (2,)}``, or None for
    a gate the table abbreviates (``16\\ \\text{terms}``)."""
    if "text{terms}" in raw:
        return None
    terms = re.findall(r"\\mathrm\{(T|CS|CCZ)\}_\{(\d+)\}", raw)
    if "".join(rf"\mathrm{{{g}}}_{{{q}}}" for g, q in terms) != raw:
        raise SystemExit(f"cannot read the gate {raw!r}")
    out = set()
    for name, wires in terms:
        if len(wires) != _NAMES[name]:
            raise SystemExit(f"{name} on {wires} in {raw!r}")
        out.add(tuple(sorted(int(q) - 1 for q in wires)))
    return out


def checked(row, gates, where):
    """Stop unless ``gates`` is the row's factory; return its measurements."""
    k, wires, n, d = (int(row[name]) for name in ("k", "N", "n", "d"))
    problems = []
    if len({S for S, _c in gates}) != len(gates):
        problems.append("repeated support")
    if max(q for S, _c in gates for q in S) + 1 != wires:
        problems.append(f"the rotations do not use {wires} wires")
    odd = magic(gates)
    if len(odd) != n:
        problems.append(f"{len(odd)} odd-coefficient rotations, the row says "
                        f"n={n}")
    bad = borrowed_identity_violation(gates, k, LEVEL)
    if bad is not None:
        problems.append(f"monomial {bad} touches a check with genuine "
                        f"level-{LEVEL} phase")
    columns = [list(gates[i][0]) for i in odd]
    gate = {tuple(sorted(m)) for m in
            FC.recover_gate(FC.rows_over_columns(columns, wires), k)}
    want = raw_gate(row["raw"])
    if want is not None and gate != want:
        problems.append(f"the rotations deposit {sorted(gate)}, the row says "
                        f"{row['raw']}")
    report = FC.distance_report(columns, k, wires, budget=FC.Budget())
    if report["d_exact"] != d:
        problems.append(f"measured distance {report['d_exact']} "
                        f"(at least {report['d_at_least']}), the row says {d}")
    if problems:
        raise SystemExit(f"{where}: " + "; ".join(problems))
    a_d = EC.error_coefficient(columns, k, wires, d)["count"]
    return columns, report["witness"], a_d


# ------------------------------------------------------------- the export
def build():
    published = [(i, r) for i, r in enumerate(read_table("all_factories.csv"), 2)
                 if r["l"] == str(LEVEL)]
    rebuilt = unified_circuits()
    links = read_links()
    entries, seen = [], {}
    for line, row in published:
        key = row_key({**row, "clifford_class": ""})
        if row["search_stage"] == "SAT":
            gates = sat_circuit(links[row_key(row)], int(row["N"]), int(row["k"]))
        elif key in rebuilt:
            gates = rebuilt.pop(key)
        else:
            raise SystemExit(f"all_factories.csv line {line}: the upstream "
                             f"run does not write this row")
        entries.append(entry(row, gates, "all_factories.csv", line, seen))
    if rebuilt:
        raise SystemExit(f"the upstream run writes {len(rebuilt)} row(s) "
                         f"all_factories.csv does not have")
    sweep = [(i, r) for i, r in enumerate(read_table("large_sweep.csv"), 2)
             if r["l"] == str(LEVEL) and int(r["n"]) <= LARGE_SWEEP_MAX_N]
    for line, row in sweep:
        row = {**row, "search_stage": "two-group",
               "params": f"s_total={row['s_total']},s_O={row['s_O']}"}
        made = entry(row, large_sweep_circuit(row), "large_sweep.csv", line, seen)
        if made is not None:
            entries.append(made)
    targets = [(i, r) for i, r in enumerate(read_table("l3_k78_targets.csv"), 2)]
    for line, row in targets:
        row = {**row, "search_stage": "gluing", "raw": row["reduced"]}
        made = entry(row, k78_circuit(row), "l3_k78_targets.csv", line, seen)
        if made is not None:
            entries.append(made)
    return entries, len(published), len(sweep), len(targets)


def entry(row, gates, table, line, seen):
    """One circuit entry, or None for a large-sweep repeat of a listed one."""
    gates = sorted((tuple(sorted(S)), int(c) % (1 << LEVEL)) for S, c in gates)
    ident = (int(row["k"]), json.dumps(gates))
    if ident in seen:
        if table != "all_factories.csv":
            return None
        raise SystemExit(f"{table} line {line} repeats the circuit of "
                         f"{seen[ident]}")
    where = f"{table} line {line}"
    seen[ident] = where
    columns, witness, a_d = checked(row, gates, where)
    return {
        "id": f"{TABLE_TAGS[table]}-{line:04d}",
        "table": table, "line": line,
        "stage": row["search_stage"], "params": row["params"],
        "masks": row.get("masks", ""),
        "k": int(row["k"]), "wires": int(row["N"]), "n": int(row["n"]),
        "d": int(row["d"]), "d_witness": witness, "A_d": a_d,
        "raw": row["raw"], "reference": row.get("reference", ""),
        "gates": [[list(S), c] for S, c in gates],
        "columns": columns,
    }


def merge_record(e):
    regime = REGIMES[e["stage"]]
    record = {
        "k": e["k"], "N": e["wires"], "n": e["n"], "d": e["d"],
        "columns": e["columns"],
        "regime": regime,
        "discovery": "pre-existing",
        "citations": [BORROWED],
        "file": "borrowed_identities/circuits/unified_l3.json",
        "label": e["id"],
        "provenance": (f"unified search l=3, {e['stage']} "
                       f"{e['params']}" + (f" masks={e['masks']}"
                                           if e["masks"] else "")),
        "origin": f"{REPOSITORY} at {COMMIT[:7]}, outputs/{e['table']} "
                  f"line {e['line']}",
    }
    if regime in STRENGTHS:
        record["strength"] = STRENGTHS[regime]
    return record


def one_per_line(head, name, items):
    text = json.dumps(head, indent=1, ensure_ascii=False)[:-2]
    body = ",\n".join("  " + json.dumps(item, ensure_ascii=False,
                                         separators=(",", ":"))
                      for item in items)
    return f"{text},\n \"{name}\": [\n{body}\n ]\n}}\n"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files():
    entries, published, swept, targets = build()
    head = {
        "about": ("Explicit circuits for the level-3 rows of the unified "
                  "borrowed-identity search, rebuilt by "
                  f"borrowed_identities/export_unified.py. Cite {CITATION}."),
        "source": {"repository": REPOSITORY, "commit": COMMIT,
                   "files": {name: sha256(UPSTREAM / "outputs" / name)
                             for name in ("all_factories.csv",
                                          "all_factories_with_quirk.csv.zip",
                                          "large_sweep.csv",
                                          "l3_k78_targets.csv")}},
        "level": LEVEL,
        "rows": {"all_factories.csv": published,
                 f"large_sweep.csv, n <= {LARGE_SWEEP_MAX_N}": swept,
                 "l3_k78_targets.csv": targets},
        "conventions": (
            "n counts the input T states and N the circuit wires, as in the "
            "upstream tables; wires 0..k-1 are the outputs. A gate [support, "
            "c] is the parity rotation by c*pi/8 on its support, c modulo 8; "
            "the odd-c gates consume T states and are the columns, and even-c "
            "gates are Clifford. d is measured here over the columns, with "
            "d_witness an undetectable damaging fault of that weight, and A_d "
            "is the number of such faults. A circuit of the other two tables "
            "identical to an all_factories.csv one is listed once, under the "
            "latter."),
    }
    return {
        OUT / "unified_l3.json": one_per_line(head, "circuits", entries),
        OUT / "factories_unified_l3.json": one_per_line({
            "about": ("The circuits of unified_l3.json in the input format of "
                      "master_catalog/merge_results.py, all_factories.csv "
                      "first, then the large sweep, then k = 7, 8."),
        }, "results", [merge_record(e) for e in entries]),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="rebuild and compare with the files on disk")
    args = parser.parse_args(argv)
    built = files()
    if args.check:
        stale = [path for path, text in built.items()
                 if not path.exists() or path.read_text(encoding="utf-8") != text]
        for path in stale:
            print(f"differs: {path.relative_to(REPO)}")
        print("up to date" if not stale else f"{len(stale)} file(s) differ")
        return 1 if stale else 0
    OUT.mkdir(exist_ok=True)
    for path, text in built.items():
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
