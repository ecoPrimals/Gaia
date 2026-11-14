#!/system/bin/sh
# GAIA NEEDLE — Speak Friend and Enter
# Universal gate login: username=gatename, password=gatename (lowercase)
# Works on any ecoPrimals gate with the standard credential pattern
#
# Environment variables:
#   NEEDLE_GATE - gate name in lowercase (e.g., biomegate, strandgate)

SU="/debug_ramdisk/su"
TYPE="/data/local/tmp/type.sh"
GATE="${NEEDLE_GATE:?Set NEEDLE_GATE to the gate name (lowercase)}"
EASTGATE="${NEEDLE_EASTGATE:-primals.eco}"

run() { $SU -c "sh $TYPE $*"; }

echo "=== GAIA NEEDLE — Speak Friend and Enter ==="
echo "Gate: $GATE"

# Wait for login screen
sleep 5
run --enter
sleep 1

# Mellon
echo "Phase 1: Speaking the name..."
run --line "$GATE"
sleep 2
run --line "$GATE"
sleep 5

# Open terminal
echo "Phase 2: Open terminal"
run --ctrl-alt-t
sleep 3

# Install SSH
echo "Phase 3: Install SSH"
run --line "sudo apt-get update -qq && sudo apt-get install -y openssh-server curl ethtool 2>/dev/null || sudo dnf install -y openssh-server curl ethtool 2>/dev/null || sudo pacman -Sy --noconfirm openssh curl ethtool 2>/dev/null"
sleep 30

# Start SSH
echo "Phase 4: Start SSH"
run --line "sudo systemctl enable --now ssh 2>/dev/null || sudo systemctl enable --now sshd"
sleep 2

# Inject key
echo "Phase 5: Inject SSH key"
run --line "mkdir -p ~/.ssh && chmod 700 ~/.ssh && curl -s http://${EASTGATE}:8080/data/eastgate-key.pub >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && echo KEY_INJECTED"
sleep 3

# WoL
echo "Phase 6: Enable WoL"
run --line "IFACE=\$(ip -o link show | grep 'state UP' | grep -v lo | head -1 | awk -F: '{print \$2}' | tr -d ' ') && sudo ethtool -s \$IFACE wol g 2>/dev/null && echo WoL enabled on \$IFACE"
sleep 2

# Heart-pull
echo "Phase 7: Absorb"
run --line "mkdir -p ~/gaia && curl -s http://${EASTGATE}:8080/data/heart-pull.json -o ~/gaia/heart-pull.json && echo ABSORBED"

echo "=== ${GATE}: FRIEND ENTERED ==="
