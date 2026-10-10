#!/usr/bin/env python3
"""One-off migration: merge the transversal-T codes of Jain and Albert.

    python master_catalog/migrations/transversal_t_codes_2026_10_10.py [--dry-run]

S. P. Jain and V. V. Albert, "Transversal Clifford and T-gate codes of short
length and high distance", IEEE J. Sel. Areas Inf. Theory 6, 127 (2025),
arXiv:2408.12752, build one-qubit codes with a transversal logical ``T`` by
doubling.  `transversal_t_codes/build_codes.py` rebuilds every code the paper
lists that can be built -- all fifteen of its Table II and the first five of
its Table I, seventeen distinct codes -- and writes them as factory records in
``transversal_t_codes/factories.json``.  In order, this script:

1.  **Adds the works** the new rows credit to the header's ``references``: the
    paper itself (``jain2025transversal``) and M. Sullivan, "Code conversion
    with the quantum Golay code for a universal transversal gate set", Phys.
    Rev. A 109, 042416 (2024) (``sullivan2024code``), the earliest publication
    of the ``[[95,1,7]]`` code.  Their dates are Crossref's: Sullivan's article
    appeared on 2024-04-18; for the paper Crossref records only the year, and
    2025-05-16 is the date it registered the article, its early-access date.
    The ``scope`` and ``discovery`` sentences name the new source.
2.  **Merges the records** through `merge_results.merge`, the bar every merge
    clears.  Their two regimes are registered by the merge, at the end of the
    header's order, as witnesses.  The ``[[15,1,3]]`` and ``[[49,1,5]]`` codes
    are classes the catalogue already holds with a smaller circuit, so they are
    duplicates and change nothing; their records name no citation, so the held
    rows keep their credit.  ``[[95,1,7]]`` is a new class, credited to
    Sullivan alone; every other code is new and credited to the paper.
3.  **States the paper's distances.**  The sweep proves only a floor for the
    codes above ``n = 95`` -- 7 through ``n = 283``, 6 through ``n = 1011``, 3
    beyond.  Each such row gets the paper's distance as a certificate,
    ``d_certified``, as a LOWER bound (``d_certified_is_exact: false``), whose
    source is the doubling theorem; and, where the sweep did not already find
    one, the explicit fault of exactly that weight `build_codes.py` builds
    (two qubits of each self-dual block plus the smaller code's fault), as
    ``d_upper`` and ``d_witness``.  The verifier re-checks that fault against
    the true syndromes, so the distance is pinned between the certified lower
    bound and the exhibited fault.
4.  **Shows the paper's transversal gate.**  A weak triply even code (Table
    II) is the logical ``T^m`` under ``T`` on ``M+`` and ``T-dagger`` on
    ``M-``, ``m = 7``; scaled by ``m^-1 = 7`` that is the logical ``T`` with
    ``T-dagger`` on ``M+`` and ``T`` on ``M-``.  Those powers replace the
    merge's own ``rotation_powers`` solution on these rows -- any valid list
    passes the verifier, and this one is the paper's.

Every changed row then passes `verify_catalog.verify_row` in full before
anything is written.  A second run finds every code held and writes nothing.
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

import catalogfile as CF                                          # noqa: E402
import merge_results as MR                                        # noqa: E402
import verify_catalog as VC                                       # noqa: E402

FACTORIES = "transversal_t_codes/factories.json"
CODES = REPO / "transversal_t_codes" / "codes.json"
REGIMES = ("Jain-Albert doubling: weak triply even family",
           "Jain-Albert doubling: triorthogonal family")

REFERENCES = {
    "jain2025transversal": {
        "short": "Jain & Albert (2025)",
        "full": "S. P. Jain and V. V. Albert, \"Transversal Clifford and T-gate "
                "codes of short length and high distance,\" IEEE J. Sel. Areas "
                "Inf. Theory 6, 127-137 (2025); arXiv:2408.12752.",
        "url": "https://doi.org/10.1109/JSAIT.2025.3570832",
        "date": "2025-05-16",
    },
    "sullivan2024code": {
        "short": "Sullivan (2024)",
        "full": "M. Sullivan, \"Code conversion with the quantum Golay code for "
                "a universal transversal gate set,\" Phys. Rev. A 109, 042416 "
                "(2024).",
        "url": "https://doi.org/10.1103/PhysRevA.109.042416",
        "date": "2024-04-18",
    },
}

SCOPE_OLD = ("from the borrowed-identity searches of Singh, Gidney and Jones "
             "(borrowed_identities/), and from search campaigns")
SCOPE_NEW = ("from the borrowed-identity searches of Singh, Gidney and Jones "
             "(borrowed_identities/), from the doubled transversal-T codes of "
             "Jain and Albert (transversal_t_codes/), and from search campaigns")
DISCOVERY_OLD = "the borrowed-identity searches, the exhaustive"
DISCOVERY_NEW = ("the borrowed-identity searches, the codes of Jain and Albert "
                 "rebuilt in transversal_t_codes/, the exhaustive")


def update_header(payload):
    said = []
    references = payload["references"]
    for key, entry in REFERENCES.items():
        if references.get(key) != entry:
            references[key] = dict(entry)
            said.append(f"reference {key}: {entry['full']}")
    if SCOPE_OLD in payload["scope"]:
        payload["scope"] = payload["scope"].replace(SCOPE_OLD, SCOPE_NEW)
        said.append("scope names transversal_t_codes/")
    glossary = payload["discovery"]
    if DISCOVERY_OLD in glossary["pre-existing"]:
        glossary["pre-existing"] = glossary["pre-existing"].replace(
            DISCOVERY_OLD, DISCOVERY_NEW)
        said.append("discovery glossary names transversal_t_codes/")
    return said


def certify(payload, codes):
    """Certificates and witnesses on the rows the paper's codes became."""
    changed = []
    by_label = {entry["id"]: entry for entry in codes}
    for row in payload["factories"]:
        mine = [s for s in row["sources"] if s["regime"] in REGIMES]
        if not mine or row["d_is_exact"]:
            continue
        entry = by_label[mine[0]["label"]]
        claim = entry["parameters"][2]
        before = json.dumps(row, sort_keys=True)
        if row["d_upper"] is None or row["d_upper"] > claim:
            row["d_upper"], row["d_witness"] = claim, list(entry["witness"])
        wte = entry["weak_triply_even"]
        if wte is not None:
            inverse = {1: 1, 7: 7}[wte["m"]]           # m * m = 1 mod 8
            minus = set(wte["minus"])
            row["rotation_powers"] = [
                [c, (inverse * (-1 if c in minus else 1)) % 8]
                for c in range(row["n"])
                if (inverse * (-1 if c in minus else 1)) % 8 != 1]
        row["d_certified"] = claim
        row["d_certified_is_exact"] = False
        row["d_certified_source"] = entry["distance_certificate"]
        if json.dumps(row, sort_keys=True) != before:
            changed.append(row)
    return changed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load()
    said = update_header(payload)
    for line in said:
        print(line)

    records = MR.read_records(REPO / FACTORIES)
    started = time.time()
    verdicts = MR.merge(payload, records, FACTORIES)
    print(f"merged {len(records)} records in {time.time() - started:.0f}s:")
    rejected = False
    touched = []
    for index, verdict, row, detail in verdicts:
        label = records[index]["label"]
        if verdict == "rejected":
            rejected = True
            print(f"  {label}: REJECTED {detail}")
            continue
        where = row["catalog_label"]
        print(f"  {label}: {verdict} as {where}"
              + (f" ({detail})" if detail else ""))
        if verdict in ("accepted", "improved"):
            touched.append(row)
    if rejected:
        raise SystemExit("a record was rejected; nothing written")

    codes = json.loads(CODES.read_text(encoding="utf-8"))["codes"]
    certified = certify(payload, codes)
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
    residue = (VC.citation_problems(payload) + VC.header_problems(payload)
               + VC.provenance_problems(payload)
               + VC.duplicate_label_problems(payload["factories"]))
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the catalogue would fail its checks; nothing written")
    if args.dry_run or not (said or changed):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    payload["n_classes"] = len(payload["factories"])
    CF.write(payload)
    print(f"wrote master_catalog.json and MASTER_CATALOG.md "
          f"({payload['n_classes']} classes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
