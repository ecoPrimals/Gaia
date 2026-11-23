"""Open the left eye — force Display 2 alive WITHOUT reboot"""
import subprocess, os

print("=" * 60)
print("OPENING THE LEFT EYE — NO REBOOT")
print("=" * 60)

# Strategy 1: Force-install AMD driver on the VGA_ device at bus 123
print("\n[1] Force AMD driver on VGA_ device...\n")

# First find the exact instance ID
cmd1 = '''
pnputil /enum-devices /problem 28 /instanceid "PCI\VEN_1022&DEV_14DE*"
'''
r1 = subprocess.run(['powershell', '-Command', cmd1], capture_output=True, text=True, timeout=10)
print(r1.stdout[:500])

# Try installing oem76.inf (AMD display driver) on the VGA device
cmd2 = '''
$dev = "PCI\\VEN_1022&DEV_14DE&SUBSYS_88771043&REV_C9\\4&1ebe6a9c&0&0041"
pnputil /add-driver "C:\\Windows\\System32\\DriverStore\\FileRepository\\u0200157.inf_amd64_*\\u0200157.inf" /install 2>&1
'''
r2 = subprocess.run(['powershell', '-Command', cmd2], capture_output=True, text=True, timeout=15)
print(f"Driver install: {r2.stdout}")
if r2.stderr: print(f"Err: {r2.stderr[:200]}")

# Strategy 2: Use the Amyuni virtual display driver to create Display 2
print("\n[2] Amyuni Virtual Display...\n")

# Check if usbmmidd driver is available
cmd3 = '''
pnputil /enum-drivers /class Display | Select-String -Pattern "Amyuni|usbmmidd" -Context 3,0
'''
r3 = subprocess.run(['powershell', '-Command', cmd3], capture_output=True, text=True, timeout=10)
print(r3.stdout if r3.stdout.strip() else "  Amyuni driver not found in enum")

# Check for the inf file
cmd4 = '''
Get-ChildItem "C:\\Windows\\System32\\DriverStore\\FileRepository" -Filter "usbmmidd*" -Recurse -ErrorAction SilentlyContinue | Select-Object FullName
'''
r4 = subprocess.run(['powershell', '-Command', cmd4], capture_output=True, text=True, timeout=10)
print(f"  Amyuni files: {r4.stdout}")

# Strategy 3: Try devcon-like approach to enable the iGPU
print("\n[3] Enable VGA_ device via pnputil...\n")
instance_id = "PCI\\VEN_1022&DEV_14DE&SUBSYS_88771043&REV_C9\\4&1ebe6a9c&0&0041"
r5 = subprocess.run(['pnputil', '/enable-device', instance_id], capture_output=True, text=True, timeout=10)
print(f"  Enable: {r5.stdout}")

# Strategy 4: Restart the device
print("\n[4] Restart VGA_ device...\n")
r6 = subprocess.run(['pnputil', '/restart-device', instance_id], capture_output=True, text=True, timeout=10)
print(f"  Restart: {r6.stdout}")

# Strategy 5: Check if any new display appeared
print("\n[5] Check displays...\n")
import time
time.sleep(3)

cmd7 = '''
Add-Type -AssemblyName System.Windows.Forms
$s = [System.Windows.Forms.Screen]::AllScreens
Write-Output "Displays: $($s.Count)"
foreach ($sc in $s) { Write-Output "  $($sc.DeviceName) $($sc.Bounds.Width)x$($sc.Bounds.Height)" }

Get-PnpDevice -Class Display | ForEach-Object {
    Write-Output "$($_.FriendlyName): $($_.Status)"
}
'''
r7 = subprocess.run(['powershell', '-Command', cmd7], capture_output=True, text=True, timeout=10)
print(r7.stdout)

# Strategy 6: Use NVIDIA to detect a second output
print("\n[6] NVIDIA display outputs...\n")
r8 = subprocess.run(['nvidia-smi', '--query-gpu=name,display_mode,display_active', '--format=csv,noheader'], capture_output=True, text=True, timeout=5)
print(f"  {r8.stdout.strip()}")

# Check if 5090 has HDMI connected
cmd9 = '''
Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorConnectionParams -ErrorAction SilentlyContinue | ForEach-Object {
    $type = switch ($_.VideoOutputTechnology) {
        0 {"VGA"} 5 {"DVI"} 9 {"HDMI"} 10 {"DP"} 11 {"DP-embedded"} default {"Type$($_.VideoOutputTechnology)"}
    }
    Write-Output "Monitor: $($_.InstanceName) Type=$type"
}
'''
r9 = subprocess.run(['powershell', '-Command', cmd9], capture_output=True, text=True, timeout=10)
print(r9.stdout)

print("\nDone!")
