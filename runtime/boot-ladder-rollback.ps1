# Undo boot-ladder-activate.ps1: restore the old boot paths exactly as they were.

$ErrorActionPreference = "Continue"
$Retired = "$env:LOCALAPPDATA\Gaia\retired"
$Startup = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$OldTasks = "GaiaGate", "Gaia-Startup-Watcher", "GaiaPostReboot", "GaiaLeftEyeWake", "GaiaTor"

Unregister-ScheduledTask -TaskName "GaiaBootLadder" -Confirm:$false -ErrorAction SilentlyContinue
foreach ($t in $OldTasks) { Enable-ScheduledTask -TaskName $t -ErrorAction SilentlyContinue | Out-Null }
if (Test-Path "$Retired\biomeOS-AMALGAM-BOOT.bat") { Move-Item "$Retired\biomeOS-AMALGAM-BOOT.bat" "$Startup\" -Force }

Write-Output "old boot paths restored; ladder removed"
