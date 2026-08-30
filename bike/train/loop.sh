#!/usr/bin/env bash
# The training loop. One cycle = sample a batch, swap in the judge, score, swap it out,
# update. Three separate processes because the judge needs 68 GB and the policy needs the
# card to itself — and because a crash then costs one cycle, not the run.
#
#   ./train/loop.sh 20 128        # 20 cycles of 128 rollouts (16 steps each) = 320 steps
set -uo pipefail
cd "$(dirname "$0")/.."
CYCLES=${1:-20}; N=${2:-128}; GROUP=${GROUP:-8}
RUN=${RUN:-$PWD/run}; mkdir -p "$RUN/cycles" "$RUN/samples"
export RENDER_BACKEND=playwright JUDGE_SINGLE=1 \
       JUDGE_BASE_URL=http://localhost:8000/v1 \
       JUDGE_MODEL=Qwen/Qwen2.5-VL-72B-Instruct-AWQ \
       PAIRWISE_MODEL=Qwen/Qwen2.5-VL-72B-Instruct-AWQ

start=$( [ -f "$RUN/state.json" ] && python3 -c "import json;print(json.load(open('$RUN/state.json'))['cycle'])" 2>/dev/null || echo 0 )
for c in $(seq "$start" $((start + CYCLES - 1))); do
  D="$RUN/cycles/$(printf %03d "$c")"; mkdir -p "$D"
  echo "=== cycle $c  $(date +%H:%M:%S)"

  [ -f "$D/tokens.pt" ] || python3 train/rollout.py --out "$D" -n "$N" --lora "$RUN/lora" || exit 1

  if [ ! -f "$D/rewards.json" ]; then
    setsid nohup ../box/serve-judge.sh "$JUDGE_MODEL" > "$RUN/judge.log" 2>&1 < /dev/null &
    for _ in $(seq 60); do curl -s --max-time 3 localhost:8000/v1/models | grep -q 72B && break; sleep 10; done
    python3 train/score.py --dir "$D" --group "$GROUP"
    pkill -f "[v]llm serve"; sleep 8
    # HPS runs alone: it peaks at 64GB, the judge holds 46GB, and the card is 80GB. It is
    # fast (0.16s an image, ~20s a cycle) so sequencing costs almost nothing.
    HPS_BATCH=${HPS_BATCH:-2} python3 train/score.py --dir "$D" --group "$GROUP" --hps-only
  fi

  python3 train/update.py --dir "$D" --run "$RUN" --group "$GROUP" || exit 1
  python3 -c "
import json,pathlib
p=pathlib.Path('$RUN/state.json'); s=json.loads(p.read_text()); s['cycle']=$c+1; p.write_text(json.dumps(s))"

  # a contact sheet every cycle: 16 steps apart, which is the sampling cadence we want
  step=$(python3 -c "import json;print(json.load(open('$RUN/state.json'))['step'])")
  python3 sheet.py "$D"/gen_*.png -o "$RUN/samples/step_$(printf %04d "$step").png" --cols 8 --cell 150 2>/dev/null
  echo "=== cycle $c done, step $step"
done
