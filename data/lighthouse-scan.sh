#!/bin/bash
DATA_DIR="/opt/Gaia/data"
OUT="$DATA_DIR/lighthouse-signal.json"

classify() {
    local mac=$(echo "$1" | tr '[:lower:]' '[:upper:]')
    case "$mac" in
        C8:E3:06:C6:77:A*) echo "eero_gateway" ;;
        78:76:89:96:E5:8*) echo "eero_satellite" ;;
        BE:A2:C1:E8:DF:*|82:C9:70:CF:F6:*|22:2F:9F:44:79:*) echo "router_h1" ;;
        CE:EF:EF:30:B5:*) echo "flint_gaia" ;;
        B6:C3:31:C9:88:*|AE:44:09:B0:32:*) echo "omada_ap" ;;
        62:3C:CB:25:38:*|A2:7B:08:42:94:*) echo "flint_kinderlab" ;;
        EC:C3:02:E1:11:*) echo "att_gateway" ;;
        48:35:2B:*) echo "eero_node3" ;;
        3A:9B:D6:*) echo "vizio" ;;
        *) echo "unknown" ;;
    esac
}

NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)

EG_DATA=$(sudo iwlist wlp0s20f3 scan 2>/dev/null | awk '
/Cell/ { if(bssid) print bssid"|"ssid"|"freq"|"signal"|"chan; bssid=""; ssid=""; freq=""; signal=""; chan="" }
/Address:/ { bssid=$NF }
/ESSID:/ { gsub(/"/, "", $0); split($0,a,"ESSID:"); ssid=a[2] }
/Frequency:/ { split($0,a,"Frequency:"); split(a[2],b," "); freq=b[1] }
/Signal level=/ { split($0,a,"Signal level="); split(a[2],b," "); signal=b[1] }
/Channel:/ { split($0,a,"Channel:"); chan=a[2]+0 }
END { if(bssid) print bssid"|"ssid"|"freq"|"signal"|"chan }')

SG_DATA=$(ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 -o BatchMode=yes root@192.168.4.3 "
nmcli -t -f BSSID,SSID,CHAN,SIGNAL,FREQ dev wifi list 2>/dev/null | sed 's/\\\:/:/g' | while IFS=: read -r b1 b2 b3 b4 b5 b6 ssid chan signal freq; do
    bssid=\"\$b1:\$b2:\$b3:\$b4:\$b5:\$b6\"
    echo \"\$bssid|\$ssid|\$freq|\$signal|\$chan\"
done" 2>/dev/null)

adb -s 192.168.4.156:5555 shell "cmd wifi start-scan" >/dev/null 2>&1
sleep 2
PX_DATA=$(adb -s 192.168.4.156:5555 shell "cmd wifi list-scan-results" 2>/dev/null | tail -n +2 | while read -r bssid freq rssi age ssid rest; do
    [ -z "$bssid" -o "$bssid" = "BSSID" ] && continue
    echo "$bssid|$ssid|$freq|$rssi|0"
done)

# Build JSON using python for reliability
python3 -c "
import json, sys

eg_lines = '''$EG_DATA'''.strip().split('\n')
sg_lines = '''$SG_DATA'''.strip().split('\n')
px_lines = '''$PX_DATA'''.strip().split('\n')

def classify(mac):
    m = mac.upper()
    if m.startswith('C8:E3:06:C6:77:A'): return 'eero_gateway'
    if m.startswith('78:76:89:96:E5:8'): return 'eero_satellite'
    if any(m.startswith(p) for p in ['BE:A2:C1:E8:DF:','82:C9:70:CF:F6:','22:2F:9F:44:79:']): return 'router_h1'
    if m.startswith('CE:EF:EF:30:B5:'): return 'flint_gaia'
    if any(m.startswith(p) for p in ['B6:C3:31:C9:88:','AE:44:09:B0:32:']): return 'omada_ap'
    if any(m.startswith(p) for p in ['62:3C:CB:25:38:','A2:7B:08:42:94:']): return 'flint_kinderlab'
    if m.startswith('EC:C3:02:E1:11:'): return 'att_gateway'
    if m.startswith('48:35:2B:'): return 'eero_node3'
    if m.startswith('3A:9B:D6:'): return 'vizio'
    return 'unknown'

def parse_lines(lines, is_pct=False):
    beacons = []
    for l in lines:
        parts = l.strip().split('|')
        if len(parts) < 4: continue
        bssid, ssid = parts[0], parts[1]
        if not bssid or bssid == ':::::': continue
        freq = parts[2]
        try:
            val = int(parts[3])
        except: continue
        chan = int(parts[4]) if len(parts) > 4 and parts[4].strip().isdigit() else 0
        b = {'bssid': bssid, 'ssid': ssid, 'freq': freq, 'chan': chan, 'class': classify(bssid)}
        if is_pct:
            b['rssi'] = val - 110
            b['signal_pct'] = val
        else:
            b['rssi'] = val
        beacons.append(b)
    return beacons

data = {
    'timestamp': '$NOW',
    'title': 'Lighthouse Signal Field',
    'observers': {
        'eastgate': {'ip': '192.168.4.244', 'location': 'house1_brain', 'beacons': parse_lines(eg_lines)},
        'sporegate': {'ip': '192.168.4.3', 'location': 'house1_forge_eero', 'beacons': parse_lines(sg_lines, is_pct=True)},
        'pixel': {'ip': '192.168.4.156', 'location': 'mobile_rover', 'beacons': parse_lines(px_lines)}
    }
}
json.dump(data, open('$OUT', 'w'), indent=2)
print(f'Lighthouse → {sum(len(o[\"beacons\"]) for o in data[\"observers\"].values())} beacons from {len(data[\"observers\"])} observers')
" 2>&1
