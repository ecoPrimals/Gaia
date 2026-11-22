Write-Host "=== POST-REBOOT DISPLAY SCAN ==="
Write-Host ""

Write-Host "--- GPU ADAPTERS ---"
Get-CimInstance Win32_VideoController | Select-Object Name, Status, Availability, CurrentHorizontalResolution, CurrentVerticalResolution | Format-Table -AutoSize

Write-Host "--- PNP DISPLAY DEVICES ---"
Get-PnpDevice | Where-Object { $_.Class -eq 'Display' } | Select-Object FriendlyName, Status, Problem, InstanceId | Format-Table -AutoSize

Write-Host "--- ALL MONITORS ---"
Get-PnpDevice | Where-Object { $_.Class -eq 'Monitor' } | Select-Object FriendlyName, Status, Problem, InstanceId | Format-Table -AutoSize

Write-Host "--- ACTIVE SCREENS ---"
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Screen]::AllScreens | ForEach-Object { 
    Write-Host "  $($_.DeviceName) | $($_.Bounds) | Primary=$($_.Primary)"
}

Write-Host ""
Write-Host "--- WMI MONITOR INSTANCES ---"
Get-CimInstance -Namespace root/wmi -Class WmiMonitorBasicDisplayParams -ErrorAction SilentlyContinue | Select-Object Active, InstanceName, MaxHorizontalImageSize, MaxVerticalImageSize | Format-Table -AutoSize

Write-Host ""
Write-Host "--- NVIDIA DISPLAY OUTPUTS ---"
$nv = Get-PnpDevice | Where-Object { $_.FriendlyName -match '5090' -and $_.Class -eq 'Display' }
Write-Host "  5090 status: $($nv.Status) / $($nv.Problem)"

$amd = Get-PnpDevice | Where-Object { $_.FriendlyName -match 'AMD Radeon' -and $_.Class -eq 'Display' }
Write-Host "  AMD iGPU status: $($amd.Status) / $($amd.Problem)"

$usb = Get-PnpDevice | Where-Object { $_.FriendlyName -match 'USB Mobile' -and $_.Class -eq 'Display' }
Write-Host "  USB Mobile status: $($usb.Status) / $($usb.Problem)"
