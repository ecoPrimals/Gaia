# WMI unlock attempt — correct parameter names
$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement

# 1. Check password with empty (is BIOS password-protected?)
Write-Output "=== PASSWORD CHECK ==="
$pw1 = Invoke-CimMethod -InputObject $inst -MethodName CheckPassword -Arguments @{CurrentPassword=""}
Write-Output "Empty password: ErrorCode=$($pw1.ErrorCode)"

$pw2 = Invoke-CimMethod -InputObject $inst -MethodName CheckPassword -Arguments @{CurrentPassword="579163"}
Write-Output "PIN 579163: ErrorCode=$($pw2.ErrorCode)"

# 2. Try SetFastBoot with correct param name (SetValue)
Write-Output "`n=== SET FAST BOOT ==="
$fb = Invoke-CimMethod -InputObject $inst -MethodName SetFastBoot -Arguments @{SetValue=[byte]0}
Write-Output "SetFastBoot(0): ErrorCode=$($fb.ErrorCode)"

# Verify
$fbr = Invoke-CimMethod -InputObject $inst -MethodName GetOptionData -Arguments @{OptionName="FastBoot"}
Write-Output "FastBoot readback: $($fbr.Value)"

# 3. Try SetOptionDefault (reset to factory default)
Write-Output "`n=== SET OPTION DEFAULT ==="
try {
    $cls = Get-CimClass -Namespace root/WMI -ClassName ASUSManagement
    $sod = $cls.CimClassMethods | Where-Object { $_.Name -eq "SetOptionDefault" }
    Write-Output "SetOptionDefault parameters:"
    $sod.Parameters | ForEach-Object { Write-Output "  $($_.Name) : $($_.CimType)" }
    
    $def = Invoke-CimMethod -InputObject $inst -MethodName SetOptionDefault -Arguments @{OptionName="Above4GDecoding"; Value=[uint32]1}
    Write-Output "SetOptionDefault(Above4GDecoding,1): ErrorCode=$($def.ErrorCode)"
} catch {
    Write-Output "SetOptionDefault error: $_"
}

# 4. Check ALL critical settings current values
Write-Output "`n=== CURRENT STATE ==="
$settings = @("Above4GDecoding","ResizableBar","FastBoot","SvmMode")
foreach ($s in $settings) {
    $v = Invoke-CimMethod -InputObject $inst -MethodName GetOptionData -Arguments @{OptionName=$s}
    Write-Output "  $s = $($v.Value) (ErrorCode=$($v.ErrorCode))"
}

# 5. Try SetDeviceControl
Write-Output "`n=== SetDeviceControl signature ==="
$sdc = $cls.CimClassMethods | Where-Object { $_.Name -eq "SetDeviceControl" }
$sdc.Parameters | ForEach-Object { Write-Output "  $($_.Name) : $($_.CimType)" }
