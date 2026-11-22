# Direct UEFI NVRAM variable probe
# Try to read the "Setup" variable — if we can read it, we might be able to write it

# Enable SeSystemEnvironmentPrivilege
$signature = @'
[DllImport("kernel32.dll", SetLastError=true)]
public static extern uint GetFirmwareEnvironmentVariableEx(
    string lpName, string lpGuid, byte[] pBuffer, uint nSize, out uint pdwAttribubable);

[DllImport("kernel32.dll", SetLastError=true)]
public static extern bool SetFirmwareEnvironmentVariableEx(
    string lpName, string lpGuid, byte[] pValue, uint nSize, uint dwAttributes);
'@

# First enable privilege
$adj = @'
using System;
using System.Runtime.InteropServices;

public class TokenPriv {
    [DllImport("advapi32.dll", SetLastError=true)]
    static extern bool OpenProcessToken(IntPtr ProcessHandle, uint DesiredAccess, out IntPtr TokenHandle);
    
    [DllImport("advapi32.dll", SetLastError=true)]
    static extern bool LookupPrivilegeValue(string lpSystemName, string lpName, out long lpLuid);
    
    [DllImport("advapi32.dll", SetLastError=true)]
    static extern bool AdjustTokenPrivileges(IntPtr TokenHandle, bool DisableAllPrivileges,
        ref TOKEN_PRIVILEGES NewState, uint BufferLength, IntPtr PreviousState, IntPtr ReturnLength);

    [StructLayout(LayoutKind.Sequential)]
    public struct TOKEN_PRIVILEGES {
        public uint PrivilegeCount;
        public long Luid;
        public uint Attributes;
    }

    public static bool Enable() {
        IntPtr token;
        if (!OpenProcessToken((IntPtr)(-1), 0x0020 | 0x0008, out token)) return false;
        long luid;
        if (!LookupPrivilegeValue(null, "SeSystemEnvironmentPrivilege", out luid)) return false;
        TOKEN_PRIVILEGES tp = new TOKEN_PRIVILEGES();
        tp.PrivilegeCount = 1;
        tp.Luid = luid;
        tp.Attributes = 0x00000002;
        return AdjustTokenPrivileges(token, false, ref tp, 0, IntPtr.Zero, IntPtr.Zero);
    }
}
'@

Add-Type -TypeDefinition $adj
$ok = [TokenPriv]::Enable()
Write-Output "SeSystemEnvironmentPrivilege: $ok"

Add-Type -MemberDefinition $signature -Name UEFI -Namespace Win32

# The Setup VarStore GUID from IFR: EC87D643-EBA4-4BB5-A1E5-3F3E36B20DA9
$setupGuid = "{EC87D643-EBA4-4BB5-A1E5-3F3E36B20DA9}"

# Try to read the "Setup" variable (369 bytes from IFR)
$buf = New-Object byte[] 4096
$attr = [uint32]0
$size = [Win32.UEFI]::GetFirmwareEnvironmentVariableEx("Setup", $setupGuid, $buf, 4096, [ref]$attr)
$err = [System.Runtime.InteropServices.Marshal]::GetLastWin32Error()

Write-Output "Setup variable read: size=$size, error=$err, attributes=$attr"

if ($size -gt 0) {
    Write-Output "First 64 bytes (hex):"
    $hex = ($buf[0..63] | ForEach-Object { $_.ToString("X2") }) -join " "
    Write-Output $hex
    Write-Output "Total size: $size bytes"
    
    # Save full dump
    $outPath = "C:\Users\mokke\Desktop\Gaia\data\gut\setup-nvram-dump.bin"
    [System.IO.File]::WriteAllBytes($outPath, $buf[0..($size-1)])
    Write-Output "Saved to $outPath"
} else {
    Write-Output "Could not read Setup variable (error $err)"
    
    # Try alternate GUIDs
    $guids = @(
        "{EC87D643-EBA4-4BB5-A1E5-3F3E36B20DA9}",
        "{A04A27F4-DF00-4D42-B552-39511302113D}",  # common AMI
        "{4570B7F1-ADE8-4943-8DC3-406472842F0D}",  # AMD CBS
        "{3A997502-647A-4C82-998E-52EF9ED84F5F}"   # AMD PBS
    )
    
    foreach ($g in $guids) {
        foreach ($name in @("Setup", "AmdSetup", "PchSetup", "AMITSESetup")) {
            $buf2 = New-Object byte[] 8192
            $attr2 = [uint32]0
            $sz = [Win32.UEFI]::GetFirmwareEnvironmentVariableEx($name, $g, $buf2, 8192, [ref]$attr2)
            $e = [System.Runtime.InteropServices.Marshal]::GetLastWin32Error()
            if ($sz -gt 0) {
                Write-Output "  FOUND: $name @ $g — $sz bytes, attr=$attr2"
            }
        }
    }
}
