"""BIOS Healer — reads all BIOS settings via ASUS WMI, diagnoses, prescribes fixes.
Wire this into biomeOS as a self-healing hook on every boot."""
import subprocess, json, os
from datetime import datetime

print("=" * 60)
print("BIOS HEALER — Gaia reads her own firmware")
print("=" * 60)

# All discovered ASUS WMI option names
BIOS_OPTIONS = {
    "UmaFrameBufferSize": {"want": 512, "desc": "iGPU memory (MB)", "fix": "NB Config → UMA Frame Buffer Size = [512M]"},
    "PrimaryVideo": {"want": 2, "desc": "Primary display (2=PCIE)", "fix": "NB Config → Primary Video Device = [PCIE Video]"},
}

# Read all BIOS settings
print("\n[1] Reading BIOS via ASUS WMI...\n")
readings = {}
prescriptions = []

for name, config in BIOS_OPTIONS.items():
    cmd = f'''
    $inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement
    $result = Invoke-CimMethod -InputObject $inst -MethodName "GetOptionData" -Arguments @{{ OptionName = "{name}" }}
    Write-Output "$($result.Value)|$($result.ErrorCode)"
    '''
    r = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, timeout=10)
    parts = r.stdout.strip().split('|')
    if len(parts) == 2:
        value = int(parts[0])
        error = int(parts[1])
        readings[name] = {"value": value, "error": error}
        
        if error == 0:
            status = "✅" if value == config["want"] else "⚠️ WRONG"
            print(f"  {status} {name} = {value} (want: {config['want']}) — {config['desc']}")
            if value != config["want"]:
                prescriptions.append(config["fix"])
        else:
            print(f"  ❌ {name}: Error {error}")

# Hardware checks
print("\n[2] Hardware state...\n")

# PCIe Gen
r = subprocess.run(['nvidia-smi', '--query-gpu=pcie.link.gen.current,pcie.link.gen.max,pcie.link.width.current,pcie.link.width.max', '--format=csv,noheader'], capture_output=True, text=True, timeout=5)
pcie = r.stdout.strip()
print(f"  RTX 5090 PCIe: {pcie}")

# iGPU
cmd = 'Get-PnpDevice -Class Display | ForEach-Object { Write-Output "$($_.FriendlyName): $($_.Status)" }'
r = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, timeout=10)
for line in r.stdout.strip().split('\n'):
    if line.strip():
        print(f"  {line.strip()}")
        if 'Unknown' in line or 'Error' in line:
            if 'AMD' in line or 'Radeon' in line:
                prescriptions.append("NB Config → Integrated Graphics = [Force]")

# AKD1000
cmd2 = '''
$found = $false
Get-PnpDevice | ForEach-Object {
    if ($_.InstanceId -like "*1E7C*") { Write-Output "AKD1000: $($_.Status)"; $found = $true }
}
if (-not $found) { Write-Output "AKD1000: NOT ON BUS" }
'''
r2 = subprocess.run(['powershell', '-Command', cmd2], capture_output=True, text=True, timeout=10)
akd_status = r2.stdout.strip()
print(f"  {akd_status}")
if 'NOT ON BUS' in akd_status:
    prescriptions.append("AMD CBS → NBIO → Persistence mode for legacy endpoints = [Enable]")
    prescriptions.append("Physical: reseat AKD1000 in PCIEX16(G4), clean gold fingers")

# Displays
cmd3 = '''
Add-Type -AssemblyName System.Windows.Forms
Write-Output "Displays: $([System.Windows.Forms.Screen]::AllScreens.Count)"
'''
r3 = subprocess.run(['powershell', '-Command', cmd3], capture_output=True, text=True, timeout=10)
print(f"  {r3.stdout.strip()}")

# Prescription
print("\n" + "=" * 60)
if prescriptions:
    print("PRESCRIPTION — Next reboot, apply these BIOS fixes:\n")
    for i, rx in enumerate(prescriptions, 1):
        print(f"  {i}. {rx}")
else:
    print("ALL HEALTHY — no BIOS fixes needed!")

# Save state
state = {
    "timestamp": datetime.now().isoformat(),
    "readings": readings,
    "prescriptions": prescriptions,
    "pcie": pcie,
    "akd1000": akd_status,
}
out_path = os.path.join("data", "uefi-sniffs", "bios-healer-state.json")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(state, f, indent=2)
print(f"\n  State saved to {out_path}")
print("  Wire into biomeOS cron for self-healing on every boot!")
