#!/usr/bin/env python3
"""Combine the JSON lines of the slices of one weight of mitm.c and re-check every witness with the
catalogue's faultcore.Circuit.harmful and by the XOR of wire masks.

usage: python combine.py LABEL W M FILE...    (M = the number of slices the sweep was split into)
A weight is CLEAN only if all M slices are present, complete and clean."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'mitm'))
import mitm as MM
import faultcore as FC
label, w, m = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
row = json.loads((MM.PLAN / 'data' / 'rows' / f'{label}.json').read_text())
circ = FC.Circuit(row['columns'], row['k'], row['N'])
recs = {}
for fn in sys.argv[4:]:
    for line in open(fn):
        line = line.strip()
        if line.startswith('{'):
            r = json.loads(line)
            if r.get('w') == w and r.get('slice', [None, None])[1] == m:
                recs[r['slice'][0]] = r
witnesses = []
for i, r in sorted(recs.items()):
    if r['status'] == 'found':
        cols = r['witness']
        acc = 0
        for j in cols:
            for q in row['columns'][j]:
                acc ^= 1 << q
        ok = (len(set(cols)) == w and circ.harmful(cols) and acc != 0 and (acc >> row['k']) == 0)
        witnesses.append({'slice': i, 'witness': cols, 'checked': ok})
present = sorted(recs)
clean = len(present) == m and all(r['complete'] == 1 and r['status'] == 'clean' for r in recs.values())
secs = [r['seconds'] for r in recs.values()]
print(json.dumps({'label': label, 'w': w, 'slices_expected': m, 'slices_present': len(present),
                  'parts_log2': sorted({r['parts_log2'] for r in recs.values()}),
                  'statuses': {s: sum(r['status'] == s for r in recs.values()) for s in ('clean', 'found', 'stopped')},
                  'all_clean': clean, 'witnesses': witnesses[:3],
                  'all_witnesses_checked': all(x['checked'] for x in witnesses),
                  'slice_seconds_min_max_sum': [min(secs, default=0), max(secs, default=0), round(sum(secs), 1)]}))
