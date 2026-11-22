# Switch northGate from the five overlapping boot paths to the single boot ladder.
# Nothing is deleted: old tasks are disabled, the Startup .bat is moved aside.
# Undo with boot-ladder-rollback.ps1.

$ErrorActionPreference = "Stop"
$G       = "C:\Users\mokke\Desktop\Gaia"
$Home_   = "$env:LOCALAPPDATA\Gaia"
$Retired = "$Home_\retired"
$Startup = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$Bat     = "$Startup\biomeOS-AMALGAM-BOOT.bat"
$OldTasks = "GaiaGate", "Gaia-Startup-Watcher", "GaiaPostReboot", "GaiaLeftEyeWake", "GaiaTor"

New-Item -ItemType Directory -Force $Retired | Out-Null

# Identity env moves out of the Startup script into a local file the ladder reads.
if ((Test-Path $Bat) -and -not (Test-Path "$Home_\boot.env")) {
    Get-Content $Bat | Where-Object { $_ -match '^set (\w+)=(.*)$' } |
        ForEach-Object { "$($Matches[1])=$($Matches[2])" } |
        Set-Content "$Home_\boot.env" -Encoding ascii
}
if (Test-Path $Bat) { Move-Item $Bat "$Retired\" -Force }

foreach ($t in $OldTasks) {
    if (Get-ScheduledTask -TaskName $t -ErrorAction SilentlyContinue) {
        Disable-ScheduledTask -TaskName $t | Out-Null
    }
}

$action  = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$G\runtime\boot-ladder.ps1`""
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 15)
Register-ScheduledTask -TaskName "GaiaBootLadder" -Action $action -Trigger $trigger -Settings $settings `
    -Description "Gaia boot ladder: tor -> ollama -> biomeOS -> gate -> senses" -Force | Out-Null

Write-Output "ladder active; retired: $($OldTasks -join ', ') + Startup .bat"
