# AMD_ACPI + ASUSManagement WMI — The user-free write path
# These are ACPI methods that bypass Windows EFI write protection

Write-Host "=== AMD_ACPI + ASUS WMI DEEP DIVE ==="

# === 1. AMD_ACPI (AMD Overclocking Driver) ===
Write-Host "`n--- AMD_ACPI Class ---"
try {
    $amdClass = Get-CimClass -Namespace "root\WMI" -ClassName "AMD_ACPI" -ErrorAction Stop
    Write-Host "  Properties:"
    foreach ($p in $amdClass.CimClassProperties) {
        Write-Host ("    {0} [{1}] Quals={2}" -f $p.Name, $p.CimType, ($p.Qualifiers | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join ",")
    }
    Write-Host "  Methods:"
    foreach ($m in $amdClass.CimClassMethods) {
        $params = ($m.Parameters | ForEach-Object { "$($_.Name):$($_.CimType)" }) -join ", "
        Write-Host ("    {0}({1})" -f $m.Name, $params)
    }
    
    # Get instances
    $amdInst = Get-CimInstance -Namespace "root\WMI" -ClassName "AMD_ACPI" -ErrorAction Stop
    foreach ($inst in $amdInst) {
        Write-Host "  Instance: $($inst.InstanceName)"
        foreach ($p in $inst.CimInstanceProperties) {
            if ($null -ne $p.Value -and $p.Value -ne "") {
                $val = $p.Value
                if ($val -is [byte[]]) { $val = "byte[$($val.Length)]" }
                Write-Host ("    {0} = {1}" -f $p.Name, $val)
            }
        }
    }
} catch { Write-Host "  Error: $($_.Exception.Message)" }

# === 2. ASUSManagement ===
Write-Host "`n--- ASUSManagement Class ---"
try {
    $asusClass = Get-CimClass -Namespace "root\WMI" -ClassName "ASUSManagement" -ErrorAction Stop
    Write-Host "  Properties:"
    foreach ($p in $asusClass.CimClassProperties) {
        Write-Host ("    {0} [{1}]" -f $p.Name, $p.CimType)
    }
    Write-Host "  Methods:"
    foreach ($m in $asusClass.CimClassMethods) {
        $params = ($m.Parameters | ForEach-Object { "$($_.Name):$($_.CimType)" }) -join ", "
        Write-Host ("    {0}({1})" -f $m.Name, $params)
    }
    
    $asusInst = Get-CimInstance -Namespace "root\WMI" -ClassName "ASUSManagement" -ErrorAction Stop
    foreach ($inst in $asusInst) {
        Write-Host "  Instance: $($inst.InstanceName)"
    }
} catch { Write-Host "  Error: $($_.Exception.Message)" }

# === 3. ALL ASUS WMI classes ===
Write-Host "`n--- All ASUS/AMD WMI Classes ---"
try {
    Get-CimClass -Namespace "root\WMI" -ErrorAction Stop | Where-Object { $_.CimClassName -match '^(ASUS|AMD|Asus|amd)' } | ForEach-Object {
        $methods = ($_.CimClassMethods | ForEach-Object { $_.Name }) -join ", "
        Write-Host ("  {0} methods=[{1}]" -f $_.CimClassName, $methods)
    }
} catch {}

# === 4. Try ASUSManagement methods ===
Write-Host "`n--- Trying ASUSManagement methods ---"
try {
    $asusInst = Get-CimInstance -Namespace "root\WMI" -ClassName "ASUSManagement" -ErrorAction Stop | Select-Object -First 1
    
    # Common ASUS WMI method patterns: 
    # DEVS (Device Status), DSTS (Device Settings), BSOF/BSIF (BIOS setting)
    $asusMethods = (Get-CimClass -Namespace "root\WMI" -ClassName "ASUSManagement").CimClassMethods
    foreach ($m in $asusMethods) {
        Write-Host "  Method: $($m.Name)"
        $params = $m.Parameters
        foreach ($p in $params) {
            Write-Host ("    Param: {0} [{1}] {2}" -f $p.Name, $p.CimType, $(if($p.Qualifiers | Where-Object { $_.Name -eq 'in' }){'IN'}else{'OUT'}))
        }
    }
} catch { Write-Host "  Error: $($_.Exception.Message)" }

# === 5. NVIDIA WMI ===
Write-Host "`n--- NVIDIA WMI ---"
try {
    Get-CimClass -Namespace "root\WMI" -ErrorAction Stop | Where-Object { $_.CimClassName -match '^Nv' } | ForEach-Object {
        $methods = ($_.CimClassMethods | ForEach-Object { $_.Name }) -join ", "
        Write-Host ("  {0} methods=[{1}]" -f $_.CimClassName, $methods)
    }
} catch {}

# === 6. Try AMD_ACPI methods ===
Write-Host "`n--- Trying AMD_ACPI methods ---"
try {
    $amdInst = Get-CimInstance -Namespace "root\WMI" -ClassName "AMD_ACPI" -ErrorAction Stop | Select-Object -First 1
    $amdMethods = (Get-CimClass -Namespace "root\WMI" -ClassName "AMD_ACPI").CimClassMethods
    foreach ($m in $amdMethods) {
        Write-Host "  Method: $($m.Name)"
        $params = $m.Parameters
        foreach ($p in $params) {
            $direction = if ($p.Qualifiers | Where-Object { $_.Name -eq 'in' }) { 'IN' } elseif ($p.Qualifiers | Where-Object { $_.Name -eq 'out' }) { 'OUT' } else { '?' }
            Write-Host ("    {0} [{1}] {2}" -f $p.Name, $p.CimType, $direction)
        }
        
        # Try calling read-only methods
        if ($m.Name -match 'Get|Read|Query|Status|Info|List') {
            try {
                $result = Invoke-CimMethod -InputObject $amdInst -MethodName $m.Name -ErrorAction Stop
                Write-Host "    Result: $($result | ConvertTo-Json -Compress -Depth 2)"
            } catch {
                Write-Host "    Call failed: $($_.Exception.Message.Substring(0, [Math]::Min(80, $_.Exception.Message.Length)))"
            }
        }
    }
} catch { Write-Host "  Error: $($_.Exception.Message)" }

Write-Host "`n=== SUMMARY ==="
Write-Host "If AMD_ACPI or ASUSManagement have write methods, we can modify BIOS from Windows!"
