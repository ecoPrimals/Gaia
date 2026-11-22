# ASUS WMI ADMIN WRITE — Elevated + dedicated methods
$gutDir = "c:\Users\mokke\Desktop\Gaia\data\gut"
Start-Transcript "$gutDir\asus-wmi-admin-write.txt" -Force

Write-Host "=== ASUS WMI ADMIN WRITE ===" -ForegroundColor Cyan
Write-Host "Admin: $([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)"

$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement

# 1. Try SetFastBoot (dedicated method)
Write-Host "`n--- SetFastBoot (dedicated method) ---"
$r = Invoke-CimMethod -InputObject $inst -MethodName GetOptionData -Arguments @{OptionName="FastBoot"}
Write-Host "  Before: FastBoot = $($r.Value)"
try {
    $w = Invoke-CimMethod -InputObject $inst -MethodName SetFastBoot -Arguments @{SetValue=[byte]0}
    Write-Host "  SetFastBoot(0): err=$($w.ErrorCode)" -ForegroundColor $(if($w.ErrorCode -eq 0){"Green"}else{"Red"})
} catch { Write-Host "  SetFastBoot error: $_" -ForegroundColor Red }
$r2 = Invoke-CimMethod -InputObject $inst -MethodName GetOptionData -Arguments @{OptionName="FastBoot"}
Write-Host "  After: FastBoot = $($r2.Value)"

# 2. Try SetOptionData with admin
Write-Host "`n--- SetOptionData (admin) ---"
$testOptions = @(
    @{name="AboveForGBMemorySupport"; val=1},
    @{name="SmtMode"; val=1},
    @{name="ResizableBarSupport"; val=1},
    @{name="IntegratedGraphics"; val=1},
    @{name="SvmMode"; val=1}
)

foreach ($opt in $testOptions) {
    $before = (Invoke-CimMethod -InputObject $inst -MethodName GetOptionData -Arguments @{OptionName=$opt.name}).Value
    $w = Invoke-CimMethod -InputObject $inst -MethodName SetOptionData -Arguments @{OptionName=$opt.name; Value=[uint32]$opt.val}
    $after = (Invoke-CimMethod -InputObject $inst -MethodName GetOptionData -Arguments @{OptionName=$opt.name}).Value
    $ok = if($after -eq $opt.val){"WRITTEN"}else{"BLOCKED (err=$($w.ErrorCode))"}
    $color = if($after -eq $opt.val){"Green"}else{"Yellow"}
    Write-Host "  $($opt.name): $before -> $after [$ok]" -ForegroundColor $color
}

# 3. Try SetOptionDefault (might bypass write protection)
Write-Host "`n--- SetOptionDefault (might unlock) ---"
try {
    $w = Invoke-CimMethod -InputObject $inst -MethodName SetOptionDefault -Arguments @{OptionName="SmtMode"; Value=[uint32]1}
    Write-Host "  SetOptionDefault SmtMode=1: err=$($w.ErrorCode)"
    $after = (Invoke-CimMethod -InputObject $inst -MethodName GetOptionData -Arguments @{OptionName="SmtMode"}).Value
    Write-Host "  SmtMode now: $after"
} catch { Write-Host "  Error: $_" }

# 4. Try device_ctrl for PCIe devices
Write-Host "`n--- device_ctrl / device_status ---"
for ($id = 0; $id -lt 8; $id++) {
    try {
        $s = Invoke-CimMethod -InputObject $inst -MethodName device_status -Arguments @{device_id=[uint32]$id}
        Write-Host "  device $id : ctrl_param=$($s.ctrl_param)"
    } catch {}
}

# 5. Direct PCI config read of root ports (the REAL test)
Write-Host "`n--- PCI Config Read (asio_hw_fun11) — Root Ports ---"
# RP05 (0:1.3) — Samsung 4TB ghost
try {
    $r = Invoke-CimMethod -InputObject $inst -MethodName asio_hw_fun11 -Arguments @{Bus=[byte]0; Dev=[byte]1; Func=[byte]3; Reg=[uint16]0; Width=[byte]4}
    Write-Host "  RP05 (0:1.3) VID/DID: 0x$($r.dwData.ToString('X8'))" -ForegroundColor Cyan
} catch { Write-Host "  RP05 read error: $_" }

# RP06 (0:1.4) — WD BLACK ghost
try {
    $r = Invoke-CimMethod -InputObject $inst -MethodName asio_hw_fun11 -Arguments @{Bus=[byte]0; Dev=[byte]1; Func=[byte]4; Reg=[uint16]0; Width=[byte]4}
    Write-Host "  RP06 (0:1.4) VID/DID: 0x$($r.dwData.ToString('X8'))" -ForegroundColor Cyan
} catch { Write-Host "  RP06 read error: $_" }

# Working RP04 (0:1.2) — boot NVMe for comparison
try {
    $r = Invoke-CimMethod -InputObject $inst -MethodName asio_hw_fun11 -Arguments @{Bus=[byte]0; Dev=[byte]1; Func=[byte]2; Reg=[uint16]0; Width=[byte]4}
    Write-Host "  RP04 (0:1.2) VID/DID: 0x$($r.dwData.ToString('X8')) (working boot drive)" -ForegroundColor Green
} catch { Write-Host "  RP04 read error: $_" }

# GPU RP03 (0:1.1)
try {
    $r = Invoke-CimMethod -InputObject $inst -MethodName asio_hw_fun11 -Arguments @{Bus=[byte]0; Dev=[byte]1; Func=[byte]1; Reg=[uint16]0; Width=[byte]4}
    Write-Host "  RP03 (0:1.1) VID/DID: 0x$($r.dwData.ToString('X8')) (RTX 5090)" -ForegroundColor Green
} catch { Write-Host "  RP03 read error: $_" }

# Read PCIe link status registers (offset 0x12 in PCIe cap)
Write-Host "`n--- PCIe Link Status for ghost ports ---"
foreach ($func in @(2, 3, 4)) {
    # Find PCIe capability (usually at 0x40 or 0x60 for AMD)
    foreach ($capOff in @(0x58, 0x40, 0x60, 0x80)) {
        try {
            $r = Invoke-CimMethod -InputObject $inst -MethodName asio_hw_fun11 -Arguments @{Bus=[byte]0; Dev=[byte]1; Func=[byte]$func; Reg=[uint16]($capOff); Width=[byte]4}
            if (($r.dwData -band 0xFF) -eq 0x10) {  # PCIe capability ID
                $linkStat = Invoke-CimMethod -InputObject $inst -MethodName asio_hw_fun11 -Arguments @{Bus=[byte]0; Dev=[byte]1; Func=[byte]$func; Reg=[uint16]($capOff+0x12); Width=[byte]2}
                $speed = $linkStat.dwData -band 0xF
                $width = ($linkStat.dwData -shr 4) -band 0x3F
                Write-Host "  0:1.$func PCIe cap@0x$($capOff.ToString('X2')): LinkSpeed=$speed Width=x$width" -ForegroundColor Cyan
                break
            }
        } catch {}
    }
}

Stop-Transcript
