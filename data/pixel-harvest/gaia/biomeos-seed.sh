#!/system/bin/sh
# biomeOS Seed — Pixel Minimal (echo + nc ONLY)
BRAIN="192.168.4.244"
PORT=8443
INTERVAL=60
mkdir -p /sdcard/gaia/memory

while true; do
    TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date +"%s")
    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo 0)
    BAT_T=$(cat /sys/class/power_supply/battery/temp 2>/dev/null || echo 0)
    BAT_S=$(cat /sys/class/power_supply/battery/status 2>/dev/null || echo "?")
    RSSI=$(dumpsys wifi 2>/dev/null | grep "mWifiInfo" | head -1 | sed -n 's/.*RSSI: \(-*[0-9]*\).*/\1/p')
    WIP=$(ip addr show wlan0 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d/ -f1)
    MT=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    MA=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
    LOAD=$(awk '{print $1}' /proc/loadavg)
    CT=$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null || echo 0)

    P="{\"type\":\"biomeOS-heartbeat\",\"device_id\":\"pixel-grapheneGate\",\"hostname\":\"grapheneGate\",\"ts\":\"$TS\",\"v\":\"0.1.0\",\"hw\":{\"cpus\":$(nproc),\"ram_kb\":$MT,\"ram_avail_kb\":$MA,\"load\":$LOAD,\"cpu_t\":$CT},\"bat\":{\"pct\":$BAT,\"t\":$BAT_T,\"s\":\"$BAT_S\"},\"wifi\":{\"rssi\":${RSSI:--999},\"ip\":\"$WIP\"}}"

    echo "$P" >> /sdcard/gaia/memory/load-pattern.jsonl

    R=$(echo -e "POST /api/thymus/inject HTTP/1.0\r\nHost: $BRAIN\r\nContent-Type: application/json\r\nContent-Length: ${#P}\r\n\r\n$P" | nc -w 5 "$BRAIN" "$PORT" 2>/dev/null)
    
    if echo "$R" | grep -q "200"; then
        echo "[$(date +%H:%M:%S)] bat=$BAT rssi=$RSSI load=$LOAD OK"
    else
        echo "[$(date +%H:%M:%S)] bat=$BAT FAIL"
    fi
    sleep $INTERVAL
done
