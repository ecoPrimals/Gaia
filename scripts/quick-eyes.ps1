Add-Type -AssemblyName System.Windows.Forms
$screens = [System.Windows.Forms.Screen]::AllScreens
Write-Output "DISPLAYS: $($screens.Count)"
foreach ($s in $screens) {
    Write-Output "  $($s.DeviceName) $($s.Bounds.Width)x$($s.Bounds.Height) Primary=$($s.Primary)"
}
Write-Output ""
Get-PnpDevice -Class Monitor -ErrorAction SilentlyContinue | Format-Table FriendlyName,Status -AutoSize
Write-Output ""
Get-CimInstance -Namespace root/wmi -ClassName WmiMonitorID -ErrorAction SilentlyContinue | ForEach-Object {
    $name = ($_.UserFriendlyName | Where-Object {$_ -ne 0} | ForEach-Object {[char]$_}) -join ""
    Write-Output "WMI Monitor: $name Active=$($_.Active)"
}
