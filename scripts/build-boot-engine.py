#!/usr/bin/env python3
"""Build Auto-Boot Engine on eastGate
Creates a custom GRUB EFI with embedded config using grub-mkstandalone.
This EFI auto-executes setup_var commands and chainloads Windows — no typing needed.
"""
import subprocess, json, sys, os

EASTGATE = "192.168.4.244"
USER = "eastgate"
PASSWORD = "eastgate"

def ssh(cmd, timeout=15):
    r = subprocess.run(
        ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=5",
         "-o", "PreferredAuthentications=password",
         f"{USER}@{EASTGATE}", cmd],
        capture_output=True, text=True, timeout=timeout,
        input=PASSWORD + "\n"
    )
    return r.stdout.strip(), r.stderr.strip(), r.returncode

def sshpass_cmd(cmd, timeout=15):
    r = subprocess.run(
        ["sshpass", "-p", PASSWORD, "ssh",
         "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=5",
         f"{USER}@{EASTGATE}", cmd],
        capture_output=True, text=True, timeout=timeout
    )
    return r.stdout.strip(), r.stderr.strip(), r.returncode

print("=== BOOT ENGINE BUILDER ===")

# Check if grub tools exist on eastGate
print("\n--- Checking grub tools on eastGate ---")
for tool_cmd in [
    "which grub-mkstandalone 2>/dev/null || which grub2-mkstandalone 2>/dev/null || echo 'NOT_FOUND'",
    "which grub-mkimage 2>/dev/null || which grub2-mkimage 2>/dev/null || echo 'NOT_FOUND'",
    "dpkg -l | grep grub-efi 2>/dev/null || rpm -qa | grep grub2-efi 2>/dev/null || echo 'no_package_found'",
    "ls /usr/lib/grub/x86_64-efi/ 2>/dev/null | head -5 || ls /usr/lib/grub2/x86_64-efi/ 2>/dev/null | head -5 || echo 'no_grub_modules'",
]:
    out, err, rc = sshpass_cmd(tool_cmd)
    print(f"  {out or err or '(empty)'}")

# Create the grub.cfg content that will be embedded
grub_cfg = """# GAIA Boot Engine — Auto-execute firmware mods then chainload Windows
# This config is EMBEDDED in the EFI binary — auto-runs on boot

set timeout=3
set default=0

menuentry "GAIA: iGPU Enable + Boot Windows" {
    echo "GAIA Boot Engine v1"
    echo "Writing iGPU firmware variables..."
    
    # Enable iGPU (AMD_PBS_SETUP offset 0x48 = Forces)
    setup_var_cv AMD_PBS_SETUP 0x48 0x01 0x01
    echo "  0x48 = 0x01 (iGPU Forces) — WRITTEN"
    
    # Set UMA to 512MB (AMD_PBS_SETUP offset 0x49 = 512M)  
    setup_var_cv AMD_PBS_SETUP 0x49 0x01 0x06
    echo "  0x49 = 0x06 (UMA 512M) — WRITTEN"
    
    echo ""
    echo "Firmware modified. Rebooting to Windows..."
    sleep 2
    reboot
}

menuentry "GAIA: Boot Windows (no changes)" {
    echo "Chainloading Windows Boot Manager..."
    search --file --set=root /EFI/Microsoft/Boot/bootmgfw.efi
    chainloader /EFI/Microsoft/Boot/bootmgfw.efi
}

menuentry "GAIA: Drop to GRUB Shell" {
    echo "Entering GRUB shell. Type 'reboot' to restart."
    # This just falls through to shell
}
"""

print("\n--- Creating embedded grub.cfg ---")
print(grub_cfg)

# Write config to eastGate
write_cmd = f"""cat > /tmp/gaia-boot-engine.cfg << 'GAIAEOF'
{grub_cfg}
GAIAEOF
echo "Config written to /tmp/gaia-boot-engine.cfg"
"""
out, err, rc = sshpass_cmd(write_cmd)
print(f"  {out}")

# Try to build the standalone EFI
print("\n--- Building standalone EFI binary ---")
build_cmd = """
GRUB_MKSTANDALONE=$(which grub-mkstandalone 2>/dev/null || which grub2-mkstandalone 2>/dev/null)
GRUB_DIR=""
if [ -d /usr/lib/grub/x86_64-efi ]; then
    GRUB_DIR=/usr/lib/grub/x86_64-efi
elif [ -d /usr/lib/grub2/x86_64-efi ]; then
    GRUB_DIR=/usr/lib/grub2/x86_64-efi
fi

if [ -z "$GRUB_MKSTANDALONE" ]; then
    echo "NEED_INSTALL: grub-mkstandalone not found"
    echo "Try: sudo apt install grub-efi-amd64-bin"
    
    # Fallback: try grub-mkimage (more common)
    GRUB_MKIMAGE=$(which grub-mkimage 2>/dev/null || which grub2-mkimage 2>/dev/null)
    if [ -n "$GRUB_MKIMAGE" ] && [ -n "$GRUB_DIR" ]; then
        echo "FALLBACK: Using grub-mkimage with embedded config"
        $GRUB_MKIMAGE -O x86_64-efi -o /tmp/gaia-boot-engine.efi \
            -c /tmp/gaia-boot-engine.cfg \
            -d $GRUB_DIR \
            -p /EFI/tools \
            part_gpt fat ext2 normal chain boot configfile \
            linux reboot search efi_gop efi_uga \
            setup_var 2>&1
        
        if [ -f /tmp/gaia-boot-engine.efi ]; then
            SIZE=$(stat -c%s /tmp/gaia-boot-engine.efi)
            echo "SUCCESS: /tmp/gaia-boot-engine.efi ($SIZE bytes)"
        else
            echo "FAIL: grub-mkimage failed"
        fi
    else
        echo "NO_FALLBACK: neither grub-mkstandalone nor grub-mkimage available"
        echo "GRUB_DIR=$GRUB_DIR"
    fi
else
    echo "FOUND: $GRUB_MKSTANDALONE"
    $GRUB_MKSTANDALONE -O x86_64-efi \
        -o /tmp/gaia-boot-engine.efi \
        --modules="part_gpt fat ext2 normal chain boot configfile linux reboot search efi_gop efi_uga" \
        "/boot/grub/grub.cfg=/tmp/gaia-boot-engine.cfg" 2>&1
    
    if [ -f /tmp/gaia-boot-engine.efi ]; then
        SIZE=$(stat -c%s /tmp/gaia-boot-engine.efi)
        echo "SUCCESS: /tmp/gaia-boot-engine.efi ($SIZE bytes)"
    else
        echo "FAIL: grub-mkstandalone failed"
    fi
fi

# Also check if setup_var module exists
if [ -n "$GRUB_DIR" ]; then
    echo ""
    echo "Available GRUB modules:"
    ls $GRUB_DIR/*.mod 2>/dev/null | grep -E 'setup|var|efi' | head -20
    echo "Total modules: $(ls $GRUB_DIR/*.mod 2>/dev/null | wc -l)"
fi
"""
out, err, rc = sshpass_cmd(build_cmd, timeout=30)
print(f"  {out}")
if err:
    print(f"  stderr: {err}")

# Summary
print("\n=== BOOT ENGINE STATUS ===")
print("Model: data/gut/uefi-reactor-model.json")
print("Current state: iGPU=OFF, NVMe=2×ghost, CPU=8C/8T (should be 16C/32T)")
print("\nReboot targets (priority order):")
print("  1. iGPU enable — 2 firmware var writes, LOW risk")
print("  2. NVMe wake — need UMAF exploration first, MEDIUM risk")
print("  3. CPU CCD1+SMT — need UMAF exploration first, LOW risk")
print("\nAuto-boot engine: see above for build status")
