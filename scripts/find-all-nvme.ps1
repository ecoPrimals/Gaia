Write-Host "=" * 60
Write-Host "  FIND ALL NVMe — Every stick on this body"
Write-Host "=" * 60

# Physical disks
Write-Host "`n--- Physical Disks ---"
Get-PhysicalDisk | Format-Table FriendlyName, MediaType, Size, HealthStatus, OperationalStatus, BusType -AutoSize

# Disk drives (WMI)
Write-Host "`n--- WMI Disk Drives ---"
Get-CimInstance Win32_DiskDrive | Format-Table Caption, Model, Size, Status, InterfaceType, MediaType, Index -AutoSize

# NVMe controllers (PnP)
Write-Host "`n--- NVMe Controllers (PnP) ---"
Get-PnpDevice -Class 'SCSIAdapter' -ErrorAction SilentlyContinue | Where-Object { $_.FriendlyName -match 'NVMe|Samsung|WD|Western' } | Format-Table FriendlyName, Status, InstanceId -AutoSize

# ALL storage controllers
Write-Host "`n--- ALL Storage Controllers ---"
Get-PnpDevice -Class 'SCSIAdapter' -ErrorAction SilentlyContinue | Format-Table FriendlyName, Status, InstanceId -AutoSize

# Disk Management view
Write-Host "`n--- Disks from Get-Disk ---"
Get-Disk | Format-Table Number, FriendlyName, Size, PartitionStyle, OperationalStatus, HealthStatus, BusType -AutoSize

# Partitions
Write-Host "`n--- All Partitions ---"
Get-Partition | Format-Table DiskNumber, PartitionNumber, DriveLetter, Size, Type -AutoSize

# Volumes
Write-Host "`n--- All Volumes ---"
Get-Volume | Where-Object { $_.DriveLetter -or $_.FileSystemLabel } | Format-Table DriveLetter, FileSystemLabel, Size, SizeRemaining, FileSystem, HealthStatus -AutoSize

# Missing drive letters from registry
Write-Host "`n--- Registry Drive Letters (MountedDevices) ---"
$mounted = Get-ItemProperty 'HKLM:\SYSTEM\MountedDevices' -ErrorAction SilentlyContinue
if ($mounted) {
    $mounted.PSObject.Properties | Where-Object { $_.Name -match '\\DosDevices\\' } | ForEach-Object {
        $letter = $_.Name -replace '.*\\', ''
        Write-Host "  $letter → (mapped)"
    }
}

# PCIe devices - look for NVMe on bus
Write-Host "`n--- PCIe NVMe Devices (including dead) ---"
Get-PnpDevice | Where-Object { $_.InstanceId -match 'NVME|VEN_144D|VEN_15B7|1C5C|Samsung|WD_BLACK' } | Format-Table FriendlyName, Status, Class, InstanceId -AutoSize

# Broader: ALL PCI devices that are Unknown or Error
Write-Host "`n--- Unknown/Error PCI Devices ---"
Get-PnpDevice | Where-Object { ($_.Status -eq 'Unknown' -or $_.Status -eq 'Error') -and $_.InstanceId -match 'PCI' } | Format-Table FriendlyName, Status, Class, InstanceId -AutoSize

# DeviceManager storage view
Write-Host "`n--- Storage Namespaces ---"
Get-PnpDevice -Class 'DiskDrive' -ErrorAction SilentlyContinue | Format-Table FriendlyName, Status, InstanceId -AutoSize

# Steam library config
Write-Host "`n--- Steam Library Folders ---"
$steamConfig = "C:\Program Files (x86)\Steam\config\libraryfolders.vdf"
if (Test-Path $steamConfig) {
    Write-Host "  Steam config exists!"
    Get-Content $steamConfig | Select-String -Pattern '"path"|"totalsize"|"label"' | ForEach-Object { Write-Host "  $_" }
} else {
    Write-Host "  No Steam config found"
}

# Check M: drive specifically
Write-Host "`n--- M: Drive Check ---"
if (Test-Path "M:\") {
    Write-Host "  M: ALIVE!"
    Get-ChildItem "M:\" -ErrorAction SilentlyContinue | Select-Object -First 10
} else {
    Write-Host "  M: NOT ACCESSIBLE"
}

Write-Host "`n" + "=" * 60
Write-Host "  NVMe HUNT COMPLETE"  
Write-Host "=" * 60
