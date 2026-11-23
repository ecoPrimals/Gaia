# Rescan drives — output to file
$out = "C:\Users\mokke\Desktop\Gaia\data\gut\rescan-result.txt"

$log = @()
$log += "=== FORCING DISK RESCAN ==="
Update-StorageProviderCache -ErrorAction SilentlyContinue

$log += "`n=== ALL DISKS ==="
$log += (Get-Disk | Format-Table Number,FriendlyName,@{N='SizeGB';E={[math]::Round($_.Size/1GB)}},OperationalStatus,HealthStatus,BusType -AutoSize | Out-String)

$log += "`n=== DISK DRIVES (Device Manager) ==="
$log += (Get-PnpDevice -Class DiskDrive | Format-Table FriendlyName,Status -AutoSize | Out-String)

$log += "`n=== NVMe CONTROLLERS ==="
$log += (Get-PnpDevice | Where-Object { $_.FriendlyName -match 'NVMe' } | Format-Table FriendlyName,Status,InstanceId -AutoSize | Out-String)

$log += "`n=== PROBLEM DEVICES ==="
Get-PnpDevice -Class DiskDrive | Where-Object { $_.Status -ne 'OK' } | ForEach-Object {
    $prob = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_ProblemCode' -ErrorAction SilentlyContinue).Data
    $log += "  $($_.FriendlyName) [$($_.Status)] Problem=$prob ID=$($_.InstanceId)"
}

$log += "`n=== ENABLING UNKNOWN DRIVES ==="
Get-PnpDevice -Class DiskDrive | Where-Object { $_.Status -ne 'OK' } | ForEach-Object {
    $log += "  Enabling: $($_.FriendlyName)..."
    try {
        Enable-PnpDevice -InstanceId $_.InstanceId -Confirm:$false -ErrorAction Stop
        $log += "    -> Enabled OK"
    } catch {
        $log += "    -> Error: $_"
    }
}

Start-Sleep -Seconds 3

$log += "`n=== DISKS AFTER ==="
$log += (Get-Disk | Format-Table Number,FriendlyName,@{N='SizeGB';E={[math]::Round($_.Size/1GB)}},OperationalStatus -AutoSize | Out-String)

$log += "`n=== VOLUMES AFTER ==="
$log += (Get-Volume | Where-Object { $_.DriveLetter } | Format-Table DriveLetter,FileSystemLabel,@{N='SizeGB';E={[math]::Round($_.Size/1GB)}},FileSystem -AutoSize | Out-String)

$log -join "`n" | Out-File -FilePath $out -Encoding utf8
