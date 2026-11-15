#!/bin/bash
# imprint-watch.sh — Gaia's immune system for the LAN
# Detects new devices joining the network, logs them as "imprints"
# When people come, their phones hit the WiFi — Gaia FEELS them arrive

DATA_DIR="/home/eastgate/.local/share/gaia/data/gut"
BASELINE_FILE="$DATA_DIR/lan-baseline.json"
IMPRINT_LOG="$DATA_DIR/imprint-log.jsonl"
CURRENT_FILE="$DATA_DIR/lan-current.json"
PIXEL_IP="192.168.9.217"
PIXEL_PORT="5555"
EASTGATE_DATA="/opt/Gaia/data"

mkdir -p "$DATA_DIR"

OUI_FILE="/usr/share/nmap/nmap-mac-prefixes"

lookup_vendor() {
    local mac="$1"
    local prefix=$(echo "$mac" | tr ':' '-' | cut -d'-' -f1-3 | tr '[:lower:]' '[:upper:]' | tr '-' '')
    if [ -f "$OUI_FILE" ]; then
        grep -i "^$prefix" "$OUI_FILE" 2>/dev/null | head -1 | sed "s/^$prefix //"
    else
        echo "unknown"
    fi
}

scan_lan() {
    local ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    local devices='[]'
    
    # Scan both subnets
    local scan_4=$(nmap -sn 192.168.4.0/24 --min-rate 500 2>/dev/null)
    local scan_9=$(nmap -sn 192.168.9.0/24 --min-rate 500 2>/dev/null)
    
    # Get ARP table for MAC addresses
    local arp_data=$(arp -a 2>/dev/null)
    
    # Get DHCP leases from router
    local leases=$(sshpass -p 'ExoticPanda714!!' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 root@192.168.4.1 "cat /tmp/dhcp.leases 2>/dev/null" 2>/dev/null)
    
    # Parse all alive hosts
    local hosts_4=$(echo "$scan_4" | grep "Nmap scan report" | awk '{print $NF}' | tr -d '()')
    local hosts_9=$(echo "$scan_9" | grep "Nmap scan report" | awk '{print $NF}' | tr -d '()')
    
    python3 -c "
import json, subprocess, sys

hosts_4 = '''$hosts_4'''.strip().split('\n')
hosts_9 = '''$hosts_9'''.strip().split('\n')
arp_raw = '''$arp_data'''
lease_raw = '''$leases'''
ts = '$ts'

all_hosts = [h for h in hosts_4 + hosts_9 if h]

# Parse ARP for MACs
arp_map = {}
for line in arp_raw.split('\n'):
    parts = line.split()
    if len(parts) >= 4 and 'at' in parts:
        ip = parts[0].strip('()')
        for i, p in enumerate(parts):
            if p == 'at' and i+1 < len(parts):
                mac = parts[i+1]
                if ':' in mac:
                    arp_map[ip] = mac
                break
    # Also handle the (ip) format
    for part in parts:
        if part.startswith('(') and part.endswith(')'):
            ip = part.strip('()')
            for i, p in enumerate(parts):
                if p == 'at' and i+1 < len(parts):
                    mac = parts[i+1]
                    if ':' in mac:
                        arp_map[ip] = mac

# Parse DHCP leases for hostnames and MACs
lease_map = {}  # ip -> {mac, name}
for line in lease_raw.strip().split('\n'):
    parts = line.split()
    if len(parts) >= 4:
        mac = parts[1]
        ip = parts[2]
        name = parts[3] if parts[3] != '*' else None
        lease_map[ip] = {'mac': mac, 'name': name}

# Known devices
known = {
    '192.168.4.1':   {'name': 'router',      'role': 'GL-MT6000'},
    '192.168.4.2':   {'name': 'mikrotik',     'role': 'L2 bridge'},
    '192.168.4.3':   {'name': 'sporeGate',    'role': 'forge + heart-pull'},
    '192.168.4.103': {'name': 'eastGate',     'role': 'brain+gut'},
    '192.168.4.244': {'name': 'eastGate-eth', 'role': 'brain+gut (ethernet)'},
    '192.168.4.107': {'name': 'graftGate',    'role': 'Mac Mini'},
    '192.168.4.111': {'name': 'jetstream',    'role': 'House 2 switch'},
    '192.168.4.147': {'name': 'northGate',    'role': 'Polaris - 63 models'},
    '192.168.4.148': {'name': 'southGate',    'role': 'iPhone XS'},
    '192.168.4.237': {'name': 'ironGate',     'role': 'Ubuntu NUC'},
    '192.168.4.100': {'name': 'blueGate',     'role': 'Windows SSH'},
    '192.168.4.200': {'name': 'epson-printer','role': 'EPSON ET-2400'},
    '192.168.4.250': {'name': 'router-enp5s0','role': 'GL-MT6000 secondary'},
    '192.168.4.110': {'name': 'epson-printer','role': 'EPSON (old IP)'},
    '192.168.9.203': {'name': 'grapheneGate', 'role': 'Pixel 8a rover'},
}

devices = []
for ip in sorted(set(all_hosts)):
    mac = arp_map.get(ip) or (lease_map.get(ip, {}).get('mac') if ip in lease_map else None) or 'unknown'
    lease_info = lease_map.get(ip, {})
    known_info = known.get(ip, {})
    
    name = known_info.get('name') or lease_info.get('name') or 'unknown'
    role = known_info.get('role', '')
    subnet = '4.x LAN' if ip.startswith('192.168.4.') else '9.x WiFi'
    is_known = ip in known
    
    devices.append({
        'ip': ip,
        'mac': mac,
        'name': name,
        'role': role,
        'subnet': subnet,
        'known': is_known,
        'first_seen': ts
    })

result = {
    'ts': ts,
    'total_devices': len(devices),
    'known': sum(1 for d in devices if d['known']),
    'unknown': sum(1 for d in devices if not d['known']),
    'devices': devices
}

print(json.dumps(result, indent=2))
" 2>/dev/null
}

baseline() {
    echo "[imprint-watch] Capturing baseline..."
    scan_lan > "$BASELINE_FILE"
    local count=$(python3 -c "import json; d=json.load(open('$BASELINE_FILE')); print(d['total_devices'])")
    echo "[imprint-watch] Baseline: $count devices ($BASELINE_FILE)"
    
    # Copy to data server
    cp "$BASELINE_FILE" "$EASTGATE_DATA/gut/lan-baseline.json" 2>/dev/null
}

detect_new() {
    if [ ! -f "$BASELINE_FILE" ]; then
        echo "[imprint-watch] No baseline! Run: $0 --baseline first"
        return 1
    fi
    
    scan_lan > "$CURRENT_FILE"
    
    python3 -c "
import json, sys
from datetime import datetime

baseline = json.load(open('$BASELINE_FILE'))
current = json.load(open('$CURRENT_FILE'))

base_ips = {d['ip'] for d in baseline['devices']}
base_macs = {d['mac'] for d in baseline['devices'] if d['mac'] != 'unknown'}

new_devices = []
departed = []

for dev in current['devices']:
    if dev['ip'] not in base_ips:
        new_devices.append(dev)

for dev in baseline['devices']:
    curr_ips = {d['ip'] for d in current['devices']}
    if dev['ip'] not in curr_ips:
        departed.append(dev)

if new_devices:
    print(f'🆕 NEW IMPRINTS DETECTED: {len(new_devices)}')
    for d in new_devices:
        print(f'  → {d[\"ip\"]:20s} MAC={d[\"mac\"]:20s} name={d[\"name\"]}')
        # Log to imprint log
        entry = {**d, 'event': 'arrive', 'ts': current['ts']}
        with open('$IMPRINT_LOG', 'a') as f:
            f.write(json.dumps(entry) + '\n')
else:
    print('No new devices since baseline')

if departed:
    print(f'👋 DEPARTED: {len(departed)}')
    for d in departed:
        print(f'  ← {d[\"ip\"]:20s} MAC={d[\"mac\"]:20s} name={d[\"name\"]}')
        entry = {**d, 'event': 'depart', 'ts': current['ts']}
        with open('$IMPRINT_LOG', 'a') as f:
            f.write(json.dumps(entry) + '\n')

print(f'Total now: {current[\"total_devices\"]} (was {baseline[\"total_devices\"]})')
print(f'Known: {current[\"known\"]}  Unknown: {current[\"unknown\"]}')
" 2>/dev/null
    
    # Copy current state to data server
    cp "$CURRENT_FILE" "$EASTGATE_DATA/gut/lan-current.json" 2>/dev/null
}

watch_loop() {
    local interval="${1:-60}"
    echo "[imprint-watch] Watching every ${interval}s... (Ctrl+C to stop)"
    
    if [ ! -f "$BASELINE_FILE" ]; then
        baseline
    fi
    
    while true; do
        echo ""
        echo "=== $(date) ==="
        detect_new
        
        # Optional: announce via Pixel TTS
        local new_count=$(python3 -c "
import json
b = json.load(open('$BASELINE_FILE'))
c = json.load(open('$CURRENT_FILE'))
base_ips = {d['ip'] for d in b['devices']}
new = [d for d in c['devices'] if d['ip'] not in base_ips]
print(len(new))
" 2>/dev/null)
        
        if [ "$new_count" -gt 0 ] 2>/dev/null; then
            adb -s "$PIXEL_IP:$PIXEL_PORT" shell "su -c 'am start -a android.intent.action.TTS -e text \"$new_count new devices detected on the network\"'" 2>/dev/null &
        fi
        
        sleep "$interval"
    done
}

show_map() {
    local file="${1:-$CURRENT_FILE}"
    [ ! -f "$file" ] && file="$BASELINE_FILE"
    [ ! -f "$file" ] && { echo "No scan data. Run --baseline or --detect first."; return 1; }
    
    python3 -c "
import json
d = json.load(open('$file'))
print(f'LAN MAP — {d[\"ts\"]}')
print(f'Total: {d[\"total_devices\"]}  Known: {d[\"known\"]}  Unknown: {d[\"unknown\"]}')
print()
print(f'{\"IP\":20s} {\"MAC\":20s} {\"Name\":16s} {\"Subnet\":10s} {\"Role\"}')
print('─' * 90)
for dev in sorted(d['devices'], key=lambda x: (x['subnet'], x['ip'])):
    known_mark = '✓' if dev['known'] else '?'
    print(f'{dev[\"ip\"]:20s} {dev[\"mac\"]:20s} {dev[\"name\"]:16s} {dev[\"subnet\"]:10s} {dev[\"role\"]} {known_mark}')
" 2>/dev/null
}

show_log() {
    if [ ! -f "$IMPRINT_LOG" ]; then
        echo "No imprints logged yet."
        return 0
    fi
    echo "=== IMPRINT LOG ==="
    python3 -c "
import json
with open('$IMPRINT_LOG') as f:
    for line in f:
        e = json.loads(line)
        icon = '🆕' if e['event'] == 'arrive' else '👋'
        print(f'{icon} {e[\"ts\"]} {e[\"ip\"]:20s} {e[\"mac\"]:20s} {e[\"name\"]}')
" 2>/dev/null
}

case "${1:-}" in
    --baseline)  baseline ;;
    --detect)    detect_new ;;
    --watch)     watch_loop "${2:-60}" ;;
    --map)       show_map "$2" ;;
    --log)       show_log ;;
    *)
        echo "imprint-watch.sh — Gaia's LAN immune system"
        echo ""
        echo "Usage:"
        echo "  --baseline        Capture current LAN as known baseline"
        echo "  --detect          Detect new/departed devices since baseline"
        echo "  --watch [SEC]     Continuous monitoring (default: 60s)"
        echo "  --map             Show full LAN map"
        echo "  --log             Show imprint arrival/departure log"
        ;;
esac
