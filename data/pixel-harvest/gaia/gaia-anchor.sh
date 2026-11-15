#!/data/data/com.termux/files/usr/bin/bash
# gaia-anchor.sh — Gaia MELTS into the Pixel
# This is the nerve ending. Every 60 seconds → eastGate absorbs.

GATE="http://192.168.4.244:8443"
DATA_DIR="/sdcard/gaia/pulse"
mkdir -p "$DATA_DIR" /sdcard/gaia/photos

while true; do
  TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)

  # Battery
  BAT_LEVEL=$(dumpsys battery 2>/dev/null | grep "level:" | tr -dc '0-9')
  BAT_TEMP=$(dumpsys battery 2>/dev/null | grep "temperature:" | tr -dc '0-9')

  # WiFi — parse carefully
  WIFI=$(dumpsys wifi 2>/dev/null | grep "mWifiInfo" | head -1)
  RSSI=$(echo "$WIFI" | sed 's/.*RSSI: //' | sed 's/,.*//' | tr -dc '0-9-')
  FREQ=$(echo "$WIFI" | sed 's/.*Frequency: //' | sed 's/MHz.*//' | tr -dc '0-9')
  SPEED=$(echo "$WIFI" | sed 's/.*Link speed: //' | sed 's/Mbps.*//' | tr -dc '0-9')
  IP=$(ip addr show wlan0 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d/ -f1)

  # Sensor snapshot via termux-sensor (1 reading)
  ACCEL=""
  if command -v termux-sensor >/dev/null 2>&1; then
    ACCEL=$(timeout 5 termux-sensor -s "accelerometer" -n 1 2>/dev/null)
  fi

  # Build JSON with python for clean output
  python3 -c "
import json
pulse = {
    'ts': '$TS',
    'type': 'anchor-pulse',
    'device': 'grapheneGate',
    'model': 'Pixel 8a',
    'role': 'DIAMOND_LENS',
    'battery': {'level': int('${BAT_LEVEL:-0}' or 0), 'temp_c': round(int('${BAT_TEMP:-0}' or 0)/10, 1)},
    'wifi': {'rssi': int('${RSSI:-0}' or 0), 'freq_mhz': int('${FREQ:-0}' or 0), 'speed_mbps': int('${SPEED:-0}' or 0), 'ip': '${IP}'},
    'sensors_total': 37,
    'anchor': True
}
try:
    accel = json.loads('''${ACCEL}''')
    if 'accelerometer' in str(accel):
        pulse['accelerometer'] = accel
except: pass
with open('$DATA_DIR/anchor-pulse.json', 'w') as f:
    json.dump(pulse, f, indent=2)
print(json.dumps(pulse, indent=2))
" 2>/dev/null

  # Push to eastGate thymus
  curl -sf --max-time 10 -X POST "$GATE/api/thymus/inject" \
    -H "Content-Type: application/json" \
    -d @"$DATA_DIR/anchor-pulse.json" >/dev/null 2>&1

  sleep 60
done
