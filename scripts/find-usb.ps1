# Find USB stick + check all drives
Write-Host "--- ALL DISKS ---"
Get-Disk | Select-Object Number, FriendlyName, BusType, @{N="SizeGB";E={[math]::Round($_.Size/1GB,1)}}, PartitionStyle, OperationalStatus | Format-Table -AutoSize

Write-Host "--- ALL VOLUMES ---"
Get-Volume | Select-Object DriveLetter, FileSystemLabel, FileSystem, @{N="SizeGB";E={[math]::Round($_.Size/1GB,2)}}, @{N="FreeGB";E={[math]::Round($_.SizeRemaining/1GB,2)}}, DriveType, HealthStatus | Format-Table -AutoSize

Write-Host "--- DISK DRIVES (PnP) ---"
Get-PnpDevice -Class DiskDrive -Status OK | Select-Object FriendlyName, InstanceId | Format-Table -AutoSize

Write-Host "--- REMOVABLE DRIVES ---"
foreach ($d in [System.IO.DriveInfo]::GetDrives()) {
    if ($d.DriveType -eq 'Removable' -and $d.IsReady) {
        Write-Host "  $($d.Name) Format=$($d.DriveFormat) Size=$([math]::Round($d.TotalSize/1GB,2))GB Free=$([math]::Round($d.AvailableFreeSpace/1GB,2))GB"
    }
}

Write-Host "--- USB STORAGE DEVICES ---"
Get-PnpDevice -Status OK | Where-Object { $_.InstanceId -match 'USBSTOR|USB\\VID' -and $_.Class -eq 'DiskDrive' } | Select-Object FriendlyName, InstanceId | Format-Table -AutoSize

Write-Host "--- UNALLOCATED SPACE ---"
$disk = Get-Disk -Number 0
$usedBytes = (Get-Partition -DiskNumber 0 | Measure-Object -Property Size -Sum).Sum
$freeGB = [math]::Round(($disk.Size - $usedBytes)/1GB, 1)
Write-Host "  Disk 0 total: $([math]::Round($disk.Size/1GB,1)) GB"
Write-Host "  Partitions use: $([math]::Round($usedBytes/1GB,1)) GB"
Write-Host "  UNALLOCATED: $freeGB GB  <-- ready for Linux dual boot!"
