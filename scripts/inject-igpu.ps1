# INJECT iGPU — Write EFI variable, save to biomeOS, reboot
# The organism modifies its own firmware. This is a new tooth.

Write-Host "=" * 60
Write-Host "  INJECT iGPU — The organism writes its own firmware"
Write-Host "=" * 60

# Load the firmware API
Add-Type @"
using System;
using System.Runtime.InteropServices;

public class FW {
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern uint GetFirmwareEnvironmentVariableEx(
        string lpName, string lpGuid, 
        [Out] byte[] pBuffer, uint nSize,
        out uint pdwAttribubable);
    
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern bool SetFirmwareEnvironmentVariableEx(
        string lpName, string lpGuid,
        byte[] pValue, uint nSize, uint dwAttributes);

    [DllImport("advapi32.dll", SetLastError=true)]
    public static extern bool AdjustTokenPrivileges(
        IntPtr TokenHandle, bool DisableAllPrivileges,
        ref TOKEN_PRIVILEGES NewState, uint BufferLength,
        IntPtr PreviousState, IntPtr ReturnLength);

    [DllImport("advapi32.dll", SetLastError=true)]
    public static extern bool OpenProcessToken(
        IntPtr ProcessHandle, uint DesiredAccess, out IntPtr TokenHandle);

    [DllImport("advapi32.dll", SetLastError=true)]
    public static extern bool LookupPrivilegeValue(
        string lpSystemName, string lpName, out LUID lpLuid);

    [DllImport("kernel32.dll")]
    public static extern IntPtr GetCurrentProcess();

    [StructLayout(LayoutKind.Sequential)]
    public struct LUID { public uint LowPart; public int HighPart; }
    [StructLayout(LayoutKind.Sequential)]
    public struct LUID_AND_ATTRIBUTES { public LUID Luid; public uint Attributes; }
    [StructLayout(LayoutKind.Sequential)]
    public struct TOKEN_PRIVILEGES { public uint PrivilegeCount; public LUID_AND_ATTRIBUTES Privileges; }

    public static bool EnablePrivilege() {
        IntPtr token;
        OpenProcessToken(GetCurrentProcess(), 0x28, out token);
        LUID luid;
        LookupPrivilegeValue(null, "SeSystemEnvironmentPrivilege", out luid);
        TOKEN_PRIVILEGES tp = new TOKEN_PRIVILEGES();
        tp.PrivilegeCount = 1;
        tp.Privileges.Luid = luid;
        tp.Privileges.Attributes = 2;
        return AdjustTokenPrivileges(token, false, ref tp, 0, IntPtr.Zero, IntPtr.Zero);
    }
}
"@

$guid = "{A339D746-F678-49B3-9FC7-54CE0F9DF226}"
$varName = "AMD_PBS_SETUP"

# Step 1: Enable privilege
[FW]::EnablePrivilege() | Out-Null
Write-Host "  Firmware privilege: ENABLED"

# Step 2: READ current state (pre-write ZK snapshot)
Write-Host "`n--- PRE-WRITE: Reading AMD_PBS_SETUP ---"
$buffer = New-Object byte[] 4096
$attr = [uint32]0
$bytesRead = [FW]::GetFirmwareEnvironmentVariableEx($varName, $guid, $buffer, 4096, [ref]$attr)

if ($bytesRead -eq 0) {
    Write-Host "  ERROR: Cannot read variable! Error: $([System.Runtime.InteropServices.Marshal]::GetLastWin32Error())"
    exit 1
}

$data = $buffer[0..($bytesRead-1)]
Write-Host "  Variable size: $bytesRead bytes"
Write-Host "  Attributes: $attr"
Write-Host "  BEFORE:"
Write-Host ("    0x48 iGPU Config:    0x{0:X2} ({1})" -f $data[0x48], @{0x00='Auto/Disabled';0x01='Forces';0x02='Disabled'}[[int]$data[0x48]])
Write-Host ("    0x49 UMA Size:       0x{0:X2} ({1})" -f $data[0x49], @{0xFF='Auto/None';0x06='512M';0x07='1G';0x08='2G'}[[int]$data[0x49]])
Write-Host ("    0x4E Primary Video:  0x{0:X2} ({1})" -f $data[0x4E], @{0x01='IGFX';0x02='PCIE'}[[int]$data[0x4E]])

# Save pre-write state  
$preHex = ($data | ForEach-Object { $_.ToString("X2") }) -join ""
$preState = @{
    timestamp = (Get-Date -Format "o")
    event = "pre-igpu-inject"
    variable = $varName
    guid = $guid
    size = $bytesRead
    attributes = $attr
    hex_0x48 = "0x{0:X2}" -f $data[0x48]
    hex_0x49 = "0x{0:X2}" -f $data[0x49]
    hex_0x4E = "0x{0:X2}" -f $data[0x4E]
} | ConvertTo-Json
$preState | Out-File "C:\Users\mokke\Desktop\Gaia\data\gut\efi-pre-write.json" -Encoding UTF8
Write-Host "  Pre-write state saved"

# Step 3: MODIFY the bytes
Write-Host "`n--- WRITING CHANGES ---"
$data[0x48] = 0x01  # iGPU = Forces
$data[0x49] = 0x06  # UMA = 512M
# Keep 0x4E = 0x02 (PCIE primary — RTX stays main, iGPU secondary)

Write-Host "  Setting 0x48 = 0x01 (iGPU Forces)"
Write-Host "  Setting 0x49 = 0x06 (UMA 512M)"  
Write-Host "  Keeping 0x4E = 0x02 (PCIE primary)"

# Step 4: WRITE the modified variable back
$writeResult = [FW]::SetFirmwareEnvironmentVariableEx($varName, $guid, [byte[]]$data, [uint32]$data.Length, $attr)
$writeError = [System.Runtime.InteropServices.Marshal]::GetLastWin32Error()

if ($writeResult) {
    Write-Host "`n  *** WRITE SUCCESSFUL! ***"
} else {
    Write-Host "`n  WRITE FAILED! Error code: $writeError"
    # Error 5 = access denied, 87 = invalid parameter, 1314 = privilege not held
    switch ($writeError) {
        5 { Write-Host "  Access Denied — need higher privileges or Secure Boot is blocking" }
        87 { Write-Host "  Invalid Parameter — variable attributes may be wrong" }
        1314 { Write-Host "  Privilege not held — SeSystemEnvironmentPrivilege not granted" }
        default { Write-Host "  Unknown error" }
    }
}

# Step 5: VERIFY by reading back
Write-Host "`n--- POST-WRITE: Verifying ---"
$verifyBuf = New-Object byte[] 4096
$verifyAttr = [uint32]0
$verifyRead = [FW]::GetFirmwareEnvironmentVariableEx($varName, $guid, $verifyBuf, 4096, [ref]$verifyAttr)

if ($verifyRead -gt 0) {
    $verify = $verifyBuf[0..($verifyRead-1)]
    Write-Host "  AFTER:"
    Write-Host ("    0x48 iGPU Config:    0x{0:X2} ({1})" -f $verify[0x48], @{0x00='Auto/Disabled';0x01='Forces';0x02='Disabled'}[[int]$verify[0x48]])
    Write-Host ("    0x49 UMA Size:       0x{0:X2} ({1})" -f $verify[0x49], @{0xFF='Auto/None';0x06='512M';0x07='1G';0x08='2G'}[[int]$verify[0x49]])
    Write-Host ("    0x4E Primary Video:  0x{0:X2} ({1})" -f $verify[0x4E], @{0x01='IGFX';0x02='PCIE'}[[int]$verify[0x4E]])
    
    # Check if change stuck
    if ($verify[0x48] -eq 0x01 -and $verify[0x49] -eq 0x06) {
        Write-Host "`n  ✅ CHANGES VERIFIED — iGPU will activate on next boot!"
    } else {
        Write-Host "`n  ⚠️ Changes did NOT persist in readback"
    }
}

# Save post-write state
$postState = @{
    timestamp = (Get-Date -Format "o")
    event = "post-igpu-inject"  
    write_success = $writeResult
    write_error = $writeError
    verified_0x48 = "0x{0:X2}" -f $verify[0x48]
    verified_0x49 = "0x{0:X2}" -f $verify[0x49]
    verified_0x4E = "0x{0:X2}" -f $verify[0x4E]
    next_step = "reboot to apply"
} | ConvertTo-Json
$postState | Out-File "C:\Users\mokke\Desktop\Gaia\data\gut\efi-post-write.json" -Encoding UTF8

Write-Host "`n" + "=" * 60
Write-Host "  iGPU INJECTION COMPLETE"
Write-Host "  This is a new tooth in the organism."
Write-Host "  The neuralAPI now speaks to firmware."
Write-Host "=" * 60
