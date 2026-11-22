"""PCI X-ray — use ASUS WMI to scan raw PCI config space for AKD1000"""
import subprocess

print("=== PCI X-RAY — Scanning for BrainChip 1E7C ===\n")

# Scan all PCI buses for vendor ID 1E7C (BrainChip)
# PCI config register 0x00 = Vendor ID (16-bit) + Device ID (16-bit)
# BrainChip: VEN=0x1E7C, DEV=0xBCA1

# The PCIEX16(G4) slot goes through the X870E chipset
# Chipset downstream switch ports are on buses 6, 9, 20
# Devices behind them would be bus 7, 10-14, 21+

# Scan a wide range of buses
print("Scanning ALL buses 0-30 for vendor 1E7C...\n")

found = False
for bus in range(31):
    for dev in range(2):  # Usually dev 0 for endpoints
        cmd = f'''
        $inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement
        $result = Invoke-CimMethod -InputObject $inst -MethodName "asio_hw_fun11" -Arguments @{{ Bus = [byte]{bus}; Dev = [byte]{dev}; Func = [byte]0; Reg = [uint16]0; Width = [byte]4 }}
        $data = $result.dwData
        if ($data -ne 0 -and $data -ne 4294967295) {{
            $ven = $data -band 0xFFFF
            $devid = ($data -shr 16) -band 0xFFFF
            Write-Output "Bus {bus:2d} Dev {dev} Func 0: VEN=$($ven.ToString('X4')) DEV=$($devid.ToString('X4'))"
        }}
        '''
        r = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, timeout=5)
        out = r.stdout.strip()
        if out:
            print(f"  {out}")
            if '1E7C' in out.upper():
                found = True
                print("  *** BRAINCHIP FOUND! ***")

# Also scan high buses (chipset downstream)
print("\nScanning buses 100-130...\n")
for bus in range(100, 131):
    cmd = f'''
    $inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement
    $result = Invoke-CimMethod -InputObject $inst -MethodName "asio_hw_fun11" -Arguments @{{ Bus = [byte]{bus}; Dev = [byte]0; Func = [byte]0; Reg = [uint16]0; Width = [byte]4 }}
    $data = $result.dwData
    if ($data -ne 0 -and $data -ne 4294967295) {{
        $ven = $data -band 0xFFFF
        $devid = ($data -shr 16) -band 0xFFFF
        Write-Output "Bus {bus:3d} Dev 0 Func 0: VEN=$($ven.ToString('X4')) DEV=$($devid.ToString('X4'))"
    }}
    '''
    r = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, timeout=5)
    out = r.stdout.strip()
    if out:
        print(f"  {out}")
        if '1E7C' in out.upper():
            found = True
            print("  *** BRAINCHIP FOUND! ***")

if not found:
    print("\n1E7C NOT found on any scanned bus.")
    print("The AKD1000 PCIe link is NOT training.")
    print("LED blinks = 3.3V standby power, but no data link.")
else:
    print("\nBRAINCHIP IS ON THE BUS! Reading full config...")

print("\nDone!")
