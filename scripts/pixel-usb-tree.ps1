# Find Pixel in USB tree
$pixel = Get-PnpDevice | Where-Object { $_.InstanceId -match '18D1' }
foreach ($dev in $pixel) {
    Write-Output "=== PIXEL DEVICE ==="
    Write-Output "  Name: $($dev.FriendlyName)"
    Write-Output "  ID: $($dev.InstanceId)"
    Write-Output "  Status: $($dev.Status)"
    
    $loc = (Get-PnpDeviceProperty -InstanceId $dev.InstanceId -KeyName 'DEVPKEY_Device_LocationInfo' -ErrorAction SilentlyContinue).Data
    Write-Output "  Location: $loc"
    
    # Walk up the tree
    $current = $dev.InstanceId
    $depth = 0
    while ($current -and $depth -lt 5) {
        $parent = (Get-PnpDeviceProperty -InstanceId $current -KeyName 'DEVPKEY_Device_Parent' -ErrorAction SilentlyContinue).Data
        if ($parent) {
            $pdev = Get-PnpDevice | Where-Object { $_.InstanceId -eq $parent }
            if ($pdev) {
                Write-Output "  Parent[$depth]: $($pdev.FriendlyName) ($($pdev.InstanceId))"
            }
            $current = $parent
        } else {
            break
        }
        $depth++
    }
}

Write-Output ""
Write-Output "=== USB CONTROLLERS ==="
Get-PnpDevice | Where-Object { $_.FriendlyName -match 'USB.*Host Controller|USB4' -and $_.Status -eq 'OK' } | 
    Format-Table FriendlyName, InstanceId -AutoSize
