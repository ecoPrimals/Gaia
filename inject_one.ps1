param([string]$File, [string]$Title, [int]$Index)
$gaiaRoot = Split-Path -Parent $PSScriptRoot
if (-not $gaiaRoot) { $gaiaRoot = $PSScriptRoot }
$path = Join-Path $gaiaRoot "paintings\$File"
$bytes = [IO.File]::ReadAllBytes($path)
$b64 = [Convert]::ToBase64String($bytes)
$titleEsc = $Title -replace "'", "\'"
$js = "window._gaiaEyeState.paintings.push({b64:'$b64',title:'$titleEsc'});if(window._gaiaEyeState.paintings.length===1)window._gaiaEyeShowPainting(0);'added:$titleEsc'"
[IO.File]::WriteAllText((Join-Path $gaiaRoot "inject_p$Index.js"), $js)
Write-Host "inject_p$Index.js: $($js.Length) chars"
