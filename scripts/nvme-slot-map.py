"""Map NVMe drives to M.2 physical slots on X870E-E"""
import subprocess, json, re

print("=== NVMe → M.2 Slot Mapping ===\n")

# Get NVMe controllers via PnP with PCI location
cmd = '''
Get-PnpDevice | Where-Object { $_.InstanceId -like "PCI\\VEN_144D*" -or $_.InstanceId -like "PCI\\VEN_15B7*" -or ($_.InstanceId -like "PCI\\VEN_*" -and $_.FriendlyName -like "*NVMe*") } | ForEach-Object {
    $dev = $_
    $loc = (Get-PnpDeviceProperty -InstanceId $dev.InstanceId -KeyName DEVPKEY_Device_LocationInfo -ErrorAction SilentlyContinue).Data
    $addr = (Get-PnpDeviceProperty -InstanceId $dev.InstanceId -KeyName DEVPKEY_Device_Address -ErrorAction SilentlyContinue).Data
    [PSCustomObject]@{
        InstanceId = $dev.InstanceId
        Name = $dev.FriendlyName
        Status = $dev.Status
        Location = $loc
        Address = $addr
    }
} | Format-List
'''
r = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, timeout=15)
print(r.stdout)
if r.stderr: print("ERR:", r.stderr[:300])

# Also get the PCIe root port tree to understand which slots the NVMe are behind
print("\n=== PCIe Root Complex → NVMe path ===\n")
cmd2 = '''
Get-PnpDevice -Class "System" | Where-Object { $_.FriendlyName -like "*PCI Express Root Port*" -or $_.FriendlyName -like "*Root Complex*" -or $_.FriendlyName -like "*Upstream*" } | Select-Object InstanceId, FriendlyName, Status | Format-Table -AutoSize -Wrap
'''
r2 = subprocess.run(['powershell', '-Command', cmd2], capture_output=True, text=True, timeout=15)
print(r2.stdout)

# Get the actual PCIe addresses
print("\n=== All PCI devices with Bus/Dev/Func ===\n")
cmd3 = '''
Get-WmiObject Win32_PnPEntity | Where-Object { $_.DeviceID -like "PCI\\VEN_*" } | ForEach-Object {
    $loc = $_.GetDeviceProperties("DEVPKEY_Device_LocationInfo").DeviceProperties[0].Data
    if ($loc -match "PCI bus (\d+)") {
        "$($_.DeviceID.Substring(0,30).PadRight(30)) Bus=$($matches[1].PadRight(3)) $($_.Name.Substring(0, [Math]::Min($_.Name.Length, 60)))"
    }
} | Sort-Object
'''
r3 = subprocess.run(['powershell', '-Command', cmd3], capture_output=True, text=True, timeout=30)
print(r3.stdout[:3000])

# The key mapping for X870E-E with 9950X3D:
# CPU PCIe lanes: Bus 0 root
# M.2_1 = CPU attached, own lanes (Gen5 x4) - usually Bus 1 or 2
# M.2_2 = CPU attached, SHARES with PCIEX16(G5) - steals x4 from GPU
# M.2_3 = CPU attached, SHARES with PCIEX16(G5) - steals x4 from GPU  
# M.2_4 = Chipset attached (Gen4 x4)
# M.2_5 = Chipset attached (Gen4 x4)
# PCIEX16(G5) = CPU direct (Gen5 x16/x8)
# PCIEX16(G4) = Chipset (Gen4 x4)

print("\n=== PCIe Link Speed for GPU ===\n")
cmd4 = '''
$gpu = Get-PnpDevice | Where-Object { $_.FriendlyName -like "*5090*" -or $_.FriendlyName -like "*NVIDIA*GeForce*" }
foreach ($g in $gpu) {
    $props = Get-PnpDeviceProperty -InstanceId $g.InstanceId
    Write-Output "GPU: $($g.FriendlyName)"
    Write-Output "ID: $($g.InstanceId)"
    $locProp = $props | Where-Object { $_.KeyName -eq "DEVPKEY_Device_LocationInfo" }
    Write-Output "Location: $($locProp.Data)"
    
    # Extract bus number from InstanceId
    if ($g.InstanceId -match "PCI\\\\VEN_10DE&DEV_\w+&SUBSYS_\w+&REV_\w+\\\\(\w+)") {
        Write-Output "PCI Address: $($matches[1])"
    }
}
'''
r4 = subprocess.run(['powershell', '-Command', cmd4], capture_output=True, text=True, timeout=15)
print(r4.stdout)
if r4.stderr: print("ERR:", r4.stderr[:200])

print("\n=== StorageController PCIe Addresses ===\n")
cmd5 = '''
Get-WmiObject -Namespace root\\Microsoft\\Windows\\Storage -Class MSFT_StorageSubSystem | 
    Get-CimAssociatedInstance -ResultClassName MSFT_PhysicalDisk |
    Select-Object DeviceId, FriendlyName, PhysicalLocation, @{N='SizeGB';E={[math]::Round($_.Size/1GB,1)}} |
    Format-Table -AutoSize
'''
r5 = subprocess.run(['powershell', '-Command', cmd5], capture_output=True, text=True, timeout=15)
print(r5.stdout)

print("\nDone — check Bus numbers against X870E-E topology!")
