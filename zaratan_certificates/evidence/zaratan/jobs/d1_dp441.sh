#!/bin/bash
#SBATCH -J msf-d1-dp441
#SBATCH -A vva-prj-aac
#SBATCH -p standard
#SBATCH -t 03:00:00
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 16
#SBATCH --mem=64G
#SBATCH --constraint=epyc_7763
#SBATCH -o /scratch/zt1/project/vva-prj/user/sjn/msf/logs/%x-%j.out
set -u
source /scratch/zt1/project/vva-prj/user/sjn/msf/env.sh
cd $MSF/magic-state-factory-research/research/plan
echo "== node $(hostname) $(date)"
echo '== 441.1.6.a: tropidist predicted a 32 GiB dense-DP table, 515 s on one thread of its authors server'
python zaratan/dp_run.py --pass d1 --limit 9800 --table-gb 40 --threads 16 --mem-mb 56000 441.1.6.a
echo "== done $(date)"
