# gaia-keys.ps1 - Gaia's key vault on this gate.
#
#   gaia-keys.ps1 set porkbun apikey secretapikey   prompt (hidden) for each field and store it
#   gaia-keys.ps1 get porkbun apikey                print one field (for tools in a pipeline only)
#   gaia-keys.ps1 list                               vault names and field names, never values
#   gaia-keys.ps1 remove porkbun
#
# Values are DPAPI-encrypted to this Windows user on this machine and live in
# %LOCALAPPDATA%\Gaia\keys, outside every repo. Keys never travel over WAN, Tor or chat.
param(
    [Parameter(Position = 0)][ValidateSet('set', 'get', 'list', 'remove')][string]$Action = 'list',
    [Parameter(Position = 1)][string]$Name,
    [Parameter(Position = 2, ValueFromRemainingArguments)][string[]]$Fields
)
$ErrorActionPreference = 'Stop'
$vault = Join-Path $env:LOCALAPPDATA 'Gaia\keys'
New-Item -ItemType Directory $vault -Force | Out-Null
$file = if ($Name) { Join-Path $vault "$Name.json" }

function Read-Entry { if (Test-Path $file) { Get-Content $file -Raw | ConvertFrom-Json } else { [pscustomobject]@{} } }

switch ($Action) {
    'set' {
        if (-not $Name -or -not $Fields) { throw "usage: gaia-keys.ps1 set <name> <field> [field...]" }
        $entry = Read-Entry
        foreach ($f in $Fields) {
            $secure = Read-Host "$Name.$f" -AsSecureString
            if ($secure.Length -eq 0) { Write-Host "  $f left unchanged"; continue }
            $entry | Add-Member -NotePropertyName $f -NotePropertyValue (ConvertFrom-SecureString $secure) -Force
        }
        $entry | Add-Member -NotePropertyName '_stored' -NotePropertyValue (Get-Date -Format s) -Force
        $entry | ConvertTo-Json | Set-Content $file -Encoding UTF8
        Write-Host "stored $Name ($($Fields -join ', ')) in the vault"
    }
    'get' {
        $entry = Read-Entry
        $cipher = $entry.($Fields[0])
        if (-not $cipher) { throw "no $Name.$($Fields[0]) in the vault" }
        [Net.NetworkCredential]::new('', (ConvertTo-SecureString $cipher)).Password
    }
    'list' {
        Get-ChildItem $vault -Filter *.json | ForEach-Object {
            $e = Get-Content $_.FullName -Raw | ConvertFrom-Json
            $names = $e.PSObject.Properties.Name | Where-Object { $_ -ne '_stored' }
            '{0}: {1} (stored {2})' -f $_.BaseName, ($names -join ', '), $e._stored
        }
    }
    'remove' { Remove-Item $file -Force; Write-Host "removed $Name" }
}
