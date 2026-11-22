
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
