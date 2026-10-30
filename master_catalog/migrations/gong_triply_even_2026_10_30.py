#!/usr/bin/env python3
"""One-off migration: merge A. Gong's four triply even transversal-T codes.

    python master_catalog/migrations/gong_triply_even_2026_10_30.py [--dry-run]

In a note in her repository github.com/gongaa/RM127 (``triply-even/``, 2025),
A. Gong found two doubly even self-dual CSS codes, ``[[41,1,9]]`` and
``[[65,1,13]]``, and doubled them with the quantum QR codes of length 47 and 79
onto ``[[95,1,7]]``.  That gives ``[[177,1,9]]``, ``[[271,1,11]]``,
``[[401,1,13]]`` and ``[[559,1,15]]``, each shorter than the code of the same
distance in Jain and Albert's Tables I and II (185, 279, 417 and 575 qubits in
Table I).  Every X stabiliser weighs 0 mod 8, so ``T`` on every qubit is the
logical ``T`` or ``T``-dagger and no S or CZ correction is needed.
`transversal_t_codes/build_codes.py` rebuilds the four from her two self-dual
codes (`transversal_t_codes/gong_self_dual_codes.json`) and writes them to
``transversal_t_codes/factories.json`` as ``G-177`` ... ``G-559``.  In order,
this script:

1.  **Adds the work** the new rows credit, ``gong2025triply``, to the header's
    ``references``, dated by the commit that added the note (2025-04-10), and
    names her codes in the ``scope`` and ``discovery`` sentences.
2.  **Merges the four records** through `merge_results.merge`.  Each is a new
    class, credited to her note alone.
3.  **States the distances.**  The sweep proves only a floor at these lengths.
    Each row gets the doubling theorem's distance as ``d_certified``, a lower
    bound, and the explicit fault of exactly that weight the build makes as
    ``d_upper`` and ``d_witness``.  The theorem needs the self-dual inputs'
    distances, which the tests prove by enumerating every word of their
    stabiliser spaces (largest weights 32 and 52, so distances 9 and 13).
4.  **Shows the transversal gate**: ``T`` on every qubit is the logical
    ``T^m``, ``m = n mod 8``, so ``rotation_powers`` is empty when ``m = 1`` and
    ``T``-dagger on every qubit when ``m = 7``.

Every changed row passes `verify_catalog.verify_row` in full before anything is
written.  A second run writes nothing.
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
import merge_results as MR                                        # noqa: E402
import verify_catalog as VC                                       # noqa: E402

FACTORIES = "transversal_t_codes/factories.json"
CODES = REPO / "transversal_t_codes" / "codes.json"
REGIME = "Gong doubling: triply even family"

REFERENCES = {
    "gong2025triply": {
        "short": "Gong (2025)",
        "full": "A. Gong, \"On some K=1 codes admitting strongly transversal "
                "T,\" note in the RM127 repository, triply-even/ (2025).",
        "url": "https://github.com/gongaa/RM127/tree/main/triply-even",
        "date": "2025-04-10",
    },
}

SCOPE_OLD = ("from the doubled transversal-T codes of Jain and Albert "
             "(transversal_t_codes/), ")
SCOPE_NEW = ("from the doubled transversal-T codes of Jain and Albert and of "
             "A. Gong (transversal_t_codes/), ")
DISCOVERY_OLD = "the codes of Jain and Albert rebuilt in transversal_t_codes/"
DISCOVERY_NEW = ("the codes of Jain and Albert and of A. Gong rebuilt in "
                 "transversal_t_codes/")


def update_header(payload):
    said = []
    references = payload["references"]
    for key, entry in REFERENCES.items():
        if references.get(key) != entry:
            references[key] = dict(entry)
            said.append(f"reference {key}: {entry['full']}")
    if SCOPE_OLD in payload["scope"]:
        payload["scope"] = payload["scope"].replace(SCOPE_OLD, SCOPE_NEW)
        said.append("scope names Gong's codes")
    glossary = payload["discovery"]
    if DISCOVERY_OLD in glossary["pre-existing"] and DISCOVERY_NEW not in glossary["pre-existing"]:
        glossary["pre-existing"] = glossary["pre-existing"].replace(
            DISCOVERY_OLD, DISCOVERY_NEW)
        said.append("discovery glossary names Gong's codes")
    return said


def certify(payload, codes, regime=REGIME, triply_even=True):
    """Certificates and witnesses on the rows of ``regime``, and, for a triply
    even family, the transversal gate: ``T`` on every qubit."""
    changed = []
    by_label = {entry["id"]: entry for entry in codes}
    for row in payload["factories"]:
        mine = [s for s in row["sources"] if s["regime"] == regime]
        if not mine or row["d_is_exact"]:
            continue
        entry = by_label[mine[0]["label"]]
        claim = entry["parameters"][2]
        before = json.dumps(row, sort_keys=True)
        if row["d_upper"] is None or row["d_upper"] > claim:
            row["d_upper"], row["d_witness"] = claim, list(entry["witness"])
        if triply_even:
            m = entry["weak_triply_even"]["m"]
            row["rotation_powers"] = [] if m == 1 else [[c, 7] for c in range(row["n"])]
        row["d_certified"] = claim
        row["d_certified_is_exact"] = False
        row["d_certified_source"] = entry["distance_certificate"]
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


def main(argv=None, prefix="G-", regime=REGIME, triply_even=True,
         header=update_header, description=__doc__):
    parser = argparse.ArgumentParser(description=description.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load_all()
    before = len(payload["factories"])
    for line in header(payload):
        print(line)

    records = [r for r in MR.read_records(REPO / FACTORIES)
               if r["label"].startswith(prefix)]
    started = time.time()
    verdicts = MR.merge(payload, records, FACTORIES)
    print(f"merged {len(records)} records in {time.time() - started:.0f}s:")
    touched = []
    for index, verdict, row, detail in verdicts:
        label = records[index]["label"]
        if verdict == "rejected":
            print(f"  {label}: REJECTED {detail}")
            raise SystemExit("a record was rejected; nothing written")
        print(f"  {label}: {verdict} as {row['catalog_label']}"
              + (f" ({detail})" if detail else ""))
        if verdict in ("accepted", "improved"):
            touched.append(row)

    codes = json.loads(CODES.read_text(encoding="utf-8"))["codes"]
    certified = certify(payload, codes, regime, triply_even)
    for row in certified:
        print(f"  {row['catalog_label']}: certified d >= {row['d_certified']}, "
              f"witness of weight {row['d_upper']}")
    changed = {id(row): row for row in touched + certified}
    for row in changed.values():
        started = time.time()
        _facts, problems = VC.verify_row(row)
        print(f"  verified {row['catalog_label']} in {time.time() - started:.0f}s"
              + ("" if not problems else f": {problems}"))
        if problems:
            raise SystemExit("a merged row fails verification; nothing written")
    residue = (VC.duplicate_class_problems(payload["factories"])
               + VC.duplicate_label_problems(payload["factories"])
               + VC.provenance_problems(payload)
               + VC.citation_problems(payload)
               + VC.header_problems(payload))
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the merged catalogue fails a file-level check; "
                         "nothing written")
    print(f"{before} -> {len(payload['factories'])} classes")
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
