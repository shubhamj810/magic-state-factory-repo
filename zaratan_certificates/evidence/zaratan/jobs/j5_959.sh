#!/bin/bash
#SBATCH -J msf-j5-k7-959
#SBATCH -A vva-prj-aac
#SBATCH -p standard
#SBATCH -t 00:40:00
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
echo '== 959.65.6.a K=7, all anchors, depth-3 table (probe: 16 anchors in 3 s)'
python tdirect.py 959.65.6.a --K 7 --task-depth 2 --k-table 3 --time-limit 1800 --tag zaratan-j5 --out $O | cut -c1-300
echo "== done $(date)"
