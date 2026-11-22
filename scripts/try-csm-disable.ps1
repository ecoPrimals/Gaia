
$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement
$r = Invoke-CimMethod -InputObject $inst -MethodName "SetOptionData" -Arguments @{OptionName="CsmSupport"; Value=[uint32]0}
Write-Output "CsmSupport disable: Error=$($r.ErrorCode)"

# Also try alternate names
$names = @("Launch CSM", "CSM Support", "CsmSupport", "CSM")
foreach ($n in $names) {
    try {
        $r2 = Invoke-CimMethod -InputObject $inst -MethodName "SetOptionData" -Arguments @{OptionName=$n; Value=[uint32]0}
        Write-Output "$n disable: Error=$($r2.ErrorCode)"
    } catch {}
}
