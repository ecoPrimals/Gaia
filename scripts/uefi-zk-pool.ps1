# UEFI ZK POOL — Read ALL firmware variables. Know, don't guess.
# Pool every toggle and setting we can read from Windows.

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class FirmwareEnv {
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern uint GetFirmwareEnvironmentVariableEx(
        string lpName, string lpGuid, IntPtr pBuffer, uint nSize, out uint pdwAttribubable);
    
    [DllImport("ntdll.dll")]
    public static extern int NtQuerySystemEnvironmentValueEx(
        [In] ref UNICODE_STRING VariableName, ref Guid VendorGuid,
        IntPtr Value, ref uint ValueLength, out uint Attributes);
    
    [StructLayout(LayoutKind.Sequential)]
    public struct UNICODE_STRING {
        public ushort Length;
        public ushort MaximumLength;
        public IntPtr Buffer;
    }
    
    public static byte[] ReadVar(string name, string guid, int size) {
        IntPtr buf = Marshal.AllocHGlobal(size);
        try {
            uint attr;
            uint read = GetFirmwareEnvironmentVariableEx(name, "{" + guid + "}", buf, (uint)size, out attr);
            if (read == 0) return null;
            byte[] data = new byte[read];
            Marshal.Copy(buf, data, 0, (int)read);
            return data;
        } finally {
            Marshal.FreeHGlobal(buf);
        }
    }
}
"@

# Enable privilege
$processToken = [System.Diagnostics.Process]::GetCurrentProcess().Handle
$TOKEN_ADJUST_PRIVILEGES = 0x20
$TOKEN_QUERY = 0x8
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Priv {
    [DllImport("advapi32.dll", SetLastError=true)]
    public static extern bool OpenProcessToken(IntPtr ProcessHandle, uint DesiredAccess, out IntPtr TokenHandle);
    [DllImport("advapi32.dll", SetLastError=true)]
    public static extern bool LookupPrivilegeValue(string lpSystemName, string lpName, out long lpLuid);
    [DllImport("advapi32.dll", SetLastError=true)]
    public static extern bool AdjustTokenPrivileges(IntPtr TokenHandle, bool DisableAllPrivileges,
        ref TOKEN_PRIVILEGES NewState, uint BufferLength, IntPtr PreviousState, IntPtr ReturnLength);
    [StructLayout(LayoutKind.Sequential)]
    public struct TOKEN_PRIVILEGES {
        public uint PrivilegeCount;
        public long Luid;
        public uint Attributes;
    }
    public static bool Enable(string priv) {
        IntPtr token;
        if (!OpenProcessToken((IntPtr)(-1), 0x28, out token)) return false;
        TOKEN_PRIVILEGES tp = new TOKEN_PRIVILEGES();
        tp.PrivilegeCount = 1;
        tp.Attributes = 2;
        if (!LookupPrivilegeValue(null, priv, out tp.Luid)) return false;
        return AdjustTokenPrivileges(token, false, ref tp, 0, IntPtr.Zero, IntPtr.Zero);
    }
}
"@
[Priv]::Enable("SeSystemEnvironmentPrivilege") | Out-Null

Write-Host "=== UEFI ZK POOL — READ ALL SETTINGS ===`n"

$pool = @{}

# Known UEFI variable GUIDs for ASUS/AMD boards
$guids = @{
    "AMD_PBS_SETUP"     = "A339D746-F678-49B3-9FC7-54CE0F9DF226"
    "CBS_SETUP"         = "C6D4769E-7F48-4D2A-98E9-87ADCCF35CCC"  # AMD CBS
    "SETUP"             = "EC87D643-EBA4-4BB5-A1E5-3F3E36B20DA9"  # AMI Setup
    "AMI_SETUP"         = "A04A27F4-DF00-4D42-B552-39511302113D"  # AMI
    "NBIO_SETUP"        = "4A12AF7B-7F66-4904-A349-69F0EE63C7A5"  # AMD NBIO
    "FCH_SETUP"         = "0E96A9DA-1F6E-46B1-9A3D-D0E4F4B60830"  # AMD FCH
    "PCIE_SETUP"        = "3D3DD48D-E5D7-4AEA-9C1B-D2ED4A4AB40A"  # PCIe
    "CCD_SETUP"         = "72E20C60-C3F3-42D7-B0C4-2C6E6D83C319"  # CCD
    "SMU_SETUP"         = "4B766C83-3A3F-4C8A-BC9D-E6F2C7BDFB32"  # SMU
    "DF_SETUP"          = "B2B4B724-4F94-4F76-B0B3-5A2F3F0E5F1C"  # Data Fabric
    "CPPC_SETUP"        = "9B1FC62F-5D53-4B81-958D-EFF7BD41E3D0"  # CPPC
    "GLOBAL_SETUP"      = "4570B7F1-ADE8-4943-8DC3-406472842F0D"  # Global
    "CUSTOM_DEFAULTS"   = "4599D26F-1A11-49B8-B91F-858745CFF824"
    "ASUS_SETUP"        = "4BAFC2B4-02DC-4104-B236-D6F1B98D1535"  # ASUS specific
    "OC_SETUP"          = "C8411D47-7E7B-4E3D-AA88-33C7DAA20C8D"  # Overclocking
}

Write-Host "--- Reading UEFI Variables ---"
foreach ($name in ($guids.Keys | Sort-Object)) {
    $guid = $guids[$name]
    $data = [FirmwareEnv]::ReadVar($name, $guid, 4096)
    if ($data) {
        $hex = ($data | ForEach-Object { $_.ToString("X2") }) -join " "
        $hexShort = if ($hex.Length -gt 120) { $hex.Substring(0, 120) + "..." } else { $hex }
        Write-Host "  ZK $name ($($data.Length) bytes): $hexShort"
        $pool[$name] = @{
            guid = $guid
            size = $data.Length
            hex = ($data | ForEach-Object { $_.ToString("X2") }) -join ""
            first32 = ($data[0..31] | ForEach-Object { $_.ToString("X2") }) -join " "
        }
    } else {
        $err = [System.Runtime.InteropServices.Marshal]::GetLastWin32Error()
        Write-Host "  -- $name : not found (error $err)"
    }
}

# Read AMD_PBS_SETUP specifically and decode known offsets
Write-Host "`n--- AMD_PBS_SETUP Decoded ---"
$pbs = [FirmwareEnv]::ReadVar("AMD_PBS_SETUP", $guids["AMD_PBS_SETUP"], 4096)
if ($pbs) {
    Write-Host "  Size: $($pbs.Length) bytes"
    Write-Host "  [0x48] iGPU Control:     0x$($pbs[0x48].ToString('X2')) $(if($pbs[0x48] -eq 0){'DISABLED'}elseif($pbs[0x48] -eq 1){'ENABLED'}else{'UNKNOWN'})"
    Write-Host "  [0x49] UMA Frame Size:   0x$($pbs[0x49].ToString('X2')) $(if($pbs[0x49] -eq 0xFF){'None/Auto'}elseif($pbs[0x49] -eq 6){'512MB'}else{'other'})"
    Write-Host "  [0x4E] Primary Display:  0x$($pbs[0x4E].ToString('X2')) $(if($pbs[0x4E] -eq 2){'PCIE'}elseif($pbs[0x4E] -eq 0){'iGPU'}else{'other'})"
    
    # Dump ALL non-zero bytes with offsets
    Write-Host "`n  Non-zero offsets:"
    for ($i = 0; $i -lt $pbs.Length; $i++) {
        if ($pbs[$i] -ne 0) {
            Write-Host "    [0x$($i.ToString('X2'))] = 0x$($pbs[$i].ToString('X2')) ($($pbs[$i]))"
        }
    }
}

# Read Setup
Write-Host "`n--- SETUP Variable ---"
$setup = [FirmwareEnv]::ReadVar("Setup", $guids["SETUP"], 8192)
if ($setup) {
    Write-Host "  Size: $($setup.Length) bytes"
    # Look for PCIe/NVMe related offsets (common patterns)
    Write-Host "  First 64 bytes: $(($setup[0..63] | ForEach-Object { $_.ToString('X2') }) -join ' ')"
} else {
    # Try alternate name
    $setup = [FirmwareEnv]::ReadVar("Setup", "EC87D643-EBA4-4BB5-A1E5-3F3E36B20DA9", 8192)
    if ($setup) { Write-Host "  Size: $($setup.Length) bytes (alt GUID)" }
    else { Write-Host "  Not readable" }
}

# Save the ZK pool
$outPath = "c:\Users\mokke\Desktop\Gaia\data\gut\uefi-zk-pool.json"
$poolJson = $pool | ConvertTo-Json -Depth 3
$poolJson | Out-File $outPath -Encoding utf8
Write-Host "`nZK POOL SAVED: $outPath"
Write-Host "Variables found: $($pool.Count)"
Write-Host "`n=== WE ZK KNOW, NOT ASSUME ==="
