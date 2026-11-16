"""THREE REBOOTS — Budget 3 reboots to open the left eye.
Reboot 1: modGRUBShell (CSM disable + UMA set)
Reboot 2: Smokeless_UMAF fallback
Reboot 3: Kevin flips the switch manually
Also: find CSM offset in Setup variable for modGRUBShell."""
import ctypes, ctypes.wintypes, struct, subprocess, json, os

print("=" * 70)
print("THREE REBOOTS — Left eye surgery plan")
print("=" * 70)

# ─── PRIVILEGE ───
kernel32 = ctypes.windll.kernel32
advapi32 = ctypes.windll.advapi32
kernel32.GetCurrentProcess.restype = ctypes.wintypes.HANDLE
advapi32.OpenProcessToken.argtypes = [ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD, ctypes.POINTER(ctypes.wintypes.HANDLE)]
advapi32.OpenProcessToken.restype = ctypes.wintypes.BOOL
token = ctypes.wintypes.HANDLE()
advapi32.OpenProcessToken(kernel32.GetCurrentProcess(), 0x0028, ctypes.byref(token))
class LUID(ctypes.Structure):
    _fields_ = [("L", ctypes.wintypes.DWORD), ("H", ctypes.wintypes.LONG)]
class LA(ctypes.Structure):
    _fields_ = [("Luid", LUID), ("Attr", ctypes.wintypes.DWORD)]
class TP(ctypes.Structure):
    _fields_ = [("Count", ctypes.wintypes.DWORD), ("Privs", LA * 1)]
luid = LUID()
advapi32.LookupPrivilegeValueW(None, "SeSystemEnvironmentPrivilege", ctypes.byref(luid))
tp = TP(); tp.Count = 1; tp.Privs[0].Luid = luid; tp.Privs[0].Attr = 2
advapi32.AdjustTokenPrivileges(token, False, ctypes.byref(tp), 0, None, None)

GetVar = kernel32.GetFirmwareEnvironmentVariableExW
GetVar.restype = ctypes.wintypes.DWORD
GetVar.argtypes = [ctypes.wintypes.LPCWSTR, ctypes.wintypes.LPCWSTR,
                   ctypes.c_void_p, ctypes.wintypes.DWORD, ctypes.POINTER(ctypes.wintypes.DWORD)]

# ─── 1: Find CSM offset in Setup variable ───
print("\n[1] Hunting CSM offset in Setup variable...")

SETUP_GUID = "{EC87D643-EBA4-4BB5-A1E5-3F3E36B20DA9}"
buf = ctypes.create_string_buffer(65536)
attrs = ctypes.wintypes.DWORD(0)
ret = GetVar("Setup", SETUP_GUID, buf, 65536, ctypes.byref(attrs))

if ret > 0:
    setup = bytearray(buf.raw[:ret])
    print(f"  Setup variable: {ret} bytes, attrs=0x{attrs.value:02X}")
    
    # CSM is typically a single byte: 0=Disabled, 1=Enabled
    # WMI says CsmSupport=1, so we need to find offset with value 0x01
    # In the Setup hex dump from earlier, 0xE0 area had: 01 01 01 10 02 00 FF FF FF FF
    
    # Search for CSM: it's often near other boot config flags
    # Let's check specific ASUS-known offsets
    print(f"\n  Setup hex dump (searching for CSM=0x01):")
    for row in range(0, ret, 16):
        hexs = ' '.join(f'{setup[i]:02X}' for i in range(row, min(row+16, ret)))
        print(f"    0x{row:02X}: {hexs}")
    
    # Cross-reference with WMI known values
    # CsmSupport=1, PrimaryVideo=2, UmaFrameBufferSize=0xFFFFFFFF
    # Look for 0x01 bytes that when changed to 0x00 would disable CSM
    
    # Known ASUS X870E Setup offsets (from community IFR extraction):
    # CSM is usually in the 0xE0-0xFF range for AMI BIOS
    csm_candidates = []
    for i in range(ret):
        if setup[i] == 0x01:
            csm_candidates.append(i)
    
    print(f"\n  Offsets with value 0x01 (CSM candidates): {len(csm_candidates)} found")
    for off in csm_candidates:
        # Show context around each one
        ctx = ' '.join(f'{setup[max(0,off-2)+j]:02X}' for j in range(5) if max(0,off-2)+j < ret)
        print(f"    [0x{off:02X}] = 0x01  context: {ctx}")

# ─── 2: Also read AMD_PBS_SETUP for complete map ───
print("\n[2] AMD_PBS_SETUP graphics region...")
PBS_GUID = "{A339D746-F678-49B3-9FC7-54CE0F9DF226}"
buf2 = ctypes.create_string_buffer(65536)
attrs2 = ctypes.wintypes.DWORD(0)
ret2 = GetVar("AMD_PBS_SETUP", PBS_GUID, buf2, 65536, ctypes.byref(attrs2))

if ret2 > 0:
    pbs = bytearray(buf2.raw[:ret2])
    print(f"  Bytes 0x46-0x52:")
    for i in range(0x46, min(0x53, ret2)):
        print(f"    [0x{i:02X}] = 0x{pbs[i]:02X}")

# ─── 3: Try WMI CSM disable (probably Error 26 but TRY) ───
print("\n[3] Attempting WMI CSM disable...")
cmd_csm = '''
$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement
$r = Invoke-CimMethod -InputObject $inst -MethodName "SetOptionData" -Arguments @{OptionName="CsmSupport"; Value=[uint32]0}
Write-Output "CsmSupport disable: Error=$($r.ErrorCode)"

# Also try alternate names
$names = @("Launch CSM", "CSM Support", "CsmSupport", "CSM")
foreach ($n in $names) {
    try {
        $r2 = Invoke-CimMethod -InputObject $inst -MethodName "SetOptionData" -Arguments @{OptionName=$n; Value=[uint32]0}
        Write-Output "$n disable: Error=$($r2.ErrorCode)"
    } catch {}
}
'''

with open(r'c:\Users\mokke\Desktop\Gaia\scripts\try-csm-disable.ps1', 'w') as f:
    f.write(cmd_csm)

r3 = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File',
                     r'c:\Users\mokke\Desktop\Gaia\scripts\try-csm-disable.ps1'],
                    capture_output=True, text=True, timeout=15)
print(r3.stdout.strip())

# ─── 4: Build the modGRUBShell command list ───
print("\n" + "=" * 70)
print("REBOOT PLAN")
print("=" * 70)

print("""
╔══════════════════════════════════════════════════════╗
║  REBOOT 1: modGRUBShell (automatic, no DEL key)     ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  1. Restart Windows                                  ║
║  2. At boot menu, select:                            ║
║     "GAIA EFI Key - UMA Unlock"                      ║
║                                                      ║
║  3. In GRUB shell, type these commands:              ║
║                                                      ║
║     setup_var_cv AMD_PBS_SETUP 0x49 0x06             ║
║     (Set UMA = 512MB)                                ║
║                                                      ║
║     setup_var_cv AMD_PBS_SETUP 0x48 0x01             ║
║     (Set Integrated Graphics = Force)                ║
║                                                      ║
║     reboot                                           ║
║                                                      ║
║  4. Let Windows boot normally                        ║
║  5. Check if left eye opens                          ║
║                                                      ║
║  NOTE: CSM needs separate offset in Setup variable   ║
║  modGRUBShell can write it too if we find the offset ║
╚══════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════╗
║  REBOOT 2: If #1 didn't work — Smokeless_UMAF       ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  1. Download Smokeless_UMAF to FAT32 USB             ║
║  2. Boot from USB                                    ║
║  3. Device Manager > AMD CBS > NBIO Common Options   ║
║  4. GFX Configuration > iGPU = UMA Specified         ║
║  5. UMA Frame Buffer Size = 512M                     ║
║  6. Save & Reboot                                    ║
╚══════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════╗
║  REBOOT 3: Kevin flips the switch (manual BIOS)      ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  1. Reboot, press DEL for BIOS                       ║
║  2. Advanced > Boot > CSM > DISABLED                 ║
║  3. If NB Configuration appears:                     ║
║     Integrated Graphics = Force                      ║
║     UMA Frame Buffer Size = 512M                     ║
║  4. If NB Configuration still hidden:                ║
║     Save & Exit, Clear CMOS, re-enter BIOS           ║
║  5. Save & Exit                                      ║
╚══════════════════════════════════════════════════════╝
""")

# ─── 5: Create post-reboot verification script ───
verify_script = r'''
"""POST-REBOOT VERIFY — Check if left eye opened."""
import subprocess, socket

print("=" * 50)
print("POST-REBOOT — Did the left eye open?")
print("=" * 50)

# Check UMA
cmd = 'powershell -Command "$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement; $r = Invoke-CimMethod -InputObject $inst -MethodName GetOptionData -Arguments @{OptionName=\'UmaFrameBufferSize\'}; Write-Output $r.Value"'
import os
r = os.popen(cmd).read().strip()
uma = int(r) if r.isdigit() else -1
if uma == 4294967295:
    print("  UMA: STILL 0xFFFFFFFF (not set) :(")
elif uma > 0:
    print(f"  UMA: {uma} ({uma/1024/1024:.0f}MB) — SET!")
else:
    print(f"  UMA: {r}")

# Check CSM
cmd2 = 'powershell -Command "$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement; $r = Invoke-CimMethod -InputObject $inst -MethodName GetOptionData -Arguments @{OptionName=\'CsmSupport\'}; Write-Output $r.Value"'
csm = os.popen(cmd2).read().strip()
print(f"  CSM: {csm} ({'ENABLED (bad)' if csm == '1' else 'DISABLED (good!)'})")

# Check AMD GPU
cmd3 = 'powershell -Command "Get-PnpDevice -Class Display | Format-Table FriendlyName,Status -AutoSize"'
gpus = os.popen(cmd3).read()
print(f"\n  GPUs:\n{gpus}")

# Check monitors
cmd4 = 'powershell -Command "Get-PnpDevice -Class Monitor | Format-Table FriendlyName,Status -AutoSize"'
mons = os.popen(cmd4).read()
print(f"  Monitors:\n{mons}")

print("=" * 50)
if uma != 4294967295 and csm != '1':
    print("LEFT EYE SHOULD BE OPEN! Check Display 2!")
else:
    print("Left eye still blocked. Next reboot.")
print("=" * 50)
'''

with open(r'c:\Users\mokke\Desktop\Gaia\scripts\post-reboot-verify.py', 'w') as f:
    f.write(verify_script)

# ─── 6: Save plan ───
plan = {
    "reboot_budget": 3,
    "reboots": [
        {"id": 1, "method": "modGRUBShell", "commands": [
            "setup_var_cv AMD_PBS_SETUP 0x49 0x06",
            "setup_var_cv AMD_PBS_SETUP 0x48 0x01",
            "reboot"
        ]},
        {"id": 2, "method": "Smokeless_UMAF", "steps": "FAT32 USB boot > AMD CBS > UMA"},
        {"id": 3, "method": "manual_bios", "steps": "DEL > CSM OFF > NB Config > iGPU Force > UMA 512M"}
    ],
    "verify": "python scripts/post-reboot-verify.py",
    "csm_current": 1,
    "uma_current": "0xFFFFFFFF"
}

with open(r'c:\Users\mokke\Desktop\Gaia\data\uefi-sniffs\reboot-plan.json', 'w') as f:
    json.dump(plan, f, indent=2)

print(f"\nPlan saved to data/uefi-sniffs/reboot-plan.json")
print(f"Post-reboot verify: python scripts/post-reboot-verify.py")
