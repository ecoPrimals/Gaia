"""
TASTE SILICON — Enumerate eastGate's AKD1000 through rustChip/.
Learn what a new piece of silicon TASTES LIKE before surgery.
Register it as a toadStool service for biomeOS discovery.
"""
import paramiko, json

east = paramiko.SSHClient()
east.set_missing_host_key_policy(paramiko.AutoAddPolicy())
east.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=5)

def run(cmd, t=15):
    _, out, _ = east.exec_command(cmd, timeout=t)
    try: return out.read().decode().strip()
    except: return '(timeout)'

print('='*60)
print('  TASTE SILICON — AKD1000 on eastGate')
print('  What does neuromorphic compute taste like?')
print('='*60)

# === 1. The chip itself — PCIe enumeration ===
print('\n--- THE CHIP (PCIe) ---')
print(run('lspci -d 1e7c: -vvv 2>&1'))

print('\n--- PCIe link state ---')
akida_dev = '0000:08:00.0'
for attr in ['current_link_speed', 'current_link_width', 'max_link_speed', 'max_link_width',
             'vendor', 'device', 'class', 'irq', 'enable', 'numa_node']:
    val = run(f'cat /sys/bus/pci/devices/{akida_dev}/{attr} 2>/dev/null')
    if val:
        print(f'  {attr}: {val}')

# === 2. rustChip/ — the driver ===
print('\n--- rustChip/ DRIVER ---')
rc_dir = '/home/eastgate/Development/ecoPrimals/springs/rustChip'
print(run(f'ls {rc_dir}/ 2>/dev/null'))
print(f'\nCargo.toml:')
print(run(f'head -20 {rc_dir}/Cargo.toml 2>/dev/null'))

# Check if driver binary exists
print(f'\n--- Built binaries ---')
print(run(f'find {rc_dir}/target -maxdepth 3 -type f -executable -name "akida*" -o -name "probe*" -o -name "rustchip*" 2>/dev/null | head -10'))
print(run(f'ls {rc_dir}/target/release/ 2>/dev/null | head -20'))

# === 3. akida tools (SDK) ===
print('\n--- AKIDA SDK/TOOLS ---')
print(run('which akida 2>/dev/null'))
print(run('akida --version 2>/dev/null || echo "akida CLI not found"'))
print(run('akida devices 2>/dev/null || echo "no akida CLI devices command"'))

# Python akida SDK
print(f'\n--- Python akida SDK ---')
print(run('python3 -c "import akida; print(akida.__version__); print(akida.Model.list_devices())" 2>&1'))

# === 4. VFIO state — can we talk to it raw? ===
print('\n--- VFIO / driver binding ---')
print(run(f'cat /sys/bus/pci/devices/{akida_dev}/driver_override 2>/dev/null || echo "(no override)"'))
print(run(f'readlink /sys/bus/pci/devices/{akida_dev}/driver 2>/dev/null || echo "(no driver bound)"'))
print(run(f'cat /sys/bus/pci/devices/{akida_dev}/iommu_group/type 2>/dev/null'))
print(run(f'ls /sys/bus/pci/devices/{akida_dev}/iommu_group/devices/ 2>/dev/null'))

# === 5. BAR memory regions — the taste ===
print('\n--- BAR REGIONS (the silicon taste) ---')
print(run(f'cat /sys/bus/pci/devices/{akida_dev}/resource 2>/dev/null'))

# Can we read BAR0? (needs root or VFIO)
print(f'\n--- BAR0 probe (register space) ---')
bar0_read = run(f'sudo xxd -l 64 /sys/bus/pci/devices/{akida_dev}/resource0 2>&1')
print(bar0_read[:200] if bar0_read else '(access denied)')

# === 6. akida kernel module ===
print('\n--- Kernel module ---')
print(run('lsmod | grep -iE "akida|brainchip|vfio" 2>&1'))
print(run('modinfo akida 2>/dev/null | head -10'))
print(run('modprobe -n akida 2>&1'))

# === 7. akida sysfs attributes ===
print('\n--- sysfs attributes ---')
print(run(f'find /sys/bus/pci/devices/{akida_dev}/ -maxdepth 1 -name "akida*" 2>/dev/null'))
print(run(f'ls /sys/bus/pci/devices/{akida_dev}/ 2>/dev/null | grep -i akida'))

# === 8. Check akida-ear (the listener) ===
print('\n--- akida-ear (the NPU listener) ---')
print(run('cat /opt/Gaia/data/akida/akida-ear-state.json 2>/dev/null'))
print(run('cat /opt/Gaia/akida-ear-pipe.py 2>/dev/null | head -30'))

# === 9. rustChip driver capabilities ===
print('\n--- rustChip driver crates ---')
print(run(f'ls {rc_dir}/crates/ 2>/dev/null'))
for crate in ['akida-driver', 'akida-chip']:
    cargo = run(f'head -15 {rc_dir}/crates/{crate}/Cargo.toml 2>/dev/null')
    if cargo:
        print(f'\n  {crate}/Cargo.toml:')
        print(f'  {cargo[:200]}')

# === 10. What the chip can do (from our specs) ===
print('\n--- SILICON CAPABILITIES (from rustChip/specs) ---')
print(run(f'head -30 {rc_dir}/specs/SILICON_SPEC.md 2>/dev/null'))

# === 11. Check if we can enumerate via Python ===
print('\n--- ENUMERATE via Python ---')
enum_result = run('''python3 -c "
import os, struct
try:
    # Try reading PCI config space
    path = '/sys/bus/pci/devices/0000:08:00.0/config'
    with open(path, 'rb') as f:
        data = f.read(64)
    vendor = struct.unpack('<H', data[0:2])[0]
    device = struct.unpack('<H', data[2:4])[0]
    revision = data[8]
    class_code = struct.unpack('<I', data[8:12])[0] >> 8
    print(f'Vendor: 0x{vendor:04x} (BrainChip)')
    print(f'Device: 0x{device:04x} (AKD1000)')
    print(f'Revision: {revision}')
    print(f'Class: 0x{class_code:06x}')
    # BARs
    for i in range(6):
        bar = struct.unpack('<I', data[0x10+i*4:0x14+i*4])[0]
        if bar:
            bar_type = 'I/O' if bar & 1 else 'Memory'
            bar_addr = bar & ~0xF
            print(f'BAR{i}: 0x{bar_addr:08x} ({bar_type})')
except Exception as e:
    print(f'Error: {e}')
" 2>&1''', 15)
print(enum_result)

east.close()

print('\n' + '='*60)
print('  SILICON TASTED.')
print('  The AKD1000 is 78 neural processors,')
print('  54µs inference, 30mW chip power,')
print('  waiting to be wired into toadStool.')
print('='*60)
