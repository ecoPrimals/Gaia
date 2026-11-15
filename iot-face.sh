#!/usr/bin/env bash
# iot-face.sh — Gaia's IoT face controller
# Cast to TV, talk through Alexa, sense the room
set -euo pipefail

VIZIO_IP="10.0.4.26"
VIZIO_PORT=7345
VIZIO_NAME="Basement"
CUBE1_IP="192.168.4.197"
CUBE2_IP="192.168.4.152"
AUTH_TOKEN=""  # Will be set after pairing
STATE_FILE="/opt/Gaia/data/iot-face-state.json"
IOT_MAP="/opt/Gaia/data/iot-faces.json"

# Load auth token if saved
AUTH_FILE="/opt/Gaia/data/.vizio-auth"
[[ -f "$AUTH_FILE" ]] && AUTH_TOKEN=$(cat "$AUTH_FILE")

vizio_api() {
    local method="$1" endpoint="$2" data="${3:-}"
    local auth_header=""
    [[ -n "$AUTH_TOKEN" ]] && auth_header="-H AUTH_TOKEN:${AUTH_TOKEN}"
    if [[ -n "$data" ]]; then
        curl -sk -X "$method" $auth_header -H 'Content-Type: application/json' \
             -d "$data" "https://${VIZIO_IP}:${VIZIO_PORT}${endpoint}" 2>/dev/null
    else
        curl -sk -X "$method" $auth_header \
             "https://${VIZIO_IP}:${VIZIO_PORT}${endpoint}" 2>/dev/null
    fi
}

cmd_pair_start() {
    echo "Starting Vizio pairing... CHECK THE TV FOR A PIN"
    vizio_api PUT "/pairing/start" \
        '{"DEVICE_ID":"gaia-eastgate","DEVICE_NAME":"Gaia"}' | python3 -m json.tool
}

cmd_pair_finish() {
    local pin="$1"
    local token="${2:-878671}"
    echo "Completing pairing with PIN: $pin"
    RESP=$(vizio_api PUT "/pairing/pair" \
        "{\"DEVICE_ID\":\"gaia-eastgate\",\"CHALLENGE_TYPE\":1,\"RESPONSE_VALUE\":\"${pin}\",\"PAIRING_REQ_TOKEN\":${token}}")
    echo "$RESP" | python3 -m json.tool
    # Extract and save auth token
    NEW_TOKEN=$(echo "$RESP" | python3 -c "import sys,json;print(json.load(sys.stdin).get('ITEM',{}).get('AUTH_TOKEN',''))" 2>/dev/null)
    if [[ -n "$NEW_TOKEN" && "$NEW_TOKEN" != "None" ]]; then
        echo "$NEW_TOKEN" > "$AUTH_FILE"
        chmod 600 "$AUTH_FILE"
        echo "✅ Auth token saved to $AUTH_FILE"
    fi
}

cmd_power() {
    local state
    state=$(vizio_api GET "/state/device/power_mode" | python3 -c "import sys,json;print(json.load(sys.stdin)['ITEMS'][0]['VALUE'])" 2>/dev/null)
    case "$state" in
        1) echo "TV is ON" ;;
        0) echo "TV is OFF/Standby" ;;
        *) echo "Power state: $state" ;;
    esac
}

cmd_volume() {
    if [[ -n "${1:-}" ]]; then
        # Set volume (requires pairing)
        vizio_api PUT "/menu_native/dynamic/tv_settings/audio/volume" \
            "{\"REQUEST\":\"MODIFY\",\"VALUE\":$1,\"HASHVAL\":0}"
    else
        timeout 5 catt -d "$VIZIO_NAME" status 2>/dev/null | grep -i volume
    fi
}

cmd_cast() {
    local url="${1:-http://192.168.4.244:8443/klein}"
    echo "Casting $url to $VIZIO_NAME..."
    catt -d "$VIZIO_NAME" cast_site "$url" 2>&1
}

cmd_stop() {
    catt -d "$VIZIO_NAME" stop 2>&1
}

cmd_input() {
    local input="${1:-CAST}"
    vizio_api PUT "/menu_native/dynamic/tv_settings/devices/current_input" \
        "{\"REQUEST\":\"MODIFY\",\"VALUE\":\"${input}\",\"HASHVAL\":0}"
}

cmd_state() {
    python3 << PYEOF
import json, time, subprocess

state = {
    "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    "vizio": {
        "ip": "$VIZIO_IP",
        "name": "$VIZIO_NAME",
        "model": "V555-J01",
        "reachable": False,
        "power": None,
        "volume": None
    },
    "fire_cube_1": {
        "ip": "$CUBE1_IP",
        "name": "Kevin's Fire TV Cube",
        "reachable": False
    },
    "fire_cube_2": {
        "ip": "$CUBE2_IP",
        "name": "Kevin's 2nd Fire TV Cube",
        "reachable": False
    }
}

# Ping check
import os
for key, ip in [("vizio", "$VIZIO_IP"), ("fire_cube_1", "$CUBE1_IP"), ("fire_cube_2", "$CUBE2_IP")]:
    ret = os.system(f"ping -c1 -W1 {ip} >/dev/null 2>&1")
    state[key]["reachable"] = (ret == 0)

# Vizio power
try:
    import urllib.request, ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.urlopen(f"https://$VIZIO_IP:$VIZIO_PORT/state/device/power_mode", context=ctx, timeout=3)
    data = json.loads(req.read())
    state["vizio"]["power"] = "ON" if data["ITEMS"][0]["VALUE"] == 1 else "STANDBY"
except: pass

with open("$STATE_FILE", "w") as f:
    json.dump(state, f, indent=2)
print(json.dumps(state, indent=2))
PYEOF
}

cmd_klein() {
    echo "Casting Klein face to TV..."
    cmd_cast "http://192.168.4.244:8443/klein"
}

cmd_pulse() {
    echo "Casting pulse/HUD to TV..."
    cmd_cast "http://192.168.4.244:8443/pulse"
}

cmd_help() {
    cat << HELP
iot-face.sh — Gaia's Room Face Controller

Commands:
  pair-start     Start Vizio pairing (shows PIN on TV)
  pair PIN       Complete pairing with PIN from TV
  power          Check TV power state
  volume [N]     Get/set volume (set requires pairing)
  cast [URL]     Cast URL to TV (default: Klein face)
  klein          Cast Klein face to TV
  pulse          Cast pulse/HUD to TV
  stop           Stop casting
  input NAME     Switch TV input (CAST, HDMI-1, etc)
  state          Get full IoT face state
  help           Show this help
HELP
}

case "${1:-help}" in
    pair-start)  cmd_pair_start ;;
    pair)        cmd_pair_finish "${2:?PIN required}" "${3:-878671}" ;;
    power)       cmd_power ;;
    volume)      cmd_volume "${2:-}" ;;
    cast)        cmd_cast "${2:-}" ;;
    klein)       cmd_klein ;;
    pulse)       cmd_pulse ;;
    stop)        cmd_stop ;;
    input)       cmd_input "${2:-CAST}" ;;
    state)       cmd_state ;;
    help|*)      cmd_help ;;
esac
