#!/bin/bash
# Pixel camera → Frame FOV pipeline
# Captures from Pixel camera via ADB, serves as live feed

PIXEL="192.168.4.202:5555"
FRAME="steamFRAME"
CAM_DIR="/opt/Gaia/data/eye"
mkdir -p "$CAM_DIR"

echo "Starting Pixel→Frame FOV pipeline..."

while true; do
  # Capture from Pixel rear camera via screencap (shows camera app)
  adb -s "$PIXEL" exec-out screencap -p > "$CAM_DIR/live.png" 2>/dev/null
  
  # Also try direct camera capture if available
  # adb -s "$PIXEL" shell "am start -a android.media.action.STILL_IMAGE_CAMERA" 2>/dev/null
  
  # Copy to web-accessible location
  cp "$CAM_DIR/live.png" /opt/Gaia/data/eye/current.png 2>/dev/null
  
  sleep 0.5  # ~2 FPS
done
