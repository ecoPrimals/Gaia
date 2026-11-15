#!/bin/bash
# ╔════════════════════════════════════════════════════════╗
# ║  GAIA CHIPMUNK — biomeGate Ancient Relic Extraction    ║
# ║  Inject, inventory, extract, pass OUT to eastGate      ║
# ║  Then melt Pop!_OS and remake as biomeOS               ║
# ╚════════════════════════════════════════════════════════╝

EASTGATE="192.168.4.244"
GATE_NAME="biomeGate"
DUMP_DIR="/tmp/gaia-chipmunk"
mkdir -p "$DUMP_DIR"

echo "=== GAIA CHIPMUNK — $GATE_NAME ==="
echo "$(date -Iseconds)"
echo ""

# ─── PHASE 1: INSTALL SSH (permanent pore) ───
echo ">>> PHASE 1: Opening the pore..."
sudo apt-get update -qq
sudo apt-get install -y openssh-server ethtool curl jq 2>/dev/null
sudo systemctl enable --now ssh
echo "✓ SSH pore opened — Gaia can reach in forever"

# ─── PHASE 2: INJECT SSH KEY ───
echo ""
echo ">>> PHASE 2: Injecting SSH key..."
mkdir -p ~/.ssh && chmod 700 ~/.ssh
curl -s "http://${EASTGATE}:8080/data/eastgate-key.pub" >> ~/.ssh/authorized_keys 2>/dev/null
chmod 600 ~/.ssh/authorized_keys
echo "✓ eastGate SSH key injected"

# ─── PHASE 3: HARDWARE INVENTORY (the real treasure) ───
echo ""
echo ">>> PHASE 3: Hardware inventory..."
{
  echo "{"
  echo '  "gate": "biomeGate",'
  echo "  \"ts\": \"$(date -Iseconds)\","
  echo '  "hostname": "'$(hostname)'",'
  
  echo '  "cpu": {'
  echo '    "model": "'$(grep "model name" /proc/cpuinfo | head -1 | cut -d: -f2 | xargs)'",'
  echo '    "cores": '$(nproc)','
  echo '    "threads": '$(grep -c processor /proc/cpuinfo)
  echo '  },'
  
  echo '  "ram": {'
  echo '    "total_gb": "'$(free -g | awk '/Mem:/{print $2}')'",'
  echo '    "used_gb": "'$(free -g | awk '/Mem:/{print $3}')'",'
  echo '    "free_gb": "'$(free -g | awk '/Mem:/{print $4}')'"'
  echo '  },'
  
  echo '  "gpus": ['
  lspci | grep -iE "vga|3d|display" | while read line; do
    echo "    \"$(echo $line | cut -d: -f3- | xargs)\","
  done
  echo '    null'
  echo '  ],'
  
  echo '  "nvidia": ['
  nvidia-smi -L 2>/dev/null | while read line; do
    echo "    \"$line\","
  done
  echo '    null'
  echo '  ],'
  
  echo '  "nvidia_detail": "'$(nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>/dev/null | tr '\n' '; ')'",'
  
  echo '  "pci_devices": ['
  lspci | grep -iE "nvidia|amd|brainchip|akida|radeon|tensor" | while read line; do
    echo "    \"$(echo $line | xargs)\","
  done
  echo '    null'
  echo '  ],'
  
  echo '  "storage": ['
  lsblk -d -o NAME,SIZE,MODEL,TRAN 2>/dev/null | tail -n+2 | while read line; do
    echo "    \"$line\","
  done
  echo '    null'
  echo '  ],'
  
  echo '  "board": {'
  echo '    "vendor": "'$(cat /sys/class/dmi/id/board_vendor 2>/dev/null)'",'
  echo '    "product": "'$(cat /sys/class/dmi/id/board_name 2>/dev/null)'",'
  echo '    "bios": "'$(cat /sys/class/dmi/id/bios_version 2>/dev/null)'"'
  echo '  },'
  
  echo '  "network": ['
  ip -o link show | grep -v lo | while read line; do
    echo "    \"$(echo $line | awk '{print $2, $NF}')\"," 
  done
  echo '    null'
  echo '  ],'
  
  echo '  "os": {'
  echo '    "distro": "'$(lsb_release -ds 2>/dev/null || cat /etc/os-release | grep PRETTY | cut -d= -f2 | tr -d '"')'",'
  echo '    "kernel": "'$(uname -r)'"'
  echo '  },'
  
  echo '  "usb": ['
  lsusb 2>/dev/null | while read line; do
    echo "    \"$line\","
  done
  echo '    null'
  echo '  ]'
  
  echo "}"
} > "$DUMP_DIR/hardware.json"
echo "✓ Hardware inventory saved"

# ─── PHASE 4: DATA ARCHAEOLOGY (the old genome) ───
echo ""
echo ">>> PHASE 4: Data archaeology — finding the ancient genome..."
{
  echo "=== FILESYSTEM SUMMARY ==="
  df -h
  echo ""
  echo "=== HOME DIRECTORY STRUCTURE (depth 3) ==="
  find /home -maxdepth 3 -type d 2>/dev/null
  echo ""
  echo "=== LARGE FILES (>100MB) ==="
  find /home -size +100M -type f 2>/dev/null | head -50
  echo ""
  echo "=== /opt CONTENTS ==="
  ls -la /opt/ 2>/dev/null
  find /opt -maxdepth 3 -type d 2>/dev/null
  echo ""
  echo "=== OLD GAIA DATA ==="
  find / -path /proc -prune -o -path /sys -prune -o -name "*.json" -print 2>/dev/null | grep -iE "gaia|primal|eco|biome|coral|hot.?spring|nucleus" | head -50
  echo ""
  echo "=== GIT REPOS ==="
  find /home /opt /root -name ".git" -type d 2>/dev/null | head -20
  echo ""
  echo "=== DOCKER IMAGES ==="
  docker images 2>/dev/null
  echo ""
  echo "=== RUST/CARGO PROJECTS ==="
  find /home -name "Cargo.toml" 2>/dev/null | head -20
  echo ""
  echo "=== GPU DRIVER STATE ==="
  nvidia-smi 2>/dev/null
  echo ""
  rocm-smi 2>/dev/null || echo "no rocm-smi"
  echo ""
  echo "=== AKIDA/BRAINCHIP ==="
  find / -path /proc -prune -o -path /sys -prune -o -iname "*akida*" -print 2>/dev/null | head -10
  find / -path /proc -prune -o -path /sys -prune -o -iname "*brainchip*" -print 2>/dev/null | head -10
} > "$DUMP_DIR/archaeology.txt" 2>&1
echo "✓ Archaeology complete"

# ─── PHASE 5: PULL HEART-PULL (inject current Gaia state) ───
echo ""
echo ">>> PHASE 5: Absorbing current organism state..."
curl -s "http://${EASTGATE}:8080/data/heart-pull.json" -o "$DUMP_DIR/heart-pull.json" 2>/dev/null
echo "✓ Heart-pull absorbed: $(python3 -c 'import json; print(len(json.load(open("'$DUMP_DIR'/heart-pull.json"))))' 2>/dev/null || echo '?') sections"

# ─── PHASE 6: ENABLE WoL (never need physical touch again) ───
echo ""
echo ">>> PHASE 6: Enabling Wake-on-LAN..."
IFACE=$(ip -o link show | grep "state UP" | grep -v lo | head -1 | awk -F: '{print $2}' | tr -d ' ')
sudo ethtool -s "$IFACE" wol g 2>/dev/null && echo "✓ WoL enabled on $IFACE" || echo "WoL not supported on $IFACE"

# ─── PHASE 7: PHONE HOME ───
echo ""
echo ">>> PHASE 7: Phoning home to eastGate..."
# Try to push data back to eastGate
scp -o StrictHostKeyChecking=no "$DUMP_DIR/hardware.json" eastgate@${EASTGATE}:/tmp/biomegate-hardware.json 2>/dev/null && echo "✓ Hardware sent to eastGate" || echo "(scp failed — pull from eastGate instead)"
scp -o StrictHostKeyChecking=no "$DUMP_DIR/archaeology.txt" eastgate@${EASTGATE}:/tmp/biomegate-archaeology.txt 2>/dev/null && echo "✓ Archaeology sent to eastGate" || echo "(pull from eastGate instead)"

echo ""
echo "=== DATA IS AT: $DUMP_DIR/ ==="
ls -la "$DUMP_DIR/"
echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║  CHIPMUNK COMPLETE — biomeGate → biomeOS       ║"
echo "║  SSH pore: OPEN                                 ║"
echo "║  SSH key:  INJECTED                             ║"
echo "║  WoL:     ENABLED                               ║"
echo "║  Genome:  EXTRACTED to /tmp/gaia-chipmunk/      ║"
echo "║                                                  ║"
echo "║  eastGate can now:                               ║"
echo "║    ssh biomegate@192.168.4.198                   ║"
echo "║    scp the genome back                           ║"
echo "║    Then MELT and REMAKE as biomeOS               ║"
echo "╚════════════════════════════════════════════════╝"
