#!/usr/bin/env bash
set -eo pipefail
: "${HOME:=/root}"
# ============================================================================
# ion-channel-gate.sh — ionChannel membrane integration
# ============================================================================
# Wires ionChannel tier detection + bingoCube identity into cellMembrane.
# Runs on ANY gate to auto-configure RustDesk eyeball with zero human input.
#
# ionChannel tiers (from ion-compositor/src/capture/tier.rs):
#   Dmabuf  = GPU zero-copy   (bare metal, 60fps, <5% CPU)
#   Shm     = shared memory   (VMs, 30-60fps, ~15% CPU)
#   Cpu     = framebuffer      (headless, 15-30fps, ~30% CPU)
#   None    = input-only       (no capture, keyboard/mouse only)
#
# bingoCube identity: relay_key → SHA256 → first 16 chars = universal password
# The key IS the identity. Every cell with the key can see every other cell.
# ============================================================================

RELAY_IP="192.168.4.244"
RELAY_KEY="6oVQBFyHHNAJqm1OlS+XvpdoJ5plYrPzJoPTTYlgQdg="
BINGO_PASS=$(echo -n "$RELAY_KEY" | sha256sum | head -c 16)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/ion-channel.log"
STATE_FILE="${SCRIPT_DIR}/local-terminal/remote/ion-channel-state.json"

log() { echo "[$(date -Is)] $*" | tee -a "$LOG_FILE"; }

# ============================================================================
# PHASE 1: Environment Detection (from ion-core TierSelector)
# ============================================================================
detect_environment() {
    local is_vm="false"
    local has_drm="false"
    local has_wayland="false"
    local has_x11="false"
    local gpu_vendor="unknown"
    local capture_tier="None"

    # VM detection (matches ionChannel's detect_vm)
    for f in /sys/class/dmi/id/product_name /sys/class/dmi/id/sys_vendor; do
        if [ -f "$f" ]; then
            local content
            content=$(cat "$f" 2>/dev/null | tr '[:upper:]' '[:lower:]')
            if echo "$content" | grep -qE "virtualbox|vmware|qemu|kvm|xen|hyper-v|bochs"; then
                is_vm="true"
            fi
        fi
    done
    if grep -q "hypervisor" /proc/cpuinfo 2>/dev/null; then
        is_vm="true"
    fi

    # DRM detection
    if [ -e /dev/dri/renderD128 ] || [ -e /dev/dri/card0 ]; then
        has_drm="true"
    fi

    # GPU vendor detection (matches ionChannel's detect_gpu_vendor)
    for drm_path in /sys/class/drm/card0/device/vendor /sys/class/drm/card1/device/vendor; do
        if [ -f "$drm_path" ]; then
            local vendor_id
            vendor_id=$(cat "$drm_path" 2>/dev/null | tr -d '[:space:]')
            case "$vendor_id" in
                0x10de) gpu_vendor="NVIDIA" ;;
                0x1002) gpu_vendor="AMD" ;;
                0x8086) gpu_vendor="Intel" ;;
                0x1af4) gpu_vendor="Virtio" ;;
                0x1234) gpu_vendor="QEMU" ;;
            esac
            break
        fi
    done

    # Display detection
    if [ -n "${WAYLAND_DISPLAY:-}" ]; then
        has_wayland="true"
    fi
    if [ -n "${DISPLAY:-}" ]; then
        has_x11="true"
    fi
    # Also check for running X/Wayland
    if pgrep -x Xorg >/dev/null 2>&1 || pgrep -x Xwayland >/dev/null 2>&1; then
        has_x11="true"
    fi
    if pgrep -x gnome-shell >/dev/null 2>&1 || pgrep -x cosmic-comp >/dev/null 2>&1; then
        has_wayland="true"
    fi

    # Tier selection (matches ionChannel TierSelector::select_best)
    if [ "$has_drm" = "true" ] && [ "$is_vm" = "false" ]; then
        capture_tier="Dmabuf"
    elif [ "$has_drm" = "true" ] && [ "$is_vm" = "true" ]; then
        if [ "$gpu_vendor" = "Virtio" ] || [ "$gpu_vendor" = "QEMU" ]; then
            capture_tier="Shm"
        else
            capture_tier="Dmabuf"
        fi
    elif [ "$has_wayland" = "true" ] || [ "$has_x11" = "true" ]; then
        capture_tier="Cpu"
    else
        capture_tier="None"
    fi

    # Determine mode (from ion-core RemoteDesktopMode)
    local has_capture="false"
    local has_input="true"
    local mode="InputOnly"
    if [ "$capture_tier" != "None" ]; then
        has_capture="true"
        mode="Full"
    fi

    # Ion type (from gaia-wan-trace.js Na+/K+/Ca2+ mapping)
    local ion_type="Cl-"
    local hostname
    hostname=$(hostname)
    case "$hostname" in
        *north*|*polaris*|tamison) ion_type="Na+" ;;
        *east*|*brain*)            ion_type="K+" ;;
        *spore*|*forge*)           ion_type="Ca2+" ;;
        *iron*|*forge2*)           ion_type="Mg2+" ;;
        *graft*|*mac*)             ion_type="Fe2+" ;;
        *blue*|*cursor*)           ion_type="Zn2+" ;;
        *)                          ion_type="Cl-" ;;
    esac

    log "Environment: vm=$is_vm drm=$has_drm gpu=$gpu_vendor x11=$has_x11 wayland=$has_wayland"
    log "ionChannel: tier=$capture_tier mode=$mode ion=$ion_type"

    # Export for other phases
    export ION_IS_VM="$is_vm"
    export ION_HAS_DRM="$has_drm"
    export ION_GPU_VENDOR="$gpu_vendor"
    export ION_HAS_X11="$has_x11"
    export ION_HAS_WAYLAND="$has_wayland"
    export ION_CAPTURE_TIER="$capture_tier"
    export ION_MODE="$mode"
    export ION_ION_TYPE="$ion_type"
    export ION_HAS_CAPTURE="$has_capture"
    export ION_HAS_INPUT="$has_input"
}

# ============================================================================
# PHASE 2: Display Bootstrap (handles headless)
# ============================================================================
ensure_display() {
    if [ "$ION_HAS_X11" = "true" ] || [ "$ION_HAS_WAYLAND" = "true" ]; then
        log "Display already available"
        return 0
    fi

    log "No display detected — bootstrapping headless X"

    # Check if Xorg exists
    if ! command -v Xorg >/dev/null 2>&1; then
        log "WARN: No Xorg binary. Install xserver-xorg for capture tier."
        return 1
    fi

    # Check if already running
    if [ -f /tmp/.X0-lock ]; then
        log "X display :0 already locked, checking..."
        if kill -0 "$(cat /tmp/.X0-lock 2>/dev/null | tr -d '[:space:]')" 2>/dev/null; then
            log "X display :0 is alive"
            export DISPLAY=:0
            ION_HAS_X11="true"
            ION_CAPTURE_TIER="Cpu"
            ION_MODE="Full"
            ION_HAS_CAPTURE="true"
            return 0
        else
            log "Stale X lock, cleaning"
            rm -f /tmp/.X0-lock /tmp/.X11-unix/X0
        fi
    fi

    # Start Xorg headless on vt1
    log "Starting Xorg :0 vt1..."
    Xorg :0 vt1 -noreset -nolisten tcp &
    local xpid=$!
    sleep 5

    if kill -0 "$xpid" 2>/dev/null; then
        log "Xorg :0 started (PID $xpid)"
        export DISPLAY=:0
        ION_HAS_X11="true"
        ION_CAPTURE_TIER="Cpu"
        ION_MODE="Full"
        ION_HAS_CAPTURE="true"
    else
        log "WARN: Xorg failed to start. Running in input-only mode."
        ION_CAPTURE_TIER="None"
        ION_MODE="InputOnly"
        ION_HAS_CAPTURE="false"
    fi
}

# ============================================================================
# PHASE 3: GDM Auto-Login (if GDM present)
# ============================================================================
configure_autologin() {
    if ! command -v gdm3 >/dev/null 2>&1 && ! [ -f /usr/sbin/gdm3 ]; then
        log "No GDM3 found, skipping auto-login config"
        return 0
    fi

    local current_user
    current_user=$(logname 2>/dev/null || whoami)

    local conf="/etc/gdm3/custom.conf"
    if [ -f "$conf" ]; then
        if grep -q "AutomaticLoginEnable=true" "$conf" 2>/dev/null; then
            log "GDM auto-login already enabled"
            return 0
        fi
    fi

    log "Configuring GDM auto-login for $current_user"
    cat > "$conf" << GDMEOF
[daemon]
WaylandEnable=false
AutomaticLoginEnable=true
AutomaticLogin=$current_user

[security]

[xdmcp]

[chooser]

[debug]
GDMEOF

    log "GDM auto-login configured for $current_user"
}

# ============================================================================
# PHASE 4: RustDesk bingoCube Identity
# ============================================================================
configure_rustdesk() {
    if ! command -v rustdesk >/dev/null 2>&1; then
        log "RustDesk not installed. Skipping."
        return 0
    fi

    local rd_id
    rd_id=$(rustdesk --get-id 2>/dev/null || echo "unknown")
    log "RustDesk ID: $rd_id"

    # Find the active config location
    local config_dir=""
    local config_user=""
    for try_dir in \
        "$HOME/.config/rustdesk" \
        "/var/lib/gdm3/.config/rustdesk" \
        "/root/.config/rustdesk"; do
        if [ -d "$try_dir" ]; then
            config_dir="$try_dir"
            break
        fi
    done

    if [ -z "$config_dir" ]; then
        config_dir="$HOME/.config/rustdesk"
        mkdir -p "$config_dir"
    fi

    local toml="$config_dir/RustDesk2.toml"
    log "Configuring RustDesk at $toml"

    # Detect local IP
    local local_ip
    local_ip=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "0.0.0.0")

    # Write config — relay key IS the identity
    cat > "$toml" << RDEOF
rendezvous_server = '${RELAY_IP}:21116'
nat_type = 1
serial = 0
unlock_pin = ''

[options]
relay-server = '${RELAY_IP}'
custom-rendezvous-server = '${RELAY_IP}'
key = '${RELAY_KEY}'
verification-method = 'use-permanent-password'
approve-mode = 'password'
direct-server = 'Y'
allow-remote-config-modification = 'Y'
allow-auto-disconnect = 'N'
local-ip-addr = '${local_ip}'
RDEOF

    # Set bingoCube identity password
    rustdesk --password "$BINGO_PASS" 2>/dev/null || true

    # Fix ownership if running as root for another user's dir
    if [ -n "${SUDO_USER:-}" ] && [ -d "$config_dir" ]; then
        chown -R "${SUDO_USER}:${SUDO_USER}" "$config_dir" 2>/dev/null || true
    fi

    # Restart RustDesk service (non-blocking — systemctl can timeout on busy systems)
    if systemctl is-active rustdesk >/dev/null 2>&1; then
        (systemctl restart rustdesk &) 2>/dev/null || true
        log "RustDesk service restart requested"
    fi

    log "RustDesk configured: relay=$RELAY_IP key=present bingo=$BINGO_PASS id=$rd_id"
}

# ============================================================================
# PHASE 5: Write State (membrane readable)
# ============================================================================
write_state() {
    mkdir -p "$(dirname "$STATE_FILE")"

    local rd_id
    rd_id=$(rustdesk --get-id 2>/dev/null || echo "unknown")
    local hostname
    hostname=$(hostname)
    local local_ip
    local_ip=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "0.0.0.0")

    cat > "$STATE_FILE" << JSONEOF
{
  "ts": "$(date -Is)",
  "hostname": "$hostname",
  "local_ip": "$local_ip",
  "ion_channel": {
    "version": "1.0.0",
    "capture_tier": "$ION_CAPTURE_TIER",
    "mode": "$ION_MODE",
    "ion_type": "$ION_ION_TYPE",
    "has_capture": $ION_HAS_CAPTURE,
    "has_input": $ION_HAS_INPUT,
    "environment": {
      "is_vm": $ION_IS_VM,
      "has_drm": $ION_HAS_DRM,
      "gpu_vendor": "$ION_GPU_VENDOR",
      "has_x11": $ION_HAS_X11,
      "has_wayland": $ION_HAS_WAYLAND
    }
  },
  "rustdesk": {
    "id": "$rd_id",
    "relay": "$RELAY_IP",
    "bingocube_pass": "$BINGO_PASS",
    "bingocube_derivation": "SHA256(relay_key)[0:16]"
  },
  "eyeball": {
    "sclera": "membrane",
    "iris": "$ION_ION_TYPE",
    "pupil": "rustdesk:$rd_id",
    "optic_nerve": "$RELAY_IP:21116"
  }
}
JSONEOF

    log "State written to $STATE_FILE"
}

# ============================================================================
# MAIN
# ============================================================================
main() {
    log "=========================================="
    log "ionChannel Gate — cellMembrane integration"
    log "=========================================="

    detect_environment

    if [ "${1:-}" = "--full" ] || [ "$(id -u)" = "0" ]; then
        ensure_display
        configure_autologin
    fi

    configure_rustdesk
    write_state

    log "=========================================="
    log "COMPLETE: tier=$ION_CAPTURE_TIER mode=$ION_MODE ion=$ION_ION_TYPE"
    log "=========================================="
}

main "$@"
