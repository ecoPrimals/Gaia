# shadowcast-check.ps1 — Run after each reboot to check alignment state
# Part of the 3-cycle shadowcast learning sequence
# Usage: powershell -ExecutionPolicy Bypass -File shadowcast-check.ps1

$cycleFile = "$PSScriptRoot\shadowcast-cycles.log"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Write-Host ""
Write-Host "=== SHADOWCAST ALIGNMENT CHECK ===" -ForegroundColor Cyan
Write-Host "  $timestamp" -ForegroundColor DarkGray
Write-Host ""

# Count boot cycle
if (Test-Path $cycleFile) {
    $lines = (Get-Content $cycleFile | Measure-Object -Line).Lines
    $cycle = $lines
} else {
    $cycle = 0
}

Write-Host "  REBOOT CYCLE: $cycle / 3" -ForegroundColor Yellow
Write-Host ""

# GPU STATUS
Write-Host "--- GPU STATUS ---" -ForegroundColor Green
$gpus = Get-PnpDevice -Class Display
foreach ($gpu in $gpus) {
    $color = if ($gpu.Status -eq "OK") { "Green" } elseif ($gpu.Status -eq "Error") { "Red" } else { "Yellow" }
    Write-Host "  $($gpu.FriendlyName): $($gpu.Status)" -ForegroundColor $color
}
Write-Host ""

# DISPLAY OUTPUTS
Write-Host "--- ACTIVE DISPLAYS ---" -ForegroundColor Green
Add-Type -AssemblyName System.Windows.Forms
$screens = [System.Windows.Forms.Screen]::AllScreens
foreach ($s in $screens) {
    $eye = if ($s.Primary) { "RIGHT EYE (Apollo)" } else { "LEFT EYE (Luna)" }
    Write-Host "  $($s.DeviceName): $($s.Bounds.Width)x$($s.Bounds.Height) — $eye" -ForegroundColor White
}
Write-Host ""

# MONITOR IDENTIFICATION
Write-Host "--- MONITORS ---" -ForegroundColor Green
try {
    $monitors = Get-CimInstance -Namespace root/wmi -ClassName WmiMonitorID -ErrorAction Stop
    foreach ($m in $monitors) {
        $name = ($m.UserFriendlyName | Where-Object {$_ -ne 0} | ForEach-Object {[char]$_}) -join ''
        $active = if ($m.Active) { "ACTIVE" } else { "SHADOW" }
        Write-Host "  $name — $active" -ForegroundColor $(if ($m.Active) { "Green" } else { "DarkGray" })
    }
} catch {
    Write-Host "  (WMI monitor query unavailable)" -ForegroundColor DarkGray
}
Write-Host ""

# DUMMY PLUG STATUS (bag of holding)
Write-Host "--- BAG OF HOLDING (HDMI Dummy) ---" -ForegroundColor Green
$dummy = Get-PnpDevice | Where-Object { $_.InstanceId -match "IDVED11" }
foreach ($d in $dummy) {
    $color = switch ($d.Status) { "OK" { "Cyan" } "Unknown" { "DarkGray" } "Error" { "Red" } default { "Yellow" } }
    Write-Host "  $($d.FriendlyName) [$($d.Status)] — UID $($d.InstanceId.Split('UID')[-1])" -ForegroundColor $color
}
if (-not $dummy) { Write-Host "  (no dummy entries found)" -ForegroundColor DarkGray }
Write-Host ""

# AMD RADEON (shadow channel)
Write-Host "--- SHADOW CHANNEL (AMD Radeon) ---" -ForegroundColor Green
$amd = Get-PnpDevice -Class Display | Where-Object { $_.FriendlyName -match "AMD" }
if ($amd) {
    $color = switch ($amd.Status) { "OK" { "Cyan" } "Error" { "Red" } default { "Yellow" } }
    Write-Host "  $($amd.FriendlyName): $($amd.Status)" -ForegroundColor $color
    if ($amd.Status -eq "OK") {
        Write-Host "  Shadow channel FLOWING — energy attenuation active" -ForegroundColor DarkCyan
    } elseif ($amd.Status -eq "Error") {
        Write-Host "  Shadow INTERRUPTED — disable/re-enable to reset" -ForegroundColor DarkYellow
    }
}
Write-Host ""

# SPECTRUM SUMMARY
Write-Host "--- SPECTRUM ---" -ForegroundColor Green
$rtxOk = @($gpus | Where-Object { $_.FriendlyName -match "RTX" -and $_.Status -eq "OK" }).Count -gt 0
$amdOk = @($gpus | Where-Object { $_.FriendlyName -match "AMD" -and $_.Status -eq "OK" }).Count -gt 0
$dummyPresent = @($dummy | Where-Object { $_.Status -ne "Error" }).Count -gt 0

$white = if ($rtxOk) { "WHITE [OK]" } else { "WHITE [DOWN]" }
$black = if ($amdOk) { "BLACK [OK]" } else { "BLACK [INTERRUPTED]" }
$gray = if ($dummyPresent) { "GRAY [PRESENT]" } else { "GRAY [MISSING]" }

Write-Host "  $white + $black + $gray" -ForegroundColor White
if ($rtxOk -and $amdOk -and $dummyPresent) {
    Write-Host "  FULL SPECTRUM — all channels aligned" -ForegroundColor Green
} elseif ($rtxOk -and -not $amdOk) {
    Write-Host "  LIGHT ONLY — shadow interrupted (disable attenuation)" -ForegroundColor Yellow
} else {
    Write-Host "  PARTIAL — check connections" -ForegroundColor DarkYellow
}
Write-Host ""

# NVIDIA POWER
Write-Host "--- RTX 5090 POWER ---" -ForegroundColor Green
$nvOut = nvidia-smi --query-gpu=power.draw,temperature.gpu,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits 2>$null
if ($nvOut) {
    $parts = $nvOut.Split(',').Trim()
    Write-Host "  Power: $($parts[0])W | Temp: $($parts[1])C | GPU: $($parts[2])% | VRAM: $($parts[3])/$($parts[4]) MiB" -ForegroundColor White
}
Write-Host ""

# LOG THIS CYCLE
$logEntry = "$timestamp | Cycle $cycle | RTX=$($rtxOk) AMD=$($amdOk) Dummy=$($dummyPresent) Screens=$($screens.Count)"
Add-Content -Path $cycleFile -Value $logEntry
Write-Host "  Logged to shadowcast-cycles.log" -ForegroundColor DarkGray
Write-Host ""
Write-Host "=== SHADOWCAST CHECK COMPLETE ===" -ForegroundColor Cyan
Write-Host ""
