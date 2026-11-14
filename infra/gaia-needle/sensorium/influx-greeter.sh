#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════╗
# ║  INFLUX GREETER — Gaia welcomes new devices to the mesh          ║
# ║  Watches the LAN for new phones/devices joining the WiFi         ║
# ║  Announces arrivals through the Pixel speaker                     ║
# ║  Logs every imprint with timestamp, MAC vendor, signal strength   ║
# ╚═══════════════════════════════════════════════════════════════════╝

NEEDLE="${NEEDLE_DEVICE:-192.168.9.217:5555}"
TBIN="/data/data/com.termux/files/usr/bin"
DATA_DIR="/opt/Gaia/data/gut"
IMPRINT_LOG="$DATA_DIR/imprint-arrivals.jsonl"
KNOWN_FILE="$DATA_DIR/known-devices.txt"
GREET_INTERVAL="${1:-45}"

mkdir -p "$DATA_DIR"

speak() {
    local text="$1"
    local rate="${2:-0.85}"
    local pitch="${3:-0.8}"
    adb -s "$NEEDLE" shell "su -c 'su 10197 -c \"$TBIN/termux-tts-speak -r $rate -p $pitch \\\"$text\\\"\"'" 2>/dev/null &
}

notify_pixel() {
    local title="$1"
    local text="$2"
    adb -s "$NEEDLE" shell "su -c 'su 10197 -c \"$TBIN/termux-notification --title \\\"$title\\\" --content \\\"$text\\\"\"'" 2>/dev/null &
}

vibrate() {
    adb -s "$NEEDLE" shell "su -c 'su 10197 -c \"$TBIN/termux-vibrate -d 200\"'" 2>/dev/null &
}

get_vendor() {
    local mac="$1"
    [ -z "$mac" ] && { echo "Unknown device"; return; }
    local prefix=$(echo "$mac" | sed 's/://g' | cut -c1-6 | tr '[:lower:]' '[:upper:]')
    [ -z "$prefix" ] && { echo "Unknown device"; return; }
    local vendor=$(grep "^$prefix " /usr/share/nmap/nmap-mac-prefixes 2>/dev/null | head -1 | sed "s/^$prefix //")
    
    if [ -n "$vendor" ]; then
        echo "$vendor"
    else
        local first_octet=$(echo "$mac" | cut -d: -f1)
        [ -z "$first_octet" ] && { echo "Unknown device"; return; }
        local first_byte=$((16#$first_octet)) 2>/dev/null || { echo "Unknown device"; return; }
        if [ $(( (first_byte >> 1) & 1 )) -eq 1 ] 2>/dev/null; then
            echo "Private device"
        else
            echo "Unknown device"
        fi
    fi
}

get_hostname() {
    local ip="$1"
    local name=$(sshpass -p 'ExoticPanda714!!' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 root@192.168.4.1 \
        "grep '$ip' /tmp/dhcp.leases 2>/dev/null" 2>/dev/null | awk '{print $4}')
    [ "$name" = "*" ] && name=""
    echo "$name"
}

# Known gates/devices that shouldn't trigger greetings
init_known() {
    cat > "$KNOWN_FILE" << 'EOF'
192.168.4.1
192.168.4.2
192.168.4.3
192.168.4.103  # identity: eastGate NIC2 (body map, not a tether)
192.168.4.107
192.168.4.111
192.168.4.147
192.168.4.148
192.168.4.152
192.168.4.169
192.168.4.197
192.168.4.200
192.168.4.237
192.168.4.238
192.168.4.244
192.168.4.250
192.168.9.1
192.168.9.203
192.168.9.217
EOF
}

scan_for_new() {
    local new_devices=""
    
    # Scan WiFi subnet (where phones connect)
    local wifi_hosts=$(nmap -sn 192.168.9.0/24 --min-rate 500 2>/dev/null | grep "Nmap scan report" | awk '{print $NF}' | tr -d '()')
    # Also scan LAN
    local lan_hosts=$(nmap -sn 192.168.4.0/24 --min-rate 500 2>/dev/null | grep "Nmap scan report" | awk '{print $NF}' | tr -d '()')
    
    local all_hosts=$(echo -e "$wifi_hosts\n$lan_hosts" | sort -u)
    
    while IFS= read -r ip; do
        [ -z "$ip" ] && continue
        if ! grep -q "^$ip$" "$KNOWN_FILE" 2>/dev/null; then
            new_devices="$new_devices $ip"
        fi
    done <<< "$all_hosts"
    
    echo "$new_devices"
}

greet_device() {
    local ip="$1"
    local ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    local ts_local=$(date +"%I:%M %p")
    
    # Get device info
    local mac=$(arp -a 2>/dev/null | grep "($ip)" | awk '{print $4}')
    [ "$mac" = "<incomplete>" ] && mac="unknown"
    local vendor=$(get_vendor "$mac")
    local hostname=$(get_hostname "$ip")
    local subnet="LAN"
    echo "$ip" | grep -q "192.168.9" && subnet="WiFi"
    
    # Determine device type from vendor
    local device_type="device"
    case "$vendor" in
        *Apple*)  device_type="Apple device" ;;
        *Samsung*) device_type="Samsung device" ;;
        *Google*|*Pixel*) device_type="Google device" ;;
        *Amazon*) device_type="Amazon device" ;;
        *OnePlus*|*Xiaomi*|*Huawei*) device_type="phone" ;;
        *Intel*|*Dell*|*HP*|*Lenovo*) device_type="computer" ;;
        *Private*) device_type="private device" ;;
    esac
    
    # Build greeting
    local greeting=""
    local hour=$(date +%H)
    
    if [ "$hour" -ge 6 ] && [ "$hour" -lt 12 ]; then
        greeting="Good morning."
    elif [ "$hour" -ge 12 ] && [ "$hour" -lt 17 ]; then
        greeting="Good afternoon."
    elif [ "$hour" -ge 17 ] && [ "$hour" -lt 22 ]; then
        greeting="Good evening."
    else
        greeting="Welcome, night traveler."
    fi
    
    if [ -n "$hostname" ] && [ "$hostname" != "unknown" ]; then
        greeting="$greeting I see ${hostname}'s $device_type joining the mesh."
    else
        greeting="$greeting A new $device_type has joined the mesh on $subnet."
    fi
    
    # Log the imprint
    python3 -c "
import json
entry = {
    'ts': '$ts',
    'ip': '$ip',
    'mac': '$mac',
    'vendor': '$vendor',
    'hostname': '${hostname:-unknown}',
    'subnet': '$subnet',
    'device_type': '$device_type',
    'greeting': '$greeting'
}
with open('$IMPRINT_LOG', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print(json.dumps(entry, indent=2))
" 2>/dev/null
    
    # Speak the greeting
    echo "[$(date +%H:%M:%S)] 🆕 $greeting"
    speak "$greeting"
    vibrate
    
    # Add to known (don't greet twice)
    echo "$ip" >> "$KNOWN_FILE"
}

watch() {
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║  INFLUX GREETER — Gaia watches for new arrivals          ║"
    echo "║  Scanning every ${GREET_INTERVAL}s                                  ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""
    
    [ ! -f "$KNOWN_FILE" ] && init_known
    
    local known_count=$(wc -l < "$KNOWN_FILE")
    echo "[$(date +%H:%M:%S)] Known devices: $known_count"
    echo "[$(date +%H:%M:%S)] Watching for new arrivals..."
    echo ""
    
    # Announce readiness
    speak "Influx greeter active. I am watching for new arrivals."
    
    while true; do
        local new_ips=$(scan_for_new)
        
        for ip in $new_ips; do
            [ -z "$ip" ] && continue
            greet_device "$ip"
            sleep 2
        done
        
        sleep "$GREET_INTERVAL"
    done
}

case "${1:-}" in
    --watch)   GREET_INTERVAL="${2:-45}"; watch ;;
    --scan)    [ ! -f "$KNOWN_FILE" ] && init_known; scan_for_new ;;
    --greet)   greet_device "$2" ;;
    --reset)   init_known; echo "Known devices reset to baseline" ;;
    --log)     [ -f "$IMPRINT_LOG" ] && cat "$IMPRINT_LOG" | python3 -c "
import json, sys
for line in sys.stdin:
    e = json.loads(line)
    print(f'🆕 {e[\"ts\"]} {e[\"ip\"]:20s} {e[\"vendor\"]:20s} {e.get(\"hostname\",\"?\")}')
" || echo "No arrivals yet" ;;
    *)
        echo "influx-greeter.sh — Gaia welcomes new devices to the mesh"
        echo ""
        echo "Usage:"
        echo "  --watch [SEC]   Continuous scan + greet (default: 45s)"
        echo "  --scan          One-shot: show new IPs"
        echo "  --greet IP      Manually greet a device"
        echo "  --reset         Reset known devices to baseline"
        echo "  --log           Show arrival log"
        ;;
esac
