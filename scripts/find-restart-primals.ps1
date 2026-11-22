# Find all primal binaries and restart biomeOS properly
Write-Host "=== FIND + RESTART PRIMALS ==="

# Find all .exe in primals dir
Write-Host "`n--- All primal binaries ---"
Get-ChildItem -Path "c:\Users\mokke\Desktop\Gaia\primals" -Recurse -Filter "*.exe" -ErrorAction SilentlyContinue | ForEach-Object {
    $mb = [math]::Round($_.Length / 1MB, 1)
    Write-Host ("  [{0,5}MB] {1}" -f $mb, $_.FullName.Replace("c:\Users\mokke\Desktop\Gaia\primals\", ""))
}

# Also check plasmidBin
Write-Host "`n--- plasmidBin binaries ---"
Get-ChildItem -Path "c:\Users\mokke\Desktop\Gaia\primals\biomeOS\plasmidBin" -Recurse -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer -and $_.Length -gt 100000 } | ForEach-Object {
    $mb = [math]::Round($_.Length / 1MB, 1)
    Write-Host ("  [{0,5}MB] {1}" -f $mb, $_.FullName.Replace("c:\Users\mokke\Desktop\Gaia\primals\biomeOS\", ""))
}

# Check if biomeOS has a binary search path config
Write-Host "`n--- biomeOS config (stability tiers) ---"
$stabilityPath = "c:\Users\mokke\Desktop\Gaia\primals\biomeOS\config\stability_tiers.toml"
if (Test-Path $stabilityPath) {
    Get-Content $stabilityPath | Where-Object { $_ -match 'binary|path|search|dir|bin' } | ForEach-Object {
        Write-Host "  $($_.Trim())"
    }
}

# Check primal launch profiles for binary paths
Write-Host "`n--- Launch profiles ---"
$profilePath = "c:\Users\mokke\Desktop\Gaia\primals\biomeOS\config\primal_launch_profiles.toml"
if (Test-Path $profilePath) {
    Get-Content $profilePath | Where-Object { $_ -match 'binary|path|subcommand' } | Select-Object -First 10 | ForEach-Object {
        Write-Host "  $($_.Trim())"
    }
}

# Check AppData config
Write-Host "`n--- AppData biomeos config ---"
$appDataPath = "$env:APPDATA\biomeos"
if (Test-Path $appDataPath) {
    Get-ChildItem $appDataPath -Recurse | ForEach-Object {
        Write-Host "  $($_.FullName)"
        if (-not $_.PSIsContainer -and $_.Length -lt 5000) {
            Get-Content $_.FullName | Select-Object -First 5 | ForEach-Object { Write-Host "    $_" }
        }
    }
}

# Try restarting with the ORIGINAL command (dual mode was working before)
Write-Host "`n--- Restarting biomeOS (original dual mode) ---"
$bioPath = "c:\Users\mokke\Desktop\Gaia\primals\biomeOS\target\release\biomeos.exe"

# Kill any existing
Get-Process biomeos -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start with original flags
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $bioPath
$psi.Arguments = "nucleus start --node-id polaris --family-id gaia-pi --mode full --port 31415 --bind 0.0.0.0 --bind-mode dual --verbose"
$psi.WorkingDirectory = "c:\Users\mokke\Desktop\Gaia"
$psi.UseShellExecute = $true
$psi.WindowStyle = "Minimized"

$proc = [System.Diagnostics.Process]::Start($psi)
Write-Host "  Started PID=$($proc.Id)"
Write-Host "  Same command as before — primals should respawn"

Start-Sleep -Seconds 5

# Check if primals are coming back
Write-Host "`n--- Primal check (5s after start) ---"
$procs = Get-Process | Where-Object { $_.Path -and $_.Path -match 'primals' }
Write-Host "  Primal processes: $($procs.Count)"
$procs | Group-Object ProcessName | ForEach-Object {
    Write-Host ("  {0}: {1} instances" -f $_.Name, $_.Count)
}

# Check port
$tcp = New-Object System.Net.Sockets.TcpClient
try {
    $tcp.Connect("127.0.0.1", 31415)
    Write-Host "  :31415 ✅ ALIVE"
    $tcp.Close()
} catch {
    Write-Host "  :31415 ❌ not yet"
}
