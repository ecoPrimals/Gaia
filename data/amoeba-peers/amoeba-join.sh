#!/bin/bash
# Amoeba mesh join — curl this from any gate to join
# Usage: curl -s http://192.168.4.244:8080/data/amoeba-peers/amoeba-join.sh | bash

set -e
GATE_NAME="${1:-$(hostname)}"
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo "🧬 Joining amoeba mesh as $GATE_NAME ($LOCAL_IP)..."

# Config dir
CONF_DIR="$HOME/.config/rustdesk"
mkdir -p "$CONF_DIR/peers"

# Write RustDesk2.toml
cat > "$CONF_DIR/RustDesk2.toml" << TOML
rendezvous_server = '192.168.4.244:21116'
nat_type = 1
serial = 0
unlock_pin = ''

[options]
allow-remote-config-modification = 'Y'
local-ip-addr = '$LOCAL_IP'
relay-server = '192.168.4.244'
verification-method = 'use-permanent-password'
approve-mode = 'password'
custom-rendezvous-server = '192.168.4.244'
direct-server = 'Y'
key = '6oVQBFyHHNAJqm1OlS+XvpdoJ5plYrPzJoPTTYlgQdg='
direct-access-port = '21118'
enable-lan-discovery = 'Y'
allow-auto-disconnect = 'N'
TOML

# Pull peer files
for f in 19091278 1871544996 412828750; do
    curl -s "http://192.168.4.244:8080/data/amoeba-peers/$f.toml" > "$CONF_DIR/peers/$f.toml"
done

# Set password + restart
rustdesk --password 579163 2>/dev/null || true
sudo systemctl restart rustdesk 2>/dev/null || true
sleep 3
rustdesk --password 579163 2>/dev/null || true

echo "✅ $GATE_NAME joined amoeba mesh!"
echo "   ID: $(rustdesk --get-id 2>/dev/null)"
echo "   Password: 579163"
echo "   Relay: 192.168.4.244"
