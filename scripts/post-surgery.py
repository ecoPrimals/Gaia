"""Post-surgery diagnostic — find AKD1000 + verify PCIe"""
import subprocess

print("=" * 60)
print("POST-SURGERY DIAGNOSTIC — Wave 246")
print("=" * 60)

# 1. Find AKD1000 BrainChip (VEN_1E7C)
print("\n=== AKD1000 BrainChip Scan ===\n")
cmd = '''
Get-PnpDevice | ForEach-Object {
    if ($_.InstanceId -like "*1E7C*" -or $_.FriendlyName -like "*BrainChip*" -or $_.FriendlyName -like "*AKD*" -or $_.FriendlyName -like "*Akida*") {
        $loc = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName DEVPKEY_Device_LocationInfo -ErrorAction SilentlyContinue).Data
        Write-Output "FOUND: $($_.FriendlyName)"
        Write-Output "  Status: $($_.Status)"
        Write-Output "  Class: $($_.Class)"
        Write-Output "  InstanceId: $($_.InstanceId)"
        Write-Output "  Location: $loc"
    }
}
'''
r = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, timeout=30)
print(r.stdout if r.stdout.strip() else "NOT DETECTED via PnP — checking raw PCI...")
if r.stderr: print("ERR:", r.stderr[:200])

# 2. Scan ALL PCI devices for unknown/new ones
print("\n=== New/Unknown PCI Devices ===\n")
cmd2 = '''
Get-PnpDevice | ForEach-Object {
    if ($_.InstanceId -like "PCI*" -and ($_.Status -eq "Error" -or $_.Status -eq "Unknown" -or $_.FriendlyName -like "*PCI Device*" -or $_.FriendlyName -like "*Unknown*")) {
        $loc = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName DEVPKEY_Device_LocationInfo -ErrorAction SilentlyContinue).Data
        Write-Output "$($_.Status.ToString().PadRight(8)) $($_.FriendlyName.PadRight(40)) Bus=$loc ID=$($_.InstanceId.Substring(0, [Math]::Min($_.InstanceId.Length, 60)))"
    }
}
'''
r2 = subprocess.run(['powershell', '-Command', cmd2], capture_output=True, text=True, timeout=30)
print(r2.stdout)

# 3. RTX 5090 PCIe status
print("\n=== RTX 5090 PCIe Link ===\n")
r3 = subprocess.run(['nvidia-smi', '--query-gpu=name,pci.bus_id,pcie.link.gen.current,pcie.link.gen.max,pcie.link.width.current,pcie.link.width.max,memory.total,temperature.gpu,power.draw', '--format=csv'], capture_output=True, text=True, timeout=10)
print(r3.stdout)

# 4. Check the PCIEX16(G4) slot specifically (Bus 5+ area, chipset)
print("\n=== All PCI Devices on Chipset Buses (5-20) ===\n")
cmd4 = '''
Get-PnpDevice | ForEach-Object {
    if ($_.InstanceId -like "PCI*") {
        $loc = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName DEVPKEY_Device_LocationInfo -ErrorAction SilentlyContinue).Data
        if ($loc -match "PCI bus (\d+)" -and [int]$Matches[1] -ge 5 -and [int]$Matches[1] -le 20) {
            Write-Output "Bus $($Matches[1].PadLeft(2)) | $($_.Status.ToString().PadRight(8)) | $($_.FriendlyName)"
        }
    }
}
'''
r4 = subprocess.run(['powershell', '-Command', cmd4], capture_output=True, text=True, timeout=30)
print(r4.stdout)

# 5. Check ALL buses for the new device
print("\n=== Full PCI Bus Scan (looking for 1E7C) ===\n")
cmd5 = '''
Get-WmiObject Win32_PnPEntity | ForEach-Object {
    if ($_.DeviceID -like "*1E7C*") {
        Write-Output "BRAINCHIP FOUND!"
        Write-Output "  Name: $($_.Name)"
        Write-Output "  DeviceID: $($_.DeviceID)"
        Write-Output "  Status: $($_.Status)"
        Write-Output "  ConfigManagerErrorCode: $($_.ConfigManagerErrorCode)"
    }
}
'''
r5 = subprocess.run(['powershell', '-Command', cmd5], capture_output=True, text=True, timeout=30)
print(r5.stdout if r5.stdout.strip() else "1E7C not found in WMI — card may need reseat or BIOS enable")

# 6. Also scan via device manager class filter
print("\n=== Device Manager — All 'System' class PCI ===\n")
cmd6 = '''
Get-PnpDevice -Class System | ForEach-Object {
    if ($_.InstanceId -like "PCI*") {
        $loc = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName DEVPKEY_Device_LocationInfo -ErrorAction SilentlyContinue).Data
        Write-Output "$($_.Status.ToString().PadRight(8)) $loc  $($_.FriendlyName)"
    }
}
'''
r6 = subprocess.run(['powershell', '-Command', cmd6], capture_output=True, text=True, timeout=30)
print(r6.stdout)

# 7. PCIe topology summary
print("\n=== PCIe Slot Summary ===")
print("RTX 5090:   Gen2 x8 current / Gen5 x16 max")
print("            (Gen2 = warm boot improvement from Gen1!)")
print("            (x8 = M.2_2 + M.2_3 lane sharing, expected)")
print("AKD1000:    Searching...")
print()

# 8. Did BIOS settings take?
print("=== BIOS Setting Check ===")
print("Gen2 (not Gen5) means PCIEX16 Link Mode may still be [Auto]")
print("Need to force [GEN 5] in BIOS to get full speed")
print()
print("Done!")
