"""Post-reboot probe — verify AKD1000 + PCIe Gen5 + iGPU"""
import subprocess, json, time
from datetime import datetime

print("=" * 60)
print(f"POST-REBOOT PROBE — {datetime.now().strftime('%H:%M:%S')}")
print("=" * 60)

results = {}

# 1. AKD1000 BrainChip
print("\n[1/6] AKD1000 BrainChip (VEN_1E7C)...\n")
cmd = '''
Get-PnpDevice | ForEach-Object {
    if ($_.InstanceId -like "*1E7C*") {
        $loc = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName DEVPKEY_Device_LocationInfo -ErrorAction SilentlyContinue).Data
        Write-Output "BRAINCHIP DETECTED!"
        Write-Output "  Name: $($_.FriendlyName)"
        Write-Output "  Status: $($_.Status)"
        Write-Output "  Location: $loc"
        Write-Output "  InstanceId: $($_.InstanceId)"
    }
}
'''
r = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, timeout=30)
if '1E7C' in r.stdout.upper() or 'BRAINCHIP' in r.stdout.upper():
    print("  ✅ " + r.stdout)
    results['akd1000'] = 'DETECTED'
else:
    # Check for any new unknown PCI devices
    cmd_unk = '''
    Get-PnpDevice | ForEach-Object {
        if ($_.InstanceId -like "PCI*" -and ($_.FriendlyName -like "*PCI Device*" -or $_.Status -eq "Error") -and $_.InstanceId -notlike "*1022*" -and $_.InstanceId -notlike "*14C3*") {
            $loc = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName DEVPKEY_Device_LocationInfo -ErrorAction SilentlyContinue).Data
            Write-Output "  NEW? $($_.FriendlyName) | $($_.Status) | $loc | $($_.InstanceId)"
        }
    }
    '''
    r2 = subprocess.run(['powershell', '-Command', cmd_unk], capture_output=True, text=True, timeout=30)
    if r2.stdout.strip():
        print("  ⚠️ New PCI devices found (could be AKD1000):")
        print(r2.stdout)
        results['akd1000'] = 'POSSIBLE'
    else:
        print("  ❌ Not detected — may need deeper reseat")
        results['akd1000'] = 'NOT_FOUND'

# 2. RTX 5090 PCIe speed
print("\n[2/6] RTX 5090 PCIe Link...\n")
r3 = subprocess.run([
    'nvidia-smi',
    '--query-gpu=name,pcie.link.gen.current,pcie.link.gen.max,pcie.link.width.current,pcie.link.width.max,temperature.gpu,power.draw',
    '--format=csv,noheader'
], capture_output=True, text=True, timeout=10)
parts = r3.stdout.strip().split(', ')
if len(parts) >= 5:
    gen_cur, gen_max = parts[1], parts[2]
    width_cur, width_max = parts[3], parts[4]
    print(f"  GPU: {parts[0]}")
    print(f"  PCIe: Gen{gen_cur} x{width_cur} (max: Gen{gen_max} x{width_max})")
    print(f"  Temp: {parts[5] if len(parts) > 5 else '?'}°C, Power: {parts[6] if len(parts) > 6 else '?'}")
    
    if gen_cur == '5':
        print("  ✅ GEN 5 ACHIEVED!")
    elif gen_cur in ('1', '2'):
        print(f"  ⚠️ Gen{gen_cur} at idle is NORMAL (power saving)")
        print("  Running quick GPU load to check max speed...")
        # Brief GPU load to force PCIe ramp
        load_cmd = 'nvidia-smi --query-gpu=pcie.link.gen.current,pcie.link.width.current --format=csv,noheader -l 1'
        r_load = subprocess.run(['nvidia-smi', '-q', '-d', 'PERFORMANCE'], capture_output=True, text=True, timeout=10)
        if 'Gen5' in r_load.stdout or 'Gen 5' in r_load.stdout:
            print("  ✅ Max capable = Gen5!")
        print(r_load.stdout[:500] if r_load.stdout else "")
    results['pcie_gen'] = gen_cur
    results['pcie_width'] = width_cur
else:
    print(f"  Raw: {r3.stdout}")

# 3. iGPU
print("\n[3/6] iGPU Multi-Monitor...\n")
cmd4 = '''
Get-PnpDevice | ForEach-Object {
    if ($_.InstanceId -like "*VEN_1002&DEV_13C0*") {
        Write-Output "AMD Radeon iGPU: $($_.Status)"
    }
}
'''
r4 = subprocess.run(['powershell', '-Command', cmd4], capture_output=True, text=True, timeout=10)
print(f"  {r4.stdout.strip()}")
results['igpu'] = 'OK' if 'OK' in r4.stdout else 'Unknown'

# 4. Displays
print("\n[4/6] Displays...\n")
cmd5 = '''
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Screen]::AllScreens | ForEach-Object {
    Write-Output "  $($_.DeviceName) | Primary=$($_.Primary) | $($_.Bounds.Width)x$($_.Bounds.Height)"
}
'''
r5 = subprocess.run(['powershell', '-Command', cmd5], capture_output=True, text=True, timeout=10)
print(r5.stdout)

cmd5b = '''
Get-CimInstance Win32_VideoController | ForEach-Object {
    Write-Output "  $($_.Name): $($_.CurrentHorizontalResolution)x$($_.CurrentVerticalResolution) @ $($_.CurrentRefreshRate)Hz"
}
'''
r5b = subprocess.run(['powershell', '-Command', cmd5b], capture_output=True, text=True, timeout=10)
print(r5b.stdout)

# 5. Network
print("\n[5/6] Network...\n")
for target, name in [('192.168.4.1', 'Gateway'), ('192.168.4.244', 'eastGate'), ('8.8.8.8', 'Internet')]:
    r = subprocess.run(['ping', '-n', '1', '-w', '2000', target], capture_output=True, text=True, timeout=5)
    status = '✅' if r.returncode == 0 else '❌'
    print(f"  {status} {name} ({target})")

# 6. biomeOS
print("\n[6/6] biomeOS Primals...\n")
cmd6 = '''
$procs = Get-Process | Where-Object { $_.ProcessName -match "biomeOS|barracuda|beardog|nestgate|squirrel|toadstool" }
Write-Output "  Active primal families: $($procs | Select-Object -Unique ProcessName | Measure-Object | Select-Object -ExpandProperty Count)"
Write-Output "  Total primal processes: $($procs | Measure-Object | Select-Object -ExpandProperty Count)"
'''
r6 = subprocess.run(['powershell', '-Command', cmd6], capture_output=True, text=True, timeout=10)
print(r6.stdout)

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
akd = results.get('akd1000', '?')
gen = results.get('pcie_gen', '?')
width = results.get('pcie_width', '?')
igpu = results.get('igpu', '?')
akd_icon = '✅' if akd == 'DETECTED' else ('⚠️' if akd == 'POSSIBLE' else '❌')
gen_icon = '✅' if gen == '5' else ('⚡' if gen in ('1','2') else '❌')
igpu_icon = '✅' if igpu == 'OK' else '⚠️'
print(f"  {akd_icon} AKD1000: {akd}")
print(f"  {gen_icon} PCIe: Gen{gen} x{width} (Gen1/2 at idle = normal)")
print(f"  {igpu_icon} iGPU: {igpu}")
print()

# Save results
out_path = 'data/uefi-sniffs/post-surgery-probe.json'
try:
    results['timestamp'] = datetime.now().isoformat()
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"  Saved to {out_path}")
except:
    pass
