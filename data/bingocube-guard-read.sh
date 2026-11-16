#!/usr/bin/env bash
# bingoCube Steam Guard Reader
# Captures the Steam Guard code from Pixel via ADB screencap
# Uses the known screen layout: code is 5 chars in center of screen
set -euo pipefail

TMPDIR="${TMPDIR:-/tmp}"
IMG="$TMPDIR/steam-guard-capture.png"

echo "[bingoCube] Reading Steam Guard from Pixel..."

# Ensure Steam Guard is open
adb shell am start -n com.valvesoftware.android.steam.community/.MainActivity 2>/dev/null || true
sleep 0.5

# Navigate to Steam Guard (tap shield icon — 5th nav tab)
# Bottom nav: Store, News, Steam Guard (shield), Notifications, Menu
# Shield icon is at roughly x=507, y=940 in portrait mode
adb shell input tap 507 940 2>/dev/null
sleep 1

# Capture screen
adb exec-out screencap -p > "$IMG"
echo "[bingoCube] Screenshot: $IMG"

# Try OCR via tesseract if available
if command -v tesseract &>/dev/null; then
    # Crop center where code appears (roughly 100-350 x 450-650 in portrait)
    CODE=$(tesseract "$IMG" - 2>/dev/null | grep -oE '[A-Z0-9]{5}' | head -1)
    if [ -n "$CODE" ]; then
        echo "[bingoCube] ✓ Steam Guard code: $CODE"
        echo "$CODE"
        exit 0
    fi
fi

# Fallback: manual read
echo "[bingoCube] OCR not available or failed"
echo "[bingoCube] Check screenshot at $IMG"
echo "[bingoCube] The code is the 5 large characters in the center of the screen"
echo "[bingoCube] Current account: gaia / tamisonecoprimal"
