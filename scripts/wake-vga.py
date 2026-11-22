"""Wake VGA_ device at bus 123 and try ASUS WMI for UMA"""
import subprocess

print("=== WAKING VGA + ASUS WMI BIOS CONTROL ===\n")

# 1. Find the exact instance ID of the VGA device
print("[1] Finding VGA_ device...\n")
cmd1 = '''
pnputil /enum-devices /problem 28 /deviceids /drivers /location
'''
r1 = subprocess.run(['powershell', '-Command', cmd1], capture_output=True, text=True, timeout=15)
print(r1.stdout[:3000])

# 2. Try ASUS WMI GetOptionData for UMA/iGPU settings
print("\n[2] Reading BIOS options via ASUS WMI...\n")
options = [
    "Integrated Graphics",
    "UMA Frame Buffer Size",
    "Primary Video Device",
    "iGPU Configuration",
    "IGD Multi-Monitor",
    "Above 4G Decoding",
    "Re-Size BAR Support",
    "PCIEX16 Link Mode",
]
for opt in options:
    cmd = f'''
    $inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement
    try {{
        $result = Invoke-CimMethod -InputObject $inst -MethodName "GetOptionData" -Arguments @{{ OptionName = "{opt}" }}
        Write-Output "{opt}: Value=$($result.Value) Error=$($result.ErrorCode)"
    }} catch {{
        Write-Output "{opt}: FAILED - $($_.Exception.Message)"
    }}
    '''
    r = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, timeout=10)
    print(f"  {r.stdout.strip()}")

# 3. Try to set UMA Frame Buffer Size = 512M via WMI
print("\n[3] Attempting to SET UMA Frame Buffer Size...\n")
# 512M might be value 7 (index in the list: Auto=0, 64M=1, 80M=2, 96M=3, 128M=4, 256M=5, 384M=6, 512M=7)
for val in [7, 512, 0x200]:
    cmd3 = f'''
    $inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement
    try {{
        $result = Invoke-CimMethod -InputObject $inst -MethodName "SetOptionData" -Arguments @{{ OptionName = "UMA Frame Buffer Size"; Value = {val} }}
        Write-Output "Set UMA={val}: Error=$($result.ErrorCode)"
    }} catch {{
        Write-Output "Set UMA={val}: $($_.Exception.Message)"
    }}
    '''
    r3 = subprocess.run(['powershell', '-Command', cmd3], capture_output=True, text=True, timeout=10)
    print(f"  {r3.stdout.strip()}")

# 4. Try to install the AMD driver on the VGA device
print("\n[4] Installing AMD driver on VGA device...\n")
cmd4 = '''
# Find the VGA device at bus 123
$vga = pnputil /enum-devices /problem 28 /instanceid "PCI\VEN_*14DE*"
Write-Output $vga

# Try to update driver for all problem 28 PCI devices
pnputil /scan-devices
'''
r4 = subprocess.run(['powershell', '-Command', cmd4], capture_output=True, text=True, timeout=15)
print(r4.stdout)

print("\nDone!")
