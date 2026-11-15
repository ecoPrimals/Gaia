"""
UEFI SNIFFER — Learn the ASUS ROG STRIX X870E-E GAMING WIFI mobo.
Reads SMBIOS, ACPI, firmware, PCIe topology, slot config, BIOS settings.
Run before and after reboot to diff what changes.
"""
import subprocess, json, os, time
from datetime import datetime

STATE_DIR = os.path.expanduser('~\\Desktop\\Gaia\\data\\uefi-sniffs')
os.makedirs(STATE_DIR, exist_ok=True)

def ps(cmd, t=15):
    try:
        r = subprocess.run(
            ['powershell', '-NoProfile', '-Command', cmd],
            capture_output=True, text=True, timeout=t
        )
        return (r.stdout + r.stderr).strip()
    except:
        return '(timeout)'

def cmd(c, t=15):
    try:
        r = subprocess.run(c, shell=True, capture_output=True, text=True, timeout=t)
        return (r.stdout + r.stderr).strip()
    except:
        return '(timeout)'

sniff = {}
sniff['timestamp'] = datetime.now().isoformat()
sniff['hostname'] = os.environ.get('COMPUTERNAME', '?')

print('='*60)
print('  UEFI SNIFFER — ASUS ROG STRIX X870E-E GAMING WIFI')
print('='*60)

# === 1. BIOS / Firmware ===
print('\n--- BIOS / FIRMWARE ---')
bios = ps('Get-CimInstance Win32_BIOS | Format-List *')
print(bios[:600])
sniff['bios'] = bios

# === 2. Motherboard ===
print('\n--- MOTHERBOARD ---')
mobo = ps('Get-CimInstance Win32_BaseBoard | Format-List *')
print(mobo[:400])
sniff['motherboard'] = mobo

# === 3. SMBIOS / System ===
print('\n--- SYSTEM ---')
sys_info = ps('Get-CimInstance Win32_ComputerSystem | Select-Object Manufacturer,Model,SystemType,TotalPhysicalMemory,NumberOfProcessors,NumberOfLogicalProcessors | Format-List')
print(sys_info)
sniff['system'] = sys_info

# === 4. Processor ===
print('\n--- CPU ---')
cpu = ps('Get-CimInstance Win32_Processor | Select-Object Name,MaxClockSpeed,NumberOfCores,NumberOfLogicalProcessors,L2CacheSize,L3CacheSize,SocketDesignation | Format-List')
print(cpu)
sniff['cpu'] = cpu

# === 5. Memory ===
print('\n--- MEMORY MODULES ---')
mem = ps('Get-CimInstance Win32_PhysicalMemory | Select-Object BankLabel,Capacity,Speed,ConfiguredClockSpeed,Manufacturer,PartNumber | Format-Table -AutoSize')
print(mem)
sniff['memory'] = mem

# === 6. PCIe Topology (the big one) ===
print('\n--- PCIe TOPOLOGY ---')
# GPU link state
gpu_pcie = cmd('nvidia-smi --query-gpu=pci.bus_id,pcie.link.gen.max,pcie.link.gen.current,pcie.link.width.max,pcie.link.width.current --format=csv')
print(f'GPU PCIe:\n{gpu_pcie}')
sniff['gpu_pcie'] = gpu_pcie

# All PCI devices via PowerShell
print('\n--- ALL PCI DEVICES ---')
pci_devs = ps("""
Get-PnpDevice -Class System,Display,Net,SCSIAdapter,HDC | 
    Where-Object {$_.Status -eq 'OK'} |
    Select-Object Status,Class,FriendlyName,InstanceId |
    Format-Table -AutoSize | Out-String
""")
print(pci_devs[:1200])
sniff['pci_devices'] = pci_devs

# === 7. System Slots (PCIe physical slots) ===
print('\n--- SYSTEM SLOTS ---')
slots = ps("""
Get-CimInstance Win32_SystemSlot | 
    Select-Object SlotDesignation,CurrentUsage,Description,MaxDataWidth,Tag |
    Format-Table -AutoSize | Out-String
""")
print(slots)
sniff['slots'] = slots

# === 8. UEFI Firmware variables (what BIOS exposes) ===
print('\n--- UEFI VARIABLES ---')
# Secure Boot state
sb = ps('Confirm-SecureBootUEFI')
print(f'Secure Boot: {sb}')
sniff['secure_boot'] = sb

# BIOS mode
bios_mode = ps('$env:firmware_type')
print(f'Firmware type: {bios_mode}')
sniff['firmware_type'] = bios_mode

# === 9. ACPI tables ===
print('\n--- ACPI TABLES ---')
acpi = ps("""
$sig = (Get-CimInstance -Namespace root\\wmi -ClassName MSAcpi_ThermalZoneTemperature -ErrorAction SilentlyContinue)
if ($sig) { $sig | Format-Table InstanceName,CurrentTemperature -AutoSize | Out-String }
else { 'ACPI thermal: access denied or not available' }
""")
print(acpi)
sniff['acpi_thermal'] = acpi

# === 10. Storage controllers ===
print('\n--- STORAGE ---')
storage = ps('Get-PhysicalDisk | Select-Object FriendlyName,MediaType,BusType,Size,HealthStatus | Format-Table -AutoSize')
print(storage)
sniff['storage'] = storage

# === 11. Network adapters ===
print('\n--- NETWORK ---')
net = ps('Get-NetAdapter | Select-Object Name,InterfaceDescription,Status,LinkSpeed,MacAddress | Format-Table -AutoSize')
print(net)
sniff['network'] = net

# === 12. USB controllers ===
print('\n--- USB CONTROLLERS ---')
usb = ps("Get-PnpDevice -Class USB | Where-Object {$_.Status -eq 'OK'} | Select-Object FriendlyName | Format-Table -AutoSize | Out-String")
print(usb[:600])
sniff['usb'] = usb

# === 13. Power plan ===
print('\n--- POWER ---')
power = ps('powercfg /getactivescheme')
print(power)
sniff['power'] = power

# === 14. GPU detailed ===
print('\n--- GPU DETAILED ---')
gpu_detail = cmd('nvidia-smi -q 2>&1 | findstr /i "Product PCIe Generation Width Bar1 Power"')
print(gpu_detail)
sniff['gpu_detail'] = gpu_detail

# === 15. ASUS-specific (ArmouryCrate might expose) ===
print('\n--- ASUS-SPECIFIC ---')
asus = ps("Get-Service | Where-Object {$_.DisplayName -match 'ASUS|Armoury|ArmouryCrate|ROG'} | Select-Object Status,DisplayName | Format-Table -AutoSize")
print(asus if asus else '  (no ASUS services)')
sniff['asus_services'] = asus

# Save sniff
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
outfile = os.path.join(STATE_DIR, f'uefi-sniff-{timestamp}.json')
with open(outfile, 'w') as f:
    json.dump(sniff, f, indent=2, default=str)
print(f'\n--- SAVED to {outfile} ---')

# Check for previous sniff to diff
sniffs = sorted([f for f in os.listdir(STATE_DIR) if f.endswith('.json')])
if len(sniffs) > 1:
    prev_file = os.path.join(STATE_DIR, sniffs[-2])
    with open(prev_file) as f:
        prev = json.load(f)
    print(f'\n--- DIFF vs {sniffs[-2]} ---')
    if prev.get('gpu_pcie') != sniff.get('gpu_pcie'):
        print(f'  GPU PCIe CHANGED:')
        print(f'    BEFORE: {prev.get("gpu_pcie", "?").split(chr(10))[-1]}')
        print(f'    AFTER:  {sniff.get("gpu_pcie", "?").split(chr(10))[-1]}')
    else:
        print(f'  GPU PCIe: unchanged')
    if prev.get('memory') != sniff.get('memory'):
        print(f'  MEMORY CONFIG CHANGED')
    if prev.get('slots') != sniff.get('slots'):
        print(f'  SLOT CONFIG CHANGED')
    if prev.get('pci_devices') != sniff.get('pci_devices'):
        print(f'  PCI DEVICES CHANGED')
else:
    print('\n  (first sniff — reboot and run again to get a diff)')

print('\n' + '='*60)
print('  UEFI SNIFF COMPLETE — run again after reboot to diff')
print('='*60)
