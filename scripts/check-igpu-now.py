"""Check iGPU status RIGHT NOW after reboot — is UMA set?"""
import subprocess, ctypes, ctypes.wintypes, struct

print("=" * 60)
print("POST-REBOOT iGPU CHECK")
print("=" * 60)

# CPU info
print("\n[1] CPU...\n")
r = subprocess.run(['powershell', '-Command', 
    'Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores | Format-List'],
    capture_output=True, text=True, timeout=10)
print(r.stdout.strip())

# Display adapters
print("\n[2] Display adapters...\n")
r2 = subprocess.run(['powershell', '-Command',
    'Get-PnpDevice -Class Display -ErrorAction SilentlyContinue | Format-Table FriendlyName,Status,InstanceId -AutoSize'],
    capture_output=True, text=True, timeout=10)
print(r2.stdout.strip())

# All AMD 1002 devices
print("\n[3] All AMD (VEN_1002) devices...\n")
cmd3 = "Get-PnpDevice | Where-Object { $_.InstanceId -like '*1002*' } | Format-Table FriendlyName,Status,Class,InstanceId -AutoSize"
r3 = subprocess.run(['powershell', '-Command', cmd3], capture_output=True, text=True, timeout=10)
print(r3.stdout.strip() if r3.stdout.strip() else "  None found")

# Monitor count
print("\n[4] Displays...\n")
cmd4 = "Add-Type -AssemblyName System.Windows.Forms; Write-Output \"Display count: $([System.Windows.Forms.Screen]::AllScreens.Count)\""
r4 = subprocess.run(['powershell', '-Command', cmd4], capture_output=True, text=True, timeout=10)
print(f"  {r4.stdout.strip()}")

# UEFI variable check
print("\n[5] UEFI UMA value...\n")
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
        uma_val = struct.unpack_from('<I', data, 0x49)[0]
        print(f"  AMD_PBS_SETUP[0x49] = 0x{uma_val:08X}")
        if uma_val == 0xFFFFFFFF:
            print("  Still [Auto] = 0xFFFFFFFF — UMA was NOT changed")
        else:
            print(f"  CHANGED to 0x{uma_val:08X}!")
        
        # Also check the ASUS WMI
        cmd_wmi = 'Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement | ForEach-Object { $r = Invoke-CimMethod -InputObject $_ -MethodName "GetOptionData" -Arguments @{OptionName="UmaFrameBufferSize"}; Write-Output "WMI UmaFrameBufferSize: Value=$($r.Value) Error=$($r.ErrorCode)" }'
        rw = subprocess.run(['powershell', '-Command', cmd_wmi], capture_output=True, text=True, timeout=10)
        print(f"  {rw.stdout.strip()}")
except Exception as e:
    print(f"  Error: {e}")

# AKD1000 check
print("\n[6] AKD1000...\n")
cmd6 = "Get-PnpDevice | Where-Object { $_.InstanceId -like '*1E7C*' } | Format-Table FriendlyName,Status,InstanceId -AutoSize"
r6 = subprocess.run(['powershell', '-Command', cmd6], capture_output=True, text=True, timeout=10)
print(r6.stdout.strip() if r6.stdout.strip() else "  AKD1000: NOT ON BUS")

# PCIe
print("\n[7] RTX 5090 PCIe...\n")
r7 = subprocess.run(['nvidia-smi', '--query-gpu=pcie.link.gen.current,pcie.link.gen.max,pcie.link.width.current,pcie.link.width.max', '--format=csv'], capture_output=True, text=True, timeout=5)
print(f"  {r7.stdout.strip()}")

print("\n" + "=" * 60)
print("KEY QUESTION: Does the 9950X3D have iGPU silicon?")
print("Ryzen 9000 (Granite Ridge) = Zen 5 + RDNA 2 iGPU (2 CUs)")  
print("The mobo HDMI SHOULD work if UMA is allocated.")
print("If UMA option is HIDDEN in BIOS, the BIOS may not detect iGPU.")
print("=" * 60)
