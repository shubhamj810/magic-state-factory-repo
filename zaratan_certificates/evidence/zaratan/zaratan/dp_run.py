#!/usr/bin/env python3
"""tropidist's pipeline (config dp=2, as in research/tropidist/) on chosen catalogue rows, with a larger
table budget and more threads than the laptop allowed.  Runs on Zaratan; each result is checked by
tropirun.run_row exactly as in the laptop passes (witness re-checked with faultcore and by the XOR of
wire masks).  One JSON line per row goes to research/tropidist/work/zaratan_<pass>.jsonl.

usage: python dp_run.py --pass NAME --limit SECONDS --table-gb G --threads T --mem-mb M LABEL ...
"""
import argparse, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tropidist'))
import tropirun as T

ap = argparse.ArgumentParser()
ap.add_argument('--pass', dest='pass_name', required=True)
ap.add_argument('--limit', type=float, required=True)
ap.add_argument('--table-gb', type=int, required=True)
ap.add_argument('--threads', type=int, default=1)
ap.add_argument('--mem-mb', type=float, required=True)
ap.add_argument('labels', nargs='+')
a = ap.parse_args()
T.THREADS = a.threads
T.CPU_ENV['OMP_NUM_THREADS'] = str(a.threads)
rows = {r['catalog_label']: r for r in T.load_rows()}
commit = T.tropidist_commit()
records = T.HERE / 'records_zaratan' / a.pass_name
T.WORK.mkdir(parents=True, exist_ok=True)
out = T.WORK / f'zaratan_{a.pass_name}.jsonl'
config = f'dp=2,table_gb={a.table_gb}'
print(f'tropidist {commit}, config {config}, threads {a.threads}', flush=True)
for label in a.labels:
    t0 = time.time()
    res = T.run_row(rows[label], a.limit, records, commit, mem_limit_mb=a.mem_mb, config=config)
    with open(out, 'a') as f:
        f.write(json.dumps(res) + '\n')
    print(json.dumps({k: res.get(k) for k in ('label', 'status', 'lower_bound', 'upper_bound', 'witness_check',
                                              'wall_seconds', 'peak_group_rss_mb', 'runner_note', 'decision')}),
          flush=True)
