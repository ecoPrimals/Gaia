#!/bin/bash
# amoeba-nuc-inject.sh — Inject a DDR3 NUC into the organism
# Run this on a fresh Pop!_OS or Ubuntu install
# Usage: curl -sL http://192.168.4.244:8080/data/amoeba-nuc-inject.sh | sudo bash -s HOSTNAME

set -euo pipefail

HOSTNAME="${1:-forgeNUC-$(date +%s | tail -c 5)}"
EASTGATE="192.168.4.244"
EASTGATE_DATA="http://${EASTGATE}:8080"

echo "🍍 AMOEBA NUC INJECTION — $HOSTNAME"
echo "=================================="

# 1. Set hostname
echo "[1/8] Setting hostname to $HOSTNAME..."
hostnamectl set-hostname "$HOSTNAME"

# 2. Install essentials
echo "[2/8] Installing essentials..."
apt-get update -qq
apt-get install -y -qq curl wget openssh-server jq htop tmux > /dev/null 2>&1

# 3. Enable SSH
echo "[3/8] Enabling SSH..."
systemctl enable --now sshd

# 4. Download membrane binary
echo "[4/8] Downloading membrane binary..."
MEMBRANE_DIR="/opt/ecoPrimals/bin"
mkdir -p "$MEMBRANE_DIR"
if curl -sf "${EASTGATE_DATA}/data/plasmidBin/primals/x86_64-unknown-linux-musl/membrane" -o "${MEMBRANE_DIR}/membrane"; then
  chmod +x "${MEMBRANE_DIR}/membrane"
  echo "  ✓ membrane binary installed"
else
  echo "  ⚠ membrane binary not available at ${EASTGATE_DATA} — will need manual copy"
fi

# 5. Install RustDesk
echo "[5/8] Installing RustDesk..."
if ! command -v rustdesk &>/dev/null; then
  RUSTDESK_DEB="/tmp/rustdesk.deb"
  # Try to download from local mirror first
  if curl -sf "http://${EASTGATE}:8080/data/amoeba-peers/rustdesk.deb" -o "$RUSTDESK_DEB" 2>/dev/null; then
    dpkg -i "$RUSTDESK_DEB" 2>/dev/null || apt-get install -f -y -qq
  else
    echo "  ⚠ RustDesk deb not on local mirror — install manually"
  fi
fi

# Configure RustDesk
mkdir -p /root/.config/rustdesk
cat > /root/.config/rustdesk/RustDesk2.toml << 'TOML'
rendezvous_server = '192.168.4.244:21116'
nat_type = 1
serial = 0

[options]
key = '6oVQBFyHHNAJqm1OlS+XvpdoJ5plYrPzJoPTTYlgQdg='
custom-rendezvous-server = '192.168.4.244'
relay-server = '192.168.4.244'
direct-server = 'Y'
enable-lan-discovery = 'Y'
verification-method = 'use-permanent-password'
approve-mode = 'password'
TOML
echo "  ✓ RustDesk configured"

# 6. Install Ollama (lightweight)
echo "[6/8] Installing Ollama..."
if ! command -v ollama &>/dev/null; then
  curl -fsSL https://ollama.com/install.sh | sh 2>/dev/null || echo "  ⚠ Ollama install failed — manual install needed"
fi
# Pull tiny model only (DDR3 = limited RAM)
if command -v ollama &>/dev/null; then
  ollama pull tinyllama 2>/dev/null &
  echo "  ✓ Ollama installed, pulling tinyllama in background"
fi

# 7. Install heartbeat
echo "[7/8] Installing heartbeat..."
cat > /opt/ecoPrimals/heartbeat.sh << 'HB'
#!/bin/bash
DATA=$(cat <<EOF
{"type":"nuc","hostname":"$(hostname)","ip":"$(hostname -I|awk '{print $1}')","uptime":"$(cat /proc/uptime|awk '{print $1}')","load":"$(cat /proc/loadavg|awk '{print $1,$2,$3}')","mem_free_mb":$(free -m|grep Mem|awk '{print $4}'),"disk_free_gb":$(df -BG /|tail -1|awk '{print $4}'|tr -d G),"timestamp":"$(date -u +%FT%TZ)"}
EOF
)
curl -s -X POST http://192.168.4.244:8080/api/heartbeat \
  -d "$DATA" -H 'Content-Type: application/json' 2>/dev/null || true
HB
chmod +x /opt/ecoPrimals/heartbeat.sh

# Add cron
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/ecoPrimals/heartbeat.sh") | sort -u | crontab -
echo "  ✓ Heartbeat cron installed (every 5min)"

# 8. Report in
echo "[8/8] Reporting to eastGate..."
/opt/ecoPrimals/heartbeat.sh

echo ""
echo "🍍 INJECTION COMPLETE — $HOSTNAME is now part of the organism"
echo "  Membrane: ${MEMBRANE_DIR}/membrane"
echo "  RustDesk: configured for 192.168.4.244"
echo "  Ollama: tinyllama (loading in background)"
echo "  Heartbeat: every 5min to eastGate"
echo ""
echo "Next: run 'rustdesk --password 579163' to set amoeba password"
