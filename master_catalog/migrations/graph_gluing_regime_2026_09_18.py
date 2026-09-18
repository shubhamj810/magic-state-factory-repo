#!/usr/bin/env python3
"""One-off migration: file the nine graph-glued factories under "AI search: graph gluing".

    python master_catalog/migrations/graph_gluing_regime_2026_09_18.py [--dry-run]

The nine pure-T witnesses merged from
``master_catalog/imports/2026-09-18_graph_gluing_d3/factories.json`` carried
the regime name, labels and provenance of the analysis they were prepared in.
That file now names the regime ``AI search: graph gluing``, labels each record
``graph gluing [[n,k,d]]`` and states the construction in one sentence (which
factories were glued along which graph, and where the witness is).  This brings
the nine catalogue rows into line with it: the header regime is renamed in
place, and each row's ``regimes``, ``strongest_claim`` and single source entry
are taken from the record with the same ``(n, k, N)``.  Circuits, distances,
citations and every other row are untouched.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import catalogfile as CF                                          # noqa: E402
import verify_catalog as VC                                       # noqa: E402

NEW = "AI search: graph gluing"
INPUT = HERE.parent / "imports" / "2026-09-18_graph_gluing_d3" / "factories.json"
IMPORTS = "master_catalog/imports/2026-09-18_"


def former_regime(payload):
    """The regime the nine rows carry: the one whose sources are this import."""
    names = {s["regime"] for row in payload["factories"] for s in row["sources"]
             if s["file"].startswith(IMPORTS) and s["regime"] != NEW}
    if len(names) != 1:
        raise SystemExit(f"expected one regime on the import's rows, found "
                         f"{sorted(names)}; nothing to do" if not names else
                         f"expected one regime on the import's rows, found "
                         f"{sorted(names)}")
    return names.pop()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load()
    OLD = former_regime(payload)
    data = json.loads(INPUT.read_text())
    records = {(r["n"], r["k"], r["N"]): r
               for r in (data["results"] if isinstance(data, dict) else data)}
    strength = next(iter(records.values()))["strength"]
    payload["regimes"] = {(NEW if key == OLD else key): (strength if key == OLD else s)
                          for key, s in payload["regimes"].items()}
    touched = 0
    for row in payload["factories"]:
        if OLD not in row["regimes"]:
            continue
        record = records[(row["n"], row["k"], row["N"])]
        row["regimes"] = [NEW if name == OLD else name for name in row["regimes"]]
        row["strongest_claim"] = payload["regimes"][row["regimes"][0]]
        source, = [s for s in row["sources"] if s["regime"] == OLD]
        source.update(regime=NEW, file=record["file"], label=record["label"],
                      provenance=record["provenance"], notes=record["notes"])
        touched += 1
    print(f"{OLD!r} -> {NEW!r}: {touched} rows re-sourced from {INPUT.name}")
    residue = (VC.provenance_problems(payload) + VC.citation_problems(payload)
               + VC.header_problems(payload)
               + [p for row in payload["factories"] if NEW in row["regimes"]
                  for p in VC.verify_row(row)[1]])
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("inconsistent; nothing written")
    if args.dry_run:
        print("dry run: nothing written")
        return 0
    CF.write(payload)
    print("wrote master_catalog.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
