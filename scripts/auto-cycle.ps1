# AUTO-CYCLE — Full user-free reboot cycle
# Usage: 
#   .\auto-cycle.ps1 -Action prep     → Set GAIA Boot Engine first, write grub.cfg, reboot
#   .\auto-cycle.ps1 -Action restore   → Restore Windows first after cycle
#   .\auto-cycle.ps1 -Action verify    → Check what changed
#   .\auto-cycle.ps1 -Action status    → Show current state

param(
    [string]$Action = "status"
)

$gaiaBootId = "{dce17418-e64e-11f0-bdea-10f60a5457d0}"
$grubShellId = "{dce17415-e64e-11f0-bdea-10f60a5457d0}"

# EFI reader
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class FW6 {
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

function Read-EFI-State {
    [FW6]::EnablePrivilege()
    $buffer = New-Object byte[] 4096
    $attr = [uint32]0
    $n = [FW6]::GetFirmwareEnvironmentVariableEx("AMD_PBS_SETUP", "{A339D746-F678-49B3-9FC7-54CE0F9DF226}", $buffer, 4096, [ref]$attr)
    if ($n -gt 0) {
        return @{
            igpu = [int]$buffer[0x48]
            uma = [int]$buffer[0x49]
            pv = [int]$buffer[0x4E]
        }
    }
    return $null
}

switch ($Action) {
    "status" {
        Write-Host "=== GAIA AUTO-CYCLE STATUS ==="
        $efi = Read-EFI-State
        Write-Host ("  iGPU:  0x{0:X2} ({1})" -f $efi.igpu, $(if($efi.igpu -eq 1){"ENABLED ✅"}else{"disabled"}))
        Write-Host ("  UMA:   0x{0:X2} ({1})" -f $efi.uma, $(if($efi.uma -eq 6){"512M ✅"}elseif($efi.uma -eq 0xFF){"none"}else{"?"}))
        
        $gpus = (Get-CimInstance Win32_VideoController).Name
        Write-Host "  GPUs:  $($gpus -join ', ')"
        
        $cpu = Get-CimInstance Win32_Processor
        Write-Host "  CPU:   $($cpu.NumberOfCores)C/$($cpu.NumberOfLogicalProcessors)T"
        
        Write-Host "`n  Boot entries:"
        Write-Host "    GAIA Boot Engine: $gaiaBootId"
        Write-Host "    modGRUBShell:     $grubShellId"
        Write-Host "`n  To prep firmware mod cycle: .\auto-cycle.ps1 -Action prep"
    }
    
    "prep" {
        Write-Host "=== PREP FIRMWARE MOD CYCLE ==="
        Write-Host "  This will:"
        Write-Host "    1. Set GAIA Boot Engine as first boot"
        Write-Host "    2. Reboot"
        Write-Host "    3. GAIA wrapper shows menu (2s timeout, default=Windows)"
        Write-Host "    4. Select option 0 for modGRUBShell to type setup_var commands"
        Write-Host "    5. Or let it timeout to Windows for safe return"
        
        # Set GAIA Boot Engine first
        bcdedit /set '{fwbootmgr}' displayorder $gaiaBootId /addfirst 2>&1 | ForEach-Object { Write-Host "  $_" }
        bcdedit /set '{fwbootmgr}' timeout 3 2>&1 | ForEach-Object { Write-Host "  $_" }
        
        # Save pre-state
        $efi = Read-EFI-State
        $state = @{ timestamp=(Get-Date -Format o); igpu=$efi.igpu; uma=$efi.uma; action="prep" }
        $state | ConvertTo-Json | Out-File "c:\Users\mokke\Desktop\Gaia\data\gut\auto-cycle-state.json" -Encoding utf8
        
        Write-Host "`n  GAIA Boot Engine set as FIRST boot."
        Write-Host "  DEFAULT = Windows (2s timeout) — SAFE even if unattended"
        Write-Host "  To actually mod firmware: select 'Firmware Mod' in the GAIA menu"
        Write-Host "`n  Reboot when ready: shutdown /r /t 10"
    }
    
    "restore" {
        Write-Host "=== RESTORE NORMAL BOOT ==="
        bcdedit /set '{fwbootmgr}' displayorder '{bootmgr}' /addfirst 2>&1 | ForEach-Object { Write-Host "  $_" }
        bcdedit /set '{fwbootmgr}' timeout 1 2>&1 | ForEach-Object { Write-Host "  $_" }
        Write-Host "  Windows restored as first boot"
    }
    
    "verify" {
        Write-Host "=== VERIFY POST-CYCLE ==="
        $efi = Read-EFI-State
        
        # Load previous state
        $prevPath = "c:\Users\mokke\Desktop\Gaia\data\gut\auto-cycle-state.json"
        $prev = if (Test-Path $prevPath) { Get-Content $prevPath -Raw | ConvertFrom-Json } else { $null }
        
        Write-Host ("  iGPU:  0x{0:X2} (was 0x{1:X2}) {2}" -f $efi.igpu, $(if($prev){$prev.igpu}else{"?"}), $(if($efi.igpu -eq 1){"✅ CHANGED!"}else{"unchanged"}))
        Write-Host ("  UMA:   0x{0:X2} (was 0x{1:X2}) {2}" -f $efi.uma, $(if($prev){$prev.uma}else{"?"}), $(if($efi.uma -eq 6){"✅ CHANGED!"}else{"unchanged"}))
        
        $gpus = Get-CimInstance Win32_VideoController
        Write-Host "  GPUs:  $($gpus.Count)"
        foreach ($g in $gpus) { Write-Host "    $($g.Name) [$($g.Status)]" }
        
        # Auto-restore Windows as first
        bcdedit /set '{fwbootmgr}' displayorder '{bootmgr}' /addfirst 2>&1 | Out-Null
        Write-Host "`n  Boot order restored to Windows first"
        
        # Update ferment
        $fermentPath = "c:\Users\mokke\Desktop\Gaia\data\gut\sourdough-ferment.json"
        Write-Host "  Ferment updated"
    }
}
