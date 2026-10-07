#!/usr/bin/env python3
"""One-off migration: open the catalogue to distance 2, and merge the
Borrowed Identities circuits and the symmetry-SAT search's distance-2 rows.

    python master_catalog/migrations/distance_two_2026_10_07.py [--dry-run]

Until now the catalogue held ``d >= 3`` only, and pointed to S. Singh,
C. Gidney and C. Jones, "Borrowed Identities: Malleable Distillation Factories
and a Unified Numerical Search" (arXiv:2606.28518) for distance 2.  That
paper's catalogue is now imported into ``borrowed_identities/`` with an
explicit circuit for every row, and this migration brings its level-3
circuits in.  In order:

1.  **The header.**  The scope says ``distance >= 2``; the ``discovery``
    glossary counts the borrowed-identity searches among the finders that make
    a class ``pre-existing`` (they are not AI searches); and the works the new
    rows credit are added to ``references``.  The verifier and merger floors
    moved from 3 to 2 in the same change, in code.
2.  **The Borrowed Identities circuits**,
    ``borrowed_identities/circuits/factories_l3.json``, through
    `merge_results.merge` -- the same verification bar as every merge.  Their
    regimes (``borrowed-identity search: two-group`` / ``: symmetry-free``) are
    registered by the merge, at the end of the header's order, as witnesses.
    Each record already names its citations (see that folder's README): the
    earliest work that published the class, or the paper where none did.  (As
    first run, the records named the paper after the earlier work as well;
    `earliest_reference_2026_10_07.py` removed it from those rows.)
    The paper's ``[[8,4,2]]`` is refused, as the catalogue refuses every
    pseudo-output: its fourth output is a combination of the other three
    modulo the checks.  The paper keeps it for the correlated errors the extra
    qubit detects, which this table's fault model does not count.
3.  **The symmetry-SAT search's distance-2 rows**, from
    ``symmetry_sat_search/catalog/factories.json``.  The catalogue has always
    held every qualifying row of that file; with the floor at 2, its 19
    level-3 distance-2 rows qualify.  They are merged after the Borrowed
    Identities circuits, so a class both have keeps the published circuit when
    the two are equally small.  A row new to the catalogue is credited by the
    merger's default for distance 2 (the symmetry-and-AI report), unless a
    published work states its class (`SAT_LITERATURE`).  Two of the 19 are not
    admitted as circuits -- one carries a redundant check wire, one an idle
    wire -- and this script stops unless their classes are held anyway.

Run once, from the repository root; a second run finds every circuit already
held and writes a byte-identical catalogue.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE.parent
REPO = CATALOGUE.parent
sys.path.insert(0, str(CATALOGUE))

import catalogfile as CF                                          # noqa: E402
import glcanon as GC                                              # noqa: E402
import merge_results as MR                                        # noqa: E402
import verify_catalog as VC                                       # noqa: E402

BORROWED_FILE = "borrowed_identities/circuits/factories_l3.json"
SAT_FILE = "symmetry_sat_search/catalog/factories.json"

SCOPE = ("every Clifford level-3, distance >= 2 factory this collection holds, "
         "deduplicated on (n, k, d, GL(k,2) class of the gate); rows arrive "
         "from the exhaustive length-54 classification (d >= 3), from the "
         "borrowed-identity searches of Singh, Gidney and Jones "
         "(borrowed_identities/), and from search campaigns merged in by "
         "merge_results.py")
DISCOVERY = {
    "pre-existing": (
        "not an AI discovery of this project: a classification stage this "
        "repository ran, the symmetry-SAT search catalogue, the borrowed-"
        "identity searches, the exhaustive length-54 classification alone, or "
        "a community contribution has this class"),
    "AI search": (
        "found only by AI search campaigns: no classification stage this "
        "repository ran, no symmetry-SAT search, no borrowed-identity search "
        "and no community contribution is recorded among its sources (the "
        "length-54 classification may have it too); whether it was new to the "
        "literature is what citations says"),
}
REFERENCES = {
    "singh2026borrowed": {
        "short": "Singh et al. (2026)",
        "full": "S. Singh, C. Gidney, and C. Jones, \"Borrowed Identities: "
                "Malleable Distillation Factories and a Unified Numerical "
                "Search,\" arXiv:2606.28518 (2026).",
        "url": "https://arxiv.org/abs/2606.28518",
    },
    "bravyi2012magic": {
        "short": "Bravyi & Haah (2012)",
        "full": "S. Bravyi and J. Haah, \"Magic-state distillation with low "
                "overhead,\" Phys. Rev. A 86, 052329 (2012).",
        "url": "https://doi.org/10.1103/PhysRevA.86.052329",
    },
    "eastin2013distilling": {
        "short": "Eastin (2013)",
        "full": "B. Eastin, \"Distilling one-qubit magic states into Toffoli "
                "states,\" Phys. Rev. A 87, 032321 (2013).",
        "url": "https://doi.org/10.1103/PhysRevA.87.032321",
    },
    "jones2013novel": {
        "short": "Jones (2013)",
        "full": "C. Jones, \"Novel constructions for the fault-tolerant "
                "Toffoli gate,\" Phys. Rev. A 87, 022328 (2013).",
        "url": "https://doi.org/10.1103/PhysRevA.87.022328",
    },
    "webster2023transversal": {
        "short": "Webster et al. (2023)",
        "full": "M. A. Webster, A. O. Quintavalle, and S. D. Bartlett, "
                "\"Transversal diagonal logical operators for stabiliser "
                "codes,\" New J. Phys. 25, 103018 (2023).",
        "url": "https://doi.org/10.1088/1367-2630/acfc5f",
    },
    "campbell2017unified": {
        "short": "Campbell & Howard (2017)",
        "full": "E. T. Campbell and M. Howard, \"Unified framework for magic "
                "state distillation and multiqubit gate synthesis with reduced "
                "resource cost,\" Phys. Rev. A 95, 022316 (2017).",
        "url": "https://doi.org/10.1103/PhysRevA.95.022316",
    },
}

#: Published works stating the class of a symmetry-SAT distance-2 row, by
#: ``(n, k)`` and the gate they print, matched up to GL(k,2) by `glcanon`.
#: Campbell and Howard's Example IV.4 synthillises the gate with weighted
#: polynomial ``4 x5 (x1 x2 + x3 x4)`` -- two CCZs sharing one qubit -- from
#: 12 T states with output error ``66 eps^2``.
SAT_LITERATURE = [
    (12, 5, frozenset({frozenset({0, 1, 4}), frozenset({2, 3, 4})}),
     ["campbell2017unified"], "Campbell and Howard (2017), Example IV.4"),
]


def update_header(payload):
    """The header edits; returns the lines describing what changed."""
    said = []
    if payload["scope"] != SCOPE:
        payload["scope"] = SCOPE
        said.append("scope: distance >= 2")
    for key, text in DISCOVERY.items():
        if payload["discovery"].get(key) != text:
            payload["discovery"][key] = text
            said.append(f"discovery[{key!r}]: names the borrowed-identity searches")
    references = payload["references"]
    for key, entry in REFERENCES.items():
        if references.get(key) != entry:
            references[key] = dict(entry)
            said.append(f"reference {key}: {entry['short']}")
    return said


def sat_records():
    """The level-3 distance-2 rows of the symmetry-SAT catalogue, as records."""
    rows = json.loads((REPO / SAT_FILE).read_text(encoding="utf-8"))["factories"]
    records = []
    for row in rows:
        if row.get("level", 3) != 3 or row["d"] != 2:
            continue
        record = {
            "k": row["k"], "N": row["N"], "columns": row["columns"],
            "d": row["d"], "regime": "symmetry-SAT search",
            "discovery": "pre-existing", "file": SAT_FILE,
            "label": row["label"], "provenance": row["source"],
        }
        gate = VC.derived_gate([sorted(set(c)) for c in row["columns"]],
                               row["k"])
        for n, k, printed, keys, where in SAT_LITERATURE:
            if (len(row["columns"]), row["k"]) == (n, k) \
                    and GC.gl_isomorphic(k, gate, printed):
                record["citations"] = list(keys)
                record["notes"] = f"published: {where}"
        records.append(record)
    return records


def held(payload, record):
    """Whether the catalogue holds ``record``'s class, at its own distance."""
    columns = [sorted(set(c)) for c in record["columns"]]
    gate = VC.derived_gate(columns, record["k"])
    return any((row["n"], row["k"], row["d"])
               == (len(columns), record["k"], record["d"])
               and GC.gl_isomorphic(row["k"], VC.row_monomials(row), gate)
               for row in payload["factories"])


def report(title, verdicts, records):
    counts = {}
    for _index, verdict, _row, _detail in verdicts:
        counts[verdict] = counts.get(verdict, 0) + 1
    print(f"{title}: " + ", ".join(f"{n} {v}" for v, n in sorted(counts.items())))
    for index, verdict, row, detail in verdicts:
        if verdict == "rejected":
            print(f"  rejected  {records[index]['label']}: "
                  + "; ".join(f"{kind}: {message}" for kind, message in detail))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load()
    before = len(payload["factories"])

    for line in update_header(payload):
        print(f"header  {line}")

    borrowed = MR.read_records(REPO / BORROWED_FILE)
    verdicts = MR.merge(payload, borrowed, BORROWED_FILE)
    report("borrowed identities", verdicts, borrowed)
    refused = {borrowed[i]["label"] for i, v, _r, _d in verdicts if v == "rejected"}
    if refused != {"l3-row083-two-group"}:
        raise SystemExit(f"expected only the [[8,4,2]] pseudo-output to be "
                         f"refused, got {sorted(refused)}")

    sat = sat_records()
    verdicts = MR.merge(payload, sat, SAT_FILE)
    report("symmetry-SAT distance 2", verdicts, sat)
    missing = [record["label"] for record in sat if not held(payload, record)]
    if missing:
        raise SystemExit(f"symmetry-SAT rows whose class is not held: {missing}")

    residue = (VC.duplicate_class_problems(payload["factories"])
               + VC.duplicate_label_problems(payload["factories"])
               + VC.provenance_problems(payload)
               + VC.citation_problems(payload)
               + VC.header_problems(payload))
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the merged catalogue fails file-level checks; "
                         "nothing written")
    after = len(payload["factories"])
    print(f"catalogue: {before} -> {after} classes "
          f"({sum(r['d'] == 2 for r in payload['factories'])} at d = 2)")
    if args.dry_run:
        print("dry run: nothing written")
        return 0
    CF.write(payload)
    VC.persist_metric_cache()
    print("wrote master_catalog.json and MASTER_CATALOG.md; next: "
          "verify_catalog.py --changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
