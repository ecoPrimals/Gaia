# Rescan and wake NVMe drives post-reboot
Write-Output "=== FORCING DISK RESCAN ==="
Update-StorageProviderCache -ErrorAction SilentlyContinue
"rescan" | diskpart 2>$null

Write-Output "`n=== ALL DISKS ==="
Get-Disk | Format-Table Number,FriendlyName,@{N='SizeGB';E={[math]::Round($_.Size/1GB)}},OperationalStatus,HealthStatus,BusType -AutoSize

Write-Output "`n=== ALL DISK DRIVES (Device Manager) ==="
Get-PnpDevice -Class DiskDrive | Format-Table FriendlyName,Status -AutoSize

Write-Output "`n=== NVMe CONTROLLERS ==="
Get-PnpDevice | Where-Object { $_.FriendlyName -match 'NVMe' } | Format-Table FriendlyName,Status,InstanceId -AutoSize

Write-Output "`n=== UNKNOWN/ERROR DEVICES ==="
Get-PnpDevice -Class DiskDrive | Where-Object { $_.Status -ne 'OK' } | ForEach-Object {
    Write-Output "  $($_.FriendlyName) [$($_.Status)]"
    $prob = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_ProblemCode' -ErrorAction SilentlyContinue).Data
    $desc = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_ProblemDescription' -ErrorAction SilentlyContinue).Data
    Write-Output "    ProblemCode: $prob"
    Write-Output "    ProblemDesc: $desc"
    Write-Output "    InstanceId: $($_.InstanceId)"
}

Write-Output "`n=== TRY ENABLE UNKNOWN DRIVES ==="
Get-PnpDevice -Class DiskDrive | Where-Object { $_.Status -ne 'OK' } | ForEach-Object {
    Write-Output "  Enabling: $($_.FriendlyName)..."
    Enable-PnpDevice -InstanceId $_.InstanceId -Confirm:$false -ErrorAction SilentlyContinue
}

Start-Sleep -Seconds 2

Write-Output "`n=== DISKS AFTER ENABLE ==="
Get-Disk | Format-Table Number,FriendlyName,@{N='SizeGB';E={[math]::Round($_.Size/1GB)}},OperationalStatus -AutoSize

Write-Output "`n=== VOLUMES AFTER ==="
Get-Volume | Where-Object { $_.DriveLetter } | Format-Table DriveLetter,FileSystemLabel,@{N='SizeGB';E={[math]::Round($_.Size/1GB)}},FileSystem -AutoSize
