# UEFI ZK POOL — Must run as Administrator
# Reads ALL firmware variables and ZK stamps them

$outFile = "c:\Users\mokke\Desktop\Gaia\data\gut\uefi-zk-output.txt"
$jsonFile = "c:\Users\mokke\Desktop\Gaia\data\gut\uefi-zk-pool.json"

Start-Transcript -Path $outFile -Force

Write-Host "=== UEFI ZK POOL — ADMIN READ ==="
Write-Host "Running as: $([System.Security.Principal.WindowsIdentity]::GetCurrent().Name)"
Write-Host "Admin: $([bool](([System.Security.Principal.WindowsPrincipal][System.Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)))"

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class FW {
    [DllImport("kernel32.dll", SetLastError=true, CharSet=CharSet.Unicode)]
    public static extern uint GetFirmwareEnvironmentVariableExW(
        string lpName, string lpGuid, byte[] pBuffer, uint nSize, out uint pdwAttrib);
}
"@

# Enable SE_SYSTEM_ENVIRONMENT_NAME privilege
$priv = @"
using System;
using System.Runtime.InteropServices;
public class TokenPriv {
    [DllImport("advapi32.dll", SetLastError=true)]
    static extern bool OpenProcessToken(IntPtr h, uint access, out IntPtr token);
    [DllImport("advapi32.dll", SetLastError=true, CharSet=CharSet.Unicode)]
    static extern bool LookupPrivilegeValue(string sys, string name, out long luid);
    [DllImport("advapi32.dll", SetLastError=true)]
    static extern bool AdjustTokenPrivileges(IntPtr token, bool disableAll, ref TokPriv1 newState, int len, IntPtr prev, IntPtr retlen);
    [StructLayout(LayoutKind.Sequential)] public struct TokPriv1 { public int Count; public long Luid; public int Attr; }
    public static bool Enable(string privilege) {
        IntPtr token;
        if (!OpenProcessToken((IntPtr)(-1), 0x0020 | 0x0008, out token)) return false;
        TokPriv1 tp; tp.Count = 1; tp.Attr = 2;
        if (!LookupPrivilegeValue(null, privilege, out tp.Luid)) return false;
        if (!AdjustTokenPrivileges(token, false, ref tp, 0, IntPtr.Zero, IntPtr.Zero)) return false;
        return Marshal.GetLastWin32Error() == 0;
    }
}
"@
Add-Type $priv
$ok = [TokenPriv]::Enable("SeSystemEnvironmentPrivilege")
Write-Host "Privilege SeSystemEnvironmentPrivilege: $ok"

function Read-EfiVar($name, $guid, $size=4096) {
    $buf = New-Object byte[] $size
    $attr = [uint32]0
    $read = [FW]::GetFirmwareEnvironmentVariableExW($name, "{$guid}", $buf, [uint32]$size, [ref]$attr)
    $err = [System.Runtime.InteropServices.Marshal]::GetLastWin32Error()
    if ($read -gt 0) {
        return @{ data = $buf[0..($read-1)]; size = $read; attr = $attr; error = 0 }
    }
    return @{ data = $null; size = 0; attr = 0; error = $err }
}

$vars = @(
    @{name="AmdSetup";         guid="A339D746-F678-49B3-9FC7-54CE0F9DF226"},
    @{name="AMD_PBS_SETUP";    guid="A339D746-F678-49B3-9FC7-54CE0F9DF226"},
    @{name="CbsSetupData";     guid="C6D4769E-7F48-4D2A-98E9-87ADCCF35CCC"},
    @{name="CBS_SETUP";        guid="C6D4769E-7F48-4D2A-98E9-87ADCCF35CCC"},
    @{name="AmdCbsConfig";     guid="C6D4769E-7F48-4D2A-98E9-87ADCCF35CCC"},
    @{name="Setup";            guid="EC87D643-EBA4-4BB5-A1E5-3F3E36B20DA9"},
    @{name="PchSetup";         guid="4570B7F1-ADE8-4943-8DC3-406472842F0D"},
    @{name="IntelSetup";       guid="4570B7F1-ADE8-4943-8DC3-406472842F0D"},
    @{name="SaSetup";          guid="72C5E28C-7783-43A1-8767-FAD73FCCAFA4"},
    @{name="NbSetup";          guid="4BAFC2B4-02DC-4104-B236-D6F1B98D1535"},
    @{name="SbSetup";          guid="4BAFC2B4-02DC-4104-B236-D6F1B98D1535"},
    @{name="OcSetup";          guid="4570B7F1-ADE8-4943-8DC3-406472842F0D"},
    @{name="AmdPbsSetup";      guid="A339D746-F678-49B3-9FC7-54CE0F9DF226"},
    @{name="PBSSetup";         guid="A339D746-F678-49B3-9FC7-54CE0F9DF226"},
    @{name="AmdCbsSetup";      guid="C6D4769E-7F48-4D2A-98E9-87ADCCF35CCC"},
    @{name="CbsConfig";        guid="C6D4769E-7F48-4D2A-98E9-87ADCCF35CCC"},
    @{name="AmdNbioSetup";     guid="4A12AF7B-7F66-4904-A349-69F0EE63C7A5"},
    @{name="NbioSetup";        guid="4A12AF7B-7F66-4904-A349-69F0EE63C7A5"},
    @{name="AmdDfSetup";       guid="B2B4B724-4F94-4F76-B0B3-5A2F3F0E5F1C"},
    @{name="FchSetup";         guid="0E96A9DA-1F6E-46B1-9A3D-D0E4F4B60830"},
    @{name="AmdSmmuSetup";     guid="4A12AF7B-7F66-4904-A349-69F0EE63C7A5"},
    @{name="AmdCpmSetup";      guid="A339D746-F678-49B3-9FC7-54CE0F9DF226"},
    @{name="Resizable BAR";    guid="EC87D643-EBA4-4BB5-A1E5-3F3E36B20DA9"},
    @{name="Above4GDecoding";  guid="EC87D643-EBA4-4BB5-A1E5-3F3E36B20DA9"}
)

Write-Host "`n--- Reading ALL firmware variables ---"
$found = @{}
foreach ($v in $vars) {
    $r = Read-EfiVar $v.name $v.guid
    if ($r.size -gt 0) {
        $hexFirst = ($r.data[0..([Math]::Min(63, $r.size-1))] | ForEach-Object { $_.ToString("X2") }) -join " "
        Write-Host "  ZK FOUND: $($v.name) ($($r.size) bytes, attr=$($r.attr))"
        Write-Host "    First 64: $hexFirst"
        $found[$v.name] = @{
            guid = $v.guid
            size = $r.size
            attr = $r.attr
            hex = ($r.data | ForEach-Object { $_.ToString("X2") }) -join ""
        }
        
        # Decode known offsets for AMD_PBS_SETUP
        if ($v.name -match "PBS" -and $r.size -ge 0x50) {
            Write-Host "    [0x48] iGPU:    0x$($r.data[0x48].ToString('X2'))"
            Write-Host "    [0x49] UMA:     0x$($r.data[0x49].ToString('X2'))"
            Write-Host "    [0x4E] Display: 0x$($r.data[0x4E].ToString('X2'))"
            # Dump all non-zero
            Write-Host "    Non-zero:"
            for ($i=0; $i -lt $r.size; $i++) {
                if ($r.data[$i] -ne 0) {
                    Write-Host "      [0x$($i.ToString('X2'))] = 0x$($r.data[$i].ToString('X2'))"
                }
            }
        }
    } else {
        Write-Host "  -- $($v.name): error $($r.error)"
    }
}

# Also try enumerating ALL variables
Write-Host "`n--- Enumerating variable names ---"
try {
    # Use bcdedit to show firmware entries as cross-reference
    $bcd = bcdedit /enum firmware 2>&1 | Select-String "description|path|device" | Out-String
    Write-Host $bcd.Substring(0, [Math]::Min(500, $bcd.Length))
} catch {}

# Save
$found | ConvertTo-Json -Depth 3 | Out-File $jsonFile -Encoding utf8
Write-Host "`nZK POOL: $jsonFile ($($found.Count) variables)"

Stop-Transcript
