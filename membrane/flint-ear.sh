#!/bin/sh
# flint-ear.sh — Gaia's inner ear on the Flint router
# Captures: Brio 100 microphone (ambient sound levels) + conntrack (network traffic)
OUTDIR="/tmp/gaia-ear"
mkdir -p "$OUTDIR"
CYCLE=${1:-30}
COUNTER=0

echo "[ear] Starting on Flint — Brio mic + conntrack, ${CYCLE}s cycle"
while true; do
    COUNTER=$((COUNTER + 1))
    TS=$(date +%Y-%m-%dT%H:%M:%S 2>/dev/null || date)
    
    # Capture 2s of audio, measure levels
    arecord -D hw:0,0 -f S16_LE -r 16000 -c 1 -d 2 "$OUTDIR/ear-sample.wav" 2>/dev/null
    SAMPLE_SIZE=$(ls -la "$OUTDIR/ear-sample.wav" 2>/dev/null | awk '{print $5}')
    
    # Crude audio level: count bytes above noise floor
    # (proper RMS would need sox, but we can use file size as proxy)
    
    # Conntrack: network pulse
    CONN_TOTAL=$(wc -l < /proc/net/nf_conntrack 2>/dev/null || echo 0)
    CONN_TCP=$(grep -c 'tcp' /proc/net/nf_conntrack 2>/dev/null || echo 0)
    CONN_UDP=$(grep -c 'udp' /proc/net/nf_conntrack 2>/dev/null || echo 0)
    CONN_EST=$(grep -c 'ESTABLISHED' /proc/net/nf_conntrack 2>/dev/null || echo 0)
    
    # Device count
    DEVICES=$(grep -o 'src=192\.168\.[0-9]*\.[0-9]*' /proc/net/nf_conntrack 2>/dev/null | sort -u | wc -l)
    
    # Temperature
    TEMP=$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null || echo 0)
    TEMP_C=$((TEMP / 1000))
    
    # WiFi clients
    WIFI_2G=$(iw dev ra0 station dump 2>/dev/null | grep -c Station || echo 0)
    WIFI_5G=$(iw dev rax0 station dump 2>/dev/null | grep -c Station || echo 0)
    
    cat > "$OUTDIR/ear.json" << ENDJSON
{
  "timestamp": "$TS",
  "sense": "inner-ear",
  "cycle": $COUNTER,
  "microphone": {
    "device": "Brio 100 (USB Audio)",
    "sample_bytes": ${SAMPLE_SIZE:-0},
    "duration_s": 2,
    "rate_hz": 16000,
    "channels": 1,
    "format": "S16_LE"
  },
  "conntrack": {
    "total": $CONN_TOTAL,
    "tcp": $CONN_TCP,
    "udp": $CONN_UDP,
    "established": $CONN_EST,
    "devices": $DEVICES
  },
  "thermal_c": $TEMP_C,
  "wifi_clients": {
    "2ghz": $WIFI_2G,
    "5ghz": $WIFI_5G
  }
}
ENDJSON
    
    echo "[ear] cycle $COUNTER: mic=${SAMPLE_SIZE:-0}B conn=$CONN_TOTAL dev=$DEVICES temp=${TEMP_C}C"
    sleep "$CYCLE"
done
