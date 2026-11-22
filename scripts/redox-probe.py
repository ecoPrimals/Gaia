"""Full redox probe — AKD1000 + Display 2 + biomeOS + PCIe"""
import subprocess, json
from datetime import datetime

print("=" * 60)
print(f"REDOX PROBE — {datetime.now().strftime('%H:%M:%S')}")
print("=" * 60)

# 1. AKD1000 — THE BIG ONE
print("\n[1] AKD1000 BrainChip Hunt...\n")
cmd = '''
$found = $false
Get-PnpDevice | ForEach-Object {
    if ($_.InstanceId -like "*1E7C*") {
        $loc = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName DEVPKEY_Device_LocationInfo -ErrorAction SilentlyContinue).Data
        Write-Output "BRAINCHIP FOUND ON PCI BUS!"
        Write-Output "  Name: $($_.FriendlyName)"
        Write-Output "  Status: $($_.Status)"  
        Write-Output "  Location: $loc"
        Write-Output "  ID: $($_.InstanceId)"
        $found = $true
    }
}
if (-not $found) {
    # Check for ANY new unknown PCI device that wasn't there before
    Get-PnpDevice | ForEach-Object {
        if ($_.InstanceId -like "PCI*" -and $_.InstanceId -notlike "*1022*" -and $_.InstanceId -notlike "*10DE*" -and $_.InstanceId -notlike "*1002*" -and $_.InstanceId -notlike "*144D*" -and $_.InstanceId -notlike "*15B7*" -and $_.InstanceId -notlike "*14C3*" -and $_.InstanceId -notlike "*10EC*" -and $_.InstanceId -notlike "*1B21*") {
            $loc = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName DEVPKEY_Device_LocationInfo -ErrorAction SilentlyContinue).Data
            Write-Output "NEW PCI DEVICE: $($_.FriendlyName) | $($_.Status) | $loc"
            Write-Output "  ID: $($_.InstanceId)"
        }
    }
    Write-Output "1E7C not in device tree — checking all vendor IDs..."
    $vids = @{}
    Get-PnpDevice | ForEach-Object {
        if ($_.InstanceId -match "PCI\\\\VEN_([0-9A-F]{4})") {
            $vids[$Matches[1]] = $true
        }
    }
    Write-Output "Known VENs: $($vids.Keys -join ', ')"
}
'''
r1 = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, timeout=30)
print(r1.stdout)

# 2. Displays — both eyes
print("\n[2] Display Eyes...\n")
cmd2 = '''
Add-Type -AssemblyName System.Windows.Forms
$screens = [System.Windows.Forms.Screen]::AllScreens
Write-Output "Total displays: $($screens.Count)"
foreach ($s in $screens) {
    Write-Output "  $($s.DeviceName) Primary=$($s.Primary) $($s.Bounds.Width)x$($s.Bounds.Height) at ($($s.Bounds.X),$($s.Bounds.Y))"
}
'''
r2 = subprocess.run(['powershell', '-Command', cmd2], capture_output=True, text=True, timeout=10)
print(r2.stdout)

cmd2b = '''
Get-PnpDevice -Class Display | ForEach-Object {
    Write-Output "$($_.FriendlyName): $($_.Status)"
}
Get-PnpDevice -Class Monitor -Status OK | ForEach-Object {
    $loc = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName DEVPKEY_Device_LocationInfo -ErrorAction SilentlyContinue).Data
    Write-Output "Monitor: $($_.FriendlyName) | $loc"
}
'''
r2b = subprocess.run(['powershell', '-Command', cmd2b], capture_output=True, text=True, timeout=10)
print(r2b.stdout)

# 3. RTX 5090 PCIe
print("\n[3] RTX 5090 PCIe...\n")
r3 = subprocess.run(['nvidia-smi', '--query-gpu=name,pcie.link.gen.current,pcie.link.gen.max,pcie.link.width.current,pcie.link.width.max,temperature.gpu,power.draw', '--format=csv,noheader'], capture_output=True, text=True, timeout=10)
print(f"  {r3.stdout.strip()}")

# 4. biomeOS state — clean up sockets
print("\n[4] biomeOS Membrane State...\n")
import os, glob
membrane_dir = r'C:\Users\mokke\Desktop\Gaia\runtime\membrane'
if os.path.exists(membrane_dir):
    files = os.listdir(membrane_dir)
    print(f"  Membrane dir has {len(files)} files:")
    for f in sorted(files):
        fpath = os.path.join(membrane_dir, f)
        size = os.path.getsize(fpath)
        print(f"    {f} ({size}b)")
else:
    print(f"  No membrane dir at {membrane_dir}")

# 5. biomeOS processes
print("\n[5] biomeOS Processes...\n")
cmd5 = '''
$primals = @("biomeos","barracuda","beardog","nestgate","squirrel","toadstool","songbird","skunkbat","petaltongue","rhizocrypt","loamspine","coralreef","swarmvine","sweetgrass","dromedary","bingocube","sourdough")
foreach ($p in $primals) {
    $procs = Get-Process -Name $p -ErrorAction SilentlyContinue
    if ($procs) {
        Write-Output "  $($p.PadRight(15)) ALIVE x$($procs.Count)"
    }
}
'''
r5 = subprocess.run(['powershell', '-Command', cmd5], capture_output=True, text=True, timeout=10)
print(r5.stdout if r5.stdout.strip() else "  No primals running")

# 6. Network
print("\n[6] Network...\n")
for target, name in [('192.168.4.244', 'eastGate'), ('8.8.8.8', 'Internet')]:
    r = subprocess.run(['ping', '-n', '1', '-w', '1000', target], capture_output=True, text=True, timeout=5)
    print(f"  {'OK' if r.returncode == 0 else 'FAIL'} {name}")

print("\nDone!")
