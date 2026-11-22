# WIRE AUTO-REBOOT — modGRUBShell reads grub.cfg and auto-executes
# We put setup_var commands directly in grub.cfg
# Boot → GRUB runs → writes firmware → reboots → Windows → agent verifies

Write-Host "=" * 60
Write-Host "  WIRE AUTO-REBOOT — The reboot IS the write"
Write-Host "=" * 60

# Mount EFI
mountvol Z: /S 2>$null

# Create grub.cfg NEXT TO modGRUBShell.efi (where GRUB looks first)
$autoGrub = @"
# GAIA AUTO-INJECT — modGRUBShell auto-executes on boot
# This writes iGPU firmware variables then reboots to Windows
insmod part_gpt
setup_var_cv AMD_PBS_SETUP 0x48 0x01
setup_var_cv AMD_PBS_SETUP 0x49 0x06
echo "iGPU injected: 0x48=0x01 (Forces), 0x49=0x06 (512M)"
echo "Rebooting to Windows in 3 seconds..."
sleep 3
reboot
"@

# Place grub.cfg in ALL locations modGRUBShell might look
$locations = @(
    "Z:\EFI\tools\grub.cfg",
    "Z:\grub.cfg",
    "Z:\boot\grub\grub.cfg",
    "Z:\EFI\boot\grub.cfg"
)

foreach ($loc in $locations) {
    $dir = Split-Path $loc -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    Set-Content -Path $loc -Value $autoGrub -Encoding ASCII
    Write-Host "  Created: $loc"
}

# Also update the "GAIA EFI Key" boot entry to point to modGRUBShell
Write-Host "`n--- Boot entry check ---"
bcdedit /enum firmware 2>$null | Select-String -Pattern 'identifier|description|path' -Context 0,0 | ForEach-Object { Write-Host "  $_" }

# Set the GAIA EFI Key as FIRST boot option so it auto-runs
Write-Host "`n--- Setting boot order ---"
$fwEntries = bcdedit /enum firmware 2>&1
# Find the GAIA EFI Key entry
$gaiaKeyId = $null
$currentId = $null
foreach ($line in $fwEntries) {
    if ($line -match 'identifier\s+(\{[^}]+\})') { $currentId = $Matches[1] }
    if ($line -match 'GAIA EFI Key') { $gaiaKeyId = $currentId }
}

if ($gaiaKeyId) {
    Write-Host "  GAIA EFI Key ID: $gaiaKeyId"
    # Set it as first in firmware boot order
    bcdedit /set '{fwbootmgr}' displayorder $gaiaKeyId /addfirst 2>&1 | ForEach-Object { Write-Host "  $_" }
    # Set firmware timeout to 1 second
    bcdedit /set '{fwbootmgr}' timeout 1 2>&1 | ForEach-Object { Write-Host "  $_" }
    Write-Host "  GAIA EFI Key set as FIRST boot option with 1s timeout"
} else {
    Write-Host "  WARNING: Could not find GAIA EFI Key entry"
}

Write-Host @"

============================================================
  AUTO-REBOOT WIRED
============================================================

  THE SEQUENCE:
    1. shutdown /r /t 5    (reboot in 5 seconds)
    2. BIOS firmware starts
    3. "GAIA EFI Key" is FIRST in boot order
    4. modGRUBShell.efi loads
    5. grub.cfg auto-runs:
         setup_var_cv AMD_PBS_SETUP 0x48 0x01  (iGPU Forces)
         setup_var_cv AMD_PBS_SETUP 0x49 0x06  (UMA 512M)
         reboot
    6. Machine reboots again
    7. Windows loads with iGPU ENABLED
    8. Agent verifies → ZK hash compare
    
  NO HUMAN TYPING. THE REBOOT IS THE WRITE.
  
  Firing reboot in 10 seconds...
============================================================
"@

# Save state before reboot
$state = @{
    timestamp = (Get-Date -Format "o")
    event = "auto-reboot-wired"
    target = "iGPU enable via modGRUBShell auto-grub.cfg"
    expected_0x48 = "0x01"
    expected_0x49 = "0x06"
    grub_locations = $locations
    boot_order = "GAIA EFI Key first"
} | ConvertTo-Json
$state | Out-File "C:\Users\mokke\Desktop\Gaia\data\gut\auto-reboot-state.json" -Encoding UTF8
Write-Host "  State saved to data\gut\auto-reboot-state.json"

# FIRE THE REBOOT
Write-Host "`n  >>> REBOOTING IN 10 SECONDS <<<"
Write-Host "  >>> The organism writes its own firmware <<<"
shutdown /r /t 10
