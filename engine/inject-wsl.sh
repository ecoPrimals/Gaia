#!/bin/bash
# BENCH ONLY. Not pilot. Not local inject.
# One clean observation. Compare. Stop.
set -euo pipefail
SRC="/mnt/c/Users/mokke/Desktop/Gaia3"
HOME_OS="${HOME}/biomeOS/bench"
LOG="$HOME_OS/compare.log"
mkdir -p "$HOME_OS"
{
  echo "trial=$(date -Iseconds)"
  echo "host=$(hostname)"
  echo "kernel=$(uname -srm)"
  echo "node=$(command -v node || echo NONE)"
  echo "scale=bench"
  echo "pilot=deny"
} > "$LOG"
cp -f "$SRC/bench-scale.json" "$HOME_OS/" 2>/dev/null || true
cp -f "$SRC/golgi-generations.json" "$HOME_OS/" 2>/dev/null || true
echo "BENCH: $HOME_OS"
cat "$LOG"
if ! command -v node >/dev/null 2>&1; then
  echo "FAIL: no node. Reagent missing. Do not start organs."
  exit 0
fi
echo "node present — still bench. No organs. No inject."
