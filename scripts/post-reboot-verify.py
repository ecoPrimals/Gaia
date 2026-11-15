
"""POST-REBOOT VERIFY — Run automatically after reboot to check BIOS changes."""
import subprocess, json, os, ctypes, ctypes.wintypes, struct, time
from datetime import datetime

print("=" * 60)
print("POST-REBOOT VERIFY — Checking BIOS surgery results")
print("=" * 60)

results = {"timestamp": datetime.now().isoformat(), "phase": "post-reboot", "checks": {}}

# ─── Check 1: Displays ───
print("
[1] Displays...
")
cmd = 'Add-Type -AssemblyName System.Windows.Forms; $screens = [System.Windows.Forms.Screen]::AllScreens; Write-Output "Count: $($screens.Count)"; foreach ($s in $screens) { Write-Output "  $($s.DeviceName): $($s.Bounds.Width)x$($s.Bounds.Height) Primary=$($s.Primary)" }'
r = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, timeout=10)
print(r.stdout)
results["checks"]["displays"] = r.stdout.strip()
display_count = 1
for line in r.stdout.split('
'):
    if 'Count:' in line:
        try:
            display_count = int(line.split(':')[1].strip())
        except:
            pass

if display_count >= 2:
    print("  🎉 TWO DISPLAYS LIVE! LEFT EYE OPEN!")
else:
    print("  ⚠️ Still 1 display — UMA may not have been set")

# ─── Check 2: Video adapters ───
print("
[2] Video adapters...
")
cmd2 = 'Get-PnpDevice -Class Display | ForEach-Object { Write-Output "$($_.FriendlyName): $($_.Status) ($($_.InstanceId))" }'
r2 = subprocess.run(['powershell', '-Command', cmd2], capture_output=True, text=True, timeout=10)
print(r2.stdout)
results["checks"]["video_adapters"] = r2.stdout.strip()

# ─── Check 3: AKD1000 ───
print("
[3] AKD1000 (VEN_1E7C)...
")
cmd3 = '$found = $false; Get-PnpDevice | ForEach-Object { if ($_.InstanceId -like "*1E7C*") { Write-Output "AKD1000 FOUND: $($_.FriendlyName) Status=$($_.Status) ID=$($_.InstanceId)"; $found = $true } }; if (-not $found) { Write-Output "AKD1000: NOT ON BUS" }'
r3 = subprocess.run(['powershell', '-Command', cmd3], capture_output=True, text=True, timeout=10)
print(r3.stdout)
results["checks"]["akd1000"] = r3.stdout.strip()

# ─── Check 4: PCIe Gen ───
print("
[4] RTX 5090 PCIe...
")
r4 = subprocess.run(['nvidia-smi', '--query-gpu=pcie.link.gen.current,pcie.link.gen.max,pcie.link.width.current,pcie.link.width.max', '--format=csv,noheader'], capture_output=True, text=True, timeout=5)
print(f"  {r4.stdout.strip()}")
results["checks"]["pcie"] = r4.stdout.strip()

# ─── Check 5: UEFI variable verify ───
print("
[5] UEFI variable check (UMA)...
")
try:
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
    
    buf = ctypes.create_string_buffer(65536)
    attrs = ctypes.wintypes.DWORD(0)
    ret = GetVar("AMD_PBS_SETUP", "{A339D746-F678-49B3-9FC7-54CE0F9DF226}", buf, 65536, ctypes.byref(attrs))
    if ret > 0:
        data = buf.raw[:ret]
        uma_bytes = data[0x49:0x4D]
        uma_val = struct.unpack_from('<I', uma_bytes, 0)[0]
        print(f"  AMD_PBS_SETUP[0x49] = 0x{uma_val:08X}")
        if uma_val == 0xFFFFFFFF:
            print("  ⚠️ Still Auto (0xFFFFFFFF) — UMA not changed!")
        else:
            print(f"  ✅ UMA CHANGED! New value: 0x{uma_val:08X}")
        results["checks"]["uma_value"] = f"0x{uma_val:08X}"
except Exception as e:
    print(f"  Error: {e}")

# ─── Check 6: Network ───
print("
[6] Network...
")
r6 = subprocess.run(['ping', '-n', '1', '-w', '500', '192.168.4.244'], capture_output=True, text=True, timeout=3)
eastgate = 'Reply from' in r6.stdout
print(f"  eastGate: {'✅' if eastgate else '❌'}")
r7 = subprocess.run(['ping', '-n', '1', '-w', '500', '192.168.4.1'], capture_output=True, text=True, timeout=3)
router = 'Reply from' in r7.stdout
print(f"  Router: {'✅' if router else '❌'}")

# ─── Save results ───
os.makedirs("data/uefi-sniffs", exist_ok=True)
with open("data/uefi-sniffs/post-reboot-verify.json", 'w') as f:
    json.dump(results, f, indent=2)
print(f"
  Results saved to data/uefi-sniffs/post-reboot-verify.json")

# ─── Summary ───
print("
" + "=" * 60)
if display_count >= 2:
    print("🎉 BOTH EYES OPEN! Display 2 is ALIVE!")
    print("   Next: Set up RustDesk/amoeba on Display 2")
else:
    print("⚠️ Display 2 not yet live. Check BIOS settings.")
print("=" * 60)
