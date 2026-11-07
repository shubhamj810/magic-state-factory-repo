#!/bin/bash
#SBATCH -J msf-t2c-dp
#SBATCH -A vva-prj-aac
#SBATCH -p standard
#SBATCH -t 00:30:00
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 8
#SBATCH --mem=32G
#SBATCH --constraint=epyc_7763
#SBATCH -o /scratch/zt1/project/vva-prj/user/sjn/msf/logs/%x-%j.out
set -u
source /scratch/zt1/project/vva-prj/user/sjn/msf/env.sh
cd $MSF/magic-state-factory-research/research/plan
echo "== node $(hostname) $(date)"
echo '== DP driver test: 417.1.6.a (laptop o2: exact 13 with a 4 GiB table in 20 s) and 177.1.7.a'
python zaratan/dp_run.py --pass t2c --limit 900 --table-gb 16 --threads 8 --mem-mb 28000 177.1.7.a 417.1.6.a
echo "== done $(date)"
