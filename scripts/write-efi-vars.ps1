# WRITE EFI VARIABLES — Toggle iGPU from Windows, no UMAF clicking needed!
#
# Known variable from OSINT:
#   Variable: AMD_PBS_SETUP
#   GUID: {A339D746-F678-49B3-9FC7-54CE0F9DF226}
#   Offset 0x48 = iGPU Configuration (0x00=Auto, 0x01=Forces, 0x02=Disabled)
#   Offset 0x49 = UMA Frame Buffer Size (0x06=512M)
#   Offset 0x4E = Primary Video (0x01=IGFX, 0x02=PCIE)

Write-Host "=" * 60
Write-Host "  WRITE EFI VARS — Agent solves firmware directly"
Write-Host "=" * 60

# === Method 1: Try reading EFI variable via Windows API ===
Write-Host "`n--- Method 1: Windows Firmware Environment Variables ---"

Add-Type @"
using System;
using System.Runtime.InteropServices;

public class FirmwareEnv {
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
    public struct TOKEN_PRIVILEGES { 
        public uint PrivilegeCount; 
        public LUID_AND_ATTRIBUTES Privileges; 
    }

    public static bool EnablePrivilege() {
        IntPtr token;
        OpenProcessToken(GetCurrentProcess(), 0x28, out token); // TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY
        LUID luid;
        LookupPrivilegeValue(null, "SeSystemEnvironmentPrivilege", out luid);
        TOKEN_PRIVILEGES tp = new TOKEN_PRIVILEGES();
        tp.PrivilegeCount = 1;
        tp.Privileges.Luid = luid;
        tp.Privileges.Attributes = 2; // SE_PRIVILEGE_ENABLED
        return AdjustTokenPrivileges(token, false, ref tp, 0, IntPtr.Zero, IntPtr.Zero);
    }

    public static byte[] ReadVar(string name, string guid, uint size) {
        byte[] buffer = new byte[size];
        uint attr;
        uint bytesRead = GetFirmwareEnvironmentVariableEx(name, guid, buffer, size, out attr);
        if (bytesRead == 0) return null;
        byte[] result = new byte[bytesRead];
        Array.Copy(buffer, result, bytesRead);
        return result;
    }

    public static bool WriteVar(string name, string guid, byte[] data, uint attr) {
        return SetFirmwareEnvironmentVariableEx(name, guid, data, (uint)data.Length, attr);
    }
}
"@

# Enable firmware privilege
$privResult = [FirmwareEnv]::EnablePrivilege()
Write-Host "  Privilege enabled: $privResult"

# Read AMD_PBS_SETUP variable
$guid = "{A339D746-F678-49B3-9FC7-54CE0F9DF226}"
$varName = "AmdSetup"  # Try common names

$names = @("AmdSetup", "AMD_PBS_SETUP", "AmdPbsSetup", "Setup", "CbsSetup")
foreach ($name in $names) {
    $data = [FirmwareEnv]::ReadVar($name, $guid, 4096)
    if ($data) {
        Write-Host "`n  FOUND variable: $name (size: $($data.Length) bytes)"
        Write-Host "  Offset 0x48 (iGPU): 0x$([System.BitConverter]::ToString(@($data[0x48])))"
        Write-Host "  Offset 0x49 (UMA):  0x$([System.BitConverter]::ToString(@($data[0x49])))"
        Write-Host "  Offset 0x4E (PriV): 0x$([System.BitConverter]::ToString(@($data[0x4E])))"
        
        # Show hex dump around offset 0x48
        Write-Host "`n  Hex dump 0x40-0x58:"
        for ($i = 0x40; $i -lt [Math]::Min(0x58, $data.Length); $i += 16) {
            $hex = ""
            $end = [Math]::Min($i + 16, $data.Length)
            for ($j = $i; $j -lt $end; $j++) {
                $hex += $data[$j].ToString("X2") + " "
            }
            Write-Host ("    0x{0:X4}: {1}" -f $i, $hex)
        }
        break
    } else {
        $err = [System.Runtime.InteropServices.Marshal]::GetLastWin32Error()
        Write-Host "  $name : not found (error $err)"
    }
}

# Also try reading without specific GUID
Write-Host "`n--- Trying other GUIDs ---"
$guids = @(
    "{A339D746-F678-49B3-9FC7-54CE0F9DF226}",
    "{4570B7F1-ADE8-4943-8DC3-406472842F7D}",
    "{B04535E3-3004-4946-9EB7-149428983053}",
    "{C8E2EE48-3461-4546-87C0-C04AFAB42B34}"
)
foreach ($g in $guids) {
    foreach ($n in @("Setup", "AmdSetup", "PBSetup")) {
        $data = [FirmwareEnv]::ReadVar($n, $g, 4096)
        if ($data) {
            Write-Host "  FOUND: $n at GUID $g (size: $($data.Length))"
        }
    }
}

# === Method 2: Check if we can do it via modGRUBShell auto-script ===
Write-Host "`n`n--- Method 2: modGRUBShell auto-script ---"
Write-Host "  Creating startup.nsh on EFI partition..."

# Mount EFI
mountvol Z: /S 2>$null

$startupNsh = @"
@echo -off
echo "=== GAIA AUTO-CONFIGURE ==="
echo "Setting iGPU = Forces (offset 0x48 = 0x01)"
echo "Setting UMA = 512M (offset 0x49 = 0x06)"
echo "Setting Primary Video = PCIE (offset 0x4E = 0x02)"
echo ""
echo "Launching modGRUBShell..."
\EFI\tools\modGRUBShell.efi
"@

# Save the startup script
Set-Content -Path "Z:\startup.nsh" -Value $startupNsh -Encoding ASCII
Write-Host "  Created Z:\startup.nsh"

# Create a GRUB script with setup_var commands
$grubScript = @"
# GAIA iGPU Enable Script for modGRUBShell
# Run these commands in the GRUB shell:
#
# setup_var_cv AmdSetup 0x48 0x01
# setup_var_cv AmdSetup 0x49 0x06
# setup_var_cv AmdSetup 0x4E 0x02
# reboot
#
# If AmdSetup doesn't work, try:
# setup_var 0x48 0x01
# setup_var 0x49 0x06
"@
Set-Content -Path "Z:\EFI\UMAF\igpu-enable.txt" -Value $grubScript -Encoding ASCII
Write-Host "  Created Z:\EFI\UMAF\igpu-enable.txt"

# List what we have on EFI
Write-Host "`n--- EFI partition contents ---"
Get-ChildItem Z:\ -ErrorAction SilentlyContinue | ForEach-Object { Write-Host ("  " + $_.Name) }
Get-ChildItem Z:\EFI -ErrorAction SilentlyContinue | ForEach-Object { Write-Host ("  EFI\" + $_.Name) }

Write-Host "`n" + "=" * 60
Write-Host "  EFI VAR SCAN COMPLETE"
Write-Host "=" * 60
Write-Host @"

  IF Method 1 found the variable:
    → We can write it directly from Windows
    → Then normal reboot applies the change
    
  IF Method 1 failed:
    → Boot to modGRUBShell (GAIA EFI Key in boot menu)
    → Type: setup_var_cv AmdSetup 0x48 0x01
    → Type: setup_var_cv AmdSetup 0x49 0x06
    → Type: reboot
    → The shell does it, not Kevin clicking menus!
"@
