# DEEP POST-REBOOT SCAN — What REALLY changed?

Write-Output "=== ALL DISKS (including hidden) ==="
Get-Disk | Format-Table Number,FriendlyName,@{N='SizeGB';E={[math]::Round($_.Size/1GB)}},PartitionStyle,OperationalStatus,BusType -AutoSize

Write-Output "`n=== ALL VOLUMES ==="
Get-Volume | Format-Table DriveLetter,FileSystemLabel,@{N='SizeGB';E={[math]::Round($_.Size/1GB)}},FileSystem,DriveType,HealthStatus -AutoSize

Write-Output "`n=== PCI DEVICES (NVMe + storage) ==="
Get-PnpDevice | Where-Object { $_.FriendlyName -match 'NVMe|Samsung|Storage|AHCI|4TB' } | Format-Table FriendlyName,Status,InstanceId -AutoSize

Write-Output "`n=== ALL DISPLAY ADAPTERS ==="
Get-PnpDevice -Class Display | Format-Table FriendlyName,Status,InstanceId -AutoSize

Write-Output "`n=== MONITORS ==="
Get-PnpDevice -Class Monitor | Format-Table FriendlyName,Status -AutoSize

Write-Output "`n=== SCREENS ==="
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Screen]::AllScreens | ForEach-Object { 
    Write-Output "  $($_.DeviceName) $($_.Bounds.Width)x$($_.Bounds.Height) Primary=$($_.Primary)"
}

Write-Output "`n=== CPU (full) ==="
Get-CimInstance Win32_Processor | Format-List Name,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed,L2CacheSize,L3CacheSize

Write-Output "`n=== NVIDIA GPU DETAILS ==="
nvidia-smi --query-gpu=name,pci.bus_id,memory.total,memory.free,pstate --format=csv,noheader 2>$null

Write-Output "`n=== PCI BAR SIZES (ReBAR check) ==="
nvidia-smi -q 2>$null | Select-String -Pattern 'BAR1|Resizable|rBAR'

Write-Output "`n=== ALL ASUS WMI READS ==="
$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement
$settings = @(
    'Above4GDecoding','ResizableBar','FastBoot','SvmMode',
    'CsmSupport','IntegratedGraphics','UmaFrameBufferSize',
    'SmtControl','PrimaryDisplay','SataMode',
    'ErpReady','SecureBoot','PlatformTrustTechnology',
    'XmpProfile','AboveNvmeRaid'
)
foreach ($s in $settings) {
    try {
        $r = Invoke-CimMethod -InputObject $inst -MethodName GetOptionData -Arguments @{OptionName=$s}
        Write-Output "  $s = $($r.Value) (err=$($r.ErrorCode))"
    } catch {
        Write-Output "  $s = N/A"
    }
}

Write-Output "`n=== PHYSICAL DISKS (WMI) ==="
Get-CimInstance MSFT_PhysicalDisk -Namespace root/Microsoft/Windows/Storage | Format-Table FriendlyName,@{N='SizeGB';E={[math]::Round($_.Size/1GB)}},MediaType,BusType,HealthStatus -AutoSize

Write-Output "`n=== DEVICE MANAGER — DISK DRIVES ==="
Get-PnpDevice -Class DiskDrive | Format-Table FriendlyName,Status -AutoSize
