#!/usr/bin/env python3
"""One-off migration: the second research round's distances and counts.

    python master_catalog/migrations/round2_evidence_2026_11_07.py [--dry-run]

`round2_certificates/` holds the records of the second-round distance search
of 7 November 2026 and of the plan's kernel, assembled by
`round2_certificates/assemble.py` into `certificates.json` (lower bounds and
re-checked faults) and `coefficients.json` (exact counts of the harmful
faults of one weight), each record bound to its circuit by the SHA-256 of
the columns.  This script, idempotent, writes them into the rows:

1.  **Faults at the certified distance.**  A row whose ``d`` is a floor that
    a certificate proves, and for which the file holds a re-checked fault of
    weight ``d``, becomes exact: ``d_upper`` and ``d_witness`` are that fault
    (935.89.7.a, 936.88.7.a and 998.26.8.a).
2.  **More evidence.**  A row whose ``d`` rests on a certificate gets an
    entry in ``d_certified_evidence`` for every record of
    ``certificates.json`` that states exactly that bound for its circuit
    (599.1.15.a gets tropidist's dense DP; 988.36.7.a, 935.89.7.a and
    936.88.7.a a second sweep; the doubled codes up to 401.1.13.a the
    trellis and mitml).
3.  **1715.287.3.a.**  The plan's kernel and this catalogue's own sweep at a
    raised budget both find weights 1 to 5 clean, and mitml's count found a
    fault of weight 6, re-checked.  The row's certificate ``d = 6``, until now
    beside ``d`` because it rested on the gamma frontier release alone, so
    becomes its ``d`` by the rule of `distance_policy_2026_11_07.py`: the
    sweep's floor goes to ``d_sweep_floor`` and the row becomes 1715.287.6.a,
    keeping its old label in ``former_labels``.
4.  **Counts.**  An exact row whose circuit has a count of weight ``d`` in
    ``coefficients.json`` gets ``A_d`` and ``A_d_evidence``, one entry per
    tool that counted it.  A row that already has an ``A_d`` must agree.

Every changed row passes `verify_catalog.verify_row` (which recounts
``A_d`` wherever `errorcoeff` reaches and otherwise checks the evidence), the
file-level checks pass over both files, and only then is anything written.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE.parent
REPO = CATALOGUE.parent
sys.path.insert(0, str(CATALOGUE))
sys.path.insert(0, str(HERE))

import catalogfile as CF                                          # noqa: E402
import constructions as CO                                        # noqa: E402
import distance_policy_2026_11_07 as DP                           # noqa: E402
import verify_catalog as VC                                       # noqa: E402

CERTS = "round2_certificates/certificates.json"
COUNTS = "round2_certificates/coefficients.json"
PROMOTE = "1715.287.3.a"


def load():
    records, problem = VC.evidence_records(CERTS)
    if problem:
        raise SystemExit(problem)
    counts, problem = VC.coefficient_records(COUNTS)
    if problem:
        raise SystemExit(problem)
    witnesses = json.loads((REPO / CERTS).read_text(encoding="utf-8"))["witnesses"]
    return records, counts, witnesses


def entries_for(row, records):
    """``d_certified_evidence`` entries for every record stating the row's bound."""
    digest = CO.digest(row["columns"])
    out = []
    for record in records:
        if record["columns_sha256"] == digest and record["lower_bound"] == row["d_certified"]:
            entry = {"file": CERTS, "method": record["method"], "tool": record["tool"]}
            if entry not in out:
                out.append(entry)
    return out


def witness_for(row, witnesses, weight):
    digest = CO.digest(row["columns"])
    found = [w["witness"] for w in witnesses
             if w["columns_sha256"] == digest and w["weight"] == weight]
    return sorted(found[0]) if found else None


def apply(payload):
    """The four steps, in place; the labels of the rows changed, old -> new."""
    records, counts, witnesses = load()
    rows = payload["factories"]
    changed = {}
    for row in rows:
        before = json.dumps(row, sort_keys=True)
        old = row["catalog_label"]
        if row["catalog_label"] == PROMOTE and not CF.rests_on_certificate(row):
            entries = entries_for(row, records)
            fault = witness_for(row, witnesses, row["d_certified"])
            if len(entries) < 2 or fault is None or not row["d_certified_is_exact"]:
                raise SystemExit(f"{PROMOTE}: the evidence is not what the docstring says")
            floor = row["d"]
            row["d"] = row["d_certified"]
            row["d_is_exact"] = True
            row["d_upper"], row["d_witness"] = row["d"], fault
            row["d_sweep_floor"] = floor
            row["d_certified_evidence"] = entries
            row["d_certified_source"] += (
                "; since 2026-11-07 the row's d: weights 1 to 5 swept clean by the "
                "plan's meet-in-the-middle kernel and by this catalogue's own sweep "
                "at a raised budget, and a fault of weight 6 found by mitml and "
                "re-checked (round2_certificates/)")
            row["former_labels"] = (row.get("former_labels") or []) + [old]
            row["catalog_label"] = CF.next_label(rows, row["n"], row["k"], row["d"])
        if CF.rests_on_certificate(row):
            # step 1: a fault at the certified distance makes a floor exact
            if not row["d_is_exact"]:
                fault = witness_for(row, witnesses, row["d"])
                if fault is not None:
                    row["d_is_exact"] = row["d_certified_is_exact"] = True
                    row["d_upper"], row["d_witness"] = row["d"], fault
                    row["d_certified_source"] += (
                        f"; a fault of weight {row['d']}, found by the research's "
                        f"sweeps and re-checked, makes it exact "
                        f"(round2_certificates/certificates.json)")
            # step 2: every record that states the bound
            for entry in entries_for(row, records):
                if entry not in row["d_certified_evidence"]:
                    row["d_certified_evidence"].append(entry)
        # step 4: the count at d
        if row["d_is_exact"]:
            digest = CO.digest(row["columns"])
            mine = [c for c in counts if c["columns_sha256"] == digest
                    and c["weight"] == row["d"]]
            if mine:
                values = {c["count"] for c in mine}
                if len(values) != 1:
                    raise SystemExit(f"{old}: the tools disagree on A_d")
                value = values.pop()
                if row["A_d"] is not None and row["A_d"] != value:
                    raise SystemExit(f"{old}: the row says A_d={row['A_d']}, the "
                                     f"evidence {value}")
                row["A_d"] = value
                listed = row.get("A_d_evidence") or []
                for c in mine:
                    entry = {"file": COUNTS, "tool": c["tool"]}
                    if entry not in listed:
                        listed.append(entry)
                row["A_d_evidence"] = listed
        if json.dumps(row, sort_keys=True) != before:
            changed[old] = row["catalog_label"]
    return changed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load_all()
    main_rows = [row for row in payload["factories"] if not CF.is_large(row)]
    if main_rows != sorted(main_rows, key=DP.MR.sort_key):
        raise SystemExit("the main file is not in the catalogue's sort order")
    changed = apply(payload)
    DP.resort(payload)
    by_label = {row["catalog_label"]: row for row in payload["factories"]}
    for old, new in changed.items():
        row = by_label[new]
        started = time.time()
        _facts, problems = VC.verify_row(row)
        print(f"  {old}{' -> ' + new if new != old else ''}: d "
              f"{'=' if row['d_is_exact'] else '>='} {row['d']}, A_d {row['A_d']}, "
              f"{len(row.get('d_certified_evidence') or [])} distance and "
              f"{len(row.get('A_d_evidence') or [])} count evidence entries; "
              f"verified in {time.time() - started:.0f}s"
              + ("" if not problems else f": {problems}"), flush=True)
        if problems:
            raise SystemExit("a changed row fails verification; nothing written")
    rows = payload["factories"]
    residue = [p for row in rows for p in VC.certificate_problems(row)]
    residue += [p for row in rows for p in VC.label_problems(row)]
    residue += (VC.duplicate_label_problems(rows) + VC.duplicate_class_problems(rows)
                + VC.provenance_problems(payload) + VC.citation_problems(payload)
                + VC.header_problems(payload))
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the catalogue fails a file-level check; nothing written")
    print(f"{len(changed)} row(s) changed")
    if args.dry_run or not DP._changes(payload):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write_all(payload)
    VC.persist_metric_cache()
    print("wrote master_catalog.json, master_catalog_large.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
