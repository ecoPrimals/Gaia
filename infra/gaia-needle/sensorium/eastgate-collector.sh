#!/bin/bash
# ╔════════════════════════════════════════════════════════════════╗
# ║  GAIA SENSORIUM — eastGate Collector                           ║
# ║  Pulls sensor data from the Pixel and feeds it into the gut    ║
# ║  Runs on eastGate, pulls via wireless ADB                      ║
# ╚════════════════════════════════════════════════════════════════╝
#
# Usage:
#   ./eastgate-collector.sh                      # one-shot pulse
#   ./eastgate-collector.sh --loop 30            # pulse every 30s
#   ./eastgate-collector.sh --locate             # where is the pixel?
#   ./eastgate-collector.sh --listen 5           # record 5s audio
#   ./eastgate-collector.sh --scan               # full environment scan

NEEDLE="${NEEDLE_DEVICE:-192.168.9.217:5555}"
SU="/debug_ramdisk/su"
DATA_DIR="/opt/Gaia/data/gut"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$DATA_DIR"

# ─── Ensure ADB connection ───
ensure_connected() {
    adb -s "$NEEDLE" shell echo "ok" >/dev/null 2>&1 || {
        echo ">>> Reconnecting to needle at $NEEDLE..."
        adb connect "$NEEDLE" >/dev/null 2>&1
        sleep 1
        adb -s "$NEEDLE" shell echo "ok" >/dev/null 2>&1 || {
            echo "✗ Cannot reach needle"
            return 1
        }
    }
    return 0
}

# ─── Pull sensor pulse ───
pull_pulse() {
    ensure_connected || return 1

    PULSE=$(adb -s "$NEEDLE" shell "$SU -c 'sh /data/local/tmp/sensorium/sense-pulse.sh'" 2>/dev/null)

    if [ -n "$PULSE" ]; then
        echo "$PULSE" > "$DATA_DIR/graphenegate-sensors.json"
        echo "$PULSE" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    wifi = d.get('wifi', {})
    batt = d.get('battery', {})
    env = d.get('environment', {})
    scan = d.get('wifi_scan', [])
    print(f'  Battery: {batt.get(\"percent\", \"?\")}% ({batt.get(\"status\", \"?\")})')
    print(f'  WiFi: {wifi.get(\"ssid\", \"?\")} @ {wifi.get(\"rssi\", \"?\")}dBm')
    print(f'  Nearby APs: {len(scan)}')
    print(f'  Light: {env.get(\"light_lux\", \"?\")} lux')
    print(f'  CPU: {env.get(\"cpu_temp_c\", \"?\")}°C')
except:
    print('  (raw data saved)')
" 2>/dev/null
        return 0
    else
        echo "✗ Empty pulse"
        return 1
    fi
}

# ─── Pull WiFi scan for localization ───
pull_wifi_scan() {
    ensure_connected || return 1

    echo ">>> Pulling WiFi scan..."
    SCAN=$(adb -s "$NEEDLE" shell "$SU -c 'cmd wifi list-scan-results'" 2>/dev/null)

    echo "$SCAN" | python3 -c "
import sys, json

lines = sys.stdin.readlines()[1:]  # skip header
aps = []
for line in lines:
    parts = line.split()
    if len(parts) >= 5:
        aps.append({
            'bssid': parts[0],
            'freq': int(parts[1]),
            'rssi': int(parts[2]),
            'ssid': parts[4] if len(parts) > 4 else ''
        })

# Sort by signal strength
aps.sort(key=lambda x: x['rssi'], reverse=True)

result = {
    'ts': '$(date -Iseconds)',
    'device': 'grapheneGate',
    'ap_count': len(aps),
    'access_points': aps
}

json.dump(result, open('$DATA_DIR/graphenegate-wifi-scan.json', 'w'), indent=2)

# Print summary
for ap in aps[:10]:
    bars = '█' * max(0, (ap['rssi'] + 100) // 10)
    print(f'  {ap[\"rssi\"]:4d}dBm {bars:10s} {ap[\"ssid\"]:20s} {ap[\"bssid\"]}  {ap[\"freq\"]}MHz')

print(f'  Total: {len(aps)} APs visible')
" 2>/dev/null
}

# ─── Localize ───
do_locate() {
    ensure_connected || return 1
    echo ">>> Running localization..."
    adb -s "$NEEDLE" shell "$SU -c 'sh /data/local/tmp/sensorium/localize.sh locate'" 2>&1

    # Pull result
    adb -s "$NEEDLE" pull /sdcard/gaia/localization/current-location.json "$DATA_DIR/graphenegate-location.json" 2>/dev/null
}

# ─── Calibrate room ───
do_calibrate() {
    ROOM="${1:?Specify room name}"
    ensure_connected || return 1
    echo ">>> Calibrating room: $ROOM"
    adb -s "$NEEDLE" shell "$SU -c 'sh /data/local/tmp/sensorium/localize.sh calibrate \"$ROOM\"'" 2>&1
}

# ─── Listen (ear) ───
do_listen() {
    DURATION="${1:-5}"
    ensure_connected || return 1
    echo ">>> Listening for ${DURATION}s..."
    adb -s "$NEEDLE" shell "$SU -c 'sh /data/local/tmp/sensorium/ear.sh listen $DURATION'" 2>&1

    # Pull latest audio file
    LATEST=$(adb -s "$NEEDLE" shell "ls -t /sdcard/gaia/audio/ 2>/dev/null | head -1" | tr -d '\r')
    if [ -n "$LATEST" ]; then
        mkdir -p "$DATA_DIR/audio"
        adb -s "$NEEDLE" pull "/sdcard/gaia/audio/$LATEST" "$DATA_DIR/audio/$LATEST" 2>/dev/null
        echo "✓ Audio pulled to $DATA_DIR/audio/$LATEST"
    fi
}

# ─── Full environment scan ───
do_scan() {
    echo "╔═══════════════════════════════════╗"
    echo "║  GAIA SENSORIUM — Full Scan        ║"
    echo "╚═══════════════════════════════════╝"
    echo ""

    echo ">>> Sensor Pulse"
    pull_pulse
    echo ""

    echo ">>> WiFi Environment"
    pull_wifi_scan
    echo ""

    echo ">>> Location"
    do_locate
    echo ""

    echo ">>> Screenshot"
    ensure_connected && {
        adb -s "$NEEDLE" shell "$SU -c 'screencap -p /sdcard/gaia/photos/latest-screen.png'" 2>/dev/null
        adb -s "$NEEDLE" pull /sdcard/gaia/photos/latest-screen.png "$DATA_DIR/graphenegate-screen.png" 2>/dev/null
        echo "  ✓ Screen captured"
    }
    echo ""

    echo "╔═══════════════════════════════════╗"
    echo "║  Scan complete — data in $DATA_DIR"
    echo "╚═══════════════════════════════════╝"
}

# ─── Main ───
case "${1:---pulse}" in
    --pulse)
        echo ">>> Sensor pulse @ $(date)"
        pull_pulse
        ;;
    --loop)
        INTERVAL="${2:-30}"
        echo ">>> Sensor loop every ${INTERVAL}s (Ctrl+C to stop)"
        while true; do
            echo "--- $(date) ---"
            pull_pulse
            sleep "$INTERVAL"
        done
        ;;
    --wifi)
        pull_wifi_scan
        ;;
    --locate)
        do_locate
        ;;
    --calibrate)
        do_calibrate "$2"
        ;;
    --listen)
        do_listen "$2"
        ;;
    --scan)
        do_scan
        ;;
    --help|-h)
        echo "Gaia Sensorium — eastGate Collector"
        echo ""
        echo "Usage: eastgate-collector.sh [command]"
        echo ""
        echo "Commands:"
        echo "  --pulse              One sensor reading (default)"
        echo "  --loop SECONDS       Continuous polling"
        echo "  --wifi               WiFi environment scan"
        echo "  --locate             Determine Pixel room"
        echo "  --calibrate ROOM     Record WiFi fingerprint for room"
        echo "  --listen SECONDS     Record audio"
        echo "  --scan               Full environment scan"
        echo ""
        echo "Data lands in: $DATA_DIR"
        ;;
esac
