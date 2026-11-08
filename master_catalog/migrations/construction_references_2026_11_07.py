#!/usr/bin/env python3
"""One-off migration: San-José's and Wills's papers in the references, named
in the provenance of the rows built from their constructions.

    python master_catalog/migrations/construction_references_2026_11_07.py [--dry-run]

The owner's decision of 7 November 2026: "you can put them in references,
credit the AI search but put these papers in the provenance". So:

* the header's ``references`` gains R. San-José, "Asymptotically good binary
  triorthogonal codes and higher-level transversal gates", arXiv:2609.08203,
  and A. Wills, "Improved Quantum Codes with Transversal T Gates",
  arXiv:2608.24000. The titles, authors and arXiv numbers are as
  theorem_certificates/README.md and the gamma frontier release's
  sources/gamma_frontier/WILLS_CONSTRUCTIONS.md give them; the year is the
  one the arXiv number encodes (26xx, 2026). No ``date`` is given, since no
  file in the repository states a day;
* the regime sentence of "AI search (gamma frontier): from Wills parent
  codes" now names the paper (arXiv:2608.24000), as the other Wills regimes
  and both San-José regimes already do, and every row of that regime takes
  the new sentence as its ``strongest_claim``;
* ``citations`` and ``discovery`` do not change: these rows stay credited to
  the AI search that built them. The website shows a paper named in a row's
  regime sentence beside the provenance, not as its source.

Only the header and provenance change. The file-level checks pass before
anything is written. Idempotent.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import catalogfile as CF                                          # noqa: E402
import distance_policy_2026_11_07 as DP                           # noqa: E402
import verify_catalog as VC                                       # noqa: E402

REFERENCES = {
    "sanjose2026asymptotically": {
        "short": "San-José (2026)",
        "full": "R. San-José, \"Asymptotically good binary triorthogonal codes and "
                "higher-level transversal gates,\" arXiv:2609.08203 (2026).",
        "url": "https://arxiv.org/abs/2609.08203"},
    "wills2026improved": {
        "short": "Wills (2026)",
        "full": "A. Wills, \"Improved Quantum Codes with Transversal T Gates,\" "
                "arXiv:2608.24000 (2026).",
        "url": "https://arxiv.org/abs/2608.24000"},
}
WILLS = "AI search (gamma frontier): from Wills parent codes"
OLD = "built from one of Wills's parent codes (weighted Reed-Muller"
NEW = "built from one of Wills's parent codes (arXiv:2608.24000; weighted Reed-Muller"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load_all()
    references = payload["references"]
    for key, entry in REFERENCES.items():
        if key in references and references[key] != entry:
            raise SystemExit(f"the header already has a different {key}")
        clash = [k for k, e in references.items()
                 if k != key and entry["url"] in (e.get("url"), e.get("full", ""))]
        if clash:
            raise SystemExit(f"{entry['url']} is already the reference {clash}")
        references[key] = dict(entry)
    sentence = payload["regimes"][WILLS]
    if NEW not in sentence:
        if OLD not in sentence:
            raise SystemExit("the Wills regime sentence is not the one expected")
        payload["regimes"][WILLS] = sentence.replace(OLD, NEW)
    changed = 0
    for row in payload["factories"]:
        if row["regimes"][0] == WILLS and row["strongest_claim"] != payload["regimes"][WILLS]:
            row["strongest_claim"] = payload["regimes"][WILLS]
            changed += 1
    rows = payload["factories"]
    residue = (VC.duplicate_label_problems(rows) + VC.provenance_problems(payload)
               + VC.citation_problems(payload) + VC.header_problems(payload))
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the catalogue fails a file-level check; nothing written")
    print(f"{len(REFERENCES)} references; {changed} row(s) take the new sentence")
    if args.dry_run or not DP._changes(payload):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write_all(payload)
    print("wrote master_catalog.json, master_catalog_large.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
