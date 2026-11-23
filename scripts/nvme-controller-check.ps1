# Check NVMe controllers and PCI resource allocation
$out = "C:\Users\mokke\Desktop\Gaia\data\gut\nvme-controller-result.txt"
$log = @()

$log += "=== NVMe/Storage CONTROLLERS ==="
Get-PnpDevice | Where-Object { $_.FriendlyName -match 'NVMe|Non-Volatile' } | ForEach-Object {
    $log += "  $($_.FriendlyName) [$($_.Status)]"
    $log += "    ID: $($_.InstanceId)"
    $prob = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_ProblemCode' -ErrorAction SilentlyContinue).Data
    $pdesc = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_ProblemDescription' -ErrorAction SilentlyContinue).Data
    $log += "    Problem Code: $prob"
    $log += "    Problem Desc: $pdesc"
    
    # Get allocated resources
    $res = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_AllocatedResources' -ErrorAction SilentlyContinue).Data
    if ($res) { $log += "    Resources: (present)" }
    
    # Check config flags
    $flags = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_ConfigFlags' -ErrorAction SilentlyContinue).Data
    $log += "    ConfigFlags: $flags"
}

$log += "`n=== ALL PCI NVMe DEVICES ==="
Get-PnpDevice | Where-Object { $_.InstanceId -match 'PCI.*144D|PCI.*15B7|PCI.*1B21|PCI.*1C5C' -and $_.Class -ne 'Display' } | ForEach-Object {
    $log += "  $($_.FriendlyName) [$($_.Status)] Class=$($_.Class)"
    $log += "    $($_.InstanceId)"
}

$log += "`n=== PCI BRIDGE STATUS (4G resources) ==="
Get-PnpDevice | Where-Object { $_.FriendlyName -match 'PCI Express.*Port|PCI-to-PCI' -and $_.Status -ne 'OK' } | ForEach-Object {
    $log += "  $($_.FriendlyName) [$($_.Status)]"
    $prob = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_ProblemCode' -ErrorAction SilentlyContinue).Data
    $log += "    Problem: $prob ID=$($_.InstanceId)"
}

$log += "`n=== DEVICES WITH RESOURCE CONFLICTS ==="
Get-PnpDevice | Where-Object { $_.Status -eq 'Error' -or $_.Status -eq 'Degraded' } | ForEach-Object {
    $prob = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_ProblemCode' -ErrorAction SilentlyContinue).Data
    if ($prob -gt 0) {
        $log += "  $($_.FriendlyName) [$($_.Status)] Problem=$prob"
    }
}

$log += "`n=== Check: Is Above4G actually on? (resource test) ==="
# If Above4G is on, we should see memory resources above 0x100000000 (4GB)
$log += "Checking GPU BAR..."
$gpu = Get-PnpDevice | Where-Object { $_.FriendlyName -match 'RTX 5090' }
if ($gpu) {
    $res = Get-PnpDeviceProperty -InstanceId $gpu.InstanceId -KeyName 'DEVPKEY_Device_AllocatedResources' -ErrorAction SilentlyContinue
    $log += "  RTX 5090 resources: $(if ($res.Data) { 'allocated' } else { 'none visible' })"
}

$log -join "`n" | Out-File -FilePath $out -Encoding utf8
