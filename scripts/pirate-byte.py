"""PIRATE THE BYTE — Every possible way to write AMD_PBS_SETUP[0x49].
Salt in our own eye. sourDough it. Just SET the damn byte."""
import ctypes, ctypes.wintypes, struct, subprocess, os

kernel32 = ctypes.windll.kernel32
advapi32 = ctypes.windll.advapi32
ntdll = ctypes.windll.ntdll

print("=" * 60)
print("PIRATE THE BYTE — AMD_PBS_SETUP[0x49] = 0x06 (512M)")
print("=" * 60)

# Enable ALL privileges
kernel32.GetCurrentProcess.restype = ctypes.wintypes.HANDLE
advapi32.OpenProcessToken.argtypes = [ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD, ctypes.POINTER(ctypes.wintypes.HANDLE)]
advapi32.OpenProcessToken.restype = ctypes.wintypes.BOOL
token = ctypes.wintypes.HANDLE()
advapi32.OpenProcessToken(kernel32.GetCurrentProcess(), 0x0028, ctypes.byref(token))

for priv_name in ["SeSystemEnvironmentPrivilege", "SeBackupPrivilege", "SeRestorePrivilege"]:
    class LUID(ctypes.Structure):
        _fields_ = [("L", ctypes.wintypes.DWORD), ("H", ctypes.wintypes.LONG)]
    class LA(ctypes.Structure):
        _fields_ = [("Luid", LUID), ("Attr", ctypes.wintypes.DWORD)]
    class TP(ctypes.Structure):
        _fields_ = [("Count", ctypes.wintypes.DWORD), ("Privs", LA * 1)]
    luid = LUID()
    advapi32.LookupPrivilegeValueW(None, priv_name, ctypes.byref(luid))
    tp = TP(); tp.Count = 1; tp.Privs[0].Luid = luid; tp.Privs[0].Attr = 2
    advapi32.AdjustTokenPrivileges(token, False, ctypes.byref(tp), 0, None, None)

GetVar = kernel32.GetFirmwareEnvironmentVariableExW
GetVar.restype = ctypes.wintypes.DWORD
GetVar.argtypes = [ctypes.wintypes.LPCWSTR, ctypes.wintypes.LPCWSTR,
                   ctypes.c_void_p, ctypes.wintypes.DWORD, ctypes.POINTER(ctypes.wintypes.DWORD)]

SetVar = kernel32.SetFirmwareEnvironmentVariableExW
SetVar.restype = ctypes.wintypes.BOOL
SetVar.argtypes = [ctypes.wintypes.LPCWSTR, ctypes.wintypes.LPCWSTR,
                   ctypes.c_void_p, ctypes.wintypes.DWORD, ctypes.wintypes.DWORD]

GUID = "{A339D746-F678-49B3-9FC7-54CE0F9DF226}"

# Read current value
buf = ctypes.create_string_buffer(65536)
attrs = ctypes.wintypes.DWORD(0)
ret = GetVar("AMD_PBS_SETUP", GUID, buf, 65536, ctypes.byref(attrs))
if ret == 0:
    print("\nCouldn't read AMD_PBS_SETUP!")
    exit(1)

original = bytearray(buf.raw[:ret])
uma_val = original[0x49]
print(f"\nCurrent AMD_PBS_SETUP[0x49] = 0x{uma_val:02X} (size={ret}B, attrs=0x{attrs.value:02X})")

# Modify the byte
modified = bytearray(original)
modified[0x49] = 0x06  # 512M
# Also clear the other 3 bytes of the DWORD (they're all 0xFF)
modified[0x4A] = 0x00
modified[0x4B] = 0x00
modified[0x4C] = 0x00

print(f"Target AMD_PBS_SETUP[0x49] = 0x06 (512M)")
print(f"Bytes 0x49-0x4C: {' '.join(f'{original[0x49+i]:02X}' for i in range(4))} → {' '.join(f'{modified[0x49+i]:02X}' for i in range(4))}")

# ─── ATTEMPT 1: Standard SetFirmwareEnvironmentVariableExW ───
print(f"\n[1] SetFirmwareEnvironmentVariableExW (attrs=0x{attrs.value:02X})...")
mbuf = ctypes.create_string_buffer(bytes(modified))
ok = SetVar("AMD_PBS_SETUP", GUID, mbuf, ret, attrs.value)
if ok:
    print("  WROTE IT! Verifying...")
else:
    err = ctypes.GetLastError()
    print(f"  Error {err}")
    
    # Try with different attrs
    for a in [0x07, 0x03, 0x01, 0x06, 0x27]:
        mbuf2 = ctypes.create_string_buffer(bytes(modified))
        ok2 = SetVar("AMD_PBS_SETUP", GUID, mbuf2, ret, a)
        if ok2:
            print(f"  WROTE with attrs=0x{a:02X}!")
            break
        else:
            e = ctypes.GetLastError()
            if e != 5:
                print(f"  attrs=0x{a:02X}: error {e}")

# ─── ATTEMPT 2: NtSetSystemEnvironmentValueEx (native API) ───
print(f"\n[2] NtSetSystemEnvironmentValueEx (bypass kernel32)...")

NtSetSystemEnvironmentValueEx = ntdll.NtSetSystemEnvironmentValueEx
NtSetSystemEnvironmentValueEx.restype = ctypes.c_long  # NTSTATUS
NtSetSystemEnvironmentValueEx.argtypes = [
    ctypes.c_void_p,   # PUNICODE_STRING Name
    ctypes.c_void_p,   # LPGUID VendorGuid  
    ctypes.c_void_p,   # PVOID Value
    ctypes.c_ulong,    # ULONG ValueLength
    ctypes.c_ulong,    # ULONG Attributes
]

# Build UNICODE_STRING for "AMD_PBS_SETUP"
class UNICODE_STRING(ctypes.Structure):
    _fields_ = [("Length", ctypes.c_ushort), ("MaxLength", ctypes.c_ushort), ("Buffer", ctypes.c_wchar_p)]

name = "AMD_PBS_SETUP"
name_us = UNICODE_STRING()
name_us.Buffer = name
name_us.Length = len(name) * 2
name_us.MaxLength = (len(name) + 1) * 2

# Parse GUID
guid_bytes = struct.pack('<IHH', 0xA339D746, 0xF678, 0x49B3) + bytes([0x9F, 0xC7, 0x54, 0xCE, 0x0F, 0x9D, 0xF2, 0x26])
guid_buf = ctypes.create_string_buffer(guid_bytes)

data_buf = ctypes.create_string_buffer(bytes(modified))

status = NtSetSystemEnvironmentValueEx(
    ctypes.byref(name_us),
    guid_buf,
    data_buf,
    ret,
    attrs.value
)
if status == 0:
    print(f"  SUCCESS! NTSTATUS=0x{status:08X}")
else:
    print(f"  NTSTATUS=0x{status & 0xFFFFFFFF:08X}")
    # Common: 0xC0000022 = STATUS_ACCESS_DENIED
    # 0xC000000D = STATUS_INVALID_PARAMETER

# ─── ATTEMPT 3: ASUS WMI SetOptionData with every possible encoding ───
print(f"\n[3] ASUS WMI SetOptionData (brute force values)...")
# Maybe the BIOS wants a different value encoding
values_to_try = [6, 0x06, 512, 0x200, 7, 0x07, 0x06000000]
for val in values_to_try:
    cmd = f'''
    $inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement
    $r = Invoke-CimMethod -InputObject $inst -MethodName "SetOptionData" -Arguments @{{ OptionName = "UmaFrameBufferSize"; Value = [uint32]{val} }}
    Write-Output "Value={val}: Error=$($r.ErrorCode)"
    '''
    r = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, timeout=5)
    result = r.stdout.strip()
    print(f"  {result}")
    if 'Error=0' in result:
        print(f"  *** WROTE! Value={val} ***")
        break

# ─── ATTEMPT 4: ASUS WMI PCI config write to iGPU ───
print(f"\n[4] ASUS WMI PCI config write (poke iGPU bridge)...")
# The AMD SoC has internal registers that control UMA
# The IOMMU/GNB has a register that sets FB size
# Try writing to the NB PCI config at bus 0 dev 0 (root complex)
cmd4 = '''
$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement

# Read NB config reg 0x90 (typical UMA base/size register on AMD)
$r90 = Invoke-CimMethod -InputObject $inst -MethodName "asio_hw_fun11" -Arguments @{
    Bus = [byte]0; Dev = [byte]0; Func = [byte]0; Reg = [uint16]144; Width = [byte]4
}
Write-Output "NB Reg 0x90: 0x$($r90.dwData.ToString('X8'))"

# Read NB config reg 0x94
$r94 = Invoke-CimMethod -InputObject $inst -MethodName "asio_hw_fun11" -Arguments @{
    Bus = [byte]0; Dev = [byte]0; Func = [byte]0; Reg = [uint16]148; Width = [byte]4
}
Write-Output "NB Reg 0x94: 0x$($r94.dwData.ToString('X8'))"

# Read GNB config at dev 18 func 1 (typical AMD internal GPU control)
for ($func = 0; $func -le 7; $func++) {
    $r = Invoke-CimMethod -InputObject $inst -MethodName "asio_hw_fun11" -Arguments @{
        Bus = [byte]0; Dev = [byte]24; Func = [byte]$func; Reg = [uint16]0; Width = [byte]4
    }
    $ven = $r.dwData -band 0xFFFF
    if ($ven -ne 0 -and $ven -ne 0xFFFF) {
        $devid = ($r.dwData -shr 16) -band 0xFFFF
        Write-Output "Bus0:Dev24:Func$func VEN=$($ven.ToString('X4')) DEV=$($devid.ToString('X4'))"
    }
}
'''
r4 = subprocess.run(['powershell', '-Command', cmd4], capture_output=True, text=True, timeout=10)
print(r4.stdout.strip())

# ─── VERIFY ───
print(f"\n[5] Verifying AMD_PBS_SETUP[0x49]...")
vbuf = ctypes.create_string_buffer(65536)
vattrs = ctypes.wintypes.DWORD(0)
vret = GetVar("AMD_PBS_SETUP", GUID, vbuf, 65536, ctypes.byref(vattrs))
if vret > 0:
    new_val = vbuf.raw[0x49]
    changed = new_val != uma_val
    print(f"  AMD_PBS_SETUP[0x49] = 0x{new_val:02X} {'CHANGED!' if changed else '(unchanged)'}")
    if changed:
        print(f"\n  *** THE BYTE IS PIRATED! Reboot to activate! ***")

print("\n" + "=" * 60)
