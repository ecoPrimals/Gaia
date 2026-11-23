# Test ASUS WMI BIOS write — single setting
# Must run as Administrator
$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement
$r = Invoke-CimMethod -InputObject $inst -MethodName SetOptionData -Arguments @{OptionName="Above4GDecoding"; Value=1}
$r | Format-List *
Write-Output "ReturnValue: $($r.ReturnValue)"

# Also try alternate method names
try {
    $r2 = Invoke-CimMethod -InputObject $inst -MethodName SetBIOSSetting -Arguments @{OptionName="Above4GDecoding"; Value="1"}
    Write-Output "SetBIOSSetting: $($r2.ReturnValue)"
} catch {
    Write-Output "SetBIOSSetting: not available"
}

try {
    $r3 = Invoke-CimMethod -InputObject $inst -MethodName SetCurrentValue -Arguments @{OptionName="Above4GDecoding"; CurrentValue="1"}
    Write-Output "SetCurrentValue: $($r3.ReturnValue)"
} catch {
    Write-Output "SetCurrentValue: not available"
}

# Check available methods
$cls = Get-CimClass -Namespace root/WMI -ClassName ASUSManagement
Write-Output "`nAvailable methods:"
$cls.CimClassMethods | ForEach-Object { Write-Output "  $($_.Name)" }
