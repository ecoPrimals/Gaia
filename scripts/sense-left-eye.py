"""Sense the left eye — is Display 2 alive with the LG plugged into mobo HDMI?"""
import subprocess

print("=" * 60)
print("SENSING LEFT EYE — LG on mobo HDMI")
print("=" * 60)

# Display count
print("\n[1] How many displays?...\n")
r1 = subprocess.run(['powershell', '-Command',
    'Add-Type -AssemblyName System.Windows.Forms; $s = [System.Windows.Forms.Screen]::AllScreens; Write-Output "DISPLAYS: $($s.Count)"; foreach ($scr in $s) { Write-Output "  $($scr.DeviceName) $($scr.Bounds.Width)x$($scr.Bounds.Height) Primary=$($scr.Primary)" }'],
    capture_output=True, text=True, timeout=10)
print(r1.stdout.strip())

# All monitors via WMI
print("\n[2] WMI Monitors...\n")
r2 = subprocess.run(['powershell', '-Command',
    'Get-CimInstance -ClassName WmiMonitorID -Namespace root/wmi -ErrorAction SilentlyContinue | ForEach-Object { $name = ($_.UserFriendlyName | Where-Object {$_ -ne 0} | ForEach-Object {[char]$_}) -join ""; Write-Output "Monitor: $name Serial=$([System.Text.Encoding]::ASCII.GetString($_.SerialNumberID).Trim([char]0)) Active=$($_.Active)" }'],
    capture_output=True, text=True, timeout=10)
print(r2.stdout.strip() if r2.stdout.strip() else "  No WMI monitors")

# Display adapters + connected monitors
print("\n[3] Display adapters + monitors...\n")
r3 = subprocess.run(['powershell', '-Command',
    'Get-PnpDevice -Class Monitor -ErrorAction SilentlyContinue | Format-Table FriendlyName,Status,InstanceId -AutoSize'],
    capture_output=True, text=True, timeout=10)
print(r3.stdout.strip())

# Video controllers
print("\n[4] Video controllers...\n")
r4 = subprocess.run(['powershell', '-Command',
    'Get-CimInstance -ClassName Win32_VideoController | Format-Table Name,Status,CurrentHorizontalResolution,CurrentVerticalResolution,AdapterCompatibility -AutoSize'],
    capture_output=True, text=True, timeout=10)
print(r4.stdout.strip())

# NVIDIA display outputs
print("\n[5] NVIDIA connected displays...\n")
r5 = subprocess.run(['nvidia-smi', '--query-gpu=name,display_active,display_mode', '--format=csv'], capture_output=True, text=True, timeout=5)
print(r5.stdout.strip())

# Try to detect new display devices
print("\n[6] Rescanning hardware...\n")
r6 = subprocess.run(['powershell', '-Command', 'pnputil /scan-devices'], capture_output=True, text=True, timeout=15)
print(r6.stdout.strip())

# Check again after rescan
import time
time.sleep(2)
print("\n[7] Displays AFTER rescan...\n")
r7 = subprocess.run(['powershell', '-Command',
    'Add-Type -AssemblyName System.Windows.Forms; Write-Output "DISPLAYS: $([System.Windows.Forms.Screen]::AllScreens.Count)"; Get-PnpDevice -Class Monitor -ErrorAction SilentlyContinue | Format-Table FriendlyName,Status -AutoSize'],
    capture_output=True, text=True, timeout=10)
print(r7.stdout.strip())

# Check if iGPU display device appeared
print("\n[8] AMD display devices...\n")
r8 = subprocess.run(['powershell', '-Command',
    'Get-PnpDevice -Class Display -ErrorAction SilentlyContinue | Format-Table FriendlyName,Status,InstanceId -AutoSize; Write-Output ""; Get-PnpDevice | Where-Object { $_.InstanceId -like "*1002*13C0*" -or $_.InstanceId -like "*1002*164E*" -or ($_.InstanceId -like "*1002*" -and $_.Class -eq "Display") } | Format-Table FriendlyName,Status,InstanceId -AutoSize'],
    capture_output=True, text=True, timeout=10)
print(r8.stdout.strip())

print("\n" + "=" * 60)
