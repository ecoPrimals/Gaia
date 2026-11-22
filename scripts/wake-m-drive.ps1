# WAKE M: DRIVE — Samsung 990 PRO 4TB
# Root port 0:1.3 is OK but controller won't init
# Above4G=0 and FastBoot=1 are the root cause
# But let's try EVERYTHING we can from Windows first

Write-Host "=== WAKE M: DRIVE — Samsung 4TB ===" -ForegroundColor Cyan

# 1. Current disk state
Write-Host "`n--- Physical Disks ---"
Get-PhysicalDisk | Format-Table FriendlyName, MediaType, HealthStatus, OperationalStatus, Size, BusType -AutoSize

# 2. Current volumes
Write-Host "--- Volumes / Drive Letters ---"
Get-Volume | Where-Object DriveLetter | Format-Table DriveLetter, FileSystemLabel, FileSystem, Size, SizeRemaining -AutoSize

# 3. Disk Management view
Write-Host "--- All Disks (Get-Disk) ---"
Get-Disk | Format-Table Number, FriendlyName, OperationalStatus, HealthStatus, Size, PartitionStyle -AutoSize

# 4. NVMe controllers
Write-Host "--- NVMe PnP Devices ---"
Get-PnpDevice -Class SCSIAdapter | Where-Object { $_.FriendlyName -match "NVM" } | Format-Table FriendlyName, Status, InstanceId -AutoSize

# 5. Try hardware scan / rescan
Write-Host "--- Attempting PnP rescan ---"
try {
    $devcon = "pnputil /scan-devices"
    $result = Invoke-Expression $devcon 2>&1
    Write-Host "  pnputil scan: $result"
} catch {
    Write-Host "  pnputil error: $_"
}

# 6. Check root ports again
Write-Host "`n--- Root Port 0:1.3 (Samsung 4TB) ---"
$rp = Get-PnpDevice | Where-Object { $_.InstanceId -match "0B$" -and $_.FriendlyName -match "Root Port" }
if ($rp) {
    Write-Host "  Status: $($rp.Status)"
    Write-Host "  Instance: $($rp.InstanceId)"
    
    # Try disable/re-enable the root port
    Write-Host "  Attempting disable/re-enable cycle..."
    try {
        Disable-PnpDevice -InstanceId $rp.InstanceId -Confirm:$false -ErrorAction Stop
        Start-Sleep -Seconds 2
        Enable-PnpDevice -InstanceId $rp.InstanceId -Confirm:$false -ErrorAction Stop
        Start-Sleep -Seconds 3
        
        $rpAfter = Get-PnpDevice -InstanceId $rp.InstanceId
        Write-Host "  After cycle: $($rpAfter.Status)" -ForegroundColor $(if($rpAfter.Status -eq "OK"){"Green"}else{"Yellow"})
    } catch {
        Write-Host "  Cycle error: $_" -ForegroundColor Yellow
    }
}

Write-Host "`n--- Root Port 0:1.4 (WD BLACK 4TB) ---"
$rp2 = Get-PnpDevice | Where-Object { $_.InstanceId -match "0C$" -and $_.FriendlyName -match "Root Port" }
if ($rp2) {
    Write-Host "  Status: $($rp2.Status)"
    Write-Host "  Instance: $($rp2.InstanceId)"
    
    Write-Host "  Attempting disable/re-enable cycle..."
    try {
        Disable-PnpDevice -InstanceId $rp2.InstanceId -Confirm:$false -ErrorAction Stop
        Start-Sleep -Seconds 2
        Enable-PnpDevice -InstanceId $rp2.InstanceId -Confirm:$false -ErrorAction Stop
        Start-Sleep -Seconds 3
        
        $rp2After = Get-PnpDevice -InstanceId $rp2.InstanceId
        Write-Host "  After cycle: $($rp2After.Status)" -ForegroundColor $(if($rp2After.Status -eq "OK"){"Green"}else{"Yellow"})
    } catch {
        Write-Host "  Cycle error: $_" -ForegroundColor Yellow
    }
}

# 7. Re-check NVMe after cycling
Write-Host "`n--- NVMe After Root Port Cycle ---"
Start-Sleep -Seconds 2
Get-PnpDevice -Class SCSIAdapter | Where-Object { $_.FriendlyName -match "NVM" } | Format-Table FriendlyName, Status -AutoSize
Get-PhysicalDisk | Format-Table FriendlyName, OperationalStatus, Size -AutoSize

# 8. Check if M: came back
$mDrive = Get-Volume -DriveLetter M -ErrorAction SilentlyContinue
if ($mDrive) {
    Write-Host "  M: DRIVE IS BACK! $($mDrive.FileSystemLabel) $([math]::Round($mDrive.Size/1GB))GB" -ForegroundColor Green
} else {
    Write-Host "  M: still not present. Need BIOS: Above4G=1, FastBoot=0" -ForegroundColor Yellow
}
