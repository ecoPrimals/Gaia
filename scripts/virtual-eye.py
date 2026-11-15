"""Create a virtual Display 2 using IddSampleDriver or devcon"""
import subprocess, os, ctypes

print("=== VIRTUAL LEFT EYE ===\n")

# Method 1: Check if we can use devcon to create a virtual display
print("[1] Checking devcon / device creation tools...\n")
devcon_paths = [
    r"C:\Windows\System32\devcon.exe",
    r"C:\Program Files (x86)\Windows Kits\10\Tools\x64\devcon.exe",
]
for p in devcon_paths:
    if os.path.exists(p):
        print(f"  Found devcon: {p}")
        break
else:
    print("  No devcon found")

# Method 2: Use PowerShell to enumerate virtual display possibilities
print("\n[2] Looking for IDD (Indirect Display Driver) options...\n")
cmd2 = '''
# Check if there are any IDD drivers
Get-PnpDevice -Class Display -Status OK | ForEach-Object {
    $hw = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName DEVPKEY_Device_HardwareIds -ErrorAction SilentlyContinue).Data
    Write-Output "$($_.FriendlyName) | $($_.Status) | $($hw -join '; ')"
}
Write-Output ""
# Check for virtual/software adapters
Get-PnpDevice | Where-Object { $_.FriendlyName -like "*virtual*" -or $_.FriendlyName -like "*indirect*" -or $_.FriendlyName -like "*IDD*" -or $_.FriendlyName -like "*Amyuni*" } | ForEach-Object {
    Write-Output "Virtual: $($_.FriendlyName) | $($_.Status) | $($_.Class)"
}
'''
r2 = subprocess.run(['powershell', '-Command', cmd2], capture_output=True, text=True, timeout=15)
print(r2.stdout)

# Method 3: Use Win32 API to try creating a virtual display
print("[3] Attempting to add virtual display via ChangeDisplaySettingsEx...\n")
# On Windows 10+, you can use the IddCx framework but it needs a proper driver
# Let's check what display paths the system has
cmd3 = '''
Get-CimInstance -ClassName Win32_DesktopMonitor | ForEach-Object {
    Write-Output "Monitor: $($_.Name) Screen=$($_.ScreenWidth)x$($_.ScreenHeight) Status=$($_.Status)"
}
Write-Output ""
Get-CimInstance -ClassName Win32_VideoController | ForEach-Object {
    Write-Output "Adapter: $($_.Name) RAM=$([math]::Round($_.AdapterRAM/1MB))MB Res=$($_.CurrentHorizontalResolution)x$($_.CurrentVerticalResolution)"
}
'''
r3 = subprocess.run(['powershell', '-Command', cmd3], capture_output=True, text=True, timeout=10)
print(r3.stdout)

# Method 4: Try NVIDIA Mosaic / Surround for multi-display
print("[4] NVIDIA display connector info...\n")
r4 = subprocess.run(['nvidia-smi', '-q', '-d', 'ECC'], capture_output=True, text=True, timeout=10)
# Get connected displays  
r5 = subprocess.run(['nvidia-smi', '--query-gpu=name,display_mode,display_active', '--format=csv'], capture_output=True, text=True, timeout=5)
print(r5.stdout)

# Method 5: The REAL creative solve — use the ASUS WMI PCI write to force UMA
print("[5] Attempting ASUS WMI PCI config write to force iGPU...\n")
# Read what's at bus 0 dev 8 func 1 reg 0x18 (secondary bus number for iGPU bridge)
cmd5 = '''
$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement

# Read the bridge at bus 0 dev 8 func 1 — this is the root port for iGPU
# Reg 0x00: VEN/DEV ID
$r = Invoke-CimMethod -InputObject $inst -MethodName "asio_hw_fun11" -Arguments @{ Bus = [byte]0; Dev = [byte]8; Func = [byte]1; Reg = [uint16]0; Width = [byte]4 }
$ven = $r.dwData -band 0xFFFF
$devid = ($r.dwData -shr 16) -band 0xFFFF
Write-Output "Root port Bus0 Dev8 Func1: VEN=$($ven.ToString('X4')) DEV=$($devid.ToString('X4'))"

# Reg 0x18: Bus numbers (primary/secondary/subordinate)
$r2 = Invoke-CimMethod -InputObject $inst -MethodName "asio_hw_fun11" -Arguments @{ Bus = [byte]0; Dev = [byte]8; Func = [byte]1; Reg = [uint16]24; Width = [byte]4 }
$primary = $r2.dwData -band 0xFF
$secondary = ($r2.dwData -shr 8) -band 0xFF
$subordinate = ($r2.dwData -shr 16) -band 0xFF
Write-Output "  Primary=$primary Secondary=$secondary Subordinate=$subordinate"

# Now try to read the actual iGPU at that secondary bus
if ($secondary -gt 0) {
    $r3 = Invoke-CimMethod -InputObject $inst -MethodName "asio_hw_fun11" -Arguments @{ Bus = [byte]$secondary; Dev = [byte]0; Func = [byte]0; Reg = [uint16]0; Width = [byte]4 }
    $ven2 = $r3.dwData -band 0xFFFF
    $devid2 = ($r3.dwData -shr 16) -band 0xFFFF
    Write-Output "  Behind bridge: VEN=$($ven2.ToString('X4')) DEV=$($devid2.ToString('X4'))"
}

# Also check bus 0 dev 8 func 0
$r4 = Invoke-CimMethod -InputObject $inst -MethodName "asio_hw_fun11" -Arguments @{ Bus = [byte]0; Dev = [byte]8; Func = [byte]0; Reg = [uint16]0; Width = [byte]4 }
Write-Output "Bus0 Dev8 Func0: 0x$($r4.dwData.ToString('X8'))"
'''
r6 = subprocess.run(['powershell', '-Command', cmd5], capture_output=True, text=True, timeout=15)
print(r6.stdout)

print("\nDone!")
