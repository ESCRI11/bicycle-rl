#!/usr/bin/env bash
# Follow the training run from the workstation. Reads the mirror that pull.sh keeps here,
# so it works even when the box is unreachable.
#
#   ./box/watch-train.sh                 # every 60s
set -uo pipefail
D="$(cd "$(dirname "$0")/.." && pwd)/runs/ubuntu_216_81_200_38"
while true; do
  if [ -f "$D/log.jsonl" ]; then
    python3 - "$D" <<'PY'
import json, pathlib, sys, datetime
d = pathlib.Path(sys.argv[1])
rows = [json.loads(l) for l in (d / "log.jsonl").read_text().splitlines() if l.strip()]
if rows:
    last, first = rows[-1], rows[0]
    recent = rows[-16:]
    m = lambda k, rs: sum(r[k] for r in rs) / len(rs)
    print(f"{datetime.datetime.now():%H:%M:%S}  step {last['step']:4d}  "
          f"reward {m('reward_mean', recent):.3f} (first 16: {m('reward_mean', rows[:16]):.3f})  "
          f"gate {m('gate', recent):.2f}  checklist {m('checklist', recent):.3f}  "
          f"sheets: {len(list((d / 'samples').glob('*.png')))}")
PY
  else
    echo "$(date +%H:%M:%S) waiting for the first cycle to finish..."
  fi
  sleep 60
done
