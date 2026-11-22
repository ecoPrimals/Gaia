# PRE-REBOOT SNAPSHOT — Capture EXACT state for delta comparison
$snap = @{
    ts = Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"
    wave = 233
    type = "pre-reboot-snapshot"
}

# NVMe state
$nvme = @()
Get-PnpDevice | Where-Object { $_.FriendlyName -match 'NVMe|SN850X|990 PRO' } | ForEach-Object {
    $nvme += @{ id = $_.InstanceId; name = $_.FriendlyName; status = $_.Status; class = $_.Class }
}
$snap.nvme = $nvme

# CPU
$cpu = Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, ThreadCount
$snap.cpu = @{ name = $cpu.Name; cores = $cpu.NumberOfCores; threads = $cpu.NumberOfLogicalProcessors }

# GPU  
$gpus = @()
Get-CimInstance Win32_VideoController | ForEach-Object {
    $gpus += @{ name = $_.Name; ram = $_.AdapterRAM; status = $_.Status }
}
$snap.gpus = $gpus

# Physical disks
$disks = @()
Get-PhysicalDisk | ForEach-Object {
    $disks += @{ name = $_.FriendlyName; size = $_.Size; health = $_.HealthStatus; bus = $_.BusType }
}
$snap.disks = $disks

# Volumes
$vols = @()
Get-Volume | Where-Object { $_.DriveLetter } | ForEach-Object {
    $vols += @{ letter = [string]$_.DriveLetter; label = $_.FileSystemLabel; fs = $_.FileSystem; size = $_.Size }
}
$snap.volumes = $vols

# Root ports
$rps = @()
Get-PnpDevice | Where-Object { $_.FriendlyName -match 'Root Port' -and $_.InstanceId -match 'VEN_1022.*DEV_14DB' } | ForEach-Object {
    $func = $_.InstanceId -replace '.*&0&',''
    $rps += @{ func = $func; status = $_.Status; id = $_.InstanceId }
}
$snap.root_ports = $rps

# Boot entries
$boot = bcdedit /enum firmware 2>&1 | Out-String
$snap.boot_order = $boot.Substring(0, [Math]::Min($boot.Length, 1000))

# AMD_PBS_SETUP
try {
    $pbs = [System.Runtime.InteropServices.Marshal]
    # Read via .NET
    $guid = '{A339D746-F678-49B3-9FC7-54CE0F9DF226}'
    # Can't read EFI vars without P/Invoke, just note we tried
    $snap.amd_pbs = "needs-elevated-read"
} catch {
    $snap.amd_pbs = "error"
}

$outPath = "c:\Users\mokke\Desktop\Gaia\data\gut\pre-reboot-wave233.json"
$snap | ConvertTo-Json -Depth 5 | Out-File $outPath -Encoding utf8
Write-Host "PRE-REBOOT SNAPSHOT SAVED: $outPath"
Write-Host ""
Write-Host "CURRENT STATE:"
Write-Host "  CPU: $($cpu.Name) — $($cpu.NumberOfCores)C/$($cpu.NumberOfLogicalProcessors)T"
Write-Host "  NVMe: $($nvme.Count) devices ($($nvme | Where-Object { $_.status -eq 'OK' } | Measure-Object | Select-Object -ExpandProperty Count) OK, $($nvme | Where-Object { $_.status -eq 'Unknown' } | Measure-Object | Select-Object -ExpandProperty Count) Unknown)"
Write-Host "  GPUs: $(($gpus | ForEach-Object { $_.name }) -join ', ')"
Write-Host "  Disks: $(($disks | ForEach-Object { $_.name }) -join ', ')"
Write-Host "  Root Ports: $($rps.Count) ($(($rps | Where-Object { $_.status -eq 'OK' }).Count) OK, $(($rps | Where-Object { $_.status -ne 'OK' }).Count) not OK)"
Write-Host ""
Write-Host "=== REBOOT BIOS CHECKLIST ==="
Write-Host "  1. M.2 slots → ALL ENABLED"
Write-Host "  2. PCIe Gen → Auto or Gen4"
Write-Host "  3. Above 4G Decoding → ENABLED"
Write-Host "  4. Re-Size BAR → ENABLED"
Write-Host "  5. AMD CBS → CCD0+CCD1 → ENABLED"
Write-Host "  6. AMD CBS → SMT → ENABLED"
Write-Host "  7. AMD CBS → All core count → ENABLED"
Write-Host "  8. Save & Exit"
Write-Host ""
Write-Host "After boot, run: .\scripts\reboot-cycle.ps1 -Phase post"
