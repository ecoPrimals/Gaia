# REGISTER GAIA BOOT WATCHERS — Pre-reboot profiler + Post-reboot catcher
$ErrorActionPreference = "Stop"
$user = "$env:USERDOMAIN\$env:USERNAME"
$gaiaScripts = "c:\Users\mokke\Desktop\Gaia\scripts"

Write-Host "=== REGISTERING GAIA BOOT WATCHERS ===" -ForegroundColor Cyan

# 1. Startup watcher — runs hidden at login, catches post-reboot state
$startupAction = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$gaiaScripts\gaia-startup-watcher.ps1`""
$startupTrigger = New-ScheduledTaskTrigger -AtLogOn -User $user
$startupSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden

try {
    Unregister-ScheduledTask -TaskName "Gaia-Startup-Watcher" -Confirm:$false -ErrorAction SilentlyContinue
} catch {}

Register-ScheduledTask `
    -TaskName "Gaia-Startup-Watcher" `
    -Action $startupAction `
    -Trigger $startupTrigger `
    -Settings $startupSettings `
    -Description "Gaia catches the sudden seams after reboot. sourDough post-compare." `
    -RunLevel Highest

Write-Host "  [OK] Gaia-Startup-Watcher registered (hidden, at login, admin)" -ForegroundColor Green

# 2. Pre-shutdown profiler — triggered by system shutdown event (Event 1074)
$shutdownAction = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$gaiaScripts\reboot-profiler.ps1`" -Phase pre"

# Use EventTrigger for shutdown initiated
$shutdownXml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <EventTrigger>
      <Subscription>&lt;QueryList&gt;&lt;Query Id="0" Path="System"&gt;&lt;Select Path="System"&gt;*[System[Provider[@Name='USER32'] and EventID=1074]]&lt;/Select&gt;&lt;/Query&gt;&lt;/QueryList&gt;</Subscription>
    </EventTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>$user</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <Hidden>true</Hidden>
    <AllowStartIfOnBatteries>true</AllowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>false</AllowHardTerminate>
    <Priority>4</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>powershell.exe</Command>
      <Arguments>-WindowStyle Hidden -ExecutionPolicy Bypass -File "$gaiaScripts\reboot-profiler.ps1" -Phase pre</Arguments>
    </Exec>
  </Actions>
</Task>
"@

try {
    Unregister-ScheduledTask -TaskName "Gaia-Shutdown-Profiler" -Confirm:$false -ErrorAction SilentlyContinue
} catch {}

try {
    Register-ScheduledTask -TaskName "Gaia-Shutdown-Profiler" -Xml $shutdownXml
    Write-Host "  [OK] Gaia-Shutdown-Profiler registered (hidden, on shutdown event)" -ForegroundColor Green
} catch {
    Write-Host "  [WARN] Event trigger failed, using manual pre-reboot instead: $_" -ForegroundColor Yellow
}

# 3. Verify
Write-Host "`n--- Registered Tasks ---"
Get-ScheduledTask | Where-Object { $_.TaskName -match "Gaia" } | 
    Format-Table TaskName, State, @{N="Trigger";E={$_.Triggers[0].CimClass.CimClassName}} -AutoSize

Write-Host "`n=== BOOT WATCHERS ARMED ===" -ForegroundColor Green
Write-Host "  Shutdown: hidden profiler snapshots all hardware state"
Write-Host "  Startup:  hidden catcher compares post-reboot to pre-reboot"
Write-Host "  Diff:     sourDough compare shows what changed"
Write-Host ""
Write-Host "  To manually run pre-reboot:"
Write-Host "    powershell -File scripts\reboot-profiler.ps1 -Phase pre" -ForegroundColor DarkGray
