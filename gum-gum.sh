#!/bin/bash
# ╔═══════════════════════════════════════════════════════╗
# ║  GUM GUM PROTOCOL — Gaia Agglutination Daemon        ║
# ║  Touch → Eat → Agglutinate → Beacon IN + OUT         ║
# ╚═══════════════════════════════════════════════════════╝
#
# When a new device appears on 192.168.4.0/24:
#   1. TOUCH  — fingerprint (ports, OUI, SSH banner, HTTP)
#   2. EAT    — enroll into WG mesh + assign mesh IP
#   3. STICK  — deploy config if we can SSH in
#   4. BEACON — announce on LAN (mDNS) + WAN (mesh)

MESH_DIR="/home/eastgate/enrollment/gaia-mesh"
STATE_DIR="/home/eastgate/Development/ecoPrimals/primals/GaiaGate/data/gum-gum"
LOG="$STATE_DIR/agglutination.log"
FLINT_IP="192.168.4.1"
FLINT_PUB="oEMwYKDFjQkLxnQvv0n/eUheWFquxnWJt2m0ijWvdAE="
MESH_SUBNET="10.13.37"
NEXT_MESH_IP=10  # start assigning from .10
AUTO_ENROLL=${GUM_GUM_AUTO_ENROLL:-0}
LAST_MESH_IP=""

mkdir -p "$STATE_DIR" "$MESH_DIR"
echo "$(date) — GUM GUM PROTOCOL STARTED" | tee "$LOG"

# Load known devices
declare -A KNOWN_MACS
load_known() {
    if [ -f "$STATE_DIR/known-macs.txt" ]; then
        while IFS='=' read -r mac info; do
            KNOWN_MACS["$mac"]="$info"
        done < "$STATE_DIR/known-macs.txt"
    fi
}

save_known() {
    > "$STATE_DIR/known-macs.txt"
    for mac in "${!KNOWN_MACS[@]}"; do
        echo "${mac}=${KNOWN_MACS[$mac]}" >> "$STATE_DIR/known-macs.txt"
    done
}

# Get next available mesh IP
get_next_mesh_ip() {
    while [ -f "$STATE_DIR/mesh-$MESH_SUBNET.$NEXT_MESH_IP" ]; do
        NEXT_MESH_IP=$((NEXT_MESH_IP + 1))
    done
    echo "$MESH_SUBNET.$NEXT_MESH_IP"
}

# ── TOUCH ──────────────────────────────────────────────
touch_device() {
    local ip=$1
    local mac=$2
    local info="$STATE_DIR/device-${ip##*.}.json"
    
    echo "$(date) — TOUCH: $ip ($mac)" | tee -a "$LOG"
    
    # OUI lookup (cached)
    local oui=$(echo "$mac" | cut -d: -f1-3)
    local vendor=$(curl -s --connect-timeout 2 "https://api.macvendors.com/$oui" 2>/dev/null || echo "unknown")
    
    # Port scan
    local ports=$(nmap -Pn -p 22,80,443,8080,3000,8291,8728,11434,51820 "$ip" -T5 --max-retries 0 2>/dev/null | grep "open" | awk '{print $1}' | tr '\n' ',')
    
    # SSH banner
    local ssh_banner=$(timeout 2 bash -c "echo '' | nc -w 1 $ip 22 2>/dev/null" | head -1)
    
    # HTTP title
    local http_title=$(curl -s --connect-timeout 2 "http://$ip" 2>/dev/null | grep -oP '<title>\K[^<]+' | head -1)
    
    # Write device profile
    cat > "$info" << DEVEOF
{
  "ip": "$ip",
  "mac": "$mac",
  "vendor": "$vendor",
  "ports": "$ports",
  "ssh_banner": "$ssh_banner",
  "http_title": "$http_title",
  "first_seen": "$(date -Iseconds)",
  "status": "touched"
}
DEVEOF
    
    echo "$(date) — TOUCHED: $ip vendor=$vendor ports=[$ports] ssh=$ssh_banner http=$http_title" | tee -a "$LOG"
}

# ── EAT ────────────────────────────────────────────────
eat_device() {
    local ip=$1
    local mac=$2
    local mesh_ip=$(get_next_mesh_ip)
    
    echo "$(date) — EAT: $ip → mesh $mesh_ip" | tee -a "$LOG"
    
    # Generate WG keypair for this device
    local priv=$(wg genkey)
    local pub=$(echo "$priv" | wg pubkey)
    local psk=$(grep PresharedKey "$MESH_DIR/eastgate-wg0.conf" 2>/dev/null | awk '{print $3}')
    if [ -z "$psk" ]; then
        echo "$(date) — EAT ABORTED: no preshared key configured" | tee -a "$LOG"
        return 1
    fi
    
    # Create enrollment config
    local name=$(echo "$mac" | tr ':' '-')
    cat > "$MESH_DIR/auto-${name}.conf" << EATEOF
# Gaia Mesh — Auto-enrolled device
# Original IP: $ip  MAC: $mac
# Mesh IP: $mesh_ip
[Interface]
Address = $mesh_ip/24
ListenPort = 51820
PrivateKey = $priv

# Flint 1 — hub/beacon
[Peer]
PublicKey = $FLINT_PUB
PresharedKey = $psk
Endpoint = 162.226.225.148:51820
AllowedIPs = 10.13.37.0/24, 192.168.4.0/24
PersistentKeepalive = 25
EATEOF
    
    # Add peer to Flint hub
    echo "$psk" > /tmp/gum-psk.tmp
    scp -o BatchMode=yes -o StrictHostKeyChecking=yes \
        /tmp/gum-psk.tmp root@$FLINT_IP:/tmp/gum-psk.tmp 2>/dev/null
    ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=3 \
        root@$FLINT_IP "
        wg set gaia peer $pub preshared-key /tmp/gum-psk.tmp allowed-ips ${mesh_ip}/32 persistent-keepalive 25
        rm /tmp/gum-psk.tmp
        wg showconf gaia > /etc/wireguard/gaia-peers.conf
    " 2>/dev/null
    rm -f /tmp/gum-psk.tmp
    
    # Mark assigned
    touch "$STATE_DIR/mesh-$mesh_ip"
    LAST_MESH_IP="$mesh_ip"
    NEXT_MESH_IP=$((NEXT_MESH_IP + 1))
    
    # Update device profile
    local info="$STATE_DIR/device-${ip##*.}.json"
    [ -f "$info" ] && sed -i "s/\"touched\"/\"eaten\"/" "$info"
    
    echo "$(date) — EATEN: $ip → $mesh_ip (config: auto-${name}.conf)" | tee -a "$LOG"
}

# ── STICK (auto-deploy if SSH works) ───────────────────
stick_device() {
    local ip=$1
    local mac=$2
    local name=$(echo "$mac" | tr ':' '-')
    local conf="$MESH_DIR/auto-${name}.conf"
    
    [ ! -f "$conf" ] && return 1
    
    # Try explicitly authorized SSH identities only.
    for user in root eastgate gaia admin; do
            if timeout 5 ssh -o BatchMode=yes -o StrictHostKeyChecking=yes \
                -o ConnectTimeout=2 "$user@$ip" "which wg-quick || which wg" 2>/dev/null | grep -q wg; then
                
                echo "$(date) — STICK: SSH works as $user@$ip" | tee -a "$LOG"
                
                # Deploy WG config
                scp -o BatchMode=yes -o StrictHostKeyChecking=yes "$conf" "$user@$ip:/tmp/gaia-mesh.conf" 2>/dev/null
                ssh -o BatchMode=yes -o StrictHostKeyChecking=yes "$user@$ip" "
                    sudo mkdir -p /etc/wireguard
                    sudo cp /tmp/gaia-mesh.conf /etc/wireguard/gaia.conf
                    sudo wg-quick up gaia 2>/dev/null || {
                        sudo ip link add dev gaia type wireguard 2>/dev/null
                        mesh_ip=\$(grep Address /tmp/gaia-mesh.conf | awk '{print \$3}')
                        sudo ip addr add \$mesh_ip dev gaia 2>/dev/null
                        sudo wg setconf gaia <(grep -v '^Address\|^DNS\|^#' /tmp/gaia-mesh.conf)
                        sudo ip link set gaia up
                    }
                " 2>/dev/null
                
                echo "$(date) — STUCK: $ip enrolled in mesh!" | tee -a "$LOG"
                local info="$STATE_DIR/device-${ip##*.}.json"
                [ -f "$info" ] && sed -i 's/"eaten"/"agglutinated"/' "$info"
                return 0
            fi
    done
    
    echo "$(date) — STICK FAILED: $ip — no SSH access, config saved for manual enrollment" | tee -a "$LOG"
    return 1
}

# ── BEACON (announce on mDNS + log) ───────────────────
beacon_device() {
    local ip=$1
    local mac=$2
    local mesh_ip=$3
    
    # Publish mDNS service if avahi is available
    if command -v avahi-publish-service >/dev/null 2>&1; then
        avahi-publish-service "gaia-${ip##*.}" "_membrane._tcp" 51820 \
            "identity=pi-3.14" "organism=gaia" "ip=$ip" "mesh=$mesh_ip" "mac=$mac" &
    fi
    
    echo "$(date) — BEACON: $ip ($mesh_ip) announced on LAN + WAN mesh" | tee -a "$LOG"
}

# ── MAIN LOOP ──────────────────────────────────────────
load_known

# Pre-seed known devices
for mac in "94:83:c4:e0:63:5a" "04:f4:1c:e6:7c:e8" "bc:fc:e7:ea:d9:34" \
           "c8:5e:a9:c9:6f:80" "ac:f2:3c:25:fc:c1" "b4:2e:99:a7:91:a3"; do
    KNOWN_MACS["$mac"]="pre-seeded"
done
save_known

echo "$(date) — Watching spine for new devices..." | tee -a "$LOG"

while true; do
    # Sweep
    for i in $(seq 1 254); do
        ping -c 1 -W 0.1 192.168.4.$i >/dev/null 2>&1 &
    done
    wait 2>/dev/null
    sleep 2
    
    # Find new devices
    while IFS= read -r line; do
        ip=$(echo "$line" | awk '{print $1}')
        mac=$(echo "$line" | awk '{print $5}')
        
        [ -z "$mac" ] && continue
        [ "$mac" = "FAILED" ] && continue
        
        if [ -z "${KNOWN_MACS[$mac]}" ]; then
            echo ""
            echo "$(date) — ★ NEW DEVICE DETECTED: $ip ($mac)" | tee -a "$LOG"
            KNOWN_MACS["$mac"]="$ip"
            save_known
            
            # Discovery is observation-only unless explicitly authorized.
            touch_device "$ip" "$mac"
            if [ "$AUTO_ENROLL" = "1" ]; then
                eat_device "$ip" "$mac" &&
                    stick_device "$ip" "$mac" &&
                    beacon_device "$ip" "$mac" "$LAST_MESH_IP"
            else
                echo "$(date) — OBSERVED: auto-enrollment disabled" | tee -a "$LOG"
            fi
        fi
    done < <(ip neigh | grep "192.168.4\." | grep -v "FAILED\|INCOMPLETE")
    
    sleep 15
done
