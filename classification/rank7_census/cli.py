#!/usr/bin/env python3
"""COMMAND LINE for the r <= 7 census.  Start here.

    python cli.py --help

Subcommands
-----------
``data-check``
    Verify the bundled Gillot--Langevin orbit table before trusting anything
    built on it: 3,486 classes, maximum degree 3, and -- the real test -- that
    the orbit sizes sum to exactly 2^64 = |RM(3,7)|.  Run this first; it takes
    a few seconds and it is the difference between "we parsed a file" and "we
    parsed the right file, completely".

``census``
    Run the classification itself over the selected marked geometries.  With no
    restriction and both budgets set to 0 this is the full r <= 7, n <= 44
    sweep, which is cluster scale.  Use ``--class-index`` / ``--origin`` /
    ``--max-parents`` and finite budgets for anything interactive.

    **Only an output whose top-level ``complete`` is true is a classification
    certificate.**  A budget hit gives ``complete: false``, which is useful
    search data and nothing more.  Checkpoints are written atomically, so an
    interrupted run never leaves a malformed JSON behind.

For analysing ONE parent -- kappa/mu/tau, a targeted solve, or the compatible
gate list -- use the sibling directory ``../../parent_first``, whose ``cli.py``
drives the same shared ``factorylib.parent`` implementation with a friendlier
interface.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))          # run from anywhere: siblings by bare name

from gillot_langevin import integrity_report        # noqa: E402
from rank7 import DEFAULT_DATA, run as run_census   # noqa: E402


def _budget(value: int):
    """0 on the command line means 'unlimited'."""
    return None if value == 0 else value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Complete r <= 7, n <= 44 check-parent census. See README.md.")
    commands = parser.add_subparsers(dest="command", required=True)

    integrity = commands.add_parser(
        "data-check", help="verify the bundled Gillot--Langevin orbit table")
    integrity.add_argument("--data", default=str(DEFAULT_DATA))

    census = commands.add_parser(
        "census", help="run the r<=7 classification over selected geometries")
    census.add_argument("--data", default=str(DEFAULT_DATA))
    census.add_argument("--output", required=True,
                        help="destination JSON (checkpointed atomically)")
    census.add_argument("--mode", choices=("reps", "all"), default="reps",
                        help="'reps': one safe origin per stabilizer orbit "
                             "(fast); 'all': all 71 x 128 marked geometries")
    census.add_argument("--nmax", type=int, default=44)
    census.add_argument("--kmax", type=int, default=4)
    census.add_argument("--dedup", choices=("gl", "symmetric"), default="gl",
                        help="'gl': GL(k,2) phase-tensor action; 'symmetric': "
                             "output permutations S_k only (the key used by "
                             "the n<=38 catalogue)")
    census.add_argument("--class-index", action="append", type=int,
                        help="restrict to these RM(3,7) orbit indices (repeatable)")
    census.add_argument("--origin", action="append", type=int,
                        help="restrict to these marked origins (repeatable)")
    census.add_argument("--max-parents", type=int,
                        help="cap the number of parents; omit for the full sweep")
    census.add_argument("--node-budget", type=int, default=1_000_000,
                        help="per parent; 0 means unlimited")
    census.add_argument("--orbit-budget", type=int, default=1_000_000,
                        help="per gate orbit; 0 means unlimited")
    census.add_argument("--checkpoint-every", type=int, default=10)
    census.add_argument("--allow-incomplete", action="store_true", help=(
        "exit 0 even when the run is incomplete.  A capped or restricted run is "
        "useful search data and the documented smoke run is deliberately one of "
        "them -- but without this flag an incomplete classification exits 1, so "
        "cluster and shell automation cannot read it as success"))
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "data-check":
            report = integrity_report(args.data)
            print(json.dumps(report, indent=2))
            if report["valid"]:
                print("\nOK: 3,486 orbit classes, degree <= 3, orbit sizes sum "
                      "to 2^64 = |RM(3,7)|.")
            return 0 if report["valid"] else 1

        payload = run_census(
            data=args.data,
            output=args.output,
            mode=args.mode,
            nmax=args.nmax,
            kmax=args.kmax,
            dedup=args.dedup,
            class_indices=args.class_index,
            origins=args.origin,
            max_parents=args.max_parents,
            node_budget=_budget(args.node_budget),
            orbit_budget=_budget(args.orbit_budget),
            checkpoint_every=args.checkpoint_every,
        )
        print(f"wrote {args.output}: {payload['processed_parents']} parents, "
              f"{len(payload['factories'])} gates, "
              f"complete={payload['complete']}")
        if payload["complete"]:
            return 0
        print("NOTE: complete=false. This run is search data, NOT a "
              "classification certificate, because:")
        for reason in payload.get("incomplete_reasons", ["(unrecorded)"]):
            print(f"        - {reason}")
        # An incomplete classification is not a successful one.  Returning 0
        # here meant a `&&`-chained cluster job, or any script reading the exit
        # code, treated a budget-capped partial sweep as a finished census.
        if args.allow_incomplete:
            print("(--allow-incomplete: exiting 0 anyway)")
            return 0
        print("Exiting 1. Pass --allow-incomplete if a partial run is what you "
              "wanted.")
        return 1
    except (KeyError, OSError, ValueError) as error:
        raise SystemExit(f"error: {error}") from error


if __name__ == "__main__":
    raise SystemExit(main())
