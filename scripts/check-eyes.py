"""Check both eyes — display enumeration"""
import subprocess

print("=== BOTH EYES CHECK ===\n")

cmd1 = '''
Add-Type -AssemblyName System.Windows.Forms
$screens = [System.Windows.Forms.Screen]::AllScreens
Write-Output "Total displays: $($screens.Count)"
foreach ($s in $screens) {
    Write-Output "  $($s.DeviceName) | Primary=$($s.Primary) | $($s.Bounds.Width)x$($s.Bounds.Height) at ($($s.Bounds.X),$($s.Bounds.Y))"
}
'''
r1 = subprocess.run(['powershell', '-Command', cmd1], capture_output=True, text=True, timeout=10)
print(r1.stdout)

cmd2 = '''
Get-CimInstance Win32_VideoController | ForEach-Object {
    $name = $_.Name
    $res = "$($_.CurrentHorizontalResolution)x$($_.CurrentVerticalResolution)"
    $hz = $_.CurrentRefreshRate
    $status = $_.Status
    Write-Output "$name : $res @ ${hz}Hz | Status=$status"
}
'''
r2 = subprocess.run(['powershell', '-Command', cmd2], capture_output=True, text=True, timeout=10)
print(r2.stdout)

cmd3 = '''
Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBasicDisplayParams -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Output "Monitor: $($_.InstanceName) | Active=$($_.Active)"
}
'''
r3 = subprocess.run(['powershell', '-Command', cmd3], capture_output=True, text=True, timeout=10)
print(r3.stdout)

print("iGPU adapter status:")
cmd4 = 'Get-PnpDevice -Class Display | Format-Table FriendlyName, Status -AutoSize'
r4 = subprocess.run(['powershell', '-Command', cmd4], capture_output=True, text=True, timeout=10)
print(r4.stdout)
