# NVME ENUMERATE — Self-enumerate all storage from northGate
# toadStool pattern: discover ALL, even the ghosts
# Why can't we see 2x 4TB NVMe? Let's find out.

Write-Host "=== NVME SELF-ENUMERATE — NORTHGATE ==="
Write-Host ""

# 1. Physical Disks
Write-Host "--- PHYSICAL DISKS ---"
Get-PhysicalDisk | Format-Table DeviceId, FriendlyName, MediaType, Size, HealthStatus, BusType -AutoSize

# 2. ALL Disk drives (WMI)
Write-Host "--- WMI DISK DRIVES ---"
Get-CimInstance Win32_DiskDrive | Format-Table Caption, Size, InterfaceType, Status, Model, SerialNumber -AutoSize

# 3. NVMe controllers specifically
Write-Host "--- NVME CONTROLLERS ---"
Get-CimInstance -Namespace root\Microsoft\Windows\Storage -ClassName MSFT_PhysicalDisk | 
    Select-Object FriendlyName, Size, MediaType, BusType, HealthStatus, DeviceId, UniqueId |
    Format-Table -AutoSize

# 4. PCI Bus — ALL devices
Write-Host "--- PCI ROOT PORTS (Bus 0, looking for NVMe hosts) ---"
Get-PnpDevice -Class "System" -Status OK | Where-Object { $_.FriendlyName -match "PCI|Root Port|NVMe" } |
    Format-Table InstanceId, FriendlyName, Status -AutoSize

# 5. ALL PnP storage devices
Write-Host "--- PNP STORAGE DEVICES ---"
Get-PnpDevice -Class "DiskDrive" | Format-Table InstanceId, FriendlyName, Status -AutoSize
Get-PnpDevice -Class "SCSIAdapter" | Format-Table InstanceId, FriendlyName, Status -AutoSize

# 6. NVMe namespaces
Write-Host "--- STORAGE CONTROLLERS ---"
Get-PnpDevice | Where-Object { $_.FriendlyName -match "NVMe|Samsung|WD|Western Digital|SSD|4TB" } |
    Format-Table InstanceId, FriendlyName, Status, Class -AutoSize

# 7. PCIe topology — root ports
Write-Host "--- PCIE ROOT PORT TOPOLOGY ---"
$rootPorts = Get-PnpDevice | Where-Object { $_.FriendlyName -match "Root Port" }
foreach ($rp in $rootPorts) {
    $children = Get-PnpDevice | Where-Object { $_.InstanceId -like "$($rp.InstanceId.Substring(0,20))*" -and $_.InstanceId -ne $rp.InstanceId }
    $childNames = if ($children) { ($children | Select-Object -ExpandProperty FriendlyName) -join ", " } else { "(EMPTY)" }
    Write-Host "  $($rp.FriendlyName) [$($rp.Status)] -> $childNames"
}

# 8. Check for ERROR/UNKNOWN devices
Write-Host ""
Write-Host "--- ERROR/UNKNOWN DEVICES ---"
Get-PnpDevice -Status Error 2>$null | Format-Table InstanceId, FriendlyName, Status, Class -AutoSize
Get-PnpDevice -Status Unknown 2>$null | Format-Table InstanceId, FriendlyName, Status, Class -AutoSize
Get-PnpDevice -Status Degraded 2>$null | Format-Table InstanceId, FriendlyName, Status, Class -AutoSize

# 9. Volumes / partitions
Write-Host "--- VOLUMES ---"
Get-Volume | Where-Object { $_.DriveLetter -or $_.FileSystemLabel } |
    Format-Table DriveLetter, FileSystemLabel, FileSystem, Size, SizeRemaining, HealthStatus -AutoSize

# 10. Device Manager hidden devices  
Write-Host "--- HIDDEN/PHANTOM STORAGE ---"
Get-PnpDevice -Class "DiskDrive" -Status OK | ForEach-Object {
    $size = (Get-Disk -Number ($_.DeviceID -replace '.*PHYSICALDRIVE','') -ErrorAction SilentlyContinue).Size
    Write-Host "  $($_.FriendlyName): $([math]::Round($size / 1GB, 1)) GB"
}

# 11. Raw PCIe enumeration via PowerShell
Write-Host ""
Write-Host "--- RAW PCIE BUS SCAN ---"
$pciDevices = Get-CimInstance Win32_PnPEntity | Where-Object { $_.DeviceID -match "^PCI\\\\VEN_" }
$nvmeDevices = $pciDevices | Where-Object { $_.Name -match "NVMe|Non-Volatile|SSD|Samsung|Western" }
Write-Host "  Total PCI devices: $($pciDevices.Count)"
Write-Host "  NVMe-related: $($nvmeDevices.Count)"
foreach ($d in $nvmeDevices) {
    Write-Host "  $($d.DeviceID) = $($d.Name) [$($d.Status)]"
}

# 12. BIOS slots / physical slots
Write-Host ""
Write-Host "--- M.2 SLOT INFO ---"
$slots = Get-CimInstance Win32_SystemSlot
$m2 = $slots | Where-Object { $_.SlotDesignation -match "M.2|NVMe|PCIE|SSD" }
Write-Host "  Total system slots: $($slots.Count)"
foreach ($s in $m2) {
    Write-Host "  $($s.SlotDesignation): $($s.CurrentUsage) [Tag: $($s.Tag)]"
}
if (-not $m2) {
    Write-Host "  No M.2 slots reported by BIOS (may not expose)"
    foreach ($s in $slots) {
        Write-Host "  $($s.SlotDesignation): $($s.CurrentUsage)"
    }
}

Write-Host ""
Write-Host "=== ENUMERATE COMPLETE ==="
