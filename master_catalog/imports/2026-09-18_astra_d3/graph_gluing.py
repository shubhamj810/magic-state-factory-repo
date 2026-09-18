#!/usr/bin/env python3
"""Reproducible d=3 graph gluing. Standard library only; writes only here.

Each graph edge consumes one distinct independent-syndrome port in each seed.
Its two columns are cancelled after quotienting their syndrome difference.
The verifier below independently recovers all degree <=3 moments and counts
all harmful faults of weights 1,2,3 from the emitted columns.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import importlib.util
import itertools
import json
import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('reference_verifier', HERE/'verify_factory.py')
ref = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ref)


def seed(n=127, k=23):
    records = [json.loads(line) for line in (HERE/'seed_catalogue.jsonl').open()]
    rows = [x for x in records if x['n']==n and x['k']==k and x.get('V_ex')==k and x.get('d_exact')==3]
    return min(rows, key=lambda x:(x['A_d'],x['id']))


def join(seeds, edges, port_syndromes=None):
    assert len(edges)==len(set(tuple(sorted(e)) for e in edges))
    assert all(0<=u<v<len(seeds) for u,v in edges), 'use an ordered simple graph'
    total_k = sum(s['k'] for s in seeds)
    out_shift = check_shift = 0
    columns = []
    origins = []
    ports = []
    for v,s in enumerate(seeds):
        if port_syndromes is None:
            assert s['N']-s['k'] >= sum(v in e for e in edges)
        lookup = {}
        for j,col in enumerate(s['columns']):
            om = sum(1 << q for q in col if q<s['k']) << out_shift
            sm = sum(1 << (q-s['k']) for q in col if q>=s['k'])
            lookup[sm] = len(columns)
            columns.append([sm << check_shift,om])
            origins.append([v,j])
        # These seeds have full-simplex check supports, including every e_i.
        chosen=port_syndromes[v] if port_syndromes is not None else [1<<i for i in range(s['N']-s['k'])]
        assert len(chosen)==len(set(chosen))
        assert len(chosen)>=sum(v in e for e in edges)
        selected=[columns[lookup[x]][0] | (columns[lookup[x]][1]<<check_shift+s['N']-s['k']) for x in chosen]
        assert ref.f2_rank(selected)==ref.f2_rank(chosen), 'port set has a harmful dependency'
        ports.append([lookup[x] for x in chosen])
        out_shift += s['k']
        check_shift += s['N']-s['k']
    used = [0]*len(seeds)
    schedule=[]
    for u,v in edges:
        a,b = ports[u][used[u]],ports[v][used[v]]
        used[u]+=1; used[v]+=1
        schedule.append((a,b))
    active = set(range(len(columns)))
    for a,b in schedule:
        ds=columns[a][0]^columns[b][0]
        do=columns[a][1]^columns[b][1]
        if not ds:
            assert not do, 'dependent gluing relation changes logical output'
            active.remove(a); active.remove(b)
            continue
        pivot=ds.bit_length()-1
        active.remove(a); active.remove(b)
        for j in active:
            sm,om=columns[j]
            if sm>>pivot&1:
                sm ^= ds
                om ^= do
            sm=(sm&((1<<pivot)-1)) | ((sm>>(pivot+1))<<pivot)
            columns[j]=[sm,om]
        check_shift-=1
    cols=[]
    for j in sorted(active):
        sm,om=columns[j]
        cols.append([i for i in range(total_k) if om>>i&1]+[total_k+i for i in range(check_shift) if sm>>i&1])
    return {'n':len(cols),'k':total_k,'N':total_k+check_shift,'d':3,'columns':cols,
            'provenance':{'operation':'simple-graph gluing; dependent ports permitted only with full verification',
                          'seed_ids':[s['id'] for s in seeds], 'edges':edges,
                          'port_syndromes':port_syndromes,
                          'port_pairs_original_indices':schedule,
                          'scope':'new construction in this analysis; publication novelty unestablished'}}


def certify(obj):
    cols,k,N=obj['columns'],obj['k'],obj['N']
    rows=ref.wire_rows(cols,N)
    gate,contam=ref.recover_gate(rows,k,N)
    assert not contam, contam[:5]
    assert gate==[(i,) for i in range(k)], gate[:5]
    rankh=ref.f2_rank(rows[k:])
    assert rankh==N-k,(rankh,N-k)
    assert ref.f2_rank(rows)-rankh==k
    counts=ref.harmful_counts(cols,k,3)
    assert counts[1]==counts[2]==0 and counts[3]>0,counts
    return {'n':len(cols),'k':k,'N':N,'V_ex':k,'rho':len(cols)/k,
            'gamma_rho':math.log(len(cols)/k)/math.log(3), 'd_exact':3,
            'A3':counts[3], 'A3_div_k':counts[3]/k,
            'harmful_by_weight':counts,'factory_condition':True,
            'pure_T':True,'independent_outputs':True,'redundant_checks':0}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--copies',type=int,default=8)
    ap.add_argument('--graph',choices=['complete','path','bipartite'],default='complete')
    ap.add_argument('--seed-n',type=int,default=127)
    ap.add_argument('--seed-k',type=int,default=23)
    ap.add_argument('--port-syndromes',help='Comma separated list, randomly permuted independently at each vertex.')
    ap.add_argument('--assignment-seed',type=int,default=18)
    ap.add_argument('--replay',type=Path,help='Rebuild an emitted record from its saved provenance and compare every column.')
    args=ap.parse_args()
    if args.replay:
        old=json.loads(args.replay.read_text())
        catalogue={x['id']:x for x in map(json.loads,(HERE/'seed_catalogue.jsonl').open())}
        prov=old['provenance']
        rec=join([catalogue[i] for i in prov['seed_ids']],prov['edges'],prov.get('port_syndromes'))
        assert rec['columns']==old['columns'] and rec['k']==old['k']
        old['verification']=certify(rec)
        args.replay.write_text(json.dumps(old,indent=2)+'\n')
        print(json.dumps({'replay':str(args.replay),**old['verification']},indent=2),flush=True)
        return
    b=args.copies
    s=seed(args.seed_n,args.seed_k)
    edges=list(itertools.combinations(range(b),2)) if args.graph=='complete' else [(i,i+1) for i in range(b-1)]
    if args.graph=='bipartite':
        assert b%2==0
        edges=[(i,j) for i in range(b//2) for j in range(b//2,b)]
    ports=None
    if args.port_syndromes:
        ps=[int(x) for x in args.port_syndromes.split(',')]
        rng=random.Random(args.assignment_seed)
        ports=[rng.sample(ps,len(ps)) for _ in range(b)]
    rec=join([s]*b,edges,ports)
    facts=certify(rec)
    rec['verification']=facts
    tag='dependent_ports_'+args.graph if ports is not None else args.graph
    path=HERE/'verified'/f"graph_{tag}_n{rec['n']}_k{rec['k']}_d3.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(rec,indent=2)+'\n')
    print(json.dumps({'source_seed':s['id'],'file':str(path.relative_to(ROOT)),**facts},indent=2),flush=True)


if __name__=='__main__':
    main()
