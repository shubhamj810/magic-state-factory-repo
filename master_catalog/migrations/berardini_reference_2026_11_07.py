#!/usr/bin/env python3
"""One-off migration: add Berardini et al. to the header's references.

    python master_catalog/migrations/berardini_reference_2026_11_07.py [--dry-run]

Their Example 1, the [[753,1,17]] doubling of a cyclic [89,44] code onto the
[[575,1,15]] code of Jain and Albert, is imported on 2026-11-07 and credited to
them.  The entry was read off the paper's arXiv page on 2026-11-07 (no journal
reference is listed there; the comments say it was accepted by the IEEE
Journal on Selected Areas in Information Theory).  Idempotent.
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

KEY = "berardini2024asymptotically"
ENTRY = {
    "short": "Berardini et al. (2024)",
    "full": ("E. Berardini, R. Dastbasteh, J. Etxezarreta Martinez, S. Jain, and "
             "O. Sanz Larrarte, \"Asymptotically good CSS-T codes and a new "
             "construction of triorthogonal codes,\" arXiv:2412.08586 (2024)."),
    "url": "https://arxiv.org/abs/2412.08586",
    "date": "2024-12-11",
}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load_all()
    if payload["references"].get(KEY) not in (None, ENTRY):
        raise SystemExit(f"{KEY} is already in the header with other text")
    payload["references"][KEY] = ENTRY
    problems = VC.citation_problems(payload) + VC.header_problems(payload)
    if problems:
        raise SystemExit(f"the header fails its checks: {problems}")
    if args.dry_run or not DP._changes(payload):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write_all(payload)
    print(f"added {KEY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
