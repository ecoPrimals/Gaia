# REDOX biomeOS — Fix discovery by switching to TCP-only mode
Write-Host "=== REDOX biomeOS ==="

# 1. Current state
Write-Host "`n--- Current biomeOS ---"
$bio = Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'biomeos' }
foreach ($b in $bio) {
    Write-Host "  PID=$($b.ProcessId) CMD=$($b.CommandLine)"
}

# 2. Get the binary path
$bioPath = "c:\Users\mokke\Desktop\Gaia\primals\biomeOS\target\release\biomeos.exe"
Write-Host "  Binary: $bioPath"
Write-Host "  Exists: $(Test-Path $bioPath)"

# 3. Check what primals are running (save their PIDs)
Write-Host "`n--- Running primals ---"
$primalProcs = Get-Process | Where-Object { $_.Path -and $_.Path -match 'primals\\biomeOS\\target' }
$primalCount = ($primalProcs | Select-Object -Unique ProcessName).Count
Write-Host "  $primalCount unique species, $($primalProcs.Count) total processes"

# 4. Read membrane state
$memDir = "c:\Users\mokke\Desktop\Gaia\runtime\membrane"
Write-Host "`n--- Membrane state ---"
$pidFiles = Get-ChildItem $memDir -Filter "*.pid" -ErrorAction SilentlyContinue
$portFiles = Get-ChildItem $memDir -Filter "*.port" -ErrorAction SilentlyContinue
Write-Host "  PID files: $($pidFiles.Count)"
Write-Host "  Port files: $($portFiles.Count)"
foreach ($pf in $portFiles) {
    $portVal = Get-Content $pf.FullName -Raw
    Write-Host "    $($pf.Name) = $($portVal.Trim())"
}

# 5. Kill biomeOS nucleus (but NOT the individual primals)
Write-Host "`n--- Stopping biomeOS nucleus ---"
$nucleusProcs = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'nucleus start' }
foreach ($np in $nucleusProcs) {
    Write-Host "  Killing nucleus PID=$($np.ProcessId)"
    Stop-Process -Id $np.ProcessId -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 2

# 6. Set environment variables
Write-Host "`n--- Setting TCP environment ---"
$env:PRIMAL_BIND_MODE = "tcp"
$env:XDG_RUNTIME_DIR = "c:\Users\mokke\Desktop\Gaia\runtime"
$env:BIOMEOS_SOCKET_TRANSPORT = "tcp"

# 7. Restart biomeOS with TCP-only bind mode
Write-Host "`n--- Restarting biomeOS nucleus (TCP-only) ---"
$args_str = "nucleus start --node-id polaris --family-id gaia-pi --mode full --port 31415 --bind 0.0.0.0 --bind-mode tcp --verbose"
Write-Host "  CMD: $bioPath $args_str"

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $bioPath
$psi.Arguments = $args_str
$psi.WorkingDirectory = "c:\Users\mokke\Desktop\Gaia"
$psi.UseShellExecute = $false
$psi.EnvironmentVariables["PRIMAL_BIND_MODE"] = "tcp"
$psi.EnvironmentVariables["XDG_RUNTIME_DIR"] = "c:\Users\mokke\Desktop\Gaia\runtime"
$psi.EnvironmentVariables["BIOMEOS_SOCKET_TRANSPORT"] = "tcp"

$proc = [System.Diagnostics.Process]::Start($psi)
Write-Host "  Started PID=$($proc.Id)"

Start-Sleep -Seconds 3

# 8. Verify
Write-Host "`n--- Verify ---"
$newBio = Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'biomeos' }
foreach ($nb in $newBio) {
    Write-Host "  PID=$($nb.ProcessId) CMD=$($nb.CommandLine)"
}

$tcpAlive = (New-Object System.Net.Sockets.TcpClient)
try {
    $tcpAlive.Connect("127.0.0.1", 31415)
    Write-Host "  :31415 TCP ALIVE ✅"
    $tcpAlive.Close()
} catch {
    Write-Host "  :31415 not yet ❌"
}

Write-Host "`n=== biomeOS restarted with --bind-mode tcp ==="
Write-Host "  Watch the console — discovery should find primals now!"
