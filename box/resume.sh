#!/usr/bin/env bash
# Put a mirrored training run back onto a fresh box so it continues where it stopped.
#
#   ./box/sync.sh   ubuntu@<new-ip>                 # code + photos
#   ssh ubuntu@<new-ip> 'bash -s' < box/setup.sh    # deps, ~10 min
#   ./box/resume.sh ubuntu@<new-ip> [runs/<old>]    # adapter + optimiser + counters
#   ssh ubuntu@<new-ip>
#     cd bicycle-rl/bike && setsid nohup ./train/loop.sh <cycles-left> 128 > ~/train.log 2>&1 &
#
# The loop reads state.json for which cycle to start at, so pass the number of cycles STILL
# TO RUN, not the total. Past cycles' tokens.pt are not mirrored (they are large and only
# needed by the update that already happened), so an interrupted cycle restarts cleanly.
set -euo pipefail
HOST=${1:?usage: resume.sh user@host [run-dir]}
ROOT="$(cd "$(dirname "$0")/.." && pwd)/runs"
SRC=${2:-$(ls -dt "$ROOT"/*/ 2>/dev/null | head -1)}
[ -f "$SRC/state.json" ] || { echo "no state.json in $SRC"; exit 1; }

step=$(python3 -c "import json;print(json.load(open('$SRC/state.json'))['step'])")
cycle=$(python3 -c "import json;print(json.load(open('$SRC/state.json'))['cycle'])")
echo "resuming $SRC — step $step, next cycle $cycle"

ssh -o BatchMode=yes "$HOST" 'mkdir -p ~/bicycle-rl/bike/run'
rsync -az --info=stats1 "$SRC/lora" "$SRC/opt.pt" "$SRC/state.json" "$SRC/log.jsonl" \
  "$HOST:~/bicycle-rl/bike/run/"
echo
echo "on the box:  cd bicycle-rl/bike && setsid nohup ./train/loop.sh \$((20 - $cycle)) 128 > ~/train.log 2>&1 &"
echo "here:        ./box/pull.sh $HOST 120 &   and   ./box/watch-train.sh $HOST"
