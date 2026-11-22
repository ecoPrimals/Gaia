# ASUS WMI — Read/Write BIOS settings from Windows!
# THIS IS THE USER-FREE PATH

Write-Host "=== ASUS WMI — BIOS SETTINGS ==="

$asus = Get-CimInstance -Namespace "root\WMI" -ClassName "ASUSManagement" | Select-Object -First 1

# === 1. Try common iGPU option names ===
Write-Host "`n--- Probing BIOS Option Names ---"
$optionNames = @(
    "Integrated Graphics",
    "iGPU Multi-Monitor",
    "iGPU",
    "IGD",
    "Internal Graphics",
    "Primary Display",
    "Primary Video Adaptor",
    "Primary Video Device",
    "Init Display First",
    "Initiate Graphic Adapter",
    "GFX Configuration",
    "UMA Frame Buffer Size",
    "UMA Mode",
    "UMA Size",
    "IGFX",
    "GfxMode",
    "AMD CBS",
    "NBIO Common Options",
    "Display Configuration",
    "GFX",
    "Integrated Graphics Configuration",
    "iGPU Configuration",
    "AmdCbsIGpuControl",
    "CbsIGpuControl",
    "IGpuControl",
    "IGPU Control",
    "GnbGfxMode",
    "Above 4G Decoding",
    "Re-Size BAR Support",
    "SR-IOV Support",
    "Fast Boot",
    "CSM Support",
    "Secure Boot",
    "SMT Mode",
    "SVM Mode",
    "NX Mode",
    "Precision Boost Overdrive",
    "Core Performance Boost",
    "Global C-state Control",
    "IOMMU",
    "AmdCbsDbgGnbGfxiGPU",
    "CbsGnbGfxiGPUControl"
)

$found = @()
foreach ($name in $optionNames) {
    try {
        $result = Invoke-CimMethod -InputObject $asus -MethodName "GetOptionData" -Arguments @{OptionName=$name}
        $errCode = $result.ErrorCode
        $value = $result.Value
        if ($errCode -eq 0) {
            Write-Host ("  [FOUND] '{0}' = {1} (0x{1:X})" -f $name, $value)
            $found += @{ name=$name; value=$value }
        } else {
            Write-Host ("  [err={0}] '{1}'" -f $errCode, $name)
        }
    } catch {
        Write-Host ("  [FAIL] '{0}' -> {1}" -f $name, $_.Exception.Message.Substring(0, [Math]::Min(50, $_.Exception.Message.Length)))
    }
}

# === 2. Try SetDeviceControl for iGPU ===
Write-Host "`n--- Device Control Probe ---"
$deviceNames = @("iGPU", "IGD", "Integrated Graphics", "GPU", "AMD iGPU", "Radeon", "Display")
foreach ($dev in $deviceNames) {
    try {
        $result = Invoke-CimMethod -InputObject $asus -MethodName "device_status" -Arguments @{device_id=[uint32]0x00060013}
        Write-Host ("  device_status(0x60013) = ctrl_param={0}" -f $result.ctrl_param)
        break
    } catch {}
}

# === 3. Read PCI config space for dead root ports ===
Write-Host "`n--- PCI Config Read (dead root ports) ---"
# RP05 = bus 0, dev 1, func 3
# RP06 = bus 0, dev 1, func 4
foreach ($rp in @(
    @{name="RP03 (RTX5090)"; bus=0; dev=1; func=1},
    @{name="RP04 (NVMe 1TB OK)"; bus=0; dev=1; func=2},
    @{name="RP05 (Samsung 4TB ghost)"; bus=0; dev=1; func=3},
    @{name="RP06 (WD BLACK 4TB ghost)"; bus=0; dev=1; func=4}
)) {
    try {
        # Read vendor/device ID (reg 0, width 4)
        $result = Invoke-CimMethod -InputObject $asus -MethodName "asio_hw_fun11" -Arguments @{
            Bus=[byte]$rp.bus; Dev=[byte]$rp.dev; Func=[byte]$rp.func; Reg=[uint16]0; Width=[byte]4
        }
        $venDev = $result.dwData
        $vendor = $venDev -band 0xFFFF
        $device = ($venDev -shr 16) -band 0xFFFF
        
        # Read status/command (reg 4)
        $result2 = Invoke-CimMethod -InputObject $asus -MethodName "asio_hw_fun11" -Arguments @{
            Bus=[byte]$rp.bus; Dev=[byte]$rp.dev; Func=[byte]$rp.func; Reg=[uint16]4; Width=[byte]4
        }
        $stCmd = $result2.dwData
        
        # Read link status (PCIe cap, typically at offset 0x80+0x12=0x92)
        $result3 = Invoke-CimMethod -InputObject $asus -MethodName "asio_hw_fun11" -Arguments @{
            Bus=[byte]$rp.bus; Dev=[byte]$rp.dev; Func=[byte]$rp.func; Reg=[uint16]0x92; Width=[byte]2
        }
        $linkSt = $result3.dwData
        $speed = $linkSt -band 0xF
        $width = ($linkSt -shr 4) -band 0x3F
        
        Write-Host ("  {0}: VEN={1:X4} DEV={2:X4} CMD/ST={3:X8} LinkSpeed={4} Width=x{5}" -f $rp.name, $vendor, $device, $stCmd, $speed, $width)
    } catch {
        Write-Host ("  {0}: FAILED — {1}" -f $rp.name, $_.Exception.Message.Substring(0, [Math]::Min(60, $_.Exception.Message.Length)))
    }
}

# === 4. Read MSR for CPU topology ===
Write-Host "`n--- MSR Read (CPU topology) ---"
try {
    # CPUID via asio_hw_fun17: Index=1 gets feature flags
    $cpuid = Invoke-CimMethod -InputObject $asus -MethodName "asio_hw_fun17" -Arguments @{Index=[uint32]1}
    Write-Host ("  CPUID(1): EAX={0:X8} EBX={1:X8} ECX={2:X8} EDX={3:X8}" -f $cpuid.Eax, $cpuid.Ebx, $cpuid.Ecx, $cpuid.Edx)
    $stepping = $cpuid.Eax -band 0xF
    $model = (($cpuid.Eax -shr 4) -band 0xF) + (($cpuid.Eax -shr 16) -band 0xF) * 16
    $family = (($cpuid.Eax -shr 8) -band 0xF) + (($cpuid.Eax -shr 20) -band 0xFF)
    Write-Host ("  Family={0} Model={1} Stepping={2}" -f $family, $model, $stepping)
    
    # Logical processor count from EBX[23:16]
    $logicalCount = ($cpuid.Ebx -shr 16) -band 0xFF
    Write-Host ("  Max logical CPUs per package: {0}" -f $logicalCount)
} catch { Write-Host "  CPUID failed: $_" }

# === 5. GetBootOrder ===
Write-Host "`n--- Boot Order ---"
try {
    $bootResult = Invoke-CimMethod -InputObject $asus -MethodName "GetBootOrder" -Arguments @{}
    Write-Host "  BootOrder: $($bootResult.BootOrder)"
    Write-Host "  ErrorCode: $($bootResult.ErrorCode)"
} catch { Write-Host "  GetBootOrder failed: $_" }

Write-Host "`n=== FOUND OPTIONS: $($found.Count) ==="
$found | ForEach-Object { Write-Host ("  {0} = {1}" -f $_.name, $_.value) }

if ($found.Count -gt 0) {
    Write-Host "`n  🎉 BIOS options readable from Windows! SetOptionData can WRITE them!"
} else {
    Write-Host "`n  Need to find correct option names. Try UMAF to see exact BIOS labels."
}
