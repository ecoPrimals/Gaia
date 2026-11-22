Write-Host "=== WAKING THE 3RD EYE — MBO HDMI / AMD iGPU ==="
Write-Host ""

# Check AMD iGPU status
Write-Host "--- AMD iGPU DEVICE STATUS ---"
$amd = Get-CimInstance Win32_PnPEntity | Where-Object { $_.Name -match 'AMD Radeon' -and $_.PNPClass -eq 'Display' }
$amd | Select-Object Name, Status, DeviceID, ConfigManagerErrorCode | Format-List

# Try to enable it
Write-Host "--- ATTEMPTING TO ENABLE AMD iGPU ---"
$amdDev = Get-PnpDevice | Where-Object { $_.FriendlyName -match 'AMD Radeon' -and $_.Class -eq 'Display' }
$amdDev | Select-Object FriendlyName, Status, InstanceId, Problem | Format-List

if ($amdDev.Status -eq 'Error' -or $amdDev.Status -ne 'OK') {
    Write-Host "AMD iGPU is in error state. Trying disable/enable cycle..."
    try {
        $amdDev | Disable-PnpDevice -Confirm:$false -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        $amdDev | Enable-PnpDevice -Confirm:$false -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 3
        Write-Host "Disable/enable cycle complete."
    } catch {
        Write-Host "Error during enable: $_"
    }
}

# Also try the 5090
Write-Host ""
Write-Host "--- RTX 5090 STATUS ---"
$nv = Get-PnpDevice | Where-Object { $_.FriendlyName -match '5090' -and $_.Class -eq 'Display' }
$nv | Select-Object FriendlyName, Status, InstanceId, Problem | Format-List

if ($nv.Status -eq 'Error' -or $nv.Status -ne 'OK') {
    Write-Host "RTX 5090 is in error state. Trying disable/enable cycle..."
    try {
        $nv | Disable-PnpDevice -Confirm:$false -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        $nv | Enable-PnpDevice -Confirm:$false -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 3
        Write-Host "Disable/enable cycle complete."
    } catch {
        Write-Host "Error during enable: $_"
    }
}

Start-Sleep -Seconds 2

# Re-check all
Write-Host ""
Write-Host "--- POST-WAKE STATUS ---"
Get-PnpDevice | Where-Object { $_.Class -eq 'Display' } | Select-Object FriendlyName, Status, Problem | Format-Table -AutoSize

Write-Host ""
Write-Host "--- SCREENS AFTER WAKE ---"
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Screen]::AllScreens | ForEach-Object { 
    Write-Host "  $($_.DeviceName) | $($_.Bounds) | Primary=$($_.Primary)"
}

Write-Host ""
Write-Host "--- GPU ADAPTERS AFTER WAKE ---"
Get-CimInstance Win32_VideoController | Select-Object Name, Status, CurrentHorizontalResolution, CurrentVerticalResolution | Format-Table -AutoSize
