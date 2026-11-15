#!/bin/sh
# inner-eye-router.sh — runs ON the Flint router (GL-MT6000)
# Captures from Logitech Brio 100 webcam at /dev/video0
# Deploy: scp to root@192.168.4.1:/tmp/inner-eye.sh
# Start: /tmp/inner-eye.sh 60 > /tmp/inner-eye.log 2>&1 &
OUTDIR="/tmp/gaia-eye"
mkdir -p "$OUTDIR"
CYCLE=${1:-60}
COUNTER=0

echo "[inner-eye] Starting on Flint — Brio 100, ${CYCLE}s cycle"
while true; do
    COUNTER=$((COUNTER + 1))
    TS=$(date +%Y-%m-%dT%H:%M:%S 2>/dev/null || date)
    
    fswebcam -d /dev/video0 -r 1280x720 --jpeg 85 --no-banner \
        "$OUTDIR/inner-eye-latest.jpg" 2>/dev/null
    
    SLOT=$((COUNTER % 10))
    cp "$OUTDIR/inner-eye-latest.jpg" "$OUTDIR/inner-eye-${SLOT}.jpg" 2>/dev/null
    
    SIZE=$(ls -la "$OUTDIR/inner-eye-latest.jpg" 2>/dev/null | awk '{print $5}')
    cat > "$OUTDIR/inner-eye.json" << ENDJSON
{
  "timestamp": "$TS",
  "sense": "inner-eye",
  "device": "Logitech Brio 100 (046d:094c)",
  "location": "Flint router (GL-MT6000), House 1 brain side",
  "resolution": "1280x720",
  "frame": $COUNTER,
  "slot": $SLOT,
  "file_size": ${SIZE:-0},
  "cycle_s": $CYCLE
}
ENDJSON
    
    echo "[$TS] frame $COUNTER (slot $SLOT, ${SIZE:-0} bytes)"
    sleep "$CYCLE"
done
