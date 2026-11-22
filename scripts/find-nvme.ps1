# WHERE ARE THE OTHER NVMe DRIVES?
Write-Host "=" * 60
Write-Host "  NVMe HUNT - Where are the 2x 4TB drives?"
Write-Host "=" * 60

Write-Host "`n--- ALL DISKS (Get-Disk) ---"
Get-Disk | Select-Object Number, FriendlyName, BusType, @{N="SizeGB";E={[math]::Round($_.Size/1GB,1)}}, PartitionStyle, OperationalStatus, IsOffline | Format-Table -AutoSize

Write-Host "`n--- ALL DISK DRIVES (PnP - any status) ---"
Get-PnpDevice -Class DiskDrive | Select-Object FriendlyName, Status, InstanceId | Format-Table -AutoSize

Write-Host "`n--- NVMe CONTROLLERS ---"
Get-PnpDevice | Where-Object { $_.FriendlyName -match 'NVMe|NVM Express|Storage Controller' } | Select-Object FriendlyName, Status, Class, InstanceId | Format-Table -AutoSize

Write-Host "`n--- STORAGE CONTROLLERS ---"
Get-PnpDevice -Class SCSIAdapter -Status OK | Select-Object FriendlyName, InstanceId | Format-Table -AutoSize

Write-Host "`n--- PCIe STORAGE DEVICES (all states) ---"
Get-PnpDevice | Where-Object { $_.InstanceId -match 'NVME|VEN_144D|VEN_1987|VEN_15B7|VEN_C0A9|VEN_1E0F|PROD_SSD' } | Select-Object FriendlyName, Status, InstanceId | Format-Table -AutoSize

Write-Host "`n--- OFFLINE / ERROR DISKS ---"
Get-Disk | Where-Object { $_.OperationalStatus -ne 'Online' -or $_.IsOffline -eq $true } | Select-Object Number, FriendlyName, @{N="SizeGB";E={[math]::Round($_.Size/1GB,1)}}, OperationalStatus, IsOffline, HealthStatus | Format-Table -AutoSize

Write-Host "`n--- BitLocker Status (Secure Boot change can lock drives!) ---"
Get-BitLockerVolume -ErrorAction SilentlyContinue | Select-Object MountPoint, VolumeStatus, ProtectionStatus, LockStatus, EncryptionMethod | Format-Table -AutoSize

Write-Host "`n--- Disk Management raw view ---"
Get-CimInstance Win32_DiskDrive | Select-Object Caption, DeviceID, @{N="SizeGB";E={[math]::Round($_.Size/1GB,1)}}, InterfaceType, Status, MediaType, Partitions | Format-Table -AutoSize

Write-Host "`n--- Physical NVMe namespaces ---"
Get-PhysicalDisk | Select-Object FriendlyName, MediaType, BusType, @{N="SizeGB";E={[math]::Round($_.Size/1GB,1)}}, HealthStatus, OperationalStatus | Format-Table -AutoSize

Write-Host "`n--- Device Manager PROBLEM devices ---"
Get-PnpDevice | Where-Object { $_.Status -eq 'Error' -or $_.Status -eq 'Degraded' -or $_.Status -eq 'Unknown' } | Where-Object { $_.Class -match 'Disk|Storage|SCSI|Volume' } | Select-Object FriendlyName, Status, Class, InstanceId | Format-Table -AutoSize

Write-Host "`n--- Recent disk events ---"
$cutoff = (Get-Date).AddMinutes(-30)
Get-WinEvent -FilterHashtable @{LogName='System'; StartTime=$cutoff} -ErrorAction SilentlyContinue | Where-Object { $_.Message -match 'disk|nvme|storage|drive|volume|bitlocker|mount' } | Select-Object -First 10 TimeCreated, Id, Message | Format-List
