# boot-journal.ps1 — one line per boot, per gate, in data/spine/boot-journal/<gate>.jsonl
# Built from what Windows already records: boot/stop events, crashes, boot timing, app faults.
#   powershell -File boot-journal.ps1              record the current boot (run once boot has settled)
#   powershell -File boot-journal.ps1 -Backfill 30 rebuild the last 30 days of boots
param([int]$Backfill = 0, [string]$Gate = $env:GAIA_GATE)

$ErrorActionPreference = "SilentlyContinue"
if (-not $Gate) { $Gate = "northGate" }
$dir = Join-Path $PSScriptRoot "..\data\spine\boot-journal"
New-Item -ItemType Directory -Force -Path $dir | Out-Null
$journal = Join-Path $dir "$Gate.jsonl"

function EventData($e) {
    $d = @{}
    ([xml]$e.ToXml()).Event.EventData.Data | ForEach-Object { $d[$_.Name] = $_.'#text' }
    $d
}

$days = if ($Backfill -gt 0) { $Backfill } else { 2 }
$since = (Get-Date).AddDays(-$days)
$sys = Get-WinEvent -FilterHashtable @{ LogName = 'System'; StartTime = $since; Id = 6005, 6006, 6008, 41, 1001 }
$perf = Get-WinEvent -FilterHashtable @{ LogName = 'Microsoft-Windows-Diagnostics-Performance/Operational'; StartTime = $since; Id = 100 }
$faults = Get-WinEvent -FilterHashtable @{ LogName = 'Application'; StartTime = $since; Id = 1000 }
$whea = Get-WinEvent -FilterHashtable @{ LogName = 'System'; ProviderName = 'Microsoft-Windows-WHEA-Logger'; StartTime = $since }

# 6005 = event log started, the first reliable mark of each boot.
$boots = @($sys | Where-Object Id -eq 6005 | Sort-Object TimeCreated | Select-Object -Expand TimeCreated)
if ($Backfill -le 0) { $boots = @($boots | Select-Object -Last 1) }

$known = @{}
if (Test-Path $journal) {
    Get-Content $journal | ForEach-Object { try { $known[($_ | ConvertFrom-Json).boot] = $true } catch {} }
}

$all = @($sys | Where-Object Id -eq 6005 | Sort-Object TimeCreated | Select-Object -Expand TimeCreated)
$written = 0
foreach ($b in $boots) {
    $key = $b.ToString('yyyy-MM-ddTHH:mm:ss')
    if ($known[$key]) { continue }
    $prev = $all | Where-Object { $_ -lt $b } | Select-Object -Last 1
    $next = $all | Where-Object { $_ -gt $b } | Select-Object -First 1
    $windowEnd = if ($next) { $next } else { Get-Date }

    # Kernel-Power 41 and the bugcheck summary are written a few seconds BEFORE 6005.
    $crashFrom = if ($prev) { $prev.AddMinutes(1) } else { $b.AddMinutes(-2) }
    $clean = $prev -and ($sys | Where-Object { $_.Id -eq 6006 -and $_.TimeCreated -gt $prev -and $_.TimeCreated -lt $b })
    $kp = $sys | Where-Object { $_.Id -eq 41 -and $_.TimeCreated -ge $crashFrom -and $_.TimeCreated -lt $b.AddMinutes(5) -and (-not $next -or $_.TimeCreated -lt $next) } | Select-Object -First 1
    $bug = $sys | Where-Object { $_.Id -eq 1001 -and $_.TimeCreated -ge $crashFrom -and $_.TimeCreated -lt $b.AddMinutes(10) -and (-not $next -or $_.TimeCreated -lt $next) } | Select-Object -First 1
    $p = $perf | Where-Object { $_.TimeCreated -ge $b -and $_.TimeCreated -lt $b.AddMinutes(15) -and (-not $next -or $_.TimeCreated -lt $next) } | Select-Object -First 1
    if ($kp) { $prevShutdownOverride = "unexpected" } else { $prevShutdownOverride = $null }

    $prevShutdown = if ($prevShutdownOverride) { $prevShutdownOverride } elseif (-not $prev) { "unknown" } elseif ($clean) { "clean" } else { "unexpected" }
    $crash = $null
    if ($kp) {
        $d = EventData $kp
        $code = [int]$d.BugcheckCode
        $crash = [ordered]@{
            kind     = if ($code -ne 0) { "bugcheck" } else { "hard power loss or freeze" }
            bugcheck = if ($code -ne 0) { '0x{0:X}' -f $code } else { $null }
        }
        if ($bug -and $bug.Message -match 'Minidump\\(\S+\.dmp)') { $crash.minidump = $matches[1] }
    }
    $timing = $null
    if ($p) {
        $d = EventData $p
        $timing = [ordered]@{ boot_s = [math]::Round([int]$d.BootTime / 1000, 1); main_s = [math]::Round([int]$d.MainPathBootTime / 1000, 1); post_s = [math]::Round([int]$d.BootPostBootTime / 1000, 1) }
    }
    $appFaults = @($faults | Where-Object { $_.TimeCreated -ge $b -and $_.TimeCreated -lt $windowEnd } | ForEach-Object {
        if ($_.Message -match 'Faulting application name: ([^,]+)') { $matches[1] } } | Group-Object | Sort-Object Count -Descending |
        ForEach-Object { "$($_.Name) x$($_.Count)" })
    $wheaCount = @($whea | Where-Object { $_.TimeCreated -ge $b -and $_.TimeCreated -lt $windowEnd }).Count

    $entry = [ordered]@{
        gate              = $Gate
        boot              = $key
        previous_shutdown = $prevShutdown
        crash_before_boot = $crash
        timing            = $timing
        app_faults        = $appFaults
        whea_errors       = $wheaCount
        uptime_h          = if ($next) { [math]::Round(($next - $b).TotalHours, 2) } else { $null }
    }
    Add-Content -Path $journal -Value ($entry | ConvertTo-Json -Compress -Depth 4) -Encoding utf8
    $written++
}
"boot-journal: $written new entries -> $journal"
