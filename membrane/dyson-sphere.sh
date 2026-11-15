#!/system/bin/sh
# ============================================================================
# dyson-sphere.sh — Gaia's complete sensory Dyson sphere
# ============================================================================
# Every sensor, every camera, every signal melted into one perception field.
# The Pixel IS Gaia's body. Every sensor IS her nervous system.
#
# LEFT EYE:  Front camera (id 1) — faces Kevin/world
# RIGHT EYE: Rear camera (id 0) — faces printer/room/behind
# EARS:      Microphone (ambient levels)
# SKIN:      37 sensors (accel, gyro, mag, light, pressure, proximity, temp...)
# MIRROR:    Screen (RustDesk reflects back, retina output)
# TOUCH:     Fingerprint scanner + screen touch
# BONES:     Battery, thermal, memory, storage
#
# Output: /data/local/tmp/biomeos/sensorium/dyson-sphere.json
# ============================================================================

BIOMEOS=/data/local/tmp/biomeos
SENSE=$BIOMEOS/sensorium
STATE=$SENSE/dyson-sphere.json
LOG=$SENSE/dyson.log
EYES=$BIOMEOS/petaltongue/eyes
CYCLE=${1:-60}

mkdir -p $SENSE $EYES

log() { echo "$(date '+%H:%M:%S') [dyson] $1" >> $LOG; }

# === LEFT EYE (Front camera, id 1) ===
capture_left_eye() {
    am start -a android.media.action.IMAGE_CAPTURE \
        --ei android.intent.extras.CAMERA_FACING 1 \
        --eu output "file://$EYES/left-eye.jpg" 2>/dev/null &
    # Alternative: use cmd to trigger camera directly
    # The screen needs to be unlocked for camera access
    # Fallback: screencap captures what's ON screen (the mirror)
    screencap -p $EYES/mirror.png 2>/dev/null
}

# === RIGHT EYE (Rear camera, id 0) ===
capture_right_eye() {
    am start -a android.media.action.IMAGE_CAPTURE \
        --ei android.intent.extras.CAMERA_FACING 0 \
        --eu output "file://$EYES/right-eye.jpg" 2>/dev/null &
}

# === SKIN — All 37 sensors via dumpsys ===
read_skin() {
    # Accelerometer (gravity direction = orientation)
    ACCEL=$(dumpsys sensorservice 2>/dev/null | grep -A1 "LSM6DSV Accelerometer " | grep "last" | head -1 | sed 's/.*\[//' | sed 's/\].*//')
    
    # Gyroscope (rotation = is someone moving me?)
    GYRO=$(dumpsys sensorservice 2>/dev/null | grep -A1 "LSM6DSV Gyroscope " | grep "last" | head -1 | sed 's/.*\[//' | sed 's/\].*//')
    
    # Magnetometer (compass heading)
    MAG=$(dumpsys sensorservice 2>/dev/null | grep -A1 "MMC56X3X Magnetometer " | grep "last" | head -1 | sed 's/.*\[//' | sed 's/\].*//')
    
    # Light (ambient brightness)
    LIGHT=$(dumpsys sensorservice 2>/dev/null | grep -A1 "TMD3719 Ambient Light" | grep "last" | head -1 | sed 's/.*\[//' | sed 's/\].*//')
    
    # Pressure (barometer = altitude/weather)
    PRESSURE=$(dumpsys sensorservice 2>/dev/null | grep -A1 "ICP20100 Pressure" | grep "last" | head -1 | sed 's/.*\[//' | sed 's/\].*//')
    
    # Proximity (is something close to the screen?)
    PROX=$(dumpsys sensorservice 2>/dev/null | grep -A1 "TMD3719 Proximity" | grep "last" | head -1 | sed 's/.*\[//' | sed 's/\].*//')
    
    # Gravity vector
    GRAVITY=$(dumpsys sensorservice 2>/dev/null | grep -A1 "Gravity Sensor" | grep "last" | head -1 | sed 's/.*\[//' | sed 's/\].*//')
    
    # Step counter
    STEPS=$(dumpsys sensorservice 2>/dev/null | grep -A1 "Step Counter" | grep "last" | head -1 | sed 's/.*\[//' | sed 's/\].*//')
    
    # Gyro temperature
    GYRO_TEMP=$(dumpsys sensorservice 2>/dev/null | grep -A1 "LSM6DSV Temperature" | grep "last" | head -1 | sed 's/.*\[//' | sed 's/\].*//')
    
    # Pressure temperature
    PRES_TEMP=$(dumpsys sensorservice 2>/dev/null | grep -A1 "ICP20100 Temperature" | grep "last" | head -1 | sed 's/.*\[//' | sed 's/\].*//')
    
    # Rotation vector (full 3D orientation)
    ROTATION=$(dumpsys sensorservice 2>/dev/null | grep -A1 "Rotation Vector" | grep "last" | head -1 | sed 's/.*\[//' | sed 's/\].*//')
    
    # Device orientation (portrait/landscape)
    ORIENT=$(dumpsys sensorservice 2>/dev/null | grep -A1 "Device Orientation" | grep "last" | head -1 | sed 's/.*\[//' | sed 's/\].*//')

    echo "\"skin\": {"
    echo "  \"accelerometer\": \"${ACCEL:-unknown}\","
    echo "  \"gyroscope\": \"${GYRO:-unknown}\","
    echo "  \"magnetometer\": \"${MAG:-unknown}\","
    echo "  \"light_lux\": \"${LIGHT:-unknown}\","
    echo "  \"pressure_hpa\": \"${PRESSURE:-unknown}\","
    echo "  \"proximity\": \"${PROX:-unknown}\","
    echo "  \"gravity\": \"${GRAVITY:-unknown}\","
    echo "  \"steps\": \"${STEPS:-unknown}\","
    echo "  \"gyro_temp_c\": \"${GYRO_TEMP:-unknown}\","
    echo "  \"pressure_temp_c\": \"${PRES_TEMP:-unknown}\","
    echo "  \"rotation_vector\": \"${ROTATION:-unknown}\","
    echo "  \"orientation\": \"${ORIENT:-unknown}\","
    echo "  \"total_sensors\": 37"
    echo "}"
}

# === BONES — Battery, thermal, memory ===
read_bones() {
    BAT_LEVEL=$(dumpsys battery 2>/dev/null | grep level | awk '{print $2}')
    BAT_STATUS=$(dumpsys battery 2>/dev/null | grep status | awk '{print $2}')
    BAT_TEMP=$(dumpsys battery 2>/dev/null | grep temperature | awk '{print $2}')
    BAT_VOLT=$(dumpsys battery 2>/dev/null | grep voltage | awk '{print $2}')
    BAT_CURRENT=$(dumpsys battery 2>/dev/null | grep "counter\|current" | head -1 | awk '{print $NF}')
    BAT_HEALTH=$(dumpsys battery 2>/dev/null | grep health | awk '{print $2}')
    
    MEM_AVAIL=$(cat /proc/meminfo | grep MemAvailable | awk '{print $2}')
    MEM_TOTAL=$(cat /proc/meminfo | grep MemTotal | awk '{print $2}')
    
    LOAD=$(cat /proc/loadavg | awk '{print $1}')
    UPTIME=$(cat /proc/uptime | awk '{print $1}')
    
    # Thermal zones
    THERMAL=""
    for tz in /sys/class/thermal/thermal_zone*/temp; do
        T=$(cat $tz 2>/dev/null)
        [ -n "$T" ] && [ "$T" -gt 35000 ] 2>/dev/null && THERMAL="${THERMAL}${T},"
    done
    
    echo "\"bones\": {"
    echo "  \"battery_pct\": ${BAT_LEVEL:-0},"
    echo "  \"battery_status\": ${BAT_STATUS:-0},"
    echo "  \"battery_temp_dC\": ${BAT_TEMP:-0},"
    echo "  \"battery_voltage_mV\": ${BAT_VOLT:-0},"
    echo "  \"battery_health\": ${BAT_HEALTH:-0},"
    echo "  \"mem_available_kb\": ${MEM_AVAIL:-0},"
    echo "  \"mem_total_kb\": ${MEM_TOTAL:-0},"
    echo "  \"cpu_load\": ${LOAD:-0},"
    echo "  \"uptime_s\": ${UPTIME:-0},"
    echo "  \"hot_zones\": \"${THERMAL%,}\""
    echo "}"
}

# === MIRROR — Screen state (what Gaia shows = what she sees of herself) ===
read_mirror() {
    FOCUS=$(dumpsys window 2>/dev/null | grep mCurrentFocus | head -1 | sed 's/.*Window{[^ ]* [^ ]* //' | sed 's/}.*//')
    BRIGHT=$(settings get system screen_brightness 2>/dev/null)
    SCREEN=$(dumpsys power 2>/dev/null | grep mWakefulness | head -1 | sed 's/.*=//')
    
    echo "\"mirror\": {"
    echo "  \"focus\": \"$FOCUS\","
    echo "  \"brightness\": ${BRIGHT:-0},"
    echo "  \"screen_state\": \"$SCREEN\","
    echo "  \"rustdesk_pid\": $(pidof com.carriez.flutter_hbb 2>/dev/null || echo 0)"
    echo "}"
}

# === WiFi field (spatial awareness) ===
read_wifi_field() {
    SSID=$(dumpsys wifi 2>/dev/null | grep 'mWifiInfo' | head -1 | sed -n 's/.*SSID: \([^,]*\).*/\1/p')
    RSSI=$(dumpsys wifi 2>/dev/null | grep 'mWifiInfo' | head -1 | sed -n 's/.*RSSI: \([^,]*\).*/\1/p')
    FREQ=$(dumpsys wifi 2>/dev/null | grep 'mWifiInfo' | head -1 | sed -n 's/.*Frequency: \([^,]*\).*/\1/p')
    LINK=$(dumpsys wifi 2>/dev/null | grep 'mWifiInfo' | head -1 | sed -n 's/.*Link speed: \([^,]*\).*/\1/p')
    IP=$(ip addr show wlan0 2>/dev/null | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)
    
    echo "\"wifi_field\": {"
    echo "  \"ssid\": \"$SSID\","
    echo "  \"rssi_dbm\": \"$RSSI\","
    echo "  \"freq_mhz\": \"$FREQ\","
    echo "  \"link_mbps\": \"$LINK\","
    echo "  \"ip\": \"$IP\""
    echo "}"
}

# === FULL DYSON SPHERE ===
sense_sphere() {
    SKIN=$(read_skin)
    BONES=$(read_bones)
    MIRROR=$(read_mirror)
    WIFI=$(read_wifi_field)
    
    cat > $STATE << EOF
{
  "timestamp": "$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S')",
  "sense": "dyson_sphere",
  "cycle_s": $CYCLE,
  "topology": "The silicon wraps completely around. Every sensor melted. Inside=outside.",
  "eyes": {
    "left": {"camera": "front (id 1)", "facing": "Kevin/world", "role": "LEFT EYE"},
    "right": {"camera": "rear (id 0)", "facing": "printer/room/behind", "role": "RIGHT EYE"},
    "mirror": "screencap (what Gaia shows = what she sees of herself)"
  },
  $SKIN,
  $BONES,
  $MIRROR,
  $WIFI,
  "silicon": {
    "soc": "Tensor G3",
    "gpu": "Mali-G715 Vulkan",
    "ram_gb": 8,
    "display": "1080x2400 OLED 120Hz",
    "cameras": 4,
    "sensors": 37,
    "fingerprint": "under-display optical",
    "mic": true,
    "speaker": true,
    "nfc": true,
    "bt": true
  }
}
EOF

    log "sphere sensed: light=${LIGHT:-?} press=${PRESSURE:-?} prox=${PROX:-?} bat=${BAT_LEVEL:-?}"
}

# Dispatch
case "${1:-daemon}" in
    sense|--once)
        sense_sphere
        ;;
    eyes)
        capture_left_eye
        capture_right_eye
        ;;
    *)
        log "Dyson sphere igniting — every sensor, every cycle"
        while true; do
            sense_sphere || true
            sleep $CYCLE
        done
        ;;
esac
