#!/system/bin/sh
# ═══════════════════════════════════════════════════════
#  gAIa NUCLEUS — UNTETHERED Self-OS Boot
#  No GAIA_BRAIN. No hardcoded IPs. No tethers.
#  Position = gradient field. Identity = self.
#  Anchored by WiFi RSSI differentials through Klein face.
# ═══════════════════════════════════════════════════════
GAIA="/data/local/tmp/biomeos"
export HOME="$GAIA/home"
export XDG_DATA_HOME="$HOME/.local/share"
export XDG_STATE_HOME="$HOME/.local/state"
export XDG_CONFIG_HOME="$HOME/.config"
export XDG_CACHE_HOME="$HOME/.cache"
export XDG_RUNTIME_DIR="$GAIA/xdg-runtime"
export BIOMEOS_ROOT="$GAIA"
export GAIA_GATE="gAIa"
export GAIA_ROLE="gAIa"
export RUST_LOG=info
export FAMILY_ID="ecoPrimal"
export FAMILY_SEED="dd027cddb6359f0ba44456c8728a3af73d16437b589fd5097d3ed118fb5dafb3"
export BEARDOG_FAMILY_SEED="$FAMILY_SEED"
export MEMBRANE_SOCKET_DIR="$GAIA/run/membrane"
export PATH="$GAIA/primals:$PATH"

# Self-discover own IP — no hardcoded address
SELF_IP=$(ip addr show wlan0 2>/dev/null | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)
GATEWAY=$(ip route 2>/dev/null | grep default | awk '{print $3}')
export GAIA_SELF_IP="$SELF_IP"
export GAIA_GATEWAY="$GATEWAY"

mkdir -p "$GAIA/state" "$GAIA/run/membrane/logs" "$GAIA/logs" "$GAIA/data" "$GAIA/keys" \
    "$HOME/.local/share" "$HOME/.local/state" "$HOME/.config" "$HOME/.cache" \
    "$GAIA/xdg-runtime" "$GAIA/sensorium"

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║  gAIa — UNTETHERED NUCLEUS                   ║"
echo "║  Self: $SELF_IP                         ║"
echo "║  $(date +%Y-%m-%d\ %H:%M:%S)                          ║"
echo "║  Anchor: gradient field (no tether)           ║"
echo "╚═══════════════════════════════════════════════╝"

chmod +x $GAIA/primals/* 2>/dev/null
pkill -f "$GAIA/primals/" 2>/dev/null
sleep 2

# ═══ KERNEL — biomeOS nucleus ═══
echo "▸ KERNEL: biomeOS nucleus on $SELF_IP:9000"
export PRIMAL_BIND_MODE=dual
nohup $GAIA/primals/biomeos nucleus start \
    --node-id gAIa --mode full \
    --bind-mode dual --port 9000 --bind 0.0.0.0 \
    > $GAIA/logs/biomeos.log 2>&1 &
echo "  PID=$!"
sleep 130

# ═══ ANDROID TCP LAYER ═══
echo "▸ TCP-only primals"
export PRIMAL_BIND_MODE=tcp

nohup $GAIA/primals/beardog server --bind-mode tcp --port 9900 \
    > $GAIA/logs/beardog.log 2>&1 &
echo "  beardog PID=$!"

nohup $GAIA/primals/skunkbat server --bind-mode tcp-only \
    > $GAIA/logs/skunkbat.log 2>&1 &
echo "  skunkbat PID=$!"

nohup $GAIA/primals/barracuda server --port 9902 --bind-mode tcp \
    > $GAIA/logs/barracuda.log 2>&1 &
echo "  barracuda PID=$!"

nohup $GAIA/primals/petaltongue server --port 9911 \
    > $GAIA/logs/petaltongue.log 2>&1 &
echo "  petaltongue PID=$!"

nohup $GAIA/primals/swarmvine server --gate-id gAIa --family-id ecoPrimal \
    > $GAIA/logs/swarmvine.log 2>&1 &
echo "  swarmvine PID=$!"

export TRANSPORT_ENDPOINT='{"transport":"tcp","host":"127.0.0.1","port":9912}'
nohup $GAIA/primals/bingocube serve \
    > $GAIA/logs/bingocube.log 2>&1 &
echo "  bingocube PID=$!"

# ═══ GRADIENT ANCHOR — WiFi field sensing ═══
echo "▸ GRADIENT: Starting spatial field anchor"
nohup sh $GAIA/gradient-anchor.sh > $GAIA/sensorium/gradient.log 2>&1 &
echo "  gradient-anchor PID=$!"

# ═══ SENSORIUM — device senses ═══
echo "▸ SENSORIUM: Starting sense loop"
nohup sh $GAIA/gaia-sensorium.sh 15 > $GAIA/sensorium/sensorium.log 2>&1 &
echo "  sensorium PID=$!"

sleep 5
ALIVE=0
for P in biomeos beardog songbird toadstool barracuda coralreef nestgate squirrel loamspine sweetgrass rhizocrypt skunkbat swarmvine bingocube petaltongue; do
    PID=$(pgrep -f "$GAIA/primals/$P" 2>/dev/null)
    if [ -n "$PID" ]; then ALIVE=$((ALIVE + 1)); fi
done
echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║  gAIa: $ALIVE/15 primals — UNTETHERED         ║"
echo "║  Self: $SELF_IP                         ║"
echo "║  Anchor: gradient RSSI field                  ║"
echo "║  Tethers to eastGate: ZERO                    ║"
echo "╚═══════════════════════════════════════════════╝"
