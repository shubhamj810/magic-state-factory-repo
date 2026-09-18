# Distance-three graph-glued factories (2026-09-18)

Nine new pure-T witnesses imported from the graph-gluing analysis in the companion AI
search repository. All have exact distance three. The main rate results are
495-to-99 and 880-to-176 (five inputs per output); 255-to-47 meets the earlier
fixed-length width target. General graph gluing has prior art; global novelty
and optimality are not asserted.

`factories.json` is the exact input to the unmodified master catalogue merger.
`witnesses/` preserves the original matrices and construction provenance.
`seed_catalogue.jsonl` contains all four seed circuits, so reconstruction does
not depend on the companion repository. `graph_gluing.py` has only its source
paths adapted for this self-contained bundle. It uses `verify_factory.py`, an
unchanged copy of the companion repository's independent standard-library
reference verifier, and asserts exact column equality when replaying a witness.
The destination merger and full `master_catalog/verify_catalog.py` also verify
the imported rows using this repository's current authority.

From this directory, with Python 3.10 or newer:

```bash
python3 graph_gluing.py --replay witnesses/graph_dependent_ports_complete_n495_k99_d3.json
python3 verify_factory.py witnesses/graph_dependent_ports_complete_n495_k99_d3.json
```

From the repository root:

```bash
.venv/bin/python master_catalog/merge_results.py master_catalog/imports/2026-09-18_graph_gluing_d3/factories.json --dry-run
.venv/bin/python master_catalog/verify_catalog.py
.venv/bin/python -m unittest discover -s master_catalog/tests
```

Acceptance and logical-error numbers use independent stochastic input Z faults
and ideal Clifford operations. At p=1e-4, the 495-to-99 witness has acceptance
0.9517028063001617, retry-inclusive cost 5.253740944022212 per output, and worst
marginal error 2.237606076711557e-10. Detailed exact-channel certificates remain
in the original analysis; the catalogue claims follow from columns alone.

Verification receipt: [`verification.json`](verification.json) records all nine
witness hashes, exact-distance fault witnesses, catalogue hash, completed
reconstruction/merge/full-verifier checks, and the 247 passing regression tests.
Full transcripts are in [`validation_logs/`](validation_logs/).
