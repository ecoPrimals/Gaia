# boot-ladder.ps1 — DRAFT. One ordered boot for northGate; each rung waits for the last to be healthy.
# Replaces: biomeOS-AMALGAM-BOOT.bat (Startup), GaiaGate, GaiaTor, GaiaPostReboot, GaiaLeftEyeWake,
#           Gaia-Startup-Watcher. Not registered yet — run by hand with -DryRun to see the plan.
#   powershell -File boot-ladder.ps1 -DryRun
param([switch]$DryRun)

$ErrorActionPreference = "SilentlyContinue"
$gaia = Split-Path $PSScriptRoot -Parent
$python = "C:\Users\mokke\AppData\Local\Programs\Python\Python312\python.exe"
$ollama = "C:\Users\mokke\AppData\Local\Programs\Ollama\ollama.exe"
$biomeos = "$gaia\primals\biomeOS\target\release\biomeos.exe"
$tor = "$gaia\engine\tor\tor\tor.exe"
$ladderLog = "$gaia\data\spine\boot-journal\northGate-ladder.jsonl"

# biomeOS identity. FAMILY_SEED is deliberately NOT here: set it once as a user
# environment variable so it never sits in a file.
$env:FAMILY_ID = "gaia-pi"
$env:NODE_ID = "polaris"
$env:XDG_RUNTIME_DIR = "$gaia\runtime"
$env:RUST_LOG = "info"
$env:BIOMEOS_SOVEREIGN = "true"
$env:ECOPRIMALS_PLASMID_BIN = "$gaia\primals\biomeOS\plasmidBin"

$start = Get-Date
$rungs = [System.Collections.Generic.List[object]]::new()

function Listening([int]$port) { [bool](Get-NetTCPConnection -LocalPort $port -State Listen) }
function Running([string]$name) { [bool](Get-Process $name) }

# Wait for $healthy to be true (polling, not a fixed sleep); record how long it took.
function Rung([string]$name, [scriptblock]$alreadyUp, [scriptblock]$launch, [scriptblock]$healthy, [int]$timeoutS = 60) {
    $t0 = Get-Date
    if (& $alreadyUp) { $rungs.Add([ordered]@{ rung = $name; state = "already up"; s = 0 }); return $true }
    if ($DryRun) { $rungs.Add([ordered]@{ rung = $name; state = "would start" }); return $true }
    & $launch
    while (((Get-Date) - $t0).TotalSeconds -lt $timeoutS) {
        if (& $healthy) {
            $rungs.Add([ordered]@{ rung = $name; state = "healthy"; s = [math]::Round(((Get-Date) - $t0).TotalSeconds, 1) })
            return $true
        }
        Start-Sleep -Milliseconds 500
    }
    $rungs.Add([ordered]@{ rung = $name; state = "TIMEOUT"; s = $timeoutS })
    return $false
}

# 1 — pores: Tor (one instance; the old .bat and GaiaTor both started it)
Rung "tor" { Listening 9050 } {
    Start-Process $tor -ArgumentList "-f", "$gaia\engine\tor\torrc" -WindowStyle Hidden
} { Listening 9050 } 60 | Out-Null

# 2 — mind: Ollama (was in no boot path at all)
Rung "ollama" { Listening 11434 } {
    Start-Process $ollama -ArgumentList "serve" -WindowStyle Hidden
} { try { [bool](Invoke-RestMethod http://127.0.0.1:11434/api/version -TimeoutSec 2) } catch { $false } } 60 | Out-Null

# 3 — pipes: biomeOS. It doesn't open :31415 on Windows yet, so "healthy" = still alive after 10s.
Rung "biomeos" { Running "biomeos" } {
    Start-Process $biomeos -WindowStyle Minimized -ArgumentList "nucleus", "start", "--node-id", "polaris",
        "--family-id", "gaia-pi", "--mode", "full", "--port", "31415", "--bind", "0.0.0.0", "--bind-mode", "dual"
    $script:biomeStarted = Get-Date
} { (Running "biomeos") -and (((Get-Date) - $script:biomeStarted).TotalSeconds -ge 10) } 30 | Out-Null

# 4 — face: the gate on :8443 (gaia-boot.ps1 pointed at a Python that doesn't exist).
#     Only stale gates are stopped — not every Python process.
Rung "gate" { Listening 8443 } {
    Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object CommandLine -match 'gaia_gate\.pi' |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
    Start-Process $python -ArgumentList "$gaia\runtime\gaia_gate.pi" -WorkingDirectory $gaia -WindowStyle Hidden
} { Listening 8443 } 45 | Out-Null

# 5 — senses: watchers (full Python path; Task Scheduler couldn't find "python")
Rung "watchers" { $false } {
    Start-Process powershell -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-WindowStyle", "Hidden",
        "-File", "$gaia\scripts\gaia-startup-watcher.ps1" -WindowStyle Hidden
    Start-Process $python -ArgumentList "$gaia\scripts\post-reboot-verify.py" -WorkingDirectory $gaia -WindowStyle Hidden
} { $true } 5 | Out-Null

# 6 — memory: record this boot (and any crash before it) in the boot journal
Rung "journal" { $false } {
    & powershell -NoProfile -ExecutionPolicy Bypass -File "$gaia\runtime\boot-journal.ps1"
} { $true } 30 | Out-Null

$entry = [ordered]@{ ladder_start = $start.ToString('yyyy-MM-ddTHH:mm:ss'); dry_run = [bool]$DryRun; rungs = $rungs
                     total_s = [math]::Round(((Get-Date) - $start).TotalSeconds, 1) }
if ($DryRun) { $entry | ConvertTo-Json -Depth 4 } else { Add-Content $ladderLog ($entry | ConvertTo-Json -Compress -Depth 4) }
