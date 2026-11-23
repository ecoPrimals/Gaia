# SHRED BLOAT — Kill everything non-essential before UMAF reboot
Write-Host "=" * 60
Write-Host "  SHRED BLOAT — Cut the fat"
Write-Host "=" * 60

# === 1. AUDIT: What's running and how much RAM? ===
Write-Host "`n--- TOP 40 by RAM usage ---"
Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 40 | Format-Table @{N='Name';E={$_.ProcessName}}, @{N='PID';E={$_.Id}}, @{N='RAM_MB';E={[math]::Round($_.WorkingSet64/1MB)}}, @{N='CPU_s';E={[math]::Round($_.CPU,1)}}, @{N='Responding';E={$_.Responding}} -AutoSize

# === 2. Identify BLOAT categories ===
Write-Host "`n--- BLOAT CATEGORIES ---"

# ASUS bloat
$asus = Get-Process | Where-Object { $_.ProcessName -match 'asus|armour|aura|aac|rog' }
$asusRam = ($asus | Measure-Object WorkingSet64 -Sum).Sum / 1MB
Write-Host ("  ASUS bloat: " + $asus.Count + " processes, " + [math]::Round($asusRam) + " MB")

# Microsoft bloat (non-essential)
$msBloat = Get-Process | Where-Object { $_.ProcessName -match 'copilot|gamebar|xbox|cortana|yourphone|phoneexp|widget|teams|onedrive|edge' -and $_.ProcessName -notmatch 'cursor' }
$msBloatRam = ($msBloat | Measure-Object WorkingSet64 -Sum).Sum / 1MB
Write-Host ("  MS bloat: " + $msBloat.Count + " processes, " + [math]::Round($msBloatRam) + " MB")

# NVIDIA overlay (not needed for compute)
$nvBloat = Get-Process | Where-Object { $_.ProcessName -match 'NVIDIA.*overlay|nvcontainer|NVDisplay|GeForce' -and $_.ProcessName -notmatch 'smi' }
$nvBloatRam = ($nvBloat | Measure-Object WorkingSet64 -Sum).Sum / 1MB
Write-Host ("  NVIDIA bloat: " + $nvBloat.Count + " processes, " + [math]::Round($nvBloatRam) + " MB")

# Steam (will restart after reboot anyway)
$steamAll = Get-Process | Where-Object { $_.ProcessName -match 'steam' }
$steamRam = ($steamAll | Measure-Object WorkingSet64 -Sum).Sum / 1MB
Write-Host ("  Steam: " + $steamAll.Count + " processes, " + [math]::Round($steamRam) + " MB")

# ChatGPT desktop (we have Cursor)
$chatgpt = Get-Process | Where-Object { $_.ProcessName -match 'chatgpt' }
$chatRam = ($chatgpt | Measure-Object WorkingSet64 -Sum).Sum / 1MB
Write-Host ("  ChatGPT app: " + $chatgpt.Count + " processes, " + [math]::Round($chatRam) + " MB")

# Edge webviews (not needed)
$edge = Get-Process | Where-Object { $_.ProcessName -match 'msedge' -and $_.ProcessName -notmatch 'cursor' }
$edgeRam = ($edge | Measure-Object WorkingSet64 -Sum).Sum / 1MB
Write-Host ("  Edge/WebView: " + $edge.Count + " processes, " + [math]::Round($edgeRam) + " MB")

# Zombies
$zombies = Get-Process | Where-Object { $_.Responding -eq $false }
Write-Host ("  Zombies: " + $zombies.Count + " processes")

# MsMpEng (Defender - heavy but important)
$defender = Get-Process MsMpEng -ErrorAction SilentlyContinue
if ($defender) { Write-Host ("  Defender: " + [math]::Round($defender.WorkingSet64/1MB) + " MB (keeping)") }

$totalBloat = $asusRam + $msBloatRam + $nvBloatRam + $steamRam + $chatRam + $edgeRam
Write-Host ("`n  TOTAL BLOAT: " + [math]::Round($totalBloat) + " MB reclaimable")

# === 3. KILL BLOAT ===
Write-Host "`n--- KILLING BLOAT ---"

# Kill ASUS
$asus | ForEach-Object { 
    Write-Host ("  KILL: " + $_.ProcessName + " (PID " + $_.Id + ", " + [math]::Round($_.WorkingSet64/1MB) + "MB)")
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}

# Kill MS bloat
$msBloat | ForEach-Object {
    Write-Host ("  KILL: " + $_.ProcessName + " (PID " + $_.Id + ", " + [math]::Round($_.WorkingSet64/1MB) + "MB)")
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}

# Kill NVIDIA overlay
$nvBloat | ForEach-Object {
    Write-Host ("  KILL: " + $_.ProcessName + " (PID " + $_.Id + ", " + [math]::Round($_.WorkingSet64/1MB) + "MB)")
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}

# Kill ChatGPT desktop
$chatgpt | ForEach-Object {
    Write-Host ("  KILL: " + $_.ProcessName + " (PID " + $_.Id + ", " + [math]::Round($_.WorkingSet64/1MB) + "MB)")
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}

# Kill Edge webviews (not Cursor ones)
$edge | ForEach-Object {
    Write-Host ("  KILL: " + $_.ProcessName + " (PID " + $_.Id + ", " + [math]::Round($_.WorkingSet64/1MB) + "MB)")
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}

# Kill zombies
$zombies | ForEach-Object {
    Write-Host ("  KILL ZOMBIE: " + $_.ProcessName + " (PID " + $_.Id + ")")
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}

# Kill Steam (will restart after reboot)  
$steamAll | ForEach-Object {
    Write-Host ("  KILL: " + $_.ProcessName + " (PID " + $_.Id + ", " + [math]::Round($_.WorkingSet64/1MB) + "MB)")
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}

Start-Sleep -Seconds 2

# === 4. DISABLE bloat services for next boot ===
Write-Host "`n--- DISABLING startup bloat ---"
$services = @(
    'ArmouryCrateService',
    'asabortsrv',
    'AsusCertService',
    'ASUSOptimization',
    'ASUSSoftwareManager',
    'ASUSSystemAnalysis',
    'ASUSSystemDiagnosis',
    'LightingService'
)
foreach ($svc in $services) {
    $s = Get-Service $svc -ErrorAction SilentlyContinue
    if ($s) {
        Write-Host ("  Disabling: " + $svc + " [" + $s.Status + "]")
        Set-Service $svc -StartupType Disabled -ErrorAction SilentlyContinue
        Stop-Service $svc -Force -ErrorAction SilentlyContinue
    }
}

# === 5. POST-SHRED audit ===
Write-Host "`n--- POST-SHRED ---"
$afterProcs = Get-Process | Measure-Object WorkingSet64 -Sum
$afterCount = (Get-Process).Count
Write-Host ("  Processes: " + $afterCount)
Write-Host ("  Total RAM: " + [math]::Round($afterProcs.Sum/1MB) + " MB")

# Memory freed
$mem = Get-CimInstance Win32_OperatingSystem
$freeGB = [math]::Round($mem.FreePhysicalMemory / 1MB, 1)
$totalGB = [math]::Round($mem.TotalVisibleMemorySize / 1MB, 1)
Write-Host ("  Free RAM: " + $freeGB + " / " + $totalGB + " GB")

# Remaining top processes
Write-Host "`n--- REMAINING TOP 15 ---"
Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 15 | Format-Table @{N='Name';E={$_.ProcessName}}, @{N='PID';E={$_.Id}}, @{N='RAM_MB';E={[math]::Round($_.WorkingSet64/1MB)}} -AutoSize

Write-Host "`n" + "=" * 60
Write-Host "  BLOAT SHREDDED — LEAN AND MEAN"
Write-Host "=" * 60
