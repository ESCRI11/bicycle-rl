#!/usr/bin/env bash
# Stream GEPA progress. gepa itself prints nothing until the run ends, so the signal comes
# from ollama's request log (one line per generation) and the OpenRouter balance.
#
#   ./watch-gepa.sh            # refreshes every 30s
#   ./watch-gepa.sh 10         # every 10s
cd "$(dirname "$0")"
every=${1:-30}
target=${TARGET:-150}
cap=$(python3 -c "import json;print(json.load(open('out/spend-baseline.json')).get('cap',1.5))")
# anchor on the process start, not the log's mtime: gepa keeps writing, so mtime walks
# forward and journalctl --since then finds nothing
pid=$(pgrep -f '[g]epa_run.py' | head -1)
start=$(date -d "$(ps -o lstart= -p "$pid" | sed 's/^ *//')" '+%Y-%m-%d %H:%M:%S')
started=$(date -d "$start" +%s)
base=$(python3 -c "import json;print(json.load(open('out/spend-baseline.json'))['before_gepa'])")

while true; do
  n=$(journalctl -u ollama --since "$start" --no-pager 2>/dev/null \
      | grep -c 'POST     "/v1/chat/completions"')
  mins=$(( ($(date +%s) - started) / 60 ))
  spend=$(curl -s --max-time 10 -H "Authorization: Bearer $OPENROUTER_API_KEY" \
          https://openrouter.ai/api/v1/key \
          | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['usage'])" 2>/dev/null)
  alive=$(pgrep -f '[g]epa_run.py' >/dev/null && echo running || echo STOPPED)
  python3 - "$n" "$mins" "$spend" "$base" "$target" "$alive" "$cap" <<'PY'
import sys, datetime
n, mins, spend, base, target, alive, cap = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], float(sys.argv[4]), int(sys.argv[5]), sys.argv[6], float(sys.argv[7])
rate = n / mins if mins else 0
eta = (target - n) / rate if rate else 0
spent = f"${float(spend) - base:.3f} of ${cap:.2f}" if spend else "?"
print(f"{datetime.datetime.now():%H:%M:%S}  {alive:8}  {n:3d}/{target} generations  "
      f"{rate:.2f}/min  eta {eta/60:4.1f}h  spend {spent}", flush=True)
PY
  grep -aE "Iteration [0-9]+: (Best valset aggregate|Found a better|New subsample score|Base program)" \
       out/gepa-run.log 2>/dev/null | tail -2 | sed 's/^/          /'
  sleep "$every"
done
