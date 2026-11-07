#!/bin/bash
#SBATCH -J msf-t2a-w8probe
#SBATCH -A vva-prj-aac
#SBATCH -p standard
#SBATCH -t 00:50:00
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 64
#SBATCH --mem=160G
#SBATCH --constraint=epyc_7763
#SBATCH -o /scratch/zt1/project/vva-prj/user/sjn/msf/logs/%x-%j.out
set -u
source /scratch/zt1/project/vva-prj/user/sjn/msf/env.sh
P=$MSF/magic-state-factory-research/research/plan; cd $P
OUT=zaratan/out/$SLURM_JOB_ID; mkdir -p $OUT
echo "== node $(hostname) $(date)"
python zaratan/mkprob.py 255.3.7.a zaratan/prob/255.bin
echo '== slicing check: counts summed over slices equal the unsliced count'
./mitm/mitm zaratan/prob/937.bin 5 --count > $OUT/s937_full.json
for i in 0 1 2 3 4 5 6 7; do ./mitm/mitm zaratan/prob/937.bin 5 --count --parts 3 --slice $i 8; done > $OUT/s937_sl.json
./mitm/mitm zaratan/prob/255.bin 8 --count > $OUT/s255_full.json &
for i in 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do ./mitm/mitm zaratan/prob/255.bin 8 --count --parts 4 --slice $i 16 > $OUT/s255_sl_$i.json & done
wait
python - $OUT <<'PY'
import json, sys, glob
o = sys.argv[1]
def tot(files):
    a = h = 0
    for f in files:
        for l in open(f):
            r = json.loads(l); assert r['complete'] == 1, r; a += r['accepted_raw']; h += r['harmful_raw']
    return a, h
f937 = json.loads(open(o + '/s937_full.json').read())
print('937 w5 full', f937['accepted'], f937['harmful'], 'sliced raw', tot([o + '/s937_sl.json']), 'full raw', f937['accepted_raw'], f937['harmful_raw'])
f255 = json.loads(open(o + '/s255_full.json').read())
print('255.3 w8 full', f255['accepted'], f255['harmful'], 'raw', f255['accepted_raw'], f255['harmful_raw'], 'sliced raw', tot(glob.glob(o + '/s255_sl_*.json')), 'seconds', f255['seconds'])
PY
echo "== timing probe, weight 8, status mode: 959 (--parts 10, slices 0-29 of 1024) and 742 (--parts 8, slices 0-29 of 256)  $(date)"
for i in $(seq 0 29); do timeout 2400 ./mitm/mitm zaratan/prob/959.bin 8 --parts 10 --slice $i 1024 > $OUT/w8_959_$i.json & done
for i in $(seq 0 29); do timeout 2400 ./mitm/mitm zaratan/prob/742.bin 8 --parts 8 --slice $i 256 > $OUT/w8_742_$i.json & done
wait
python zaratan/combine.py 959.65.6.a 8 1024 $OUT/w8_959_*.json
python zaratan/combine.py 742.36.6.a 8 256 $OUT/w8_742_*.json
echo "== done $(date)"
