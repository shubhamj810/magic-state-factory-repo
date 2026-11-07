#!/bin/bash
#SBATCH -J msf-t2b-tropi
#SBATCH -A vva-prj-aac
#SBATCH -p standard
#SBATCH -t 01:00:00
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 64
#SBATCH --mem=64G
#SBATCH --constraint=epyc_7763
#SBATCH -o /scratch/zt1/project/vva-prj/user/sjn/msf/logs/%x-%j.out
set -u
source /scratch/zt1/project/vva-prj/user/sjn/msf/env.sh
cd $MSF/magic-state-factory-research/research/plan
export OMP_NUM_THREADS=64
O=data/zaratan_pilots.jsonl
echo "== node $(hostname) $(date)"
echo '== 937 K=6 all anchors (second opinion for d >= 7)'
python tdirect.py 937.87.6.a --K 6 --time-limit 1200 --tag zaratan-t2b --out $O | cut -c1-420
echo '== 959 K=6 all anchors (second opinion for d >= 7)'
python tdirect.py 959.65.6.a --K 6 --time-limit 1200 --tag zaratan-t2b --out $O | cut -c1-420
echo '== cost probes at K=7: 64 evenly spread anchors'
python tdirect.py 742.36.6.a --K 7 --anchors sample:64 --time-limit 400 --tag zaratan-t2b-probe --out $O | cut -c1-420
python tdirect.py 959.65.6.a --K 7 --anchors sample:64 --time-limit 400 --tag zaratan-t2b-probe --out $O | cut -c1-420
echo "== done $(date)"
