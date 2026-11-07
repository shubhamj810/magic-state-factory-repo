#!/usr/bin/env python3
"""Write `certificates.json` from the run records in `evidence/`.

    python zaratan_certificates/assemble.py            # write the file
    python zaratan_certificates/assemble.py --check    # compare with it

Three kinds of run record are read, all copied unchanged from the research
branch (see README.md):

* the meet-in-the-middle kernel (`evidence/laptop/mitm.c`), one record per
  weight in `evidence/laptop/mitm_runs.jsonl` and per slice in
  `mitm_slices.jsonl`: a weight counts as swept only when every slice of it
  is ``clean`` and ``complete``.  Its lower bound is one more than the last
  weight of an unbroken clean run from weight 1;
* tropidist's search at one threshold ``K``, called by
  `evidence/laptop/tdirect.py`, one record per run in
  `evidence/zaratan/zaratan_pilots.jsonl`: ``exhausted`` over all anchors
  with the natural rank proves that no harmful fault of weight ``<= K``
  exists, so ``d >= K + 1``.  Runs on a sample of anchors prove nothing and
  are not used;
* tropidist's pipeline with its dense dynamic programme, one record per row
  in `evidence/zaratan/dp_records/zaratan_*.jsonl`: ``exact`` with its
  ``lower_bound``.

Every fault any of them returned is re-checked here with the catalogue's
`faultcore.Circuit.harmful` and by the XOR of the wire masks, on the columns
the run was given, and goes into ``witnesses``.  A record is bound to its
circuit by the SHA-256 of those columns (`constructions.digest`): the cached
row the kernel and tdirect read (`evidence/rows/`), or, for the pipeline,
which read the catalogue itself, the row of the catalogue at commit
``CATALOGUE_COMMIT``.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO / "master_catalog"))

import constructions as K                                         # noqa: E402
import faultcore as FC                                            # noqa: E402

EVIDENCE = HERE / "evidence"
CERTIFICATES = HERE / "certificates.json"
#: The catalogue the Zaratan checkout of the research branch held: the research
#: branch leaves master_catalog/ as it was at this commit.
CATALOGUE_COMMIT = "d15e4ebbfa1c221c3363437c4e62749f9ef98caa"
TROPIDIST_COMMIT = "b03ec2d4077f287f89f97b5c2c16ce5ce17c2c58"
RESEARCH_COMMITS = {
    "research/plan (kernel, tdirect.py, laptop kernel runs)":
        "9932b1538afee7e8a54bd02c8717cf6a931b225c",
    "research/zaratan (cluster runs, RESULTS.md)":
        "1300c55c01af27ebbcf283746aedf883c5b0db3e",
}
KERNEL = "mitm.c kernel"
SEARCH = "tropidist search"
PIPELINE = "tropidist pipeline"


def literal_harmful(columns, k, indices):
    value = 0
    for index in indices:
        mask = 0
        for q in columns[index]:
            mask |= 1 << q
        value ^= mask
    return value != 0 and not value >> k


def cached_rows():
    return {path.name[:-len(".json")]: json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((EVIDENCE / "rows").glob("*.json"))}


def committed_rows(labels):
    text = subprocess.run(["git", "-C", str(REPO), "show",
                           f"{CATALOGUE_COMMIT}:master_catalog/master_catalog.json"],
                          capture_output=True, text=True, check=True).stdout
    return {row["catalog_label"]: row for row in json.loads(text)["factories"]
            if row["catalog_label"] in labels}


def jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def checked_witness(row, witness, found_by):
    columns, k, N = row["columns"], row["k"], row["N"]
    if len(set(witness)) != len(witness) or not all(0 <= j < len(columns)
                                                   for j in witness):
        raise SystemExit(f"{row['catalog_label']}: witness {witness} is not a set "
                         f"of column indices")
    fast = FC.Circuit(columns, k, N).harmful(witness)
    literal = literal_harmful(columns, k, witness)
    if not (fast and literal):
        raise SystemExit(f"{row['catalog_label']}: the fault {witness} from "
                         f"{found_by} is not harmful (faultcore {fast}, literal "
                         f"{literal})")
    return {"label": row["catalog_label"], "n": row["n"], "k": k, "N": N,
            "columns_sha256": K.digest(columns), "witness": list(witness),
            "weight": len(witness), "found_by": found_by,
            "checks": {"faultcore_harmful": fast, "literal_harmful": literal}}


def kernel_records(rows):
    """The kernel's lower bound per row, and its faults."""
    swept = defaultdict(dict)                 # label -> weight -> [statuses]
    witnesses = []
    for record in jsonl(EVIDENCE / "laptop" / "mitm_runs.jsonl"):
        parts = record["parts"]
        whole = [p for p in parts if p["slice"][1] == 1]
        status = ("clean" if whole and all(p["status"] == "clean" and p["complete"]
                                           for p in whole) else record["status"])
        swept[record["label"]].setdefault(record["w"], []).append(status)
        if record.get("witness"):
            witnesses.append(checked_witness(
                rows[record["label"]], record["witness"],
                f"{KERNEL}, weight {record['w']}, laptop "
                f"(evidence/laptop/mitm_runs.jsonl)"))
    slices = defaultdict(dict)
    for record in jsonl(EVIDENCE / "laptop" / "mitm_slices.jsonl"):
        result = record["result"]
        i, m = record["slice"]
        if result["status"] == "clean" and result["complete"]:
            slices[(record["label"], record["w"])].setdefault(m, set()).add(i)
    for (label, weight), by_m in slices.items():
        if any(len(done) == m for m, done in by_m.items()):
            swept[label].setdefault(weight, []).append("clean")
    for path in sorted((EVIDENCE / "zaratan" / "zaratan" / "out").rglob("w8_*.json")):
        result = json.loads(path.read_text(encoding="utf-8"))
        label = {742: "742.36.6.a", 959: "959.65.6.a"}[result["n"]]
        if result["status"] == "found":
            witnesses.append(checked_witness(
                rows[label], result["witness"],
                f"{KERNEL}, weight 8, slice {result['slice'][0]} of "
                f"{result['slice'][1]}, Zaratan "
                f"(evidence/zaratan/zaratan/{path.relative_to(EVIDENCE / 'zaratan' / 'zaratan').as_posix()})"))
    records = []
    for label, weights in sorted(swept.items()):
        top = 0
        while "clean" in weights.get(top + 1, []):
            top += 1
        if top:
            records.append((label, KERNEL, top + 1,
                            f"weights 1 to {top} swept clean"))
    return records, witnesses


def search_records(rows):
    """tropidist's threshold searches over all anchors, and their faults."""
    best, witnesses = {}, []
    for run in jsonl(EVIDENCE / "zaratan" / "zaratan_pilots.jsonl"):
        label = run["label"]
        if run["status"] == "found" and run.get("witness") and label in rows:
            witnesses.append(checked_witness(
                rows[label], run["witness"],
                f"{SEARCH} at K={run['K']}, Zaratan run {run['tag']} "
                f"(evidence/zaratan/zaratan_pilots.jsonl)"))
        if run["status"] != "exhausted" or run["anchors"] != "all" \
                or run["rank"] != "natural" or label not in rows:
            continue
        if run["K"] + 1 > best.get(label, (0, ""))[0]:
            best[label] = (run["K"] + 1, f"threshold {run['K']} exhausted over all "
                                         f"anchors, Zaratan run {run['tag']}")
    return [(label, SEARCH, bound, how) for label, (bound, how) in sorted(best.items())], \
        witnesses


def pipeline_records(rows):
    """tropidist's pipeline (dense DP) results, and their faults."""
    records, witnesses = [], []
    for path in sorted((EVIDENCE / "zaratan" / "dp_records").glob("zaratan_*.jsonl")):
        for run in jsonl(path):
            if run["status"] != "exact":
                continue
            label = run["label"]
            records.append((label, PIPELINE, run["lower_bound"],
                            f"config {run['config']}, {run['threads']} threads, "
                            f"{run['wall_seconds']:.0f} s, peak "
                            f"{run['peak_group_rss_mb'] / 1024:.1f} GiB "
                            f"(evidence/zaratan/dp_records/{path.name})"))
            if run.get("witness"):
                witnesses.append(checked_witness(
                    rows[label], run["witness"],
                    f"{PIPELINE}, Zaratan (evidence/zaratan/dp_records/{path.name})"))
    return records, witnesses


def payload():
    cached = cached_rows()
    kernel, kernel_w = kernel_records(cached)
    search, search_w = search_records(cached)
    labels = {run["label"] for path in (EVIDENCE / "zaratan" / "dp_records")
              .glob("zaratan_*.jsonl") for run in jsonl(path)}
    committed = committed_rows(labels)
    pipeline, pipeline_w = pipeline_records(committed)
    records = []
    for label, tool, bound, how in kernel + search + pipeline:
        row = cached.get(label) if tool != PIPELINE else committed[label]
        records.append({"label": label, "n": row["n"], "k": row["k"], "N": row["N"],
                        "columns_sha256": K.digest(row["columns"]),
                        "tool": tool, "lower_bound": bound, "how": how})
    records.sort(key=lambda r: (r["n"], r["k"], r["tool"]))
    witnesses = sorted(kernel_w + search_w + pipeline_w,
                       key=lambda w: (w["n"], w["k"], w["found_by"]))
    return {
        "about": ("Distance bounds from the runs of 6 November 2026 on the UMD "
                  "cluster Zaratan and on a laptop, assembled by "
                  "zaratan_certificates/assemble.py from the run records copied "
                  "into evidence/. Each record is one tool's lower bound for one "
                  "circuit, bound to it by the SHA-256 of its columns as compact "
                  "JSON (master_catalog/constructions.digest). witnesses are the "
                  "harmful faults the runs returned, each re-checked here with "
                  "faultcore.Circuit.harmful and by the XOR of the wire masks. "
                  "The lower bounds are the tools' and are not re-derived by "
                  "verify_catalog.py; every fault is."),
        "method": "exhaustive search",
        "tools": {
            KERNEL: ("the meet-in-the-middle kernel research/plan/mitm/mitm.c "
                     "(copied as evidence/laptop/mitm.c), which sweeps every "
                     "fault of one weight, optionally in slices"),
            SEARCH: ("tropidist (B. Cheng, N. Guo and F. Pan, arXiv:2611.08247; "
                     f"github.com/Fanerst/tropidist at {TROPIDIST_COMMIT[:8]}, "
                     "built with OpenMP) called at one threshold by "
                     "research/plan/tdirect.py (copied as evidence/laptop/tdirect.py)"),
            PIPELINE: ("tropidist's benchmark pipeline, config dp=2 with a larger "
                       "table budget, through research/zaratan/zaratan/dp_run.py, "
                       f"at commit {TROPIDIST_COMMIT[:8]}"),
        },
        "tropidist_commit": TROPIDIST_COMMIT,
        "catalogue_commit": CATALOGUE_COMMIT,
        "research_commits": RESEARCH_COMMITS,
        "records": records,
        "witnesses": witnesses,
    }


def render(blob) -> str:
    import re
    text = json.dumps(blob, indent=1)
    return re.sub(r"\[\s*\n\s*((?:-?\d+,\s+)*-?\d+)\s+\]",
                  lambda m: "[" + re.sub(r"\s+", " ", m.group(1)) + "]", text) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    text = render(payload())
    if args.check:
        if not CERTIFICATES.exists() or CERTIFICATES.read_text(encoding="utf-8") != text:
            raise SystemExit("certificates.json is out of date")
        print("certificates.json is up to date")
        return 0
    CERTIFICATES.write_text(text, encoding="utf-8")
    blob = json.loads(text)
    for record in blob["records"]:
        print(f"  {record['label']:<12} {record['tool']:<18} d >= {record['lower_bound']:<3} "
              f"{record['how']}")
    for w in blob["witnesses"]:
        print(f"  {w['label']:<12} fault of weight {w['weight']}: {w['found_by']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
