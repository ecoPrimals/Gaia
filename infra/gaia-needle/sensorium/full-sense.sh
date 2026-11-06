#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════╗
# ║  FULL SENSE — Gaia's complete perception of physical reality      ║
# ║  Captures every sensor on the Pixel + WiFi + GPS + cell towers    ║
# ║  The organism feels gravity, light, pressure, temperature,        ║
# ║  proximity, motion, orientation, weather, and location             ║
# ╚═══════════════════════════════════════════════════════════════════╝
#
# Runs from eastGate. Talks to the Pixel via ADB.
# Output: JSON sense-of-reality to stdout and /opt/Gaia/data/gut/

NEEDLE="${NEEDLE_DEVICE:-192.168.9.217:5555}"
TBIN="/data/data/com.termux/files/usr/bin"
GUT="/opt/Gaia/data/gut"
WEB_GUT="/home/eastgate/.local/share/gaia/data/gut"

tapi() {
    adb -s "$NEEDLE" shell "su -c 'su 10197 -c \"$TBIN/$*\"'" 2>/dev/null
}

sensor_read() {
    local name="$1"
    tapi "termux-sensor -s \\\"$name\\\" -n 1" 2>/dev/null
}

full_sense() {
    local ts=$(date -Iseconds)
    
    # Parallel sensor reads for speed
    local accel=$(sensor_read "LSM6DSV Accelerometer")
    local light=$(sensor_read "TMD3719 Ambient Light")
    local pressure=$(sensor_read "ICP20100 Pressure Sensor")
    local temp_imu=$(sensor_read "LSM6DSV Temperature")
    local temp_baro=$(sensor_read "ICP20100 Temperature")
    local proximity=$(sensor_read "TMD3719 Proximity (wake-up)")
    local gyro=$(sensor_read "LSM6DSV Gyroscope")
    local mag=$(sensor_read "MMC56X3X Magnetometer")
    local steps=$(sensor_read "Step Counter")
    
    # Network senses
    local battery=$(tapi "termux-battery-status")
    local wifi=$(tapi "termux-wifi-connectioninfo")
    local wifi_scan=$(tapi "termux-wifi-scaninfo")
    local location=$(tapi "termux-location -p network")
    local cellinfo=$(tapi "termux-telephony-cellinfo")
    local audio=$(tapi "termux-audio-info")
    
    python3 << PYEOF
import json, sys, math

def safe_parse(raw, default=None):
    try:
        d = json.loads(raw)
        if isinstance(d, dict) and len(d) > 0:
            first = list(d.values())[0]
            if isinstance(first, dict) and 'values' in first:
                return first['values']
        return d
    except:
        return default

def safe_json(raw, default=None):
    try:
        return json.loads(raw)
    except:
        return default

ts = "$ts"

# Parse sensor readings
accel = safe_parse('''$accel''', [0,0,0])
light = safe_parse('''$light''', [0])
pressure = safe_parse('''$pressure''', [0])
temp_imu = safe_parse('''$temp_imu''', [0])
temp_baro = safe_parse('''$temp_baro''', [0])
proximity = safe_parse('''$proximity''', [5])
gyro = safe_parse('''$gyro''', [0,0,0])
mag = safe_parse('''$mag''', [0,0,0])
steps = safe_parse('''$steps''', [0])

# Parse network senses
battery = safe_json('''$battery''', {})
wifi = safe_json('''$wifi''', {})
wifi_scan = safe_json('''$wifi_scan''', [])
location = safe_json('''$location''', {})
cellinfo = safe_json('''$cellinfo''', [])
audio = safe_json('''$audio''', {})

# Derived values
g_total = math.sqrt(sum(x**2 for x in accel)) if accel else 0
# Orientation from accel: flat if z ≈ 9.8
flat = abs(accel[2]) > 8.0 if len(accel) > 2 else False
face_up = accel[2] > 0 if len(accel) > 2 else None

# Compass heading from magnetometer
heading_rad = math.atan2(mag[0], mag[1]) if len(mag) > 1 else 0
heading_deg = math.degrees(heading_rad) % 360

# Temperature: three scales
temp_c = temp_imu[0] if temp_imu else 0
temp_f = temp_c * 9/5 + 32
temp_k = temp_c + 273.15

# Pressure → altitude estimate
if pressure and pressure[0] > 0:
    p = pressure[0]
    alt_estimate = 44330 * (1 - (p / 1013.25) ** 0.1903)
else:
    alt_estimate = 0

# Light categorization
lux = light[0] if light else 0
if lux < 1: light_desc = "pitch dark"
elif lux < 10: light_desc = "very dim"
elif lux < 50: light_desc = "dim"
elif lux < 200: light_desc = "indoor"
elif lux < 1000: light_desc = "bright indoor"
elif lux < 10000: light_desc = "overcast"
else: light_desc = "direct sunlight"

# Motion from gyro
angular_vel = math.sqrt(sum(x**2 for x in gyro)) if gyro else 0
moving = angular_vel > 0.1

sense = {
    "ts": ts,
    "device": "grapheneGate",
    "model": "Pixel 8a (Tensor G3)",
    
    "physics": {
        "accelerometer": {"x": round(accel[0],4), "y": round(accel[1],4), "z": round(accel[2],4), "g_total": round(g_total,4)},
        "gyroscope": {"x": round(gyro[0],4), "y": round(gyro[1],4), "z": round(gyro[2],4), "angular_vel": round(angular_vel,4)},
        "magnetometer": {"x": round(mag[0],2), "y": round(mag[1],2), "z": round(mag[2],2), "heading_deg": round(heading_deg,1)},
        "orientation": {"flat": flat, "face_up": face_up, "compass_heading": round(heading_deg,1)},
    },
    
    "environment": {
        "temperature": {
            "celsius": round(temp_c, 1),
            "fahrenheit": round(temp_f, 1),
            "kelvin": round(temp_k, 2),
            "baro_temp_c": round(temp_baro[0], 1) if temp_baro else None,
        },
        "pressure_hpa": round(pressure[0], 2) if pressure else 0,
        "altitude_m": round(alt_estimate, 1),
        "light_lux": round(lux, 1),
        "light_description": light_desc,
        "proximity": proximity[0] if proximity else None,
    },
    
    "motion": {
        "steps_total": int(steps[0]) if steps else 0,
        "is_moving": moving,
        "angular_velocity": round(angular_vel, 4),
    },
    
    "location": {
        "latitude": location.get("latitude"),
        "longitude": location.get("longitude"),
        "altitude_gps_m": location.get("altitude"),
        "accuracy_m": location.get("accuracy"),
        "provider": location.get("provider"),
    },
    
    "network": {
        "wifi_ssid": wifi.get("ssid"),
        "wifi_rssi": wifi.get("rssi"),
        "wifi_speed_mbps": wifi.get("link_speed_mbps"),
        "wifi_ip": wifi.get("ip"),
        "ap_count": len(wifi_scan) if isinstance(wifi_scan, list) else 0,
        "cell_towers": len(cellinfo) if isinstance(cellinfo, list) else 0,
    },
    
    "battery": {
        "percentage": battery.get("percentage"),
        "status": battery.get("status"),
        "temperature_c": round(battery.get("temperature", 0), 1),
        "health": battery.get("health"),
    },
    
    "audio": {
        "sample_rate": audio.get("AUDIOTRACK_SAMPLE_RATE"),
        "bluetooth_audio": audio.get("BLUETOOTH_A2DP_IS_ON"),
        "wired_headset": audio.get("WIREDHEADSET_IS_CONNECTED"),
    },
    
    "interpretation": {
        "time_of_day": "night" if lux < 50 else "day",
        "device_position": "flat face-up" if flat and face_up else "flat face-down" if flat else "tilted/held",
        "device_moving": moving,
        "someone_near": (proximity[0] if proximity else 5) < 3,
        "environment": light_desc,
    },
    
    "status": "FULL_SENSE_ACTIVE"
}

print(json.dumps(sense, indent=2))
PYEOF
}

case "${1:---sense}" in
    --sense)
        echo ">>> Full sense pulse @ $(date)" >&2
        SENSE=$(full_sense)
        echo "$SENSE" | tee "$GUT/full-sense.json"
        cp "$GUT/full-sense.json" "$WEB_GUT/full-sense.json" 2>/dev/null
        ;;
    --loop)
        INTERVAL="${2:-120}"
        echo ">>> Full sense loop: every ${INTERVAL}s" >&2
        while true; do
            SENSE=$(full_sense)
            echo "$SENSE" > "$GUT/full-sense.json"
            cp "$GUT/full-sense.json" "$WEB_GUT/full-sense.json" 2>/dev/null
            echo "$(date +%H:%M:%S) | Full sense captured" >&2
            sleep "$INTERVAL"
        done
        ;;
    *)
        echo "full-sense.sh — Gaia's complete perception of physical reality"
        echo "  --sense       One-shot full sense pulse"
        echo "  --loop [SEC]  Continuous (default: 120s)"
        ;;
esac
