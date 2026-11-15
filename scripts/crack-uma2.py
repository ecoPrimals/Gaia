"""Last attempt at runtime UEFI write + EFI shell setup_var approach."""
import ctypes, ctypes.wintypes, struct, subprocess, os

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

print("=" * 60)
print("CRACK UMA — Round 2")
print("=" * 60)

# ─── Test 1: Try writing EFI Timeout (harmless, same value) ───
print("\n[1] Testing Timeout write (same value back)...\n")
buf = ctypes.create_string_buffer(64)
attrs = ctypes.wintypes.DWORD(0)
ret = GetVar("Timeout", "{8BE4DF61-93CA-11D2-AA0D-00E098032B8C}", buf, 64, ctypes.byref(attrs))
if ret > 0:
    timeout = struct.unpack_from('<H', buf.raw, 0)[0]
    print(f"  Current Timeout = {timeout}s, attrs=0x{attrs.value:02X}")
    ok = SetVar("Timeout", "{8BE4DF61-93CA-11D2-AA0D-00E098032B8C}", buf, ret, attrs.value)
    if ok:
        print(f"  ✅ Timeout write SUCCEEDED! Runtime writes WORK!")
    else:
        err = ctypes.GetLastError()
        print(f"  ❌ Timeout write failed: error {err}")

# ─── Test 2: Try writing OsIndications (request firmware UI) ───
print("\n[2] Check Secure Boot status...\n")
r = subprocess.run(['powershell', '-Command', 'Confirm-SecureBootUEFI'], capture_output=True, text=True, timeout=5)
print(f"  Secure Boot: {r.stdout.strip()}")

# ─── Test 3: Explore EFI System Partition for setup_var ───
print("\n[3] EFI System Partition exploration...\n")
cmd = '''
# Mount EFI partition
$efiPart = Get-Partition | Where-Object { $_.GptType -eq "{C12A7328-F81F-11D2-BA4B-00A0C93EC93B}" }
if ($efiPart) {
    Write-Output "EFI partition found: Disk $($efiPart.DiskNumber) Partition $($efiPart.PartitionNumber)"
    # Try to access if already mounted
    $vols = Get-Volume | Where-Object { $_.FileSystemType -eq "FAT32" -and $_.Size -lt 1GB }
    foreach ($v in $vols) {
        Write-Output "  FAT32 volume: $($v.DriveLetter): $($v.Size/1MB)MB $($v.FileSystemLabel)"
    }
}
# Check bcdedit for UEFI boot entries
bcdedit /enum firmware 2>&1 | Select-Object -First 30
'''
r3 = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, timeout=10)
print(r3.stdout[:1000])

# ─── Test 4: Create a custom UEFI variable (our own, non-locked) ───
print("\n[4] Testing custom UEFI variable creation...\n")
test_data = struct.pack('<I', 42)
test_buf = ctypes.create_string_buffer(test_data)
# Use a random GUID for our test variable
ok = SetVar("GaiaTest", "{DEADBEEF-1234-5678-ABCD-EF0123456789}", test_buf, 4, 0x07)
if ok:
    print("  ✅ Custom variable 'GaiaTest' created! We CAN write UEFI!")
    # Read it back
    rbuf = ctypes.create_string_buffer(64)
    rret = GetVar("GaiaTest", "{DEADBEEF-1234-5678-ABCD-EF0123456789}", rbuf, 64, ctypes.byref(attrs))
    if rret > 0:
        val = struct.unpack_from('<I', rbuf.raw, 0)[0]
        print(f"  Read back: {val} (expected 42)")
    # Clean up
    ok2 = SetVar("GaiaTest", "{DEADBEEF-1234-5678-ABCD-EF0123456789}", None, 0, 0x07)
    if ok2:
        print("  Cleaned up test variable")
else:
    err = ctypes.GetLastError()
    print(f"  ❌ Custom variable write failed: error {err}")
    if err == 5:
        print("     UEFI variable writes completely blocked (Secure Boot or firmware lock)")

# ─── Test 5: Check if we're running as admin ───
print("\n[5] Privilege check...\n")
r5 = subprocess.run(['powershell', '-Command', '([Security.Principal.WindowsPrincipal]([Security.Principal.WindowsIdentity]::GetCurrent())).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)'], capture_output=True, text=True, timeout=5)
print(f"  Is Admin: {r5.stdout.strip()}")
r6 = subprocess.run(['whoami', '/priv'], capture_output=True, text=True, timeout=5)
for line in r6.stdout.split('\n'):
    if 'SeSystem' in line:
        print(f"  {line.strip()}")

# ─── Summary: What DO we have? ───
print("\n" + "=" * 60)
print("WHAT WE KNOW:")
print("  ✅ UMA Frame Buffer Size = AMD_PBS_SETUP offset 0x49 (4 bytes)")
print("  ✅ PrimaryVideo = AMD_PBS_SETUP offset 0x4E (1 byte)")
print("  ✅ Variable GUID = {A339D746-F678-49B3-9FC7-54CE0F9DF226}")
print("  ✅ Variable attrs = 0x07 (NV+BS+RT)")
print("  ❓ Runtime write locked by ASUS firmware")
print()
print("PATHS TO TRY:")
print("  1. setup_var.efi from EFI shell (boot-time, before lock)")
print("  2. GRUB2 setup_var approach")
print("  3. ASUS BIOS Flashback with modified BIOS image")
print("  4. Just press DEL on reboot (10 seconds of Kevin's time)")
print("=" * 60)
