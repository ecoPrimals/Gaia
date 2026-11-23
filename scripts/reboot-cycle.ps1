# REBOOT CYCLE — Clean reboot with reason, pre/post verification
# Pattern: snapshot → reboot → verify → ferment delta → bone

param(
    [string]$Phase = "pre"  # "pre" = prepare, "post" = verify after reboot
)

$stateDir = "c:\Users\mokke\Desktop\Gaia\data\gut"
$preState = "$stateDir\reboot-pre-state.json"
$postState = "$stateDir\reboot-post-state.json"

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class FW4 {
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

function Read-EFI {
    [FW4]::EnablePrivilege()
    $buffer = New-Object byte[] 4096
    $attr = [uint32]0
    $n = [FW4]::GetFirmwareEnvironmentVariableEx("AMD_PBS_SETUP", "{A339D746-F678-49B3-9FC7-54CE0F9DF226}", $buffer, 4096, [ref]$attr)
    if ($n -gt 0) {
        $raw = $buffer[0..($n-1)]
        return @{
            size = [int]$n
            igpu = [int]$raw[0x48]
            uma = [int]$raw[0x49]
            primary_video = [int]$raw[0x4E]
            hex48 = ("0x{0:X2}" -f $raw[0x48])
            hex49 = ("0x{0:X2}" -f $raw[0x49])
            hex4E = ("0x{0:X2}" -f $raw[0x4E])
        }
    }
    return $null
}

function Get-HardwareSnapshot {
    $gpus = @()
    Get-CimInstance Win32_VideoController | ForEach-Object {
        $gpus += @{ name=$_.Name; status=$_.Status; vram=[long]$_.AdapterRAM }
    }
    
    $nvme = @()
    Get-PnpDevice -ErrorAction SilentlyContinue | Where-Object { $_.FriendlyName -match 'NVM|Samsung|WD.*BLACK' -and $_.Class -eq 'SCSIAdapter' } | ForEach-Object {
        $present = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_IsPresent' -ErrorAction SilentlyContinue).Data
        $nvme += @{ name=$_.FriendlyName; status=$_.Status.ToString(); present=$present }
    }
    
    $cpu = Get-CimInstance Win32_Processor
    
    return @{
        gpus = $gpus
        nvme = $nvme
        cpu_cores = [int]$cpu.NumberOfCores
        cpu_threads = [int]$cpu.NumberOfLogicalProcessors
        ram_free_gb = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB, 1)
    }
}

if ($Phase -eq "pre") {
    Write-Host "=== REBOOT CYCLE — PRE-FLIGHT ==="
    Write-Host "Goal: iGPU Enable (0x48->0x01, 0x49->0x06)"
    Write-Host "Reason: Open left eye — AMD Raphael iGPU + 512MB UMA"
    
    $efi = Read-EFI
    $hw = Get-HardwareSnapshot
    
    Write-Host "`n--- Current State ---"
    Write-Host "  iGPU:  $($efi.hex48) ($(if($efi.igpu -eq 0){'DISABLED'}else{'ENABLED'}))"
    Write-Host "  UMA:   $($efi.hex49) ($(if($efi.uma -eq 0xFF){'NONE'}elseif($efi.uma -eq 0x06){'512M'}else{'?'}))"
    Write-Host "  GPUs:  $($hw.gpus.Count)"
    $hw.gpus | ForEach-Object { Write-Host "    $($_.name) [$($_.status)]" }
    Write-Host "  NVMe:  $($hw.nvme.Count)"
    $hw.nvme | ForEach-Object { Write-Host "    $($_.name) [$($_.status)] Present=$($_.present)" }
    Write-Host "  CPU:   $($hw.cpu_cores)C/$($hw.cpu_threads)T"
    Write-Host "  RAM:   $($hw.ram_free_gb) GB free"
    
    $state = @{
        phase = "pre-reboot"
        timestamp = (Get-Date -Format o)
        cycle = 2
        goal = "iGPU enable"
        efi = $efi
        hardware = $hw
    }
    $state | ConvertTo-Json -Depth 5 | Out-File $preState -Encoding utf8
    Write-Host "`n  Pre-state saved: $preState"
    
    Write-Host "`n=== REBOOT INSTRUCTIONS ==="
    Write-Host "  1. Press F4 at POST to enter boot menu"
    Write-Host "  2. Select: GAIA EFI Key - UMA Unlock"
    Write-Host "  3. At grub> prompt, type these 3 lines:"
    Write-Host ""
    Write-Host "     setup_var_cv AMD_PBS_SETUP 0x48 0x01 0x01"
    Write-Host "     setup_var_cv AMD_PBS_SETUP 0x49 0x01 0x06"
    Write-Host "     reboot"
    Write-Host ""
    Write-Host "  4. Windows boots. Run: .\scripts\reboot-cycle.ps1 -Phase post"
    Write-Host ""
    Write-Host "  READY TO REBOOT? Run: shutdown /r /t 10"
    
} elseif ($Phase -eq "post") {
    Write-Host "=== REBOOT CYCLE — POST-VERIFY ==="
    
    $efi = Read-EFI
    $hw = Get-HardwareSnapshot
    
    # Load pre-state
    $pre = $null
    if (Test-Path $preState) {
        $pre = Get-Content $preState -Raw | ConvertFrom-Json
    }
    
    Write-Host "`n--- Post-Reboot State ---"
    Write-Host "  iGPU:  $($efi.hex48) ($(if($efi.igpu -eq 1){'ENABLED ✅ CHANGED!'}elseif($efi.igpu -eq 0){'DISABLED ❌ unchanged'}else{'?'}))"
    Write-Host "  UMA:   $($efi.hex49) ($(if($efi.uma -eq 0x06){'512M ✅ CHANGED!'}elseif($efi.uma -eq 0xFF){'NONE ❌ unchanged'}else{'?'}))"
    Write-Host "  GPUs:  $($hw.gpus.Count) $(if($hw.gpus.Count -gt 2){'(NEW GPU DETECTED!)'})"
    $hw.gpus | ForEach-Object { Write-Host "    $($_.name) [$($_.status)]" }
    Write-Host "  NVMe:  $($hw.nvme.Count)"
    $hw.nvme | ForEach-Object { Write-Host "    $($_.name) [$($_.status)] Present=$($_.present)" }
    Write-Host "  CPU:   $($hw.cpu_cores)C/$($hw.cpu_threads)T $(if($hw.cpu_cores -gt 8){'(MORE CORES VISIBLE!)'})"
    
    # Delta
    if ($pre) {
        Write-Host "`n--- DELTA (what changed) ---"
        if ($efi.igpu -ne $pre.efi.igpu) { Write-Host "  iGPU: $($pre.efi.hex48) -> $($efi.hex48) ✅" }
        if ($efi.uma -ne $pre.efi.uma) { Write-Host "  UMA:  $($pre.efi.hex49) -> $($efi.hex49) ✅" }
        if ($hw.gpus.Count -ne $pre.hardware.gpus.Count) { Write-Host "  GPUs: $($pre.hardware.gpus.Count) -> $($hw.gpus.Count)" }
        if ($hw.cpu_cores -ne $pre.hardware.cpu_cores) { Write-Host "  CPU:  $($pre.hardware.cpu_cores)C -> $($hw.cpu_cores)C" }
    }
    
    # Save post-state
    $postData = @{
        phase = "post-reboot"
        timestamp = (Get-Date -Format o)
        cycle = 2
        efi = $efi
        hardware = $hw
        success = ($efi.igpu -eq 1)
    }
    $postData | ConvertTo-Json -Depth 5 | Out-File $postState -Encoding utf8
    
    # Update ferment
    $fermentPath = "$stateDir\sourdough-ferment.json"
    if (Test-Path $fermentPath) {
        $ferment = Get-Content $fermentPath -Raw | ConvertFrom-Json
        Write-Host "`n  Ferment updated with cycle 2 results"
    }
    
    if ($efi.igpu -eq 1) {
        Write-Host "`n  🎉 LEFT EYE OPEN! iGPU is alive!"
    } else {
        Write-Host "`n  ⚠️ iGPU still disabled. Try UMAF browser next."
    }
}
