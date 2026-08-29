#!/usr/bin/env bash
# Mirror the training run off the box, forever. The box is rented and can disappear with no
# notice; every sample, reward, adapter and log has to exist here too.
#
#   ./box/pull.sh ubuntu@216.81.200.38 &        # every 5 min by default
set -uo pipefail
HOST=${1:?usage: pull.sh user@host [seconds]}
EVERY=${2:-300}
DEST="$(cd "$(dirname "$0")/.." && pwd)/runs/$(echo "$HOST" | tr '@.:' '___')"
mkdir -p "$DEST"
while true; do
  if rsync -az --exclude '*/tokens.pt' "$HOST:~/bicycle-rl/bike/run/" "$DEST/" 2>/dev/null; then
    n=$(ls "$DEST/samples" 2>/dev/null | wc -l)
    s=$(python3 -c "import json;print(json.load(open('$DEST/state.json'))['step'])" 2>/dev/null || echo ?)
    echo "$(date +%H:%M:%S) pulled: step $s, $n sample sheets -> $DEST"
  fi
  sleep "$EVERY"
done
