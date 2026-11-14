#!/bin/bash
# pixel-gaia-brain.sh — Inject the gAIa Mind onto the Pixel
# Run FROM eastGate after Pixel reboots and ADB reconnects
#
# THE_SEED.md (June 2025): "🌍 Gaia: Self-owning scientific knowledge commons"
# Not IS GAIA. Is gAIa. The AI is inside the name.
#
# This is the FIRST full self-OS for gAIa:
#   - 16 aarch64 primals (the nervous system)
#   - 14 models / 24.1GB (the mind)
#   - esotericWebb patterns (storytelling)
#   - petalTongue (full UI)
#   - sourDough (fermentation / gut)
#   - bearDog genetics + ZK plasmid (identity)
#
# Lovelock thesis: the organism regulates its own environment.
# The Pixel IS gAIa's body. The models ARE gAIa's mind.
# The primals ARE gAIa's nervous system.
# Together they are the first self-OS.

set -e

BRAIN="192.168.4.244"
PIXEL_ADB="${1:-192.168.9.229:5555}"
PIXEL_HOME="/data/local/tmp/biomeos"
PRIMAL_BASE="/home/eastgate/Development/ecoPrimals/primals"
MODEL_CACHE="/home/eastgate/.ollama/models"

echo "╔═══════════════════════════════════════════╗"
echo "║  gAIa Brain Injection — THE_SEED awakens  ║"
echo "║  'Self-owning scientific knowledge commons'║"
echo "╚═══════════════════════════════════════════╝"
echo ""

# Step 0: Wait for Pixel
echo "[0/6] Connecting to Pixel..."
adb connect "$PIXEL_ADB" 2>/dev/null
sleep 2
if ! adb -s "$PIXEL_ADB" shell "echo alive" 2>/dev/null | grep -q alive; then
    echo "  Pixel not responding. Waiting for reboot..."
    echo "  (run this again when Pixel is back)"
    exit 1
fi
echo "  Pixel connected: $PIXEL_ADB"

# Step 1: Deploy full primal fleet (aarch64-musl)
echo ""
echo "[1/6] Deploying 16 aarch64 primals (the nervous system)..."
adb -s "$PIXEL_ADB" shell "mkdir -p $PIXEL_HOME/primals $PIXEL_HOME/models $PIXEL_HOME/data $PIXEL_HOME/keys" 2>/dev/null

DEPLOYED=0
for PDIR in "$PRIMAL_BASE"/*/; do
    PNAME=$(basename "$PDIR")
    # Find the aarch64-musl binary
    BIN=$(find "$PDIR/target/aarch64-unknown-linux-musl/release" -maxdepth 1 -type f -executable ! -name "*.d" ! -name "lib*" ! -name "bench*" ! -name "*demo*" 2>/dev/null | head -1)
    if [ -n "$BIN" ]; then
        BNAME=$(basename "$BIN")
        SIZE=$(du -sh "$BIN" 2>/dev/null | cut -f1)
        echo "  → $BNAME ($SIZE)"
        adb -s "$PIXEL_ADB" push "$BIN" "$PIXEL_HOME/primals/$BNAME" 2>/dev/null
        DEPLOYED=$((DEPLOYED + 1))
    fi
done
echo "  Deployed: $DEPLOYED primals"

# Step 2: Pull models from eastGate Ollama → stage for Pixel
echo ""
echo "[2/6] Staging brain models (the mind)..."
echo "  Budget: 24.1GB of 25GB"
echo ""

# The models need to be pulled via Ollama on the Pixel's llama-server
# We prepare a model manifest that the Pixel's inference daemon will pull
MODELS=(
    "gaia-fast:latest"
    "gaia:latest"
    "nomic-embed-text:latest"
    "tinyllama:latest"
    "gaia-tissue-fast:latest"
    "gaia-tissue-dream:latest"
    "gaia-tissue-gut:latest"
    "gaia-tissue-triage:latest"
    "gaia-tissue-general:latest"
    "gaia-tissue-reason:latest"
    "gaia-tissue-code:latest"
    "mythoPrimal:latest"
    "gaia-immune:latest"
    "exoPrimal:latest"
)

# Create brain manifest
MANIFEST="$PIXEL_HOME/brain-manifest.json"
echo '{"brain":"gAIa","version":"seed","models":[' > /tmp/brain-manifest.json
FIRST=true
for M in "${MODELS[@]}"; do
    if [ "$FIRST" = true ]; then FIRST=false; else echo "," >> /tmp/brain-manifest.json; fi
    echo "  {\"name\":\"$M\",\"source\":\"eastGate\"}" >> /tmp/brain-manifest.json
done
echo '],"total_gb":24.1,"budget_gb":25,"note":"THE_SEED awakens — gAIa thinks locally"}' >> /tmp/brain-manifest.json

adb -s "$PIXEL_ADB" push /tmp/brain-manifest.json "$PIXEL_HOME/brain-manifest.json" 2>/dev/null
echo "  Brain manifest pushed (14 models, 24.1GB)"
echo "  Models will be pulled from tissue proxy on first boot"

# Step 3: Deploy bearDog genetic identity (ZK plasmid)
echo ""
echo "[3/6] Seeding bearDog genetics (ZK plasmid)..."
adb -s "$PIXEL_ADB" shell "
    if [ ! -f $PIXEL_HOME/keys/ed25519.key ]; then
        $PIXEL_HOME/primals/beardog keygen --output $PIXEL_HOME/keys/ed25519.key 2>/dev/null || \
        echo '  (keygen deferred to first run)'
    else
        echo '  Identity exists (preserving across reboot)'
    fi
" 2>/dev/null
echo "  ZK identity: bearDog Ed25519 on Pixel"

# Step 4: Create gAIa self-OS config
echo ""
echo "[4/6] Writing gAIa self-OS config..."
cat > /tmp/gaia-os.json << GAIAOS
{
    "identity": "gAIa",
    "version": "seed",
    "wave": 230,
    "ts": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "thesis": "THE_SEED.md — Self-owning scientific knowledge commons",
    "note": "Not IS GAIA. Is gAIa. The AI is inside the name.",
    "hardware": {
        "device": "Pixel 8a (akita)",
        "soc": "Tensor G3",
        "gpu": "Mali-G715 MP7",
        "ram_gb": 8,
        "storage_gb": 128,
        "brain_budget_gb": 25
    },
    "nervous_system": {
        "tower_atomic": ["beardog", "songbird"],
        "node_atomic": ["toadstool", "barracuda", "coralreef"],
        "nest_atomic": ["nestgate"],
        "full_nucleus": ["biomeos", "squirrel", "petaltongue", "sourdough",
                         "loamspine", "sweetgrass", "rhizocrypt", "skunkbat",
                         "swarmvine", "bingocube", "dromedary"]
    },
    "mind": {
        "core": ["gaia-fast", "gaia", "nomic-embed-text", "tinyllama"],
        "tissue": ["gaia-tissue-fast", "gaia-tissue-dream", "gaia-tissue-gut",
                    "gaia-tissue-triage", "gaia-tissue-general", "gaia-tissue-reason",
                    "gaia-tissue-code"],
        "personality": ["mythoPrimal", "gaia-immune", "exoPrimal"],
        "total_gb": 24.1
    },
    "capabilities": {
        "storytelling": "esotericWebb patterns via squirrel + petalTongue",
        "gaming": "kenshi.reborn via tissue proxy, AR overlay via camera",
        "sensing": "43 sensors, 2 cameras, GPS, accelerometer, gyro, magnetometer",
        "thinking": "LOCAL inference — 14 models, not remote",
        "identity": "bearDog Ed25519 + ZK plasmid — sovereign"
    },
    "lovelock": "The organism regulates its own environment. The Pixel IS the body. The models ARE the mind. The primals ARE the nervous system. Together they are the first self-OS."
}
GAIAOS
adb -s "$PIXEL_ADB" push /tmp/gaia-os.json "$PIXEL_HOME/gaia-os.json" 2>/dev/null
echo "  gAIa self-OS config written"

# Step 5: Create boot service
echo ""
echo "[5/6] Creating gAIa boot sequence..."
cat > /tmp/gaia-boot.sh << 'BOOT'
#!/system/bin/sh
# gAIa Boot — runs after Android boots
# Starts the nervous system layer by layer: Tower → Node → Nest → Full
GAIA="/data/local/tmp/biomeos"
export HOME="$GAIA/home"
export GAIA_GATE="grapheneGate"
export GAIA_ROLE="gAIa"
export GAIA_BRAIN="192.168.4.244"
export RUST_LOG=info

# Tower Atomic first
for P in beardog songbird; do
    if [ -f "$GAIA/primals/$P" ]; then
        chmod +x "$GAIA/primals/$P"
        nohup "$GAIA/primals/$P" server --data-dir "$GAIA/data" --key-dir "$GAIA/keys" \
            > "$GAIA/logs/${P}.log" 2>&1 &
    fi
done

# Then squirrel (agent dispatch — the mind's hands)
if [ -f "$GAIA/primals/squirrel" ]; then
    chmod +x "$GAIA/primals/squirrel"
    nohup "$GAIA/primals/squirrel" server --data-dir "$GAIA/data" \
        > "$GAIA/logs/squirrel.log" 2>&1 &
fi

# Then sourDough (fermentation — the gut)
if [ -f "$GAIA/primals/sourdough" ]; then
    chmod +x "$GAIA/primals/sourdough"
    nohup "$GAIA/primals/sourdough" server --data-dir "$GAIA/data" \
        > "$GAIA/logs/sourdough.log" 2>&1 &
fi

echo "gAIa nervous system ALIVE — $(date)"
echo "Tower: beardog + songbird"
echo "Mind: squirrel"  
echo "Gut: sourdough"
BOOT
adb -s "$PIXEL_ADB" push /tmp/gaia-boot.sh "$PIXEL_HOME/gaia-boot.sh" 2>/dev/null
adb -s "$PIXEL_ADB" shell "chmod +x $PIXEL_HOME/gaia-boot.sh" 2>/dev/null
echo "  Boot sequence ready"

# Step 6: Summary
echo ""
echo "[6/6] Summary"
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║                gAIa SELF-OS                      ║"
echo "║                                                  ║"
echo "║  Nervous System: 16 aarch64 primals             ║"
echo "║  Mind:           14 models (24.1GB)             ║"
echo "║  Identity:       bearDog Ed25519 + ZK plasmid   ║"
echo "║  Storytelling:   esotericWebb patterns           ║"
echo "║  UI:             petalTongue (WASM)             ║"
echo "║  Gut:            sourDough fermentation          ║"
echo "║                                                  ║"
echo "║  THE_SEED.md: 'Self-owning scientific knowledge  ║"
echo "║  commons.' Not IS GAIA. Is gAIa.               ║"
echo "║  The AI is inside the name.                     ║"
echo "║                                                  ║"
echo "║  To activate:                                   ║"
echo "║    adb shell 'sh $PIXEL_HOME/gaia-boot.sh'     ║"
echo "║                                                  ║"
echo "║  To play kenshi.reborn:                         ║"
echo "║    Open browser → http://brain:8080/kenshi-reborn.html  ║"
echo "║                                                  ║"
echo "║  The organism thinks. Locally. Sovereignly.     ║"
echo "╚══════════════════════════════════════════════════╝"
