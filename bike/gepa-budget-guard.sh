#!/usr/bin/env bash
# Kills the GEPA run if it spends past the cap. The run has no idea what it costs, and the
# last one overshot its estimate by 2.3x, so the stop is automatic rather than a promise.
#
#   ./gepa-budget-guard.sh &        # CAP=1.50 by default
cd "$(dirname "$0")"
CAP=${CAP:-1.50}
base=$(python3 -c "import json;print(json.load(open('out/spend-baseline.json'))['before_gepa'])")
while pgrep -f '[g]epa_run.py' >/dev/null; do
  u=$(curl -s --max-time 15 -H "Authorization: Bearer $OPENROUTER_API_KEY" \
      https://openrouter.ai/api/v1/key \
      | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['usage'])" 2>/dev/null)
  if [ -n "$u" ] && [ "$(python3 -c "print(1 if $u-$base > $CAP else 0)")" = 1 ]; then
    pkill -f '[g]epa_run.py'
    echo "$(date +%T) BUDGET STOP at \$$(python3 -c "print(f'{$u-$base:.3f}')") > cap \$$CAP" \
      | tee -a out/gepa-budget.log
    exit 1
  fi
  sleep 60
done
echo "$(date +%T) finished under budget (\$$(python3 -c "print(f'{${u:-0}-$base:.3f}')"))" | tee -a out/gepa-budget.log
