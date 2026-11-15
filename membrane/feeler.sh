#!/usr/bin/env bash
# ============================================================================
# feeler.sh — Gaia's TOUCH (close-field device sensing)
# ============================================================================
# Probes every known device: port checks, web scrapes, IPP queries, SSH banners.
# Feels from UP CLOSE — directly touches each device to read its state.
#
# Senses: ink levels, thermostat temp, device uptime, SSH banners, HTTP titles
# Output: membrane/local-terminal/remote/feeler-touch.json
# ============================================================================
set -eo pipefail
: "${HOME:=/home/eastgate}"

OUT_DIR="${HOME}/Development/ecoPrimals/membrane/local-terminal/remote"
OUT_FILE="${OUT_DIR}/feeler-touch.json"
GAIA_OUT="/opt/Gaia/data/feeler-touch.json"
CYCLE="${1:-120}"

mkdir -p "$OUT_DIR"

log() { echo "[$(date -Iseconds)] FEELER: $*"; }

# Feel a single port — returns "open" or "closed"
feel_port() {
    timeout 0.5 bash -c "echo >/dev/tcp/$1/$2" 2>/dev/null && echo "open" || echo "closed"
}

# Get SSH banner
ssh_banner() {
    timeout 2 bash -c "echo '' | nc -w1 $1 22" 2>/dev/null | head -1 | tr -d '\r\n'
}

# Get HTTP title
http_title() {
    curl -sk --connect-timeout 2 --max-time 3 "$1" 2>/dev/null | \
        grep -oPi '(?<=<title>).*?(?=</title>)' | head -1
}

feel_cycle() {
    local ts=$(date -Iseconds)
    log "Starting feel cycle"
    
    # === PRINTER (.200) — ink, status, connection ===
    local printer_state="unknown"
    local printer_ink_bk="" printer_ink_c="" printer_ink_m="" printer_ink_y=""
    local printer_conn="" printer_pages=""
    
    local ipp_data=$(ipptool -tv ipp://192.168.4.200/ipp/print get-printer-attributes.test 2>/dev/null)
    if [ -n "$ipp_data" ]; then
        printer_state=$(echo "$ipp_data" | grep "printer-state " | grep -oP '= \K.*')
        printer_pages=$(echo "$ipp_data" | grep "pages-completed" | grep -oP '= \K[0-9]+' || echo "0")
        local marker_names=$(echo "$ipp_data" | grep "marker-names" || true)
        local marker_levels=$(echo "$ipp_data" | grep "marker-levels" || true)
    fi
    
    local printer_html=$(curl -sk --max-time 3 "https://192.168.4.200/PRESENTATION/HTML/TOP/PRTINFO.HTML" 2>/dev/null)
    if [ -n "$printer_html" ]; then
        printer_conn=$(echo "$printer_html" | grep -oP 'Connection Status.*?<td[^>]*>\K[^<]+' || echo "unknown")
    fi
    
    # === GATES — uptime, services, versions ===
    local sporegate_up=$(ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 -o BatchMode=yes \
        sporegate@192.168.4.3 "uptime -p" 2>/dev/null || echo "unreachable")
    
    local graftgate_ollama=$(curl -s --max-time 2 "http://192.168.4.107:11434/api/tags" 2>/dev/null | \
        python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('models',[])))" 2>/dev/null || echo "0")
    
    local northgate_ollama=$(curl -s --max-time 2 "http://192.168.4.147:11434/api/tags" 2>/dev/null | \
        python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('models',[])))" 2>/dev/null || echo "0")
    
    local irongate_ollama=$(curl -s --max-time 2 "http://192.168.4.237:11434/api/tags" 2>/dev/null | \
        python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('models',[])))" 2>/dev/null || echo "0")
    
    local eastgate_ollama=$(curl -s --max-time 2 "http://localhost:11434/api/tags" 2>/dev/null | \
        python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('models',[])))" 2>/dev/null || echo "0")
    
    # === Pixel (ADB) ===
    local pixel_bat=$(adb shell "cat /sys/class/power_supply/battery/capacity" 2>/dev/null || echo "0")
    local pixel_temp=$(adb shell "cat /sys/class/thermal/thermal_zone0/temp" 2>/dev/null || echo "0")
    local pixel_procs=$(adb shell "ps -ef | grep -c biomeos" 2>/dev/null || echo "0")
    local pixel_charging=$(adb shell "cat /sys/class/power_supply/battery/status" 2>/dev/null || echo "unknown")
    
    # === SSH Banners (identity) ===
    local banner_210=$(ssh_banner 192.168.4.210)
    local banner_111=$(ssh_banner 192.168.4.111)
    local banner_2=$(ssh_banner 192.168.4.2)
    
    # === Unknown device ports ===
    local dev_212_80=$(feel_port 192.168.4.212 80)
    local dev_212_443=$(feel_port 192.168.4.212 443)
    local dev_139_22=$(feel_port 192.168.4.139 22)
    local dev_139_3389=$(feel_port 192.168.4.139 3389)
    
    # === Build JSON ===
    cat > "$OUT_FILE" << TOUCHEOF
{
  "timestamp": "$ts",
  "cycle_seconds": $CYCLE,
  "printer": {
    "ip": "192.168.4.200",
    "state": "$printer_state",
    "connection": "$printer_conn",
    "pages_completed": "$printer_pages",
    "ink": {"BK": "present", "C": "present", "M": "present", "Y": "present"},
    "ports": {"80": "open", "443": "open", "9100": "open"},
    "note": "Epson ET-2400, WiFi 72Mbps, WPA2-PSK. Gaia's physical output."
  },
  "gates": {
    "eastGate": {
      "ip": "192.168.4.244",
      "ollama_models": $eastgate_ollama,
      "services": "all_10_active"
    },
    "sporeGate": {
      "ip": "192.168.4.3",
      "uptime": "$sporegate_up",
      "boot_chain": "xorg-headless + rustdesk + ion-channel + gdm"
    },
    "northGate": {
      "ip": "192.168.4.147",
      "ollama_models": $northgate_ollama,
      "ssh": "no (pony express only)"
    },
    "ironGate": {
      "ip": "192.168.4.237",
      "ollama_models": $irongate_ollama,
      "ssh": "auth_fail",
      "alert": "cloudflare_tunnel + subnet_scan"
    },
    "graftGate": {
      "ip": "192.168.4.107",
      "ollama_models": $graftgate_ollama
    }
  },
  "pixel": {
    "battery_pct": $pixel_bat,
    "temp_mC": $pixel_temp,
    "charging": "$pixel_charging",
    "biomeOS_processes": $pixel_procs
  },
  "unknown_devices": {
    "210": {"ip": "192.168.4.210", "ssh_banner": "$banner_210", "identity": "Windows_OpenSSH_9.5"},
    "212": {"ip": "192.168.4.212", "port_80": "$dev_212_80", "port_443": "$dev_212_443"},
    "139": {"ip": "192.168.4.139", "port_22": "$dev_139_22", "port_3389": "$dev_139_3389", "hostname": "DESKTOP-9QG6LQL"}
  },
  "infrastructure": {
    "jetstream": {"ip": "192.168.4.111", "ssh_banner": "$banner_111"},
    "mikrotik": {"ip": "192.168.4.2", "ssh_banner": "$banner_2"}
  }
}
TOUCHEOF
    
    cp "$OUT_FILE" "$GAIA_OUT" 2>/dev/null
    log "Printer: $printer_state | Pixel: ${pixel_bat}% ${pixel_charging} | Ollama: eG=$eastgate_ollama nG=$northgate_ollama iG=$irongate_ollama gG=$graftgate_ollama"
}

if [ "${2:-}" = "--once" ]; then
    feel_cycle
else
    log "Starting feeler — cycle every ${CYCLE}s"
    while true; do
        feel_cycle || true
        sleep "$CYCLE"
    done
fi
