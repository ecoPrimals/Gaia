"""Crack UMA — find the exact byte and write path for iGPU memory."""
import ctypes, ctypes.wintypes, struct, subprocess, json, os

# ─── Part 1: Get the exact WMI SetOptionData parameter names ───
print("=" * 60)
print("CRACKING UMA — Finding the write path")
print("=" * 60)

print("\n[1] Exact WMI method signatures for SetOptionData...\n")
cmd1 = '''
$class = Get-CimClass -Namespace root/WMI -ClassName ASUSManagement
foreach ($m in $class.CimClassMethods) {
    $params = $m.Parameters | ForEach-Object { "$($_.Name)($($_.CimType))" }
    Write-Output "$($m.Name): $($params -join ', ')"
}
'''
r1 = subprocess.run(['powershell', '-Command', cmd1], capture_output=True, text=True, timeout=10)
print(r1.stdout)

# ─── Part 2: Try SetOptionData with correct parameter names ───
print("[2] Trying SetOptionData with discovered params...\n")
cmd2 = '''
$class = Get-CimClass -Namespace root/WMI -ClassName ASUSManagement
$setMethod = $class.CimClassMethods | Where-Object { $_.Name -eq "SetOptionData" }
Write-Output "SetOptionData params:"
foreach ($p in $setMethod.Parameters) {
    Write-Output "  $($p.Name) : $($p.CimType) (Qualifiers: $($p.Qualifiers | ForEach-Object { "$($_.Name)=$($_.Value)" }))"
}

$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement

# Try with correct params
try {
    $r = Invoke-CimMethod -InputObject $inst -MethodName "SetOptionData" -Arguments @{
        OptionName = "UmaFrameBufferSize"
        Value = [uint32]512
    }
    Write-Output "SetOptionData (Value=512): Error=$($r.ErrorCode) Return=$($r | ConvertTo-Json -Compress)"
} catch {
    Write-Output "Error with Value: $_"
}

# Try with different param names
$paramNames = @("Value", "OptionValue", "Data", "Setting", "dwValue", "NewValue")
foreach ($pn in $paramNames) {
    try {
        $args = @{ OptionName = "UmaFrameBufferSize" }
        $args[$pn] = [uint32]4
        $r = Invoke-CimMethod -InputObject $inst -MethodName "SetOptionData" -Arguments $args
        Write-Output "SetOptionData ($pn=4): Error=$($r.ErrorCode)"
    } catch {
        # Silently skip param name errors
    }
}
'''
r2 = subprocess.run(['powershell', '-Command', cmd2], capture_output=True, text=True, timeout=15)
print(r2.stdout)
if r2.stderr:
    print(f"  stderr: {r2.stderr[:300]}")

# ─── Part 3: Direct UEFI variable analysis ───
print("\n[3] Comparing AMD_PBS_SETUP with StdDefaults...\n")

kernel32 = ctypes.windll.kernel32
advapi32 = ctypes.windll.advapi32

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
advapi32.OpenProcessToken(kernel32.GetCurrentProcess(), 0x0028, ctypes.byref(token))
luid = LUID()
advapi32.LookupPrivilegeValueW(None, "SeSystemEnvironmentPrivilege", ctypes.byref(luid))
tp = TOKEN_PRIVILEGES()
tp.PrivilegeCount = 1
tp.Privileges[0].Luid = luid
tp.Privileges[0].Attributes = 0x00000002
advapi32.AdjustTokenPrivileges(token, False, ctypes.byref(tp), 0, None, None)

GetVar = kernel32.GetFirmwareEnvironmentVariableExW
GetVar.restype = ctypes.wintypes.DWORD
GetVar.argtypes = [ctypes.wintypes.LPCWSTR, ctypes.wintypes.LPCWSTR,
                   ctypes.c_void_p, ctypes.wintypes.DWORD, ctypes.POINTER(ctypes.wintypes.DWORD)]

SetVar = kernel32.SetFirmwareEnvironmentVariableExW
SetVar.restype = ctypes.wintypes.BOOL
SetVar.argtypes = [ctypes.wintypes.LPCWSTR, ctypes.wintypes.LPCWSTR,
                   ctypes.c_void_p, ctypes.wintypes.DWORD, ctypes.wintypes.DWORD]

# Read AMD_PBS_SETUP
buf = ctypes.create_string_buffer(65536)
attrs = ctypes.wintypes.DWORD(0)
ret = GetVar("AMD_PBS_SETUP", "{A339D746-F678-49B3-9FC7-54CE0F9DF226}", buf, 65536, ctypes.byref(attrs))
pbs_data = bytearray(buf.raw[:ret])
print(f"AMD_PBS_SETUP: {ret} bytes, attrs=0x{attrs.value:02X}")

# Hex dump around offset 0x49
print("\nAMD_PBS_SETUP around offset 0x49 (suspected UMA):")
for i in range(0x40, min(0x60, len(pbs_data)), 16):
    hex_part = ' '.join(f'{pbs_data[i+j]:02X}' for j in range(min(16, len(pbs_data)-i)))
    ascii_part = ''.join(chr(pbs_data[i+j]) if 32 <= pbs_data[i+j] < 127 else '.' for j in range(min(16, len(pbs_data)-i)))
    print(f"  {i:04X}: {hex_part:<48s} {ascii_part}")

# Read Setup variable
buf2 = ctypes.create_string_buffer(65536)
ret2 = GetVar("Setup", "{EC87D643-EBA4-4BB5-A1E5-3F3E36B20DA9}", buf2, 65536, ctypes.byref(attrs))
setup_data = bytearray(buf2.raw[:ret2])
print(f"\nSetup: {ret2} bytes, attrs=0x{attrs.value:02X}")

print("\nSetup around offset 0xE6 (suspected UMA):")
for i in range(0xE0, min(0xF8, len(setup_data)), 16):
    hex_part = ' '.join(f'{setup_data[i+j]:02X}' for j in range(min(16, len(setup_data)-i)))
    print(f"  {i:04X}: {hex_part}")

# ─── Part 4: Try a TEST WRITE — write same value back ───
print("\n[4] Testing UEFI variable WRITE capability...\n")

# First, try writing AMD_PBS_SETUP back with SAME data (safe test)
test_buf = ctypes.create_string_buffer(bytes(pbs_data))
ok = SetVar("AMD_PBS_SETUP", "{A339D746-F678-49B3-9FC7-54CE0F9DF226}", test_buf, len(pbs_data), attrs.value)
if ok:
    print("  ✅ AMD_PBS_SETUP write SUCCEEDED (same value)! WE CAN WRITE BIOS!")
else:
    err = ctypes.GetLastError()
    print(f"  ❌ Write failed: error {err}")
    # Error codes: 1 = invalid function, 5 = access denied, 
    # 87 = invalid parameter, 1314 = privilege not held
    error_names = {1: "invalid function", 5: "access denied", 87: "invalid param", 
                   1314: "privilege not held", 0: "ok"}
    print(f"     ({error_names.get(err, 'unknown')})")

# Also test with Setup variable
test_buf2 = ctypes.create_string_buffer(bytes(setup_data))
ok2 = SetVar("Setup", "{EC87D643-EBA4-4BB5-A1E5-3F3E36B20DA9}", test_buf2, len(setup_data), attrs.value)
if ok2:
    print("  ✅ Setup write SUCCEEDED (same value)!")
else:
    err2 = ctypes.GetLastError()
    print(f"  ❌ Setup write failed: error {err2}")

# ─── Part 5: Scan ALL 0xFF bytes and their context ───
print("\n[5] All single-byte 0xFF positions in AMD_PBS_SETUP...\n")
ff_bytes = [(i, pbs_data[i]) for i in range(len(pbs_data)) if pbs_data[i] == 0xFF]
print(f"  Found {len(ff_bytes)} bytes with value 0xFF")
print(f"  Offsets: {', '.join(f'0x{i:02X}' for i, _ in ff_bytes)}")

# Check for PrimaryVideo = 2
print(f"\n  All bytes with value 0x02:")
twos = [i for i in range(len(pbs_data)) if pbs_data[i] == 0x02]
print(f"  Offsets: {', '.join(f'0x{i:02X}' for i in twos)}")

# Check neighborhood of first 0x02 after the 0xFF block
for t in twos:
    if 0x40 <= t <= 0x60:
        context = ' '.join(f'{pbs_data[t-3+j]:02X}' for j in range(7) if 0 <= t-3+j < len(pbs_data))
        print(f"  Context around 0x{t:02X}: {context}")

print("\n" + "=" * 60)
print("RESULT: Can we write BIOS from Windows?")
print("=" * 60)
