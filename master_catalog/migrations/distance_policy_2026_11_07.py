#!/usr/bin/env python3
"""One-off migration: a certificate the catalogue is sure of becomes the distance.

    python master_catalog/migrations/distance_policy_2026_11_07.py [--dry-run]

Until now ``d`` was always the floor of this folder's own sweep, and a stronger
proved bound sat beside it in ``d_certified``.  The owner's decision of
2026-11-07: where the catalogue is sure of a certificate, ``d`` is the
certified bound.  A certificate is sure when an evidence file in this
repository states it for the row's circuit (bound by the SHA-256 of its
columns) and comes from

* the doubling theorem of Jain and Albert, along a chain whose every input
  distance is proved in ``transversal_t_codes/`` (``distance_certificates.json``,
  written by ``transversal_t_codes/certify_distances.py``);
* tropidist, the exhaustive solver of Cheng, Guo and Pan, already accepted as a
  certificate source (``tropidist_certificates/certificates.json``); or
* the Zaratan runs of tropidist and the meet-in-the-middle kernel
  (``zaratan_certificates/certificates.json``, entered as certificates by
  ``zaratan_certificates_2026_11_07.py``).

For every row with ``d_certified > d`` and such evidence, in file order:

1.  ``d_sweep_floor`` keeps the sweep's floor, the old ``d``, and ``d``
    becomes ``d_certified``.
2.  ``d_is_exact`` is true when the row stores a fault of weight ``d``
    (``d_upper == d``), and ``d_certified_is_exact`` is set to it.  ``A_d`` is
    counted where `errorcoeff` reaches, and is otherwise null.
3.  ``d_certified_evidence`` lists every evidence record stating the bound.
4.  The row gets the next unused label at its new ``(n, k, d)``, by the scheme
    of ``catalog_labels_2026_10_06.py``, and its old label goes into
    ``former_labels``, so it is never handed out again.

A certificate with no such evidence stays beside ``d``, and the script says
why.  The rows are then put back in the catalogue's sort order, every changed
row passes `verify_catalog.verify_row`, the file-level checks (classes,
labels, certificates, header) pass over both files, and only then is anything
written.  A second run changes nothing.
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
import errorcoeff as EC                                           # noqa: E402
import merge_results as MR                                        # noqa: E402
import verify_catalog as VC                                       # noqa: E402

#: The evidence files whose records the catalogue is sure of, in the order a
#: row lists them.
SURE = ("transversal_t_codes/distance_certificates.json",
        "tropidist_certificates/certificates.json",
        "zaratan_certificates/certificates.json")


def sure_entries(row):
    """Every record of a sure evidence file stating the row's certificate for
    its circuit, as ``d_certified_evidence`` entries."""
    digest = CO.digest(row["columns"])
    entries = []
    for path in SURE:
        records, problem = VC.evidence_records(path)
        if problem:
            raise SystemExit(problem)
        for record in records:
            if record["columns_sha256"] == digest \
                    and record["lower_bound"] == row["d_certified"]:
                entry = {"file": path, "method": record["method"],
                         "tool": record["tool"]}
                if entry not in entries:
                    entries.append(entry)
    return entries


def adopt(payload):
    """Apply the policy in place; ``(changed, left)``."""
    rows = payload["factories"]
    changed, left = [], []
    for row in rows:
        if "d_certified" not in row or CF.rests_on_certificate(row):
            continue
        if row["d_certified"] <= row["d"]:
            continue
        entries = sure_entries(row)
        if not entries:
            left.append(row)
            continue
        old_label, floor, bound = row["catalog_label"], row["d"], row["d_certified"]
        row["d"] = bound
        row["d_is_exact"] = row["d_upper"] == bound and row["d_witness"] is not None
        row["A_d"] = (EC.error_coefficient(row["columns"], row["k"], row["N"], bound)
                      ["count"] if row["d_is_exact"] else None)
        row["d_certified_is_exact"] = row["d_is_exact"]
        listed = [e for e in row.get("d_certified_evidence") or [] if e not in entries]
        row["d_certified_evidence"] = entries + listed
        row["d_sweep_floor"] = floor
        row["former_labels"] = (row.get("former_labels") or []) + [old_label]
        row["catalog_label"] = CF.next_label(rows, row["n"], row["k"], bound)
        changed.append((old_label, floor, row))
    return changed, left


#: The header sentences that say how a distance is proved: each old text, the
#: part of it that changes, and what replaces that part.
HEADER = {
    "dedup_key": (
        "(n, k, d, gate up to GL(k,2)) -- circuits at different distances",
        "(n, k, d, gate up to GL(k,2)) -- d is the row's proved lower bound, the "
        "sweep's or, where the row carries d_sweep_floor, a certificate's; "
        "circuits at different distances"),
    "caveat": (
        "This table is their union, not a uniform claim.",
        "This table is their union, not a uniform claim. A row's d is proved by "
        "the exhaustive sweep of verify_catalog.py or, where the row carries "
        "d_sweep_floor, by a certificate the repository is sure of: a theorem "
        "whose hypotheses it checks, or an exhaustive search by another "
        "program, with its evidence file in the repository; d_sweep_floor is "
        "what the sweep alone proves. A certificate the repository cannot "
        "check stays in d_certified beside the sweep's d."),
    "verification": (
        "distance (absence proved by exhaustive enumeration, presence witnessed "
        "by an explicit fault)",
        "distance (absence proved by exhaustive enumeration below d, or below "
        "d_sweep_floor where a certificate proves the rest, its evidence file "
        "bound to the circuit by the SHA-256 of the columns; presence witnessed "
        "by an explicit fault, checked by faultcore and by the XOR of the wire "
        "masks)"),
}


def update_header(payload):
    """The header's account of how distances are proved, brought up to date."""
    for key, (old, new) in HEADER.items():
        text = payload[key]
        if new in text:
            continue
        if text.count(old) != 1:
            raise SystemExit(f"the header's {key} does not read as expected")
        payload[key] = text.replace(old, new)


def resort(payload):
    """Each file's rows back in the catalogue's sort order, after checking that
    they were in it apart from the rows this moved."""
    rows = payload["factories"]
    main = [row for row in rows if not CF.is_large(row)]
    large = [row for row in rows if CF.is_large(row)]
    if large != sorted(large, key=MR.sort_key):
        raise SystemExit("the large file is not in the catalogue's sort order")
    payload["factories"] = sorted(main, key=MR.sort_key) + large


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
    main_before = [row["catalog_label"] for row in payload["factories"]
                   if not CF.is_large(row)]
    sorted_before = [row["catalog_label"] for row in sorted(
        (row for row in payload["factories"] if not CF.is_large(row)),
        key=MR.sort_key)]
    if main_before != sorted_before:
        raise SystemExit("the main file is not in the catalogue's sort order")
    changed, left = adopt(payload)
    resort(payload)
    update_header(payload)
    for old, floor, row in changed:
        how = CF.distance_basis(row)
        print(f"  {old} -> {row['catalog_label']}: d {floor} -> "
              f"{'' if row['d_is_exact'] else '>='}{row['d']} ({how}), "
              f"A_d {row['A_d']}")
    for row in left:
        print(f"  left {row['catalog_label']}: certificate d >= {row['d_certified']} "
              f"has no evidence file the catalogue is sure of")
    for _old, _floor, row in changed:
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
    print(f"{len(changed)} row(s) changed, {len(left)} certificate(s) left beside d")
    if args.dry_run or not _changes(payload):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write_all(payload)
    VC.persist_metric_cache()
    print("wrote master_catalog.json, master_catalog_large.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
