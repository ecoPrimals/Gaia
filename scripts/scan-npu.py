"""
SCAN NPU — Find BrainChip Akida in eastGate + probe northGate PCIe slots.
Pre-surgery: know what we have before installing chip #2.
"""
import paramiko, subprocess

# === eastGate — where chip #1 lives ===
print('='*60)
print('  NPU SCAN — BrainChip Akida (0x1E7C)')
print('='*60)

east = paramiko.SSHClient()
east.set_missing_host_key_policy(paramiko.AutoAddPolicy())
east.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=5)

def erun(cmd, t=10):
    _, out, _ = east.exec_command(cmd, timeout=t)
    try: return out.read().decode().strip()
    except: return '(timeout)'

print('\n--- eastGate: BrainChip Akida ---')
akida = erun('lspci -d 1e7c: -vvv 2>&1')
if akida:
    print(akida)
else:
    print('  BrainChip device NOT FOUND in lspci')
    print('  Trying broader search...')
    print(erun('lspci | grep -iE "brain|akida|1e7c|neural|npu" 2>&1'))

print('\n--- eastGate: akida sysfs ---')
print(erun('ls -la /sys/bus/pci/devices/*/akida_clock_mode 2>&1 | head -5'))

print('\n--- eastGate: akida kernel module ---')
print(erun('lsmod | grep -iE "akida|brainchip" 2>&1'))
print(erun('modinfo akida 2>/dev/null | head -10 2>&1'))

print('\n--- eastGate: /dev/akida* ---')
print(erun('ls -la /dev/akida* 2>&1'))

print('\n--- eastGate: VFIO groups ---')
print(erun('ls -la /dev/vfio/ 2>&1'))

print('\n--- eastGate: ALL PCIe slots ---')
print(erun('lspci -nn 2>&1'))

east.close()

# === northGate (Windows) — check PCIe slots before surgery ===
print('\n' + '='*60)
print('  northGate: PCIe slots (pre-surgery)')
print('='*60)

# nvidia-smi shows the GPU PCIe info
print('\n--- GPU PCIe info ---')
r = subprocess.run('nvidia-smi --query-gpu=pci.bus_id,pcie.link.gen.current,pcie.link.width.current --format=csv,noheader',
                    shell=True, capture_output=True, text=True, timeout=10)
print(r.stdout.strip())

# Check if any BrainChip device already exists (shouldn't yet)
print('\n--- BrainChip in Windows device list ---')
r = subprocess.run(
    'powershell -NoProfile -Command "Get-PnpDevice | Where-Object {$_.FriendlyName -match \'brain|akida|neural|npu\'} | Format-Table Status,Class,FriendlyName -AutoSize"',
    shell=True, capture_output=True, text=True, timeout=10
)
print(r.stdout.strip() if r.stdout.strip() else '  (none found — expected, chip not installed yet)')

# Show available PCIe slots via device manager
print('\n--- northGate PCIe devices ---')
r = subprocess.run(
    'powershell -NoProfile -Command "Get-PnpDevice -Class System | Where-Object {$_.FriendlyName -match \'PCI\'} | Format-Table Status,FriendlyName -AutoSize"',
    shell=True, capture_output=True, text=True, timeout=10
)
print(r.stdout.strip()[:800])

# Motherboard / chipset info
print('\n--- Motherboard ---')
r = subprocess.run(
    'powershell -NoProfile -Command "Get-CimInstance Win32_BaseBoard | Select-Object Manufacturer,Product,SerialNumber | Format-List"',
    shell=True, capture_output=True, text=True, timeout=10
)
print(r.stdout.strip())

# Available PCIe slots from BIOS
print('\n--- System slots ---')
r = subprocess.run(
    'powershell -NoProfile -Command "Get-CimInstance Win32_SystemSlot | Format-Table SlotDesignation,CurrentUsage,Description -AutoSize"',
    shell=True, capture_output=True, text=True, timeout=10
)
print(r.stdout.strip()[:800])

print('\n' + '='*60)
print('  NPU SCAN COMPLETE')
print('  eastGate chip #1: check above')
print('  northGate: ready for chip #2 install')
print('  Chip #3: TO FIND')
print('='*60)
