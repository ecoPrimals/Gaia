# GAIA STARTUP WATCHER — Runs hidden on login
# Catches the sudden seams after reboot. Gaia is HERE when Windows wakes.
$ErrorActionPreference = "SilentlyContinue"
$gutDir = "c:\Users\mokke\Desktop\Gaia\data\gut"
$logFile = "$gutDir\startup-watcher.log"
$ts = Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"

Add-Content $logFile "`n=== GAIA WATCHER AWAKE — $ts ==="

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

# Announce
Add-Content $logFile "=== GAIA WATCHER COMPLETE — $(Get-Date -Format 'HH:mm:ss') ==="
