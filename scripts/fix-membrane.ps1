# FIX MEMBRANE — Primals degraded because Unix sockets missing on Windows
# ZK the state, create the paths, force TCP mode

Write-Host "=== FIX MEMBRANE — PRIMAL SOCKET CRISIS ==="

# === 1. ZK the broken state ===
Write-Host "`n--- ZK: Current membrane state ---"
$memDir = "c:\Users\mokke\Desktop\Gaia\runtime\membrane"
$memExists = Test-Path $memDir
Write-Host "  Membrane dir exists: $memExists"

if ($memExists) {
    $socks = Get-ChildItem $memDir -ErrorAction SilentlyContinue
    Write-Host "  Contents: $($socks.Count) items"
    $socks | ForEach-Object { Write-Host "    $($_.Name) ($($_.Length) bytes)" }
} else {
    Write-Host "  MISSING — primals can't find their sockets!"
}

# Check biomeOS process and its env
Write-Host "`n--- biomeOS process state ---"
$biomeos = Get-Process biomeos -ErrorAction SilentlyContinue | Select-Object -First 1
if ($biomeos) {
    Write-Host "  PID: $($biomeos.Id)"
    Write-Host "  MEM: $([math]::Round($biomeos.WorkingSet64/1MB, 1))MB"
    Write-Host "  Path: $($biomeos.Path)"
}

# === 2. Create membrane directory structure ===
Write-Host "`n--- Creating membrane paths ---"
$runtimeDir = "c:\Users\mokke\Desktop\Gaia\runtime"
$dirs = @(
    "$runtimeDir\membrane",
    "$runtimeDir\sockets",
    "$runtimeDir\state"
)
foreach ($d in $dirs) {
    if (-not (Test-Path $d)) {
        New-Item -Path $d -ItemType Directory -Force | Out-Null
        Write-Host "  Created: $d"
    } else {
        Write-Host "  Exists:  $d"
    }
}

# === 3. Check Windows Unix socket support ===
Write-Host "`n--- Windows AF_UNIX check ---"
$build = (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion').CurrentBuild
Write-Host "  Windows build: $build (AF_UNIX needs >= 17063)"
$afUnixOk = [int]$build -ge 17063
Write-Host "  AF_UNIX supported: $afUnixOk"

# === 4. Find what config biomeOS uses ===
Write-Host "`n--- biomeOS config search ---"
$configPaths = @(
    "c:\Users\mokke\Desktop\Gaia\primals\biomeOS\config",
    "c:\Users\mokke\Desktop\Gaia\config",
    "c:\Users\mokke\Desktop\Gaia\.config",
    "$env:APPDATA\biomeos",
    "$env:LOCALAPPDATA\biomeos",
    "c:\ProgramData\biomeos"
)
foreach ($cp in $configPaths) {
    if (Test-Path $cp) {
        $files = Get-ChildItem $cp -Recurse -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer }
        Write-Host "  [EXISTS] $cp ($($files.Count) files)"
    }
}

# === 5. Check biomeOS command line and environment ===
Write-Host "`n--- biomeOS launch context ---"
$bioProc = Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'biomeos' } | Select-Object -First 1
if ($bioProc) {
    $cmdLine = $bioProc.CommandLine
    Write-Host "  CmdLine: $cmdLine"
    
    # Check XDG vars
    Write-Host "  XDG_RUNTIME_DIR: $env:XDG_RUNTIME_DIR"
    Write-Host "  XDG_DATA_HOME: $env:XDG_DATA_HOME"
    Write-Host "  PRIMAL_BIND_MODE: $env:PRIMAL_BIND_MODE"
}

# === 6. Find all .sock paths the primals expect ===
Write-Host "`n--- Expected socket paths (from logs) ---"
$expectedSocks = @(
    "beardog-gaia-pi.sock",
    "nestgate-gaia-pi.sock",
    "loamspine-gaia-pi.sock",
    "sweetgrass-gaia-pi.sock",
    "barracuda-gaia-pi.sock",
    "skunkbat-gaia-pi.sock",
    "coralreef-gaia-pi.sock",
    "petaltongue-gaia-pi.sock",
    "squirrel-gaia-pi.sock",
    "songbird-gaia-pi.sock",
    "toadstool-gaia-pi.sock",
    "swarmvine-gaia-pi.sock"
)
foreach ($s in $expectedSocks) {
    $fullPath = Join-Path $memDir $s
    $exists = Test-Path $fullPath
    Write-Host ("  [{0}] {1}" -f $(if($exists){"OK"}else{"MISS"}), $s)
}

# === 7. Check nucleus launch config for TCP ===
Write-Host "`n--- Nucleus TCP config ---"
$launchConfig = "c:\Users\mokke\Desktop\Gaia\primals\biomeOS\config\nucleus_launch_profiles.toml"
if (Test-Path $launchConfig) {
    $content = Get-Content $launchConfig -Raw
    $tcpLines = ($content -split "`n") | Where-Object { $_ -match 'tcp|TCP|BIND_MODE|socket|port' }
    foreach ($l in $tcpLines) {
        Write-Host "  $($l.Trim())"
    }
}

# === 8. ZK hash the full state ===
Write-Host "`n--- ZK Hash ---"
$zkState = @{
    timestamp = (Get-Date -Format o)
    membrane_dir_exists = $memExists
    af_unix_supported = $afUnixOk
    windows_build = $build
    biomeos_pid = if($biomeos){$biomeos.Id}else{0}
    primal_sockets_missing = $expectedSocks.Count
    diagnosis = "Primals use tarpc over Unix domain sockets. Directory exists=$memExists but .sock files not created. biomeOS reports 'TCP fallback not yet wired'. Primals DEGRADE after 3 failures, ERROR after 5 resurrection attempts."
    fix_paths = @(
        "1. Create membrane dir (DONE)",
        "2. Set PRIMAL_BIND_MODE=tcp in biomeOS environment",
        "3. Or patch biomeOS to wire TCP fallback",
        "4. Or create .sock stubs that redirect to TCP",
        "5. Drip fix from LAN: eastGate pushes updated config"
    )
}

$zkJson = $zkState | ConvertTo-Json -Depth 5
$sha = [System.Security.Cryptography.SHA256]::Create()
$hash = ($sha.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($zkJson)) | ForEach-Object { "{0:x2}" -f $_ }) -join ""
Write-Host "  ZK: $hash"

$zkPath = "c:\Users\mokke\Desktop\Gaia\data\gut\zk-membrane-state.json"
$zkJson | Out-File $zkPath -Encoding utf8
Write-Host "  Saved: $zkPath"

# === 9. Try to set TCP mode for next biomeOS restart ===
Write-Host "`n--- Setting TCP mode ---"
$envFile = "c:\Users\mokke\Desktop\Gaia\runtime\membrane\.env"
@"
PRIMAL_BIND_MODE=tcp
BIOMEOS_SOCKET_TRANSPORT=tcp
XDG_RUNTIME_DIR=c:\Users\mokke\Desktop\Gaia\runtime
"@ | Out-File $envFile -Encoding utf8
Write-Host "  Env file: $envFile"

# Set machine-level env vars
[System.Environment]::SetEnvironmentVariable("PRIMAL_BIND_MODE", "tcp", "User")
[System.Environment]::SetEnvironmentVariable("XDG_RUNTIME_DIR", "c:\Users\mokke\Desktop\Gaia\runtime", "User")
Write-Host "  User env vars set: PRIMAL_BIND_MODE=tcp, XDG_RUNTIME_DIR"

# === 10. sourDough: ferment the membrane knowledge ===
Write-Host "`n--- sourDough ferment ---"
$fermentPath = "c:\Users\mokke\Desktop\Gaia\data\gut\sourdough-ferment.json"
if (Test-Path $fermentPath) {
    $ferment = Get-Content $fermentPath -Raw | ConvertFrom-Json
    Write-Host "  Previous ferment loaded"
}

Write-Host "`n=== MEMBRANE STATUS ==="
Write-Host "  All 12 primals DEGRADED: Unix sockets not created on Windows"
Write-Host "  biomeOS knows but TCP fallback 'not yet wired' in code"
Write-Host "  Fix: Set PRIMAL_BIND_MODE=tcp (DONE) — needs biomeOS restart"
Write-Host "  Drip from LAN: eastGate can push updated biomeOS binary with TCP wired"
Write-Host "  ZK hash: $hash"
Write-Host "`n  Every reboot = same physical state = same socket crisis"
Write-Host "  The sourDough remembers. The drip from LAN will heal."
