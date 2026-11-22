Add-Type -AssemblyName System.Windows.Forms
$screens = [System.Windows.Forms.Screen]::AllScreens
foreach ($s in $screens) {
    Write-Output ("SCREEN: " + $s.DeviceName + " " + $s.Bounds.Width + "x" + $s.Bounds.Height + " Primary=" + $s.Primary)
}
Write-Output ""
Write-Output "=== Display Adapters ==="
Get-PnpDevice -Class Display | Format-Table FriendlyName,Status -AutoSize
Write-Output "=== Monitors ==="
Get-PnpDevice -Class Monitor | Format-Table FriendlyName,Status -AutoSize
Write-Output "=== USB Mobile Monitor / IDD ==="
Get-PnpDevice | Where-Object { $_.FriendlyName -like "*USB Mobile*" -or $_.FriendlyName -like "*IDD*" -or $_.FriendlyName -like "*Virtual*" -or $_.FriendlyName -like "*usbmmidd*" } | Format-Table FriendlyName,Status,InstanceId -AutoSize
