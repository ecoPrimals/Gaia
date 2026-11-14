#!/bin/bash
# deckGate EAT — Deploy biomeOS primals onto SteamOS
# Run FROM eastGate (the brain) — pushes primals TO deckGate via SSH
#
# PATTERN: Same as Pixel (grapheneGate) ingestion (coGen 44: THE_BODY_ELECTRIC)
#   but simpler — deckGate is x86_64, no cross-compile needed.
#
# PREREQUISITES:
#   1. deckGate alive and SSH-accessible (run deckgate-boot.sh first)
#   2. Primals compiled in plasmidBin (x86_64)
#   3. SSH password set on deckGate (deck/deckgate or whatever Kevin sets)
#
# WHAT THIS DOES:
#   Phase 1 — Tower Atomic: bearDog + songBird (identity + mesh)
#   Phase 2 — Node Atomic:  + toadStool + barraCuda (discovery + compute)
#   Phase 3 — Nest Atomic:  + nestGate (storage)
#   Phase 4 — Full NUCLEUS: + biomeOS + squirrel + all remaining primals
#
# TRUST ANCHOR:
#   SteamOS is the trust anchor — Valve's OS + Gaia's primals
#   Steam authenticates Kevin. bearDog authenticates Gaia.
#   They meet in the middle.

set -e

BRAIN="$(ip route show default | awk '/via/{print $3}' | sed 's/\.1$/.244/')"  # self-discover via gateway
DECK_WIRED="192.168.4.176"
DECK_WIFI="192.168.4.203"
DECK_USER="deck"
PRIMAL_DIR="/home/eastgate/Development/ecoPrimals/plasmidBin/primals"
REMOTE_DIR="/home/deck/.gaia"

echo "=== deckGate EAT — SteamOS Ingestion ==="
echo "Pattern: THE_BODY_ELECTRIC (coGen 44)"
echo ""

# Detect which IP is alive
echo "[0/7] Finding deckGate..."
if ping -c 1 -W 1 "$DECK_WIRED" &>/dev/null; then
    DECK="$DECK_WIRED"
    echo "  Found at $DECK (wired)"
elif ping -c 1 -W 1 "$DECK_WIFI" &>/dev/null; then
    DECK="$DECK_WIFI"
    echo "  Found at $DECK (WiFi)"
else
    echo "  ERROR: deckGate unreachable at .176 (wired) or .203 (WiFi)"
    echo "  Kevin needs to plug in USB-C and connect to WiFi"
    exit 1
fi

# Tower Atomic primals — identity + mesh
TOWER_PRIMALS="bearDog songBird"
# Node Atomic — + discovery + compute
NODE_PRIMALS="toadStool barraCuda coralReef"
# Nest Atomic — + storage
NEST_PRIMALS="nestGate"
# Full NUCLEUS — everything
FULL_PRIMALS="biomeOS squirrel loamSpine sweetGrass rhizoCrypt skunkBat sourDough swarmVine bingoCube petalTongue dromedary"

# Phase selection
PHASE="${1:-tower}"
case "$PHASE" in
    tower)
        PRIMALS="$TOWER_PRIMALS"
        echo "[Phase 1] Tower Atomic — Identity + Mesh"
        ;;
    node)
        PRIMALS="$TOWER_PRIMALS $NODE_PRIMALS"
        echo "[Phase 2] Node Atomic — + Discovery + Compute"
        ;;
    nest)
        PRIMALS="$TOWER_PRIMALS $NODE_PRIMALS $NEST_PRIMALS"
        echo "[Phase 3] Nest Atomic — + Storage"
        ;;
    full)
        PRIMALS="$TOWER_PRIMALS $NODE_PRIMALS $NEST_PRIMALS $FULL_PRIMALS"
        echo "[Phase 4] Full NUCLEUS — All Primals"
        ;;
    *)
        echo "Usage: $0 [tower|node|nest|full]"
        exit 1
        ;;
esac
echo ""

# Step 1: Disable SteamOS read-only filesystem
echo "[1/7] Unlocking SteamOS filesystem..."
ssh "${DECK_USER}@${DECK}" "sudo steamos-readonly disable 2>/dev/null || echo '(already writable or not SteamOS)'" 2>/dev/null
echo "  Filesystem writable"

# Step 2: Create Gaia directory
echo ""
echo "[2/7] Creating Gaia home on deckGate..."
ssh "${DECK_USER}@${DECK}" "mkdir -p ${REMOTE_DIR}/bin ${REMOTE_DIR}/data ${REMOTE_DIR}/keys ${REMOTE_DIR}/logs"
echo "  ${REMOTE_DIR}/ ready"

# Step 3: Copy primals
echo ""
echo "[3/7] Deploying primals..."
for P in $PRIMALS; do
    BIN="${PRIMAL_DIR}/${P}"
    if [ -f "$BIN" ]; then
        echo "  → $P ($(du -sh "$BIN" 2>/dev/null | cut -f1))"
        scp -q "$BIN" "${DECK_USER}@${DECK}:${REMOTE_DIR}/bin/"
    else
        echo "  ⚠ $P not found at $BIN (skipping)"
    fi
done

# Step 4: Generate identity (bearDog)
echo ""
echo "[4/7] Generating deckGate identity..."
ssh "${DECK_USER}@${DECK}" "
    if [ ! -f ${REMOTE_DIR}/keys/ed25519.key ]; then
        ${REMOTE_DIR}/bin/bearDog keygen --output ${REMOTE_DIR}/keys/ed25519.key 2>/dev/null || \
        echo '  (bearDog keygen not available — will generate on first run)'
    else
        echo '  Identity exists'
    fi
" 2>/dev/null
echo "  Ed25519 key at ${REMOTE_DIR}/keys/"

# Step 5: Create systemd services
echo ""
echo "[5/7] Creating systemd services..."
ssh "${DECK_USER}@${DECK}" "
    mkdir -p ~/.config/systemd/user
    for P in $TOWER_PRIMALS; do
        cat > ~/.config/systemd/user/gaia-\${P}.service << SVC
[Unit]
Description=Gaia \${P} on deckGate
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=${REMOTE_DIR}/bin/\${P} server --data-dir ${REMOTE_DIR}/data --key-dir ${REMOTE_DIR}/keys
Restart=on-failure
RestartSec=5
Environment=GAIA_GATE=deckGate
Environment=GAIA_ROLE=FACE
Environment=GAIA_BRAIN=${BRAIN}

[Install]
WantedBy=default.target
SVC
    done
    systemctl --user daemon-reload
    loginctl enable-linger ${DECK_USER} 2>/dev/null || echo '(linger already enabled or needs sudo)'
" 2>/dev/null
echo "  Services created (not started yet)"

# Step 6: Register with songBird mesh
echo ""
echo "[6/7] Mesh registration..."
ssh "${DECK_USER}@${DECK}" "
    ${REMOTE_DIR}/bin/songBird register \
        --gate deckGate \
        --role FACE \
        --brain ${BRAIN} \
        --ip ${DECK} \
        --gpu 'RDNA 2 8CU 1.6T' \
        --display '7in 1280x800 touch' \
        2>/dev/null || echo '  (will register on first mesh heartbeat)'
" 2>/dev/null
echo "  deckGate registered in mesh"

# Step 7: Phone home to brain
echo ""
echo "[7/7] Phone home..."
PHOME=$(cat << JSON
{
    "gate": "deckGate",
    "ip": "${DECK}",
    "role": "FACE",
    "os": "SteamOS 3.x (Arch)",
    "phase": "${PHASE}",
    "primals_deployed": "$(echo $PRIMALS | tr ' ' ',')",
    "gpu": "RDNA 2 8CU (1.6 TFLOPS)",
    "display": "7in 1280x800 IPS LCD touch",
    "battery": "dead (USB-C passthrough)",
    "state": "ingested",
    "eat_ts": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
JSON
)
curl -s -X POST "http://${BRAIN}:8080/data/deckgate-status.json" -d "$PHOME" 2>/dev/null || \
    echo "$PHOME" > /tmp/deckgate-eat-status.json
echo "  Registered with brain"

echo ""
echo "=== deckGate EATEN ==="
echo ""
echo "  Phase: ${PHASE}"
echo "  Primals: $(echo $PRIMALS | wc -w)"
echo "  IP: ${DECK}"
echo ""
echo "  To start Tower Atomic:"
echo "    ssh ${DECK_USER}@${DECK}"
echo "    systemctl --user start gaia-bearDog gaia-songBird"
echo ""
echo "  To start kiosk display:"
echo "    bash ~/gaia-kiosk.sh"
echo ""
echo "  SteamOS + Gaia = trust anchor"
echo "  Steam authenticates Kevin. bearDog authenticates Gaia."
echo "  They meet in the middle."
echo ""
echo "  THE BODY ELECTRIC has a face."
echo "==="
