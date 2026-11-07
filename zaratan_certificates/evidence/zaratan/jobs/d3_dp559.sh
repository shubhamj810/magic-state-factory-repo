#!/bin/bash
#SBATCH -J msf-d3-dp559
#SBATCH -A vva-prj-aac
#SBATCH -p standard
#SBATCH -t 03:00:00
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 32
#SBATCH --mem=180G
#SBATCH --constraint=epyc_7763
#SBATCH -o /scratch/zt1/project/vva-prj/user/sjn/msf/logs/%x-%j.out
set -u
source /scratch/zt1/project/vva-prj/user/sjn/msf/env.sh
cd $MSF/magic-state-factory-research/research/plan
echo "== node $(hostname) $(date)"
echo '== 559.1.6.a: tropidist predicted a 128 GiB table, 2439 s on one thread of its authors server'
python zaratan/dp_run.py --pass d3 --limit 9800 --table-gb 140 --threads 32 --mem-mb 172000 559.1.6.a
echo "== done $(date)"
