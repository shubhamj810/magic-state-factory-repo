#!/usr/bin/env python3
"""One-off migration: record the distances the gamma frontier release certifies.

    python master_catalog/migrations/distance_certificates_2026_09_16.py [--dry-run]

The gamma frontier merge (commit fa249ad) stored every release circuit with the
distance this folder proved.  At the largest lengths that is only a floor --
the sweep below the release's stated ``d`` is out of reach -- so six rows read
weaker than the release certifies.  This copies the release's statement onto
those rows as ``d_certified`` / ``d_certified_is_exact`` / ``d_certified_source``
and touches nothing else: ``d``, ``d_is_exact`` and every circuit field stay
what was proved here.

A row gets a certificate exactly when one of its ``gamma frontier`` sources is
a record of ``frontier.json`` whose stated ``d`` exceeds the row's proved,
non-exact ``d``.  The release's ``distance_kind`` (``exact`` or
``lower_bound``) becomes ``d_certified_is_exact``; the release itself says
which, and a lower bound is never shown as a value.

Certificates are not carried by `merge_results`: an improvement that replaces
one of these circuits drops them, and re-running the gamma frontier merge from
scratch does not recreate them.  Re-run this script after either.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE.parent
sys.path.insert(0, str(CATALOGUE))

import catalogfile as CF                                          # noqa: E402
import verify_catalog as VC                                       # noqa: E402

FRONTIER = CATALOGUE.parent / "gamma_frontier_release" / "frontier.json"
REGIME = "gamma frontier"
KINDS = {"exact": True, "lower_bound": False}


def release_records(path=FRONTIER):
    records = {}
    for record in json.loads(path.read_text())["all_protocols"]:
        if record["distance_kind"] not in KINDS:
            raise SystemExit(f"{record['id']}: distance_kind "
                             f"{record['distance_kind']!r} is neither exact nor "
                             f"a lower bound; refusing to guess")
        records[record["id"]] = record
    return records


def certify(payload, records):
    certified = []
    for row in payload["factories"]:
        for name in VC.CERTIFICATE_FIELDS:
            row.pop(name, None)
        if row["d_is_exact"]:
            continue
        best = None
        for source in row["sources"]:
            record = records.get(source.get("label"))
            if source.get("regime") != REGIME or record is None:
                continue
            if record["n"] != row["n"] or record["k"] != row["k"]:
                raise SystemExit(f"source {record['id']} is [[{record['n']},"
                                 f"{record['k']}]] but cited by row "
                                 f"[[{row['n']},{row['k']}]]")
            if record["d"] > row["d"] and (best is None or record["d"] > best["d"]):
                best = record
        if best is None:
            continue
        row["d_certified"] = best["d"]
        row["d_certified_is_exact"] = KINDS[best["distance_kind"]]
        row["d_certified_source"] = (
            f"gamma frontier release record {best['id']} "
            f"(gamma_frontier_release/frontier.json, distance_kind "
            f"{best['distance_kind']}, Z distance)")
        certified.append(row)
    return certified


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load()
    certified = certify(payload, release_records())
    for row in certified:
        relation = "=" if row["d_certified_is_exact"] else ">="
        print(f"  [[{row['n']},{row['k']},>={row['d']}]]  certified d "
              f"{relation} {row['d_certified']}")
    print(f"{len(certified)} row(s) carry a release distance certificate")
    residue = [p for row in payload["factories"]
               for p in VC.certificate_problems(row)]
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("a certificate is inconsistent; nothing written")
    if args.dry_run:
        print("dry run: nothing written")
        return 0
    CF.write(payload)
    print("wrote master_catalog.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
