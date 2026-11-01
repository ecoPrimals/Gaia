param([Parameter(Mandatory = $true)][string]$Path)
$uri = 'http://127.0.0.1:31415/share'
$body = @{ path = $Path } | ConvertTo-Json -Compress
try {
  Invoke-RestMethod -Uri $uri -Method POST -ContentType 'application/json; charset=utf-8' -Body $body | Out-Null
} catch {
  exit 1
}
