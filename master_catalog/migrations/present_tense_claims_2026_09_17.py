#!/usr/bin/env python3
"""One-off migration: state two regime claims as they stand, without their edit history.

    python master_catalog/migrations/present_tense_claims_2026_09_17.py [--dry-run]

Two header regime sentences carried notes about their own earlier wording --
when a correction was made, and what an earlier revision of the sentence said.
A reader of `MASTER_CATALOG.md` needs the claim, not its history (git keeps
that).  This rewrites exactly those two sentences to the claim they already
make, updates ``strongest_claim`` on every row whose strongest regime is one of
them, and re-renders both files.  No number and no other field changes.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import catalogfile as CF                                          # noqa: E402
import verify_catalog as VC                                       # noqa: E402

CLAIMS = {
    "AI search: pure-T width campaign n=255, 511": (
        "new [[n,k,d]] classes at n=255 and n=511 (the n=511 one the first at "
        "d=3 there) -- pure disjoint T^k, verified from columns. NOT rate "
        "records: both are strictly dominated by direct sums of the catalogued "
        "[[127,23,3]] (rho 5.5217) -- 2 copies give [[254,46,3]] and 4 give "
        "[[508,92,3]], each with FEWER inputs and MORE outputs than the row "
        "here. Beating the derived baseline needs k>=47 at n=255 and k>=93 at "
        "n=511."),
    "AI search: full-simplex pure-T frames": (
        "widest pure-T frames held at n=511. DOMINATED on rate by the derived "
        "direct-sum baseline [[508,92,3]] = 4 x [[127,23,3]], rho = 508/92 = "
        "5.5217. These are WIDTH points, explicitly NOT rate records: beating "
        "the baseline at n=511 needs k >= 93."),
}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load()
    header = payload["regimes"]
    for regime, sentence in CLAIMS.items():
        if regime not in header:
            raise SystemExit(f"the header has no regime {regime!r}")
        print(f"{regime}:\n  was: {header[regime]}\n  now: {sentence}")
        header[regime] = sentence
    touched = 0
    for row in payload["factories"]:
        if row["regimes"][0] in CLAIMS:
            row["strongest_claim"] = header[row["regimes"][0]]
            touched += 1
    print(f"{touched} row(s) re-read their strongest_claim")
    residue = VC.provenance_problems(payload) + VC.header_problems(payload)
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the header would be inconsistent; nothing written")
    if args.dry_run:
        print("dry run: nothing written")
        return 0
    CF.write(payload)
    print("wrote master_catalog.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
