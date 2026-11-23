# Primal process scan + biomeOS config + plasmidBin
Write-Host "=== PRIMAL PROCESSES ==="
$primals = Get-Process | Where-Object { $_.ProcessName -match 'biomeos|songbird|squirrel|beardog|nestgate|sweetgrass|barracuda|coralreef|loamspine|skunkbat|swarmvine|toadstool|rhizocrypt|petaltongue' }
$primals | Group-Object ProcessName | ForEach-Object { Write-Host ("  " + $_.Name + ": " + $_.Count + " pids") }
Write-Host ("`n  Total: " + $primals.Count + " primal processes")

Write-Host "`n=== biomeOS PATH ==="
$bio = Get-Process biomeos -ErrorAction SilentlyContinue | Select-Object -First 1
if ($bio) { Write-Host ("  " + $bio.Path) }

Write-Host "`n=== ProgramData dirs ==="
foreach ($d in @("C:\ProgramData\biomeOS", "C:\ProgramData\songbird")) {
    if (Test-Path $d) {
        Write-Host "  $d :"
        Get-ChildItem $d | ForEach-Object { Write-Host ("    " + $_.Name + " " + $_.Length + " bytes") }
    }
}

Write-Host "`n=== plasmidBin ==="
$pb = "C:\Users\mokke\Desktop\Gaia\plasmidBin\primals"
if (Test-Path $pb) {
    Get-ChildItem $pb | ForEach-Object { Write-Host ("  " + $_.Name + " " + [math]::Round($_.Length/1KB) + "KB") }
} else { Write-Host "  not found at $pb" }

Write-Host "`n=== LISTENING PORTS (primal) ==="
$primalPids = $primals.Id
Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | ForEach-Object {
    if ($primalPids -contains $_.OwningProcess) {
        $name = (Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).ProcessName
        Write-Host ("  :" + $_.LocalPort + " <- " + $name)
    }
}
