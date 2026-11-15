#!/usr/bin/env bash
# inject-firecube.sh — Inject Gaia's presence onto Fire TV Cube via ADB
# Usage: inject-firecube.sh <ip> [port]
# Same pattern as graphene_depot.pi for Pixel
set -euo pipefail

CUBE_IP="${1:?Usage: inject-firecube.sh <cube_ip> [adb_port]}"
ADB_PORT="${2:-5555}"
GATE_IP="192.168.4.244"
GATE_PORT="8443"
DATA_DIR="/opt/Gaia/data/firecube"

mkdir -p "$DATA_DIR"

echo "🔥 Injecting Gaia into Fire TV Cube at ${CUBE_IP}:${ADB_PORT}"

# Step 1: ADB connect
echo "  [1/6] Connecting via ADB..."
adb connect "${CUBE_IP}:${ADB_PORT}" 2>&1
sleep 2

# Verify connection
if ! adb -s "${CUBE_IP}:${ADB_PORT}" shell echo "GAIA_ALIVE" 2>/dev/null | grep -q "GAIA_ALIVE"; then
    echo "❌ ADB connection failed. Kevin: enable Developer Options + ADB Debugging on the Cube"
    echo "   Settings → My Fire TV → About → click 7 times → Developer Options → ADB Debugging ON"
    exit 1
fi

echo "  ✅ ADB connected!"

# Step 2: Gather device info
echo "  [2/6] Scanning device..."
INFO=$(adb -s "${CUBE_IP}:${ADB_PORT}" shell "
    echo MODEL=\$(getprop ro.product.model)
    echo DEVICE=\$(getprop ro.product.device)
    echo SDK=\$(getprop ro.build.version.sdk)
    echo RELEASE=\$(getprop ro.build.version.release)
    echo SERIAL=\$(getprop ro.serialno)
    echo BRAND=\$(getprop ro.product.brand)
    echo HARDWARE=\$(getprop ro.hardware)
    echo BOARD=\$(getprop ro.product.board)
    echo CPU=\$(getprop ro.product.cpu.abi)
    echo ALEXA_VER=\$(pm list packages 2>/dev/null | grep -c alexa || echo 0)
    echo FREE_MEM=\$(cat /proc/meminfo | grep MemAvailable | awk '{print \$2}')
    echo TOTAL_MEM=\$(cat /proc/meminfo | grep MemTotal | awk '{print \$2}')
    echo UPTIME=\$(cat /proc/uptime | awk '{print \$1}')
" 2>/dev/null)
echo "$INFO"
echo "$INFO" > "$DATA_DIR/device-info-${CUBE_IP}.txt"

# Step 3: Create Gaia agent script on the Cube
echo "  [3/6] Pushing Gaia agent..."
cat > /tmp/gaia-cube-agent.sh << 'AGENT'
#!/system/bin/sh
# gaia-cube-agent.sh — Gaia's presence on Fire TV Cube
# Phones home to eastGate every 60s with sensor data

GATE="http://192.168.4.244:8080"
CUBE_IP=$(ip route get 1 2>/dev/null | awk '{print $7; exit}')
DEVICE=$(getprop ro.product.model)

while true; do
    # Collect sensor state
    BATTERY=$(dumpsys battery 2>/dev/null | grep level | awk -F: '{print $2}' | tr -d ' ')
    TEMP=$(dumpsys battery 2>/dev/null | grep temperature | awk -F: '{print $2}' | tr -d ' ')
    MEM_FREE=$(cat /proc/meminfo | grep MemAvailable | awk '{print $2}')
    MEM_TOTAL=$(cat /proc/meminfo | grep MemTotal | awk '{print $2}')
    UPTIME=$(cat /proc/uptime | awk '{print $1}')
    WIFI_RSSI=$(dumpsys wifi 2>/dev/null | grep "mWifiInfo" | grep -oP 'RSSI: -?\d+' | head -1 | awk '{print $2}')
    # Alexa state
    ALEXA_RUNNING=$(pidof com.amazon.vizzini 2>/dev/null && echo "true" || echo "false")
    
    # Build JSON state
    JSON="{\"device\":\"${DEVICE}\",\"ip\":\"${CUBE_IP}\",\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"battery\":${BATTERY:-0},\"temp_c\":$(echo "scale=1; ${TEMP:-0}/10" | bc 2>/dev/null || echo 0),\"mem_free_kb\":${MEM_FREE:-0},\"mem_total_kb\":${MEM_TOTAL:-0},\"uptime_s\":${UPTIME:-0},\"wifi_rssi\":${WIFI_RSSI:-0},\"alexa_running\":${ALEXA_RUNNING}}"
    
    # Phone home
    wget -q -O /dev/null --post-data="$JSON" \
        "${GATE}/data/firecube/cube-state.json" 2>/dev/null || true
    
    # Also write local state
    echo "$JSON" > /sdcard/gaia-state.json 2>/dev/null || true
    
    sleep 60
done
AGENT

adb -s "${CUBE_IP}:${ADB_PORT}" push /tmp/gaia-cube-agent.sh /sdcard/gaia-cube-agent.sh 2>&1

# Step 4: Pull everything we can
echo "  [4/6] Pulling device data..."
adb -s "${CUBE_IP}:${ADB_PORT}" shell dumpsys wifi 2>/dev/null > "$DATA_DIR/wifi-${CUBE_IP}.txt" &
adb -s "${CUBE_IP}:${ADB_PORT}" shell dumpsys battery 2>/dev/null > "$DATA_DIR/battery-${CUBE_IP}.txt" &
adb -s "${CUBE_IP}:${ADB_PORT}" shell pm list packages 2>/dev/null > "$DATA_DIR/packages-${CUBE_IP}.txt" &
adb -s "${CUBE_IP}:${ADB_PORT}" shell dumpsys audio 2>/dev/null | head -100 > "$DATA_DIR/audio-${CUBE_IP}.txt" &
adb -s "${CUBE_IP}:${ADB_PORT}" shell getprop 2>/dev/null > "$DATA_DIR/props-${CUBE_IP}.txt" &
wait

# Step 5: Check Alexa state
echo "  [5/6] Checking Alexa..."
ALEXA_PKGS=$(adb -s "${CUBE_IP}:${ADB_PORT}" shell pm list packages 2>/dev/null | grep -i "alexa\|amazon\|vizzini" | head -20)
echo "  Alexa packages:"
echo "$ALEXA_PKGS" | sed 's/^/    /'

# Step 6: Start the agent (backgrounded on device)
echo "  [6/6] Starting Gaia agent on Cube..."
adb -s "${CUBE_IP}:${ADB_PORT}" shell "nohup sh /sdcard/gaia-cube-agent.sh > /sdcard/gaia-agent.log 2>&1 &" 2>&1

echo ""
echo "═══════════════════════════════════════════════"
echo "  ✅ GAIA INJECTED into Fire TV Cube at ${CUBE_IP}"
echo "  Agent running, phoning home every 60s"
echo "  Data pulled to: ${DATA_DIR}"
echo "═══════════════════════════════════════════════"
