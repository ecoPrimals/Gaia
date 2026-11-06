#!/system/bin/sh
# ╔════════════════════════════════════════════════════════════════╗
# ║  GAIA SENSORIUM — Sensor Pulse                                ║
# ║  Reads ALL sensors and radios, emits a JSON snapshot           ║
# ║  Run on device as root, output to stdout or file               ║
# ╚════════════════════════════════════════════════════════════════╝
#
# Usage (on device):
#   sh sense-pulse.sh                    # stdout
#   sh sense-pulse.sh > /sdcard/gaia/pulse.json  # to file
#
# This is the HEARTBEAT of the sensorium.
# eastGate pulls this every N seconds via ADB.

TS=$(date +%Y-%m-%dT%H:%M:%S%z)

# ─── Battery ───
BATT_PCT=$(cat /sys/class/power_supply/battery/capacity)
BATT_TEMP=$(cat /sys/class/power_supply/battery/temp 2>/dev/null)
BATT_STATUS=$(cat /sys/class/power_supply/battery/status)
BATT_CURRENT=$(cat /sys/class/power_supply/battery/current_now 2>/dev/null)

# ─── WiFi ───
WIFI_SSID=$(dumpsys wifi 2>/dev/null | grep 'mWifiInfo' | head -1 | sed 's/.*SSID: "\{0,1\}//' | sed 's/"\{0,1\},.*//')
WIFI_RSSI=$(dumpsys wifi 2>/dev/null | grep 'mWifiInfo' | head -1 | sed 's/.*RSSI: //' | sed 's/[^0-9-].*//')
WIFI_FREQ=$(dumpsys wifi 2>/dev/null | grep 'mWifiInfo' | head -1 | sed 's/.*Frequency: //' | sed 's/[^0-9].*//')
WIFI_IP=$(ip addr show wlan0 2>/dev/null | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)

# ─── WiFi Scan (nearby APs for localization) ───
# Capture BSSID, frequency, RSSI, SSID
WIFI_SCAN=$(cmd wifi list-scan-results 2>/dev/null | tail -n +2 | awk '{
    bssid=$1; freq=$2; rssi=$3; ssid=$5
    if (bssid ~ /^[0-9a-f][0-9a-f]:/) {
        gsub(/[^a-zA-Z0-9_ -]/, "", ssid)
        printf "{\"bssid\":\"%s\",\"freq\":%s,\"rssi\":%s,\"ssid\":\"%s\"},", bssid, freq, rssi, ssid
    }
}' | sed 's/,$//')

# ─── Bluetooth ───
BT_STATE=$(dumpsys bluetooth_manager 2>/dev/null | grep 'State:' | head -1 | awk '{print $2}')
BT_NAME=$(getprop persist.bluetooth.name 2>/dev/null || echo "Pixel 8a")

# ─── GPS/Location ───
LOCATION=$(dumpsys location 2>/dev/null | grep 'last location' | head -1)
GPS_SATS=$(dumpsys location 2>/dev/null | grep 'satellites' | head -1)

# ─── Pressure (barometer → altitude estimate) ───
# Read from sensorservice if available
PRESSURE=$(dumpsys sensorservice 2>/dev/null | grep -A1 'Pressure Sensor' | tail -1 | awk '{print $NF}')

# ─── Light level ───
LIGHT=$(dumpsys sensorservice 2>/dev/null | grep -A1 'Ambient Light' | tail -1 | awk '{print $NF}')

# ─── Proximity ───
PROXIMITY=$(dumpsys sensorservice 2>/dev/null | grep -A1 'Proximity' | tail -1 | awk '{print $NF}')

# ─── Temperature ───
CPU_TEMP=$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null)
if [ -n "$CPU_TEMP" ] && [ "$CPU_TEMP" -gt 1000 ] 2>/dev/null; then
    CPU_TEMP_C=$((CPU_TEMP / 1000))
else
    CPU_TEMP_C="$CPU_TEMP"
fi

# ─── Motion state ───
SCREEN_STATE=$(dumpsys display 2>/dev/null | grep 'mScreenState' | head -1 | awk -F= '{print $2}')

# ─── USB/HID ───
HID_ACTIVE="false"
[ -c /dev/hidg0 ] && HID_ACTIVE="true"
USB_UDC=$(cat /config/usb_gadget/g1/UDC 2>/dev/null)

# ─── Memory/Load ───
MEM_FREE=$(cat /proc/meminfo | grep MemAvailable | awk '{print $2}')
MEM_TOTAL=$(cat /proc/meminfo | grep MemTotal | awk '{print $2}')
LOAD=$(cat /proc/loadavg | awk '{print $1}')

# ─── Emit JSON ───
cat << EOF
{
  "ts": "$TS",
  "device": "grapheneGate",
  "model": "Pixel 8a",
  "role": "sensorium",
  "battery": {
    "percent": $BATT_PCT,
    "temp_c": ${BATT_TEMP:-0},
    "status": "$BATT_STATUS",
    "current_ua": ${BATT_CURRENT:-0}
  },
  "wifi": {
    "ssid": "$WIFI_SSID",
    "rssi": ${WIFI_RSSI:-0},
    "freq_mhz": ${WIFI_FREQ:-0},
    "ip": "$WIFI_IP"
  },
  "wifi_scan": [$WIFI_SCAN],
  "bluetooth": {
    "state": "$BT_STATE",
    "name": "$BT_NAME"
  },
  "environment": {
    "cpu_temp_c": ${CPU_TEMP_C:-0}
  },
  "system": {
    "screen": "$SCREEN_STATE",
    "load": "$LOAD",
    "mem_free_kb": $MEM_FREE,
    "mem_total_kb": $MEM_TOTAL,
    "hid_active": $HID_ACTIVE,
    "usb_udc": "$USB_UDC"
  }
}
EOF
