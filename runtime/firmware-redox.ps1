# firmware-redox.ps1 — firmware under the redox gate.
#   Reduction (default, free): snapshot firmware setup variables, diff against the last
#     snapshot, append one line to data/spine/firmware.jsonl. Shows what a human changed in UEFI.
#   Oxidation (human only): -OneShotGrub arms the GAIA GRUB shell for the NEXT boot only
#     (firmware BootNext; normal order returns by itself). Its menu has no setup_var writes;
#     the only change it offers is entering UEFI setup at the keyboard. -Reboot fires it.
# Needs an elevated shell (SeSystemEnvironmentPrivilege).
param([switch]$OneShotGrub, [switch]$Reboot)

$ErrorActionPreference = "Stop"
$G = Split-Path $PSScriptRoot -Parent
$Snaps = "$env:LOCALAPPDATA\Gaia\firmware"
$Journal = "$G\data\spine\firmware.jsonl"
$GrubEntry = "{dce17415-e64e-11f0-bdea-10f60a5457d0}"   # GAIA EFI Key (modGRUBShell)
$Vars = @(
    @{ name = "AMD_PBS_SETUP"; guid = "{A339D746-F678-49B3-9FC7-54CE0F9DF226}" },
    # The main setup block. AMD_PBS_SETUP alone stayed "unchanged" through a UEFI unlock (Nov 24),
    # so the sense was blind to it. This one is readable from Windows too.
    @{ name = "Setup"; guid = "{EC87D643-EBA4-4BB5-A1E5-3F3E36B20DA9}" }
)

Add-Type @"
using System; using System.Runtime.InteropServices;
public class GaiaFw {
  [DllImport("kernel32.dll", SetLastError=true)] public static extern uint GetFirmwareEnvironmentVariableEx(string n, string g, [Out] byte[] b, uint s, out uint a);
  [DllImport("advapi32.dll", SetLastError=true)] static extern bool AdjustTokenPrivileges(IntPtr t, bool d, ref TP n, uint l, IntPtr p, IntPtr r);
  [DllImport("advapi32.dll", SetLastError=true)] static extern bool OpenProcessToken(IntPtr h, uint a, out IntPtr t);
  [DllImport("advapi32.dll", SetLastError=true)] static extern bool LookupPrivilegeValue(string s, string n, out LUID l);
  [DllImport("kernel32.dll")] static extern IntPtr GetCurrentProcess();
  [StructLayout(LayoutKind.Sequential)] struct LUID { public uint Lo; public int Hi; }
  [StructLayout(LayoutKind.Sequential)] struct TP { public uint C; public LUID L; public uint A; }
  public static void Priv() { IntPtr t; OpenProcessToken(GetCurrentProcess(), 0x28, out t); LUID l; LookupPrivilegeValue(null, "SeSystemEnvironmentPrivilege", out l); TP p = new TP(); p.C=1; p.L=l; p.A=2; AdjustTokenPrivileges(t,false,ref p,0,IntPtr.Zero,IntPtr.Zero); }
}
"@
[GaiaFw]::Priv()
New-Item -ItemType Directory -Force $Snaps | Out-Null

$entry = [ordered]@{ at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss"); bios = (Get-CimInstance Win32_BIOS).SMBIOSBIOSVersion; vars = @() }
foreach ($v in $Vars) {
    $buf = New-Object byte[] 8192; $attr = [uint32]0
    $n = [GaiaFw]::GetFirmwareEnvironmentVariableEx($v.name, $v.guid, $buf, 8192, [ref]$attr)
    if ($n -eq 0) { $entry.vars += [ordered]@{ name = $v.name; error = [ComponentModel.Win32Exception]::new().Message }; continue }
    $now = $buf[0..($n - 1)]
    $last = Get-ChildItem "$Snaps\$($v.name)-*.bin" -ErrorAction SilentlyContinue | Sort-Object Name | Select-Object -Last 1
    $changes = @()
    if ($last) {
        $prev = [IO.File]::ReadAllBytes($last.FullName)
        for ($i = 0; $i -lt [math]::Max($prev.Length, $now.Length); $i++) {
            $a = if ($i -lt $prev.Length) { $prev[$i] } else { $null }
            $b = if ($i -lt $now.Length) { $now[$i] } else { $null }
            if ($a -ne $b) { $changes += ("0x{0:X2}: {1} -> {2}" -f $i, ($(if ($null -eq $a) { "--" } else { "0x{0:X2}" -f $a })), ($(if ($null -eq $b) { "--" } else { "0x{0:X2}" -f $b }))) }
        }
    }
    if (-not $last -or $changes) { [IO.File]::WriteAllBytes("$Snaps\$($v.name)-$(Get-Date -Format yyyyMMdd-HHmmss).bin", $now) }
    $entry.vars += [ordered]@{ name = $v.name; size = $n; first_snapshot = (-not $last); changed = $changes }
}
Add-Content $Journal ($entry | ConvertTo-Json -Compress -Depth 5)
$entry.vars | ForEach-Object {
    if ($_.error) { "$($_.name): unreadable ($($_.error))" }
    elseif ($_.first_snapshot) { "$($_.name): first snapshot ($($_.size) bytes)" }
    elseif ($_.changed.Count) { "$($_.name): $($_.changed.Count) byte(s) changed since last snapshot"; $_.changed | ForEach-Object { "  $_" } }
    else { "$($_.name): unchanged" }
}

if ($OneShotGrub) {
    bcdedit /set '{fwbootmgr}' bootsequence $GrubEntry | Out-Null
    "GRUB armed for the next boot only; the normal boot order returns after it."
    if ($Reboot) { shutdown /r /t 10 /c "Gaia: one-shot GRUB (no firmware writes)" }
}
