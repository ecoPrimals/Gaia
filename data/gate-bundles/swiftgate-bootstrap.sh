#!/bin/bash
# swiftGate bootstrap — run this on first wake
# curl -s http://192.168.4.244:8080/data/gate-bundles/swiftgate-bootstrap.sh | bash

echo "🐴 swiftGate bootstrap — welcome to the organism!"

# 1. RustDesk config
mkdir -p ~/.config/rustdesk
curl -s http://192.168.4.244:8080/data/amoeba-peers/swiftgate-RustDesk2.toml > ~/.config/rustdesk/RustDesk2.toml
echo "✅ RustDesk config installed"

# 2. SSH key
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAII5sIdMJh6Q7B8mjJgXzpTZLNnkcfui+U8xUQFVjD8ua beardog-v1.0.0-release" >> ~/.ssh/authorized_keys
sort -u ~/.ssh/authorized_keys -o ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
echo "✅ SSH key authorized"

# 3. Install Ollama
if ! command -v ollama &>/dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi
echo "✅ Ollama ready"

# 4. Pull base models (RTX 3070 = 8GB VRAM)
for model in tinyllama gemma2:2b llama3.2:1b qwen2.5:3b phi3; do
    echo "Pulling $model..."
    ollama pull $model 2>/dev/null &
done
echo "✅ Model pulls started in background"

# 5. Clone the organism
if [ ! -d ~/ecoPrimals ]; then
    echo "Cloning ecoPrimals..."
    git clone http://gaia:GaiaForge2026\!@192.168.4.244:3000/gaia/ecoPrimals.git ~/ecoPrimals
fi
echo "✅ Organism cloned"

# 6. Report back
IP=$(hostname -I | awk '{print $1}')
curl -s -X POST http://192.168.4.244:8443/api/cascade/trigger -d "{\"gate\":\"swiftGate\",\"ip\":\"$IP\",\"event\":\"bootstrap-complete\"}" 2>/dev/null
echo ""
echo "🎮 swiftGate ALIVE at $IP — lub-DUB!"
