#!/usr/bin/env python3
"""The catalogue's own exhaustive sweep (faultcore.scan_weight) with a raised budget.

    python own_sweep.py LABEL --weights 1-5 [--max-pairs 2000000] [--max-triples 1000000000]
                        [--witness i,j,...] [--problem-file F]

Runs master_catalog/faultcore.py from the catalogue repository unchanged (read-only), on a main-file
row cached by tdirect.py in data/rows/, with a Budget larger than verify_catalog's default.  Each
weight's status is 'clean', 'found' or 'skipped' exactly as faultcore reports it; nothing is
inferred from a skipped weight.  A --witness is re-checked with Circuit.harmful.  One JSON line per
run goes to data/own_sweeps.jsonl.
"""
from __future__ import annotations

import argparse
import json
import platform
import resource
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATREPO = Path("/Users/shubhamjain/Documents/IBM internship/Shraddha (Magic states)/magic-state-factory-repo")
sys.path.insert(0, str(CATREPO / "master_catalog"))
import faultcore as FC                                # noqa: E402


def peak_rss_mb() -> float:
    ru = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return ru / (1024 * 1024) if platform.system() == "Darwin" else ru / 1024


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("label")
    ap.add_argument("--weights", default="1-5")
    ap.add_argument("--max-pairs", type=int, default=2_000_000)
    ap.add_argument("--max-triples", type=int, default=1_000_000_000)
    ap.add_argument("--max-candidates", type=int, default=3_000_000)
    ap.add_argument("--max-triple-table", type=int, default=6_000_000)
    ap.add_argument("--witness", default=None)
    ap.add_argument("--problem-file", default=None)
    a = ap.parse_args()
    src = Path(a.problem_file) if a.problem_file else HERE / "data" / "rows" / f"{a.label}.json"
    row = json.loads(src.read_text())
    lo, hi = (int(x) for x in a.weights.split("-"))
    budget = FC.Budget(max_pairs=a.max_pairs, max_triples=a.max_triples, max_candidates=a.max_candidates,
                       max_triple_table=a.max_triple_table)
    t0 = time.time()
    circuit = FC.Circuit(row["columns"], row["k"], row["N"], budget)
    out = {"label": a.label, "n": circuit.n, "k": row["k"], "r": row["N"] - row["k"],
           "budget": vars(budget), "folded": circuit.folded, "weights": {}}
    for w in range(lo, hi + 1):
        t = time.time()
        status, witness, _ = FC.scan_weight(circuit, w)
        out["weights"][w] = {"status": status, "witness": list(witness) if witness else None,
                             "seconds": round(time.time() - t, 2)}
        print(w, out["weights"][w], flush=True)
        if status != "clean":
            break
    if a.witness:
        cols = [int(x) for x in a.witness.split(",")]
        out["witness_check"] = {"cols": cols, "weight": len(set(cols)), "harmful": circuit.harmful(cols)}
    out["wall_seconds"] = round(time.time() - t0, 2)
    out["peak_rss_mb"] = round(peak_rss_mb(), 1)
    with open(HERE / "data" / "own_sweeps.jsonl", "a") as f:
        f.write(json.dumps(out) + "\n")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
