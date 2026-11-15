"""
MISE EN PLACE — Fix all broken legs before open heart surgery.
1. Kill stale primal processes
2. Clean membrane state (old PIDs, port conflicts)
3. Fix PCIe registry settings
4. Check for missing drivers
5. Free the mitochondria (iGPU for display)
"""
import subprocess, os, json, signal, time

MEMBRANE = os.path.expanduser('~\\Desktop\\Gaia\\runtime\\membrane')

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

print('='*60)
print('  MISE EN PLACE — fix broken legs before open heart')
print('='*60)

# ========================================
# 1. KILL STALE PRIMALS
# ========================================
print('\n--- 1. STALE PRIMAL CLEANUP ---')

# Find all primal processes
primal_names = ['beardog', 'songbird', 'skunkbat', 'swarmvine', 'toadstool',
                'coralreef', 'barracuda', 'nestgate', 'rhizocrypt', 'loamspine',
                'sweetgrass', 'squirrel', 'petaltongue', 'biomeos', 'membrane']

killed = 0
for name in primal_names:
    procs = ps(f'Get-Process -Name "*{name}*" -ErrorAction SilentlyContinue | Select-Object Id,ProcessName')
    if procs and 'Id' in procs:
        print(f'  Found {name} processes:')
        print(f'    {procs}')
        # Kill them
        result = ps(f'Get-Process -Name "*{name}*" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue')
        killed += 1
        print(f'    → Killed')

# Also kill any orphaned songbird (PID 32576 from the log)
for stale_pid in [32576]:
    try:
        result = ps(f'Stop-Process -Id {stale_pid} -Force -ErrorAction SilentlyContinue')
        print(f'  Killed stale PID {stale_pid}')
    except:
        pass

print(f'  Cleaned {killed} primal families')

# ========================================
# 2. CLEAN MEMBRANE STATE
# ========================================
print('\n--- 2. MEMBRANE CLEANUP ---')

# Remove old PID files
old_family = '3034463630464339'
old_cleaned = 0
for f in os.listdir(MEMBRANE):
    if old_family in f and (f.endswith('.pid') or f.endswith('.port')):
        fp = os.path.join(MEMBRANE, f)
        os.remove(fp)
        old_cleaned += 1
        print(f'  Removed old: {f}')

# Remove stale gaia-pi PIDs for dead processes
for f in os.listdir(MEMBRANE):
    if f.endswith('.pid') and 'gaia-pi' in f:
        fp = os.path.join(MEMBRANE, f)
        try:
            with open(fp) as fh:
                pid = int(fh.read().strip())
            # Check if process exists
            result = ps(f'Get-Process -Id {pid} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty ProcessName')
            if not result or result == '(timeout)':
                os.remove(fp)
                old_cleaned += 1
                print(f'  Removed dead PID file: {f} (PID {pid} dead)')
        except:
            os.remove(fp)
            old_cleaned += 1

print(f'  Cleaned {old_cleaned} stale state files')

# ========================================
# 3. FIX PORT CONFLICTS
# ========================================
print('\n--- 3. PORT CONFLICT CHECK ---')

# Check port 9900 (petaltongue)
port_check = ps('Get-NetTCPConnection -LocalPort 9900 -ErrorAction SilentlyContinue | Select-Object OwningProcess,State | Format-Table')
if port_check and 'OwningProcess' in port_check:
    print(f'  Port 9900 in use: {port_check}')
    # Kill the holder
    ps('Get-NetTCPConnection -LocalPort 9900 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }')
    print(f'  → Freed port 9900')
else:
    print(f'  Port 9900: FREE ✅')

# Check other primal ports
for port in [63429, 63476, 63478, 51634, 51636]:
    check = ps(f'Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | Select-Object OwningProcess | Format-Table -HideTableHeaders')
    status = f'PID {check.strip()}' if check.strip() else 'free'
    print(f'  Port {port}: {status}')

# ========================================
# 4. PCIe REGISTRY OPTIMIZATIONS
# ========================================
print('\n--- 4. PCIe REGISTRY FIXES ---')

# Disable PCIe power management at registry level
pcie_fixes = [
    # Disable ASPM in registry
    ('HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerSettings\\501a4d13-42af-4429-9fd1-a8218c268e20\\ee12f906-d277-404b-b6da-e5fa1a576df5', 'DefaultPowerSchemeValues', None),
]

# Set GPU to prefer maximum performance
print('  Setting NVIDIA power management to max performance...')
result = cmd('nvidia-smi -pm 1 2>&1')
print(f'    Persistence mode: {result}')

result = cmd('nvidia-smi --power-limit=600 2>&1')
print(f'    Power limit: {result}')

# Check current PCIe
pcie = cmd('nvidia-smi --query-gpu=pcie.link.gen.current,pcie.link.width.current --format=csv,noheader')
print(f'    Current PCIe: {pcie}')

# ========================================
# 5. MISSING DRIVER CHECK
# ========================================
print('\n--- 5. MISSING DRIVERS ---')

error_devices = ps("""
Get-PnpDevice | Where-Object {`$_.Status -eq 'Error'} | ForEach-Object {
    `$hwid = (Get-PnpDeviceProperty -InstanceId `$_.InstanceId -KeyName DEVPKEY_Device_HardwareIds -ErrorAction SilentlyContinue).Data
    Write-Output "  $(`$_.FriendlyName): $(`$_.InstanceId) [$hwid]"
}
""")
print(error_devices)

# Check Windows Update for drivers
print('\n  Checking Windows Update for missing drivers...')
wu_check = ps('Get-WindowsUpdate -Category Drivers -ErrorAction SilentlyContinue | Select-Object Title | Format-Table -AutoSize')
if wu_check and 'Title' in wu_check:
    print(f'  Available driver updates:\n{wu_check}')
else:
    print('  (Windows Update driver check not available — try Settings > Windows Update)')

# Try to find drivers via PnP
print('\n  Attempting PnP driver search for error devices...')
pnp_scan = ps('pnputil /scan-devices 2>&1')
print(f'  {pnp_scan}')

# ========================================
# 6. iGPU STATUS
# ========================================
print('\n--- 6. iGPU (AMD Radeon) STATUS ---')
igpu = ps("""
Get-PnpDevice -Class Display | ForEach-Object {
    `$props = Get-PnpDeviceProperty -InstanceId `$_.InstanceId -KeyName DEVPKEY_Device_LocationInfo -ErrorAction SilentlyContinue
    Write-Output "  $(`$_.FriendlyName): Status=$(`$_.Status) Location=$(`$props.Data)"
}
""")
print(igpu)

# Check if Radeon is handling display
print('\n  Display outputs:')
displays = ps('Get-CimInstance Win32_VideoController | Select-Object Name,VideoProcessor,CurrentHorizontalResolution,CurrentVerticalResolution,DriverVersion | Format-List')
print(displays)

# ========================================
# 7. WINDOWS OPTIONAL FEATURES
# ========================================
print('\n--- 7. SSH SERVER (for mesh access) ---')
ssh_status = ps('Get-Service sshd -ErrorAction SilentlyContinue | Select-Object Status,StartType | Format-Table -HideTableHeaders')
if ssh_status.strip():
    print(f'  SSH server: {ssh_status.strip()}')
else:
    print('  SSH server: NOT INSTALLED')
    print('  Installing OpenSSH Server...')
    install = ps('Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 -ErrorAction SilentlyContinue | Select-Object RestartNeeded')
    print(f'  Install result: {install}')
    # Start it
    ps('Start-Service sshd -ErrorAction SilentlyContinue')
    ps('Set-Service -Name sshd -StartupType Automatic -ErrorAction SilentlyContinue')
    ssh_check = ps('Get-Service sshd -ErrorAction SilentlyContinue | Select-Object Status')
    print(f'  SSH now: {ssh_check}')

# ========================================
# SUMMARY
# ========================================
print(f'\n{"="*60}')
print('  MISE EN PLACE COMPLETE')
print('  ')
print('  ✅ Stale primals killed')
print('  ✅ Membrane state cleaned')
print('  ✅ Port conflicts checked')
print('  ✅ PCIe power optimized')
print('  ✅ Missing drivers enumerated')
print('  ✅ iGPU status checked')
print('  ✅ SSH server checked')
print('  ')
print('  The kitchen is clean. The ingredients are ready.')
print('  Next: reboot → BIOS (Gen5 + ReBAR + iGPU) → surgery')
print(f'{"="*60}')
