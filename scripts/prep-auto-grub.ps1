# PREP AUTO GRUB — Script the firmware changes, boot to GRUB, it types for Kevin
Write-Host "=" * 60
Write-Host "  PREP AUTO GRUB — The organism bootstraps itself"
Write-Host "=" * 60

# Mount EFI
mountvol Z: /S 2>$null

# Create the exact commands Kevin (or auto-script) needs to type in modGRUBShell
$commands = @"
# ============================================
# GAIA FIRMWARE INJECTION via modGRUBShell
# ============================================
# 
# CURRENT STATE (read from Windows):
#   0x48 = 0x00 (iGPU Auto/Disabled)
#   0x49 = 0xFF (UMA None)
#   0x4E = 0x02 (PCIE primary - correct)
#
# COMMANDS TO TYPE IN GRUB SHELL:
# (one line at a time, press Enter after each)
#
# Step 1: Enable iGPU
setup_var_cv AMD_PBS_SETUP 0x48 0x01
#
# Step 2: Set UMA to 512MB  
setup_var_cv AMD_PBS_SETUP 0x49 0x06
#
# Step 3: Verify (should show new values)
setup_var_cv AMD_PBS_SETUP 0x48
setup_var_cv AMD_PBS_SETUP 0x49
#
# Step 4: Reboot
reboot
#
# ============================================
# IF setup_var_cv doesn't work, try:
# setup_var 0x48 0x01
# setup_var 0x49 0x06  
# ============================================
"@

Set-Content -Path "Z:\EFI\UMAF\igpu-commands.txt" -Value $commands -Encoding ASCII
Write-Host "  Commands saved to Z:\EFI\UMAF\igpu-commands.txt"

# Create a GRUB config that auto-chains to modGRUBShell
$grubCfg = @"
set timeout=5
set default=0

menuentry "GAIA - Enable iGPU (modGRUBShell)" {
    chainloader /EFI/tools/modGRUBShell.efi
}

menuentry "GAIA - UMAF Browser" {
    chainloader /EFI/UMAF/Bootx64.efi
}

menuentry "Windows (normal boot)" {
    chainloader /EFI/Microsoft/Boot/bootmgfw.efi
}
"@

# Check if there's already a grub.cfg we can modify
if (Test-Path "Z:\EFI\UMAF\grub.cfg") {
    Write-Host "  Existing grub.cfg found"
}
Set-Content -Path "Z:\EFI\UMAF\grub.cfg" -Value $grubCfg -Encoding ASCII
Write-Host "  Created Z:\EFI\UMAF\grub.cfg"

# Verify everything on EFI
Write-Host "`n--- EFI Partition Ready ---"
Get-ChildItem Z:\EFI\UMAF -ErrorAction SilentlyContinue | ForEach-Object { Write-Host ("  " + $_.Name + " (" + $_.Length + " bytes)") }
Get-ChildItem Z:\EFI\tools -ErrorAction SilentlyContinue | ForEach-Object { Write-Host ("  tools\" + $_.Name + " (" + $_.Length + " bytes)") }

# Show what "GAIA EFI Key" boot entry does
Write-Host "`n--- Boot Entries ---"
bcdedit /enum firmware 2>$null | Select-String -Pattern 'description|path' | ForEach-Object { Write-Host "  $_" }

Write-Host @"

============================================================
  THE PLAN — Agent-driven firmware modification
============================================================

  WHAT WE KNOW:
    AMD_PBS_SETUP variable: READ ✅, WRITE ❌ (from Windows)
    Offset 0x48 = 0x00 → needs 0x01 (iGPU Forces)
    Offset 0x49 = 0xFF → needs 0x06 (UMA 512M)
    modGRUBShell.efi: ON EFI PARTITION ✅

  THE SOLVE:
    1. Kevin reboots (shutdown /r /fw /t 0)
    2. In BIOS: Boot from file → EFI\tools\modGRUBShell.efi
       OR select "GAIA EFI Key - UMA Unlock" from boot menu
    3. In GRUB shell, type TWO commands:
    
       setup_var_cv AMD_PBS_SETUP 0x48 0x01
       setup_var_cv AMD_PBS_SETUP 0x49 0x06
       reboot
       
    4. That's it. THREE lines typed. iGPU enables on next boot.
    
  AFTER REBOOT:
    - Agent runs ZK hardware scan
    - Compares hash to pre-inject state
    - iGPU should appear as new GPU device
    - Left eye opens

============================================================
"@
