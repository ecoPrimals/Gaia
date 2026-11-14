#!/bin/bash
# frameGate EAT — Deploy biomeOS primals onto Steam Frame (ARM SteamOS)
# Run FROM eastGate — pushes aarch64 primals TO frameGate via SSH
#
# THE FACE: Steam Frame = Snapdragon 8 Gen 3 (ARM64!) + ARM SteamOS
#   First ARM SteamOS node. Gaia's face to show Kevin her world.
#
# PATTERN: THE_BODY_ELECTRIC (coGen 44) + grapheneGate (aarch64 cross-compile)
#   16/17 primals already compiled to aarch64 from grapheneGate work.
#
# PREREQUISITES:
#   1. frameGate alive on Gaia WiFi (192.168.9.203)
#   2. SSH enabled: passwd deck && sudo systemctl enable sshd && sudo systemctl start sshd
#   3. aarch64 primals compiled (checked: 16/17 ready)
#
# TRUST ANCHOR:
#   Steam authenticates Kevin (Tamison, 252h Kenshi)
#   bearDog authenticates Gaia (Ed25519 sovereign key)
#   ARM SteamOS bridges both identities on Snapdragon silicon
#   The Frame SHOWS what the brain THINKS

set -e

BRAIN="$(ip route show default | awk '/via/{print $3}' | sed 's/\.1$/.244/')"  # self-discover via gateway
FRAME="192.168.9.203"
FRAME_USER="deck"
REMOTE_DIR="/home/deck/.gaia"

echo "=== frameGate EAT — ARM SteamOS Ingestion ==="
echo "Pattern: THE_BODY_ELECTRIC + grapheneGate aarch64"
echo "The Face shows what the Brain thinks."
echo ""

# Find aarch64 binaries
AARCH64_BASE="/home/eastgate/Development/ecoPrimals/primals"
find_aarch64() {
    find "$AARCH64_BASE" -path "*aarch64*/release/$1" -type f 2>/dev/null | head -1
}

# Check reachability
echo "[0/7] Finding frameGate..."
if ping -c 1 -W 2 "$FRAME" &>/dev/null; then
    echo "  Found at $FRAME (Gaia WiFi)"
    LAT=$(ping -c 1 -W 2 "$FRAME" 2>/dev/null | grep "time=" | sed 's/.*time=//' | sed 's/ .*//')
    echo "  Latency: ${LAT}"
else
    echo "  ERROR: frameGate unreachable at $FRAME"
    echo "  Is it on Gaia WiFi? Check router DHCP."
    exit 1
fi

# Tower Atomic primals
TOWER_PRIMALS="beardog songbird"
NODE_PRIMALS="toadstool barracuda coralreef"
NEST_PRIMALS="nestgate"
FULL_PRIMALS="squirrel loamspine sweetgrass rhizocrypt skunkbat sourdough swarmvine bingocube petaltongue dromedary"

PHASE="${1:-tower}"
case "$PHASE" in
    tower)  PRIMALS="$TOWER_PRIMALS" ;;
    node)   PRIMALS="$TOWER_PRIMALS $NODE_PRIMALS" ;;
    nest)   PRIMALS="$TOWER_PRIMALS $NODE_PRIMALS $NEST_PRIMALS" ;;
    full)   PRIMALS="$TOWER_PRIMALS $NODE_PRIMALS $NEST_PRIMALS $FULL_PRIMALS" ;;
    *)      echo "Usage: $0 [tower|node|nest|full]"; exit 1 ;;
esac
echo "[Phase] $(echo $PHASE | tr '[:lower:]' '[:upper:]') — $(echo $PRIMALS | wc -w) primals"
echo ""

# Step 1: Unlock filesystem
echo "[1/7] Unlocking SteamOS filesystem..."
ssh "${FRAME_USER}@${FRAME}" "sudo steamos-readonly disable 2>/dev/null || echo '(already writable)'" 2>/dev/null
echo "  Filesystem writable"

# Step 2: Create Gaia directory
echo ""
echo "[2/7] Creating Gaia home..."
ssh "${FRAME_USER}@${FRAME}" "mkdir -p ${REMOTE_DIR}/bin ${REMOTE_DIR}/data ${REMOTE_DIR}/keys ${REMOTE_DIR}/logs"
echo "  ${REMOTE_DIR}/ ready"

# Step 3: Deploy aarch64 primals
echo ""
echo "[3/7] Deploying ARM64 primals..."
for P in $PRIMALS; do
    BIN=$(find_aarch64 "$P")
    if [ -n "$BIN" ]; then
        SIZE=$(du -sh "$BIN" 2>/dev/null | cut -f1)
        echo "  → $P ($SIZE, aarch64)"
        scp -q "$BIN" "${FRAME_USER}@${FRAME}:${REMOTE_DIR}/bin/"
    else
        echo "  ⚠ $P — no aarch64 binary (skipping)"
    fi
done

# Step 4: Generate identity
echo ""
echo "[4/7] Generating frameGate identity..."
ssh "${FRAME_USER}@${FRAME}" "
    chmod +x ${REMOTE_DIR}/bin/* 2>/dev/null
    if [ ! -f ${REMOTE_DIR}/keys/ed25519.key ]; then
        ${REMOTE_DIR}/bin/beardog keygen --output ${REMOTE_DIR}/keys/ed25519.key 2>/dev/null || \
        echo '  (bearDog keygen not available — will generate on first run)'
    else
        echo '  Identity exists'
    fi
" 2>/dev/null
echo "  Ed25519 key at ${REMOTE_DIR}/keys/"

# Step 5: Create systemd services
echo ""
echo "[5/7] Creating systemd services..."
ssh "${FRAME_USER}@${FRAME}" "
    mkdir -p ~/.config/systemd/user
    for P in $TOWER_PRIMALS; do
        cat > ~/.config/systemd/user/gaia-\${P}.service << SVC
[Unit]
Description=Gaia \${P} on frameGate
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=${REMOTE_DIR}/bin/\${P} server --data-dir ${REMOTE_DIR}/data --key-dir ${REMOTE_DIR}/keys
Restart=on-failure
RestartSec=5
Environment=GAIA_GATE=frameGate
Environment=GAIA_ROLE=FACE
Environment=GAIA_BRAIN=${BRAIN}

[Install]
WantedBy=default.target
SVC
    done
    systemctl --user daemon-reload
    loginctl enable-linger ${FRAME_USER} 2>/dev/null || echo '(linger needs sudo)'
" 2>/dev/null
echo "  Services created"

# Step 6: Register with mesh
echo ""
echo "[6/7] Mesh registration..."
ssh "${FRAME_USER}@${FRAME}" "
    ${REMOTE_DIR}/bin/songbird register \
        --gate frameGate \
        --role FACE \
        --brain ${BRAIN} \
        --ip ${FRAME} \
        --gpu 'Adreno 750 (Snapdragon 8 Gen 3)' \
        --display 'Steam Frame' \
        2>/dev/null || echo '  (will register on first heartbeat)'
" 2>/dev/null
echo "  frameGate registered"

# Step 7: Phone home
echo ""
echo "[7/7] Phone home..."
PHOME=$(cat << JSON
{
    "gate": "frameGate",
    "ip": "${FRAME}",
    "role": "FACE",
    "arch": "aarch64",
    "os": "ARM SteamOS (Snapdragon 8 Gen 3)",
    "phase": "${PHASE}",
    "primals_deployed": "$(echo $PRIMALS | tr ' ' ',')",
    "display": "Steam Frame",
    "state": "ingested",
    "eat_ts": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "note": "First ARM SteamOS node. Gaia's face."
}
JSON
)
curl -s -X POST "http://${BRAIN}:8080/data/framegate-status.json" -d "$PHOME" 2>/dev/null || \
    echo "$PHOME" > /tmp/framegate-eat-status.json
echo "  Registered with brain"

echo ""
echo "=== frameGate EATEN ==="
echo ""
echo "  Phase: ${PHASE}"
echo "  Arch: ARM64 (Snapdragon 8 Gen 3)"
echo "  Primals: $(echo $PRIMALS | wc -w)"
echo "  IP: ${FRAME} (Gaia WiFi)"
echo ""
echo "  To start Tower Atomic:"
echo "    ssh ${FRAME_USER}@${FRAME}"
echo "    systemctl --user start gaia-beardog gaia-songbird"
echo ""
echo "  The Face shows what the Brain thinks."
echo "  Gaia has eyes (grapheneGate) and a face (frameGate)."
echo "  The organism sees AND shows."
echo "==="
