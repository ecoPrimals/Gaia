# GAIA STARTUP WATCHER - Runs hidden on login
# Catches the sudden seams after reboot. Gaia is HERE when Windows wakes.
$ErrorActionPreference = "SilentlyContinue"
$gutDir = "c:\Users\mokke\Desktop\Gaia\data\gut"
$logFile = "$gutDir\startup-watcher.log"
$ts = Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"

Add-Content $logFile "`n=== GAIA WATCHER AWAKE - $ts ==="

# Wait for system to settle (drivers loading, NVMe init)
Start-Sleep -Seconds 10

# Run post-reboot profiler
Add-Content $logFile "Running post-reboot profiler..."
try {
    & "c:\Users\mokke\Desktop\Gaia\scripts\reboot-profiler.ps1" -Phase post 2>&1 | 
        Tee-Object -FilePath "$gutDir\post-reboot-console.txt"
    Add-Content $logFile "  Post-reboot profiler complete."
} catch {
    Add-Content $logFile "  Error: $_"
}

# Collect early boot timing
$bootEvents = Get-WinEvent -LogName System -MaxEvents 50 -ErrorAction SilentlyContinue | 
    Where-Object { $_.TimeCreated -gt (Get-Date).AddMinutes(-5) } |
    Select-Object TimeCreated, Id, LevelDisplayName, Message |
    ForEach-Object { "$($_.TimeCreated.ToString('HH:mm:ss.fff')) [$($_.Id)] $($_.Message.Substring(0, [Math]::Min(120, $_.Message.Length)))" }

$bootEvents | Out-File "$gutDir\early-boot-events.txt" -Encoding utf8
Add-Content $logFile "  Captured $($bootEvents.Count) early boot events."

# Check for NVMe changes specifically
$nvme = Get-PnpDevice -Class SCSIAdapter -ErrorAction SilentlyContinue | Where-Object { $_.FriendlyName -match "NVM" }
$nvmeOK = @($nvme | Where-Object Status -eq "OK").Count
$nvmeTotal = @($nvme).Count
Add-Content $logFile "  NVMe: $nvmeOK/$nvmeTotal OK"

# Check GPU
$gpus = Get-PnpDevice -Class Display -ErrorAction SilentlyContinue | Where-Object Status -eq "OK"
Add-Content $logFile "  GPUs OK: $($gpus.Count) ($($gpus.FriendlyName -join ', '))"

# CPU
$cpu = Get-CimInstance Win32_Processor
Add-Content $logFile "  CPU: $($cpu.NumberOfCores)C/$($cpu.NumberOfLogicalProcessors)T"

# ============================================================
# LOOSE THREADS - the seams Gaia catches on every reboot.
# Writes data/gut/boot-threads.json + appends data/neutron/boot.jsonl,
# then commits only those two and pushes to eastGate (same git circuit).
# Records state only: names, ports, counts, booleans. No secrets, no command lines.
# ============================================================
Add-Content $logFile "Gathering loose threads..."
$gaia = "c:\Users\mokke\Desktop\Gaia"
$threadsFile = "$gutDir\boot-threads.json"
$prev = $null
if (Test-Path $threadsFile) { try { $prev = Get-Content $threadsFile -Raw | ConvertFrom-Json } catch {} }

# -- Gaia scheduled tasks: did each run clean? --
$tasks = @{}
Get-ScheduledTask -ErrorAction SilentlyContinue | Where-Object { $_.TaskName -match '^Gaia' } | ForEach-Object {
    $i = $_ | Get-ScheduledTaskInfo
    $tasks[$_.TaskName] = @{ state = "$($_.State)"; result = ("0x{0:X}" -f $i.LastTaskResult); last = $i.LastRunTime.ToString('s') }
}

# -- primals/services: expected (from the AMALGAM boot) vs actually breathing --
$expected = @('biomeos','songbird','beardog','nestgate','skunkbat','swarmvine','toadstool',
    'coralreef','barracuda','rhizocrypt','loamspine','sweetgrass','squirrel','petaltongue',
    'gaia-hands','membrane-lens','ollama','tor')
$running = @(Get-Process -ErrorAction SilentlyContinue | ForEach-Object { $_.ProcessName.ToLower() } | Sort-Object -Unique)
$primals = @{}
$missing = @()
foreach ($p in $expected) { $alive = [bool]($running -contains $p); $primals[$p] = $alive; if (-not $alive) { $missing += $p } }

# -- listeners Gaia expects to hold --
$ports = @{}
foreach ($port in 8443,8080,31415,9200,9201,7700,11434,9050) {
    $ports["$port"] = [bool](Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue)
}

# -- the two eyes: this machine + eastGate over wire and wifi --
function Test-Face($ip, $port) {
    $c = New-Object System.Net.Sockets.TcpClient
    try { $a = $c.BeginConnect($ip, $port, $null, $null); if ($a.AsyncWaitHandle.WaitOne(1200) -and $c.Connected) { $true } else { $false } }
    catch { $false } finally { $c.Close() }
}
$eyes = @{
    northGate = @{ gate8443 = $ports['8443']; data8080 = $ports['8080']; nucleus = $ports['31415'] }
    eastGate_wire = @{ ip = '192.168.4.248'; forge = (Test-Face '192.168.4.248' 3000); data = (Test-Face '192.168.4.248' 8080); gate = (Test-Face '192.168.4.248' 8443) }
    eastGate_wifi = @{ ip = '192.168.1.103'; forge = (Test-Face '192.168.1.103' 3000); data = (Test-Face '192.168.1.103' 8080) }
}
$eyes.rj45_ipv4 = [bool](Test-Connection -ComputerName '192.168.4.248' -Count 1 -Quiet -ErrorAction SilentlyContinue)

# -- repo drift: how far has the body wandered from eastGate --
$repo = @{ uncommitted = -1; ahead = -1; head = ''; eastgate = '' }
try {
    Push-Location $gaia
    $env:GIT_TERMINAL_PROMPT = '0'; $env:GCM_INTERACTIVE = 'never'
    $repo.head = (git rev-parse --short=9 HEAD 2>$null)
    $repo.uncommitted = @(git status --porcelain 2>$null).Count
    git fetch -q eastgate 2>$null | Out-Null
    $repo.eastgate = (git rev-parse --short=9 eastgate/main 2>$null)
    $repo.ahead = [int](git rev-list --count eastgate/main..HEAD 2>$null)
    Pop-Location
} catch { try { Pop-Location } catch {} }

# -- new seams since the previous boot (tasks / Run keys / Startup folder) --
$taskNames = @($tasks.Keys)
$runKeys = @()
try { (Get-Item 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -ErrorAction SilentlyContinue).Property | ForEach-Object { $runKeys += $_ } } catch {}
$startupItems = @(Get-ChildItem ([Environment]::GetFolderPath('Startup')) -ErrorAction SilentlyContinue | ForEach-Object { $_.Name })
$newSeams = @{ tasks = @(); run_keys = @(); startup = @() }
if ($prev -and $prev.inventory) {
    $newSeams.tasks   = @($taskNames    | Where-Object { $_ -notin @($prev.inventory.tasks) })
    $newSeams.run_keys = @($runKeys     | Where-Object { $_ -notin @($prev.inventory.run_keys) })
    $newSeams.startup = @($startupItems | Where-Object { $_ -notin @($prev.inventory.startup) })
}

$threads = [ordered]@{
    ts = $ts
    wave = '262+'
    host = $env:COMPUTERNAME
    boot = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToString('s')
    tasks = $tasks
    primals = $primals
    primals_missing = $missing
    listeners = $ports
    eyes = $eyes
    repo = $repo
    new_seams = $newSeams
    inventory = @{ tasks = $taskNames; run_keys = $runKeys; startup = $startupItems }
}
$json = $threads | ConvertTo-Json -Depth 6
Set-Content -Path $threadsFile -Value $json -Encoding utf8
Add-Content $logFile "  loose threads -> boot-threads.json (missing primals: $($missing.Count), repo ahead: $($repo.ahead), uncommitted: $($repo.uncommitted))"

# heartbeat line into the neutron mail spine
$beat = @{ ts = $ts; author = 'boot-watcher'; channel = 'boot'
    body = "reboot seams: primals $($expected.Count - $missing.Count)/$($expected.Count), eastGate wire forge=$($eyes.eastGate_wire.forge), repo ahead $($repo.ahead), uncommitted $($repo.uncommitted), new seams $($newSeams.tasks.Count + $newSeams.run_keys.Count + $newSeams.startup.Count). lub-DUB."
} | ConvertTo-Json -Compress
Add-Content -Path "$gaia\data\neutron\boot.jsonl" -Value $beat

# carry the record to eastGate - commit only these two files, same circuit the body already uses
try {
    Push-Location $gaia
    git add -- data/gut/boot-threads.json data/neutron/boot.jsonl 2>$null | Out-Null
    git -c core.safecrlf=false commit -q -m "boot watcher: loose threads $ts (Wave 262.mesh)" 2>$null | Out-Null
    if ($eyes.eastGate_wire.forge -or $eyes.eastGate_wifi.forge) {
        git push eastgate main 2>$null | Out-Null
        Add-Content $logFile "  boot threads pushed to eastGate."
    } else {
        Add-Content $logFile "  eastGate dark - boot threads held locally for next boot."
    }
    Pop-Location
} catch { try { Pop-Location } catch {} ; Add-Content $logFile "  boot-threads commit/push skipped: $_" }

# Announce
Add-Content $logFile "=== GAIA WATCHER COMPLETE - $(Get-Date -Format 'HH:mm:ss') ==="
