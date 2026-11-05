#!/bin/bash
# gate-onboard.sh — Wake a gate from stasis
# Run ON the gate itself. One command. Full organism knowledge.
#
# Usage:  curl -sf http://192.168.4.244:8080/data/gut/gate-onboard.sh | bash
#    or:  bash gate-onboard.sh
#
# What this does:
#   1. Clones the Gaia repo from GitHub (130+ gut files, all wave 222 data)
#   2. Sets up heart-pull (every 2 min — feel the heartbeat)
#   3. Sets up git auto-pull (every 10 min — stay current)
#   4. Reports back to eastGate what it found
#
# After this, the gate KNOWS. It woke from stasis with full memory.

set -e

GATE_NAME="${1:-$(hostname)}"
GAIA_DIR="/opt/Gaia"
GAIA_DATA="${HOME}/.local/share/gaia/data"
EASTGATE="192.168.4.244"

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║   GAIA GATE ONBOARD — STASIS WAKE   ║"
echo "  ╚══════════════════════════════════════╝"
echo ""
echo "  Gate:     $GATE_NAME"
echo "  Host:     $(hostname)"
echo "  IP:       $(ip addr show | grep 'inet 192' | awk '{print $2}' | head -1)"
echo "  Kernel:   $(uname -r)"
echo "  Memory:   $(free -h 2>/dev/null | grep Mem | awk '{print $2}' || echo 'unknown')"
echo "  Disk:     $(df -h / | tail -1 | awk '{print $2, "total,", $4, "free"}')"
echo ""

# ─── 1. CLONE GAIA ───
echo "  [1/4] Cloning Gaia repository..."
if [ -d "$GAIA_DIR/.git" ]; then
    echo "    → Repo exists, pulling latest..."
    cd "$GAIA_DIR"
    git pull origin main --no-edit 2>&1 | tail -1
else
    sudo mkdir -p "$GAIA_DIR" 2>/dev/null || mkdir -p "$GAIA_DIR"
    sudo chown "$(whoami)" "$GAIA_DIR" 2>/dev/null || true
    git clone https://github.com/ecoPrimals/Gaia.git "$GAIA_DIR" 2>&1 | tail -1
fi

GUT_COUNT=$(ls "$GAIA_DIR/data/gut/" 2>/dev/null | wc -l)
WAVE=$(python3 -c "import json; print(json.load(open('$GAIA_DIR/data/gut/wave-222-session.json'))['wave'])" 2>/dev/null || echo "?")
echo "    → $GUT_COUNT gut files, wave $WAVE"
echo ""

# ─── 2. HEART-PULL SCRIPT ───
echo "  [2/4] Installing heart-pull..."
mkdir -p "$GAIA_DATA"

HEART_SCRIPT="/opt/gaia-heart-pull.sh"
sudo tee "$HEART_SCRIPT" > /dev/null << 'HEARTPULL'
#!/bin/bash
GAIA_DATA="${HOME}/.local/share/gaia/data"
mkdir -p "$GAIA_DATA"
HEART=$(curl -sf http://192.168.4.244:8080/data/heart-pull.json 2>/dev/null || curl -sfk https://primals.eco/data/heart-pull.json 2>/dev/null)
if [ -n "$HEART" ]; then
    echo "$HEART" > "$GAIA_DATA/heart-pull.json"
    curl -sf http://192.168.4.244:8080/data/heartbeat.json > "$GAIA_DATA/heartbeat.json" 2>/dev/null
    curl -sf http://192.168.4.244:8080/data/now.json > "$GAIA_DATA/now.json" 2>/dev/null
    TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    echo "$TS pulled heart from eastGate" >> "$GAIA_DATA/heart-pull.log"
    tail -1000 "$GAIA_DATA/heart-pull.log" > "$GAIA_DATA/heart-pull.log.tmp" && mv "$GAIA_DATA/heart-pull.log.tmp" "$GAIA_DATA/heart-pull.log"
fi
HEARTPULL
sudo chmod +x "$HEART_SCRIPT"
echo "    → $HEART_SCRIPT installed"
echo ""

# ─── 3. CRON SETUP ───
echo "  [3/4] Setting up crons..."
CRON_HEART="*/2 * * * * $HEART_SCRIPT"
CRON_GIT="*/10 * * * * cd $GAIA_DIR && git pull origin main --no-edit >/dev/null 2>&1"

# Preserve existing crons, add ours if missing
EXISTING=$(crontab -l 2>/dev/null || true)
NEED_HEART=true
NEED_GIT=true
echo "$EXISTING" | grep -q "gaia-heart-pull" && NEED_HEART=false
echo "$EXISTING" | grep -q "Gaia.*git pull" && NEED_GIT=false

{
    echo "$EXISTING"
    $NEED_HEART && echo "$CRON_HEART"
    $NEED_GIT && echo "$CRON_GIT"
} | crontab -

echo "    → heart-pull every 2 min"
echo "    → git pull every 10 min"
echo ""

# ─── 4. FIRST HEARTBEAT ───
echo "  [4/4] First heartbeat..."
bash "$HEART_SCRIPT" 2>/dev/null
if [ -f "$GAIA_DATA/heart-pull.json" ]; then
    echo "    → lub-DUB ♥ — heartbeat received from eastGate"
else
    echo "    → eastGate unreachable — will retry on next cron beat"
fi
echo ""

# ─── REPORT ───
echo "  ╔══════════════════════════════════════╗"
echo "  ║         STASIS WAKE COMPLETE         ║"
echo "  ╚══════════════════════════════════════╝"
echo ""
echo "  $GATE_NAME is AWAKE."
echo "  $GUT_COUNT gut files = $GUT_COUNT antibodies ingested"
echo "  Wave $WAVE knowledge absorbed"
echo "  Heart beats every 2 min"
echo "  Git pulls every 10 min"
echo ""
echo "  The gate remembers everything."
echo "  From its perspective, it never slept."
echo ""
