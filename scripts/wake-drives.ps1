# WAKE THE SLEEPING DRIVES
Write-Host "Attempting to re-enable NVMe controllers and USB drives..."

# Disable then re-enable the dead NVMe controllers
$deadDevices = Get-PnpDevice | Where-Object { 
    $_.Status -eq 'Unknown' -and ($_.Class -eq 'SCSIAdapter' -or $_.Class -eq 'DiskDrive') -and
    $_.InstanceId -match 'NVME|VEN_144D|VEN_15B7|SN850X|990_PRO|USBSTOR|USB_DISK'
}

foreach ($dev in $deadDevices) {
    Write-Host "`n  Device: $($dev.FriendlyName) [$($dev.Status)]"
    Write-Host "  ID: $($dev.InstanceId)"
    try {
        Write-Host "  Attempting Enable..."
        Enable-PnpDevice -InstanceId $dev.InstanceId -Confirm:$false -ErrorAction Stop
        Write-Host "  -> Enabled!"
    } catch {
        Write-Host "  -> Enable failed: $($_.Exception.Message)"
        try {
            Write-Host "  Attempting Disable then Enable..."
            Disable-PnpDevice -InstanceId $dev.InstanceId -Confirm:$false -ErrorAction Stop
            Start-Sleep 1
            Enable-PnpDevice -InstanceId $dev.InstanceId -Confirm:$false -ErrorAction Stop
            Write-Host "  -> Re-enabled!"
        } catch {
            Write-Host "  -> Failed: $($_.Exception.Message)"
        }
    }
}

Write-Host "`n--- Rescanning hardware ---"
$scanResult = pnputil /scan-devices
Write-Host $scanResult

Start-Sleep 3

Write-Host "`n--- Results ---"
Get-Disk | Select-Object Number, FriendlyName, @{N="SizeGB";E={[math]::Round($_.Size/1GB,1)}}, OperationalStatus | Format-Table -AutoSize
Get-PnpDevice -Class DiskDrive | Select-Object FriendlyName, Status | Format-Table -AutoSize
