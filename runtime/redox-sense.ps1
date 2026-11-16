# redox-sense.ps1 — what did this boot bring? Reduction only: reads, records, then starts bubbling.
# Runs at logon (task GaiaRedoxSense, elevated for the firmware read). Appends one line per boot
# to data/spine/redox-boot.jsonl.

$ErrorActionPreference = "Continue"
$G = Split-Path $PSScriptRoot -Parent
Start-Sleep -Seconds 20   # let the display stack and drivers settle before judging them

$os = Get-CimInstance Win32_OperatingSystem
$gpus = Get-PnpDevice -Class Display -ErrorAction SilentlyContinue |
    ForEach-Object { [ordered]@{ name = $_.FriendlyName; status = "$($_.Status)"; problem = "$($_.Problem)" } }
Add-Type -AssemblyName System.Windows.Forms
$screens = [System.Windows.Forms.Screen]::AllScreens |
    ForEach-Object { "$($_.DeviceName) $($_.Bounds.Width)x$($_.Bounds.Height)$(if ($_.Primary) { ' primary' })" }
$dumps = Get-ChildItem C:\Windows\LiveKernelReports -Recurse -Filter *.dmp -ErrorAction SilentlyContinue |
    Where-Object LastWriteTime -gt $os.LastBootUpTime | ForEach-Object Name
$firmware = & powershell -NoProfile -ExecutionPolicy Bypass -File "$G\runtime\firmware-redox.ps1" 2>&1 | ForEach-Object { "$_" }

$entry = [ordered]@{
    boot = $os.LastBootUpTime.ToString("yyyy-MM-ddTHH:mm:ss")
    sensed = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
    bios = (Get-CimInstance Win32_BIOS).SMBIOSBIOSVersion
    gpus = @($gpus); screens = @($screens); gpu_dumps_this_boot = @($dumps); firmware = @($firmware)
}
Add-Content "$G\data\spine\redox-boot.jsonl" ($entry | ConvertTo-Json -Compress -Depth 4)

$pin = "$G\primals\squirrel\target\release\gaia-pin.exe"
if ((Test-Path $pin) -and -not (Get-Process gaia-pin -ErrorAction SilentlyContinue)) {
    Start-Process $pin -WindowStyle Hidden
}

$bubble = "$G\primals\squirrel\target\release\gaia-bubble.exe"
$paused = Test-Path "$env:LOCALAPPDATA\Gaia\bubbles\PAUSE"   # A/B tests: the watcher stays off while this exists
if (-not $paused -and (Test-Path $bubble) -and -not (Get-Process gaia-bubble -ErrorAction SilentlyContinue)) {
    Start-Process $bubble -ArgumentList "watch", "30" -WindowStyle Hidden
}
