#!/usr/bin/env python3
"""Write `certificates.json` and `coefficients.json` from the run records in
`evidence/`.

    python round2_certificates/assemble.py            # write both files
    python round2_certificates/assemble.py --check    # compare with them

The run records are copied unchanged from the research branch (see
README.md): the second-round distance search (`evidence/distances/`, research
commit 2c3ce12) and, for 935.89, 936.88 and 1715.287, the plan's kernel runs
and the catalogue's own sweep at a raised budget (`evidence/plan/`, research
commit 9932b15).  `evidence/own_sweep_1715.json` is a run of the catalogue's
own sweep made in this repository (see `own_sweep.py`).

Every record names the circuit by the SHA-256 of its columns
(`constructions.digest`).  This script binds each one to a catalogue row:
the row the research names (by its label then, which may now be a former
label), whose current columns must have that digest; a circuit not yet in the
catalogue is matched by digest alone, and its records are written all the
same, for the merge to use.  Every fault any run returned is re-checked
here with the catalogue's `faultcore.Circuit.harmful` and by the XOR of the
wire masks.  A distance record states a lower bound only where every weight
below it was swept completely and found no harmful fault; a count record
states the number of harmful faults of one weight.  Every count that two
records state for one circuit and weight must agree, or nothing is written.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO / "master_catalog"))

import catalogfile as CF                                          # noqa: E402
import constructions as K                                         # noqa: E402
import faultcore as FC                                            # noqa: E402

EV = HERE / "evidence"
DIST = EV / "distances"
PLAN = EV / "plan"
CERTIFICATES = HERE / "certificates.json"
COEFFICIENTS = HERE / "coefficients.json"

#: The tools, as the catalogue rows name them.
MITML = ("mitml, the meet-in-the-middle sweep of the second-round distance "
         "search (evidence/distances/mitml/mitml.c)")
KERNEL = ("the plan's meet-in-the-middle kernel (evidence/plan/mitm/mitm.c)")
TRELLIS = ("the counting syndrome trellis of the second-round distance search "
           "(evidence/distances/trellis/trellis_count.c)")
DP = ("tropidist pipeline, dense DP (B. Cheng, N. Guo and F. Pan, "
      "arXiv:2611.08247; commit b03ec2d4), on a column order of cut rank 30")
FLATS = ("a literal count of the harmful 3-flats (evidence/distances/flat512.py)")
SWEEP = ("this catalogue's faultcore.scan_weight with a raised budget "
         "(round2_certificates/own_sweep.py)")


def jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines()
            if line.strip()]


def catalogue_rows():
    """Every row by label and by former label."""
    by = {}
    for row in CF.load_all()["factories"]:
        for name in [row["catalog_label"]] + (row.get("former_labels") or []):
            by[name] = row
    return by


def recheck(columns, k, N, witness):
    """A fault re-checked two ways; raises unless both call it harmful."""
    if len(set(witness)) != len(witness):
        raise AssertionError(f"fault {witness} repeats a column")
    acc = 0
    for j in witness:
        for q in columns[j]:
            acc ^= 1 << q
    literal = acc != 0 and (acc >> k) == 0
    core = FC.Circuit(columns, k, N).harmful(list(witness))
    if not (literal and core):
        raise AssertionError(f"fault {witness}: faultcore {core}, XOR {literal}")
    return {"faultcore_harmful": True, "literal_harmful": True}


class Book:
    """The records, and the circuits they are bound to."""

    def __init__(self):
        self.rows = catalogue_rows()
        self.distance, self.counts, self.witnesses = [], [], []
        self.circuits = {}                        # digest -> (label, n, k, N)

    def bind(self, label, digest):
        """The circuit a record speaks of: the catalogue row ``label`` names,
        whose columns must have ``digest``, or (for a circuit outside the
        catalogue) ``None`` and the digest."""
        if label is not None:
            row = self.rows.get(label)
            if row is None:
                raise AssertionError(f"{label}: no catalogue row has that label")
            got = K.digest(row["columns"])
            if got != digest:
                raise AssertionError(f"{label}: the run's columns have SHA-256 "
                                     f"{digest[:16]}..., the row's {got[:16]}...")
            self.circuits[digest] = (row["catalog_label"], row["n"], row["k"], row["N"])
            return row
        return None

    def add_distance(self, digest, tool, bound, how, label=None):
        lab, n, k, N = self.circuits[digest]
        self.distance.append({"label": lab, "research_label": label, "n": n,
                              "k": k, "N": N, "columns_sha256": digest,
                              "tool": tool, "lower_bound": bound, "how": how})

    def add_count(self, digest, tool, weight, count, accepted, how, label=None):
        lab, n, k, N = self.circuits[digest]
        self.counts.append({"label": lab, "research_label": label, "n": n, "k": k,
                            "N": N, "columns_sha256": digest, "tool": tool,
                            "weight": weight, "count": count,
                            "accepted": accepted, "how": how})

    def add_witness(self, row, witness, found_by, label=None):
        checks = recheck(row["columns"], row["k"], row["N"], witness)
        self.witnesses.append({"label": row["catalog_label"], "research_label": label,
                               "columns_sha256": K.digest(row["columns"]),
                               "witness": list(witness), "weight": len(witness),
                               "found_by": found_by, "checks": checks})


def swept_clean(runs, upto):
    """Whether every weight 1..upto was swept completely with no harmful
    fault, in ``runs`` (records of one circuit and one tool)."""
    for w in range(1, upto + 1):
        mine = [r for r in runs if r["w"] == w]
        if not mine or not all(r["status"] == "clean" and r.get("harmful", 0) == 0
                               for r in mine):
            return False
    return True


def plan_kernel_clean(label, upto):
    """The plan kernel's runs on ``label``: every weight 1..upto clean and
    complete (each part of each run)."""
    runs = [r for r in jsonl(PLAN / "data" / "mitm_runs.jsonl") if r["label"] == label]
    for w in range(1, upto + 1):
        mine = [r for r in runs if r["w"] == w]
        if not mine or not all(r["status"] == "clean" and all(
                p["complete"] == 1 and p["status"] == "clean" for p in r["parts"])
                for r in mine):
            return False
    return True


def plan_row_digest(label):
    row = json.loads((PLAN / "data" / "rows" / f"{label}.json").read_text())
    return K.digest(row["columns"])


def assemble():
    book = Book()
    results = jsonl(DIST / "results.jsonl")
    mruns = jsonl(DIST / "data" / "mitml_runs.jsonl")
    counts = jsonl(DIST / "data" / "counts.jsonl") + jsonl(DIST / "data" / "validation.jsonl")
    trellis = jsonl(DIST / "data" / "trellis_counts.jsonl")
    plan_counts = {r["label"]: r for r in
                   json.loads((PLAN / "data" / "A_d_counts.json").read_text())["rows"]}

    for res in results:
        label, digest = res["label"], res["sha256"]
        row = book.bind(label, digest)
        if row is None:
            continue                  # outside the catalogue: the merge's records
        if res["kind"] == "distance":
            d = res["result"]["d"]
            if res.get("witness"):
                if len(res["witness"]) != d:
                    raise AssertionError(f"{label}: a fault of weight "
                                         f"{len(res['witness'])} for d = {d}")
                book.add_witness(row, res["witness"], "; ".join(res["evidence"]), label)
            continue
        # an exact count of the harmful faults of one weight
        w, count, accepted = (res["result"][x] for x in ("w", "A_w", "accepted"))
        mine = [c for c in counts if c["sha256"] == digest and c["w"] == w
                and c["count"] and c["status"] == "found"]
        for c in mine:
            if (c["harmful"], c["accepted"]) != (count, accepted):
                raise AssertionError(f"{label}: mitml counted {c['harmful']} "
                                     f"for weight {w}, the result says {count}")
        if mine:
            book.add_count(digest, MITML, w, count, accepted,
                           f"count mode, {mine[0]['slices']} slice(s) summed "
                           f"before the division, {len(mine)} run(s) "
                           f"(evidence/distances/data/counts.jsonl, validation.jsonl)",
                           label)
        ours = [t for t in trellis if t["sha256"] == digest and t["W"] == w]
        for t in ours:
            if t["A"][w] != count:
                raise AssertionError(f"{label}: the trellis counts {t['A'][w]}")
        if ours:
            orders = sorted({t["order"] for t in ours})
            book.add_count(digest, TRELLIS, w, count, ours[0]["B_kerH"][w],
                           f"B_w(ker H) - B_w(ker [H;L]) in {len(orders)} column "
                           f"order(s): {', '.join(orders)} "
                           f"(evidence/distances/data/trellis_counts.jsonl)", label)
        plan = plan_counts.get(label)
        if plan is not None and plan["d"] == w:
            if (plan["A_d"], plan["accepted"]) != (count, accepted):
                raise AssertionError(f"{label}: the plan's kernel counted "
                                     f"{plan['A_d']}")
            book.add_count(digest, KERNEL, w, count, accepted,
                           "count mode (evidence/plan/data/A_d_counts.json); the "
                           "plan cached the row by label from the catalogue at "
                           "dadb221, and mitml's run on these columns gives the "
                           "same count", label)
        if label == "512.39.6.a":
            flats = json.loads((DIST / "data" / "flat512.json").read_text())
            if (flats["sha256"], flats["harmful_flats"], flats["accepted_flats"]) \
                    != (digest, count, accepted) or w != 8:
                raise AssertionError("512.39.6.a: the flat count disagrees")
            book.add_count(digest, FLATS, w, count, accepted,
                           f"every one of the {flats['subspaces']} 3-dimensional "
                           f"subspaces and its 64 cosets "
                           f"(evidence/distances/data/flat512.json)", label)
        if not mine and not ours and label != "512.39.6.a":
            raise AssertionError(f"{label}: no raw record behind the count")

    # ---- lower bounds -----------------------------------------------------
    by_label = {r["label"]: r for r in results if r["kind"] == "distance"}
    # mitml swept clean below d: 988 to weight 6, 177, 185, 189 to weight 8
    for label, upto in (("988.36.6.a", 6), ("177.1.7.a", 8), ("185.1.7.a", 8),
                        ("189.1.7.a", 8)):
        digest = by_label[label]["sha256"]
        runs = [r for r in mruns + counts if r["sha256"] == digest and r["count"]]
        if not swept_clean(runs, upto):
            raise AssertionError(f"{label}: mitml did not sweep 1..{upto} clean")
        book.add_distance(digest, MITML, upto + 1,
                          f"count mode, weights 1 to {upto}: no harmful fault "
                          f"(evidence/distances/data/mitml_runs.jsonl, counts.jsonl)",
                          label)
    # the trellis: A_w = 0 below W in every order it ran
    for label in ("177.1.7.a", "185.1.7.a", "189.1.7.a", "271.1.7.a",
                  "279.1.7.a", "283.1.7.a", "401.1.6.a"):
        digest = book.rows[label] and K.digest(book.rows[label]["columns"])
        ours = [t for t in trellis if t["sha256"] == digest]
        if not ours:
            raise AssertionError(f"{label}: no trellis count")
        W = ours[0]["W"]
        if any(t["W"] != W or any(t["A"][:W]) for t in ours):
            raise AssertionError(f"{label}: the trellis finds a lighter fault")
        book.bind(label, digest)
        book.add_distance(digest, TRELLIS, W,
                          f"A_w = 0 for w < {W} in {len(ours)} column order(s) "
                          f"(evidence/distances/data/trellis_counts.jsonl)", label)
    # tropidist's dense DP on 599, run on a permutation of its columns
    dp = [r for r in jsonl(DIST / "data" / "dp_perm.jsonl")
          if r["label"] == "599.1.6.a.ord" and r.get("lower_bound") == 15]
    record = json.loads((DIST / "data" / "dp_records" / "599.1.6.a.ord.json").read_text())
    order = json.loads((DIST / "data" / "orders" / "599.1.6.a.json").read_text())
    notes = json.loads(record["notes"])
    if not dp or record["lower_bound"] != 15 or notes["dp"]["main"]["value"] != 15 \
            or notes["dp"]["main"]["cut_rank"] != 30 or sorted(order) != list(range(599)):
        raise AssertionError("599.1.6.a: the DP record does not say d >= 15")
    digest = by_label["599.1.6.a"]["sha256"]
    book.add_distance(digest, DP, 15,
                      "config dp=2,table_gb=3,dp_fast=300, one thread, laptop; the "
                      "DP returned 15 after 33.7 s on the columns permuted by "
                      "evidence/distances/data/orders/599.1.6.a.json (the distance "
                      "does not depend on the column order) "
                      "(evidence/distances/data/dp_records/599.1.6.a.ord.json)",
                      "599.1.6.a")
    # the plan's kernel: 935 and 936 clean to weight 6, 1715 to weight 5
    for label, upto in (("935.89.6.a", 6), ("936.88.6.a", 6), ("1715.287.3.a", 5)):
        digest = plan_row_digest(label)
        book.bind(label, digest)
        if not plan_kernel_clean(label, upto):
            raise AssertionError(f"{label}: the kernel did not sweep 1..{upto} clean")
        book.add_distance(digest, KERNEL, upto + 1,
                          f"status mode, weights 1 to {upto} complete and clean "
                          f"(evidence/plan/data/mitm_runs.jsonl); the row it read "
                          f"is evidence/plan/data/rows/{label}.json", label)
    # the catalogue's own sweep on 1715 at a raised budget, run here and by
    # the research (the same code)
    for path in (EV / "own_sweep_1715.json", PLAN / "data" / "own_sweeps.jsonl"):
        runs = jsonl(path)
        mine = [r for r in runs if r["label"] == "1715.287.3.a"]
        if not mine or not all(all(mine[0]["weights"][str(w)]["status"] == "clean"
                                   for w in range(1, 6)) for _ in mine):
            raise AssertionError(f"{path.name}: 1715 is not swept clean to weight 5")
    digest = plan_row_digest("1715.287.3.a")
    own = jsonl(EV / "own_sweep_1715.json")[0]
    if own["columns_sha256"] != digest:
        raise AssertionError("own_sweep_1715.json ran on other columns")
    book.add_distance(digest, SWEEP, 6,
                      f"weights 1 to 5 clean, run in this repository at commit "
                      f"{own['commit']} ({own['wall_seconds']} s; "
                      f"round2_certificates/evidence/own_sweep_1715.json), as the "
                      f"research's run of the same code at dadb221 found "
                      f"(evidence/plan/data/own_sweeps.jsonl)", "1715.287.3.a")
    # the weight-6 fault of 1715, found by mitml's count
    row = book.rows["1715.287.3.a"]
    c1715 = [c for c in counts if c["id"] == "1715.287.3.a" and c["w"] == 6]
    book.add_witness(row, c1715[0]["witness"], "mitml count of weight 6 "
                     "(evidence/distances/data/counts.jsonl)", "1715.287.3.a")
    return book


def payloads(book):
    key = lambda r: (r["n"], r["k"], r["label"], r["tool"])         # noqa: E731
    head = ("Records of the second-round distance search of 7 November 2026 "
            "(research branch, research/search2/distances at 2c3ce12) and of "
            "the plan's kernel (research/plan at 9932b15), copied to evidence/, "
            "with one run of this catalogue's own sweep made here. Each record "
            "is bound to its circuit by columns_sha256 (constructions.digest of "
            "the columns); label is the catalogue row at assembly, "
            "research_label the label the research used. Written by "
            "round2_certificates/assemble.py.")
    certificates = {
        "about": head + " A distance record states lower_bound: every weight "
                 "below it was swept completely by the tool and no harmful "
                 "fault found. witnesses lists every fault the runs returned, "
                 "re-checked with faultcore and by the XOR of the wire masks.",
        "method": "exhaustive search",
        "records": sorted(book.distance, key=key),
        "witnesses": sorted(book.witnesses, key=lambda r: (r["label"], r["weight"])),
    }
    coefficients = {
        "about": head + " A count record states count, the number of harmful "
                 "accepted faults of the given weight, and accepted, the number "
                 "of accepted ones; where two tools count one circuit, they agree.",
        "records": sorted(book.counts, key=key),
    }
    return certificates, coefficients


def render(blob):
    import re
    text = json.dumps(blob, indent=1)
    return re.sub(r"\[\s*\n\s*((?:-?\d+,\s+)*-?\d+)\s+\]",
                  lambda m: "[" + re.sub(r"\s+", " ", m.group(1)) + "]", text) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    book = assemble()
    seen = defaultdict(set)
    for r in book.counts:
        seen[(r["columns_sha256"], r["weight"])].add(r["count"])
    if any(len(v) != 1 for v in seen.values()):
        raise SystemExit("two tools disagree on a count; nothing written")
    texts = dict(zip((CERTIFICATES, COEFFICIENTS), map(render, payloads(book))))
    if args.check:
        stale = [p.name for p, t in texts.items()
                 if not p.exists() or p.read_text(encoding="utf-8") != t]
        if stale:
            raise SystemExit(f"out of date: {', '.join(stale)}")
        print("certificates.json and coefficients.json are up to date")
        return 0
    for path, text in texts.items():
        path.write_text(text, encoding="utf-8")
    print(f"wrote {len(book.distance)} distance records, {len(book.witnesses)} "
          f"faults and {len(book.counts)} count records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
