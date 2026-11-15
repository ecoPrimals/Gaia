"""
FULL HARDWARE CENSUS — northGate pre-surgery baseline.
Enumerate EVERYTHING before we open the case.
If anything changes after surgery, we'll know exactly what shifted.
"""
import subprocess, json, os
from datetime import datetime

STATE_DIR = os.path.expanduser('~\\Desktop\\Gaia\\data\\uefi-sniffs')
os.makedirs(STATE_DIR, exist_ok=True)

def ps(cmd, t=20):
    try:
        r = subprocess.run(['powershell', '-NoProfile', '-Command', cmd],
                          capture_output=True, text=True, timeout=t)
        return (r.stdout + r.stderr).strip()
    except:
        return '(timeout)'

def cmd(c, t=15):
    try:
        r = subprocess.run(c, shell=True, capture_output=True, text=True, timeout=t)
        return (r.stdout + r.stderr).strip()
    except:
        return '(timeout)'

census = {}
census['timestamp'] = datetime.now().isoformat()

print('='*60)
print('  FULL HARDWARE CENSUS — northGate pre-surgery')
print('  Enumerate ALL before we cut')
print('='*60)

# ========================================
# 1. RTX 5090 — THE GPU
# ========================================
print('\n' + '='*50)
print('  1. RTX 5090 (Blackwell)')
print('='*50)
gpu_full = cmd('nvidia-smi -q 2>&1')
# Extract key lines
for line in gpu_full.split('\n'):
    line = line.strip()
    if any(k in line for k in ['Product Name', 'Product Architecture', 'CUDA Version',
        'Driver Version', 'Serial', 'GPU UUID', 'PCIe Generation', 'Link Width',
        'Max Link', 'Current Link', 'BAR1', 'Total', 'Used', 'Free',
        'GPU Current Temp', 'GPU T.Limit', 'Power Draw', 'Power Limit',
        'Memory', 'ECC', 'Retired', 'Remapped', 'Clock', 'Compute Mode',
        'Persistence', 'VBIOS']):
        print(f'  {line}')
census['gpu_full'] = gpu_full

gpu_csv = cmd('nvidia-smi --query-gpu=name,driver_version,pci.bus_id,pcie.link.gen.max,pcie.link.gen.current,pcie.link.width.max,pcie.link.width.current,temperature.gpu,power.draw,power.limit,memory.total,memory.used,memory.free,clocks.gr,clocks.mem,clocks.video,fan.speed,utilization.gpu,utilization.memory --format=csv')
print(f'\n  CSV: {gpu_csv}')
census['gpu_csv'] = gpu_csv

# ========================================
# 2. DDR5 RAM
# ========================================
print('\n' + '='*50)
print('  2. DDR5 RAM (96GB)')
print('='*50)
mem_detail = ps("""
Get-CimInstance Win32_PhysicalMemory | ForEach-Object {
    $gb = [math]::Round($_.Capacity/1GB, 1)
    Write-Output "  DIMM: $($_.BankLabel) | ${gb}GB | Speed:$($_.Speed) | Configured:$($_.ConfiguredClockSpeed) | $($_.Manufacturer) $($_.PartNumber.Trim()) | SN:$($_.SerialNumber)"
}
""")
print(mem_detail)
census['memory_dimms'] = mem_detail

mem_total = ps('(Get-CimInstance Win32_OperatingSystem).TotalVisibleMemorySize')
mem_free = ps('(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory')
if mem_total and mem_total.isdigit():
    t_gb = round(int(mem_total)/1024/1024, 1)
    f_gb = round(int(mem_free)/1024/1024, 1) if mem_free.isdigit() else '?'
    print(f'  Total: {t_gb}GB | Free: {f_gb}GB')
census['memory_totals'] = f'{mem_total} / {mem_free}'

# Memory channels
mem_config = ps('Get-CimInstance Win32_PhysicalMemoryArray | Select-Object MemoryDevices,MaxCapacity | Format-List')
print(f'  Config: {mem_config}')

# ========================================
# 3. CPU — 9950X3D
# ========================================
print('\n' + '='*50)
print('  3. AMD Ryzen 9 9950X3D')
print('='*50)
cpu_detail = ps("""
$cpu = Get-CimInstance Win32_Processor
Write-Output "  Name: $($cpu.Name)"
Write-Output "  Cores: $($cpu.NumberOfCores) | Threads: $($cpu.NumberOfLogicalProcessors)"
Write-Output "  Base Clock: $($cpu.MaxClockSpeed) MHz"
Write-Output "  Socket: $($cpu.SocketDesignation)"
Write-Output "  L2: $([math]::Round($cpu.L2CacheSize/1024, 1))MB | L3: $([math]::Round($cpu.L3CacheSize/1024, 0))MB"
Write-Output "  Voltage: $($cpu.CurrentVoltage)"
Write-Output "  Status: $($cpu.Status)"
Write-Output "  ProcessorId: $($cpu.ProcessorId)"
""")
print(cpu_detail)
census['cpu'] = cpu_detail

# CPU temperature via WMI (if available)
cpu_temp = ps('Get-CimInstance MSAcpi_ThermalZoneTemperature -Namespace root/wmi -ErrorAction SilentlyContinue | Select-Object InstanceName,CurrentTemperature | Format-Table -AutoSize')
print(f'  Thermal: {cpu_temp[:200] if cpu_temp else "(not available)"}')

# ========================================
# 4. NVMe DRIVES
# ========================================
print('\n' + '='*50)
print('  4. NVMe Storage (9TB)')
print('='*50)
storage = ps("""
Get-PhysicalDisk | ForEach-Object {
    $gb = [math]::Round($_.Size/1GB, 0)
    Write-Output "  $($_.FriendlyName) | ${gb}GB | $($_.MediaType) | $($_.BusType) | Health:$($_.HealthStatus) | Op:$($_.OperationalStatus)"
}
""")
print(storage)
census['storage_disks'] = storage

# NVMe health via SMART
nvme_health = ps("""
Get-PhysicalDisk | Get-StorageReliabilityCounter -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Output "  Disk$($_.DeviceId): Temp=$($_.Temperature)C | Wear=$($_.Wear)% | ReadErrors=$($_.ReadErrorsTotal) | WriteErrors=$($_.WriteErrorsTotal) | PowerOnHours=$($_.PowerOnHours)"
}
""")
print(f'\n  SMART:\n{nvme_health}')
census['nvme_smart'] = nvme_health

# Drive letters and space
drives = ps("""
Get-PSDrive -PSProvider FileSystem | Where-Object {$_.Used -gt 0} | ForEach-Object {
    $used = [math]::Round($_.Used/1GB,1)
    $free = [math]::Round($_.Free/1GB,1)
    $total = $used + $free
    Write-Output "  $($_.Name): ${used}GB used / ${total}GB total (${free}GB free)"
}
""")
print(f'\n  Volumes:\n{drives}')
census['volumes'] = drives

# ========================================
# 5. PCIe TOPOLOGY — FULL
# ========================================
print('\n' + '='*50)
print('  5. PCIe Topology')
print('='*50)
pcie = ps("""
Get-PnpDevice | Where-Object {$_.InstanceId -match '^PCI'} |
    Select-Object Status,Class,FriendlyName |
    Sort-Object Class,FriendlyName |
    Format-Table -AutoSize | Out-String
""")
print(pcie[:1500])
census['pcie_devices'] = pcie

# ========================================
# 6. MOTHERBOARD SENSORS
# ========================================
print('\n' + '='*50)
print('  6. Motherboard / Sensors')
print('='*50)
# BIOS version
print(f'  BIOS: {ps("(Get-CimInstance Win32_BIOS).Name")}')
print(f'  Board: {ps("(Get-CimInstance Win32_BaseBoard).Product")}')
print(f'  Serial: {ps("(Get-CimInstance Win32_BaseBoard).SerialNumber")}')

# Fan/voltage via ASUS if available
asus = ps("Get-Service | Where-Object {$_.DisplayName -match 'Fan'} | Select-Object Status,DisplayName | Format-Table -AutoSize")
print(f'  ASUS Fan Service: {asus}')

# ========================================
# 7. USB DEVICES
# ========================================
print('\n' + '='*50)
print('  7. USB Devices')
print('='*50)
usb = ps("""
Get-PnpDevice -Class USB,HIDClass -ErrorAction SilentlyContinue |
    Where-Object {$_.Status -eq 'OK'} |
    Select-Object Class,FriendlyName |
    Sort-Object Class |
    Format-Table -AutoSize | Out-String
""")
print(usb[:800])
census['usb'] = usb

# ========================================
# 8. NETWORK
# ========================================
print('\n' + '='*50)
print('  8. Network')
print('='*50)
net = ps('Get-NetAdapter | Select-Object Name,InterfaceDescription,Status,LinkSpeed,MacAddress | Format-Table -AutoSize')
print(net)
census['network'] = net

# ========================================
# SAVE CENSUS
# ========================================
outfile = os.path.join(STATE_DIR, f'pre-surgery-census-{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
with open(outfile, 'w') as f:
    json.dump(census, f, indent=2, default=str)

print(f'\n{"="*60}')
print(f'  CENSUS SAVED: {outfile}')
print(f'  Run again AFTER surgery to diff.')
print(f'  Every bit of silicon is counted.')
print(f'{"="*60}')
