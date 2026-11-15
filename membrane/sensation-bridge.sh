#!/usr/bin/env bash
# ============================================================================
# sensation-bridge.sh — Bridges Pixel outer ear → eastGate membrane
# ============================================================================
# Pulls outer-ear.json from Pixel via ADB every cycle
# Combines with listener (inner ear) for full sensation
# Output: membrane/local-terminal/remote/sensation.json
# ============================================================================
set -eo pipefail
: "${HOME:=/home/eastgate}"

OUT_DIR="${HOME}/Development/ecoPrimals/membrane/local-terminal/remote"
GAIA_OUT="/opt/Gaia/data"
CYCLE="${1:-30}"

log() { echo "[$(date -Iseconds)] SENSATION: $*"; }

sensation_cycle() {
    local ts=$(date -Iseconds)
    
    # Pull outer ear from Pixel
    local outer=$(adb shell "cat /data/local/tmp/biomeos/sensorium/outer-ear.json 2>/dev/null" < /dev/null 2>/dev/null)
    
    # Read inner ear (listener)
    local inner=""
    [ -f "$OUT_DIR/listener-signal.json" ] && inner=$(cat "$OUT_DIR/listener-signal.json")
    
    # Read touch (feeler)
    local touch=""
    [ -f "$OUT_DIR/feeler-touch.json" ] && touch=$(cat "$OUT_DIR/feeler-touch.json")
    
    # Combine into full sensation
    python3 -c "
import json, sys

ts = '$ts'
outer = {}
inner = {}
touch = {}

try: outer = json.loads('''$outer''')
except: pass
try: inner = json.loads(open('$OUT_DIR/listener-signal.json').read())
except: pass
try: touch = json.loads(open('$OUT_DIR/feeler-touch.json').read())
except: pass

# Derive proximity zone
zone = outer.get('proximity', {}).get('zone', 'unknown')
rssi_ap = int(outer.get('proximity', {}).get('rssi_aperture', -127))
battery = outer.get('battery', {}).get('pct', 0)
charging = outer.get('battery', {}).get('charging', 'unknown')

# Inner ear stats
queries = inner.get('totals', {}).get('queries', 0)
blocked = inner.get('totals', {}).get('blocked', 0)
block_rate = inner.get('totals', {}).get('block_rate_pct', 0)
wan_leaks = inner.get('totals', {}).get('forwarded_to_wan', 0)

# Touch stats
printer_state = touch.get('printer', {}).get('state', 'unknown')
ollama_total = sum([
    touch.get('gates', {}).get(g, {}).get('ollama_models', 0)
    for g in ['eastGate', 'northGate', 'ironGate', 'graftGate']
])

sensation = {
    'timestamp': ts,
    'sensation': 'FULL',
    'outer_ear': {
        'source': 'Pixel (grapheneGate)',
        'zone': zone,
        'rssi_aperture': rssi_ap,
        'battery_pct': battery,
        'charging': charging,
        'nearby_networks': outer.get('proximity', {}).get('visible_networks', 0),
        'note': 'WiFi RSSI proximity: -20=touching, -50=same room, -70=house, -85=yard'
    },
    'inner_ear': {
        'source': 'Flint (GL-MT6000 router)',
        'dns_queries': queries,
        'dns_blocked': blocked,
        'block_rate_pct': block_rate,
        'wan_leaks': wan_leaks,
        'note': 'DNS signal intelligence from router query log'
    },
    'touch': {
        'source': 'feeler.sh (device probing)',
        'printer': printer_state,
        'ollama_models_total': ollama_total,
        'note': 'Direct device probing via ports/IPP/SSH'
    },
    'organism': {
        'total_senses': 3,
        'sense_names': ['outer_ear (Pixel WiFi proximity)', 'inner_ear (Flint DNS signals)', 'touch (feeler device probing)'],
        'klein_io': '60 DNS sinkholes active',
        'devices_sensed': 22
    }
}

print(json.dumps(sensation, indent=2))
" > "$OUT_DIR/sensation.json" 2>/dev/null

    cp "$OUT_DIR/sensation.json" "$GAIA_OUT/sensation.json" 2>/dev/null
    
    log "zone=$zone rssi=$rssi_ap bat=${battery}% dns=$queries blocked=$blocked printer=$printer_state"
}

if [ "${2:-}" = "--once" ]; then
    sensation_cycle
else
    log "Starting sensation bridge — cycle every ${CYCLE}s"
    while true; do
        sensation_cycle || true
        sleep "$CYCLE"
    done
fi
