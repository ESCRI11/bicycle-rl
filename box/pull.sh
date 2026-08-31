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
# never let an empty or younger run overwrite a finished one: a re-rented box can come back
# on an IP we have already mirrored, and DEST is derived from that IP
have=$(python3 -c "import json;print(json.load(open('$DEST/state.json'))['step'])" 2>/dev/null || echo 0)
if [ "$have" -gt 0 ]; then
  there=$(ssh -o BatchMode=yes -o ConnectTimeout=15 "$HOST" \
    "python3 -c \"import json;print(json.load(open('bicycle-rl/bike/run/state.json'))['step'])\"" 2>/dev/null || echo 0)
  if [ "${there:-0}" -lt "$have" ]; then
    echo "REFUSING: $DEST holds $have steps, the box only has ${there:-0}."
    echo "Move it aside first — that mirror is the only copy of a finished run."
    exit 1
  fi
fi

# A silent mirror is worse than no mirror: this loop once ran for three hours against a box
# that had been reclaimed, printing nothing, while it looked alive in `pgrep`. Failures are
# loud now, and the message says how long it has been since the last good pull.
fails=0; last=$(date +%s)
while true; do
  # timeout + keepalives: suspending the laptop freezes the TCP connection and a plain rsync
  # then blocks forever — alive in `pgrep`, silent in the log, mirroring nothing. Same silent
  # failure as before, wearing a different hat: a hang is neither success nor error.
  if err=$(timeout 600 rsync -az \
             -e 'ssh -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=3' \
             --exclude '*/tokens.pt' --exclude 'checkpoints/*/optimizer*' \
             "$HOST:~/bicycle-rl/bike/run/" "$DEST/" 2>&1); then
    fails=0; last=$(date +%s)
    n=$(ls "$DEST/samples" 2>/dev/null | wc -l)
    s=$(python3 -c "import json;print(json.load(open('$DEST/state.json'))['step'])" 2>/dev/null || echo ?)
    echo "$(date +%H:%M:%S) pulled: step $s, $n sample sheets -> $DEST"
  else
    fails=$((fails + 1))
    echo "$(date +%H:%M:%S) PULL FAILED (${fails}x, $(( ($(date +%s) - last) / 60 ))m since last good pull)"
    echo "  ${err##*$'\n'}"
    [ "$fails" = 3 ] && echo "  three in a row — the box is probably gone. The mirror is your copy."
  fi
  sleep "$EVERY"
done
