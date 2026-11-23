"""Find the left eye — iGPU hunt after dummy plug"""
import subprocess

print("=== HUNTING THE LEFT EYE ===\n")

# 1. Force a hardware rescan
print("[1] Forcing hardware rescan...\n")
r = subprocess.run(['pnputil', '/scan-devices'], capture_output=True, text=True, timeout=15)
print(r.stdout)

import time
time.sleep(3)

# 2. Check ALL AMD devices (VEN_1002)
print("[2] All AMD (VEN_1002) devices...\n")
cmd = '''
Get-PnpDevice | ForEach-Object {
    if ($_.InstanceId -like "*1002*") {
        Write-Output "$($_.Status.ToString().PadRight(10)) $($_.FriendlyName.PadRight(40)) $($_.InstanceId)"
    }
}
'''
r2 = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, timeout=15)
print(r2.stdout if r2.stdout.strip() else "  No AMD 1002 devices found at all!")

# 3. Check display class
print("[3] Display adapters...\n")
cmd3 = 'Get-PnpDevice -Class Display | Format-Table FriendlyName, Status -AutoSize'
r3 = subprocess.run(['powershell', '-Command', cmd3], capture_output=True, text=True, timeout=10)
print(r3.stdout)

# 4. Check monitors  
print("[4] Monitors...\n")
cmd4 = '''
Add-Type -AssemblyName System.Windows.Forms
$s = [System.Windows.Forms.Screen]::AllScreens
Write-Output "Displays: $($s.Count)"
foreach ($sc in $s) {
    Write-Output "  $($sc.DeviceName) | Primary=$($sc.Primary) | $($sc.Bounds.Width)x$($sc.Bounds.Height)"
}
'''
r4 = subprocess.run(['powershell', '-Command', cmd4], capture_output=True, text=True, timeout=10)
print(r4.stdout)

# 5. Check WMI monitors
print("[5] WMI Monitor detection...\n")
cmd5 = '''
Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBasicDisplayParams -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Output "Monitor: $($_.InstanceName) Active=$($_.Active)"
}
Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorID -ErrorAction SilentlyContinue | ForEach-Object {
    $name = ($_.UserFriendlyName | Where-Object {$_ -ne 0} | ForEach-Object {[char]$_}) -join ''
    Write-Output "  Name: $name Serial: $(($_.SerialNumberID | Where-Object {$_ -ne 0} | ForEach-Object {[char]$_}) -join '')"
}
'''
r5 = subprocess.run(['powershell', '-Command', cmd5], capture_output=True, text=True, timeout=10)
print(r5.stdout)

# 6. Check if iGPU is on bus 123 via WMI raw
print("[6] Raw PCI bus 123 scan...\n")
cmd6 = '''
Get-WmiObject Win32_PnPEntity | ForEach-Object {
    if ($_.DeviceID -like "PCI*") {
        $loc = $_.GetDeviceProperties("DEVPKEY_Device_LocationInfo").DeviceProperties[0].Data
        if ($loc -like "*bus 123*") {
            Write-Output "Bus 123: $($_.Name) | Status=$($_.Status) | Error=$($_.ConfigManagerErrorCode)"
            Write-Output "  ID: $($_.DeviceID)"
        }
    }
}
'''
r6 = subprocess.run(['powershell', '-Command', cmd6], capture_output=True, text=True, timeout=30)
print(r6.stdout if r6.stdout.strip() else "  Nothing on bus 123!")

# 7. Try adding a device manually
print("\n[7] Try re-adding iGPU by hardware ID...\n")
r7 = subprocess.run(['pnputil', '/add-device', 'PCI\\VEN_1002&DEV_13C0'], capture_output=True, text=True, timeout=10)
print(r7.stdout if r7.stdout.strip() else "  (no output)")
if r7.stderr: print(f"  {r7.stderr[:200]}")

print("\nDone — is the left eye waking?")
