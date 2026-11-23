#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Push sovereign RustDesk relay config to all reachable gates.
# Run from sporeGate (or any node on 192.168.4.x with SSH keys distributed).
#
# Two modes:
#   1. SSH mode (preferred): directly SSH to each gate, push config
#   2. Discovery mode: scan LAN, attempt push to all responding hosts
#
# Prerequisites:
#   - SSH key access to target gates (or password auth enabled)
#   - RustDesk installed on target gates
#   - Run as user with sudo/pkexec capability on targets

set -euo pipefail

RELAY_CONFIG="=[KEY_SCRUBBED]"

# Known gates on the LAN (add as discovered)
declare -A GATES=(
    [eastGate]="[LAN_IP]"
    [northGate]=""          # fill when DHCP lease identified
    # [deviceX]="192.168.4.XX"
)

# Gates reachable only via WAN (SSH through golgi or public relay)
declare -A WAN_GATES=(
    [flockGate]=""          # fill with golgi-reachable IP or RustDesk ID
)

SSH_USER="${MEMBRANE_PROVISION_SSH_USER:-root}"
SSH_OPTS="-o ConnectTimeout=5 -o StrictHostKeyChecking=accept-new -o BatchMode=yes"

push_config_ssh() {
    local name="$1" ip="$2"
    echo "[$name] Pushing sovereign relay config via SSH ($ip)..."

    if ssh $SSH_OPTS "$SSH_USER@$ip" "which rustdesk" &>/dev/null; then
        ssh $SSH_OPTS "$SSH_USER@$ip" "
            pkill -9 rustdesk 2>/dev/null || true
            sleep 1
            rustdesk --config '$RELAY_CONFIG'
            systemctl restart rustdesk 2>/dev/null || nohup rustdesk --service &>/dev/null &
        "
        echo "[$name] ✅ Sovereign relay configured"
    else
        echo "[$name] ⚠️  RustDesk not installed — skipping (needs: apt install rustdesk)"
    fi
}

discover_and_push() {
    echo "=== Discovery mode: scanning [LAN_IP]/24 ==="
    local hosts
    hosts=$(nmap -sn [LAN_IP]/24 2>/dev/null | grep "Nmap scan" | awk '{print $5}')

    for ip in $hosts; do
        # Skip sporeGate itself
        [[ "$ip" == "[LAN_IP]" || "$ip" == "[LAN_IP]" ]] && continue
        # Skip known-configured (eastGate already on sovereign)
        [[ "$ip" == "[LAN_IP]" ]] && continue

        echo "[discover] Trying $ip..."
        if ssh $SSH_OPTS "$SSH_USER@$ip" "hostname" &>/dev/null; then
            local hostname
            hostname=$(ssh $SSH_OPTS "$SSH_USER@$ip" "hostname" 2>/dev/null || echo "unknown")
            push_config_ssh "$hostname@$ip" "$ip"
        else
            echo "[discover] $ip — SSH not available (try RustDesk public relay path)"
        fi
    done
}

push_wan_gate() {
    local name="$1" target="$2"
    echo "[$name] WAN gate — pushing via golgi relay..."
    # SSH hop through golgi to reach WAN gates
    ssh $SSH_OPTS "root@[RELAY_PUBLIC]" "
        ssh $SSH_OPTS '$SSH_USER@$target' '
            pkill -9 rustdesk 2>/dev/null || true
            sleep 1
            rustdesk --config \"$RELAY_CONFIG\"
            systemctl restart rustdesk 2>/dev/null || nohup rustdesk --service &>/dev/null &
        '
    " && echo "[$name] ✅ Sovereign relay configured via golgi hop" \
      || echo "[$name] ❌ Failed — may need direct public RustDesk session"
}

# --- Main ---
echo "╔══════════════════════════════════════════════════╗"
echo "║  Sovereign Relay Push — K-Derm Plasma Membrane  ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

case "${1:-lan}" in
    lan)
        echo "=== Pushing to known LAN gates ==="
        for name in "${!GATES[@]}"; do
            ip="${GATES[$name]}"
            [[ -z "$ip" ]] && { echo "[$name] IP unknown — skipping"; continue; }
            push_config_ssh "$name" "$ip"
        done
        ;;
    discover)
        discover_and_push
        ;;
    wan)
        echo "=== Pushing to WAN gates via golgi ==="
        for name in "${!WAN_GATES[@]}"; do
            target="${WAN_GATES[$name]}"
            [[ -z "$target" ]] && { echo "[$name] target unknown — skipping"; continue; }
            push_wan_gate "$name" "$target"
        done
        ;;
    all)
        echo "=== Phase 1: Known LAN gates ==="
        for name in "${!GATES[@]}"; do
            ip="${GATES[$name]}"
            [[ -z "$ip" ]] && { echo "[$name] IP unknown — skipping"; continue; }
            push_config_ssh "$name" "$ip"
        done
        echo ""
        echo "=== Phase 2: Discovery sweep ==="
        discover_and_push
        echo ""
        echo "=== Phase 3: WAN gates via golgi ==="
        for name in "${!WAN_GATES[@]}"; do
            target="${WAN_GATES[$name]}"
            [[ -z "$target" ]] && { echo "[$name] target unknown — skipping"; continue; }
            push_wan_gate "$name" "$target"
        done
        ;;
    *)
        echo "Usage: $0 [lan|discover|wan|all]"
        exit 1
        ;;
esac

echo ""
echo "Done. Verify with: rustdesk --get-id (on each gate)"
