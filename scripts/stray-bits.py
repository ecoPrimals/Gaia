"""STRAY BITS — Find the ACTUAL hardware registers that control UMA allocation.
The BIOS byte is just a NOTE. The real switch is in the silicon.
Scan PCI config space, Data Fabric, and MMIO for the split point."""
import subprocess, json, os, struct

print("=" * 70)
print("STRAY BITS — Hunting the real UMA switch in AMD silicon")
print("=" * 70)

results = {}

# ─── 1: Scan ALL PCI config space via ASUS WMI ───
# The Data Fabric (Bus 0, Dev 24, Func 0-7) controls memory mapping
# The Root Complex (Bus 0, Dev 0) has NB aperture regs
# Bus 0 Dev 8 is where the iGPU bridge SHOULD be

print("\n[1] Deep PCI config scan — Data Fabric + NB + iGPU bridge...")

script1 = r'''
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
'''

with open(r'c:\Users\mokke\Desktop\Gaia\scripts\stray-bits-scan.ps1', 'w') as f:
    f.write(script1)

r1 = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', 
                     r'c:\Users\mokke\Desktop\Gaia\scripts\stray-bits-scan.ps1'],
                    capture_output=True, text=True, timeout=60)
print(r1.stdout)
if r1.stderr:
    print("STDERR:", r1.stderr[:500])

results['pci_scan'] = r1.stdout

# ─── 2: Look at MMIO ranges for iGPU ───
print("\n[2] MMIO and memory-mapped regions...")

script2 = r'''
# Get all memory resources that might be iGPU-related
$all = Get-PnpDevice | Where-Object { $_.InstanceId -like "*1002*" -or $_.InstanceId -like "*BasicDisplay*" }
foreach ($dev in $all) {
    Write-Output ("Device: " + $dev.FriendlyName + " [" + $dev.InstanceId + "] Status=" + $dev.Status)
    $res = Get-PnpDeviceProperty -InstanceId $dev.InstanceId -ErrorAction SilentlyContinue
    foreach ($p in $res) {
        if ($p.KeyName -like "*DEVPKEY_Device_*" -and $null -ne $p.Data -and $p.Data -ne "") {
            if ($p.KeyName -like "*Resource*" -or $p.KeyName -like "*Location*" -or $p.KeyName -like "*Address*" -or $p.KeyName -like "*Config*" -or $p.KeyName -like "*Bus*") {
                Write-Output ("  " + $p.KeyName + " = " + $p.Data)
            }
        }
    }
}

# DRAM mapping from kernel
Write-Output "`n=== Physical Memory Ranges ==="
$mem = Get-CimInstance Win32_PhysicalMemoryArray
Write-Output ("  Physical arrays: " + $mem.Count)
$dimms = Get-CimInstance Win32_PhysicalMemory
foreach ($d in $dimms) {
    Write-Output ("  DIMM: " + $d.BankLabel + " " + $d.DeviceLocator + " " + [math]::Round($d.Capacity/1GB) + "GB Speed=" + $d.Speed + "MHz")
}

# Memory map from firmware
Write-Output "`n=== Firmware Memory Map ==="
$memmap = Get-CimInstance Win32_DeviceMemoryAddress | Sort-Object StartingAddress | Select-Object -First 20
foreach ($m in $memmap) {
    Write-Output ("  0x{0:X}-0x{1:X} Name={2}" -f $m.StartingAddress, $m.EndingAddress, $m.Name)
}
'''

with open(r'c:\Users\mokke\Desktop\Gaia\scripts\stray-bits-mmio.ps1', 'w') as f:
    f.write(script2)

r2 = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File',
                     r'c:\Users\mokke\Desktop\Gaia\scripts\stray-bits-mmio.ps1'],
                    capture_output=True, text=True, timeout=30)
print(r2.stdout)
results['mmio'] = r2.stdout

# ─── 3: Check if there's a GNB (Graphics NorthBridge) SMN access ───
print("\n[3] SMU / SMN access hunting...")

script3 = r'''
$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement

function Read-PCI($bus, $dev, $func, $reg) {
    $r = Invoke-CimMethod -InputObject $inst -MethodName "asio_hw_fun11" -Arguments @{
        Bus=[byte]$bus; Dev=[byte]$dev; Func=[byte]$func; Reg=[uint16]$reg; Width=[byte]4
    }
    return $r.dwData
}

# SMN (System Management Network) is accessed through NB PCI space
# Write address to 0xB8 (SMN_INDEX), read data from 0xBC (SMN_DATA)
# on Bus 0 Dev 0 Func 0

# Key SMN addresses for iGPU UMA:
# 0x13B10044 — UMA_REGION_BASE
# 0x13B10048 — UMA_REGION_SIZE  
# 0x13B1004C — UMA_REGION_CTRL
# 0x16000000+ — GFX/IOMMU region
# 0x15000000+ — Display controller registers

$smnAddrs = @(
    @{addr=0x13B10044; name="UMA_REGION_BASE"},
    @{addr=0x13B10048; name="UMA_REGION_SIZE"},
    @{addr=0x13B1004C; name="UMA_REGION_CTRL"},
    @{addr=0x13B10050; name="UMA_REGION_+0x50"},
    @{addr=0x13B10054; name="UMA_REGION_+0x54"},
    @{addr=0x13B10000; name="GNB_BASE"},
    @{addr=0x13B10004; name="GNB_+0x04"},
    @{addr=0x13B10008; name="GNB_+0x08"},
    @{addr=0x13B1000C; name="GNB_+0x0C"},
    @{addr=0x13B10010; name="GNB_+0x10"},
    @{addr=0x00000090; name="NB_0x90"},
    @{addr=0x00000094; name="NB_0x94"},
    @{addr=0x00000098; name="NB_0x98"},
    @{addr=0x0000009C; name="NB_0x9C"},
    @{addr=0x15000000; name="DCN_BASE"},
    @{addr=0x15000004; name="DCN_+4"},
    @{addr=0x00049000; name="IOMMU_L2_UMA"},
    @{addr=0x00049004; name="IOMMU_L2_UMA+4"},
    @{addr=0x16000000; name="GFX_BASE"},
    @{addr=0x16000004; name="GFX_+4"},
    @{addr=0x00050000; name="DF_BASE"},
    @{addr=0x00050044; name="DF_DRAM_HOLE"},
    @{addr=0x00050110; name="DF_DRAM_BASE0"},
    @{addr=0x00050114; name="DF_DRAM_LIMIT0"},
    @{addr=0x00050140; name="DF_MMIO_BASE0"},
    @{addr=0x00050144; name="DF_MMIO_LIMIT0"},
    @{addr=0x00050148; name="DF_MMIO_CTRL0"}
)

Write-Output "=== SMN Register Scan (via NB Index/Data) ==="

function Write-PCI($bus, $dev, $func, $reg, $value) {
    $r = Invoke-CimMethod -InputObject $inst -MethodName "asio_hw_fun12" -Arguments @{
        Bus=[byte]$bus; Dev=[byte]$dev; Func=[byte]$func; Reg=[uint16]$reg; Width=[byte]4; dwData=[uint32]$value
    }
    return $r
}

foreach ($entry in $smnAddrs) {
    # Write SMN address to NB index register 0xB8
    $wr = Write-PCI 0 0 0 0xB8 $entry.addr
    # Read SMN data from 0xBC
    $val = Read-PCI 0 0 0 0xBC
    if ($val -ne 0 -and $val -ne 0xFFFFFFFF) {
        Write-Output ("  SMN 0x{0:X8} ({1}): 0x{2:X8}" -f $entry.addr, $entry.name, $val)
    } else {
        Write-Output ("  SMN 0x{0:X8} ({1}): 0x{2:X8} (empty)" -f $entry.addr, $entry.name, $val)
    }
}

# Scan the Data Fabric DRAM map registers directly
Write-Output "`n=== Data Fabric DRAM Map (B0:D24:F0) ==="
# DF::DramHoleControl
$dhc = Read-PCI 0 24 0 0x104
Write-Output ("  DramHoleControl (0x104): 0x{0:X8}" -f $dhc)
# DF::DramBaseAddress0-7
for ($i = 0; $i -le 7; $i++) {
    $base = Read-PCI 0 24 0 (0x110 + $i*8)
    $limit = Read-PCI 0 24 0 (0x114 + $i*8)
    if ($base -ne 0 -or $limit -ne 0) {
        Write-Output ("  DRAM[$i] Base=0x{0:X8} Limit=0x{1:X8}" -f $base, $limit)
    }
}
'''

with open(r'c:\Users\mokke\Desktop\Gaia\scripts\stray-bits-smn.ps1', 'w') as f:
    f.write(script3)

r3 = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File',
                     r'c:\Users\mokke\Desktop\Gaia\scripts\stray-bits-smn.ps1'],
                    capture_output=True, text=True, timeout=60)
print(r3.stdout)
results['smn'] = r3.stdout

# ─── SAVE ALL FINDINGS ───
outdir = r'c:\Users\mokke\Desktop\Gaia\data\uefi-sniffs'
os.makedirs(outdir, exist_ok=True)
with open(os.path.join(outdir, 'stray-bits-findings.json'), 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 70)
print("Findings saved to data/uefi-sniffs/stray-bits-findings.json")
print("Ready for eastGate + sweetGrass analysis")
print("=" * 70)
