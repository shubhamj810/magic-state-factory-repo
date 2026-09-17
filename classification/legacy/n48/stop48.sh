#!/bin/zsh
# Stop a running sweep cleanly: kill the driver's whole process group so the
# spawned workers die with it.  (`pkill -f classify48.py` alone kills only the
# driver; the workers' command lines do not mention classify48.py and keep
# burning two cores as orphans -- learned the hard way, see logs/.)
#
#   ./stop48.sh            stop every classify48.py driver
#   ./stop48.sh length44   stop the driver of one source
setopt NULL_GLOB
pat="classify48.py --source ${1:-}"
pids=($(pgrep -f "$pat" | grep -v "^$$\$"))
if (( ${#pids} == 0 )); then echo "no sweep matching '$pat'"; fi
for pid in $pids; do
  pgid=$(ps -o pgid= -p "$pid" | tr -d ' ')
  echo "stopping driver $pid (process group $pgid)"
  kill -TERM -- "-$pgid" 2>/dev/null || kill -TERM "$pid"
done
# Orphaned workers (parent gone) from an earlier bad kill: report, do not kill.
orphans=($(ps -eo pid,ppid,command | awk '$2==1 && /multiprocessing.spawn/ {print $1}'))
if (( ${#orphans} > 0 )); then
  echo "orphaned multiprocessing workers (ppid 1): $orphans -- kill them by hand if they are ours"
fi
