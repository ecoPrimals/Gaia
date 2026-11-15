#!/data/data/com.termux/files/usr/bin/bash
# ============================================================================
# termux-sensor-bridge.sh — runs INSIDE Termux to read masked sensors
# ============================================================================
# GrapheneOS masks sensor values from adb shell.
# Termux:API can read them. This script bridges the gap.
# Drops data into /data/local/tmp/biomeos/sensorium/ which adb can read.
# ============================================================================

OUT=/data/local/tmp/biomeos/sensorium/raw-sensors.json
CYCLE=${1:-60}

while true; do
    # Read all sensors in one shot (1 reading each)
    SENSORS=$(termux-sensor -s all -n 1 2>/dev/null)
    
    if [ -n "$SENSORS" ]; then
        echo "$SENSORS" > $OUT
    else
        # Fallback: read specific sensors
        echo '{' > $OUT
        
        # Accelerometer
        ACC=$(termux-sensor -s "LSM6DSV Accelerometer" -n 1 2>/dev/null | head -20)
        echo "\"accelerometer\": $ACC," >> $OUT
        
        # Light
        LUX=$(termux-sensor -s "TMD3719 Ambient Light" -n 1 2>/dev/null | head -10)
        echo "\"light\": $LUX," >> $OUT
        
        # Pressure
        PRESS=$(termux-sensor -s "ICP20100 Pressure" -n 1 2>/dev/null | head -10)
        echo "\"pressure\": $PRESS," >> $OUT
        
        # Proximity
        PROX=$(termux-sensor -s "TMD3719 Proximity" -n 1 2>/dev/null | head -10)
        echo "\"proximity\": $PROX," >> $OUT
        
        echo "\"timestamp\": \"$(date -Iseconds)\"" >> $OUT
        echo '}' >> $OUT
    fi
    
    # Also do a camera capture if possible
    termux-camera-photo -c 0 /data/local/tmp/biomeos/petaltongue/eyes/right-eye.jpg 2>/dev/null &
    sleep 2
    termux-camera-photo -c 1 /data/local/tmp/biomeos/petaltongue/eyes/left-eye.jpg 2>/dev/null &
    
    sleep $CYCLE
done
