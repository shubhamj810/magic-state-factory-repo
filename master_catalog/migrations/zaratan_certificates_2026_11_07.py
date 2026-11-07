#!/usr/bin/env python3
"""One-off migration: record the distances the Zaratan runs certify.

    python master_catalog/migrations/zaratan_certificates_2026_11_07.py [--dry-run]

The runs of 6 November 2026 (tropidist and the meet-in-the-middle kernel, on
the UMD cluster Zaratan and on a laptop) are assembled in
``zaratan_certificates/certificates.json``, each record bound to its row by
the SHA-256 of the row's columns.  This writes them into the catalogue in the
form the tropidist migration of 2026-11-06 used, a certificate beside ``d``;
`distance_policy_2026_11_07.py` then makes ``d`` the certified bound.

For each row the file names, in order:

1.  **A lighter fault than the stored one** becomes ``d_upper`` and
    ``d_witness`` (`verify_catalog` re-checks it).
2.  **The strongest lower bound** of the row's records becomes its
    certificate when it is above what the sweep proves and above any
    certificate the row has; one equal to the row's certificate adds its
    source.  The certificate is exact when it meets ``d_upper``.  Every
    record stating that bound is listed in ``d_certified_evidence``.
3.  **A row whose certificate is now met by its fault** is marked exact.

A row is found by its label or by one of its ``former_labels``, and refused if
its columns are not the ones the runs were given.  Every changed row passes
`verify_catalog.verify_row` before anything is written, and a second run
writes nothing.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE.parent
REPO = CATALOGUE.parent
sys.path.insert(0, str(CATALOGUE))

import catalogfile as CF                                          # noqa: E402
import constructions as CO                                        # noqa: E402
import verify_catalog as VC                                       # noqa: E402

EVIDENCE = "zaratan_certificates/certificates.json"
TOOL_WORDS = {
    "mitm.c kernel": "the meet-in-the-middle kernel research/plan/mitm/mitm.c",
    "tropidist search": ("tropidist (B. Cheng, N. Guo and F. Pan, arXiv:2611.08247; "
                         "github.com/Fanerst/tropidist at b03ec2d4) at one threshold"),
    "tropidist pipeline": ("the dense dynamic programme of tropidist's pipeline "
                           "(B. Cheng, N. Guo and F. Pan, arXiv:2611.08247; at b03ec2d4)"),
}


def find_row(rows, label):
    """The row a run's label names: by its label, or by a former one."""
    hits = [row for row in rows if row["catalog_label"] == label
            or label in (row.get("former_labels") or [])]
    if len(hits) != 1:
        raise SystemExit(f"{label}: {len(hits)} rows carry this label")
    return hits[0]


def bound_to(row, entry, label):
    for key in ("n", "k", "N"):
        if row[key] != entry[key]:
            raise SystemExit(f"{label}: {key} is {row[key]}, the record says {entry[key]}")
    if CO.digest(row["columns"]) != entry["columns_sha256"]:
        raise SystemExit(f"{label}: the columns are not the ones the runs were given")


def source_text(label, records, bound, exact):
    tools = "; ".join(f"{TOOL_WORDS[r['tool']]}, {r['how']}" for r in records)
    claim = (f"d = {bound}, a lower bound of {bound} met by a fault of weight {bound}"
             if exact else f"d >= {bound}")
    return (f"runs on the UMD cluster Zaratan and on a laptop, 6 November 2026, "
            f"of {tools}: {claim} ({EVIDENCE}, record {label})")


def apply(payload, evidence):
    rows = payload["factories"]
    by_label = {}
    for kind in ("records", "witnesses"):
        for entry in evidence[kind]:
            by_label.setdefault(entry["label"], {"records": [], "witnesses": []})[kind].append(entry)
    changed = []
    for label, found in sorted(by_label.items(), key=lambda item: item[0]):
        row = find_row(rows, label)
        for entry in found["records"] + found["witnesses"]:
            bound_to(row, entry, label)
        before = json.dumps(row, sort_keys=True)
        swept = row.get("d_sweep_floor", row["d"])

        # 1. a lighter fault
        if found["witnesses"]:
            lightest = min(found["witnesses"], key=lambda w: w["weight"])
            weight = lightest["weight"]
            if not row["d_is_exact"] and weight <= swept:
                raise SystemExit(f"{label}: a fault of weight {weight} at or below "
                                 f"the proved floor {swept}")
            if row["d_upper"] is None or weight < row["d_upper"]:
                row["d_upper"], row["d_witness"] = weight, sorted(lightest["witness"])

        # 2. the strongest lower bound
        if found["records"]:
            bound = max(r["lower_bound"] for r in found["records"])
            stating = [r for r in found["records"] if r["lower_bound"] == bound]
            held = row.get("d_certified")
            exact = row["d_upper"] == bound
            entries = [{"file": EVIDENCE, "method": "exhaustive search",
                        "tool": r["tool"]} for r in stating]
            if bound > swept and (held is None or bound > held):
                if CF.rests_on_certificate(row):
                    raise SystemExit(f"{label}: a stronger bound than the one d rests "
                                     f"on; re-run the distance policy migration")
                row["d_certified"] = bound
                row["d_certified_is_exact"] = exact
                row["d_certified_source"] = source_text(label, stating, bound, exact)
                row["d_certified_evidence"] = entries
            elif bound > swept and bound == held:
                ours = source_text(label, stating, bound, exact)
                if ours not in row["d_certified_source"]:
                    row["d_certified_source"] += "; independently, " + ours
                listed = row.setdefault("d_certified_evidence", [])
                listed += [e for e in entries if e not in listed]
                if exact and not CF.rests_on_certificate(row):
                    row["d_certified_is_exact"] = True

        # 3. a certificate the stored fault now meets
        if "d_certified" in row and not CF.rests_on_certificate(row) \
                and row["d_upper"] == row["d_certified"] \
                and not row["d_certified_is_exact"]:
            row["d_certified_is_exact"] = True
            note = (f"; a fault of weight {row['d_upper']} found on Zaratan "
                    f"({EVIDENCE}) meets it")
            if note not in row["d_certified_source"]:
                row["d_certified_source"] += note
        if json.dumps(row, sort_keys=True) != before:
            changed.append(row)
    return changed


def _changes(payload):
    """Whether writing ``payload`` would change any of the three files."""
    real = (CF.CATALOG_JSON, CF.CATALOG_LARGE_JSON, CF.CATALOG_MD)
    with tempfile.TemporaryDirectory() as scratch:
        trial = [Path(scratch) / path.name for path in real]
        if real[1].exists():
            trial[1].write_text("", encoding="utf-8")
        CF.write_all(payload, *trial)
        return any((path.read_text(encoding="utf-8") if path.exists() else None)
                   != (out.read_text(encoding="utf-8") if out.exists() else None)
                   for path, out in zip(real, trial))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load_all()
    evidence = json.loads((REPO / EVIDENCE).read_text(encoding="utf-8"))
    changed = apply(payload, evidence)
    for row in changed:
        relation = "=" if row.get("d_certified_is_exact") else ">="
        print(f"  {row['catalog_label']}: certified d {relation} "
              f"{row.get('d_certified')}, d_upper {row['d_upper']}")
    for row in changed:
        started = time.time()
        _facts, problems = VC.verify_row(row)
        print(f"  verified {row['catalog_label']} in {time.time() - started:.0f}s"
              + ("" if not problems else f": {problems}"))
        if problems:
            raise SystemExit("a changed row fails verification; nothing written")
    residue = [p for row in payload["factories"] for p in VC.certificate_problems(row)]
    residue += VC.header_problems(payload) + VC.duplicate_label_problems(payload["factories"])
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the catalogue fails a file-level check; nothing written")
    print(f"{len(changed)} row(s) changed")
    if args.dry_run or not _changes(payload):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write_all(payload)
    VC.persist_metric_cache()
    print("wrote master_catalog.json, master_catalog_large.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
