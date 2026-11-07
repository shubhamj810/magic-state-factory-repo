#!/usr/bin/env python3
"""One-off migration: record the distances tropidist certifies on the open rows.

    python master_catalog/migrations/tropidist_certificates_2026_11_06.py [--dry-run]

tropidist, the exact distance solver of B. Cheng, N. Guo and F. Pan
("Certifying quantum code and circuit distances at scale", arXiv:2611.08247;
github.com/Fanerst/tropidist), was run on every row whose distance this folder
does not prove exactly.  Its results, bound to each row by the SHA-256 of its
columns, are in ``tropidist_certificates/certificates.json``.  The same runs
reproduced the exact distance of all 1,752 exact rows they were given.

For each record, in order:

1.  **A witness at the proved floor makes the row exact here.**  When tropidist
    returned a fault of weight ``d``, the row's own floor, the row becomes
    ``d_is_exact`` with that fault as ``d_witness``: the clean sweep below ``d``
    and the fault are both this folder's, and `verify_catalog` re-checks both.
    ``A_d`` is counted where `errorcoeff` reaches.  No certificate is needed.
2.  **A lighter witness than the stored one** replaces ``d_upper`` and
    ``d_witness``.  (A witness above the floor never lowers anything.)
3.  **A lower bound above the floor becomes a certificate**, unless the row
    already carries a stronger one.  It is exact when it meets ``d_upper``.
    A certificate of the same value as the existing one keeps that source and
    adds tropidist's; a stronger one replaces it.

``d`` is never raised, so no label changes.  Every changed row passes
`verify_catalog.verify_row` in full before anything is written, and a second
run writes nothing.
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
import verify_catalog as VC                                       # noqa: E402

CERTIFICATES = REPO / "tropidist_certificates" / "certificates.json"
SOURCE = ("tropidist (B. Cheng, N. Guo and F. Pan, arXiv:2611.08247; "
          "github.com/Fanerst/tropidist at {commit}) run here on 6 November 2026: "
          "{claim} (tropidist_certificates/certificates.json, record {label})")


def tropidist_source(record, commit, value, exact):
    claim = (f"d = {value}, a lower bound of {value} met by a fault of weight {value}"
             if exact else f"d >= {value}")
    return SOURCE.format(commit=commit[:8], claim=claim, label=record["label"])


def apply(payload, evidence):
    # a row relabelled since (its d became a certificate's, 2026-11-07) is
    # found by the label it had, which it keeps in former_labels
    rows = {label: row for row in payload["factories"]
            for label in [row["catalog_label"]] + (row.get("former_labels") or [])}
    commit = evidence["tropidist"]["commit"]
    changed = []
    for record in evidence["records"]:
        row = rows[record["label"]]
        for key in ("n", "k", "N"):
            if row[key] != record[key]:
                raise SystemExit(f"{record['label']}: {key} is {row[key]}, the "
                                 f"record says {record[key]}")
        if CO.digest(row["columns"]) != record["columns_sha256"]:
            raise SystemExit(f"{record['label']}: the columns are not the ones "
                             f"tropidist was run on")
        before = json.dumps(row, sort_keys=True)
        lower, witness = record["lower_bound"], record["witness"]
        if row["d_is_exact"] or CF.rests_on_certificate(row):
            continue
        if witness is not None and len(witness) != record["upper_bound"]:
            raise SystemExit(f"{record['label']}: witness weight disagrees")

        # 1. a witness at the floor: exact here, with this folder's proof
        if witness is not None and len(witness) == row["d"]:
            if any(name in row for name in VC.CERTIFICATE_FIELDS):
                raise SystemExit(f"{record['label']}: carries a certificate "
                                 f"below its own exact distance")
            row["d_is_exact"] = True
            row["d_upper"], row["d_witness"] = row["d"], list(witness)
            row["A_d"] = EC.error_coefficient(row["columns"], row["k"], row["N"],
                                              row["d"])["count"]
            changed.append(row)
            continue

        # 2. a lighter witness
        if witness is not None and (row["d_upper"] is None
                                    or len(witness) < row["d_upper"]):
            row["d_upper"], row["d_witness"] = len(witness), list(witness)

        # 3. a lower bound above the floor
        if lower > row["d"]:
            held = row.get("d_certified")
            exact = row["d_upper"] == lower
            if held is None or lower > held:
                row["d_certified"] = lower
                row["d_certified_is_exact"] = exact
                row["d_certified_source"] = tropidist_source(record, commit,
                                                             lower, exact)
            elif lower == held:
                ours = tropidist_source(record, commit, lower, exact)
                if ours not in row["d_certified_source"]:
                    row["d_certified_source"] += "; independently, " + ours
                row["d_certified_is_exact"] = row["d_certified_is_exact"] or exact
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
    evidence = json.loads(CERTIFICATES.read_text(encoding="utf-8"))
    changed = apply(payload, evidence)
    for row in changed:
        if row["d_is_exact"]:
            print(f"  {row['catalog_label']}: exact d = {row['d']} here, "
                  f"A_d = {row['A_d']}")
        else:
            relation = "=" if row["d_certified_is_exact"] else ">="
            print(f"  {row['catalog_label']}: certified d {relation} "
                  f"{row['d_certified']}, d_upper {row['d_upper']}")
    for row in changed:
        started = time.time()
        _facts, problems = VC.verify_row(row)
        print(f"  verified {row['catalog_label']} in {time.time() - started:.0f}s"
              + ("" if not problems else f": {problems}"))
        if problems:
            raise SystemExit("a changed row fails verification; nothing written")
    residue = [p for row in payload["factories"] for p in VC.certificate_problems(row)]
    residue += VC.header_problems(payload)
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
    print("wrote master_catalog.json, master_catalog_large.json and "
          "MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
