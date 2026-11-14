#!/bin/bash
# amoeba_bootstrap.sh — Install RustDesk client on any Linux gate
# Run this ON the target gate (via SSH, physical access, or existing RustDesk session)
#
# Usage: curl -sSL http://192.168.4.244:8443/amoeba-bootstrap | bash
#    or: bash amoeba_bootstrap.sh
#
# This makes the gate a RustDesk peer in the AMOEBA sovereign relay.
# After install, Kevin can connect via RustDesk from any other gate.

set -e

RELAY="192.168.4.244"
RELAY_PORT="21116"
RUSTDESK_VERSION="1.3.7"
GATE_NAME=$(hostname)
ARCH=$(uname -m)

echo ""
echo "🦠 AMOEBA BOOTSTRAP — RustDesk sovereign relay client"
echo "  Gate: $GATE_NAME"
echo "  Relay: $RELAY:$RELAY_PORT"
echo "  Arch: $ARCH"
echo ""

# Detect package manager
if command -v apt-get &>/dev/null; then
    PKG="apt"
elif command -v dnf &>/dev/null; then
    PKG="dnf"
elif command -v pacman &>/dev/null; then
    PKG="pacman"
else
    PKG="unknown"
fi

# Check if RustDesk is already installed
if command -v rustdesk &>/dev/null; then
    echo "✅ RustDesk already installed: $(rustdesk --version 2>/dev/null || echo 'unknown version')"
else
    echo "📦 Installing RustDesk..."
    
    case "$ARCH" in
        x86_64)
            DEB_URL="https://github.com/rustdesk/rustdesk/releases/download/${RUSTDESK_VERSION}/rustdesk-${RUSTDESK_VERSION}-x86_64.deb"
            ;;
        aarch64|arm64)
            DEB_URL="https://github.com/rustdesk/rustdesk/releases/download/${RUSTDESK_VERSION}/rustdesk-${RUSTDESK_VERSION}-aarch64.deb"
            ;;
        *)
            echo "❌ Unknown architecture: $ARCH"
            exit 1
            ;;
    esac
    
    case "$PKG" in
        apt)
            curl -sSL "$DEB_URL" -o /tmp/rustdesk.deb
            sudo apt-get install -y /tmp/rustdesk.deb
            rm /tmp/rustdesk.deb
            ;;
        pacman)
            # SteamOS uses pacman
            sudo pacman -S --noconfirm rustdesk 2>/dev/null || {
                curl -sSL "$DEB_URL" -o /tmp/rustdesk.deb
                sudo dpkg -i /tmp/rustdesk.deb 2>/dev/null || {
                    echo "⚠️ Manual install needed for SteamOS"
                    echo "  Download: $DEB_URL"
                }
            }
            ;;
        *)
            echo "⚠️ Unknown package manager. Trying direct .deb install..."
            curl -sSL "$DEB_URL" -o /tmp/rustdesk.deb
            sudo dpkg -i /tmp/rustdesk.deb || sudo apt-get install -f -y
            ;;
    esac
fi

# Configure RustDesk to use AMOEBA relay
CONFIG_DIR="$HOME/.config/rustdesk"
mkdir -p "$CONFIG_DIR"

cat > "$CONFIG_DIR/RustDesk2.toml" << EOF
rendezvous_server = '${RELAY}:${RELAY_PORT}'
nat_type = 1
serial = 0

[options]
direct-server = 'Y'
verification-method = 'use-permanent-password'
allow-auto-disconnect = 'N'
local-ip-addr = '$(hostname -I | awk '{print $1}')'
EOF

echo ""
echo "✅ RustDesk configured:"
echo "  Relay: ${RELAY}:${RELAY_PORT}"
echo "  Local IP: $(hostname -I | awk '{print $1}')"
echo "  Config: $CONFIG_DIR/RustDesk2.toml"
echo ""

# Set a default password if interactive
if [ -t 0 ]; then
    echo "Set RustDesk password (for remote access):"
    read -sp "Password: " RDPASS
    echo ""
    if [ -n "$RDPASS" ]; then
        rustdesk --password "$RDPASS" 2>/dev/null || echo "  (password set via CLI not supported, set in GUI)"
    fi
fi

# Enable and start RustDesk service
if command -v systemctl &>/dev/null; then
    sudo systemctl enable rustdesk --now 2>/dev/null || true
    echo "✅ RustDesk service enabled and started"
fi

# Report
echo ""
echo "═══ AMOEBA BOOTSTRAP COMPLETE ═══"
echo "  Gate: $GATE_NAME"
echo "  IP: $(hostname -I | awk '{print $1}')"
echo "  Relay: ${RELAY}:${RELAY_PORT}"
echo "  RustDesk ID: $(rustdesk --get-id 2>/dev/null || echo 'check GUI')"
echo ""
echo "  Kevin can now connect to this gate via RustDesk."
echo "  From northGate: open RustDesk → enter this gate's IP → connect"
echo "  lub-DUB. 🦠"
