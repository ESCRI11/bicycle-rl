#!/usr/bin/env bash
# Follow a training run from the workstation, reading the local mirror — so it keeps working
# when the box is unreachable, which these instances often are.
#
#   ./box/watch-train.sh                            # the most recently updated mirror
#   ./box/watch-train.sh ubuntu@216.81.245.141      # a specific box
#   ./box/watch-train.sh ubuntu@216.81.245.141 30   # every 30s
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)/runs"
if [ $# -ge 1 ] && [ -n "${1:-}" ]; then
  D="$ROOT/$(echo "$1" | tr '@.:' '___')"
else
  D=$(ls -dt "$ROOT"/*/ 2>/dev/null | head -1)      # newest mirror wins
fi
EVERY=${2:-60}
echo "watching $D"
while true; do
  if [ -f "$D/log.jsonl" ]; then
    python3 - "$D" <<'PY'
import json, pathlib, sys, datetime
d = pathlib.Path(sys.argv[1])
rows = [json.loads(l) for l in (d / "log.jsonl").read_text().splitlines() if l.strip()]
if rows:
    m = lambda k, rs: sum(r[k] for r in rs) / len(rs)
    recent, first = rows[-16:], rows[:16]
    print(f"{datetime.datetime.now():%H:%M:%S}  step {rows[-1]['step']:4d}/320  "
          f"reward {m('reward_mean', recent):.3f} (first16 {m('reward_mean', first):.3f})  "
          f"gate {m('gate', recent):.2f}  checklist {m('checklist', recent):.3f}  "
          f"sheets {len(list((d / 'samples').glob('*.png')))}")
PY
  else
    echo "$(date +%H:%M:%S)  $D — waiting for the first cycle to finish"
  fi
  sleep "$EVERY"
done
