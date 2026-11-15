#!/usr/bin/env bash
# ============================================================================
# listener.sh — Gaia's EAR (far-field signal intelligence)
# ============================================================================
# Reads DNS query log from router every cycle. Builds signal map:
#   WHO is talking, WHAT they're asking for, HOW OFTEN, and what got BLOCKED.
# Listens from AFAR — never touches devices, only watches the airwaves.
#
# Output: membrane/local-terminal/remote/listener-signal.json
# ============================================================================
set -eo pipefail
: "${HOME:=/home/eastgate}"

ROUTER="192.168.4.1"
ROUTER_PASS="ExoticPanda714!!"
DNS_LOG="/tmp/dns-queries.log"
OUT_DIR="${HOME}/Development/ecoPrimals/membrane/local-terminal/remote"
OUT_FILE="${OUT_DIR}/listener-signal.json"
GAIA_OUT="/opt/Gaia/data/listener-signal.json"
CYCLE="${1:-60}"

mkdir -p "$OUT_DIR"

log() { echo "[$(date -Iseconds)] LISTENER: $*"; }

listen_cycle() {
    local ts=$(date -Iseconds)
    
    # Pull DNS query log from router
    local raw=$(sshpass -p "$ROUTER_PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 \
        root@$ROUTER "cat $DNS_LOG 2>/dev/null" 2>/dev/null)
    
    if [ -z "$raw" ]; then
        log "No DNS data from router"
        return 1
    fi
    
    local total_queries=$(echo "$raw" | grep -c "query\[" || true)
    local total_blocked=$(echo "$raw" | grep -c "config.*is 0.0.0.0" || true)
    local total_redirected=$(echo "$raw" | grep -c "config.*is 192.168.4" || true)
    local total_forwarded=$(echo "$raw" | grep -c "forwarded" || true)
    
    # Top talkers (by source IP)
    local top_talkers=$(echo "$raw" | grep "query\[" | \
        grep -oP '(?<=from )\S+' | sort | uniq -c | sort -rn | head -10)
    
    # Top domains queried
    local top_domains=$(echo "$raw" | grep "query\[" | \
        awk '{print $7}' | sort | uniq -c | sort -rn | head -20)
    
    # Blocked domains (what tried to leak)
    local blocked=$(echo "$raw" | grep "config.*is 0.0.0.0" | \
        awk '{print $7}' | sort | uniq -c | sort -rn | head -15)
    
    # Forwarded to WAN (actual leaks that passed through)
    local forwarded=$(echo "$raw" | grep "forwarded" | \
        awk '{print $7}' | sort | uniq -c | sort -rn | head -15)
    
    # Unknown devices querying (not our known gates)
    local unknown_talkers=$(echo "$raw" | grep "query\[" | \
        grep -oP '(?<=from )\S+' | sort -u | \
        grep -v -E "192.168.4.(1|3|100|103|107|147|148|176|237|244)$" || true)
    
    # Build JSON
    python3 -c "
import json, sys
ts = '$ts'
data = {
    'timestamp': ts,
    'cycle_seconds': $CYCLE,
    'totals': {
        'queries': $total_queries,
        'blocked': $total_blocked,
        'redirected': $total_redirected,
        'forwarded_to_wan': $total_forwarded,
        'block_rate_pct': round($total_blocked / max($total_queries, 1) * 100, 1)
    },
    'top_talkers': [],
    'top_domains': [],
    'blocked_attempts': [],
    'wan_leaks': [],
    'unknown_sources': $(echo "$unknown_talkers" | python3 -c "import sys,json; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))" 2>/dev/null || echo '[]')
}

# Parse top talkers
for line in '''$top_talkers'''.strip().split('\n'):
    parts = line.strip().split()
    if len(parts) == 2:
        data['top_talkers'].append({'count': int(parts[0]), 'ip': parts[1]})

# Parse top domains
for line in '''$top_domains'''.strip().split('\n'):
    parts = line.strip().split()
    if len(parts) == 2:
        data['top_domains'].append({'count': int(parts[0]), 'domain': parts[1]})

# Parse blocked
for line in '''$blocked'''.strip().split('\n'):
    parts = line.strip().split()
    if len(parts) == 2:
        data['blocked_attempts'].append({'count': int(parts[0]), 'domain': parts[1]})

# Parse forwarded
for line in '''$forwarded'''.strip().split('\n'):
    parts = line.strip().split()
    if len(parts) == 2:
        data['wan_leaks'].append({'count': int(parts[0]), 'domain': parts[1]})

print(json.dumps(data, indent=2))
" > "$OUT_FILE" 2>/dev/null
    
    # Copy to Gaia data
    cp "$OUT_FILE" "$GAIA_OUT" 2>/dev/null
    
    # Rotate the DNS log on router (keep it fresh each cycle)
    sshpass -p "$ROUTER_PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 \
        root@$ROUTER "cp $DNS_LOG ${DNS_LOG}.prev; > $DNS_LOG" 2>/dev/null
    
    log "queries=$total_queries blocked=$total_blocked forwarded=$total_forwarded block_rate=$(echo "scale=1; $total_blocked * 100 / ($total_queries + 1)" | bc)%"
}

# Single run or loop
if [ "${2:-}" = "--once" ]; then
    listen_cycle
else
    log "Starting listener — cycle every ${CYCLE}s"
    while true; do
        listen_cycle || true
        sleep "$CYCLE"
    done
fi
