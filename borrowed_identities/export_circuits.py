#!/usr/bin/env python3
"""Rebuild the explicit circuit of every row of the borrowed-identity catalogue.

    .venv/bin/python borrowed_identities/export_circuits.py          # write circuits/
    .venv/bin/python borrowed_identities/export_circuits.py --check  # rebuild, compare, write nothing

The upstream catalogue (``upstream/outputs/factory_catalogue_l{2,3,4}.csv``, from
S. Singh, C. Gidney and C. Jones, "Borrowed Identities", arXiv:2606.28518) lists
each factory by the search parameters that produce it, not by its circuit.  This
script runs the upstream search code, unmodified, on those parameters and writes
the circuit each row names:

* a **two-group** row is rebuilt from ``(l, n, k, s_total, s_O)`` with
  ``Two_group.build_gate_set`` and the first sign assignment
  ``Two_group.find_valid_signs`` returns, then the output-only gate types are
  removed, exactly as ``upstream/classification/export_circuit.py`` does;
* a **symmetry-free** row is rebuilt from ``(l, parts, n - k)`` with
  ``symfree_search.solve_binding``;
* a row both searches found (``search = two-group + symmetry-free``) prints only
  the two-group parameters, so its symmetry-free circuit is rebuilt the way
  ``symfree_search.search`` finds it: the output blocks read off the row's
  ``decomposition``, and the smallest check register (1 to 4) whose solution is
  distance 2 with non-Clifford output.

Every circuit is then checked against its row, independently of the search that
built it: the gate count ``N`` (gates with an odd coefficient; even ones are
lower-level rotations the paper counts as free), the wire count ``n`` and the
borrowed-identity condition itself -- every monomial that touches a check wire
has a coefficient divisible by ``2^size`` at level ``l``.  Any mismatch stops the
script.  The distance is then MEASURED with the master catalogue's fault search
(``master_catalog/faultcore.py``): weights below ``d`` swept clean, and an
undetectable damaging fault exhibited at ``d``.  Where that disagrees with the
row's printed ``d`` the measurement is stored and the disagreement is listed in
``README.md``; it is never silently replaced.

OUTPUT
------
``circuits/circuits_l{2,3,4}.json``: one entry per circuit, with the gate list
(qubit support and coefficient modulo ``2^l``), the parameters that build it,
the row of the upstream CSV it reproduces, and the measured distance with its
witness.

``circuits/factories_l3.json``: the level-3 circuits in the input format of
``master_catalog/merge_results.py`` -- one column per odd-coefficient gate,
outputs ``0..k-1`` -- with each record's regime, provenance and citations.  The
citations follow `LITERATURE` below; see ``README.md``.  Levels 2 and 4 are not
written there: the master catalogue holds level-3 factories only.

Run with the repository's Python 3.12 environment (the upstream code needs
NumPy and Matplotlib, both in ``requirements.txt``).  The output is
deterministic: ``--check`` rebuilds everything and fails if a committed file
differs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
UPSTREAM = HERE / "upstream"
OUT = HERE / "circuits"
sys.path.insert(0, str(UPSTREAM / "searches"))
sys.path.insert(0, str(UPSTREAM / "classification"))
sys.path.insert(0, str(REPO / "master_catalog"))

import Two_group as TG                                            # noqa: E402
import symfree_search as SF                                       # noqa: E402
import faultcore as FC                                            # noqa: E402

LEVELS = (2, 3, 4)
REPOSITORY = "https://github.com/shraggy/Magic_state_factory_search"
COMMIT = "cae49828ed9ab9c1079c7cdf66c5bd337b027515"
PAPER = "https://arxiv.org/abs/2606.28518"
CITATION = ("S. Singh, C. Gidney and C. Jones, \"Borrowed Identities: "
            "Malleable Distillation Factories and a Unified Numerical Search,\" "
            "arXiv:2606.28518 (2026)")

#: The master-catalogue reference key for the paper.  A record names it when
#: no earlier work published the class; otherwise it names the earliest
#: publication alone (`LITERATURE`).
BORROWED = "singh2026borrowed"

#: Earlier publications of a level-3 factory the paper recovers, keyed by
#: ``(N, k, d, decomposition)`` as the upstream CSV writes them, with ``where``
#: saying where the parameters are printed.  Most are the paper's own
#: attributions; two come from reading Campbell and Howard, whose Examples IV.2
#: and IV.3 print the [[14,6,2]] and [[18,4,2]] protocols explicitly.  For the
#: 8 T -> CCZ factory the Jones paper is Phys. Rev. A 87, 022328, "Low-overhead
#: constructions for the fault-tolerant Toffoli gate" (arXiv:1212.5069, titled
#: there "Novel constructions ..."), the one Eastin's and Campbell and Howard's
#: papers cite for it;
#: the Borrowed Identities paper's ref. [48] points to his later composite-
#: Toffoli paper instead.  A record whose class is here names these works and
#: not the Borrowed Identities paper, which recovered the class rather than
#: introducing it.  Eastin's and Jones's 8 T -> CCZ factories are concurrent
#: and independent (arXiv:1212.4872 and 1212.5069, the same week), so both
#: stay.
LITERATURE = {
    (15, 1, 3, "T0"): dict(
        keys=["bravyi2005universal"],
        where="Bravyi and Kitaev (2005); recovered in arXiv:2606.28518 "
              "(symmetric circuits, s = 2)"),
    (14, 2, 2, "T0+T1"): dict(
        keys=["bravyi2012magic"],
        where="the k = 2 member of the Bravyi-Haah [[3k+8,k,2]] family "
              "(arXiv:2606.28518, App. F.3a)"),
    (20, 4, 2, "T0+T1+T2+T3"): dict(
        keys=["bravyi2012magic"],
        where="the k = 4 member of the Bravyi-Haah [[3k+8,k,2]] family "
              "(arXiv:2606.28518, App. F.3a)"),
    (26, 6, 2, "T0+T1+T2+T3+T4+T5"): dict(
        keys=["bravyi2012magic"],
        where="the k = 6 member of the Bravyi-Haah [[3k+8,k,2]] family "
              "(arXiv:2606.28518, App. F.3a)"),
    (8, 3, 2, "CCZ012"): dict(
        keys=["eastin2013distilling", "jones2013low"],
        where="the 8 T -> CCZ factory of Eastin (2013) and Jones (2013) "
              "(arXiv:2606.28518, malleable circuits)"),
    (12, 2, 2, "CS01"): dict(
        keys=["webster2023transversal"],
        where="the T-to-CS factory [[12,2,2]] of Webster, Quintavalle and "
              "Bartlett (arXiv:2606.28518, introduction, ref. [33])"),
    (14, 6, 2, "CCZ012+CCZ345"): dict(
        keys=["campbell2017unified"],
        where="Campbell and Howard (2017), Example IV.2: 14 T states for two "
              "CCZ gates, the N = 2 member of their 6N + 2 family "
              "(arXiv:2606.28518, two-group circuits, ref. [24])"),
    (18, 4, 2, "CS01+CS23"): dict(
        keys=["campbell2017unified"],
        where="Campbell and Howard (2017), Example IV.3: 18 T states for two "
              "CS gates with output error 45 eps^2"),
}

REGIMES = {
    "two-group": "borrowed-identity search: two-group",
    "symmetry-free": "borrowed-identity search: symmetry-free",
}
STRENGTHS = {
    "two-group": (
        "found by the two-group borrowed-identity search of Singh, Gidney and "
        "Jones (arXiv:2606.28518; borrowed_identities/): an identity circuit "
        "symmetric within its output and check blocks, with its output-only "
        "gates removed; a verified witness, not a maximum"),
    "symmetry-free": (
        "found by the symmetry-free, targeted-output borrowed-identity search "
        "of Singh, Gidney and Jones (arXiv:2606.28518; borrowed_identities/), "
        "which solves for the check couplings of a chosen output; a verified "
        "witness, not a maximum"),
}


# ----------------------------------------------------------------- the rows
def read_catalogue(level):
    path = UPSTREAM / "outputs" / f"factory_catalogue_l{level}.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def two_group_circuit(level, n, k, s_total, s_O):
    """The gate list of one two-group row, as ``export_circuit.py`` builds it."""
    pairs, W_total, W_O = TG.build_gate_set(k, n - k, s_total, s_O)
    valid = TG.find_valid_signs(level, n, k, pairs)
    if not valid:
        raise SystemExit(f"l={level} n={n} k={k} s_total={s_total} s_O={s_O}: "
                         f"no valid sign assignment")
    signs = valid[0]
    removed = {(w, 0) for w in (set(W_O) & set(W_total)) if w >= 1}
    outputs, checks = list(range(k)), list(range(k, n))
    gates = []
    for (wO, wS), sign in signs.items():
        if sign == 0 or (wO, wS) in removed:
            continue
        for O in combinations(outputs, wO):
            for S in combinations(checks, wS):
                gates.append((sorted(O + S), sign % (1 << level)))
    parameters = dict(l=level, n=n, k=k, s_total=s_total, s_O=s_O, s_S=1,
                      signs=[[wO, wS, sign] for (wO, wS), sign
                             in sorted(signs.items())])
    return gates, n, parameters


def symmetry_free_circuit(level, parts, checks):
    """The gate list `symfree_search.solve_binding` returns, or ``None``."""
    result = SF.solve_binding(list(parts), checks, level)
    if result is None:
        return None
    gates = [(sorted(support), coeff % (1 << level))
             for support, coeff in result["gates"]]
    parameters = dict(l=level, parts=list(parts), checks=checks)
    return gates, result["n"], parameters


def blocks_of(decomposition):
    """Output block sizes from a decomposition such as ``CCZ012+CS34+T5``."""
    return sorted((sum(ch.isdigit() for ch in term)
                   for term in decomposition.split("+")), reverse=True)


def symmetry_free_as_searched(level, parts):
    """The circuit `symfree_search.search` keeps: the smallest check count."""
    for checks in range(1, 5):
        built = symmetry_free_circuit(level, parts, checks)
        if built is None:
            continue
        gates, n, _parameters = built
        info = SF.classify([frozenset(g) for g, _c in gates],
                           [c for _g, c in gates],
                           set(range(sum(parts))), n, level)
        if info["distance"] == 2 and info["degree"] >= 1:
            return built
    return None


# ---------------------------------------------------- independent re-checks
def magic(gates):
    """Indices of the gates that consume a level-l magic state: odd coefficient."""
    return [index for index, (_support, coeff) in enumerate(gates) if coeff % 2]


def borrowed_identity_violation(gates, k, level):
    """The first check-touching monomial with genuine level-l phase, or None.

    The condition, written out from the paper's definition rather than imported:
    a parity gate on support ``g`` with coefficient ``c`` adds
    ``(-1)^(t+1) 2^(t-1) c`` to the monomial on every ``t``-subset of ``g``, and
    a monomial touching a check wire must be Clifford, i.e. its coefficient
    must vanish modulo ``2^t`` (it is reduced modulo ``2^l`` throughout).
    """
    mod = 1 << level
    for size in range(1, level + 1):
        totals = {}
        for support, coeff in gates:
            for T in combinations(support, size):
                totals[T] = totals.get(T, 0) + coeff
        for T, total in totals.items():
            if max(T) < k:
                continue
            value = ((-1) ** (size + 1)) * (1 << (size - 1)) * total % mod
            if value % (1 << size):
                return list(T)
    return None


def check_circuit(row, gates, n, where, from_row):
    """Stop unless the circuit is the row's: N, wires, and a borrowed identity.

    ``from_row`` is false for the one circuit not built from the row's own
    printed parameters -- the symmetry-free circuit of a row both searches
    found -- whose register may differ from the two-group ``n`` it prints.
    """
    level, k = int(row["l"]), int(row["k"])
    supports = [tuple(g) for g, _c in gates]
    problems = []
    if len(set(supports)) != len(supports):
        problems.append("repeated gate support")
    if len(magic(gates)) != int(row["N"]):
        problems.append(f"{len(magic(gates))} odd-coefficient gates, the row "
                        f"says N={row['N']}")
    if from_row and n != int(row["n"]):
        problems.append(f"{n} wires, the row says n={row['n']}")
    bad = borrowed_identity_violation(gates, k, level)
    if bad is not None:
        problems.append(f"monomial {bad} touches a check wire with genuine "
                        f"level-{level} phase")
    if problems:
        raise SystemExit(f"{where}: " + "; ".join(problems))


def measured_distance(gates, k, n, where):
    """``(d, witness)``: the exact distance over the magic gates, and one
    undetectable damaging fault of that weight, as indices into ``gates``."""
    odd = magic(gates)
    report = FC.distance_report([gates[i][0] for i in odd], k, n,
                                budget=FC.Budget())
    if report["d_exact"] is None:
        raise SystemExit(f"{where}: the distance was not pinned "
                         f"({report['scanned']})")
    return report["d_exact"], [odd[i] for i in report["witness"]]


# ------------------------------------------------------------- the export
def circuits_for(level):
    """Every circuit of one level, as the entries of ``circuits_l{level}.json``."""
    entries = []
    for index, row in enumerate(read_catalogue(level), start=1):
        k, n = int(row["k"]), int(row["n"])
        built = []
        if row["s_total"]:
            built.append(("two-group", two_group_circuit(
                level, n, k, int(row["s_total"]), int(row["s_O"])), True))
        if row["parts"]:
            parts = [int(p) for p in row["parts"].split("+")]
            circuit = symmetry_free_circuit(level, parts, n - k)
            if circuit is None:
                raise SystemExit(f"l={level} row {index}: no solution at "
                                 f"parts={parts} checks={n - k}")
            built.append(("symmetry-free", circuit, True))
        elif "symmetry-free" in row["search"]:
            circuit = symmetry_free_as_searched(level,
                                                blocks_of(row["decomposition"]))
            if circuit is None:
                raise SystemExit(f"l={level} row {index}: the symmetry-free "
                                 f"search does not reproduce "
                                 f"{row['decomposition']}")
            built.append(("symmetry-free", circuit, False))
        for search, (gates, wires, parameters), from_row in built:
            name = f"l{level}-row{index:03d}-{search}"
            check_circuit(row, gates, wires, name, from_row)
            d, witness = measured_distance(gates, k, wires, name)
            entries.append({
                "id": name,
                "row": index,
                "csv": dict(row),
                "search": search,
                "parameters": parameters,
                "wires": wires,
                "outputs": list(range(k)),
                "N": len(magic(gates)),
                "d": d,
                "d_witness": witness,
                "d_upstream": int(row["d"]),
                "gates": [[support, coeff] for support, coeff in gates],
            })
    return entries


def merge_record(entry):
    """One level-3 circuit in `merge_results.py`'s input format."""
    row = entry["csv"]
    key = (int(row["N"]), int(row["k"]), int(row["d"]), row["decomposition"])
    known = LITERATURE.get(key)
    citations = list(known["keys"]) if known else [BORROWED]
    p = entry["parameters"]
    if entry["search"] == "two-group":
        built = (f"two-group l=3 n={p['n']} k={p['k']} s_total={p['s_total']} "
                 f"s_O={p['s_O']} s_S=1")
    else:
        built = (f"symmetry-free l=3 parts={'+'.join(map(str, p['parts']))} "
                 f"checks={p['checks']}")
    record = {
        "k": int(row["k"]),
        "N": entry["wires"],
        "n": entry["N"],
        "columns": [entry["gates"][i][0] for i in magic(entry["gates"])],
        "regime": REGIMES[entry["search"]],
        "strength": STRENGTHS[entry["search"]],
        "discovery": "pre-existing",
        "citations": citations,
        "file": "borrowed_identities/circuits/circuits_l3.json",
        "label": entry["id"],
        "provenance": built,
        "origin": f"{REPOSITORY} at {COMMIT[:7]}, "
                  f"outputs/factory_catalogue_l3.csv row {entry['row']}",
    }
    notes = []
    # The row's printed distance is a CLAIM and goes in as one, so the merger
    # checks it -- except where the measurement above has already disproved it,
    # in which case the claim would only reject a sound circuit.
    if entry["d_upstream"] <= entry["d"]:
        record["d"] = entry["d_upstream"]
    else:
        notes.append(f"the upstream CSV prints d={entry['d_upstream']}; the "
                     f"faults on gates {entry['d_witness']} cancel on every "
                     f"check and not on the output, so d={entry['d']}")
    if row["t_count"] and int(row["k"]) <= 6:
        record["t_count"] = int(row["t_count"])
    if int(row["k"]) <= 4:
        record["poly_degree"] = int(row["degree"])
    if known:
        notes.append("earlier publication: " + known["where"])
    if notes:
        record["notes"] = "; ".join(notes)
    return record


def one_per_line(head, name, items):
    """``head`` indented, then ``items`` one JSON object per line."""
    text = json.dumps(head, indent=1, ensure_ascii=False)[:-2]
    body = ",\n".join("  " + json.dumps(item, ensure_ascii=False,
                                         separators=(",", ":"))
                      for item in items)
    return f"{text},\n \"{name}\": [\n{body}\n ]\n}}\n"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    files = {}
    level3 = []
    for level in LEVELS:
        entries = circuits_for(level)
        source = UPSTREAM / "outputs" / f"factory_catalogue_l{level}.csv"
        head = {
            "about": (f"Explicit circuits for every row of the level-{level} "
                      f"borrowed-identity catalogue, rebuilt by "
                      f"borrowed_identities/export_circuits.py. Cite {CITATION}."),
            "source": {"repository": REPOSITORY, "commit": COMMIT,
                       "paper": PAPER,
                       "file": f"outputs/factory_catalogue_l{level}.csv",
                       "sha256": sha256(source)},
            "level": level,
            "conventions": (
                f"wires 0..k-1 are the outputs and k..wires-1 the checks. A "
                f"gate [support, c] is the parity phase gate of the paper's "
                f"Eq. (2) at angle c*pi/2^{level}: it applies the phase "
                f"exp(2*pi*i*c/2^{level}) to basis states of odd parity on the "
                f"support, with c taken modulo 2^{level}. N counts the gates "
                f"with odd c, the level-{level} magic states consumed; gates "
                f"with even c are lower-level rotations the paper counts as "
                f"free. d is the distance measured here over the odd-c gates "
                f"(d_witness: gate indices of an undetectable damaging fault "
                f"of that weight); d_upstream is the CSV's value."),
            "rows": len(read_catalogue(level)),
        }
        files[OUT / f"circuits_l{level}.json"] = one_per_line(
            head, "circuits", entries)
        if level == 3:
            level3 = [merge_record(entry) for entry in entries]
            seen = {(int(e["csv"]["N"]), int(e["csv"]["k"]), int(e["csv"]["d"]),
                     e["csv"]["decomposition"]) for e in entries}
            unmatched = [key for key in LITERATURE if key not in seen]
            if unmatched:
                raise SystemExit(f"LITERATURE entries match no row: {unmatched}")
    files[OUT / "factories_l3.json"] = one_per_line({
        "about": ("Level-3 borrowed-identity circuits in the input format of "
                  "master_catalog/merge_results.py, one record per circuit in "
                  "circuits_l3.json. The columns are the gates with odd "
                  "coefficient: at level 3 an even coefficient is a Clifford "
                  "rotation, free and correctable, not an injection."),
    }, "results", level3)
    return files


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="rebuild and compare with the files on disk")
    args = parser.parse_args(argv)
    files = build()
    if args.check:
        stale = [path for path, text in files.items()
                 if not path.exists() or path.read_text(encoding="utf-8") != text]
        for path in stale:
            print(f"differs: {path.relative_to(REPO)}")
        print("up to date" if not stale else f"{len(stale)} file(s) differ")
        return 1 if stale else 0
    OUT.mkdir(exist_ok=True)
    for path, text in files.items():
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
