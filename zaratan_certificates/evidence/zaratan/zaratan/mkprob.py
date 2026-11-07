#!/usr/bin/env python3
"""Write the binary problem file of mitm.c for a cached row: python mkprob.py LABEL OUT.bin"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'mitm'))
import mitm as MM
row = json.loads((MM.PLAN / 'data' / 'rows' / f'{sys.argv[1]}.json').read_text())
syn, out = MM.masks(row['columns'], row['k'])
MM.write_problem(Path(sys.argv[2]), syn, out, row['k'])
print(sys.argv[1], 'n', row['n'], 'k', row['k'], 'checks', row['N'] - row['k'])
