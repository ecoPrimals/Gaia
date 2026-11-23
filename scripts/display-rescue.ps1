# DISPLAY RESCUE — What's happening with our eyes?
Write-Host "=" * 60
Write-Host "  DISPLAY RESCUE + USB-C SPINE MAP"
Write-Host "=" * 60

Write-Host "`n--- ACTIVE DISPLAYS ---"
Add-Type -AssemblyName System.Windows.Forms
$screens = [System.Windows.Forms.Screen]::AllScreens
foreach ($s in $screens) {
    Write-Host "  $($s.DeviceName) $($s.Bounds.Width)x$($s.Bounds.Height) Primary=$($s.Primary)"
}
Write-Host "  Total screens: $($screens.Count)"

Write-Host "`n--- GPU OUTPUTS ---"
Get-PnpDevice -Class Display -Status OK | Select-Object FriendlyName, Status, InstanceId | Format-Table -AutoSize

Write-Host "`n--- MONITORS (all states) ---"
Get-PnpDevice -Class Monitor | Select-Object FriendlyName, Status | Format-Table -AutoSize

Write-Host "`n--- CCD / Display Topology ---"
Get-CimInstance -Namespace root/wmi -ClassName WmiMonitorBasicDisplayParams -ErrorAction SilentlyContinue | Select-Object InstanceName, Active, @{N="HorizCM";E={$_.MaxHorizontalImageSize}}, @{N="VertCM";E={$_.MaxVerticalImageSize}} | Format-Table -AutoSize

Write-Host "`n--- USB-C SPINE MAP ---"
Write-Host "  All USB-C / USB4 / Thunderbolt devices:"
Get-PnpDevice -Status OK | Where-Object { 
    $_.FriendlyName -match 'USB4|USB-C|TypeC|Billboard|Alt.Mode|DisplayPort.*Alt|Thunderbolt|ITE' 
} | Select-Object FriendlyName, Class, InstanceId | Format-Table -AutoSize

Write-Host "`n--- ALL USB devices on 40G/20G ports ---"
Get-PnpDevice -Class USB -Status OK | Where-Object {
    $_.InstanceId -match 'ROOT_HUB30|VID_174C|VID_1B21|VID_3434|VID_28DE|VID_361C'
} | Select-Object FriendlyName, InstanceId | Format-Table -AutoSize

Write-Host "`n--- USB-C DP Alt Mode (iGPU display path) ---"
Get-PnpDevice | Where-Object { $_.FriendlyName -match 'DisplayPort|DP Alt|USB.*Display' } | Select-Object FriendlyName, Status, Class | Format-Table -AutoSize

Write-Host "`n--- Display adapter outputs ---"
Get-CimInstance Win32_VideoController | Select-Object Name, Status, CurrentHorizontalResolution, CurrentVerticalResolution, VideoProcessor, AdapterRAM | Format-List

Write-Host "`n--- displayswitch state ---"
Write-Host "  (forcing extend mode...)"
Start-Process displayswitch.exe -ArgumentList '/extend' -Wait -ErrorAction SilentlyContinue
Start-Sleep 2

$screens2 = [System.Windows.Forms.Screen]::AllScreens
Write-Host "  Screens after extend: $($screens2.Count)"
foreach ($s in $screens2) {
    Write-Host "  $($s.DeviceName) $($s.Bounds.Width)x$($s.Bounds.Height) Primary=$($s.Primary)"
}
