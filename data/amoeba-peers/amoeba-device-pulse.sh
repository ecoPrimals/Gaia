#!/bin/bash
# amoeba-device-pulse.sh — Monitor all network devices in the organism
# Runs on eastGate, outputs device-pulse.json for the HUD
# Part of the Amoeba mesh — extends visibility to routers, switches, APs

set -euo pipefail

OUTPUT="/opt/Gaia/data/amoeba-peers/device-pulse.json"
TIMESTAMP=$(date -u +%FT%TZ)

check_ping() {
  local ip=$1 name=$2
  local ms=$(ping -c 1 -W 1 "$ip" 2>/dev/null | grep -oP 'time=\K[0-9.]+' || echo "")
  if [ -n "$ms" ]; then
    echo "{\"name\":\"$name\",\"ip\":\"$ip\",\"ping_ms\":$ms,\"alive\":true}"
  else
    echo "{\"name\":\"$name\",\"ip\":\"$ip\",\"ping_ms\":null,\"alive\":false}"
  fi
}

check_tcp() {
  local ip=$1 port=$2
  timeout 2 bash -c "echo >/dev/tcp/$ip/$port" 2>/dev/null && echo "true" || echo "false"
}

check_http() {
  local url=$1
  curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 "$url" 2>/dev/null || echo "000"
}

check_adb() {
  local ip=$1
  local result=$(adb connect "$ip:5555" 2>/dev/null | grep -c "connected" || echo "0")
  adb disconnect "$ip:5555" >/dev/null 2>&1
  [ "$result" -gt 0 ] && echo "true" || echo "false"
}

cat > "$OUTPUT" <<HEADER
{
  "timestamp": "$TIMESTAMP",
  "pulse_type": "amoeba-device-pulse",
  "devices": {
HEADER

# === HOUSE 1 — Brain Side ===

# Router
ROUTER_PING=$(check_ping "192.168.4.1" "router")
ROUTER_HTTP=$(check_http "http://192.168.4.250/")
cat >> "$OUTPUT" <<DEVICE
    "router": {
      "ip": "192.168.4.1",
      "name": "GL-MT6000",
      "location": "House 1",
      "role": "Main Router",
      $(echo "$ROUTER_PING" | sed 's/^{//;s/}$//'),
      "http_admin": "$ROUTER_HTTP",
      "ssh": true
    },
DEVICE

# MikroTik
MIKROTIK_PING=$(check_ping "192.168.4.2" "mikrotik")
MIKROTIK_HTTP=$(check_http "http://192.168.4.2/")
cat >> "$OUTPUT" <<DEVICE
    "mikrotik": {
      "ip": "192.168.4.2",
      "name": "MikroTik L2 Switch",
      "location": "House 1",
      "role": "L2 Backbone",
      $(echo "$MIKROTIK_PING" | sed 's/^{//;s/}$//'),
      "http_admin": "$MIKROTIK_HTTP"
    },
DEVICE

# sporeGate
SPORE_PING=$(check_ping "192.168.4.3" "sporeGate")
SPORE_SSH=$(check_tcp "192.168.4.3" 22)
cat >> "$OUTPUT" <<DEVICE
    "sporeGate": {
      "ip": "192.168.4.3",
      "name": "sporeGate",
      "location": "House 1",
      "role": "Forge — Pop!_OS amalgam",
      $(echo "$SPORE_PING" | sed 's/^{//;s/}$//'),
      "ssh": $SPORE_SSH
    },
DEVICE

# northGate
NORTH_PING=$(check_ping "192.168.4.147" "northGate")
cat >> "$OUTPUT" <<DEVICE
    "northGate": {
      "ip": "192.168.4.147",
      "name": "northGate",
      "location": "House 1",
      "role": "Heart — RTX 5090, 63 models",
      $(echo "$NORTH_PING" | sed 's/^{//;s/}$//'),
      "gpu": "RTX 5090"
    },
DEVICE

# ironGate
IRON_PING=$(check_ping "192.168.4.237" "ironGate")
IRON_SSH=$(check_tcp "192.168.4.237" 22)
cat >> "$OUTPUT" <<DEVICE
    "ironGate": {
      "ip": "192.168.4.237",
      "name": "ironGate",
      "location": "House 1",
      "role": "Forge 2 — RTX 5070",
      $(echo "$IRON_PING" | sed 's/^{//;s/}$//'),
      "ssh": $IRON_SSH,
      "gpu": "RTX 5070"
    },
DEVICE

# === HOUSE 2 — South Pole ===

# JetStream
JET_PING=$(check_ping "192.168.4.111" "jetstream")
JET_HTTP=$(check_http "http://192.168.4.111/")
cat >> "$OUTPUT" <<DEVICE
    "jetstream": {
      "ip": "192.168.4.111",
      "name": "TP-Link JetStream",
      "location": "House 2",
      "role": "10G Fiber Bridge",
      $(echo "$JET_PING" | sed 's/^{//;s/}$//'),
      "http_admin": "$JET_HTTP",
      "omada_discovery": true
    },
DEVICE

# Omada AP
OMADA_AP=$(check_ping "192.168.4.198" "omada_ap")
cat >> "$OUTPUT" <<DEVICE
    "omada_ap": {
      "ip": "192.168.4.198",
      "name": "Omada AP",
      "location": "House 2",
      "role": "WiFi AP — ApertureScience + GAIA",
      $(echo "$OMADA_AP" | sed 's/^{//;s/}$//'),
      "omada_discovery": true,
      "bssids": {"5g": "b6:c3:31:c9:88:ec", "2g": "ae:44:09:b0:32:69"}
    },
DEVICE

# blueGate
BLUE_HTTP=$(check_http "http://192.168.4.100:3141/")
BLUE_SSH=$(check_tcp "192.168.4.210" 22)
cat >> "$OUTPUT" <<DEVICE
    "blueGate": {
      "ip_wifi": "192.168.4.100",
      "ip_wired": "192.168.4.210",
      "name": "blueGate",
      "location": "House 2",
      "role": "Gaia IDE — 12 tissue models",
      "alive": true,
      "gaia_ide": "$BLUE_HTTP",
      "ssh_wired": $BLUE_SSH,
      "tissue_models": 12
    },
DEVICE

# Pixel (at House 2)
PIXEL_ADB=$(check_adb "192.168.4.249")
cat >> "$OUTPUT" <<DEVICE
    "pixel": {
      "ip": "192.168.4.249",
      "name": "grapheneGate (Pixel 8a)",
      "location": "House 2 (mobile)",
      "role": "Diamond Lens — 37 sensors",
      "adb_wireless": $PIXEL_ADB,
      "wifi_ssid": "ApertureScience"
    }
DEVICE

# Close JSON
cat >> "$OUTPUT" <<FOOTER
  },
  "summary": {
    "house1_alive": 0,
    "house2_alive": 0,
    "total_devices": 0,
    "gpu_fleet": ["RTX 5090 (northGate)", "RTX 5070 (ironGate)", "RTX 4070 (eastGate)", "RTX 3070 (swiftGate, booting)", "M4 (graftGate)", "Mali-G715 (Pixel)"],
    "tissue_models": 12,
    "amoeba_nodes": ["eastGate", "sporeGate", "northGate", "blueGate", "Pixel"]
  }
}
FOOTER

echo "Pulse written to $OUTPUT at $TIMESTAMP"
