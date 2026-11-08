#!/usr/bin/env python3
"""One-off migration: file 742.36.8.a and 756.32.9.a under San-José's GRS construction.

    python master_catalog/migrations/provenance_742_756_2026_11_07.py [--dry-run]

The two rows came from the gamma frontier release's records weighted_sources_742_36_8 and
weighted_sources_756_32_9. Their recipes (gamma_frontier_release/sources/gamma_frontier/
weighted_sources/protocol_742_36_8.json and protocol_756_32_9.json) have category
san_jose_grs and source arXiv:2609.08203, and the release's build.py builds them with its
San-José function grs(). The columns rebuild from that construction byte for byte
(research/search2/catalogue/stage3/PROVENANCE_742_756.md). The migration of 2026-09-16
(length54_classification_2026_09_16.py, gamma_regime) sent every weighted_sources_ record to
"AI search (gamma frontier): from Wills parent codes", which is right for the release's three
weighted-monomial recipes and wrong for these two. This script moves them to "AI search (gamma
frontier): San José GRS construction", the regime of the other 84 release San-José rows, with its
sentence as strongest_claim, names the recipe in the source's origin and says so in its
provenance. The 2026-09-16 rule now keys on the recipe's category, so a re-run cannot undo this.
The finding agrees with the lead's independent review
(research/search2/lead/PROVENANCE_REVIEW_742_756.md). discovery ("AI search") and
citations (["jain2026symmetry"]) do not change. Only provenance changes; the file-level checks
pass before anything is written. Idempotent.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import catalogfile as CF                                          # noqa: E402
import constructions as K                                         # noqa: E402
import distance_policy_2026_11_07 as DP                           # noqa: E402
import verify_catalog as VC                                       # noqa: E402

WILLS = "AI search (gamma frontier): from Wills parent codes"
SJ = "AI search (gamma frontier): San José GRS construction"
ROWS = {
    "742.36.8.a": ("a4348bc8e0b996ac86c46491222def83bf939517af730b1c3fa508d397ddc940",
                   "weighted_sources_742_36_8", "protocol_742_36_8.json", 9,
                   "96ffe2906670c55300754e0a7fef194b4be7a53070cde236c9a62dc8683c8cac"),
    "756.32.9.a": ("1579d68f282d560082494a9379ca7cd23bcd73f14f7a582b0aa7c1019e723280",
                   "weighted_sources_756_32_9", "protocol_756_32_9.json", 8,
                   "ba34463d65b21c8f238dd4ec40de3693ab7a73f3b91fa666be3b6c3bab631a8d"),
}
ORIGIN = ("the gamma frontier release's recipe sources/gamma_frontier/weighted_sources/{file} "
          "(SHA-256 {sha}), category san_jose_grs: San-José's GRS construction, arXiv:2609.08203, "
          "over GF(64) with L = 62, degree 15 and P = {P}")
NOTE = ("; the release's recipe (gamma_frontier_release/sources/gamma_frontier/weighted_sources/{file}, "
        "category san_jose_grs) is San-José's GRS construction (arXiv:2609.08203) over GF(64) with "
        "L = 62, degree 15 and P = {P}, built by that folder's build.py; until 2026-11-07 the row was "
        "filed under Wills parent codes because of the folder's name")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load_all()
    by = {row["catalog_label"]: row for row in payload["factories"]}
    for label, (digest, release_id, recipe, P, sha) in ROWS.items():
        row = by[label]
        if K.digest(row["columns"]) != digest:
            raise SystemExit(f"{label} does not store the circuit {digest[:16]}...")
        (source,) = row["sources"]
        if source["label"] != release_id:
            raise SystemExit(f"{label}'s source is not the release record {release_id}")
        if row["discovery"] != "AI search" or row["citations"] != ["jain2026symmetry"]:
            raise SystemExit(f"{label}'s credit is not the one this script expects")
        row["regimes"] = [SJ]
        row["strongest_claim"] = payload["regimes"][SJ]
        source["regime"] = SJ
        source["origin"] = ORIGIN.format(file=recipe, sha=sha, P=P)
        note = NOTE.format(file=recipe, P=P)
        if note not in source["provenance"]:
            source["provenance"] = source["provenance"] + note
        print(f"  {label}: regime {SJ!r}")
    rows = payload["factories"]
    residue = (VC.duplicate_label_problems(rows) + VC.provenance_problems(payload)
               + VC.citation_problems(payload) + VC.header_problems(payload))
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the catalogue fails a file-level check; nothing written")
    if args.dry_run or not DP._changes(payload):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write_all(payload)
    print("wrote master_catalog.json, master_catalog_large.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
