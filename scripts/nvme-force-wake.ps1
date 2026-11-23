# Try to force-wake NVMe controllers without reboot
$out = "C:\Users\mokke\Desktop\Gaia\data\gut\nvme-wake-result.txt"
$log = @()

# 1. Try to restart the PCI Root Ports that are Unknown
$log += "=== PCI ROOT PORT RESTART ==="
$ports = Get-PnpDevice | Where-Object { 
    $_.FriendlyName -match 'PCI Express Root Port' -and $_.Status -ne 'OK' 
}
foreach ($p in $ports) {
    $log += "  Restarting: $($p.FriendlyName) ($($p.InstanceId))"
    try {
        Disable-PnpDevice -InstanceId $p.InstanceId -Confirm:$false -ErrorAction Stop
        Start-Sleep -Seconds 1
        Enable-PnpDevice -InstanceId $p.InstanceId -Confirm:$false -ErrorAction Stop
        $log += "    -> Restarted OK"
    } catch {
        $log += "    -> Error: $_"
    }
}

Start-Sleep -Seconds 3

# 2. Rescan PCI bus
$log += "`n=== PCI BUS RESCAN ==="
try {
    pnputil /scan-devices 2>&1 | ForEach-Object { $log += "  $_" }
} catch {
    $log += "  pnputil error: $_"
}

Start-Sleep -Seconds 2

# 3. Check NVMe controllers after
$log += "`n=== NVMe CONTROLLERS AFTER ==="
Get-PnpDevice | Where-Object { $_.FriendlyName -match 'NVM Express' } | ForEach-Object {
    $log += "  $($_.FriendlyName) [$($_.Status)] $($_.InstanceId)"
}

# 4. Check disk drives after
$log += "`n=== DISK DRIVES AFTER ==="
Get-PnpDevice -Class DiskDrive | ForEach-Object {
    $log += "  $($_.FriendlyName) [$($_.Status)]"
}

# 5. Check disks
$log += "`n=== GET-DISK ==="
$log += (Get-Disk | Format-Table Number,FriendlyName,@{N='SizeGB';E={[math]::Round($_.Size/1GB)}},OperationalStatus -AutoSize | Out-String)

# 6. Check root ports after
$log += "`n=== ROOT PORTS AFTER ==="
Get-PnpDevice | Where-Object { $_.FriendlyName -match 'PCI Express Root Port' } | ForEach-Object {
    $log += "  $($_.FriendlyName) [$($_.Status)]"
}

$log -join "`n" | Out-File -FilePath $out -Encoding utf8
