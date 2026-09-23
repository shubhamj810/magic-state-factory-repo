#!/usr/bin/env python3
"""COMMAND LINE for the parent-first workflow.  Start here.

    python cli.py --help

Three subcommands, in the order the decision pipeline uses them
(see ``../theory/03_parent_first.md``):

  analyze   Build the parent once and report the filter chain kappa -> mu -> tau.
            `--cheap-only` stops after the linear-algebra stage, which is
            sub-second even on large quotients, and is how you triage a parent
            before spending anything.
  target    Ask one parent for one specific gate.
  gates     Ask one parent for *every* gate it can carry up to `--kmax`
            (target-agnostic), deduplicated by `--dedup gl` or `--dedup symmetric`.

Parents come from either `--factory n,k,d` (resolved against the generated
search catalogue in `../symmetry_sat_search/catalog/factories.json`) or `--input parent.json`
(see `examples/README.md` for the two accepted shapes).

Budgets: every expensive stage takes a node budget, and `0` means unlimited.
A run that hits its budget reports `"complete": false`.  **A non-complete run is
search data, never a nonexistence certificate** -- that distinction is enforced
throughout `factorylib.parent` and is the reason the flag exists.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))          # run from anywhere: siblings by bare name
sys.path.insert(0, str(HERE.parent))   # shared factorylib package

from factorylib.parent import (                              # noqa: E402
    MAX_QUOTIENT_DIM,
    Parent,
    certification_metrics,
    classify_gates,
    find_target,
    form_rank_bounds,
    parse_gate,
)
from factorylib.metrics import metrics_from_named            # noqa: E402


def gate_metrics(named, k):
    """Exact minimal T count and Clifford-reduced degree of a named gate.

    A parent-first run tells you WHICH gates a check geometry can carry; these
    two numbers say how much each one is worth.  The T count is the exact
    minimum over the Reed--Muller coset (Amy--Mosca), not the number of terms in
    the phase polynomial as written -- so `T0 . T1 . CS01` is correctly reported
    as costing less than its three terms suggest.  The degree is minimised over
    output CNOT frames, so Clifford-absorbable top-degree terms do not inflate
    it.

    Returns (t_count, poly_degree); either may be None for a gate outside what
    the level-3 decoder handles (large k overflows it).
    """
    try:
        t_count, _t_note, degree, _d_note = metrics_from_named(named)
        return t_count, degree
    except (OverflowError, ValueError, KeyError, AssertionError):
        return None, None


def annotate_metrics(payload):
    """Add t_count / poly_degree to every gate record in a payload, in place."""
    for record in payload.get("gates", []):
        if "gate" in record and "k" in record:
            t, d = gate_metrics(record["gate"], record["k"])
            record["t_count"] = t
            record["poly_degree"] = d
    if "gate" in payload and payload.get("found") and "k" in payload:
        t, d = gate_metrics(payload["gate"], payload["k"])
        payload["t_count"] = t
        payload["poly_degree"] = d
    return payload

#: Generated search catalogue, used only to resolve `--factory n,k,d`.
CATALOG = HERE.parent / "symmetry_sat_search" / "catalog" / "factories.json"


def _budget(value: int) -> int | None:
    return None if value == 0 else value


def _write_or_print(payload: dict, output: str | None) -> None:
    text = json.dumps(payload, indent=2) + "\n"
    if output:
        # Write-then-rename, so an interrupted run leaves the previous file
        # intact instead of a truncated one.  The README promised this; the
        # code used to write the destination directly.
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, path)
        print(f"wrote {path}")
    else:
        print(text, end="")


def _factory(spec: str) -> dict:
    try:
        key = tuple(int(value) for value in spec.split(","))
    except ValueError as error:
        raise ValueError("--factory must be n,k,d (for example 51,5,3)") from error
    if len(key) != 3:
        raise ValueError("--factory must contain exactly n,k,d")
    entries = json.loads(CATALOG.read_text())["factories"]
    matches = [entry for entry in entries if (entry["n"], entry["k"], entry["d"]) == key]
    if not matches:
        raise ValueError(f"factory {key} is not in {CATALOG.name}")
    if len(matches) > 1:
        # Silently taking min(N, label) meant `--factory 15,2,3` analysed the CZ
        # circuit while the caller may well have meant the S one -- five
        # selectors are ambiguous, some across Clifford levels.  Name the row
        # instead of guessing which parent the user wanted.
        options = "\n".join(
            f"    --label {entry['label']!r}   (level {entry['level']}, "
            f"N={entry['N']}, gate {entry['output_gate']})" for entry in matches)
        raise ValueError(
            f"--factory {spec} matches {len(matches)} catalogue rows; add "
            f"--label to choose one:\n{options}")
    return matches[0]


def _factory_by_label(label: str) -> dict:
    """The catalogue row with this exact label (labels are unique)."""
    entries = json.loads(CATALOG.read_text())["factories"]
    matches = [entry for entry in entries if entry.get("label") == label]
    if not matches:
        raise ValueError(f"no catalogue row is labelled {label!r}")
    if len(matches) > 1:                       # build_catalog.py forbids this
        raise ValueError(f"label {label!r} is not unique in {CATALOG.name}")
    return matches[0]


def _load_parent(args) -> tuple[Parent, dict]:
    if args.factory:
        entry = _factory_by_label(args.label) if args.label else _factory(args.factory)
        if args.label:
            got = (entry["n"], entry["k"], entry["d"])
            want = tuple(int(v) for v in args.factory.split(","))
            if got != want:
                raise ValueError(
                    f"--label {args.label!r} is the [[{got[0]},{got[1]},{got[2]}]] "
                    f"row, which does not match --factory {args.factory}")
        parent = Parent.from_columns(
            entry["columns"], entry["k"], entry["N"], distance=args.distance,
            max_kappa=args.max_kappa,
        )
        return parent, {"source": "symmetry_sat_search/catalog/factories.json", "factory": args.factory,
                        "label": entry.get("label")}
    if not args.input:
        raise ValueError("one of --factory or --input is required")
    path = Path(args.input)
    blob = json.loads(path.read_text())
    if "points" in blob:
        parent = Parent.from_points(
            blob["points"], blob.get("ambient_rank"), distance=args.distance,
            max_kappa=args.max_kappa,
        )
    elif "columns" in blob:
        outputs = blob.get("k", blob.get("outputs"))
        if outputs is None:
            raise ValueError("a columns input needs 'k' or 'outputs'")
        parent = Parent.from_columns(
            blob["columns"], outputs, blob.get("N", blob.get("total_rows")),
            args.distance, max_kappa=args.max_kappa,
        )
    else:
        raise ValueError("input JSON needs either 'points' or 'columns'")
    return parent, {"source": str(path)}


def _parent_args(parser: argparse.ArgumentParser) -> None:
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--factory", help="catalog selector n,k,d, e.g. 51,5,3")
    source.add_argument("--input", help="JSON with points or columns")
    parser.add_argument("--label", help=(
        "pick one row by its catalogue label; required when --factory n,k,d "
        "matches more than one row"))
    parser.add_argument("--distance", type=int, default=3, help="distance filter (default 3)")
    parser.add_argument("--max-kappa", type=int, default=MAX_QUOTIENT_DIM,
                        help=(f"refuse a parent whose quotient dimension exceeds this "
                              f"(default {MAX_QUOTIENT_DIM}); building one costs 2^kappa "
                              f"memory, so raise it deliberately"))
    parser.add_argument("--output", help="write JSON here instead of stdout")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Parent-first factory search: build the check parent once, filter it "
            "cheaply, then solve the output problem. See README.md."
        )
    )
    commands = parser.add_subparsers(dest="command", required=True)

    analyze = commands.add_parser("analyze", help="compute kappa, mu, and product-T tau")
    _parent_args(analyze)
    analyze.add_argument("--max-width", type=int)
    analyze.add_argument("--node-budget", type=int, default=1_000_000,
                         help="per exact search; 0 means unlimited")
    analyze.add_argument("--cheap-only", action="store_true",
                         help="report kappa and compatibility-form rank bounds only")

    target = commands.add_parser("target", help="search one parent for an exact gate")
    _parent_args(target)
    target.add_argument("--gate", required=True, help="e.g. T0.T1.T2 or CCZ012")
    target.add_argument("--width", type=int)
    target.add_argument("--node-budget", type=int, default=1_000_000,
                        help="0 means unlimited")

    gates = commands.add_parser("gates", help="enumerate compatible gates on one parent")
    _parent_args(gates)
    gates.add_argument("--kmax", type=int, default=3)
    gates.add_argument("--dedup", choices=("gl", "symmetric"), default="gl")
    gates.add_argument("--node-budget", type=int, default=1_000_000,
                       help="0 means unlimited")
    gates.add_argument("--orbit-budget", type=int, default=1_000_000,
                       help="per GL orbit; 0 means unlimited")
    gates.add_argument("--include-spectators", action="store_true",
                       help="keep gates that leave an output qubit idle")
    gates.add_argument("--no-metrics", action="store_true",
                       help="skip the exact T-count / reduced-degree annotation")

    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        parent, source = _load_parent(args)
        if args.command == "analyze":
            if args.cheap_only:
                payload = {
                    **source,
                    "n": parent.n,
                    "ambient_check_rows": parent.ambient_rank,
                    "check_rank": parent.check_rank,
                    "distance_filter": parent.distance,
                    "quadric_degeneracy": parent.quadric_degeneracy,
                    "kappa": parent.kappa,
                    "form_rank_bounds": form_rank_bounds(parent),
                }
            else:
                payload = {
                    **source,
                    **certification_metrics(
                        parent,
                        max_width=args.max_width,
                        node_budget=_budget(args.node_budget),
                    ),
                }
        elif args.command == "target":
            wants = parse_gate(args.gate)
            payload = {
                **source,
                "requested_gate": args.gate,
                **find_target(parent, wants, args.width, _budget(args.node_budget)),
            }
        else:
            payload = {
                **source,
                **classify_gates(
                    parent,
                    args.kmax,
                    args.dedup,
                    _budget(args.node_budget),
                    _budget(args.orbit_budget),
                    active_only=not args.include_spectators,
                ),
            }
            if not args.no_metrics:
                annotate_metrics(payload)
        _write_or_print(payload, args.output)
        return 0
    except (KeyError, OSError, ValueError) as error:
        raise SystemExit(f"error: {error}") from error


if __name__ == "__main__":
    raise SystemExit(main())
