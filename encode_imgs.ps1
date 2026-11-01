$gaiaRoot = $PSScriptRoot
$paintings = @(
  "249-spirit-eye-octave-spire.jpg",
  "248-generations-backscatter.jpg",
  "247-golgi-inversion-vision.jpg",
  "246-url-is-anatomy.jpg",
  "245-chemistry-salt-cut-guilty-body.jpg"
)
$dir = Join-Path $gaiaRoot "paintings"
$outDir = Join-Path $gaiaRoot "img_b64"
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }

foreach ($p in $paintings) {
  $path = Join-Path $dir $p
  if (Test-Path $path) {
    $bytes = [IO.File]::ReadAllBytes($path)
    $b64 = [Convert]::ToBase64String($bytes)
    $outFile = Join-Path $outDir ($p -replace '\.jpg$', '.txt')
    [IO.File]::WriteAllText($outFile, $b64)
    Write-Host "$p -> $($b64.Length) chars"
  } else {
    Write-Host "$p NOT FOUND"
  }
}
