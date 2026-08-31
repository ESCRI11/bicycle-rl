#!/usr/bin/env bash
# Build contact sheets from the mirrored run. The box makes its own, but this works from
# whatever has been pulled down, which is the copy that survives the box being killed.
set -uo pipefail
cd "$(cd "$(dirname "$0")/.." && pwd)"
D=${1:-runs/run1}
mkdir -p "$D/samples"
for c in "$D"/cycles/*/; do
  n=$(basename "$c"); step=$(( (10#$n + 1) * 16 ))
  out="$D/samples/step_$(printf %04d $step).png"
  [ -f "$out" ] && continue
  ls "$c"/gen_*.png >/dev/null 2>&1 || continue
  python3 bike/sheet.py "$c"/gen_*.png -o "$out" --cols 12 --cell 120 2>/dev/null && echo "$out"
done
