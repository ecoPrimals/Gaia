#!/usr/bin/env bash
# face-cast.sh — Cast Gaia's face to the TV based on context
# Usage: face-cast.sh [page] — defaults to tv-face
set -euo pipefail

GATE="http://192.168.4.244:8443"
TV_NAME="Basement"

PAGE="${1:-tv-face}"

case "$PAGE" in
    tv|tv-face|dashboard)  URL="$GATE/tv-face" ;;
    klein|triad)           URL="$GATE/klein" ;;
    pulse|heartbeat)       URL="$GATE/pulse" ;;
    eye|eyes|iris)         URL="$GATE/eye" ;;
    apollo|mission)        URL="$GATE/apollo" ;;
    outer|outer-face)      URL="$GATE/outer-face" ;;
    deck|spacedock)        URL="$GATE/spacedock" ;;
    sense|left-eye)        URL="$GATE/sense" ;;
    glados|beacon)         URL="$GATE/glados" ;;
    off|stop)              catt -d "$TV_NAME" stop 2>&1; exit 0 ;;
    http*)                 URL="$PAGE" ;;
    *)                     URL="$GATE/$PAGE" ;;
esac

echo "📺 Casting $URL → $TV_NAME"
catt -d "$TV_NAME" cast_site "$URL" 2>&1
