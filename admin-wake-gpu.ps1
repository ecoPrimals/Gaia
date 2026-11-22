# Must run as admin to enable PnP devices
Write-Host "=== ADMIN GPU WAKE ==="

# Enable RTX 5090
Write-Host "Enabling RTX 5090..."
$nv = Get-PnpDevice | Where-Object { $_.FriendlyName -match '5090' -and $_.Class -eq 'Display' }
if ($nv) {
    Enable-PnpDevice -InstanceId $nv.InstanceId -Confirm:$false
    Write-Host "  RTX 5090 enable sent."
}

Start-Sleep -Seconds 3

# Enable AMD iGPU
Write-Host "Enabling AMD Radeon iGPU..."
$amd = Get-PnpDevice | Where-Object { $_.FriendlyName -match 'AMD Radeon' -and $_.Class -eq 'Display' }
if ($amd) {
    Enable-PnpDevice -InstanceId $amd.InstanceId -Confirm:$false
    Write-Host "  AMD iGPU enable sent."
}

Start-Sleep -Seconds 5

# Check results
Write-Host ""
Write-Host "--- RESULTS ---"
Get-PnpDevice | Where-Object { $_.Class -eq 'Display' } | Select-Object FriendlyName, Status, Problem | Format-Table -AutoSize

Add-Type -AssemblyName System.Windows.Forms
Write-Host "--- SCREENS ---"
[System.Windows.Forms.Screen]::AllScreens | ForEach-Object { 
    Write-Host "  $($_.DeviceName) | $($_.Bounds) | Primary=$($_.Primary)"
}
