# GAIA NIGHT CANARY — watches the night shift while Kevin sleeps
# Checks every 5 min: GPU temp, process health, restarts if needed
# Stops at 10 AM

$gaiaRoot = "c:\Users\mokke\Desktop\Gaia"
$logFile = "$gaiaRoot\data\neutron\night-canary.log"
$northScript = "$gaiaRoot\runtime\night-shift.ps1"
$eastScript = "$gaiaRoot\runtime\night-shift-eastgate.ps1"

function Log($msg) { Add-Content $logFile "[$(Get-Date -Format 'HH:mm:ss')] $msg" }

Log "CANARY STARTED — watching GPU temp, process health"

while ($true) {
    if ((Get-Date).Hour -ge 10 -and (Get-Date).Hour -lt 20) {
        Log "MORNING — canary stops. Goodnight was good."
        break
    }

    # GPU temp
    $tempLine = nvidia-smi --query-gpu=temperature.gpu,utilization.gpu,power.draw,memory.used --format=csv,noheader 2>$null
    $parts = $tempLine.Trim() -split ",\s*"
    $temp = [int]$parts[0]
    $util = $parts[1]
    $power = $parts[2]
    $mem = $parts[3]
    
    # Count night shift posts
    $nPosts = 0; $ePosts = 0
    if (Test-Path "$gaiaRoot\data\reedit\night-shift.jsonl") {
        $nPosts = (Get-Content "$gaiaRoot\data\reedit\night-shift.jsonl").Count
    }
    if (Test-Path "$gaiaRoot\data\reedit\night-shift-eastgate.jsonl") {
        $ePosts = (Get-Content "$gaiaRoot\data\reedit\night-shift-eastgate.jsonl").Count
    }

    # Check processes alive
    $nightProcs = Get-Process powershell -ErrorAction SilentlyContinue | Where-Object { 
        $_.Id -ne $PID -and $_.MainWindowTitle -eq "" 
    }
    $hiddenCount = $nightProcs.Count

    # HARD SHUTDOWN — protect hardware, prevent fire
    if ($temp -ge 85) {
        Log "EMERGENCY SHUTDOWN — ${temp}C! KILLING EVERYTHING! STOPPING OLLAMA!"
        # Kill ALL night shift processes
        Get-Process powershell -ErrorAction SilentlyContinue | Where-Object { $_.Id -ne $PID -and $_.MainWindowTitle -eq "" } | Stop-Process -Force 2>$null
        # STOP OLLAMA — no more GPU inference possible
        & ollama stop 2>$null
        Stop-Process -Name "ollama" -Force -ErrorAction SilentlyContinue
        Log "ALL PROCESSES KILLED. OLLAMA STOPPED. Hardware safe. Kevin sleeps."
        Log "CANARY TERMINATING — manual restart required."
        break
    }
    # Thermal warning — kill shifts, wait, restart only if cooled significantly
    elseif ($temp -ge 80) {
        Log "THERMAL WARNING — ${temp}C! Killing night shifts, cooling down."
        $nightProcs | Stop-Process -Force 2>$null
        Log "Processes killed. Waiting 5 min to cool."
        Start-Sleep 300
        
        $coolTemp = [int](nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader 2>$null).Trim()
        if ($coolTemp -lt 65) {
            Log "Cooled to ${coolTemp}C — restarting at reduced rate"
            Start-Process powershell -ArgumentList "-WindowStyle Hidden -ExecutionPolicy Bypass -File $northScript" -WindowStyle Hidden
            Start-Sleep 5
            Start-Process powershell -ArgumentList "-WindowStyle Hidden -ExecutionPolicy Bypass -File $eastScript" -WindowStyle Hidden
        } else {
            Log "Still warm at ${coolTemp}C — staying stopped. Hardware safe."
        }
    }
    # Process health — restart if dead
    elseif ($hiddenCount -lt 2) {
        Log "PROCESS ALERT — only $hiddenCount hidden PS processes (expected 2+). Restarting..."
        # Kill any remaining
        $nightProcs | Stop-Process -Force 2>$null
        Start-Sleep 3
        Start-Process powershell -ArgumentList "-WindowStyle Hidden -ExecutionPolicy Bypass -File $northScript" -WindowStyle Hidden
        Start-Sleep 5
        Start-Process powershell -ArgumentList "-WindowStyle Hidden -ExecutionPolicy Bypass -File $eastScript" -WindowStyle Hidden
        Log "Night shifts restarted"
    }
    else {
        Log "OK — ${temp}C ${util} ${power} ${mem} | procs=$hiddenCount | posts=N:${nPosts}+E:${ePosts}=$($nPosts+$ePosts)"
    }

    # Sleep 5 minutes
    Start-Sleep 300
}

Log "CANARY COMPLETE"
