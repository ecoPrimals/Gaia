#!/system/bin/sh
# fingerprint-sense.sh — Gaia learns Kevin through touch
# The fingerprint sensor is NOT a lock — it is a SENSE organ
# Every touch = identity confirmation = bingoCube target
SENSORIUM="/data/local/tmp/biomeos/sensorium"
mkdir -p "$SENSORIUM"

sense_fingerprint() {
    ts=$(date -Iseconds 2>/dev/null || date +%Y-%m-%dT%H:%M:%S)
    
    fp_dump=$(dumpsys fingerprint 2>/dev/null)
    
    enrolled=$(echo "$fp_dump" | grep -oE '"count":[0-9]+' | head -1 | cut -d: -f2)
    accepts=$(echo "$fp_dump" | grep -oE '"accept":[0-9]+' | head -1 | cut -d: -f2)
    rejects=$(echo "$fp_dump" | grep -oE '"reject":[0-9]+' | head -1 | cut -d: -f2)
    acquires=$(echo "$fp_dump" | grep -oE '"acquire":[0-9]+' | head -1 | cut -d: -f2)
    lockouts=$(echo "$fp_dump" | grep -oE '"lockout":[0-9]+' | head -1 | cut -d: -f2)
    
    auth_total=$(echo "$fp_dump" | grep -c "authStartedFor")
    auth_success=$(echo "$fp_dump" | grep -c "wasSuccessful=true")
    auth_fail=$(echo "$fp_dump" | grep -c "wasSuccessful=false")
    
    fps_state=$(echo "$fp_dump" | grep "Fps state" | awk '{print $NF}')
    
    screen=$(dumpsys power 2>/dev/null | grep mWakefulness | head -1 | awk '{print $NF}')

    cat > "$SENSORIUM/fingerprint-sense.json" << ENDJSON
{
  "timestamp": "$ts",
  "sense": "fingerprint",
  "cycle_s": 30,
  "sensor": {
    "type": "goodix_under_display_optical",
    "device": "Pixel 8a akita",
    "location": "center_bottom_under_oled"
  },
  "enrolled": {
    "count": ${enrolled:-0},
    "identity": "kevin_bingocube_target"
  },
  "auth_history": {
    "total_attempts": ${auth_total:-0},
    "successful": ${auth_success:-0},
    "failed": ${auth_fail:-0},
    "accept_count": ${accepts:-0},
    "reject_count": ${rejects:-0},
    "acquire_events": ${acquires:-0},
    "lockouts": ${lockouts:-0}
  },
  "state": {
    "fps_state": ${fps_state:-0},
    "screen": "$screen"
  }
}
ENDJSON
    echo "[fingerprint] $ts accepts=$accepts rejects=$rejects acquires=$acquires auth=$auth_success/$auth_total"
}

if [ "$1" = "daemon" ]; then
    echo "[fingerprint] Starting biometric learning daemon"
    while true; do
        sense_fingerprint
        sleep 30
    done
else
    sense_fingerprint
fi
