
$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement

$amd_settings = @(
    "GfxConfiguration", "iGPUConfiguration", "IGPUConfiguration",
    "IntegratedGraphicsController", "GFXOFF", "dGPUOnlyMode",
    "HybridGraphics", "SpecialDisplayFeatures", "PrimaryVideoAdaptor",
    "D3ColdSupport", "UmaVersion", "GfxUmaFrameBufferSize",
    "NbioCommonOptions", "GraphicsFeatures"
)

foreach ($s in $amd_settings) {
    try {
        $r = Invoke-CimMethod -InputObject $inst -MethodName "GetOptionData" -Arguments @{OptionName=$s}
        if ($r.ErrorCode -eq 0) {
            Write-Output ("  $s = $($r.Value)")
        }
    } catch {}
}
