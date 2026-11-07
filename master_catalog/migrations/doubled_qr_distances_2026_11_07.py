#!/usr/bin/env python3
"""One-off migration: the 18 doubled codes from [[1301,1,21]] on take the
doubling theorem's distance, with the paper's Table II distances as inputs.

    python master_catalog/migrations/doubled_qr_distances_2026_11_07.py [--dry-run]

The 18 codes of ``transversal_t_codes/`` that double a quantum QR code of
length 167, 191 or 199 rest on the minimum distances 24, 28 and 32 of the
extended QR codes of length 168, 192 and 200.  Jain and Albert
(arXiv:2408.12752) state them in their Table II; this repository does not
re-prove all of them.  The owner's decision of 2026-11-07: "for any certified
lower bound that we are sure of such as this one, we should store the distance
as that", which counts the Table II distances as sure.  So
``transversal_t_codes/certify_distances.py`` now writes a record for each of
the 18 codes, under its own tool, listing in ``rests_on_paper`` the Table II
distances it takes and in ``proved_here`` what this repository proves for it.

This script, idempotent:

1.  promotes every row whose certificate an evidence file the catalogue is
    sure of now states (`distance_policy_2026_11_07.adopt`, the same rule as
    the first promotion): ``d`` becomes the certified bound, the sweep's floor
    goes to ``d_sweep_floor``, and the row is relabelled, keeping its old
    label in ``former_labels``.  Exactly the 18 rows must move;
2.  brings each row's entries for ``transversal_t_codes/distance_certificates.json``
    in line with the record that file now holds for its circuit, so that when
    an input distance becomes proved here (the extended QR code [168,84],
    `transversal_t_codes/xqr168_distance.json`) the tool a row cites follows;
3.  sets the certificate text of each of the 18 rows to its build text from
    ``codes.json`` plus one sentence that says what the bound rests on: the
    Table II distances it takes, and the in-repository proof of the [168,84]
    distance once there is one.  The text of the other 21 codes, which other
    migrations extended, is left alone.

Every changed row passes `verify_catalog.verify_row`, the file-level checks
pass over both files, and only then is anything written.
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

EVIDENCE = "transversal_t_codes/distance_certificates.json"
CODES = REPO / "transversal_t_codes" / "codes.json"
FACTORIES = "transversal_t_codes/factories.json"
#: The 18 rows the first step moves, by their label before it.
EXPECTED = {f"{n}.1.3.a" for n in (1301, 1317, 1345, 1635, 1651, 1679, 2017,
                                    2033, 2061, 2399, 2415, 2443, 2797, 2813,
                                    2841, 3195, 3211, 3239)}
#: The sentence a code with the [168,84] distance proved here carries.
PROVED_168 = ("; the minimum distance 24 of the extended QR code [168,84] that "
              "it rests on is proved in this repository by the Brouwer-Zimmermann "
              "bound of transversal_t_codes/bz_bound.c "
              "(transversal_t_codes/xqr168_distance.json)")


def chain(record, by_label):
    """The record and the records of its inner codes, outermost first."""
    out = [record]
    while out[-1]["inner_code"] in by_label:
        out.append(by_label[out[-1]["inner_code"]])
    return out


def self_dual_length(record, by_label):
    inner = by_label.get(record["inner_code"])
    return (record["n"] - (inner["n"] if inner else 1)) // 2


def note(record, by_label):
    """The sentence a code's certificate text ends with, from its record."""
    paper = record.get("rests_on_paper") or []
    uses_168 = any(self_dual_length(r, by_label) == 167
                   and "self_dual_distance_proved_by" in r
                   for r in chain(record, by_label))
    out = ""
    if paper:
        out = ("; it rests on " + " and on ".join(paper) + ", as the owner "
               "decided on 2026-11-07; the doubling theorem and every other "
               "input distance along its chain are proved in transversal_t_codes/ "
               f"({EVIDENCE})")
    if uses_168:
        out += PROVED_168
    return out


def label_of(row):
    """The row's id in `transversal_t_codes/factories.json`, or ``None``."""
    ids = [s["label"] for s in row.get("sources") or [] if s.get("file") == FACTORIES]
    return ids[0] if ids else None


def sync(payload):
    """Steps 2 and 3; the labels of the rows changed."""
    records, problem = VC.evidence_records(EVIDENCE)
    if problem:
        raise SystemExit(problem)
    by_digest = {r["columns_sha256"]: r for r in records}
    by_label = {r["label"]: r for r in records}
    base = {c["id"]: c["distance_certificate"]
            for c in json.loads(CODES.read_text(encoding="utf-8"))["codes"]}
    changed = []
    for row in payload["factories"]:
        code = label_of(row)
        if code is None or "d_certified" not in row:
            continue
        record = by_digest.get(CO.digest(row["columns"]))
        if record is None or record["label"] != code:
            raise SystemExit(f"{row['catalog_label']}: no record of {EVIDENCE} "
                             f"for its circuit")
        before = json.dumps(row, sort_keys=True)
        if CF.rests_on_certificate(row):
            entry = {"file": EVIDENCE, "method": record["method"],
                     "tool": record["tool"]}
            others = [e for e in row["d_certified_evidence"] if e["file"] != EVIDENCE]
            row["d_certified_evidence"] = [entry] + others
        if any(self_dual_length(r, by_label) >= 167
               for r in chain(record, by_label)):
            text = row["d_certified_source"]
            if not (text == base[code] or text.startswith(base[code] + "; it rests on ")
                    or text.startswith(base[code] + PROVED_168)):
                raise SystemExit(f"{row['catalog_label']}: the certificate text "
                                 f"is not one this script wrote")
            row["d_certified_source"] = base[code] + note(record, by_label)
        if json.dumps(row, sort_keys=True) != before:
            changed.append(row["catalog_label"])
    return changed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load_all()
    main_rows = [row for row in payload["factories"] if not CF.is_large(row)]
    if main_rows != sorted(main_rows, key=DP.MR.sort_key):
        raise SystemExit("the main file is not in the catalogue's sort order")
    moved, left = DP.adopt(payload)
    old_labels = {old for old, _floor, _row in moved}
    if old_labels and old_labels != EXPECTED:
        raise SystemExit(f"step 1 would move {sorted(old_labels)}, not the 18 rows")
    DP.resort(payload)
    touched = sync(payload)
    for old, floor, row in moved:
        print(f"  {old} -> {row['catalog_label']}: d {floor} -> {row['d']} "
              f"({CF.distance_basis(row)}), A_d {row['A_d']}")
    for row in left:
        print(f"  left {row['catalog_label']}: certificate d >= "
              f"{row['d_certified']} has no evidence file the catalogue is sure of")
    print(f"  certificate text or evidence brought up to date on {len(touched)} row(s)")
    labels = set(touched) | {row["catalog_label"] for _o, _f, row in moved}
    for row in payload["factories"]:
        if row["catalog_label"] not in labels:
            continue
        started = time.time()
        _facts, problems = VC.verify_row(row)
        print(f"  verified {row['catalog_label']} in {time.time() - started:.0f}s"
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
    print(f"{len(moved)} row(s) relabelled, {len(labels)} row(s) changed")
    if args.dry_run or not DP._changes(payload):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write_all(payload)
    VC.persist_metric_cache()
    print("wrote master_catalog.json, master_catalog_large.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
