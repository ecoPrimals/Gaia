# UEFI ZK POOL v2 — Fixed privilege elevation
$outFile = "c:\Users\mokke\Desktop\Gaia\data\gut\uefi-zk-output.txt"
$jsonFile = "c:\Users\mokke\Desktop\Gaia\data\gut\uefi-zk-pool.json"
Start-Transcript -Path $outFile -Force

Write-Host "=== UEFI ZK POOL v2 ==="

Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Diagnostics;

public class EfiReader {
    [DllImport("kernel32.dll", SetLastError=true, CharSet=CharSet.Unicode)]
    public static extern uint GetFirmwareEnvironmentVariableExW(
        string lpName, string lpGuid, byte[] pBuffer, uint nSize, out uint pdwAttrib);

    [DllImport("advapi32.dll", SetLastError=true)]
    static extern bool OpenProcessToken(IntPtr ProcessHandle, uint DesiredAccess, out IntPtr TokenHandle);

    [DllImport("advapi32.dll", SetLastError=true, CharSet=CharSet.Unicode)]
    static extern bool LookupPrivilegeValue(string lpSystemName, string lpName, out long lpLuid);

    [DllImport("advapi32.dll", SetLastError=true)]
    static extern bool AdjustTokenPrivileges(IntPtr TokenHandle, bool DisableAll,
        ref TOKEN_PRIVILEGES NewState, uint BufferLength, IntPtr PreviousState, IntPtr ReturnLength);

    [DllImport("kernel32.dll")]
    static extern IntPtr GetCurrentProcess();

    [StructLayout(LayoutKind.Sequential)]
    struct TOKEN_PRIVILEGES {
        public uint PrivilegeCount;
        public long Luid;
        public uint Attributes;
    }

    public static bool EnablePrivilege() {
        IntPtr hProcess = GetCurrentProcess();
        IntPtr hToken;
        if (!OpenProcessToken(hProcess, 0x0020 | 0x0008, out hToken)) {
            Console.WriteLine("OpenProcessToken failed: " + Marshal.GetLastWin32Error());
            return false;
        }
        TOKEN_PRIVILEGES tp = new TOKEN_PRIVILEGES();
        tp.PrivilegeCount = 1;
        tp.Attributes = 2; // SE_PRIVILEGE_ENABLED
        if (!LookupPrivilegeValue(null, "SeSystemEnvironmentPrivilege", out tp.Luid)) {
            Console.WriteLine("LookupPrivilegeValue failed: " + Marshal.GetLastWin32Error());
            return false;
        }
        if (!AdjustTokenPrivileges(hToken, false, ref tp, 0, IntPtr.Zero, IntPtr.Zero)) {
            Console.WriteLine("AdjustTokenPrivileges failed: " + Marshal.GetLastWin32Error());
            return false;
        }
        int lastErr = Marshal.GetLastWin32Error();
        Console.WriteLine("AdjustTokenPrivileges lastError: " + lastErr);
        return lastErr == 0;
    }

    public static byte[] ReadVariable(string name, string guid) {
        byte[] buffer = new byte[4096];
        uint attr;
        uint bytesRead = GetFirmwareEnvironmentVariableExW(name, "{" + guid + "}", buffer, 4096, out attr);
        if (bytesRead == 0) return null;
        byte[] result = new byte[bytesRead];
        Array.Copy(buffer, result, bytesRead);
        return result;
    }
}
"@

$privOk = [EfiReader]::EnablePrivilege()
Write-Host "Privilege enabled: $privOk"

# Check privileges
whoami /priv | Select-String "SeSystem"

# Now try reading
$varNames = @(
    @("AmdSetup",       "A339D746-F678-49B3-9FC7-54CE0F9DF226"),
    @("AMD_PBS_SETUP",  "A339D746-F678-49B3-9FC7-54CE0F9DF226"),
    @("AmdPbsSetup",   "A339D746-F678-49B3-9FC7-54CE0F9DF226"),
    @("PBSSetup",      "A339D746-F678-49B3-9FC7-54CE0F9DF226"),
    @("AmdCpmSetup",   "A339D746-F678-49B3-9FC7-54CE0F9DF226"),
    @("CbsSetupData",  "C6D4769E-7F48-4D2A-98E9-87ADCCF35CCC"),
    @("CBS_SETUP",     "C6D4769E-7F48-4D2A-98E9-87ADCCF35CCC"),
    @("AmdCbsConfig",  "C6D4769E-7F48-4D2A-98E9-87ADCCF35CCC"),
    @("AmdCbsSetup",   "C6D4769E-7F48-4D2A-98E9-87ADCCF35CCC"),
    @("CbsConfig",     "C6D4769E-7F48-4D2A-98E9-87ADCCF35CCC"),
    @("Setup",         "EC87D643-EBA4-4BB5-A1E5-3F3E36B20DA9"),
    @("AmdNbioSetup",  "4A12AF7B-7F66-4904-A349-69F0EE63C7A5"),
    @("FchSetup",      "0E96A9DA-1F6E-46B1-9A3D-D0E4F4B60830")
)

$pool = @{}
Write-Host "`n--- Reading firmware variables ---"
foreach ($v in $varNames) {
    $name = $v[0]
    $guid = $v[1]
    $data = [EfiReader]::ReadVariable($name, $guid)
    if ($data) {
        $hexFirst = ($data[0..([Math]::Min(63,$data.Length-1))] | ForEach-Object { $_.ToString("X2") }) -join " "
        Write-Host "ZK FOUND: $name ($($data.Length) bytes)"
        Write-Host "  First64: $hexFirst"
        
        $pool[$name] = @{
            guid = $guid
            size = $data.Length
            hex = ($data | ForEach-Object { $_.ToString("X2") }) -join ""
        }
        
        # Decode PBS if found
        if ($name -match "PBS" -and $data.Length -ge 0x50) {
            Write-Host "  [0x48] iGPU:    0x$($data[0x48].ToString('X2'))"
            Write-Host "  [0x49] UMA:     0x$($data[0x49].ToString('X2'))"
            Write-Host "  [0x4E] Display: 0x$($data[0x4E].ToString('X2'))"
            Write-Host "  All non-zero:"
            for ($i=0; $i -lt $data.Length; $i++) {
                if ($data[$i] -ne 0) {
                    Write-Host "    [0x$($i.ToString('X2'))] = 0x$($data[$i].ToString('X2')) ($($data[$i]))"
                }
            }
        }
    } else {
        $err = [Runtime.InteropServices.Marshal]::GetLastWin32Error()
        Write-Host "-- $name : error $err"
    }
}

$pool | ConvertTo-Json -Depth 3 | Out-File $jsonFile -Encoding utf8
Write-Host "`nZK POOL: $($pool.Count) variables found"
Stop-Transcript
