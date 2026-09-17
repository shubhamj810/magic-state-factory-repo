#!/bin/zsh
# Launch one sweep source at low priority, 2 workers, logging to logs/.
#   ./run48.sh length42            # then length44, length46, length48, rm37_w48
# Refuses to start when the machine is already busy (1-min load > 4).
set -e
cd "$(dirname "$0")"
SRC="$1"; shift || true
[ -n "$SRC" ] || { echo "usage: run48.sh <source> [classify48.py options]"; exit 2; }
LOAD=$(uptime | sed 's/.*load averages*: *//' | awk '{print $1}' | tr -d ',')
if [ "${LOAD%.*}" -ge 4 ]; then echo "load average is $LOAD; not starting"; exit 3; fi
mkdir -p logs
LOG="logs/${SRC}_$(date +%Y%m%d_%H%M%S).log"
echo "logging to $LOG"
exec nice -n 15 ../../../.venv/bin/python -u classify48.py --source "$SRC" --workers 2 "$@" > "$LOG" 2>&1
