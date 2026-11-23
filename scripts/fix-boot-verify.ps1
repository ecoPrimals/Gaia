# FIX BOOT + VERIFY — Restore normal boot, check if iGPU changed
Write-Host "=" * 60
Write-Host "  FIX BOOT + VERIFY iGPU"
Write-Host "=" * 60

# === 1. RESTORE NORMAL BOOT ORDER ===
Write-Host "`n--- Restoring Windows as first boot ---"
bcdedit /set '{fwbootmgr}' displayorder '{bootmgr}' /addfirst 2>&1 | ForEach-Object { Write-Host "  $_" }
bcdedit /set '{fwbootmgr}' timeout 1 2>&1 | ForEach-Object { Write-Host "  $_" }
Write-Host "  Windows Boot Manager restored as FIRST"

# === 2. CHECK iGPU STATE ===
Write-Host "`n--- Reading AMD_PBS_SETUP from firmware ---"

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class FWR {
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
    public static bool EnablePrivilege() {
        IntPtr token; OpenProcessToken(GetCurrentProcess(), 0x28, out token);
        LUID luid; LookupPrivilegeValue(null, "SeSystemEnvironmentPrivilege", out luid);
        TOKEN_PRIVILEGES tp = new TOKEN_PRIVILEGES(); tp.PrivilegeCount = 1; tp.Privileges.Luid = luid; tp.Privileges.Attributes = 2;
        return AdjustTokenPrivileges(token, false, ref tp, 0, IntPtr.Zero, IntPtr.Zero);
    }
}
"@

[FWR]::EnablePrivilege() | Out-Null
$buffer = New-Object byte[] 4096
$attr = [uint32]0
$bytesRead = [FWR]::GetFirmwareEnvironmentVariableEx("AMD_PBS_SETUP", "{A339D746-F678-49B3-9FC7-54CE0F9DF226}", $buffer, 4096, [ref]$attr)

if ($bytesRead -gt 0) {
    $data = $buffer[0..($bytesRead-1)]
    $val48 = $data[0x48]
    $val49 = $data[0x49]
    $val4E = $data[0x4E]
    
    Write-Host ("  0x48 iGPU: 0x{0:X2} ({1})" -f $val48, $(if($val48 -eq 0x01){"FORCES ✅ CHANGED!"}elseif($val48 -eq 0x00){"Auto/Disabled ❌ unchanged"}else{"Unknown"}))
    Write-Host ("  0x49 UMA:  0x{0:X2} ({1})" -f $val49, $(if($val49 -eq 0x06){"512M ✅ CHANGED!"}elseif($val49 -eq 0xFF){"Auto/None ❌ unchanged"}else{"Unknown"}))
    Write-Host ("  0x4E PriV: 0x{0:X2} ({1})" -f $val4E, $(if($val4E -eq 0x02){"PCIE"}else{"Other"}))
    
    if ($val48 -eq 0x01) {
        Write-Host "`n  🎉 iGPU WRITE SUCCEEDED! The left eye should be opening!"
    } else {
        Write-Host "`n  ⚠️ iGPU still disabled — GRUB didn't run setup_var_cv"
    }
} else {
    Write-Host "  Could not read firmware variable"
}

# === 3. CHECK GPU DEVICES ===
Write-Host "`n--- GPU Devices ---"
Get-CimInstance Win32_VideoController | ForEach-Object {
    Write-Host ("  " + $_.Name + " [" + $_.Status + "] VRAM=" + [math]::Round($_.AdapterRAM/1GB, 1) + "GB")
}

# === 4. CHECK DISPLAYS ===
Write-Host "`n--- Displays ---"
Get-CimInstance -Namespace root\wmi -ClassName WmiMonitorBasicDisplayParams -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host ("  " + $_.InstanceName.Substring(0, [Math]::Min(60, $_.InstanceName.Length)) + " Active=" + $_.Active)
}

# === 5. NVMe drives ===
Write-Host "`n--- NVMe Drives ---"
Get-PnpDevice | Where-Object { $_.InstanceId -match 'NVME' -and $_.Class -eq 'SCSIAdapter' } | ForEach-Object {
    Write-Host ("  " + $_.FriendlyName + " [" + $_.Status + "] Present=" + (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_IsPresent' -ErrorAction SilentlyContinue).Data)
}

# === 6. Clean up GRUB files (don't auto-inject next boot!) ===
Write-Host "`n--- Cleaning auto-inject grub.cfg ---"
mountvol Z: /S 2>$null
foreach ($f in @("Z:\EFI\tools\grub.cfg", "Z:\grub.cfg", "Z:\boot\grub\grub.cfg", "Z:\EFI\boot\grub.cfg")) {
    if (Test-Path $f) {
        Remove-Item $f -Force
        Write-Host "  Removed: $f"
    }
}
Write-Host "  Auto-inject cleaned — next boot goes straight to Windows"

Write-Host "`n" + "=" * 60
Write-Host "  VERIFY COMPLETE"
Write-Host "=" * 60
