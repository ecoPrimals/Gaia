# Fast PCI scan — find the NVMe issue from inside
Write-Output "=== GPU PCI MAP ==="
Write-Output "  Display 1 — RTX 5090: PCI bus 1"
Write-Output "  Display 2 — AMD iGPU: PCI bus 121"

Write-Output "`n=== NVMe CONTROLLERS ==="
Get-PnpDevice | Where-Object { $_.FriendlyName -match 'NVM Express' } | ForEach-Object {
    $loc = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_LocationInfo' -ErrorAction SilentlyContinue).Data
    $prob = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_ProblemCode' -ErrorAction SilentlyContinue).Data
    Write-Output "  $($_.FriendlyName) [$($_.Status)] Location=[$loc] ProblemCode=$prob"
}

Write-Output "`n=== CODE 12 DEVICES (can't allocate resources = Above4G issue) ==="
$code12 = @()
Get-PnpDevice | ForEach-Object {
    $prob = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_ProblemCode' -ErrorAction SilentlyContinue).Data
    if ($prob -eq 12) {
        $code12 += $_.FriendlyName
        Write-Output "  [Code 12] $($_.FriendlyName)"
    }
}
Write-Output "  Total Code 12 devices: $($code12.Count)"

Write-Output "`n=== CODE 28 DEVICES (no driver = can't init) ==="
$code28 = @()
Get-PnpDevice | ForEach-Object {
    $prob = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_ProblemCode' -ErrorAction SilentlyContinue).Data
    if ($prob -eq 28) {
        $code28 += $_.FriendlyName
        Write-Output "  [Code 28] $($_.FriendlyName)"
    }
}
Write-Output "  Total Code 28 devices: $($code28.Count)"

Write-Output "`n=== NVIDIA GPU ==="
nvidia-smi --query-gpu=name,pci.bus_id,memory.total --format=csv,noheader 2>$null
