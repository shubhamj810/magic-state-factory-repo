#!/bin/bash
#SBATCH -J msf-d2-dp575
#SBATCH -A vva-prj-aac
#SBATCH -p standard
#SBATCH -t 03:00:00
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 24
#SBATCH --mem=96G
#SBATCH --constraint=epyc_7763
#SBATCH -o /scratch/zt1/project/vva-prj/user/sjn/msf/logs/%x-%j.out
set -u
source /scratch/zt1/project/vva-prj/user/sjn/msf/env.sh
cd $MSF/magic-state-factory-research/research/plan
echo "== node $(hostname) $(date)"
echo '== 575.1.6.a: tropidist predicted a 64 GiB table, 823 s on one thread of its authors server'
python zaratan/dp_run.py --pass d2 --limit 9800 --table-gb 72 --threads 24 --mem-mb 90000 575.1.6.a
echo "== done $(date)"
