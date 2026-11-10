#!/usr/bin/env python3
"""One-off migration: the round-6 counts and tropidist runs of s6-house go into the rows.

    python master_catalog/migrations/round6_evidence_2026_11_09.py [--dry-run]

`round6_certificates/coefficients.json` holds, for 37 rows whose ``A_d`` was
null, two or more count records from programs that share no code, which
agree (see round6_certificates/README.md).  For each such row this script
writes the count as ``A_d`` with one ``A_d_evidence`` entry per tool, as
import_counts_2026_11_07.py does for round 1.  A row that already has an
``A_d`` must agree, or nothing is written.

`round6_certificates/certificates.json` holds tropidist runs on 406.3.8.a,
448.7.8.a and 490.11.8.a (threshold 7 exhausted, 8 found).  Their ``d`` = 8
already rests on a certificate (mitml sweeps of weights 1 to 7 in
round1_certificates/); the tropidist record is added to
``d_certified_evidence`` and named in ``d_certified_source``.

Three source texts said a count was not stored, or rested on one program;
they now say where the stored count comes from (the CHANGES list below).

Every changed row passes `verify_catalog.verify_row` and the file-level checks
pass before anything is written.  Idempotent.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import catalogfile as CF                                          # noqa: E402
import constructions as CO                                        # noqa: E402
import distance_policy_2026_11_07 as DP                           # noqa: E402
import verify_catalog as VC                                       # noqa: E402

COUNTS = "round6_certificates/coefficients.json"
DISTANCES = "round6_certificates/certificates.json"
TROPIDIST_SENTENCE = ("; independently, tropidist (B. Cheng, N. Guo and F. Pan, arXiv:2611.08247), "
                      "run on 9 November 2026 by the round-6 search s6-house on the UMD cluster "
                      "Zaratan over every anchor: threshold 7 exhausted, 8 found, the fault "
                      "re-checked (round6_certificates/certificates.json)")
#: (label, source label, old text, new text) in a source's provenance
OLD_NOTE = ("which is not stored because the list ({size} gzipped) is too large for this "
            "repository; the list and the run's record are kept in the research worktree, "
            "research/search2/catalogue/stage3/data/lists/")
NEW_NOTE = ("stored since 9 November 2026 from these two count records "
            "(round6_certificates/), without the list ({size} gzipped): the record gives the "
            "list's SHA-256 and the command that regenerates it byte for byte")
ONE_PROGRAM = "(one program; research/search2/s4-d8/REPORT.md, section 1.2)"
TWO_PROGRAMS = ("(research/search2/s4-d8/REPORT.md, section 1.2); counted again on 9 November "
                "2026 by mitml on the UMD cluster Zaratan and by the counting trellis, which "
                "agree, and stored (round6_certificates/)")
CHANGES = [
    ("348.22.7.a", "s4-csum 80ade620a8", OLD_NOTE.format(size="11 MB"), NEW_NOTE.format(size="11 MB")),
    ("452.66.6.a", "s4-csum 635dd6a7cd", OLD_NOTE.format(size="42 MB"), NEW_NOTE.format(size="42 MB")),
    ("470.28.7.a", "s4-csum 9c8f7d3120", OLD_NOTE.format(size="11 MB"), NEW_NOTE.format(size="11 MB")),
    ("318.2.9.a", "s4-d8 7a24ec10dc", ONE_PROGRAM, TWO_PROGRAMS),
    ("451.3.9.a", "s4-d8 32433628f8", ONE_PROGRAM, TWO_PROGRAMS),
]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load_all()
    counts, problem = VC.coefficient_records(COUNTS)
    if problem:
        raise SystemExit(problem)
    distances, problem = VC.evidence_records(DISTANCES)
    if problem:
        raise SystemExit(problem)
    changed = {}
    for row in payload["factories"]:
        digest = CO.digest(row["columns"])
        mine = [c for c in counts if c["columns_sha256"] == digest]
        if mine:
            if not row["d_is_exact"] or {c["weight"] for c in mine} != {row["d"]}:
                raise SystemExit(f"{row['catalog_label']}: a count at another weight")
            if any((c["n"], c["k"], c["N"]) != (row["n"], row["k"], row["N"]) for c in mine):
                raise SystemExit(f"{row['catalog_label']}: a record binds other n, k, N")
            values = {c["count"] for c in mine}
            if len(values) != 1 or len({c["tool"] for c in mine}) < 2 \
                    or (row["A_d"] is not None and row["A_d"] not in values):
                raise SystemExit(f"{row['catalog_label']}: the counts disagree or one program")
            listed = list(row.get("A_d_evidence") or [])
            for c in mine:
                entry = {"file": COUNTS, "tool": c["tool"]}
                if entry not in listed:
                    listed.append(entry)
            if row["A_d"] != values.copy().pop() or listed != row.get("A_d_evidence"):
                row["A_d"] = values.pop()
                row["A_d_evidence"] = listed
                changed[row["catalog_label"]] = row
        cert = [r for r in distances if r["columns_sha256"] == digest]
        if cert:
            if "d_sweep_floor" not in row or {r["lower_bound"] for r in cert} != {row["d_certified"]}:
                raise SystemExit(f"{row['catalog_label']}: the tropidist bound is not the row's "
                                 f"certified d")
            entry = {"file": DISTANCES, "method": "exhaustive search", "tool": cert[0]["tool"]}
            if entry not in row["d_certified_evidence"]:
                row["d_certified_evidence"] = row["d_certified_evidence"] + [entry]
                changed[row["catalog_label"]] = row
            if TROPIDIST_SENTENCE not in row["d_certified_source"]:
                row["d_certified_source"] += TROPIDIST_SENTENCE
                changed[row["catalog_label"]] = row
    by = {row["catalog_label"]: row for row in payload["factories"]}
    for label, source, old, new in CHANGES:
        (entry,) = [s for s in by[label]["sources"] if s["label"] == source]
        if new in entry["provenance"]:
            continue
        if entry["provenance"].count(old) != 1:
            raise SystemExit(f"{label}: the source text is not the one expected")
        entry["provenance"] = entry["provenance"].replace(old, new)
        changed[label] = by[label]
    for row in changed.values():
        started = time.time()
        _facts, problems = VC.verify_row(row)
        print(f"  {row['catalog_label']}: A_d = {row['A_d']}, "
              f"{len(row.get('A_d_evidence') or [])} count record(s), "
              f"{len(row.get('d_certified_evidence') or [])} distance record(s); verified in "
              f"{time.time() - started:.0f}s" + (f": {problems}" if problems else ""),
              flush=True)
        if problems:
            raise SystemExit("a changed row fails verification; nothing written")
    rows = payload["factories"]
    residue = [p for row in rows for p in VC.certificate_problems(row)]
    residue += (VC.duplicate_label_problems(rows) + VC.provenance_problems(payload)
                + VC.citation_problems(payload) + VC.header_problems(payload))
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the catalogue fails a file-level check; nothing written")
    print(f"{len(changed)} row(s) changed")
    if args.dry_run or not DP._changes(payload):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write_all(payload)
    print("wrote master_catalog.json, master_catalog_large.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
