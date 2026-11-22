# BUILD UEFI MODEL — Full firmware topology for reactor simulation
$model = @{
    gate = "northGate"
    timestamp = (Get-Date -Format o)
    phase = "pre-reboot-model"
}

# === 1. FULL EFI VARIABLE DUMP (AMD_PBS_SETUP) ===
Write-Host "--- Reading AMD_PBS_SETUP (256 bytes) ---"

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class FW2 {
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

[FW2]::EnablePrivilege()
$buffer = New-Object byte[] 4096
$attr = [uint32]0
$bytesRead = [FW2]::GetFirmwareEnvironmentVariableEx("AMD_PBS_SETUP", "{A339D746-F678-49B3-9FC7-54CE0F9DF226}", $buffer, 4096, [ref]$attr)

$amdPbs = @{}
if ($bytesRead -gt 0) {
    $raw = $buffer[0..($bytesRead-1)]
    $hexDump = ($raw | ForEach-Object { "0x{0:X2}" -f $_ }) -join ","
    $amdPbs = @{
        size = [int]$bytesRead
        attributes = [int]$attr
        guid = "A339D746-F678-49B3-9FC7-54CE0F9DF226"
        offsets = @{
            "0x48_iGPU_Control" = @{ value = [int]$raw[0x48]; hex = ("0x{0:X2}" -f $raw[0x48]); meaning = $(if($raw[0x48] -eq 0){"Disabled/Auto"}elseif($raw[0x48] -eq 1){"Forces (enabled)"}else{"Unknown"}) }
            "0x49_UMA_Size" = @{ value = [int]$raw[0x49]; hex = ("0x{0:X2}" -f $raw[0x49]); meaning = $(if($raw[0x49] -eq 0xFF){"Auto/None"}elseif($raw[0x49] -eq 0x06){"512M"}elseif($raw[0x49] -eq 0x04){"256M"}elseif($raw[0x49] -eq 0x08){"1024M"}else{"Unknown"}) }
            "0x4E_Primary_Video" = @{ value = [int]$raw[0x4E]; hex = ("0x{0:X2}" -f $raw[0x4E]); meaning = $(if($raw[0x4E] -eq 0x02){"PCIE"}elseif($raw[0x4E] -eq 0x01){"iGPU"}else{"Unknown"}) }
        }
        hex_full = $hexDump
    }
    Write-Host "  Size: $bytesRead bytes, Attrs: $attr"
    Write-Host ("  0x48={0:X2} 0x49={1:X2} 0x4E={2:X2}" -f $raw[0x48], $raw[0x49], $raw[0x4E])
}
$model["amd_pbs_setup"] = $amdPbs

# === 2. TRY TO READ OTHER KNOWN AMD EFI VARIABLES ===
Write-Host "`n--- Probing other EFI variables ---"
$knownVars = @(
    @{name="AMD_CBS_SETUP"; guid="{B4EF7B32-2F9B-4B0C-9B11-6C4A3E2D4E5F}"},
    @{name="Setup"; guid="{EC87D643-EBA4-4BB5-A1E5-3F3E36B20DA9}"},
    @{name="AmdSetup"; guid="{A339D746-F678-49B3-9FC7-54CE0F9DF226}"},
    @{name="PBSSetup"; guid="{A339D746-F678-49B3-9FC7-54CE0F9DF226}"},
    @{name="CbsSetupData"; guid="{B4EF7B32-2F9B-4B0C-9B11-6C4A3E2D4E5F}"},
    @{name="NBIO_PCIE_SETUP"; guid="{A339D746-F678-49B3-9FC7-54CE0F9DF226}"},
    @{name="NbioSetup"; guid="{A339D746-F678-49B3-9FC7-54CE0F9DF226}"}
)
$otherVars = @()
foreach ($v in $knownVars) {
    $b2 = New-Object byte[] 8192
    $a2 = [uint32]0
    $r2 = [FW2]::GetFirmwareEnvironmentVariableEx($v.name, "{$($v.guid)}", $b2, 8192, [ref]$a2)
    if ($r2 -gt 0) {
        $snippet = ($b2[0..([Math]::Min(63, $r2-1))] | ForEach-Object { "{0:X2}" -f $_ }) -join " "
        Write-Host ("  FOUND: {0} = {1} bytes" -f $v.name, $r2)
        $otherVars += @{ name = $v.name; guid = $v.guid; size = [int]$r2; first64 = $snippet }
    }
}
$model["other_efi_vars"] = $otherVars

# === 3. FULL BOOT ENTRY MAP ===
Write-Host "`n--- Boot Configuration ---"
$bcd = bcdedit /enum firmware 2>&1 | Out-String
$model["bcd_firmware"] = $bcd
$bcd -split "`n" | Where-Object { $_ -match "description|identifier|path|device" } | ForEach-Object { Write-Host "  $($_.Trim())" }

# === 4. EFI PARTITION FILE TREE ===
Write-Host "`n--- EFI Partition Tree ---"
mountvol Z: /S 2>$null
$efiFiles = @()
if (Test-Path Z:\) {
    Get-ChildItem Z:\ -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
        $rel = $_.FullName.Replace("Z:\", "")
        $efiFiles += @{
            path = $rel
            size = if($_.PSIsContainer) { 0 } else { [long]$_.Length }
            isDir = $_.PSIsContainer
        }
        if (-not $_.PSIsContainer -and $_.Length -gt 10000) {
            Write-Host ("  [{0,8:N0}] {1}" -f $_.Length, $rel)
        }
    }
}
$model["efi_partition"] = @{ files = $efiFiles; count = $efiFiles.Count }

# === 5. PCIe ROOT PORT MAP ===
Write-Host "`n--- PCIe Root Port Topology ---"
$pciDevs = @()
Get-PnpDevice -Class System -ErrorAction SilentlyContinue | Where-Object { $_.FriendlyName -match 'PCI Express Root Port|PCIe' } | ForEach-Object {
    $loc = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_LocationInfo' -ErrorAction SilentlyContinue).Data
    $bus = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_BusNumber' -ErrorAction SilentlyContinue).Data
    $children = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_Children' -ErrorAction SilentlyContinue).Data
    $pciDevs += @{
        name = $_.FriendlyName
        status = $_.Status.ToString()
        instanceId = $_.InstanceId
        location = $loc
        bus = $bus
        children = $children
    }
    $childStr = if($children) { $children -join ", " } else { "(none)" }
    Write-Host ("  [{0,-2}] {1} [{2}] -> {3}" -f $bus, $_.FriendlyName, $_.Status, $childStr)
}
$model["pcie_root_ports"] = $pciDevs

# === 6. STORAGE CONTROLLER MAP ===
Write-Host "`n--- Storage Controllers ---"
$storCtrls = @()
Get-PnpDevice -Class SCSIAdapter -ErrorAction SilentlyContinue | ForEach-Object {
    $present = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_IsPresent' -ErrorAction SilentlyContinue).Data
    $loc = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_LocationInfo' -ErrorAction SilentlyContinue).Data
    $bus = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_BusNumber' -ErrorAction SilentlyContinue).Data
    $storCtrls += @{
        name = $_.FriendlyName
        status = $_.Status.ToString()
        present = $present
        location = $loc
        bus = $bus
        instanceId = $_.InstanceId
    }
    Write-Host ("  [{0}] {1} Present={2} Bus={3}" -f $_.Status, $_.FriendlyName, $present, $bus)
}
$model["storage_controllers"] = $storCtrls

# === 7. MOTHERBOARD BIOS INFO ===
Write-Host "`n--- Motherboard + BIOS ---"
$bios = Get-CimInstance Win32_BIOS
$board = Get-CimInstance Win32_BaseBoard
$model["motherboard"] = @{
    manufacturer = $board.Manufacturer
    product = $board.Product
    serialNumber = $board.SerialNumber
    bios_vendor = $bios.Manufacturer
    bios_version = $bios.SMBIOSBIOSVersion
    bios_date = $bios.ReleaseDate.ToString("yyyy-MM-dd")
    smbios_version = "$($bios.SMBIOSMajorVersion).$($bios.SMBIOSMinorVersion)"
}
Write-Host ("  Board: {0} {1}" -f $board.Manufacturer, $board.Product)
Write-Host ("  BIOS: {0} v{1} ({2})" -f $bios.Manufacturer, $bios.SMBIOSBIOSVersion, $bios.ReleaseDate.ToString("yyyy-MM-dd"))

# === 8. CPU CCD/CCX TOPOLOGY ===
Write-Host "`n--- CPU Topology ---"
$cpu = Get-CimInstance Win32_Processor
$model["cpu"] = @{
    name = $cpu.Name
    cores = [int]$cpu.NumberOfCores
    logicalProcessors = [int]$cpu.NumberOfLogicalProcessors
    socket = $cpu.SocketDesignation
    maxClock = $cpu.MaxClockSpeed
    l2Cache = $cpu.L2CacheSize
    l3Cache = $cpu.L3CacheSize
}
Write-Host ("  {0}: {1}C/{2}T, L3={3}MB" -f $cpu.Name, $cpu.NumberOfCores, $cpu.NumberOfLogicalProcessors, [math]::Round($cpu.L3CacheSize/1024))

# === 9. GPU FULL DETAIL ===
Write-Host "`n--- GPU Detail ---"
$gpus = @()
Get-CimInstance Win32_VideoController | ForEach-Object {
    $gpus += @{
        name = $_.Name
        status = $_.Status
        driverVersion = $_.DriverVersion
        vram = [long]$_.AdapterRAM
        driverDate = if($_.DriverDate) { $_.DriverDate.ToString("yyyy-MM-dd") } else { "" }
        pnpDeviceId = $_.PNPDeviceID
    }
    Write-Host ("  {0} [{1}] Driver={2}" -f $_.Name, $_.Status, $_.DriverVersion)
}
$model["gpus"] = $gpus

# === 10. modGRUBShell INVESTIGATION ===
Write-Host "`n--- modGRUBShell Binary Analysis ---"
$grubPath = "Z:\EFI\tools\modGRUBShell.efi"
if (Test-Path $grubPath) {
    $grubInfo = Get-Item $grubPath
    $grubBytes = [System.IO.File]::ReadAllBytes($grubPath)
    
    # Search for "grub.cfg" string references inside the binary
    $cfgPattern = [System.Text.Encoding]::ASCII.GetBytes("grub.cfg")
    $matches = @()
    for ($i = 0; $i -lt ($grubBytes.Length - $cfgPattern.Length); $i++) {
        $found = $true
        for ($j = 0; $j -lt $cfgPattern.Length; $j++) {
            if ($grubBytes[$i + $j] -ne $cfgPattern[$j]) { $found = $false; break }
        }
        if ($found) { $matches += $i }
    }
    
    # Search for path patterns
    $pathHits = @()
    foreach ($searchStr in @("/EFI/", "/boot/grub", "/grub/", "setup_var", "normal.mod", "configfile", "(hd", "set root")) {
        $searchBytes = [System.Text.Encoding]::ASCII.GetBytes($searchStr)
        for ($i = 0; $i -lt ($grubBytes.Length - $searchBytes.Length); $i++) {
            $found = $true
            for ($j = 0; $j -lt $searchBytes.Length; $j++) {
                if ($grubBytes[$i + $j] -ne $searchBytes[$j]) { $found = $false; break }
            }
            if ($found) {
                $ctx = [System.Text.Encoding]::ASCII.GetString($grubBytes, [Math]::Max(0,$i-20), [Math]::Min(80, $grubBytes.Length - [Math]::Max(0,$i-20)))
                $ctx = $ctx -replace '[^\x20-\x7E]', '.'
                $pathHits += @{ offset = $i; pattern = $searchStr; context = $ctx }
                break
            }
        }
    }
    
    $model["modgrubshell"] = @{
        path = $grubPath
        size = [long]$grubInfo.Length
        grub_cfg_references = $matches.Count
        grub_cfg_offsets = $matches
        path_hits = $pathHits
    }
    Write-Host ("  Size: {0:N0} bytes" -f $grubInfo.Length)
    Write-Host ("  'grub.cfg' found at {0} offsets: {1}" -f $matches.Count, ($matches -join ", "))
    foreach ($h in $pathHits) {
        Write-Host ("  [{0,6}] '{1}' => {2}" -f $h.offset, $h.pattern, $h.context)
    }
}

# === SAVE MODEL ===
$json = $model | ConvertTo-Json -Depth 10
$outPath = "c:\Users\mokke\Desktop\Gaia\data\gut\uefi-mobo-model.json"
$json | Out-File $outPath -Encoding utf8
Write-Host "`n  MODEL SAVED => $outPath"

# BLAKE2b hash
$hashBytes = [System.Text.Encoding]::UTF8.GetBytes($json)
$sha = [System.Security.Cryptography.SHA256]::Create()
$hash = ($sha.ComputeHash($hashBytes) | ForEach-Object { "{0:x2}" -f $_ }) -join ""
Write-Host "  SHA256: $hash"
Write-Host "`nDone. Model ready for reactor simulation."
