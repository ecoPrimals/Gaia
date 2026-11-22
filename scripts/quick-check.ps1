$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement
$uma = Invoke-CimMethod -InputObject $inst -MethodName "GetOptionData" -Arguments @{OptionName="UmaFrameBufferSize"}
$csm = Invoke-CimMethod -InputObject $inst -MethodName "GetOptionData" -Arguments @{OptionName="CsmSupport"}
$igpu = Invoke-CimMethod -InputObject $inst -MethodName "GetOptionData" -Arguments @{OptionName="IntegratedGraphics"}
$pv = Invoke-CimMethod -InputObject $inst -MethodName "GetOptionData" -Arguments @{OptionName="PrimaryVideo"}

Write-Output "=== POST-REBOOT 1 CHECK ==="
Write-Output "UMA Frame Buffer: $($uma.Value) (expect != 4294967295)"
Write-Output "CSM Support: $($csm.Value) (expect 0)"
Write-Output "Integrated Graphics: $($igpu.Value)"
Write-Output "Primary Video: $($pv.Value)"

if ($uma.Value -eq 4294967295) {
    Write-Output "`nUMA UNCHANGED - modGRUBShell may not have written"
} else {
    Write-Output "`nUMA CHANGED! Value=$($uma.Value)"
}

Write-Output "`n=== Display Devices ==="
Get-PnpDevice -Class Display | Format-Table FriendlyName,Status -AutoSize

Write-Output "`n=== Monitors ==="
Get-PnpDevice -Class Monitor | Format-Table FriendlyName,Status -AutoSize

Write-Output "`n=== iGPU Audio ==="
Get-PnpDevice | Where-Object { $_.InstanceId -like "*1002*1640*" } | Format-Table FriendlyName,Status -AutoSize
