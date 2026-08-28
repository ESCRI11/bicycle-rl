#!/usr/bin/env bash
# Serve a vision model as the local judge, OpenAI-compatible on :8000.
#
#   ./serve-judge.sh                                   # Qwen2.5-VL-7B
#   ./serve-judge.sh Qwen/Qwen2.5-VL-72B-Instruct-AWQ  # ~40 GB, stronger
#
# --limit-mm-per-prompt must be JSON, not image=3: the pairwise prompt sends three images
# (reference photograph + drawing A + drawing B) and vLLM defaults to one.
set -euo pipefail
MODEL=${1:-Qwen/Qwen2.5-VL-7B-Instruct}
exec "$HOME/.local/bin/vllm" serve "$MODEL" \
  --port "${PORT:-8000}" \
  --max-model-len "${MAXLEN:-16384}" \
  --limit-mm-per-prompt '{"image":3}' \
  --gpu-memory-utilization "${GPU_FRAC:-0.85}"
