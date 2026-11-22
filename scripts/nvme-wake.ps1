# NVME WAKE — Enable the ghost drives NOW
Write-Host "=== NVME WAKE — ENABLING GHOST DRIVES ==="

# Find the ghost NVMe controllers
Write-Host "`n--- Ghost NVMe controllers ---"
$ghosts = Get-PnpDevice | Where-Object { $_.Status -eq 'Unknown' -and ($_.FriendlyName -match 'NVM Express|SN850X|990 PRO 4TB') }
foreach ($g in $ghosts) {
    Write-Host "  GHOST: $($g.InstanceId)"
    Write-Host "         $($g.FriendlyName) [$($g.Status)]"
}

# Also find ghost SCSI disks
$ghostDisks = Get-PnpDevice | Where-Object { $_.Status -eq 'Unknown' -and $_.FriendlyName -match 'SN850X|990 PRO 4TB' }
foreach ($g in $ghostDisks) {
    Write-Host "  GHOST DISK: $($g.InstanceId)"
    Write-Host "              $($g.FriendlyName) [$($g.Status)]"
}

# Enable the NVMe controllers first
Write-Host "`n--- Enabling ghost NVMe controllers ---"
$controllers = Get-PnpDevice | Where-Object { $_.Status -eq 'Unknown' -and $_.FriendlyName -match 'NVM Express' }
foreach ($c in $controllers) {
    Write-Host "  Enabling: $($c.FriendlyName)"
    Write-Host "  ID: $($c.InstanceId)"
    try {
        Enable-PnpDevice -InstanceId $c.InstanceId -Confirm:$false -ErrorAction Stop
        Write-Host "  RESULT: ENABLED!" -ForegroundColor Green
    } catch {
        Write-Host "  RESULT: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Start-Sleep -Seconds 3

# Check if drives appeared
Write-Host "`n--- After enable: checking disks ---"
Get-PnpDevice | Where-Object { $_.FriendlyName -match 'SN850X|990 PRO 4TB|NVM Express' } |
    Format-Table InstanceId, FriendlyName, Status -AutoSize

# Try enabling the disk devices too
Write-Host "--- Enabling ghost disk devices ---"
$ghostDisks2 = Get-PnpDevice | Where-Object { $_.Status -eq 'Unknown' -and $_.FriendlyName -match 'SN850X|990 PRO 4TB' }
foreach ($d in $ghostDisks2) {
    Write-Host "  Enabling: $($d.FriendlyName)"
    try {
        Enable-PnpDevice -InstanceId $d.InstanceId -Confirm:$false -ErrorAction Stop
        Write-Host "  RESULT: ENABLED!" -ForegroundColor Green
    } catch {
        Write-Host "  RESULT: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Start-Sleep -Seconds 3

# Final check
Write-Host "`n--- FINAL STATE ---"
Get-PhysicalDisk | Format-Table DeviceId, FriendlyName, MediaType, Size, HealthStatus, BusType -AutoSize

Write-Host "`n--- All NVMe devices ---"
Get-PnpDevice | Where-Object { $_.FriendlyName -match 'NVMe|SN850X|990 PRO' } |
    Format-Table InstanceId, FriendlyName, Status, Class -AutoSize

# Check volumes
Write-Host "--- Volumes ---"
Get-Volume | Where-Object { $_.DriveLetter -or $_.Size -gt 1GB } |
    Format-Table DriveLetter, FileSystemLabel, FileSystem, @{N='SizeGB';E={[math]::Round($_.Size/1GB,1)}}, HealthStatus -AutoSize

Write-Host "`n=== NVME WAKE COMPLETE ==="
