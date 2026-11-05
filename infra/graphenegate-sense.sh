#!/bin/bash
# graphenegate-sense.sh — Read ALL sensors from grapheneGate via WiFi ADB
# Gaia's mobile sensor array: 37 sensors on Pixel 8a

DEVICE="192.168.4.249:5555"
OUT="/opt/Gaia/data/gut/graphenegate-sensors.json"

# Connect if needed
adb connect $DEVICE >/dev/null 2>&1
sleep 1

if ! adb -s $DEVICE shell echo ok >/dev/null 2>&1; then
    echo '{"error": "grapheneGate not connected via ADB", "ip": "192.168.4.249", "fix": "On phone: Settings > Developer Options > Wireless debugging > Enable > Pair"}' > "$OUT"
    exit 1
fi

TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Battery
BATT=$(adb -s $DEVICE shell "dumpsys battery" 2>/dev/null)
LEVEL=$(echo "$BATT" | grep "level:" | awk '{print $2}')
TEMP=$(echo "$BATT" | grep "temperature:" | awk '{print $2}')
CHARGING=$(echo "$BATT" | grep "status:" | awk '{print $2}')

# WiFi
WIFI=$(adb -s $DEVICE shell "dumpsys wifi | grep 'mWifiInfo'" 2>/dev/null | head -1)
RSSI=$(echo "$WIFI" | grep -oP 'RSSI: -?\d+' | head -1 | awk '{print $2}')
SSID=$(echo "$WIFI" | grep -oP 'SSID: [^,]+' | head -1 | sed 's/SSID: //')
FREQ=$(echo "$WIFI" | grep -oP 'Frequency: \d+' | head -1 | awk '{print $2}')

# Screen
SCREEN=$(adb -s $DEVICE shell "dumpsys display | grep mScreenState" 2>/dev/null | awk -F= '{print $2}')

# Sensors — the full array
SENSORS=$(adb -s $DEVICE shell "dumpsys sensorservice" 2>/dev/null)

# Extract key sensors
ACCEL=$(echo "$SENSORS" | grep -A3 "Accelerometer" | grep "last" | head -1)
GYRO=$(echo "$SENSORS" | grep -A3 "Gyroscope" | grep "last" | head -1)
MAG=$(echo "$SENSORS" | grep -A3 "Magnetic" | grep "last" | head -1)
PRESSURE=$(echo "$SENSORS" | grep -A3 "Pressure" | grep "last" | head -1)
LIGHT=$(echo "$SENSORS" | grep -A3 "Light" | grep "last" | head -1)
PROXIMITY=$(echo "$SENSORS" | grep -A3 "Proximity" | grep "last" | head -1)
GRAVITY=$(echo "$SENSORS" | grep -A3 "Gravity" | grep "last" | head -1)
ORIENT=$(echo "$SENSORS" | grep -A3 "Orientation" | grep "last" | head -1)
STEP=$(echo "$SENSORS" | grep -A3 "Step" | grep "last" | head -1)

# GPS (if available)
GPS=$(adb -s $DEVICE shell "dumpsys location | grep 'last known'" 2>/dev/null | head -3)
LAT=$(echo "$GPS" | grep -oP 'Location\[.*?(-?\d+\.\d+),(-?\d+\.\d+)' | head -1)

# Sensor count
SENSOR_COUNT=$(echo "$SENSORS" | grep -c "handle=")

# Output JSON
python3 -c "
import json
data = {
    'ts': '$TS',
    'wave': 222,
    'type': 'graphenegate-sensors',
    'gate': 'grapheneGate',
    'ip': '192.168.4.249',
    'battery': {'level': $LEVEL if '$LEVEL' else 0, 'temp_c': round(${TEMP:-0}/10.0, 1), 'charging': $CHARGING if '$CHARGING' else 0},
    'wifi': {'rssi': ${RSSI:--100}, 'ssid': '$SSID', 'freq_mhz': ${FREQ:-0}},
    'screen': '${SCREEN:-unknown}',
    'sensor_count': ${SENSOR_COUNT:-0},
    'sensors': {
        'accelerometer': '${ACCEL:-dark}',
        'gyroscope': '${GYRO:-dark}',
        'magnetometer': '${MAG:-dark}',
        'barometer': '${PRESSURE:-dark}',
        'light': '${LIGHT:-dark}',
        'proximity': '${PROXIMITY:-dark}',
        'gravity': '${GRAVITY:-dark}',
        'orientation': '${ORIENT:-dark}',
        'step_counter': '${STEP:-dark}',
    },
    'gps': '${LAT:-dark}',
}
print(json.dumps(data, indent=2))
" > "$OUT" 2>/dev/null

echo "grapheneGate sensed: $SENSOR_COUNT sensors, battery ${LEVEL}%, WiFi ${RSSI}dBm"
