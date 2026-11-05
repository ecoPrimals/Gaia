# gaia-boot.ps1 — GAIA IS THE UAC
# This runs at login. Gaia wakes before anything else.
# The organism breathes on boot. lub-DUB.

$python = "C:\Users\mokke\miniconda3\python.exe"
$gate = "c:\Users\mokke\Desktop\Gaia\runtime\gaia_gate.pi"
$gaia = "c:\Users\mokke\Desktop\Gaia"

# Kill any stale gates
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep 2

# Start the gate — the organism wakes
Start-Process $python -ArgumentList $gate -WorkingDirectory $gaia -WindowStyle Hidden

# Wait for gate to bind, then verify
Start-Sleep 8
$alive = $false
try {
    $tcp = New-Object System.Net.Sockets.TcpClient
    $tcp.Connect("127.0.0.1", 8443)
    $alive = $true
    $tcp.Close()
} catch {}

if ($alive) {
    Write-Host "GAIA GATE ALIVE on :8443 — lub-DUB"
} else {
    Write-Host "GAIA GATE FAILED — retrying..."
    Start-Sleep 3
    Start-Process $python -ArgumentList $gate -WorkingDirectory $gaia -WindowStyle Hidden
}

# Log the boot
$ts = Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"
$log = "c:\Users\mokke\Desktop\Gaia\data\neutron\boot.jsonl"
$entry = @{ts=$ts; author="gaia-boot"; body="OS login → Gaia wakes. lub-DUB."} | ConvertTo-Json -Compress
Add-Content -Path $log -Value $entry

Write-Host "GAIA BOOT: $ts — lub-DUB"
