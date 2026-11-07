#!/bin/bash
#SBATCH -J msf-t1-smoke
#SBATCH -A vva-prj-aac
#SBATCH -p debug
#SBATCH -t 00:15:00
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 32
#SBATCH --mem=64G
#SBATCH --constraint=epyc_7763
#SBATCH -o /scratch/zt1/project/vva-prj/user/sjn/msf/logs/%x-%j.out
set -u
source /scratch/zt1/project/vva-prj/user/sjn/msf/env.sh
P=$MSF/magic-state-factory-research/research/plan
cd $P
echo "== node $(hostname) $(date)"; lscpu | grep 'Model name'
echo '== build kernel'
gcc -O3 -o mitm/mitm mitm/mitm.c || exit 1
echo '== build tropidist libs (OpenMP)'
python -c "
import sys; sys.path.insert(0, '$MSF/tropidist-src')
from cdist import search, kernel
print(search._build()); print(kernel.build())
import subprocess; print(subprocess.run(['ldd', search._build()], capture_output=True, text=True).stdout)
"
echo '== kernel brute-force test (200 trials, seed 7)'
time timeout 150 python mitm/mitm.py test 200 7 | tail -3
echo '== tropidist modes vs brute force (seed 21), 2 threads'
OMP_NUM_THREADS=2 timeout 150 python test_modes.py 150 21 | tail -4
echo '== tdirect 901 K=6, 32 threads (laptop: found, 0.08 s)'
OMP_NUM_THREADS=32 timeout 120 python tdirect.py 901.123.6.a --K 6 --tag zaratan-smoke --out data/zaratan_pilots.jsonl | cut -c1-400
echo '== kernel 937 weights 1-7 (laptop: clean to 6, witness at 7, 39 s)'
time timeout 150 python mitm/mitm.py row 937.87.6.a 1-7 | tail -8 | cut -c1-300
echo '== tdirect 935 K=6, 32 threads (laptop single thread: exhausted, 1056 s)'
OMP_NUM_THREADS=32 timeout 300 python tdirect.py 935.89.6.a --K 6 --time-limit 280 --tag zaratan-smoke --out data/zaratan_pilots.jsonl | cut -c1-500
echo "== done $(date)"
