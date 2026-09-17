#!/bin/zsh
# Memory watchdog for a running sweep: every 30 s, if any classify48 worker
# (or the driver) holds more than MAX_MB resident, stop the whole sweep with
# stop48.sh and say so.  Written after the 2026-09-06 incident, when two
# workers grew to 18 GB + 16 GB on an 8 GB laptop and the machine went into
# swap thrash (load 200) for ~20 minutes.  Exits when no sweep is running.
#
#   ./watchdog48.sh [MAX_MB]        # default 2500
cd "$(dirname "$0")"
MAX_MB=${1:-2500}
while true; do
  driver=$(pgrep -f "classify48.py --source" | head -1)
  [ -n "$driver" ] || { echo "watchdog: no sweep running, exiting"; exit 0; }
  pgid=$(ps -o pgid= -p "$driver" | tr -d ' ')
  # ps's rss ignores swapped/compressed pages (the thrashing workers showed
  # 100 MB there while top said 18 GB), so ask top for the footprint instead.
  pidargs=($(ps -eo pgid,pid | awk -v g="$pgid" '$1==g {print "-pid", $2}'))
  worst=$(top -l 1 -stats pid,mem $pidargs 2>/dev/null | awk '
    /^[0-9]+ / { v=$2; sub(/[+-]$/, "", v); u=substr(v,length(v)); n=substr(v,1,length(v)-1)+0;
                 if (u=="G") n*=1024; else if (u=="K") n/=1024; else if (u!="M") n=v/1048576;
                 if (n>m) m=n } END { print int(m) }')
  if [ "${worst:-0}" -gt "$MAX_MB" ]; then
    echo "watchdog: a sweep process holds ${worst} MB resident (> $MAX_MB); stopping the sweep"
    ./stop48.sh
    exit 1
  fi
  sleep 30
done
