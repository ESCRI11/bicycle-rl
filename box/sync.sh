#!/usr/bin/env bash
# Push the working tree to the box. Photos go (the judge needs them); .git, the venv and
# rendered output do not. Run from the workstation:
#
#   ./box/sync.sh ubuntu@216.81.200.38
set -euo pipefail
HOST=${1:?usage: sync.sh user@host}
REPO="$(cd "$(dirname "$0")/.." && pwd)"
rsync -az --info=stats1 \
  --exclude .git --exclude .venv --exclude out --exclude __pycache__ \
  --exclude runs --exclude 'gepa-run/run.log' \
  "$REPO/" "$HOST:~/bicycle-rl/"
