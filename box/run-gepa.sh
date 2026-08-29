#!/usr/bin/env bash
# Launch a GEPA search on the box. Everything the run needs lives here rather than in an
# ssh one-liner: heredocs inside quoted ssh commands fail silently and cost an hour.
set -uo pipefail
source ~/.orkey                                   # OPENROUTER_API_KEY, chmod 600
export OPENAI_BASE_URL=${OPENAI_BASE_URL:-http://localhost:8001/v1} OPENAI_API_KEY=EMPTY
export MODEL=${MODEL:-Qwen/Qwen2.5-Coder-7B-Instruct}
export JUDGE_BASE_URL=${JUDGE_BASE_URL:-http://localhost:8000/v1}
export JUDGE_MODEL=${JUDGE_MODEL:-Qwen/Qwen2.5-VL-72B-Instruct-AWQ}
export JUDGE_SINGLE=1 RENDER_BACKEND=playwright
cd "$(dirname "$0")/../bike"
exec python3 gepa_run.py \
  --train "${TRAIN:-24}" --val "${VAL:-12}" \
  --max-metric-calls "${CALLS:-600}" \
  --reflection-lm "${REFLECT:-anthropic/claude-sonnet-5}" \
  --workers "${WORKERS:-8}"
