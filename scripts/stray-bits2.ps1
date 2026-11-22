
$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement

function Read-PCI($bus, $dev, $func, $reg) {
    $r = Invoke-CimMethod -InputObject $inst -MethodName "asio_hw_fun11" -Arguments @{
        Bus=[byte]$bus; Dev=[byte]$dev; Func=[byte]$func; Reg=[uint16]$reg; Width=[byte]4
    }
    return $r.dwData
}

function Write-PCI($bus, $dev, $func, $reg, $val) {
    $r = Invoke-CimMethod -InputObject $inst -MethodName "asio_hw_fun12" -Arguments @{
        Bus=[byte]$bus; Dev=[byte]$dev; Func=[byte]$func; Reg=[uint16]$reg; Width=[byte]4; dwData=[uint32]$val
    }
    return $r
}

# Get actual PCI locations from Windows
Write-Output "=== Known PCI Devices ==="
$gpus = Get-PnpDevice -Class Display -ErrorAction SilentlyContinue
foreach ($g in $gpus) {
    $loc = (Get-PnpDeviceProperty -InstanceId $g.InstanceId -KeyName DEVPKEY_Device_LocationInfo -ErrorAction SilentlyContinue).Data
    $path = (Get-PnpDeviceProperty -InstanceId $g.InstanceId -KeyName DEVPKEY_Device_LocationPaths -ErrorAction SilentlyContinue).Data
    Write-Output ("  GPU: " + $g.FriendlyName + " Location=" + $loc + " Path=" + ($path -join ","))
}

# Get the RTX 5090 bus location
$nv = Get-PnpDevice -Class Display | Where-Object { $_.FriendlyName -like "*NVIDIA*" }
$nvloc = (Get-PnpDeviceProperty -InstanceId $nv.InstanceId -KeyName DEVPKEY_Device_LocationInfo -ErrorAction SilentlyContinue).Data
Write-Output ("RTX 5090 at: " + $nvloc)

# Parse bus/dev/func from location string
if ($nvloc -match "bus (\d+), device (\d+), function (\d+)") {
    $nvBus = [int]$Matches[1]; $nvDev = [int]$Matches[2]; $nvFunc = [int]$Matches[3]
    Write-Output ("Trying PCI read B${nvBus}:D${nvDev}:F${nvFunc}...")
    $vendev = Read-PCI $nvBus $nvDev $nvFunc 0
    $ven = $vendev -band 0xFFFF
    $devid = ($vendev -shr 16) -band 0xFFFF
    Write-Output ("  VEN=0x{0:X4} DEV=0x{1:X4} (expect 10DE:2B85)" -f $ven, $devid)
}

# Now check the iGPU audio location — Bus 123 Dev 0 Func 1
Write-Output "`n=== iGPU Silicon (Bus 123) ==="
# Func 0 should be the display engine, Func 1 is audio
for ($func = 0; $func -le 7; $func++) {
    $vendev = Read-PCI 123 0 $func 0
    $ven = $vendev -band 0xFFFF
    if ($ven -ne 0 -and $ven -ne 0xFFFF) {
        $devid = ($vendev -shr 16) -band 0xFFFF
        Write-Output ("  B123:D0:F{0} VEN=0x{1:X4} DEV=0x{2:X4}" -f $func, $ven, $devid)
        
        # Read BARs (Base Address Registers) — where MMIO regions are
        for ($r = 0x10; $r -le 0x24; $r += 4) {
            $bar = Read-PCI 123 0 $func $r
            if ($bar -ne 0) {
                Write-Output ("    BAR 0x{0:X2}: 0x{1:X8}" -f $r, $bar)
            }
        }
        
        # Status/Command
        $statcmd = Read-PCI 123 0 $func 4
        Write-Output ("    Status/Cmd: 0x{0:X8}" -f $statcmd)
    } else {
        Write-Output ("  B123:D0:F{0} = 0x{1:X8} (not present)" -f $func, $vendev)
    }
}

# Check the BRIDGE at Bus 0 Dev 8
Write-Output "`n=== iGPU Bridge (B0:D8) ==="
for ($func = 0; $func -le 2; $func++) {
    $vendev = Read-PCI 0 8 $func 0
    $ven = $vendev -band 0xFFFF
    if ($ven -ne 0) {
        Write-Output ("  B0:D8:F{0} VEN=0x{1:X4} DEV=0x{2:X4}" -f $func, $ven, (($vendev -shr 16) -band 0xFFFF))
        # Read secondary bus number (offset 0x18-0x19) for bridges
        $buses = Read-PCI 0 8 $func 0x18
        Write-Output ("    Bus numbers: 0x{0:X8} (pri={1} sec={2} sub={3})" -f $buses, ($buses -band 0xFF), (($buses -shr 8) -band 0xFF), (($buses -shr 16) -band 0xFF))
    } else {
        Write-Output ("  B0:D8:F{0} = empty" -f $func)
    }
}

# Maybe the root complex is HIDDEN or at a different address
Write-Output "`n=== Scan ALL Bus 0 devices ==="
for ($dev = 0; $dev -le 31; $dev++) {
    for ($func = 0; $func -le 1; $func++) {
        $vendev = Read-PCI 0 $dev $func 0
        $ven = $vendev -band 0xFFFF
        if ($ven -ne 0 -and $ven -ne 0xFFFF) {
            $devid = ($vendev -shr 16) -band 0xFFFF
            Write-Output ("  B0:D{0}:F{1} VEN=0x{2:X4} DEV=0x{3:X4}" -f $dev, $func, $ven, $devid)
        }
    }
}
