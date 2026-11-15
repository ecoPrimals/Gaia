"""ALL SOLVES — Diagnose why iGPU is busted + prep every fix path."""
import subprocess, json, os, urllib.request, base64

print("=" * 70)
print("ALL SOLVES — Why is the left eye busted? Every path at once.")
print("=" * 70)

diagnosis = {}

# ─── 1: CSM STATUS — This is likely the root cause! ───
print("\n[1] CSM (Compatibility Support Module) — THE SUSPECT...")
cmd_csm = r'''
$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement

# Check CSM-related settings
$settings = @("CsmSupport", "Launch CSM", "CSM Support", "BootMode", 
              "SecureBoot", "OpROM", "Launch PXE", "Network Stack",
              "IntegratedGraphics", "PrimaryVideo", "UmaFrameBufferSize",
              "IGDMultiMonitor", "iGPU Multi-Monitor", "NbConfiguration",
              "ResizeBar", "ReBar", "Above4GDecoding", "Above 4G Decoding",
              "Iommu", "IOMMU", "SVM Mode")

foreach ($s in $settings) {
    try {
        $r = Invoke-CimMethod -InputObject $inst -MethodName "GetOptionData" -Arguments @{OptionName=$s}
        if ($r.ErrorCode -eq 0) {
            Write-Output ("  $s = $($r.Value)")
        }
    } catch {}
}

# Also check Secure Boot state
$sb = Confirm-SecureBootUEFI
Write-Output ("  SecureBootActive = $sb")

# Check boot mode
$fw = bcdedit /enum firmware 2>&1 | Out-String
Write-Output $fw
'''

with open(r'c:\Users\mokke\Desktop\Gaia\scripts\all-solves-csm.ps1', 'w') as f:
    f.write(cmd_csm)

r1 = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File',
                     r'c:\Users\mokke\Desktop\Gaia\scripts\all-solves-csm.ps1'],
                    capture_output=True, text=True, timeout=30)
print(r1.stdout.strip())
diagnosis['csm_check'] = r1.stdout.strip()

# ─── 2: AMD CBS / PBS Settings — The hidden menu ───
print("\n[2] AMD CBS / PBS / NB Configuration settings...")
cmd_amd = r'''
$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement

$amd_settings = @(
    "GfxConfiguration", "iGPUConfiguration", "IGPUConfiguration",
    "IntegratedGraphicsController", "GFXOFF", "dGPUOnlyMode",
    "HybridGraphics", "SpecialDisplayFeatures", "PrimaryVideoAdaptor",
    "D3ColdSupport", "UmaVersion", "GfxUmaFrameBufferSize",
    "NbioCommonOptions", "GraphicsFeatures"
)

foreach ($s in $amd_settings) {
    try {
        $r = Invoke-CimMethod -InputObject $inst -MethodName "GetOptionData" -Arguments @{OptionName=$s}
        if ($r.ErrorCode -eq 0) {
            Write-Output ("  $s = $($r.Value)")
        }
    } catch {}
}
'''

with open(r'c:\Users\mokke\Desktop\Gaia\scripts\all-solves-amd.ps1', 'w') as f:
    f.write(cmd_amd)

r2 = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File',
                     r'c:\Users\mokke\Desktop\Gaia\scripts\all-solves-amd.ps1'],
                    capture_output=True, text=True, timeout=15)
print(r2.stdout.strip())
diagnosis['amd_settings'] = r2.stdout.strip()

# ─── 3: Read the ACTUAL AMD_PBS_SETUP bytes around the key area ───
print("\n[3] AMD_PBS_SETUP deep read — every relevant byte...")
import ctypes, ctypes.wintypes, struct

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

GUID = "{A339D746-F678-49B3-9FC7-54CE0F9DF226}"

# Read AMD_PBS_SETUP
buf = ctypes.create_string_buffer(65536)
attrs = ctypes.wintypes.DWORD(0)
ret = GetVar("AMD_PBS_SETUP", GUID, buf, 65536, ctypes.byref(attrs))
if ret > 0:
    data = bytearray(buf.raw[:ret])
    print(f"  AMD_PBS_SETUP: {ret} bytes, attrs=0x{attrs.value:02X}")
    
    # Known offsets from Framework community + our rosetta work:
    # 0x49 = UMA Frame Buffer Size (FF FF FF FF = Auto)
    # 0x4E = Primary Video (02 = PCIE)
    # Look for Integrated Graphics enable around here
    
    # Print bytes 0x40 - 0x60 (the graphics region)
    print(f"\n  Bytes 0x00-0x0F: {' '.join(f'{data[i]:02X}' for i in range(min(16, ret)))}")
    print(f"  Bytes 0x40-0x5F (GRAPHICS REGION):")
    for row in range(0x40, min(0x60, ret), 16):
        hexs = ' '.join(f'{data[i]:02X}' for i in range(row, min(row+16, ret)))
        print(f"    0x{row:02X}: {hexs}")
    
    # Key bytes
    print(f"\n  KEY BYTES:")
    offsets = {
        0x00: "Byte 0 (config flags?)",
        0x01: "Byte 1",
        0x02: "Byte 2",
        0x48: "Pre-UMA",
        0x49: "UMA Frame Buffer Size",
        0x4A: "UMA +1",
        0x4B: "UMA +2", 
        0x4C: "UMA +3",
        0x4D: "Post-UMA",
        0x4E: "Primary Video",
        0x4F: "Primary Video +1",
        0x50: "iGPU enable?",
        0x51: "iGPU +1",
        0x52: "iGPU +2",
    }
    for off, name in sorted(offsets.items()):
        if off < ret:
            print(f"    [0x{off:02X}] = 0x{data[off]:02X} ({data[off]:3d})  — {name}")
    
    # Search for patterns that look like "enable" flags (0x00, 0x01, 0x02)
    print(f"\n  SEARCHING for iGPU enable flag (looking for 0x00 near UMA that should be 0x01)...")
    for i in range(max(0, 0x40), min(0x60, ret)):
        val = data[i]
        if val in [0x00, 0x01, 0x02, 0x03]:
            print(f"    [0x{i:02X}] = 0x{val:02X}  {'<-- potential enable flag' if val <= 1 else ''}")

    # Also check if there's a "force" value somewhere
    # From ASUS manual: Integrated Graphics = [Disabled] [Force] [Auto]
    # Typical encoding: 0=Disabled, 1=Force, 2=Auto, FF=not set
    
    # Full hex dump for analysis
    print(f"\n  FULL HEX DUMP:")
    for row in range(0, ret, 16):
        hexs = ' '.join(f'{data[row+i]:02X}' if row+i < ret else '  ' for i in range(16))
        ascii_str = ''.join(chr(data[row+i]) if 32 <= data[row+i] < 127 else '.' for i in range(16) if row+i < ret)
        print(f"    0x{row:02X}: {hexs}  {ascii_str}")
    
    diagnosis['amd_pbs_setup'] = data.hex()

# Also read Setup variable
buf2 = ctypes.create_string_buffer(65536)
attrs2 = ctypes.wintypes.DWORD(0)
SETUP_GUID = "{EC87D643-EBA4-4BB5-A1E5-3F3E36B20DA9}"
ret2 = GetVar("Setup", SETUP_GUID, buf2, 65536, ctypes.byref(attrs2))
if ret2 > 0:
    sdata = bytearray(buf2.raw[:ret2])
    print(f"\n  Setup variable: {ret2} bytes")
    # CSM is often at a known offset in the Setup variable
    # Search for CSM-related bytes
    print(f"  Setup bytes around CSM area (0xE0-0xFF):")
    for row in range(0xE0, min(0x100, ret2), 16):
        hexs = ' '.join(f'{sdata[i]:02X}' for i in range(row, min(row+16, ret2)))
        print(f"    0x{row:02X}: {hexs}")

# ─── 4: Check what solutions are ready ───
print("\n" + "=" * 70)
print("[4] SOLUTION STATUS")
print("=" * 70)

# modGRUBShell
if os.path.exists(r'Z:\EFI\tools\modGRUBShell.efi'):
    size = os.path.getsize(r'Z:\EFI\tools\modGRUBShell.efi')
    print(f"  [A] modGRUBShell.efi: READY on EFI partition ({size/1024/1024:.1f}MB)")
    print(f"      Boot entry: 'GAIA EFI Key - UMA Unlock'")
    print(f"      Command: setup_var_cv AMD_PBS_SETUP 0x49 0x06")
else:
    print(f"  [A] modGRUBShell.efi: NOT FOUND")

# Smokeless_UMAF
print(f"  [B] Smokeless_UMAF: Need to download from GitHub")
print(f"      https://github.com/DavidS95/Smokeless_UMAF/")
print(f"      Extract to FAT32 USB → boot → Device Manager → AMD CBS")

# CMOS clear
print(f"  [C] CMOS Clear: Hardware jumper on motherboard")
print(f"      → NB Configuration menu appears → set iGPU + UMA")
print(f"      → ALSO disable CSM!")

# Rust UEFI app
print(f"  [D] Rust UEFI app (viva-uefi): Can build sovereign tool")
print(f"      → Writes AMD_PBS_SETUP[0x49]=0x06 at boot time")

# ─── 5: THE DIAGNOSIS ───
print(f"\n" + "=" * 70)
print("DIAGNOSIS — Why is the left eye busted?")
print("=" * 70)

# Save
outpath = r'c:\Users\mokke\Desktop\Gaia\data\uefi-sniffs\all-solves-diagnosis.json'
with open(outpath, 'w') as f:
    json.dump(diagnosis, f, indent=2)
print(f"\nSaved to: {outpath}")
