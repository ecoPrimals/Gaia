# PREP REBIRTH — Make UMAF bootable without F-key fighting
# Option 1: bcdedit firmware boot entry for UMAF
# Option 2: shutdown /r /fw to go straight to UEFI firmware
# Option 3: Add UMAF to Windows Boot Manager

Write-Host "=" * 60
Write-Host "  PREP REBIRTH — NVMe 1TB EFI prep"
Write-Host "=" * 60

# Step 1: Mount EFI partition
Write-Host "`n--- Mounting EFI partition ---"
$efiPart = Get-Partition | Where-Object { $_.Type -eq 'System' }
if ($efiPart) {
    Write-Host "  EFI partition found: Disk $($efiPart.DiskNumber), Partition $($efiPart.PartitionNumber)"
    Write-Host "  Size: $([math]::Round($efiPart.Size / 1MB, 1)) MB"
    
    # Try to assign letter
    try {
        $efiPart | Set-Partition -NewDriveLetter Z -ErrorAction SilentlyContinue
    } catch {}
    
    # Check if mounted
    $letter = ($efiPart | Get-Volume -ErrorAction SilentlyContinue).DriveLetter
    if (-not $letter) {
        # mountvol
        mountvol Z: /S 2>$null
        $letter = 'Z'
    }
    Write-Host "  Mounted at: ${letter}:"
} else {
    Write-Host "  No EFI partition found, trying mountvol..."
    mountvol Z: /S 2>$null
    $letter = 'Z'
}

# Step 2: Verify UMAF files
Write-Host "`n--- Checking UMAF on EFI ---"
$umafPaths = @(
    "${letter}:\EFI\UMAF\Bootx64.efi",
    "${letter}:\Bootx64.efi",
    "${letter}:\EFI\tools\modGRUBShell.efi"
)
foreach ($p in $umafPaths) {
    if (Test-Path $p) {
        $size = (Get-Item $p).Length
        Write-Host "  FOUND: $p ($size bytes)"
    } else {
        Write-Host "  MISSING: $p"
    }
}

# Step 3: List current EFI boot entries
Write-Host "`n--- Current Boot Entries ---"
bcdedit /enum firmware 2>$null | Select-Object -First 40

# Step 4: Create UMAF boot entry
Write-Host "`n--- Creating UMAF boot entry ---"
try {
    # Create a new firmware boot entry
    $result = bcdedit /copy '{bootmgr}' /d "Smokeless UMAF" 2>&1
    Write-Host "  bcdedit copy: $result"
    
    # Extract the GUID
    if ($result -match '\{[^}]+\}') {
        $guid = $matches[0]
        Write-Host "  New entry GUID: $guid"
        
        # Set the path to UMAF EFI
        bcdedit /set $guid path \EFI\UMAF\Bootx64.efi 2>&1
        bcdedit /set $guid description "Smokeless UMAF (iGPU)" 2>&1
        
        # Add to firmware display order
        bcdedit /set '{fwbootmgr}' displayorder $guid /addlast 2>&1
        Write-Host "  UMAF added to boot menu!"
    }
} catch {
    Write-Host "  bcdedit failed: $($_.Exception.Message)"
}

# Step 5: List ALL EFI boot files on partition
Write-Host "`n--- All EFI files on partition ---"
Get-ChildItem -Path "${letter}:\EFI" -Recurse -Filter "*.efi" -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "  $($_.FullName) ($($_.Length) bytes)"
}

# Step 6: Check GRUB config
Write-Host "`n--- GRUB config ---"
$grubCfg = "${letter}:\EFI\ubuntu\grub.cfg"
if (Test-Path $grubCfg) {
    Write-Host "  GRUB config found at: $grubCfg"
    Get-Content $grubCfg -ErrorAction SilentlyContinue | Select-Object -First 20
} else {
    # Check other grub locations
    $grubPaths = Get-ChildItem -Path "${letter}:\" -Recurse -Filter "grub.cfg" -ErrorAction SilentlyContinue
    foreach ($g in $grubPaths) {
        Write-Host "  GRUB found: $($g.FullName)"
    }
}

# Step 7: Show the EASY reboot option
Write-Host "`n" + "=" * 60
Write-Host "  REBIRTH OPTIONS"
Write-Host "=" * 60
Write-Host @"

  OPTION A (EASIEST): Reboot straight to UEFI firmware
    shutdown /r /fw /t 0
    → Goes DIRECTLY to BIOS setup
    → Then: Boot tab → Boot from file → EFI\UMAF\Bootx64.efi

  OPTION B: F4 at POST (Kevin knows his board!)
    → Power off → Power on → F4 F4 F4
    → Select UMAF from boot menu

  OPTION C: If UMAF boot entry was created above
    → Should appear in F8/F4 boot menu automatically

  CURRENT: Run 'shutdown /r /fw /t 0' to test Option A!
"@
