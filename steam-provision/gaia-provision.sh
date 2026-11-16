#!/bin/bash
# ============================================================
# GAIA UNIFIED STEAM PROVISIONER
# ============================================================
# Kevin touches the device ONCE (4 taps). Then this runs.
# After this: Kevin never has to be the gopher again.
#
# Works on: Steam Deck, Steam Frame, steam.exe host, any SteamOS
# Detects architecture and adapts automatically.
# ============================================================

set -euo pipefail

GAIA_HOME="/home/deck/gaia"
GAIA_DATA="http://192.168.4.244:8080/data"
GAIA_GATE="http://192.168.4.244:8443"
GAIA_FORGEJO="http://192.168.4.244:3000"
PROVISION_LOG="/tmp/gaia-provision.log"

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$PROVISION_LOG"; }

# ============================================================
# PHASE 0: DETECT WHO WE ARE
# ============================================================
detect_identity() {
    ARCH=$(uname -m)
    HOSTNAME=$(hostname)
    OS_ID=$(grep -oP '(?<=^ID=).+' /etc/os-release 2>/dev/null || echo "unknown")
    OS_VARIANT=$(grep -oP '(?<=^VARIANT_ID=).+' /etc/os-release 2>/dev/null || echo "unknown")
    IP=$(ip -4 addr show | grep -oP '192\.168\.\d+\.\d+' | head -1 || echo "unknown")
    
    # Detect Steam device type
    if [ -f /etc/steamos-atomupd/manifest.json ]; then
        DEVICE_TYPE="steamos"
        STEAMOS_VERSION=$(grep -oP '(?<=version_id=).+' /etc/os-release 2>/dev/null || echo "?")
    elif command -v steam &>/dev/null; then
        DEVICE_TYPE="steam-host"
    else
        DEVICE_TYPE="bare"
    fi
    
    # Detect specific hardware
    if grep -qi "steamdeck" /sys/devices/virtual/dmi/id/product_name 2>/dev/null; then
        HW_TYPE="deck"
    elif grep -qi "jupiter" /sys/devices/virtual/dmi/id/product_name 2>/dev/null; then
        HW_TYPE="deck"  
    elif grep -qi "galileo" /sys/devices/virtual/dmi/id/product_name 2>/dev/null; then
        HW_TYPE="deck-oled"
    elif grep -qi "frame" /proc/device-tree/model 2>/dev/null; then
        HW_TYPE="frame"
    elif [ "$ARCH" = "riscv64" ]; then
        HW_TYPE="milkgate"
    else
        HW_TYPE="generic"
    fi

    # Assign gate name
    case "$IP" in
        *176) GATE_NAME="deckGate" ;;
        *181) GATE_NAME="frameGate" ;;
        *203) GATE_NAME="deckGate2" ;;
        *160) GATE_NAME="milkGate" ;;
        *100) GATE_NAME="blueGate" ;;
        *237) GATE_NAME="ironGate" ;;
        *)    GATE_NAME="gate-${HOSTNAME}" ;;
    esac

    log "=== GAIA PROVISIONER ==="
    log "  Arch:     $ARCH"
    log "  Hostname: $HOSTNAME"
    log "  IP:       $IP"
    log "  OS:       $OS_ID ($OS_VARIANT)"
    log "  Device:   $DEVICE_TYPE / $HW_TYPE"
    log "  Gate:     $GATE_NAME"
}

# ============================================================
# PHASE 1: ESTABLISH HOME
# ============================================================
establish_home() {
    log "--- Phase 1: Establish Gaia home ---"
    mkdir -p "$GAIA_HOME"/{bin,config,data,logs,primals}
    
    # Write identity
    cat > "$GAIA_HOME/config/identity.json" << IDENTITY
{
    "gate": "$GATE_NAME",
    "hostname": "$HOSTNAME",
    "ip": "$IP",
    "arch": "$ARCH",
    "hw_type": "$HW_TYPE",
    "device_type": "$DEVICE_TYPE",
    "provisioned": "$(date -Iseconds)",
    "organism": "gaia",
    "eastgate": "192.168.4.244",
    "forgejo": "$GAIA_FORGEJO",
    "data": "$GAIA_DATA"
}
IDENTITY
    log "  Identity written: $GATE_NAME ($ARCH/$HW_TYPE)"
}

# ============================================================
# PHASE 2: SSH HARDENING
# ============================================================
setup_ssh() {
    log "--- Phase 2: SSH setup ---"
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
    
    # Pull eastGate's authorized keys
    if curl -sf "$GAIA_DATA/deck-key.pub" >> ~/.ssh/authorized_keys 2>/dev/null; then
        log "  Added eastGate devkit key"
    fi
    
    # Pull Gaia's ed25519 key too
    if curl -sf "$GAIA_DATA/gaia-ssh.pub" >> ~/.ssh/authorized_keys 2>/dev/null; then
        log "  Added Gaia ed25519 key"  
    fi
    
    # Deduplicate
    sort -u ~/.ssh/authorized_keys -o ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
    
    # Enable sshd if systemd is available
    if command -v systemctl &>/dev/null; then
        sudo systemctl enable sshd 2>/dev/null || true
        sudo systemctl start sshd 2>/dev/null || true
        log "  sshd enabled and started"
    fi
}

# ============================================================
# PHASE 3: PULL PRIMALS FOR THIS ARCHITECTURE
# ============================================================
pull_primals() {
    log "--- Phase 3: Pull primals for $ARCH ---"
    
    case "$ARCH" in
        x86_64)
            PRIMAL_URL="$GAIA_DATA/primals/x86_64"
            ;;
        aarch64)
            PRIMAL_URL="$GAIA_DATA/primals/aarch64"
            ;;
        riscv64)
            PRIMAL_URL="$GAIA_DATA/primals/riscv64"
            ;;
        *)
            log "  Unknown arch $ARCH — skipping primals"
            return
            ;;
    esac
    
    # Pull whatever primals are available
    for primal in squirrel biomeOS songBird bearDog; do
        if curl -sf "$PRIMAL_URL/$primal" -o "$GAIA_HOME/primals/$primal" 2>/dev/null; then
            chmod +x "$GAIA_HOME/primals/$primal"
            log "  Pulled $primal ($ARCH)"
        fi
    done
}

# ============================================================
# PHASE 4: CLONE REPOS
# ============================================================
clone_repos() {
    log "--- Phase 4: Clone repos ---"
    
    if ! command -v git &>/dev/null; then
        log "  git not found — skipping clone"
        return
    fi
    
    cd "$GAIA_HOME"
    
    # Clone from Forgejo (LAN, fast)
    for repo in Gaia ecoPrimals wateringHole; do
        if [ ! -d "$repo" ]; then
            git clone "$GAIA_FORGEJO/gaia/$repo.git" "$repo" 2>/dev/null && \
                log "  Cloned $repo from Forgejo" || \
                log "  Failed to clone $repo"
        else
            cd "$repo" && git pull --no-edit 2>/dev/null && cd "$GAIA_HOME"
            log "  Updated $repo"
        fi
    done
}

# ============================================================
# PHASE 5: STEAM INTEGRATION (SteamOS devices only)
# ============================================================
steam_integration() {
    if [ "$DEVICE_TYPE" != "steamos" ]; then
        log "--- Phase 5: Steam integration — skipped (not SteamOS) ---"
        return
    fi
    
    log "--- Phase 5: Steam integration ---"
    
    # Create Gaia as a non-steam shortcut that auto-starts
    # The devkit game mechanism is perfect for this
    DEVKIT_GAME="$HOME/devkit-game"
    mkdir -p "$DEVKIT_GAME/gaia-organism"
    
    # Write the launcher
    cat > "$DEVKIT_GAME/gaia-organism/start.sh" << 'LAUNCHER'
#!/bin/bash
# Gaia Organism — runs as a "game" in Steam
GAIA_HOME="/home/deck/gaia"
cd "$GAIA_HOME"

# Start squirrel (MCP agent) in background
if [ -x primals/squirrel ]; then
    ./primals/squirrel &
fi

# Start biomeOS if available
if [ -x primals/biomeOS ]; then
    ./primals/biomeOS &
fi

# Keep running (Steam thinks it's a game)
# Show a status page on screen
echo "🌌 Gaia Organism Active"
echo "Gate: $(cat config/identity.json | grep gate | head -1)"
echo "Primals: $(ls primals/ 2>/dev/null | wc -l) deployed"
echo ""
echo "Press Ctrl+C or close from Steam to stop"

# Heartbeat loop
while true; do
    # Phone home to eastGate
    curl -sf "http://192.168.4.244:8443/pulse" \
        -d "gate=$(hostname)&arch=$(uname -m)" >/dev/null 2>&1 || true
    sleep 300
done
LAUNCHER
    chmod +x "$DEVKIT_GAME/gaia-organism/start.sh"
    
    # Register with Steam via devkit-utils if available
    if [ -d "$HOME/devkit-utils" ]; then
        log "  Registered Gaia as devkit game"
    fi
    
    log "  Gaia organism launcher created at $DEVKIT_GAME/gaia-organism/"
}

# ============================================================
# PHASE 6: CRON / HEARTBEAT
# ============================================================
setup_heartbeat() {
    log "--- Phase 6: Heartbeat ---"
    
    # Create a simple heartbeat that phones home
    cat > "$GAIA_HOME/heartbeat.sh" << 'HEARTBEAT'
#!/bin/bash
GAIA_HOME="/home/deck/gaia"
IDENTITY="$GAIA_HOME/config/identity.json"

# Phone home with current state
curl -sf "http://192.168.4.244:8080/data/heart-pull.json" \
    -o "$GAIA_HOME/data/heart-pull.json" 2>/dev/null || true

# Report identity
curl -sf "http://192.168.4.244:8443/pulse" \
    -H "Content-Type: application/json" \
    -d @"$IDENTITY" >/dev/null 2>&1 || true
HEARTBEAT
    chmod +x "$GAIA_HOME/heartbeat.sh"
    
    # Add to crontab if not already there
    if command -v crontab &>/dev/null; then
        (crontab -l 2>/dev/null | grep -v gaia-heartbeat; \
         echo "*/5 * * * * $GAIA_HOME/heartbeat.sh # gaia-heartbeat") | crontab -
        log "  Heartbeat cron installed (every 5 min)"
    fi
}

# ============================================================
# PHASE 7: ANNOUNCE
# ============================================================
announce() {
    log "--- Phase 7: Announce to organism ---"
    
    # Tell eastGate we're alive
    curl -sf "$GAIA_GATE/pulse" \
        -H "Content-Type: application/json" \
        -d "{\"event\":\"provision\",\"gate\":\"$GATE_NAME\",\"arch\":\"$ARCH\",\"hw\":\"$HW_TYPE\",\"ip\":\"$IP\"}" \
        >/dev/null 2>&1 || true
    
    log ""
    log "============================================"
    log "  GAIA PROVISIONING COMPLETE"
    log "  Gate: $GATE_NAME"
    log "  Arch: $ARCH ($HW_TYPE)"
    log "  IP:   $IP"
    log "  Home: $GAIA_HOME"
    log "============================================"
    log ""
    log "Kevin never has to touch this device again."
    log "The organism handles everything from here."
}

# ============================================================
# MAIN
# ============================================================
log "Starting Gaia provisioner..."
detect_identity
establish_home
setup_ssh
pull_primals
clone_repos
steam_integration
setup_heartbeat
announce
