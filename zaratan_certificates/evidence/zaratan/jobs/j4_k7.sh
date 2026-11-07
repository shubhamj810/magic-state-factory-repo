#!/bin/bash
#SBATCH -J msf-j4-k7
#SBATCH -A vva-prj-aac
#SBATCH -p standard
#SBATCH -t 02:00:00
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
echo '== 998.26.6.a K=7, all anchors (probe: 16 anchors in 2.9 s)'
python tdirect.py 998.26.6.a --K 7 --task-depth 2 --time-limit 1200 --tag zaratan-j4 --out $O | cut -c1-300
echo '== 959.65.6.a K=7, 16 anchors with a depth-3 table (probe at depth 2: 513 s)'
python tdirect.py 959.65.6.a --K 7 --anchors sample:16 --task-depth 2 --k-table 3 --time-limit 900 --tag zaratan-j4-probe-kt3 --out $O | cut -c1-300
echo '== 742.36.6.a K=7, all anchors (probe: 16 anchors in 41 s)'
python tdirect.py 742.36.6.a --K 7 --task-depth 2 --time-limit 4500 --tag zaratan-j4 --out $O | cut -c1-300
echo "== done $(date)"
