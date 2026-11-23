# Map BOTH GPUs and their PCI resource allocation
# Display 1 (RTX 5090) vs Display 2 (iGPU) — what do they see?

Write-Output "=== DISPLAY 1: RTX 5090 ==="
$rtx = Get-PnpDevice | Where-Object { $_.FriendlyName -match 'RTX 5090' }
$rtxRes = Get-PnpDeviceProperty -InstanceId $rtx.InstanceId -KeyName 'DEVPKEY_Device_LocationInfo' -ErrorAction SilentlyContinue
Write-Output "  Location: $($rtxRes.Data)"
Write-Output "  PCI: $($rtx.InstanceId)"

Write-Output "`n=== DISPLAY 2: AMD iGPU ==="
$igpu = Get-PnpDevice | Where-Object { $_.FriendlyName -match 'AMD Radeon' }
$igpuRes = Get-PnpDeviceProperty -InstanceId $igpu.InstanceId -KeyName 'DEVPKEY_Device_LocationInfo' -ErrorAction SilentlyContinue
Write-Output "  Location: $($igpuRes.Data)"
Write-Output "  PCI: $($igpu.InstanceId)"

Write-Output "`n=== PCI BUS TOPOLOGY (where NVMe SHOULD be) ==="
Get-PnpDevice | Where-Object { $_.FriendlyName -match 'PCI Express Root Port' } | ForEach-Object {
    $loc = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_LocationInfo' -ErrorAction SilentlyContinue).Data
    $children = Get-PnpDevice | Where-Object { 
        $parent = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_Parent' -ErrorAction SilentlyContinue).Data
        $parent -eq $_.InstanceId 
    }
    Write-Output "  $($_.FriendlyName) [$($_.Status)] Location=$loc"
}

Write-Output "`n=== NVMe CONTROLLER PCI ADDRESSES ==="
Get-PnpDevice | Where-Object { $_.FriendlyName -match 'NVM Express' } | ForEach-Object {
    $loc = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_LocationInfo' -ErrorAction SilentlyContinue).Data
    $prob = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_ProblemCode' -ErrorAction SilentlyContinue).Data
    $pdesc = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_ProblemDescription' -ErrorAction SilentlyContinue).Data
    Write-Output "  $($_.FriendlyName) [$($_.Status)]"
    Write-Output "    Location: $loc"
    Write-Output "    ProblemCode: $prob"
    Write-Output "    ProblemDesc: $pdesc"
    Write-Output "    PCI ID: $($_.InstanceId)"
}

Write-Output "`n=== DEVICE MANAGER RESOURCES (Code 12 = no resources) ==="
Get-PnpDevice | Where-Object { $_.Status -eq 'Error' -or $_.Status -eq 'Unknown' } | ForEach-Object {
    $prob = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_ProblemCode' -ErrorAction SilentlyContinue).Data
    if ($prob -and $prob -gt 0) {
        Write-Output "  [$prob] $($_.FriendlyName) [$($_.Status)] Class=$($_.Class)"
    }
}

Write-Output "`n=== NVIDIA-SMI GPU DETAILS ==="
nvidia-smi --query-gpu=name,pci.bus_id,memory.total,bar1.memory.total,bar1.memory.used --format=csv 2>$null

Write-Output "`n=== AMD iGPU DETAILS ==="
Get-PnpDeviceProperty -InstanceId $igpu.InstanceId | Where-Object { $_.KeyName -match 'Resource|Memory|Address' } | ForEach-Object {
    Write-Output "  $($_.KeyName): $($_.Data)"
}
