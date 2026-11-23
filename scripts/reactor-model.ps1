# REACTOR MODEL — Fast UEFI model for simulation before reboot
# Phase: Model → Simulate → Plan → Reboot (with clean goal)

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class FW3 {
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

[FW3]::EnablePrivilege()

$model = @{
    gate = "northGate"
    timestamp = (Get-Date -Format o)
    phase = "reactor-model"
}

# === 1. AMD_PBS_SETUP full dump ===
Write-Host "=== AMD_PBS_SETUP (256 bytes) ==="
$buffer = New-Object byte[] 4096
$attr = [uint32]0
$n = [FW3]::GetFirmwareEnvironmentVariableEx("AMD_PBS_SETUP", "{A339D746-F678-49B3-9FC7-54CE0F9DF226}", $buffer, 4096, [ref]$attr)
$raw = $buffer[0..($n-1)]

$hexRows = @()
for ($i = 0; $i -lt $n; $i += 16) {
    $chunk = $raw[$i..([Math]::Min($i+15, $n-1))]
    $hex = ($chunk | ForEach-Object { "{0:X2}" -f $_ }) -join " "
    $ascii = ($chunk | ForEach-Object { if ($_ -ge 0x20 -and $_ -le 0x7E) { [char]$_ } else { '.' } }) -join ''
    $hexRows += ("{0:X4}: {1,-48} {2}" -f $i, $hex, $ascii)
    Write-Host ("{0:X4}: {1,-48} {2}" -f $i, $hex, $ascii)
}

$knownOffsets = @{
    "0x48" = @{ name="iGPU_Control"; current=[int]$raw[0x48]; target=0x01; meanings=@{0="Disabled/Auto";1="Forces (enabled)"} }
    "0x49" = @{ name="UMA_Frame_Size"; current=[int]$raw[0x49]; target=0x06; meanings=@{0xFF="Auto/None";0x02="128M";0x04="256M";0x06="512M";0x08="1024M";0x0A="2048M"} }
    "0x4A" = @{ name="UMA_Above4G"; current=[int]$raw[0x4A]; target=$null; meanings=@{} }
    "0x4B" = @{ name="NB_Azalia"; current=[int]$raw[0x4B]; target=$null; meanings=@{} }
    "0x4C" = @{ name="Unknown_4C"; current=[int]$raw[0x4C]; target=$null; meanings=@{} }
    "0x4D" = @{ name="Unknown_4D"; current=[int]$raw[0x4D]; target=$null; meanings=@{} }
    "0x4E" = @{ name="Primary_Video"; current=[int]$raw[0x4E]; target=0x02; meanings=@{0x01="iGPU";0x02="PCIE"} }
}

Write-Host "`n=== Known Offsets ==="
foreach ($k in $knownOffsets.Keys | Sort-Object) {
    $o = $knownOffsets[$k]
    $curMeaning = if ($o.meanings.ContainsKey($o.current)) { $o.meanings[$o.current] } else { "?" }
    $tgtStr = if ($null -ne $o.target) { ("-> 0x{0:X2}" -f $o.target) } else { "(keep)" }
    Write-Host ("  {0} {1}: 0x{2:X2} ({3}) {4}" -f $k, $o.name, $o.current, $curMeaning, $tgtStr)
}

$model["amd_pbs_setup"] = @{
    size = [int]$n
    attributes = [int]$attr
    hex_dump = $hexRows
    known_offsets = $knownOffsets
    raw_hex = ($raw | ForEach-Object { "{0:X2}" -f $_ }) -join ""
}

# === 2. PCIe Root Ports (compact) ===
Write-Host "`n=== PCIe Root Port Topology ==="
$ports = @()
$rpIdx = 0
Get-PnpDevice -Class System -ErrorAction SilentlyContinue | Where-Object { $_.FriendlyName -match 'PCI Express Root Port' } | ForEach-Object {
    $rpIdx++
    $id = $_.InstanceId
    $status = $_.Status.ToString()
    $children = (Get-PnpDeviceProperty -InstanceId $id -KeyName 'DEVPKEY_Device_Children' -ErrorAction SilentlyContinue).Data
    $loc = (Get-PnpDeviceProperty -InstanceId $id -KeyName 'DEVPKEY_Device_LocationInfo' -ErrorAction SilentlyContinue).Data
    
    $childInfo = @()
    if ($children) {
        foreach ($c in $children) {
            $cDev = Get-PnpDevice -InstanceId $c -ErrorAction SilentlyContinue
            $childInfo += @{ id = $c; name = $cDev.FriendlyName; status = $cDev.Status.ToString() }
        }
    }
    
    $idShort = if ($id -match 'DEV_(\w+)') { $Matches[1] } else { $id.Substring(0, [Math]::Min(30, $id.Length)) }
    Write-Host ("  RP{0:D2} [{1}] DEV_{2} loc={3}" -f $rpIdx, $status, $idShort, $loc)
    foreach ($ci in $childInfo) {
        Write-Host ("    -> {0} [{1}]" -f $ci.name, $ci.status)
    }
    
    $ports += @{
        index = $rpIdx
        status = $status
        instanceId = $id
        location = $loc
        children = $childInfo
    }
}
$model["pcie_root_ports"] = $ports

# === 3. NVMe search (PCI device tree) ===
Write-Host "`n=== NVMe / Storage PCI Devices ==="
$nvme = @()
Get-PnpDevice -ErrorAction SilentlyContinue | Where-Object { $_.InstanceId -match 'NVME|144D|1C5C|15B7' -or $_.FriendlyName -match 'NVM|Samsung|WD|SSD' } | ForEach-Object {
    $present = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_IsPresent' -ErrorAction SilentlyContinue).Data
    $parent = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_Parent' -ErrorAction SilentlyContinue).Data
    $loc = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_LocationInfo' -ErrorAction SilentlyContinue).Data
    Write-Host ("  [{0,-7}] {1} Present={2} @ {3}" -f $_.Status, $_.FriendlyName, $present, $loc)
    $nvme += @{ name=$_.FriendlyName; status=$_.Status.ToString(); present=$present; parent=$parent; location=$loc; id=$_.InstanceId }
}
$model["nvme_devices"] = $nvme

# === 4. modGRUBShell string search (fast: use findstr on file) ===
Write-Host "`n=== modGRUBShell grub.cfg references ==="
mountvol Z: /S 2>$null
$grubEfi = "Z:\EFI\tools\modGRUBShell.efi"
if (Test-Path $grubEfi) {
    $sz = (Get-Item $grubEfi).Length
    Write-Host "  Size: $sz bytes"
    
    # Use strings-like approach: extract ASCII strings > 4 chars
    $bytes = [System.IO.File]::ReadAllBytes($grubEfi)
    $strings = @()
    $current = ""
    foreach ($b in $bytes) {
        if ($b -ge 0x20 -and $b -le 0x7E) {
            $current += [char]$b
        } else {
            if ($current.Length -ge 6) { $strings += $current }
            $current = ""
        }
    }
    if ($current.Length -ge 6) { $strings += $current }
    
    # Filter for interesting keywords
    $keywords = @("grub.cfg", "/boot/", "/EFI/", "configfile", "normal", "setup_var", "set root", "prefix", "(hd", "fs0:", "chain")
    $hits = @()
    foreach ($s in $strings) {
        foreach ($kw in $keywords) {
            if ($s -like "*$kw*") {
                $hits += $s
                break
            }
        }
    }
    
    Write-Host "  Strings containing keywords ($($hits.Count) hits):"
    $uniqueHits = $hits | Select-Object -Unique
    foreach ($h in $uniqueHits) {
        $trimmed = if ($h.Length -gt 120) { $h.Substring(0, 120) + "..." } else { $h }
        Write-Host "    $trimmed"
    }
    $model["modgrubshell"] = @{
        size = [long]$sz
        keyword_strings = $uniqueHits
        total_strings = $strings.Count
    }
} else {
    Write-Host "  NOT FOUND at $grubEfi"
}

# === 5. Board details ===
Write-Host "`n=== Motherboard ==="
$board = Get-CimInstance Win32_BaseBoard
$bios = Get-CimInstance Win32_BIOS
Write-Host ("  {0} {1} BIOS={2} ({3})" -f $board.Manufacturer, $board.Product, $bios.SMBIOSBIOSVersion, $bios.ReleaseDate.ToString("yyyy-MM-dd"))
$model["motherboard"] = @{
    manufacturer = $board.Manufacturer; product = $board.Product
    bios_version = $bios.SMBIOSBIOSVersion; bios_date = $bios.ReleaseDate.ToString("yyyy-MM-dd")
    chipset = "AMD X870E"; socket = "AM5"
}

# === 6. CPU (CCD visibility check) ===
Write-Host "`n=== CPU ==="
$cpu = Get-CimInstance Win32_Processor
Write-Host ("  {0}: {1}C/{2}T L2={3}KB L3={4}KB" -f $cpu.Name, $cpu.NumberOfCores, $cpu.NumberOfLogicalProcessors, $cpu.L2CacheSize, $cpu.L3CacheSize)
$model["cpu"] = @{
    name=$cpu.Name; cores=[int]$cpu.NumberOfCores; threads=[int]$cpu.NumberOfLogicalProcessors
    l2=$cpu.L2CacheSize; l3=$cpu.L3CacheSize
    note="9950X3D has 2 CCDs: CCD0 (8C/16T + 3D V-Cache 96MB L3) and CCD1 (8C/16T + 32MB L3). Showing 8C/8T means only CCD0 visible or SMT disabled."
}

# === 7. Boot entries ===
Write-Host "`n=== Boot Entries ==="
$bootOrder = bcdedit /enum firmware 2>&1 | Out-String
$entries = @()
$bootOrder -split "(?=Windows Boot Manager|Firmware Application)" | ForEach-Object {
    if ($_ -match "identifier\s+(\{[^\}]+\})") { $ident = $Matches[1] }
    if ($_ -match "description\s+(.+)") { $desc = $Matches[1].Trim() }
    if ($_ -match "path\s+(.+)") { $path = $Matches[1].Trim() }
    if ($ident -and $desc) {
        $entries += @{ id=$ident; desc=$desc; path=$path }
        Write-Host ("  {0}: {1}" -f $ident, $desc)
        $ident = $null; $desc = $null; $path = $null
    }
}
$model["boot_entries"] = $entries

# === SIMULATION: What would change per goal ===
Write-Host "`n" + "=" * 60
Write-Host "=== REACTOR SIMULATION ==="
Write-Host "=" * 60

Write-Host "`n--- GOAL A: Enable iGPU (left eye) ---"
Write-Host "  Writes needed:"
Write-Host "    setup_var_cv AMD_PBS_SETUP 0x48 0x01  (Disabled->Forces)"
Write-Host "    setup_var_cv AMD_PBS_SETUP 0x49 0x06  (None->512M UMA)"
Write-Host "  Expected: AMD Raphael iGPU appears as 2nd GPU, 512MB VRAM from system RAM"
Write-Host "  Risk: LOW — iGPU is built into 9950X3D die, just needs enabling"
Write-Host "  Verify: After reboot, Device Manager shows AMD Radeon Graphics"

Write-Host "`n--- GOAL B: Wake 4TB NVMe drives ---"
Write-Host "  Root cause: 2 PCIe Root Ports in UNKNOWN state"
$unknownPorts = $ports | Where-Object { $_.status -eq "Unknown" }
Write-Host "    $($unknownPorts.Count) unknown root ports found"
Write-Host "  Possible fixes:"
Write-Host "    1. NBIO PCIe bifurcation settings (CBS_SETUP variable)"
Write-Host "    2. PCIe slot configuration in UMAF (manual)"
Write-Host "    3. M.2 slot enable/disable in AMD CBS"
Write-Host "  Risk: MEDIUM — PCIe lane allocation affects all devices"
Write-Host "  Need: Find CBS_SETUP variable offsets for M.2 slot config"

Write-Host "`n--- GOAL C: Fix CCD visibility (8C->16C) ---"
Write-Host "  Current: 8C/8T visible (should be 16C/32T)"
Write-Host "  Possible: CCD1 disabled in BIOS, or SMT off + CCD1 off"
Write-Host "  Fix: AMD CBS -> CPU settings -> enable both CCDs + SMT"
Write-Host "  Risk: LOW — just BIOS toggle"

Write-Host "`n--- REBOOT PLAN ---"
Write-Host "  Tool: F4 boot menu -> 'GAIA EFI Key - UMA Unlock'"
Write-Host "  Action: Type 3 commands in modGRUBShell:"
Write-Host "    setup_var_cv AMD_PBS_SETUP 0x48 0x01"
Write-Host "    setup_var_cv AMD_PBS_SETUP 0x49 0x06"
Write-Host "    reboot"
Write-Host "  Fallback: F4 -> 'Smokeless UMAF (iGPU)' for manual browse"
Write-Host "  After: Agent verifies via EFI variable read + device scan"

# === SAVE ===
$json = $model | ConvertTo-Json -Depth 10
$outPath = "c:\Users\mokke\Desktop\Gaia\data\gut\uefi-reactor-model.json"
$json | Out-File $outPath -Encoding utf8
Write-Host "`n  MODEL => $outPath"

# Create the exact GRUB commands file for Kevin to paste
$cmdsPath = "c:\Users\mokke\Desktop\Gaia\data\gut\grub-commands.txt"
@"
# === GAIA REBOOT CYCLE 2 — iGPU Enable ===
# Boot: F4 -> GAIA EFI Key -> type these 3 lines:

setup_var_cv AMD_PBS_SETUP 0x48 0x01
setup_var_cv AMD_PBS_SETUP 0x49 0x06
reboot

# After Windows boots: agent verifies 0x48=0x01, 0x49=0x06
# Expected: AMD iGPU appears in Device Manager
"@ | Out-File $cmdsPath -Encoding utf8
Write-Host "  COMMANDS => $cmdsPath"

Write-Host "`nReactor model complete. Ready to simulate or reboot."
