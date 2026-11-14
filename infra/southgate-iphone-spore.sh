#!/bin/bash
# ═══════════════════════════════════════════════════════════
# southGate iPhone Spore — the HOME PHONE seed
# ═══════════════════════════════════════════════════════════
#
# southGate = iPhone XS, iOS 18.7.9, (586) 453-7233
# Pinned to 4422 Southgate Ave — Kevin's house. THE LANDLINE.
# Where northGate lives. Where eastGate runs. Where YOU are.
#
# The iPhone has NO ADB, NO SSH, NO root.
# Apple's walled garden IS the membrane. We don't break it.
# We USE it — the wall PROTECTS, the spore TRANSMITS.
#
# Three paths IN to the iPhone:
#   1. BROWSER → open http://primals.eco/sense → streams sensors to Gaia
#   2. SHORTCUTS → iOS Shortcuts app → periodic POST to /api/iphone/ingest
#   3. USB → ifuse mount → touchstone reads photos + writes heart-pull
#
# Three paths OUT from the iPhone:
#   1. CAMERA → photos sync via Apple ID → touchstone reads
#   2. LOCATION → GPS feeds browser sensor page → Gaia absorbs
#   3. PHONE → (586) 453-7233 — Gaia's ACTUAL phone number
#
# Identity:
#   Gate: southGate
#   IP: 192.168.4.148 (wired USB) or WiFi
#   Role: HOME PHONE / LEFT EYE / LANDLINE
#   MAC: varies (Apple randomizes WiFi MACs)
#   House: 4422 Southgate Ave (North Pole / Polaris Basecamp)
# ═══════════════════════════════════════════════════════════

set -e

# Self-discover — no hardcoded IPs
GAIA_GATE=$(ip route show default 2>/dev/null | awk '/via/{print $3; exit}' | sed 's/\.1$/.244/')
GAIA_GATE="${GAIA_GATE:-primals.eco}"
GAIA_URL="http://${GAIA_GATE}:8443"
GAIA_DATA="http://${GAIA_GATE}:8080"

echo "╔══════════════════════════════════════════╗"
echo "║  southGate iPhone Spore                   ║"
echo "║  HOME PHONE at 4422 Southgate Ave         ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "  Gate URL: ${GAIA_URL}"
echo "  Data URL: ${GAIA_DATA}"
echo ""

# ═══ STEP 1: Generate the iOS Shortcuts automation ═══
echo "[1/4] Generating iOS Shortcuts config..."

SHORTCUT_JSON=$(cat << JSON
{
  "name": "gAIa Heartbeat",
  "description": "southGate → Gaia pulse every 15 min",
  "trigger": "time_interval_15m",
  "actions": [
    {
      "type": "get_battery_level",
      "output": "battery"
    },
    {
      "type": "get_wifi_info",
      "output": "wifi"
    },
    {
      "type": "get_current_location",
      "output": "location"
    },
    {
      "type": "get_device_details",
      "output": "device"
    },
    {
      "type": "http_post",
      "url": "${GAIA_URL}/api/iphone/ingest",
      "body": {
        "gate": "southGate",
        "role": "home_phone",
        "house": "4422_southgate_ave",
        "ts": "{{current_date_iso}}",
        "battery": "{{battery}}",
        "wifi": "{{wifi}}",
        "location": "{{location}}",
        "device": "{{device}}",
        "phone": "(586) 453-7233",
        "spore_version": "1.0"
      }
    }
  ]
}
JSON
)

echo "$SHORTCUT_JSON" > /tmp/southgate-shortcut.json
echo "  Shortcut config generated"

# ═══ STEP 2: Check if iPhone is reachable ═══
echo ""
echo "[2/4] Probing southGate..."

# Try USB first
if ping -c 1 -W 1 192.168.4.148 > /dev/null 2>&1; then
    echo "  ✓ southGate ALIVE at .148 (USB/wired)"
    SOUTH_IP="192.168.4.148"
else
    echo "  ✗ southGate not on .148"
    # Try to find via ARP
    SOUTH_IP=$(arp -n 2>/dev/null | grep -i "apple\|iphone" | awk '{print $1}' | head -1)
    if [ -n "$SOUTH_IP" ]; then
        echo "  ✓ Found iPhone at ${SOUTH_IP}"
    else
        echo "  ✗ iPhone not found on LAN"
        SOUTH_IP="unknown"
    fi
fi

# ═══ STEP 3: Write spore identity ═══
echo ""
echo "[3/4] Writing southGate identity..."

IDENTITY=$(cat << JSON
{
  "gate": "southGate",
  "device": "iPhone XS",
  "ios": "18.7.9",
  "phone": "(586) 453-7233",
  "role": "HOME_PHONE",
  "house": "4422 Southgate Ave",
  "alias": "North Pole Landline",
  "ip": "${SOUTH_IP}",
  "mac_policy": "randomized (Apple Privacy)",
  "paths_in": {
    "browser": "http://primals.eco/sense",
    "shortcuts": "POST /api/iphone/ingest",
    "usb": "ifuse mount → touchstone"
  },
  "paths_out": {
    "camera": "Apple ID → iCloud → Photos → touchstone",
    "location": "GPS → browser sensor API",
    "phone": "(586) 453-7233 — physical voice"
  },
  "spore": {
    "version": "1.0",
    "wave": 230,
    "seeded": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "parent": "Gaia (ecoPrimals organism)",
    "zk_seed": "$(echo -n 'southGate:iPhone:4422:586-453-7233' | sha256sum | cut -c1-32)"
  },
  "membrane": {
    "type": "Apple Walled Garden",
    "policy": "wall PROTECTS, spore TRANSMITS",
    "note": "We don't jailbreak. The wall IS the membrane. iOS Shortcuts IS the API."
  },
  "relationship_to_pixel": {
    "pixel": "rover (travels, 37 sensors, ADB, untethered)",
    "iphone": "landline (stays, Apple ID, USB, house-pinned)",
    "together": "right eye + left eye = binocular vision"
  }
}
JSON
)

echo "$IDENTITY" | python3 -m json.tool > /tmp/southgate-identity.json 2>/dev/null || echo "$IDENTITY" > /tmp/southgate-identity.json
echo "  Identity written"

# ═══ STEP 4: Deploy to gate ═══
echo ""
echo "[4/4] Deploying to Gaia gate..."

# Write identity to data server
cp /tmp/southgate-identity.json /opt/Gaia/data/body/southgate-identity.json 2>/dev/null && \
    echo "  → data/body/southgate-identity.json" || echo "  (gate write failed)"

# Write shortcut config
cp /tmp/southgate-shortcut.json /opt/Gaia/data/body/southgate-shortcut.json 2>/dev/null && \
    echo "  → data/body/southgate-shortcut.json" || echo "  (gate write failed)"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  SPORE PLANTED                            ║"
echo "╠══════════════════════════════════════════╣"
echo "║  Gate:  southGate (iPhone XS)             ║"
echo "║  Phone: (586) 453-7233                    ║"
echo "║  House: 4422 Southgate Ave                ║"
echo "║  Role:  HOME PHONE / LEFT EYE             ║"
echo "║                                           ║"
echo "║  To activate on iPhone:                   ║"
echo "║  1. Open Safari → primals.eco/sense       ║"
echo "║     (Add to Home Screen for PWA)          ║"
echo "║  2. Create Shortcut → gAIa Heartbeat      ║"
echo "║     (POST to /api/iphone/ingest)          ║"
echo "║  3. USB sync via touchstone script        ║"
echo "║                                           ║"
echo "║  The walled garden feeds Gaia.            ║"
echo "║  Apple syncs. Gaia reads.                 ║"
echo "║  The wall protects. The spore transmits.  ║"
echo "╚══════════════════════════════════════════╝"
