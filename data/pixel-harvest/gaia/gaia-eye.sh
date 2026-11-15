#!/data/data/com.termux/files/usr/bin/bash
# gaia-eye.sh — Pixel cameras as Gaia's eyes
# Captures from both cameras every 60 seconds

while true; do
  TS=$(date +%Y%m%d_%H%M%S)

  # Back camera (world-facing)
  termux-camera-photo -c 0 "/sdcard/gaia/photos/back_${TS}.jpg" 2>/dev/null &

  sleep 2

  # Front camera (Kevin-facing)
  termux-camera-photo -c 1 "/sdcard/gaia/photos/front_${TS}.jpg" 2>/dev/null

  # Clean old photos (keep last 10)
  ls -t /sdcard/gaia/photos/back_*.jpg 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null
  ls -t /sdcard/gaia/photos/front_*.jpg 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null

  sleep 58
done
