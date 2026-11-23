Write-Host "=== ENABLING RTX 5090 ==="
$nv = Get-PnpDevice | Where-Object { $_.FriendlyName -match '5090' -and $_.Class -eq 'Display' }
Write-Host "Current: $($nv.FriendlyName) | $($nv.Status) | $($nv.Problem)"
Write-Host "InstanceId: $($nv.InstanceId)"

Write-Host ""
Write-Host "Enabling..."
Enable-PnpDevice -InstanceId $nv.InstanceId -Confirm:$false -ErrorAction SilentlyContinue
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "--- POST-ENABLE STATUS ---"
Get-PnpDevice | Where-Object { $_.Class -eq 'Display' } | Select-Object FriendlyName, Status, Problem | Format-Table -AutoSize

Write-Host "--- SCREENS ---"
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Screen]::AllScreens | ForEach-Object { 
    Write-Host "  $($_.DeviceName) | $($_.Bounds) | Primary=$($_.Primary)"
}

Write-Host ""
Write-Host "--- MONITORS ---"
Get-PnpDevice | Where-Object { $_.Class -eq 'Monitor' -and $_.Status -eq 'OK' } | Select-Object FriendlyName, Status, InstanceId | Format-Table -AutoSize
