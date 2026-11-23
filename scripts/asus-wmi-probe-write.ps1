# PROBE: Can ASUS WMI write? Check available methods.
$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement -ErrorAction SilentlyContinue

Write-Host "=== ASUS WMI — METHOD PROBE ===" -ForegroundColor Cyan

# List ALL methods on ASUSManagement
$class = Get-CimClass -Namespace root/WMI -ClassName ASUSManagement
Write-Host "`nMethods:"
foreach ($m in $class.CimClassMethods) {
    Write-Host "  $($m.Name)" -ForegroundColor Green
    foreach ($p in $m.Parameters) {
        Write-Host "    param: $($p.Name) [$($p.CimType)] $(if($p.Qualifiers['In']){'IN'}else{'OUT'})"
    }
}

Write-Host "`nProperties:"
foreach ($p in $class.CimClassProperties | Select-Object -First 20) {
    Write-Host "  $($p.Name) [$($p.CimType)]"
}

# Try a DRY probe of SetOptionData (read-back test with a SAFE value)
Write-Host "`n--- Testing SetOptionData availability ---"
try {
    # Just check if the method EXISTS, don't call it yet
    $hasSet = $class.CimClassMethods | Where-Object Name -eq "SetOptionData"
    if ($hasSet) {
        Write-Host "  SetOptionData: EXISTS!" -ForegroundColor Green
        foreach ($p in $hasSet.Parameters) {
            Write-Host "    param: $($p.Name) [$($p.CimType)]"
        }
    } else {
        Write-Host "  SetOptionData: NOT FOUND" -ForegroundColor Red
    }
} catch {
    Write-Host "  Error: $_" -ForegroundColor Red
}

# Also check for other ASUS WMI classes
Write-Host "`n--- All ASUS WMI classes ---"
Get-CimClass -Namespace root/WMI | Where-Object CimClassName -match "ASUS|Asus|asus" | 
    ForEach-Object { Write-Host "  $($_.CimClassName)" -ForegroundColor Yellow }
