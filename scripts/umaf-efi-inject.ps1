# INJECT UMAF INTO EFI PARTITION — No USB needed!
# Mount the EFI System Partition, copy UMAF files, boot from BIOS
Write-Host "=" * 60
Write-Host "  UMAF EFI INJECTION — bypass USB entirely"
Write-Host "=" * 60

# Step 1: Mount EFI partition
Write-Host "`n--- Mounting EFI System Partition ---"
$efiPart = Get-Partition | Where-Object { $_.Type -eq 'System' }
if ($efiPart) {
    Write-Host "  Found EFI partition: Disk $($efiPart.DiskNumber) Part $($efiPart.PartitionNumber) Size=$([math]::Round($efiPart.Size/1MB))MB"
    
    # Assign drive letter Z: to EFI
    mountvol Z: /S 2>&1
    Start-Sleep 1
    
    if (Test-Path 'Z:\') {
        Write-Host "  Mounted at Z:\"
        
        # Show current EFI contents
        Write-Host "`n--- Current EFI contents ---"
        Get-ChildItem Z:\ -Recurse -Depth 2 | Select-Object FullName, Length | Format-Table -AutoSize
        
        # Step 2: Copy UMAF files
        $umafDir = 'C:\Users\mokke\Desktop\Gaia\data\tools\UMAF'
        if (Test-Path $umafDir) {
            Write-Host "`n--- Copying UMAF to EFI partition ---"
            
            # Create UMAF boot folder
            New-Item -ItemType Directory -Force 'Z:\EFI\UMAF' | Out-Null
            
            # Copy the EFI files
            Copy-Item "$umafDir\EFI\Boot\Bootx64.efi" 'Z:\EFI\UMAF\Bootx64.efi' -Force
            Copy-Item "$umafDir\UiApp.efi" 'Z:\EFI\UMAF\UiApp.efi' -Force
            Copy-Item "$umafDir\SetupBrowser.efi" 'Z:\EFI\UMAF\SetupBrowser.efi' -Force
            Copy-Item "$umafDir\DisplayEngine.efi" 'Z:\EFI\UMAF\DisplayEngine.efi' -Force
            
            # Also copy to root for direct boot
            Copy-Item "$umafDir\UiApp.efi" 'Z:\UiApp.efi' -Force
            Copy-Item "$umafDir\SetupBrowser.efi" 'Z:\SetupBrowser.efi' -Force
            Copy-Item "$umafDir\DisplayEngine.efi" 'Z:\DisplayEngine.efi' -Force
            
            Write-Host "  UMAF files copied!"
            Write-Host "`n--- EFI partition now ---"
            Get-ChildItem Z:\ -Recurse -Depth 3 | Where-Object { -not $_.PSIsContainer } | Select-Object FullName, Length | Format-Table -AutoSize
            
            # Step 3: Create UEFI boot entry for UMAF
            Write-Host "`n--- Creating UEFI boot entry ---"
            $bcdedit = bcdedit /copy '{bootmgr}' /d "Smokeless UMAF" 2>&1
            Write-Host "  $bcdedit"
            
            Write-Host "`n  INSTRUCTIONS:"
            Write-Host "  1. Reboot, press F8 (or DEL then Boot Menu)"
            Write-Host "  2. Select 'UEFI Shell' or look for UMAF entry"
            Write-Host "  3. If UEFI Shell: type 'fs0:' then 'UiApp.efi'"
            Write-Host "  4. OR from BIOS: Boot from file -> EFI\UMAF\Bootx64.efi"
            Write-Host "  5. Device Manager -> AMD CBS -> NBIO -> GFX Config"
            Write-Host "  6. iGPU = Forces, UMA = UMA_SPECIFIED, Size = 512M"
            Write-Host "  7. ESC ESC ESC -> Save -> Reboot"
        } else {
            Write-Host "  UMAF not found at $umafDir — run the download script first!"
        }
    } else {
        Write-Host "  Failed to mount at Z: — trying diskpart..."
        # Fallback: use diskpart
        $dp = @"
select disk 0
select partition 1
assign letter=Z
"@
        $dp | diskpart
        Start-Sleep 2
        if (Test-Path 'Z:\') {
            Write-Host "  Mounted via diskpart at Z:\"
        } else {
            Write-Host "  FAILED to mount EFI partition"
        }
    }
} else {
    Write-Host "  No EFI system partition found!"
}

# Also check the NVMe situation
Write-Host "`n--- NVMe M.2 slot status (BIOS investigation needed) ---"
Write-Host "  The 2x 4TB drives have DEAD PCIe controllers."
Write-Host "  This needs checking in BIOS: Advanced -> Onboard Devices"
Write-Host "  or Advanced -> NVMe Configuration"
Write-Host "  M.2 slots may need re-enabling after Secure Boot change"
