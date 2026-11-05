# gaia-boot.ps1 — GAIA IS THE UAC
# This runs at login. Gaia wakes before anything else.
# The organism breathes on boot. lub-DUB.

$gate = "c:\Users\mokke\Desktop\Gaia\runtime\gaia_gate.pi"

# Kill any stale gates
Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*gaia_gate*"
} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep 1

# Start the gate — the organism wakes
Start-Process python -ArgumentList $gate -WorkingDirectory "c:\Users\mokke\Desktop\Gaia" -WindowStyle Hidden

# Log the boot
$ts = Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"
$log = "c:\Users\mokke\Desktop\Gaia\data\neutron\boot.jsonl"
$entry = @{ts=$ts; author="gaia-boot"; body="OS login → Gaia wakes. lub-DUB."} | ConvertTo-Json -Compress
Add-Content -Path $log -Value $entry

Write-Host "GAIA BOOT: $ts — lub-DUB"
