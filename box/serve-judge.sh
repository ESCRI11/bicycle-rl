#!/usr/bin/env bash
# Serve a vision model as the local judge, OpenAI-compatible on :8000.
#
#   ./serve-judge.sh                              # the calibrated 72B-AWQ, ~40 GB
#   ./serve-judge.sh Qwen/Qwen2.5-VL-7B-Instruct  # fails the ladder, for comparison only
#
# --limit-mm-per-prompt must be JSON, not image=3: the pairwise prompt sends three images
# (reference photograph + drawing A + drawing B) and vLLM defaults to one.
set -euo pipefail
# default to the model that PASSED calibration. The 7B is a constant-output judge and the
# 32B is inverted (scores the scrambled rung above the correct bicycle); defaulting to
# either silently trains against noise.
MODEL=${1:-${JUDGE_MODEL:-Qwen/Qwen2.5-VL-72B-Instruct-AWQ}}

# These boxes ship the driver but no CUDA toolkit, so anything that JIT-compiles dies with
# "Could not find nvcc and default cuda_home='/usr/local/cuda' doesn't exist". Keep vLLM on
# prebuilt kernels instead of installing a 3 GB toolkit.
export VLLM_USE_FLASHINFER_SAMPLER=${VLLM_USE_FLASHINFER_SAMPLER:-0}
export VLLM_ATTENTION_BACKEND=${VLLM_ATTENTION_BACKEND:-FLASH_ATTN}
exec "$HOME/.local/bin/vllm" serve "$MODEL" \
  --port "${PORT:-8000}" \
  --max-model-len "${MAXLEN:-16384}" \
  --limit-mm-per-prompt '{"image":3}' \
  --gpu-memory-utilization "${GPU_FRAC:-0.85}"
