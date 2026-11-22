# PLANT & FIRE — Install auto-fire EFI + plant grub.cfg everywhere + reboot
Write-Host "=== PLANT & FIRE ==="

# 1. Install auto-fire EFI
Write-Host "`n--- Installing auto-fire EFI ---"
mountvol Z: /S 2>$null
Copy-Item "c:\Users\mokke\Desktop\Gaia\data\gut\gaia-autofire.efi" "Z:\EFI\gaia\gaia-boot-wrapper.efi" -Force
Write-Host "  Replaced wrapper with auto-fire version"

# 2. Plant grub.cfg with setup_var commands EVERYWHERE
$grubCfg = @"
# GAIA iGPU Enable — auto-execute on modGRUBShell normal mode
set timeout=0

menuentry "GAIA iGPU Inject" {
    setup_var_cv AMD_PBS_SETUP 0x48 0x01 0x01
    setup_var_cv AMD_PBS_SETUP 0x49 0x01 0x06
    echo "iGPU: 0x48=0x01 (Forces), 0x49=0x06 (512M UMA)"
    echo "Rebooting to Windows..."
    sleep 2
    reboot
}
"@

# Also a flat script version (no menuentry, just commands)
$grubFlat = @"
setup_var_cv AMD_PBS_SETUP 0x48 0x01 0x01
setup_var_cv AMD_PBS_SETUP 0x49 0x01 0x06
echo "iGPU injected"
sleep 2
reboot
"@

Write-Host "`n--- Planting grub.cfg in ALL possible paths ---"
$paths = @(
    "Z:\grub.cfg",
    "Z:\boot\grub\grub.cfg",
    "Z:\boot\grub\x86_64-efi\grub.cfg",
    "Z:\EFI\tools\grub.cfg",
    "Z:\EFI\boot\grub.cfg",
    "Z:\EFI\gaia\grub.cfg",
    "Z:\grub\grub.cfg",
    "Z:\EFI\BOOT\grub\grub.cfg"
)

foreach ($p in $paths) {
    $dir = Split-Path $p -Parent
    if (-not (Test-Path $dir)) {
        New-Item -Path $dir -ItemType Directory -Force | Out-Null
    }
    # Use flat version (no menuentry) — just raw commands
    $grubFlat | Out-File $p -Encoding ascii
    Write-Host "  Planted: $p"
}

# 3. Save pre-fire state
Write-Host "`n--- Pre-fire state ---"
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class FW7 {
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
[FW7]::EnablePrivilege()
$buffer = New-Object byte[] 4096
$attr = [uint32]0
$n = [FW7]::GetFirmwareEnvironmentVariableEx("AMD_PBS_SETUP", "{A339D746-F678-49B3-9FC7-54CE0F9DF226}", $buffer, 4096, [ref]$attr)
Write-Host ("  iGPU: 0x{0:X2} (should become 0x01)" -f $buffer[0x48])
Write-Host ("  UMA:  0x{0:X2} (should become 0x06)" -f $buffer[0x49])

# 4. Set GAIA Boot Engine first
Write-Host "`n--- Setting boot order ---"
$gaiaBootId = "{dce17418-e64e-11f0-bdea-10f60a5457d0}"
bcdedit /set '{fwbootmgr}' displayorder $gaiaBootId /addfirst 2>&1 | ForEach-Object { Write-Host "  $_" }

# 5. FIRE
Write-Host "`n=== CHAIN: wrapper(auto) → modGRUBShell → grub.cfg(setup_var) → reboot → Windows ==="
Write-Host "  grub.cfg planted in 8 locations"
Write-Host "  If modGRUBShell finds ANY of them: iGPU gets enabled, auto-reboots to Windows"
Write-Host "  If NOT: drops to grub> shell (type 'normal' or 'configfile (hd0,gpt1)/EFI/tools/grub.cfg')"
Write-Host ""
Write-Host "  FIRING REBOOT IN 15 SECONDS..."

shutdown /r /t 15
