$engineDir = $PSScriptRoot
$bat = Join-Path $engineDir 'BOOT-AMALGAM.bat'
$wd = $engineDir
$start = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs'
$desk = [Environment]::GetFolderPath('Desktop')
$shell = New-Object -ComObject WScript.Shell
foreach ($place in @($start, $desk)) {
  foreach ($name in @('Gaia.lnk', 'biomeOS.lnk')) {
    $l = $shell.CreateShortcut((Join-Path $place $name))
    $l.TargetPath = $bat
    $l.WorkingDirectory = $wd
    $l.WindowStyle = 1
    $l.Description = 'Gaia program like Steam OS. Not an app. biomeOS.'
    $l.Save()
  }
}
Get-ChildItem $start, $desk -Filter '*.lnk' | Where-Object { $_.Name -match 'Gaia|biomeOS' } | Select-Object FullName
