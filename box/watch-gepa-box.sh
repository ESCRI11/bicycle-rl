#!/usr/bin/env bash
# Follow a GEPA run on the box from the workstation. gepa prints only on iteration
# boundaries, so this shows the valset scores as they land plus whether it is still alive.
#
#   ./box/watch-gepa-box.sh ubuntu@<ip>          # every 60s
set -uo pipefail
HOST=${1:?usage: watch-gepa-box.sh user@host}
EVERY=${2:-60}
while true; do
  ssh -o BatchMode=yes -o ConnectTimeout=15 "$HOST" '
    alive=$(pgrep -f "[g]epa_run" >/dev/null && echo running || echo STOPPED)
    base=$(grep -aoE "Base program full valset score: [0-9.]+" ~/gepa.log | tail -1 | grep -oE "[0-9.]+$")
    best=$(grep -aoE "Best valset aggregate score so far: [0-9.]+" ~/gepa.log | tail -1 | grep -oE "[0-9.]+$")
    iter=$(grep -acE "^Iteration [0-9]+:" ~/gepa.log)
    cands=$(grep -ac "New program candidate index" ~/gepa.log)
    echo "$(date +%H:%M:%S)  $alive  iters=$iter  candidates=$cands  seed=${base:-?}  best=${best:-none yet}"
    grep -aE "Found a better program|did not propose|New subsample score" ~/gepa.log | tail -1 | sed "s/^/            /"
  ' 2>/dev/null || echo "$(date +%H:%M:%S)  (ssh refused — box busy, retrying)"
  sleep "$EVERY"
done
