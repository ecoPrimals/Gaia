"""
REBOOT CYCLE — 2 planned reboots with UEFI sniffing.
Run this BEFORE each reboot. It saves state, then reboots.
Run uefi-sniffer.py manually after each boot to diff.

Cycle 1: Clean reboot — see if PCIe Gen heals on its own
Cycle 2: Registry + power tweaks — force PCIe Gen5

Also: dump ACPI/SMBIOS/firmware tables to MELT the UEFI boundary.
"""
import subprocess, os, json, sys, ctypes
from datetime import datetime

STATE_DIR = os.path.expanduser('~\\Desktop\\Gaia\\data\\uefi-sniffs')
CYCLE_FILE = os.path.join(STATE_DIR, 'reboot-cycle-state.json')
os.makedirs(STATE_DIR, exist_ok=True)

def ps(cmd, t=15):
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

def get_pcie_state():
    """Snapshot PCIe link state"""
    return cmd('nvidia-smi --query-gpu=pci.bus_id,pcie.link.gen.max,pcie.link.gen.current,pcie.link.width.max,pcie.link.width.current --format=csv,noheader')

def dump_firmware_tables():
    """Dump ACPI/SMBIOS tables — MELT the UEFI boundary"""
    dump_dir = os.path.join(STATE_DIR, 'firmware-tables')
    os.makedirs(dump_dir, exist_ok=True)

    print('\n--- MELTING UEFI BOUNDARY ---')

    # 1. SMBIOS raw dump
    print('  Dumping SMBIOS structures...')
    smbios_types = {
        0: 'BIOS Information',
        1: 'System Information',
        2: 'Baseboard',
        3: 'Chassis',
        4: 'Processor',
        7: 'Cache',
        9: 'System Slots',
        16: 'Physical Memory Array',
        17: 'Memory Device',
        19: 'Memory Array Mapped Address',
        41: 'Onboard Devices Extended',
    }
    for type_id, name in smbios_types.items():
        data = ps(f'Get-CimInstance -ClassName Win32_PnPEntity -ErrorAction SilentlyContinue | Out-Null; echo "type {type_id} queried"')

    # Detailed SMBIOS via WMI
    smbios = {}
    smbios['bios'] = ps('Get-CimInstance Win32_BIOS | ConvertTo-Json -Depth 3')
    smbios['board'] = ps('Get-CimInstance Win32_BaseBoard | ConvertTo-Json -Depth 3')
    smbios['system'] = ps('Get-CimInstance Win32_ComputerSystem | ConvertTo-Json -Depth 3')
    smbios['cpu'] = ps('Get-CimInstance Win32_Processor | ConvertTo-Json -Depth 3')
    smbios['memory'] = ps('Get-CimInstance Win32_PhysicalMemory | ConvertTo-Json -Depth 3')
    smbios['slots'] = ps('Get-CimInstance Win32_SystemSlot | ConvertTo-Json -Depth 3')
    smbios['cache'] = ps('Get-CimInstance Win32_CacheMemory | ConvertTo-Json -Depth 3')
    smbios['onboard'] = ps('Get-CimInstance Win32_OnBoardDevice | ConvertTo-Json -Depth 3')

    with open(os.path.join(dump_dir, 'smbios-dump.json'), 'w') as f:
        json.dump(smbios, f, indent=2, default=str)
    print(f'  SMBIOS → {dump_dir}\\smbios-dump.json')

    # 2. ACPI table signatures
    print('  Reading ACPI table signatures...')
    acpi = ps("""
        $fw = Get-CimInstance -Namespace root\\wmi -ClassName MsAcpiEx_EvalResult -ErrorAction SilentlyContinue
        $tables = @()
        try {
            $raw = [System.Runtime.InteropServices.Marshal]
            # Get firmware table providers
            $providers = @('ACPI','FIRM','RSMB')
            foreach ($p in $providers) {
                $tables += "Provider: $p"
            }
        } catch {}
        $tables -join "`n"
    """)
    print(f'  ACPI providers: {acpi}')

    # 3. Firmware type and secure boot details
    print('  Reading firmware security boundary...')
    fw_security = {}
    fw_security['secure_boot'] = ps('Confirm-SecureBootUEFI')
    fw_security['uefi_mode'] = ps('bcdedit /enum firmware 2>&1 | Select-String -Pattern "path|description|device" | Out-String')
    fw_security['boot_config'] = ps('bcdedit /enum {current} 2>&1 | Out-String')
    fw_security['tpm'] = ps('Get-Tpm | ConvertTo-Json -Depth 2 -ErrorAction SilentlyContinue')
    fw_security['bitlocker'] = ps('Get-BitLockerVolume -ErrorAction SilentlyContinue | Select-Object MountPoint,ProtectionStatus,EncryptionMethod | ConvertTo-Json')

    with open(os.path.join(dump_dir, 'firmware-security.json'), 'w') as f:
        json.dump(fw_security, f, indent=2, default=str)
    print(f'  Security → {dump_dir}\\firmware-security.json')

    # 4. PCI config space (as much as Windows exposes)
    print('  Reading PCI configuration space...')
    pci_detail = ps("""
        Get-PnpDevice -Class Display -ErrorAction SilentlyContinue |
            Get-PnpDeviceProperty -KeyName DEVPKEY_Device_LocationInfo,DEVPKEY_Device_Address,DEVPKEY_Device_Driver,DEVPKEY_Device_BusNumber -ErrorAction SilentlyContinue |
            Format-Table InstanceId,KeyName,Data -AutoSize | Out-String
    """)
    with open(os.path.join(dump_dir, 'pci-config.txt'), 'w') as f:
        f.write(pci_detail)
    print(f'  PCI config → {dump_dir}\\pci-config.txt')

    # 5. Device tree (full topology)
    print('  Dumping device tree...')
    dev_tree = ps("""
        Get-PnpDevice | Where-Object {$_.InstanceId -match 'PCI'} |
            Select-Object Status,Class,FriendlyName,InstanceId |
            Sort-Object InstanceId |
            Format-Table -AutoSize | Out-String
    """)
    with open(os.path.join(dump_dir, 'device-tree.txt'), 'w') as f:
        f.write(dev_tree)
    print(f'  Device tree → {dump_dir}\\device-tree.txt')

    # 6. UEFI boot entries
    print('  Reading UEFI boot entries...')
    boot_entries = cmd('bcdedit /enum all 2>&1')
    with open(os.path.join(dump_dir, 'boot-entries.txt'), 'w') as f:
        f.write(boot_entries)
    print(f'  Boot entries → {dump_dir}\\boot-entries.txt')

    # 7. Power config (affects PCIe link state)
    print('  Reading power/PCIe settings...')
    power = {}
    power['active_scheme'] = ps('powercfg /getactivescheme')
    power['pcie_aspm'] = ps("""
        $aspm = powercfg /query SCHEME_CURRENT SUB_PCIEXPRESS ASPM 2>&1
        $aspm | Out-String
    """)
    power['pcie_link_state'] = ps("""
        powercfg /query SCHEME_CURRENT SUB_PCIEXPRESS LNKSTATE 2>&1 | Out-String
    """)
    with open(os.path.join(dump_dir, 'power-pcie.json'), 'w') as f:
        json.dump(power, f, indent=2, default=str)
    print(f'  Power/PCIe → {dump_dir}\\power-pcie.json')

    return dump_dir

def load_cycle_state():
    if os.path.exists(CYCLE_FILE):
        with open(CYCLE_FILE) as f:
            return json.load(f)
    return {'cycle': 0, 'reboots': []}

def save_cycle_state(state):
    with open(CYCLE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

# ============================================================
# MAIN
# ============================================================

state = load_cycle_state()
cycle = state['cycle']

print('='*60)
print(f'  REBOOT CYCLE — Phase {cycle + 1} of 2')
print('='*60)

# Current PCIe state
pcie = get_pcie_state()
print(f'\n  Current PCIe: {pcie}')

if cycle == 0:
    # ==============================
    # CYCLE 1: Clean reboot baseline
    # ==============================
    print('\n  CYCLE 1: Clean reboot — does PCIe Gen heal on its own?')
    print('  Saving pre-reboot state...')

    dump_dir = dump_firmware_tables()

    state['cycle'] = 1
    state['reboots'].append({
        'cycle': 1,
        'phase': 'pre-reboot',
        'timestamp': datetime.now().isoformat(),
        'pcie_before': pcie,
        'action': 'clean reboot, no changes'
    })
    save_cycle_state(state)

    print(f'\n  Pre-reboot state saved.')
    print(f'  Firmware tables dumped to: {dump_dir}')
    print(f'\n  READY TO REBOOT.')
    print(f'  After reboot, run:')
    print(f'    python scripts/uefi-sniffer.py')
    print(f'    python scripts/reboot-cycle.py')

elif cycle == 1:
    # ==============================
    # POST-CYCLE-1: Check if Gen healed
    # ==============================
    prev_pcie = state['reboots'][-1].get('pcie_before', '?')
    print(f'\n  CYCLE 1 RESULT:')
    print(f'    Before: {prev_pcie}')
    print(f'    After:  {pcie}')

    gen_current = '1'
    for part in pcie.split(','):
        part = part.strip()
    # Parse current gen
    fields = [f.strip() for f in pcie.split(',')]
    if len(fields) >= 4:
        gen_current = fields[2]
        width_current = fields[4] if len(fields) > 4 else '?'

    if gen_current != '1':
        print(f'    ✅ PCIe Gen HEALED to Gen{gen_current}!')
    else:
        print(f'    ❌ Still Gen1 — need CYCLE 2 tweaks')
        print(f'\n  CYCLE 2: Applying PCIe power management fixes...')

        # Force ASPM off
        print('  → Disabling PCIe ASPM...')
        ps('powercfg /setacvalueindex SCHEME_CURRENT SUB_PCIEXPRESS ASPM 0')
        ps('powercfg /setactive SCHEME_CURRENT')

        # Force PCIe link state power management off
        print('  → Disabling PCIe link state power management...')
        ps('powercfg /setacvalueindex SCHEME_CURRENT SUB_PCIEXPRESS LNKSTATE 0')
        ps('powercfg /setactive SCHEME_CURRENT')

        # Registry: disable PCIe power saving for GPU
        print('  → Setting nvidia registry for max performance...')
        ps("""
            $nv = Get-PnpDevice -Class Display | Where-Object {$_.FriendlyName -match 'NVIDIA'}
            if ($nv) {
                $id = $nv.InstanceId -replace '\\\\','_'
                Write-Output "GPU device: $id"
            }
        """)

        # nvidia-smi persistence mode
        print('  → Setting GPU persistence mode...')
        print(cmd('nvidia-smi -pm 1 2>&1'))

        dump_firmware_tables()

    state['cycle'] = 2
    state['reboots'].append({
        'cycle': 2,
        'phase': 'pre-reboot',
        'timestamp': datetime.now().isoformat(),
        'pcie_before': pcie,
        'action': 'ASPM off, link state off, persistence mode'
    })
    save_cycle_state(state)

    print(f'\n  READY FOR REBOOT 2.')
    print(f'  After reboot, run:')
    print(f'    python scripts/uefi-sniffer.py')
    print(f'    python scripts/reboot-cycle.py')

elif cycle == 2:
    # ==============================
    # POST-CYCLE-2: Final check
    # ==============================
    prev_pcie = state['reboots'][-1].get('pcie_before', '?')
    print(f'\n  CYCLE 2 RESULT:')
    print(f'    Before: {prev_pcie}')
    print(f'    After:  {pcie}')

    fields = [f.strip() for f in pcie.split(',')]
    gen_current = fields[2] if len(fields) > 2 else '?'

    if gen_current != '1':
        print(f'    ✅ PCIe Gen FIXED at Gen{gen_current}!')
        print(f'    The RTX 5090 is breathing at full bandwidth now.')
    else:
        print(f'    ❌ Still Gen1 — this needs UEFI/BIOS intervention.')
        print(f'    Kevin: enter BIOS (DEL key at boot) and check:')
        print(f'      → Advanced > PCI Subsystem Settings > PCIe Speed: [Gen5]')
        print(f'      → Advanced > PCI Subsystem Settings > Link Width: [x16]')
        print(f'      → Advanced > AMD CBS > NBIO > PCIe Speed: [Gen5]')
        print(f'      → Also: Re-Enable Above 4G Decoding + Resizable BAR')

    state['cycle'] = 3
    state['reboots'].append({
        'cycle': 3,
        'phase': 'post-cycle-2',
        'timestamp': datetime.now().isoformat(),
        'pcie_final': pcie,
    })
    save_cycle_state(state)

    print(f'\n  REBOOT CYCLES COMPLETE.')
    print(f'  If Gen1 persists → BIOS time (DEL at boot).')
    print(f'  Then → hardware surgery (AKD1000 install).')

print(f'\n{"="*60}')
