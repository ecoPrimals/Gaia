# Kill ASUS framework and check if NVMe drives wake up
Write-Host "=== PRE-KILL: NVMe state ==="
Get-PnpDevice | Where-Object { $_.InstanceId -match 'NVME|VEN_15B7|VEN_144D' -and $_.Class -eq 'SCSIAdapter' } | Format-Table FriendlyName, Status -AutoSize

Write-Host "`n=== Killing ASUS framework (7 processes) ==="
Get-Process asus_framework -ErrorAction SilentlyContinue | ForEach-Object { 
    Write-Host ("  Killing PID " + $_.Id)
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}

Write-Host "`n=== Killing zombie SystemSettings ==="
Get-Process SystemSettings -ErrorAction SilentlyContinue | Where-Object { $_.Responding -eq $false } | ForEach-Object {
    Write-Host ("  Killing zombie PID " + $_.Id)
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}

Start-Sleep -Seconds 3

Write-Host "`n=== POST-KILL: NVMe state ==="
Get-PnpDevice | Where-Object { $_.InstanceId -match 'NVME|VEN_15B7|VEN_144D' -and $_.Class -eq 'SCSIAdapter' } | Format-Table FriendlyName, Status -AutoSize

Write-Host "`n=== Scanning for hardware changes ==="
$scan = New-Object -ComObject Shell.Application
# pnputil scan
pnputil /scan-devices 2>&1

Start-Sleep -Seconds 5

Write-Host "`n=== FINAL CHECK: NVMe + Disks ==="
Get-PnpDevice | Where-Object { $_.InstanceId -match 'NVME|VEN_15B7|VEN_144D' } | Format-Table FriendlyName, Status, Class -AutoSize
Get-PhysicalDisk | Format-Table FriendlyName, Size, HealthStatus, OperationalStatus -AutoSize

Write-Host "`n=== Root Port 0C ==="
Get-PnpDevice | Where-Object { $_.InstanceId -match '0&0C$' -and $_.Class -eq 'System' } | Format-Table FriendlyName, Status -AutoSize
