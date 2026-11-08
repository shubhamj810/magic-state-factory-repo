#!/usr/bin/env python3
"""One-off migration: store the [[217,7,7]] circuit with the smaller A_7.

    python master_catalog/migrations/store_217_7_7_2026_11_07.py [--dry-run]

Two circuits of the class (217, 7, 7, T0..T6) came from the searches of
7 November 2026: small-d7's 9c3da8b2..., stored as 217.7.7.a, and small-cyc's
69bae4f9... (research/search2/small-cyc/data/claims/, commit 27ac40e).  Both
have N = 38.  `errorcoeff` does not reach A_7 at n = 217, so the merge could
compare only the wires and filed the second circuit as a duplicate.
`round1_certificates/count_weight.py` counted weight 7 of both, with mitml's
complete list (every set re-checked) and with small-review's mydist.py:
1,034 for the stored circuit and 973 for small-cyc's, each by both programs
(`round1_certificates/coefficients.json`).  The owner asked for the better
circuit to be stored (7 November 2026).

This script builds small-cyc's row with `merge_results.candidate_row`,
checks that it is 217.7.7.a's class, makes its distance exact with the first
fault of mitml's list (re-checked here by faultcore and by the XOR of the
wire masks), gives it A_7 = 973 with both evidence records, and replaces the
stored circuit through `merge_results.improve`, which keeps the label and
appends the source.  The row passes `verify_catalog.verify_row` and the
file-level checks pass before anything is written.  Idempotent.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "round1_certificates"))

import catalogfile as CF                                          # noqa: E402
import constructions as CO                                        # noqa: E402
import distance_policy_2026_11_07 as DP                           # noqa: E402
import faultcore as FC                                            # noqa: E402
import merge_results as MR                                        # noqa: E402
import verify_catalog as VC                                       # noqa: E402
import assemble as R1                                             # noqa: E402

LABEL = "217.7.7.a"
OLD = "9c3da8b2e0653b80185ffb7c695e16043627cbe57a70531ad09e023b65878d92"
NEW = "69bae4f96f9edd256853a9fbc3a45944ed112bbf3d5fd6e7228fe9fb586fdb62"
CLAIM = Path("research/search2/small-cyc/data/claims") / f"{NEW}.json"
#: the columns of the claim, copied with it into this repository's evidence
#: folder, so the migration can be re-run without the research branch
COPY = REPO / "round1_certificates" / "evidence" / "small_cyc_217_7_7.json"
LIST = REPO / "round1_certificates" / "evidence" / "lists" / "small-cyc.69bae4f9_w7.txt"
COUNTS = "round1_certificates/coefficients.json"
A7 = 973


def record():
    claim = json.loads(COPY.read_text())
    if CO.digest(claim["columns"]) != NEW:
        raise SystemExit("the copied claim is not small-cyc's 69bae4f9 circuit")
    return {"k": claim["k"], "N": claim["N"], "columns": claim["columns"],
            "n": claim["n"], "d": 7,
            "regime": "AI search: punctured triply even cyclic codes",
            "discovery": "AI search", "citations": ["jain2026symmetry"],
            "file": f"{CLAIM} (research branch, commit 27ac40e)",
            "label": "small-cyc 69bae4f96f",
            "origin": ("research/search2/small-cyc/REPORT.md, checked again in "
                       "research/search2/lead/CHECKS.md (commit 1a6c0a6); A_7 counted "
                       "here by round1_certificates/count_weight.py"),
            "provenance": claim["source"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load_all()
    rows = payload["factories"]
    (index,) = [i for i, r in enumerate(rows) if r["catalog_label"] == LABEL]
    incumbent = rows[index]
    if CO.digest(incumbent["columns"]) == NEW and incumbent["A_d"] == A7:
        print(f"{LABEL} already stores {NEW[:16]}...; nothing to do")
        return 0
    if CO.digest(incumbent["columns"]) != OLD:
        raise SystemExit(f"{LABEL} does not store the circuit {OLD[:16]}...")
    candidate, problems = MR.candidate_row(record(), payload, "small-cyc", 0)
    if candidate is None:
        raise SystemExit(f"the candidate does not verify: {problems}")
    if CO.digest(candidate["columns"]) != NEW:
        raise SystemExit("the stored columns of the candidate are not the claim's")
    if MR.find_class(rows, candidate) != index:
        raise SystemExit(f"the candidate is not {LABEL}'s class")
    if (candidate["N"], candidate["d"]) != (incumbent["N"], incumbent["d"]):
        raise SystemExit("the candidate's N or d differs from the stored row's")
    # the exact distance: the first set of mitml's list, re-checked both ways
    fault = sorted(int(x) for x in LIST.read_text().splitlines()[0].split(":")[0].split())
    acc = 0
    for j in fault:
        for q in candidate["columns"][j]:
            acc ^= 1 << q
    literal = acc != 0 and (acc >> candidate["k"]) == 0
    if len(fault) != 7 or not literal or not FC.Circuit(
            candidate["columns"], candidate["k"], candidate["N"]).harmful(fault):
        raise SystemExit("the fault from mitml's list does not hold")
    candidate["d_is_exact"] = True
    candidate["d_upper"], candidate["d_witness"] = 7, fault
    candidate["sources"][0]["d_is_exact"] = True
    candidate["A_d"] = A7
    candidate["A_d_evidence"] = [{"file": COUNTS, "tool": R1.MITML_LIST},
                                 {"file": COUNTS, "tool": R1.MYDIST}]
    _facts, problems = VC.verify_row(candidate)
    if problems:
        raise SystemExit(f"the candidate row fails verification: {problems}")
    MR.improve(incumbent, {**candidate, "citations": ["jain2026symmetry"]},
               payload["regimes"])
    _facts, problems = VC.verify_row(incumbent)
    print(f"  {LABEL}: now {NEW[:16]}..., N = {incumbent['N']}, A_7 = {incumbent['A_d']}, "
          f"witness {incumbent['d_witness']}" + (f": {problems}" if problems else ""))
    if problems:
        raise SystemExit("the changed row fails verification; nothing written")
    residue = [p for row in rows for p in VC.certificate_problems(row)]
    residue += (VC.duplicate_label_problems(rows) + VC.provenance_problems(payload)
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
