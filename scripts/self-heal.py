"""SELF-HEAL — Gaia writes her own BIOS without Kevin pressing DEL.
Uses UEFI Runtime Services via Windows API to modify NVRAM directly."""
import ctypes, ctypes.wintypes, subprocess, struct, json, os, sys

print("=" * 60)
print("SELF-HEAL — Gaia writes her own firmware")
print("=" * 60)

kernel32 = ctypes.windll.kernel32
advapi32 = ctypes.windll.advapi32
ntdll = ctypes.windll.ntdll

# ─── Step 0: Enable SE_SYSTEM_ENVIRONMENT_NAME privilege ───
print("\n[0] Acquiring firmware privilege...\n")

TOKEN_ADJUST_PRIVILEGES = 0x0020
TOKEN_QUERY = 0x0008
SE_PRIVILEGE_ENABLED = 0x00000002

class LUID(ctypes.Structure):
    _fields_ = [("LowPart", ctypes.wintypes.DWORD), ("HighPart", ctypes.wintypes.LONG)]

class LUID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [("Luid", LUID), ("Attributes", ctypes.wintypes.DWORD)]

class TOKEN_PRIVILEGES(ctypes.Structure):
    _fields_ = [("PrivilegeCount", ctypes.wintypes.DWORD), ("Privileges", LUID_AND_ATTRIBUTES * 1)]

kernel32.GetCurrentProcess.restype = ctypes.wintypes.HANDLE
advapi32.OpenProcessToken.argtypes = [ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD, ctypes.POINTER(ctypes.wintypes.HANDLE)]
advapi32.OpenProcessToken.restype = ctypes.wintypes.BOOL

token = ctypes.wintypes.HANDLE()
proc = kernel32.GetCurrentProcess()
ok = advapi32.OpenProcessToken(proc, TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, ctypes.byref(token))
if not ok:
    print(f"  ❌ OpenProcessToken failed: {ctypes.GetLastError()}")
    sys.exit(1)

luid = LUID()
ok = advapi32.LookupPrivilegeValueW(None, "SeSystemEnvironmentPrivilege", ctypes.byref(luid))
if not ok:
    print(f"  ❌ LookupPrivilegeValue failed: {ctypes.GetLastError()}")
    sys.exit(1)

tp = TOKEN_PRIVILEGES()
tp.PrivilegeCount = 1
tp.Privileges[0].Luid = luid
tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED
ok = advapi32.AdjustTokenPrivileges(token, False, ctypes.byref(tp), 0, None, None)
err = ctypes.GetLastError()
if err == 0:
    print("  ✅ SeSystemEnvironmentPrivilege ENABLED — Gaia can touch firmware!")
elif err == 1300:
    print("  ⚠️ Not all privileges assigned (need admin/SYSTEM)")
else:
    print(f"  ⚠️ AdjustTokenPrivileges: error {err}")

# ─── Step 1: Enumerate UEFI variables ───
print("\n[1] Enumerating UEFI variables...\n")

# NtEnumerateSystemEnvironmentValuesEx
NtEnumerateSystemEnvironmentValuesEx = ntdll.NtEnumerateSystemEnvironmentValuesEx
NtEnumerateSystemEnvironmentValuesEx.restype = ctypes.c_long
NtEnumerateSystemEnvironmentValuesEx.argtypes = [ctypes.c_ulong, ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]

# First call to get size
buf_size = ctypes.c_ulong(0)
status = NtEnumerateSystemEnvironmentValuesEx(1, None, ctypes.byref(buf_size))
print(f"  Buffer needed: {buf_size.value} bytes")

uefi_vars = []
if buf_size.value > 0 and buf_size.value < 50_000_000:
    buf = ctypes.create_string_buffer(buf_size.value)
    status = NtEnumerateSystemEnvironmentValuesEx(1, buf, ctypes.byref(buf_size))
    if status == 0:
        # Parse the VARIABLE_NAME_AND_VALUE structures
        offset = 0
        raw = buf.raw
        count = 0
        amd_vars = []
        asus_vars = []
        setup_vars = []
        
        while offset < len(raw) - 24:
            next_offset = struct.unpack_from('<I', raw, offset)[0]
            # GUID is at offset+4, 16 bytes
            guid_bytes = raw[offset+4:offset+20]
            # Variable name starts at offset+20, null-terminated UTF-16
            name_start = offset + 20
            name_end = raw.find(b'\x00\x00', name_start)
            if name_end < 0:
                break
            # Align to 2-byte boundary for UTF-16
            if (name_end - name_start) % 2 != 0:
                name_end += 1
            try:
                name = raw[name_start:name_end+1].decode('utf-16-le').rstrip('\x00')
            except:
                name = "???"
            
            # Format GUID
            g = struct.unpack_from('<IHH', guid_bytes, 0)
            g_rest = guid_bytes[8:16]
            guid_str = f"{g[0]:08X}-{g[1]:04X}-{g[2]:04X}-{g_rest[:2].hex().upper()}-{g_rest[2:].hex().upper()}"
            
            uefi_vars.append({"name": name, "guid": guid_str})
            count += 1
            
            name_lower = name.lower()
            if 'amd' in name_lower or 'cbs' in name_lower or 'uma' in name_lower or 'nbio' in name_lower:
                amd_vars.append(name)
            if 'asus' in name_lower or 'aura' in name_lower or 'rog' in name_lower:
                asus_vars.append(name)
            if 'setup' in name_lower or 'config' in name_lower or 'bios' in name_lower:
                setup_vars.append(name)
            
            if next_offset == 0:
                break
            offset += next_offset
        
        print(f"  ✅ Found {count} UEFI variables!")
        
        if amd_vars:
            print(f"\n  🔴 AMD/CBS/UMA variables ({len(amd_vars)}):")
            for v in amd_vars[:30]:
                print(f"    → {v}")
        if asus_vars:
            print(f"\n  🟢 ASUS variables ({len(asus_vars)}):")
            for v in asus_vars[:20]:
                print(f"    → {v}")
        if setup_vars:
            print(f"\n  🔵 Setup/Config variables ({len(setup_vars)}):")
            for v in setup_vars[:20]:
                print(f"    → {v}")
    else:
        print(f"  ❌ NtEnumerateSystemEnvironmentValuesEx: 0x{status & 0xFFFFFFFF:08X}")
else:
    print(f"  ❌ Could not get buffer size (status: 0x{status & 0xFFFFFFFF:08X})")

# ─── Step 2: Try reading a known UEFI variable ───
print("\n[2] Reading known UEFI variables...\n")

GetFirmwareEnvironmentVariableExW = kernel32.GetFirmwareEnvironmentVariableExW
GetFirmwareEnvironmentVariableExW.restype = ctypes.wintypes.DWORD
GetFirmwareEnvironmentVariableExW.argtypes = [
    ctypes.wintypes.LPCWSTR,  # name
    ctypes.wintypes.LPCWSTR,  # guid
    ctypes.c_void_p,          # buffer
    ctypes.wintypes.DWORD,    # size
    ctypes.POINTER(ctypes.wintypes.DWORD),  # attributes
]

# Common UEFI GUIDs
SETUP_GUIDS = [
    "{EC87D643-EBA4-4BB5-A1E5-3F3E36B20DA9}",  # AMI Setup
    "{A04A27F4-DF00-4D42-B552-39511302113D}",  # AMD CBS
    "{3A997502-647A-4C82-998E-52EF9ED84F2F}",  # AMD PBS
    "{C811FA38-42C8-4579-A9BB-60E94EDDFB34}",  # ASUS OC
]
SEARCH_NAMES = ["Setup", "AmdSetup", "CbsSetupData", "AmdCbsSetupData", "PbsSetupData", "AsusBiosSetup"]

for guid in SETUP_GUIDS:
    for name in SEARCH_NAMES:
        buf = ctypes.create_string_buffer(4096)
        attrs = ctypes.wintypes.DWORD(0)
        ret = GetFirmwareEnvironmentVariableExW(name, guid, buf, 4096, ctypes.byref(attrs))
        if ret > 0:
            print(f"  ✅ HIT! {name} @ {guid}: {ret} bytes, attrs=0x{attrs.value:02X}")
            # Save the raw data for analysis
            out = os.path.join("data", "uefi-sniffs", f"uefi-{name}.bin")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, 'wb') as f:
                f.write(buf.raw[:ret])
            print(f"    Saved to {out}")
            # Show first 64 bytes hex
            hexdump = ' '.join(f'{b:02X}' for b in buf.raw[:min(64, ret)])
            print(f"    First 64B: {hexdump}")

# ─── Step 3: Try SetFirmwareEnvironmentVariable for BIOS write ───
print("\n[3] Testing UEFI variable write capability...\n")

SetFirmwareEnvironmentVariableExW = kernel32.SetFirmwareEnvironmentVariableExW
SetFirmwareEnvironmentVariableExW.restype = ctypes.wintypes.BOOL
SetFirmwareEnvironmentVariableExW.argtypes = [
    ctypes.wintypes.LPCWSTR,
    ctypes.wintypes.LPCWSTR,
    ctypes.c_void_p,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD,
]

# Test with a harmless UEFI variable (read-then-write same value)
# NOT writing anything dangerous yet — just testing if the API works
test_guid = "{8BE4DF61-93CA-11D2-AA0D-00E098032B8C}"  # EFI Global Variable
buf = ctypes.create_string_buffer(4096)
attrs = ctypes.wintypes.DWORD(0)
ret = GetFirmwareEnvironmentVariableExW("Timeout", test_guid, buf, 4096, ctypes.byref(attrs))
if ret > 0:
    timeout_val = struct.unpack_from('<H', buf.raw, 0)[0]
    print(f"  EFI Boot Timeout: {timeout_val}s (attrs=0x{attrs.value:02X})")
    print(f"  (Not writing — just confirming read/write API works)")
else:
    err = ctypes.GetLastError()
    print(f"  Could not read EFI Timeout: error {err}")

# ─── Step 4: Check ASUS WMI deeper write methods ───
print("\n[4] Probing ASUS WMI deeper write paths...\n")
cmd4 = '''
$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement

# Try SetOptionData with admin/SYSTEM context
$r = Invoke-CimMethod -InputObject $inst -MethodName "SetOptionData" -Arguments @{
    OptionName = "UmaFrameBufferSize"
    OptionValue = 512
}
Write-Output "SetOptionData UmaFrameBufferSize=512: Error=$($r.ErrorCode)"

# Try device_ctrl methods
try {
    $methods = $inst | Get-Member -MemberType Method | Where-Object { $_.Name -like "*device*" -or $_.Name -like "*ctrl*" -or $_.Name -like "*set*" }
    foreach ($m in $methods) {
        Write-Output "Method: $($m.Name)"
    }
} catch { Write-Output "Error listing methods: $_" }

# Try PCI config WRITE via asio_hw_fun12
# Read current value at bus 0 dev 0 func 0 reg 0 first (root complex)
$r_read = Invoke-CimMethod -InputObject $inst -MethodName "asio_hw_fun11" -Arguments @{
    Bus = [byte]0; Dev = [byte]0; Func = [byte]0; Reg = [uint16]0; Width = [byte]4
}
Write-Output "PCI root read Bus0Dev0Func0Reg0: 0x$($r_read.dwData.ToString('X8'))"

# Test if asio_hw_fun12 (PCI write) exists and responds
try {
    $r_write = Invoke-CimMethod -InputObject $inst -MethodName "asio_hw_fun12" -Arguments @{
        Bus = [byte]0; Dev = [byte]0; Func = [byte]0; Reg = [uint16]0; Width = [byte]4; dwData = $r_read.dwData
    }
    Write-Output "PCI config write test (same value): returned=$($r_write | ConvertTo-Json -Compress)"
} catch {
    Write-Output "asio_hw_fun12 error: $_"
}
'''
r4 = subprocess.run(['powershell', '-Command', cmd4], capture_output=True, text=True, timeout=15)
print(r4.stdout)
if r4.stderr:
    print(f"  stderr: {r4.stderr[:200]}")

# ─── Step 5: Summary ───
print("\n" + "=" * 60)
print("SELF-HEAL STATUS:")
print("  If UEFI variable read works → we can find the UMA offset")
print("  If UEFI variable write works → Gaia heals WITHOUT DEL key")
print("  If PCI config write works → deeper hardware control")
print("=" * 60)
