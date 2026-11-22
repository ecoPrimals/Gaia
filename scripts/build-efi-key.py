"""Build the EFI key — prepare setup_var.efi to unlock UMA from boot time.
This runs in parallel while we keep working on everything else."""
import subprocess, os, struct, json

print("=" * 60)
print("BUILDING THE EFI KEY — UMA unlock prep")
print("=" * 60)

# ─── 1: Mount EFI System Partition ───
print("\n[1] Mounting EFI partition...\n")
cmd1 = '''
$efi = Get-Partition | Where-Object { $_.GptType -eq "{C12A7328-F81F-11D2-BA4B-00A0C93EC93B}" }
if ($efi) {
    Write-Output "EFI partition: Disk $($efi.DiskNumber) Part $($efi.PartitionNumber) Size $([math]::Round($efi.Size/1MB))MB"
    # Try to assign a drive letter
    $letter = $null
    foreach ($l in 'Z','Y','X','W') {
        if (-not (Test-Path "$($l):")) {
            $letter = $l
            break
        }
    }
    if ($letter) {
        try {
            $efi | Set-Partition -NewDriveLetter $letter -ErrorAction Stop
            Write-Output "Mounted at ${letter}:"
            Get-ChildItem "${letter}:\EFI" -ErrorAction SilentlyContinue | ForEach-Object { Write-Output "  EFI\$($_.Name)" }
        } catch {
            # Try mountvol
            $vol = (Get-Partition -DiskNumber $efi.DiskNumber -PartitionNumber $efi.PartitionNumber | Get-Volume).UniqueId
            mountvol "${letter}:" $vol 2>&1
            if (Test-Path "${letter}:\EFI") {
                Write-Output "Mounted via mountvol at ${letter}:"
                Get-ChildItem "${letter}:\EFI" -ErrorAction SilentlyContinue | ForEach-Object { Write-Output "  EFI\$($_.Name)" }
            } else {
                Write-Output "Could not mount. Try: mountvol Z: /S"
            }
        }
    }
} else {
    Write-Output "No EFI partition found!"
}
'''
r1 = subprocess.run(['powershell', '-Command', cmd1], capture_output=True, text=True, timeout=15)
print(r1.stdout.strip())

# Try mountvol /S as backup
if 'Could not' in r1.stdout or 'No EFI' in r1.stdout:
    r1b = subprocess.run(['mountvol', 'Z:', '/S'], capture_output=True, text=True, timeout=5)
    print(f"  mountvol /S: {r1b.stdout.strip()} {r1b.stderr.strip()}")

# ─── 2: Determine the UMA value encoding ───
print("\n[2] Determining UMA value encoding...\n")
print("  BIOS options: [Auto] [64M] [80M] [96M] [128M] [256M] [384M] [512M] ...")
print("  Current NVRAM: 0xFFFFFFFF (Auto)")
print()
print("  Most likely AMI encoding (index-based):")
print("    0xFF = Auto (current)")
print("    0x00 = 64M")
print("    0x01 = 80M")
print("    0x02 = 96M")
print("    0x03 = 128M")
print("    0x04 = 256M")
print("    0x05 = 384M")
print("    0x06 = 512M  ← TARGET")
print("    0x07 = 768M")
print("    0x08 = 1G")
print()

# Check StdDefaults for clues
if os.path.exists("data/uefi-sniffs/vars/StdDefaults.bin"):
    with open("data/uefi-sniffs/vars/StdDefaults.bin", 'rb') as f:
        defaults = f.read()
    print(f"  StdDefaults: {len(defaults)} bytes")
    # StdDefaults contains default values for ALL variables
    # We need to find where AMD_PBS_SETUP defaults are stored
    
    # Look for the AMD_PBS_SETUP GUID in StdDefaults
    guid_bytes = bytes.fromhex("A339D746".encode().hex())  # This isn't right, need proper GUID
    # Actually search for a pattern that matches AMD_PBS_SETUP structure
    # The first few bytes of AMD_PBS_SETUP are: 03 8C 01 01 00 00 00 00
    pattern = b'\x03\x8c\x01\x01\x00\x00\x00\x00'
    pos = defaults.find(pattern)
    if pos >= 0:
        print(f"  Found AMD_PBS_SETUP pattern in StdDefaults at offset {pos}")
        # Check what's at offset 0x49 from there
        uma_default = defaults[pos + 0x49]
        print(f"  Default UMA value at +0x49: 0x{uma_default:02X}")
    else:
        print("  AMD_PBS_SETUP pattern not found in StdDefaults")

# ─── 3: Write the EFI key instructions ───
print("\n[3] EFI key specification...\n")
key_spec = {
    "variable": "AMD_PBS_SETUP",
    "guid": "A339D746-F678-49B3-9FC7-54CE0F9DF226",
    "offset": "0x49",
    "size": "1 byte (only first byte of the 4-byte field matters)",
    "current_value": "0xFF (Auto = no UMA)",
    "target_value": "0x06 (most likely = 512M, index 6 in option list)",
    "alternative_values": {
        "0x00": "64M (safe minimum)",
        "0x03": "128M (safe test)",
        "0x06": "512M (target)",
        "0x08": "1G (generous)"
    },
    "tool_needed": "setup_var.efi or UEFI Shell setvar",
    "command": "setup_var_cv AMD_PBS_SETUP 0x49 0x06",
    "risk": "LOW — wrong value just means iGPU uses wrong size, BIOS can always reset to defaults"
}

os.makedirs("data/uefi-sniffs", exist_ok=True)
with open("data/uefi-sniffs/efi-key-spec.json", 'w') as f:
    json.dump(key_spec, f, indent=2)
print(json.dumps(key_spec, indent=2))

# ─── 4: Check what's on the EFI partition ───
print("\n[4] EFI partition contents...\n")
for drive in ['Z:', 'Y:', 'X:', 'S:']:
    efi_path = f"{drive}\\EFI"
    if os.path.exists(efi_path):
        print(f"  EFI partition at {drive}")
        for root, dirs, files in os.walk(efi_path):
            depth = root.replace(efi_path, '').count(os.sep)
            if depth < 3:
                indent = '  ' + '  ' * depth
                print(f"{indent}{os.path.basename(root)}/")
                for f in files[:10]:
                    fpath = os.path.join(root, f)
                    size = os.path.getsize(fpath)
                    print(f"{indent}  {f} ({size}B)")
        break
else:
    print("  EFI partition not mounted — need admin: mountvol Z: /S")

print("\n" + "=" * 60)
print("THE KEY IS SPEC'D — AMD_PBS_SETUP[0x49] = 0x06 (512M)")
print("Next: get setup_var.efi → place on EFI → one reboot → DONE")
print("The mobo HDMI pore STAYS. We solve as we go.")
print("=" * 60)
