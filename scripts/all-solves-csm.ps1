
$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement

# Check CSM-related settings
$settings = @("CsmSupport", "Launch CSM", "CSM Support", "BootMode", 
              "SecureBoot", "OpROM", "Launch PXE", "Network Stack",
              "IntegratedGraphics", "PrimaryVideo", "UmaFrameBufferSize",
              "IGDMultiMonitor", "iGPU Multi-Monitor", "NbConfiguration",
              "ResizeBar", "ReBar", "Above4GDecoding", "Above 4G Decoding",
              "Iommu", "IOMMU", "SVM Mode")

foreach ($s in $settings) {
    try {
        $r = Invoke-CimMethod -InputObject $inst -MethodName "GetOptionData" -Arguments @{OptionName=$s}
        if ($r.ErrorCode -eq 0) {
            Write-Output ("  $s = $($r.Value)")
        }
    } catch {}
}

# Also check Secure Boot state
$sb = Confirm-SecureBootUEFI
Write-Output ("  SecureBootActive = $sb")

# Check boot mode
$fw = bcdedit /enum firmware 2>&1 | Out-String
Write-Output $fw
