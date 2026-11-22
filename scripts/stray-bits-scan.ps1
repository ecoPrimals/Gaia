
$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement

function Read-PCI($bus, $dev, $func, $reg) {
    $r = Invoke-CimMethod -InputObject $inst -MethodName "asio_hw_fun11" -Arguments @{
        Bus=[byte]$bus; Dev=[byte]$dev; Func=[byte]$func; Reg=[uint16]$reg; Width=[byte]4
    }
    return $r.dwData
}

# Root Complex — Bus 0 Dev 0 Func 0
Write-Output "=== Root Complex (B0:D0:F0) ==="
for ($reg = 0; $reg -le 0xFF; $reg += 4) {
    $val = Read-PCI 0 0 0 $reg
    if ($val -ne 0 -and $val -ne 0xFFFFFFFF) {
        Write-Output ("  0x{0:X2}: 0x{1:X8}" -f $reg, $val)
    }
}

# iGPU bridge — Bus 0 Dev 8 Func 0-2 (AMD puts iGPU here)
Write-Output "`n=== iGPU Bridge (B0:D8:F0-2) ==="
for ($func = 0; $func -le 2; $func++) {
    $vendev = Read-PCI 0 8 $func 0
    $ven = $vendev -band 0xFFFF
    if ($ven -ne 0 -and $ven -ne 0xFFFF) {
        Write-Output ("  B0:D8:F{0} VEN={1:X4} DEV={2:X4}" -f $func, $ven, (($vendev -shr 16) -band 0xFFFF))
        for ($reg = 0; $reg -le 0xFF; $reg += 4) {
            $val = Read-PCI 0 8 $func $reg
            if ($val -ne 0 -and $val -ne 0xFFFFFFFF) {
                Write-Output ("    0x{0:X2}: 0x{1:X8}" -f $reg, $val)
            }
        }
    }
}

# Data Fabric — Bus 0 Dev 24 Func 0-7
# THIS is where AMD controls memory mapping, DRAM holes, MMIO apertures
Write-Output "`n=== Data Fabric (B0:D24:F0-7) ==="
for ($func = 0; $func -le 7; $func++) {
    $vendev = Read-PCI 0 24 $func 0
    $ven = $vendev -band 0xFFFF
    if ($ven -ne 0 -and $ven -ne 0xFFFF) {
        $devid = ($vendev -shr 16) -band 0xFFFF
        Write-Output ("  B0:D24:F{0} VEN={1:X4} DEV={2:X4}" -f $func, $ven, $devid)
        # Scan full config space for this function
        for ($reg = 0; $reg -le 0xFF; $reg += 4) {
            $val = Read-PCI 0 24 $func $reg
            if ($val -ne 0 -and $val -ne 0xFFFFFFFF) {
                Write-Output ("    0x{0:X2}: 0x{1:X8}" -f $reg, $val)
            }
        }
    }
}

# Check Dev 1-7 for any hidden iGPU/bridges
Write-Output "`n=== Internal Bridges (B0:D1-7) ==="
for ($dev = 1; $dev -le 7; $dev++) {
    for ($func = 0; $func -le 1; $func++) {
        $vendev = Read-PCI 0 $dev $func 0
        $ven = $vendev -band 0xFFFF
        if ($ven -ne 0 -and $ven -ne 0xFFFF) {
            $devid = ($vendev -shr 16) -band 0xFFFF
            Write-Output ("  B0:D{0}:F{1} VEN={2:X4} DEV={3:X4}" -f $dev, $func, $ven, $devid)
        }
    }
}

# Check Dev 14 — AMD FCH / SMBus / etc  
Write-Output "`n=== FCH / Misc (B0:D14) ==="
for ($func = 0; $func -le 7; $func++) {
    $vendev = Read-PCI 0 14 $func 0
    $ven = $vendev -band 0xFFFF
    if ($ven -ne 0 -and $ven -ne 0xFFFF) {
        $devid = ($vendev -shr 16) -band 0xFFFF
        Write-Output ("  B0:D14:F{0} VEN={1:X4} DEV={2:X4}" -f $func, $ven, $devid)
        for ($reg = 0; $reg -le 0xFF; $reg += 4) {
            $val = Read-PCI 0 14 $func $reg
            if ($val -ne 0 -and $val -ne 0xFFFFFFFF) {
                Write-Output ("    0x{0:X2}: 0x{1:X8}" -f $reg, $val)
            }
        }
    }
}
