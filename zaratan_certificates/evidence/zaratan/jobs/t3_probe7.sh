#!/bin/bash
#SBATCH -J msf-t3-probe7
#SBATCH -A vva-prj-aac
#SBATCH -p standard
#SBATCH -t 01:10:00
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
echo "== node $(hostname) $(date)"
echo '== K=7 cost probes: 16 evenly spread anchors, task depth 2 so that 64 threads share them'
for L in 742.36.6.a 959.65.6.a 988.36.6.a 998.26.6.a; do
  python tdirect.py $L --K 7 --anchors sample:16 --task-depth 2 --time-limit 900 --tag zaratan-t3-probe --out data/zaratan_pilots.jsonl | cut -c1-300
done
echo "== done $(date)"
