#!/usr/bin/env python3
"""The catalogue's own sweep on 1715.287.3.a, with a raised budget.

    python round2_certificates/own_sweep.py      # about 7 minutes, 0.6 GB

`verify_catalog` runs `faultcore.scan_weight` with a default budget that,
at n = 1715, proves only the floor 3.  This runs the same function, unchanged,
on the row's columns with the budget the research's `own_sweep.py` used
(research/plan/own_sweep.py at 9932b15), for weights 1 to 5, and writes one
JSON line to `evidence/own_sweep_1715.json`: each weight's status as
`scan_weight` reports it (``clean``, ``found`` or ``skipped``; nothing is
inferred from a skipped weight), the budget, the SHA-256 of the columns and
the commit of this repository it ran at.
"""
from __future__ import annotations

import json
import platform
import resource
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO / "master_catalog"))

import catalogfile as CF                                          # noqa: E402
import constructions as K                                         # noqa: E402
import faultcore as FC                                            # noqa: E402

LABELS = ("1715.287.3.a", "1715.287.6.a")
BUDGET = dict(max_pairs=2_000_000, max_triples=1_000_000_000,
              max_candidates=3_000_000, max_triple_table=6_000_000)


def main():
    row = next(r for r in CF.load_all()["factories"]
               if r["catalog_label"] in LABELS
               or set(r.get("former_labels") or []) & set(LABELS))
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                            capture_output=True, text=True).stdout.strip()
    started = time.time()
    circuit = FC.Circuit(row["columns"], row["k"], row["N"], FC.Budget(**BUDGET))
    out = {"label": "1715.287.3.a", "n": circuit.n, "k": row["k"], "N": row["N"],
           "columns_sha256": K.digest(row["columns"]), "commit": commit,
           "budget": BUDGET, "folded": circuit.folded, "weights": {}}
    for w in range(1, 6):
        t = time.time()
        status, witness, _ = FC.scan_weight(circuit, w)
        out["weights"][str(w)] = {"status": status,
                                  "witness": list(witness) if witness else None,
                                  "seconds": round(time.time() - t, 2)}
        print(w, out["weights"][str(w)], flush=True)
        if status != "clean":
            break
    ru = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    out["wall_seconds"] = round(time.time() - started)
    out["peak_rss_mb"] = round(ru / (1 << 20) if platform.system() == "Darwin"
                               else ru / 1024, 1)
    (HERE / "evidence" / "own_sweep_1715.json").write_text(
        json.dumps(out) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
