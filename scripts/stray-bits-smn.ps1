
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
