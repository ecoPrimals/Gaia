# Direct UEFI NVRAM probe — MUST run as admin
# Output goes to file since we're elevating
$outFile = "C:\Users\mokke\Desktop\Gaia\data\gut\nvram-probe-result.txt"

$adj = @'
using System;
using System.Runtime.InteropServices;

public class TokenPriv2 {
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

$signature = @'
[DllImport("kernel32.dll", SetLastError=true)]
public static extern uint GetFirmwareEnvironmentVariableEx(
    string lpName, string lpGuid, byte[] pBuffer, uint nSize, out uint pdwAttribubable);
'@

$log = @()
$log += "NVRAM Probe — $(Get-Date)"

try {
    Add-Type -TypeDefinition $adj -ErrorAction SilentlyContinue
} catch {}
$ok = [TokenPriv2]::Enable()
$log += "SeSystemEnvironmentPrivilege: $ok (LastError: $([System.Runtime.InteropServices.Marshal]::GetLastWin32Error()))"

try {
    Add-Type -MemberDefinition $signature -Name UEFI2 -Namespace Win32 -ErrorAction SilentlyContinue
} catch {}

# Scan multiple variable names and GUIDs
$guids = @(
    @("{EC87D643-EBA4-4BB5-A1E5-3F3E36B20DA9}", "IFR-Setup"),
    @("{A04A27F4-DF00-4D42-B552-39511302113D}", "AMI-Setup"),
    @("{4570B7F1-ADE8-4943-8DC3-406472842F0D}", "AMD-CBS"),
    @("{3A997502-647A-4C82-998E-52EF9ED84F5F}", "AMD-PBS"),
    @("{7B59104A-C00D-4158-87FF-F04D6396A915}", "AMI-Setup2"),
    @("{8BE4DF61-93CA-11D2-AA0D-00E098032B8C}", "EFI-Global")
)

$names = @("Setup", "AmdSetup", "PchSetup", "AMITSESetup", "CustomDefaults", "AmdCbsConfig", "AmdPbsSetup", "OCMR", "BootOrder")

foreach ($gInfo in $guids) {
    $guid = $gInfo[0]
    $label = $gInfo[1]
    foreach ($name in $names) {
        $buf = New-Object byte[] 16384
        $attr = [uint32]0
        $sz = [Win32.UEFI2]::GetFirmwareEnvironmentVariableEx($name, $guid, $buf, 16384, [ref]$attr)
        $err = [System.Runtime.InteropServices.Marshal]::GetLastWin32Error()
        if ($sz -gt 0) {
            $hex = ($buf[0..31] | ForEach-Object { $_.ToString("X2") }) -join " "
            $log += "FOUND: $name @ $label ($guid) — $sz bytes, attr=$attr"
            $log += "  First 32 bytes: $hex"
            
            # Save the dump
            $dumpPath = "C:\Users\mokke\Desktop\Gaia\data\gut\nvram-$name-$label.bin"
            [System.IO.File]::WriteAllBytes($dumpPath, $buf[0..($sz-1)])
            $log += "  Saved: $dumpPath"
        }
    }
}

$log += "`nDone."
$log | Out-File -FilePath $outFile -Encoding utf8
