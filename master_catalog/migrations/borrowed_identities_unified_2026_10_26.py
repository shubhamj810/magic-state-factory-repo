#!/usr/bin/env python3
"""One-off migration: merge the unified borrowed-identity search.

    python master_catalog/migrations/borrowed_identities_unified_2026_10_26.py [--dry-run]

In October 2026 the Borrowed Identities repository (S. Singh, C. Gidney and
C. Jones, arXiv:2606.28518) replaced its per-level catalogues with the tables
of one unified search, copied into ``borrowed_identities/upstream_unified/``.
`borrowed_identities/export_unified.py` rebuilt and checked an explicit circuit
for every level-3 row of ``all_factories.csv``, of ``large_sweep.csv`` up to
``n = 4095`` inputs, and of ``l3_k78_targets.csv``, and wrote them to
``borrowed_identities/circuits/factories_unified_l3.json``.  This merges that
file through `merge_results.merge`, the same bar as every merge.

Credit: a class the merge adds is credited to the paper, unless the upstream
table's ``reference`` column names earlier work for its row
(`export_unified.upstream_credit`).  A held class the column names gets the
earliest of what it had and what the column names -- the rule of the first
import, under which a class cites only the earliest work that published it.
Every other held class keeps exactly the credit it had: the merge would append
the paper to it, as it does for any citation a record names, and this
migration puts the old list back, since the unified tables, released in
October 2026, are not earlier than any of those works.  The two works the
column names that the catalogue did not cite before are added to the header,
and a work no row cites any more is taken out of it: Eastin (2013) and Jones
(2013), whose one row, ``8.3.2.a``, now credits Bombin and Martin-Delgado
(2007) alone.

The Clifford-padding rows, a smaller factory's outputs spread over more wires
by a CNOT relabelling, are refused as pseudo-outputs: an output that equals a
combination of others modulo the checks is one logical qubit wearing two
labels in this catalogue's terms, as the first import's ``[[8,4,2]]`` was.
Re-running it on a migrated file changes nothing.
"""
from __future__ import annotations

import argparse
import collections
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE.parent
REPO = CATALOGUE.parent
sys.path.insert(0, str(CATALOGUE))

import catalogfile as CF                                          # noqa: E402
import merge_results as MR                                        # noqa: E402
import verify_catalog as VC                                       # noqa: E402

RESULTS = "borrowed_identities/circuits/factories_unified_l3.json"
BORROWED = "singh2026borrowed"
REFERENCES = {
    "litinski2019magic": {
        "short": "Litinski (2019)",
        "full": "D. Litinski, \"Magic state distillation: not as costly as "
                "you think,\" Quantum 3, 205 (2019).",
        "url": "https://doi.org/10.22331/q-2019-12-02-205",
        "date": "2019-12-02",
    },
    "bombin2007exact": {
        "short": "Bombín & Martin-Delgado (2007)",
        "full": "H. Bombín and M. A. Martin-Delgado, \"Exact topological "
                "quantum order in D=3 and beyond: Branyons and brane-net "
                "condensates,\" Phys. Rev. B 75, 075103 (2007).",
        "url": "https://doi.org/10.1103/PhysRevB.75.075103",
        "date": "2007-02",
    },
}


def earliest(keys, references):
    """``keys`` from their earliest year only, in order, without repeats."""
    year = {key: references[key]["date"][:4] for key in keys}
    first = min(year.values())
    return list(dict.fromkeys(key for key in keys if year[key] == first))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load()
    before = len(payload["factories"])
    for key, entry in REFERENCES.items():
        payload["references"].setdefault(key, dict(entry))
    credit = {row["catalog_label"]: list(row["citations"])
              for row in payload["factories"]}
    records = MR.read_records(REPO / RESULTS)
    verdicts = MR.merge(payload, records, RESULTS)
    # the classes an upstream reference names, and the works it names
    named = {}
    for index, verdict, row, _detail in verdicts:
        if row is not None and records[index]["citations"] != [BORROWED]:
            named.setdefault(row["catalog_label"], []).extend(
                records[index]["citations"])
    restored = recredited = 0
    for row in payload["factories"]:
        label = row["catalog_label"]
        old = credit.get(label)
        if label in named:
            new = earliest((old or []) + named[label], payload["references"])
            if old is not None and new != old:
                recredited += 1
        elif old is not None:
            new = old
            restored += row["citations"] != old
        else:
            continue
        row["citations"] = new
    cited = {key for row in payload["factories"] for key in row["citations"]}
    dropped = [key for key in payload["references"] if key not in cited]
    for key in dropped:
        del payload["references"][key]
    tally = collections.Counter(verdict for _i, verdict, _row, _d in verdicts)
    reasons = collections.Counter(kind for _i, verdict, _row, problems in verdicts
                                  if verdict == "rejected"
                                  for kind, _detail in problems)
    print(f"{len(records)} results: " + ", ".join(
        f"{n} {v}" for v, n in sorted(tally.items()))
        + f"; refused as {dict(reasons)}; credit restored on {restored} held "
          f"row(s), set from the upstream references on {recredited}; "
          f"references no row cites, dropped: {dropped or 'none'}; "
          f"{before} -> {len(payload['factories'])} classes")
    residue = (VC.duplicate_class_problems(payload["factories"])
               + VC.provenance_problems(payload)
               + VC.citation_problems(payload)
               + VC.header_problems(payload))
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the merged catalogue fails a file-level check; "
                         "nothing written")
    # a re-run re-adds the paper to held rows and takes it off again, so what
    # decides whether anything changed is the text, not the counters
    if args.dry_run or CF.serialise(payload) == CF.CATALOG_JSON.read_text(
            encoding="utf-8"):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write(payload)
    VC.persist_metric_cache()
    print("wrote master_catalog.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
