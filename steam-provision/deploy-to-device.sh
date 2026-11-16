#!/bin/bash
# ============================================================
# DEPLOY GAIA TO A FRESHLY-PAIRED STEAM DEVICE
# ============================================================
# Usage: ./deploy-to-device.sh <IP> [ssh-key-path]
#
# Run this from milkGate or eastGate AFTER Kevin does the 4 taps.
# The devkit pairing gives us SSH. This does the rest.
# ============================================================

DEVICE_IP="${1:?Usage: deploy-to-device.sh <IP> [key-path]}"
KEY_PATH="${2:-$HOME/.config/steamos-devkit/devkit_rsa}"
PROVISION_DIR="$(dirname "$0")"
USER="deck"

# Fall back to id_rsa_devkit
[ -f "$KEY_PATH" ] || KEY_PATH="$HOME/.ssh/id_rsa_devkit"
[ -f "$KEY_PATH" ] || { echo "No SSH key found at $KEY_PATH"; exit 1; }

SSH="ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -i $KEY_PATH"
SCP="scp -o StrictHostKeyChecking=no -i $KEY_PATH"

echo "=== Deploying Gaia to $DEVICE_IP ==="

# Test connection
echo "Testing SSH..."
$SSH $USER@$DEVICE_IP "echo 'SSH OK: $(hostname) $(uname -m)'" || {
    echo "SSH failed. Is the device paired?"
    exit 1
}

# Upload provisioner
echo "Uploading provisioner..."
$SCP -r "$PROVISION_DIR/gaia-provision.sh" $USER@$DEVICE_IP:/tmp/

# Run it
echo "Running provisioner..."
$SSH $USER@$DEVICE_IP "chmod +x /tmp/gaia-provision.sh && bash /tmp/gaia-provision.sh"

echo ""
echo "=== Deployment complete ==="
echo "Device $DEVICE_IP is now part of the organism."
echo "Kevin never touches it again."
