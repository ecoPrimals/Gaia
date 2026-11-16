# ASUS WMI ZK POOL — Read ALL known UEFI options through ASUSManagement WMI
# No admin needed! ASUS ROG motherboard exposes these directly.
$gutDir = "c:\Users\mokke\Desktop\Gaia\data\gut"
$ts = Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"

Write-Host "=== ASUS WMI ZK POOL ===" -ForegroundColor Cyan

$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement -ErrorAction SilentlyContinue
if (-not $inst) {
    Write-Host "  ASUSManagement WMI class not found!" -ForegroundColor Red
    exit 1
}

# Known ASUS WMI option names
$options = @(
    "UmaFrameBufferSize",
    "IntegratedGraphics",
    "CsmSupport",
    "AboveForGBMemorySupport",
    "ResizableBarSupport",
    "SvmMode",
    "SmtMode",
    "SmtControl",
    "CcdMode",
    "PrimaryDisplay",
    "PrimaryVideo",
    "InitDisplayFirst",
    "IommuSupport",
    "AmdCpuTSME",
    "SecureBoot",
    "SecureBootMode",
    "TpmDevice",
    "FtpmSwitch",
    "PlatformTrustTechnology",
    "SataMode",
    "NvmeConfiguration",
    "M2Configuration",
    "PcieSpeed",
    "PcieLinkSpeed",
    "PcieSlotSpeed",
    "PcieLaneSwitching",
    "PcieGenSupport",
    "XmpProfile",
    "ExpoProfile",
    "MemoryFrequency",
    "FclkFrequency",
    "UclkMode",
    "PowerLoadingControl",
    "ErpReady",
    "WakeOnLan",
    "WakeOnPme",
    "FastBoot",
    "BootOptionPriority",
    "AmdPboMode",
    "AmdPboLimits",
    "CpuCoreCount",
    "CpuCoreEnabled",
    "CpuMultiThreading",
    "GlobalCStateControl",
    "PcieAspm",
    "PciePowerManagement",
    "AcpiSlit",
    "NumaNodesPerSocket",
    "PcieNvmeSlot1",
    "PcieNvmeSlot2",
    "PcieNvmeSlot3",
    "PcieNvmeSlot4",
    "M2_1",
    "M2_2",
    "M2_3",
    "M2_4",
    "AmdAbove4GDecoding",
    "AmdReBar"
)

$pool = @{}
$found = 0
$errors = 0

foreach ($opt in $options) {
    try {
        $r = Invoke-CimMethod -InputObject $inst -MethodName GetOptionData -Arguments @{OptionName=$opt} -ErrorAction Stop
        $val = $r.Value
        $pool[$opt] = $val
        $found++
        
        # Decode known values
        $decoded = switch ($opt) {
            "IntegratedGraphics" { @{0="Disabled"; 1="Force"; 2="Auto"}[$val] }
            "CsmSupport" { @{0="Disabled"; 1="Enabled"}[$val] }
            "SvmMode" { @{0="Disabled"; 1="Enabled"}[$val] }
            "SmtMode" { @{0="Disabled"; 1="Enabled"; 2="Auto"}[$val] }
            "SecureBoot" { @{0="Disabled"; 1="Enabled"}[$val] }
            "UmaFrameBufferSize" { if($val -eq 4294967295){"Auto/None (0xFFFFFFFF)"}else{"${val}MB"} }
            default { $null }
        }
        
        if ($decoded) {
            Write-Host "  ZK $opt = $val ($decoded)" -ForegroundColor Green
        } else {
            Write-Host "  ZK $opt = $val" -ForegroundColor Green
        }
    } catch {
        $errors++
        # Don't print every miss — just count
    }
}

Write-Host "`n  Found: $found / $($options.Count) options ($errors not available)" -ForegroundColor Cyan

# Save ZK pool
$zkPool = @{
    ts = $ts
    source = "ASUS WMI ASUSManagement"
    motherboard = "ROG STRIX X870E-E GAMING WIFI"
    found = $found
    errors = $errors
    pool = $pool
}

$zkPool | ConvertTo-Json -Depth 3 | Out-File "$gutDir\asus-wmi-zk-pool.json" -Encoding utf8
Write-Host "`n  ZK POOL: $gutDir\asus-wmi-zk-pool.json" -ForegroundColor Green
