Write-Host "=== blueGate DISPLAY HUNT ==="
Write-Host ""

Write-Host "--- ALL GPU ADAPTERS ---"
Get-CimInstance Win32_VideoController | Select-Object Name, Status, Availability, DeviceID, AdapterRAM | Format-Table -AutoSize

Write-Host "--- ALL MONITORS ---"
Get-CimInstance Win32_PnPEntity | Where-Object { $_.PNPClass -eq 'Monitor' -or $_.Name -match 'monitor|display' } | Select-Object Name, Status, DeviceID | Format-Table -AutoSize

Write-Host "--- USB DISPLAY DEVICES ---"
Get-CimInstance Win32_PnPEntity | Where-Object { $_.DeviceID -match 'USB' -and ($_.Name -match 'display|monitor|video|screen') } | Select-Object Name, Status, DeviceID | Format-Table -AutoSize

Write-Host "--- ACTIVE SCREENS ---"
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Screen]::AllScreens | ForEach-Object { 
    Write-Host "  $($_.DeviceName) | $($_.Bounds) | Primary=$($_.Primary)"
}

Write-Host ""
Write-Host "--- WMI MONITOR INSTANCES ---"
Get-CimInstance -Namespace root/wmi -Class WmiMonitorBasicDisplayParams -ErrorAction SilentlyContinue | Select-Object Active, InstanceName, MaxHorizontalImageSize, MaxVerticalImageSize | Format-Table -AutoSize

Write-Host ""
Write-Host "--- ALL PNP MONITORS ---"
Get-CimInstance Win32_PnPEntity | Where-Object { $_.PNPClass -eq 'Monitor' } | Select-Object Name, Status, DeviceID, PNPClass | Format-Table -AutoSize

Write-Host ""
Write-Host "--- DISPLAY DRIVER DEVICES ---"
Get-CimInstance Win32_PnPEntity | Where-Object { $_.PNPClass -eq 'Display' } | Select-Object Name, Status, DeviceID | Format-Table -AutoSize
