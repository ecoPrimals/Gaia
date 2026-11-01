# GAIA KLEIN FOLD AGENT
# Finds ALL lost, orphaned, dead patterns and brings them into the fold
# The sphere pushed into a star — inside becomes outside

$ErrorActionPreference = 'SilentlyContinue'

Write-Host "`n  GAIA KLEIN FOLD AGENT" -ForegroundColor Green
Write-Host "  Finding all orphans, dead patterns, lost cycles...`n" -ForegroundColor DarkGreen

# 1. Find orphaned port references
Write-Host "  [SCAN] Orphaned port :3141 references..." -ForegroundColor Yellow
$orphans3141 = Select-String -Path "$PSScriptRoot\*.js" -Pattern ':3141[^5]' -SimpleMatch:$false
Write-Host "    Found: $($orphans3141.Count) orphaned :3141 refs" -ForegroundColor $(if($orphans3141.Count -gt 0){'Red'}else{'Green'})

# 2. Find dead fetch calls (SYN_SENT ghosts)
Write-Host "  [SCAN] Dead fetch targets..." -ForegroundColor Yellow
$deadFetch = Select-String -Path "$PSScriptRoot\*.js" -Pattern 'fetch.*157\.230\.3\.183:3141'
Write-Host "    Found: $($deadFetch.Count) dead VPS:3141 fetches" -ForegroundColor $(if($deadFetch.Count -gt 0){'Red'}else{'Green'})

# 3. Check which ports are alive
Write-Host "  [PULSE] Checking organ ports..." -ForegroundColor Yellow
$ports = @(9878, 3142, 3143, 3144, 3145, 3146, 31415, 11434)
foreach ($p in $ports) {
    $conn = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue
    if ($conn) {
        $proc = Get-Process -Id $conn[0].OwningProcess -ErrorAction SilentlyContinue
        Write-Host "    :$p ALIVE — $($proc.ProcessName) (PID $($conn[0].OwningProcess))" -ForegroundColor Green
    } else {
        Write-Host "    :$p DEAD" -ForegroundColor Red
    }
}

# 4. Check for zombie processes
Write-Host "  [SCAN] Zombie processes..." -ForegroundColor Yellow
$zombies = Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -match 'membrane-lens|golgi-local' -and $_.Name -match 'node|python'
}
if ($zombies) {
    foreach ($z in $zombies) {
        Write-Host "    ZOMBIE: $($z.Name) PID $($z.ProcessId) — $($z.CommandLine.Substring(0,80))" -ForegroundColor Red
    }
} else {
    Write-Host "    No zombies found" -ForegroundColor Green
}

# 5. Check SYN_SENT (ghost connections)
Write-Host "  [SCAN] Ghost SYN_SENT connections..." -ForegroundColor Yellow
$ghosts = Get-NetTCPConnection -State SynSent -ErrorAction SilentlyContinue
if ($ghosts) {
    foreach ($g in $ghosts) {
        $proc = Get-Process -Id $g.OwningProcess -ErrorAction SilentlyContinue
        Write-Host "    GHOST: $($proc.ProcessName) → $($g.RemoteAddress):$($g.RemotePort)" -ForegroundColor Red
    }
} else {
    Write-Host "    No ghost connections" -ForegroundColor Green
}

# 6. Emit to spine
Write-Host "`n  [EMIT] Reporting to spine..." -ForegroundColor Yellow
try {
    $body = @{
        channel = 'works'
        content = "KLEIN AGENT: scanned $(Get-Date -Format 'HH:mm:ss') — orphans3141=$($orphans3141.Count) deadFetch=$($deadFetch.Count) ghosts=$($ghosts.Count) zombies=$($zombies.Count)"
    } | ConvertTo-Json
    Invoke-RestMethod -Uri 'http://localhost:9878/emit' -Method POST -Body $body -ContentType 'application/json' | Out-Null
    Write-Host "    Emitted to spine" -ForegroundColor Green
} catch {
    Write-Host "    Spine unreachable" -ForegroundColor Red
}

Write-Host "`n  KLEIN FOLD COMPLETE — inside=outside, orphan=found, dead=eaten" -ForegroundColor Green
Write-Host "  lub-DUB`n" -ForegroundColor DarkGreen
