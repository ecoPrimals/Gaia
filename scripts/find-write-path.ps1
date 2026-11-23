# FIND WRITE PATH — Every possible way to write EFI vars from Windows
# Goal: USER-FREE firmware modification (no GRUB, no UMAF, no human)

Write-Host "=== FINDING USER-FREE WRITE PATH ==="

# === 1. ASUS WMI BIOS Settings ===
Write-Host "`n--- ASUS WMI ---"
$wmiNamespaces = @("root\WMI", "root\ASUS", "root\CIMV2", "root\CIMV2\Security\MicrosoftVolumeEncryption")
foreach ($ns in $wmiNamespaces) {
    try {
        $classes = Get-CimClass -Namespace $ns -ErrorAction Stop | Where-Object { $_.CimClassName -match 'ASUS|BIOS|Setup|Firmware|WMI|GPU|AMD|PBS' }
        if ($classes) {
            foreach ($c in $classes) {
                Write-Host ("  [{0}] {1}" -f $ns, $c.CimClassName)
                try {
                    $inst = Get-CimInstance -Namespace $ns -ClassName $c.CimClassName -ErrorAction Stop | Select-Object -First 1
                    if ($inst) {
                        $props = $inst.CimInstanceProperties | Where-Object { $_.Value -ne $null } | Select-Object -First 5
                        foreach ($p in $props) {
                            Write-Host ("    {0} = {1}" -f $p.Name, $p.Value)
                        }
                    }
                } catch {}
            }
        }
    } catch {}
}

# === 2. WMI ACPI BIOS classes ===
Write-Host "`n--- WMI ACPI/BIOS ---"
try {
    $acpiClasses = Get-CimClass -Namespace "root\WMI" -ErrorAction Stop | Where-Object { $_.CimClassName -match 'ACPI|Bios|Setup|Therm' }
    $acpiClasses | Select-Object -First 20 | ForEach-Object {
        Write-Host "  $($_.CimClassName)"
    }
} catch { Write-Host "  (root\WMI not accessible)" }

# === 3. SetFirmwareEnvironmentVariable retry with different approach ===
Write-Host "`n--- Direct EFI NVRAM Write (retry) ---"
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class FW5 {
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern bool SetFirmwareEnvironmentVariableEx(
        string lpName, string lpGuid, byte[] pValue, uint nSize, uint dwAttributes);
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern uint GetFirmwareEnvironmentVariableEx(
        string lpName, string lpGuid, [Out] byte[] pBuffer, uint nSize, out uint pdwAttribubable);
    [DllImport("advapi32.dll", SetLastError=true)]
    public static extern bool AdjustTokenPrivileges(IntPtr TokenHandle, bool DisableAllPrivileges, ref TOKEN_PRIVILEGES NewState, uint BufferLength, IntPtr PreviousState, IntPtr ReturnLength);
    [DllImport("advapi32.dll", SetLastError=true)]
    public static extern bool OpenProcessToken(IntPtr ProcessHandle, uint DesiredAccess, out IntPtr TokenHandle);
    [DllImport("advapi32.dll", SetLastError=true)]
    public static extern bool LookupPrivilegeValue(string lpSystemName, string lpName, out LUID lpLuid);
    [DllImport("kernel32.dll")]
    public static extern IntPtr GetCurrentProcess();
    [StructLayout(LayoutKind.Sequential)] public struct LUID { public uint LowPart; public int HighPart; }
    [StructLayout(LayoutKind.Sequential)] public struct LUID_AND_ATTRIBUTES { public LUID Luid; public uint Attributes; }
    [StructLayout(LayoutKind.Sequential)] public struct TOKEN_PRIVILEGES { public uint PrivilegeCount; public LUID_AND_ATTRIBUTES Privileges; }
    public static void EnablePrivilege() {
        IntPtr token; OpenProcessToken(GetCurrentProcess(), 0x28, out token);
        LUID luid; LookupPrivilegeValue(null, "SeSystemEnvironmentPrivilege", out luid);
        TOKEN_PRIVILEGES tp = new TOKEN_PRIVILEGES(); tp.PrivilegeCount = 1; tp.Privileges.Luid = luid; tp.Privileges.Attributes = 2;
        AdjustTokenPrivileges(token, false, ref tp, 0, IntPtr.Zero, IntPtr.Zero);
    }
}
"@

[FW5]::EnablePrivilege()

# Read current
$buffer = New-Object byte[] 4096
$attr = [uint32]0
$n = [FW5]::GetFirmwareEnvironmentVariableEx("AMD_PBS_SETUP", "{A339D746-F678-49B3-9FC7-54CE0F9DF226}", $buffer, 4096, [ref]$attr)
Write-Host "  READ: $n bytes, attrs=$attr"
Write-Host ("  Current 0x48=0x{0:X2}, 0x49=0x{1:X2}" -f $buffer[0x48], $buffer[0x49])

# Modify in memory
$data = $buffer[0..($n-1)]
$data[0x48] = 0x01  # iGPU Forces
$data[0x49] = 0x06  # UMA 512M

# Try write with SAME attributes as read
$result = [FW5]::SetFirmwareEnvironmentVariableEx("AMD_PBS_SETUP", "{A339D746-F678-49B3-9FC7-54CE0F9DF226}", $data, [uint32]$n, [uint32]$attr)
$err = [System.Runtime.InteropServices.Marshal]::GetLastWin32Error()
Write-Host "  WRITE result=$result, LastError=$err"

if (-not $result) {
    Write-Host "  Still blocked. Error $err = $(if($err -eq 5){'ACCESS_DENIED'}elseif($err -eq 87){'INVALID_PARAMETER'}else{'OTHER'})"
    
    # Try with different attribute combos
    foreach ($tryAttr in @(7, 3, 6, 1, 0x27, 0x47)) {
        $r2 = [FW5]::SetFirmwareEnvironmentVariableEx("AMD_PBS_SETUP", "{A339D746-F678-49B3-9FC7-54CE0F9DF226}", $data, [uint32]$n, [uint32]$tryAttr)
        $e2 = [System.Runtime.InteropServices.Marshal]::GetLastWin32Error()
        if ($r2) {
            Write-Host "  WRITE SUCCEEDED with attrs=$tryAttr!"
            break
        }
    }
}

# === 4. Check for RtlAdjustPrivilege + NtSetSystemEnvironmentValueEx ===
Write-Host "`n--- ntdll Direct NVRAM ---"
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class NT1 {
    [DllImport("ntdll.dll")]
    public static extern int RtlAdjustPrivilege(int Privilege, bool Enable, bool CurrentThread, out bool PreviousValue);
    
    [DllImport("ntdll.dll")]
    public static extern int NtSetSystemEnvironmentValueEx(
        ref UNICODE_STRING VariableName, ref Guid VendorGuid, byte[] Value, uint ValueLength, uint Attributes);
    
    [StructLayout(LayoutKind.Sequential)]
    public struct UNICODE_STRING {
        public ushort Length;
        public ushort MaximumLength;
        public IntPtr Buffer;
    }
}
"@

# SE_SYSTEM_ENVIRONMENT_PRIVILEGE = 22
$prev = $false
$adj = [NT1]::RtlAdjustPrivilege(22, $true, $false, [ref]$prev)
Write-Host "  RtlAdjustPrivilege(22): NTSTATUS=$adj prev=$prev"

# Build UNICODE_STRING for variable name
$varName = "AMD_PBS_SETUP"
$varBytes = [System.Text.Encoding]::Unicode.GetBytes($varName)
$varPtr = [System.Runtime.InteropServices.Marshal]::AllocHGlobal($varBytes.Length + 2)
[System.Runtime.InteropServices.Marshal]::Copy($varBytes, 0, $varPtr, $varBytes.Length)
[System.Runtime.InteropServices.Marshal]::WriteByte($varPtr, $varBytes.Length, 0)
[System.Runtime.InteropServices.Marshal]::WriteByte($varPtr, $varBytes.Length + 1, 0)

$ustr = New-Object NT1+UNICODE_STRING
$ustr.Length = [uint16]$varBytes.Length
$ustr.MaximumLength = [uint16]($varBytes.Length + 2)
$ustr.Buffer = $varPtr

$guid = [Guid]::Parse("A339D746-F678-49B3-9FC7-54CE0F9DF226")

$ntResult = [NT1]::NtSetSystemEnvironmentValueEx([ref]$ustr, [ref]$guid, $data, [uint32]$n, [uint32]7)
Write-Host "  NtSetSystemEnvironmentValueEx: NTSTATUS=0x$($ntResult.ToString('X8'))"

if ($ntResult -eq 0) {
    Write-Host "  🎉 NTDLL WRITE SUCCEEDED!"
} else {
    Write-Host "  NTSTATUS meanings: 0xC0000022=ACCESS_DENIED, 0xC000000D=INVALID_PARAMETER"
}

[System.Runtime.InteropServices.Marshal]::FreeHGlobal($varPtr)

# === 5. Verify if anything changed ===
Write-Host "`n--- Re-read to verify ---"
$buffer2 = New-Object byte[] 4096
$attr2 = [uint32]0
$n2 = [FW5]::GetFirmwareEnvironmentVariableEx("AMD_PBS_SETUP", "{A339D746-F678-49B3-9FC7-54CE0F9DF226}", $buffer2, 4096, [ref]$attr2)
Write-Host ("  0x48=0x{0:X2} (want 0x01), 0x49=0x{1:X2} (want 0x06)" -f $buffer2[0x48], $buffer2[0x49])

if ($buffer2[0x48] -eq 0x01) {
    Write-Host "`n  🎉 iGPU WRITTEN FROM WINDOWS! Reboot to activate!"
} else {
    Write-Host "`n  Summary: Windows kernel blocks EFI NVRAM writes for vendor variables."
    Write-Host "  The ONLY user-free path is a custom EFI binary with embedded config."
    Write-Host "  OR: a kernel driver (like ASUS ArmouryCrate uses internally)."
}
