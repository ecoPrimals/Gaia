# Probe USB for Pixel/grapheneGate connected to mobo
Write-Output "=== USB DEVICES WITH DETAILS ==="
Get-PnpDevice -Class USB | Where-Object { $_.Status -ne 'OK' -or $_.FriendlyName -match 'Composite|Unknown|Mass' } | 
    ForEach-Object {
        $dev = $_
        $props = Get-PnpDeviceProperty -InstanceId $dev.InstanceId -ErrorAction SilentlyContinue
        $vid = ($props | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_BusReportedDeviceDesc' }).Data
        $hwid = ($props | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_HardwareIds' }).Data
        Write-Output "  $($dev.FriendlyName) [$($dev.Status)]"
        if ($vid) { Write-Output "    BusDesc: $vid" }
        if ($hwid) { Write-Output "    HwId: $($hwid -join ', ')" }
    }

Write-Output ""
Write-Output "=== LOOKING FOR GOOGLE/PIXEL (VID 18D1) ==="
Get-PnpDevice | Where-Object { $_.InstanceId -match '18D1' } |
    Format-Table FriendlyName,Status,InstanceId -AutoSize

Write-Output ""
Write-Output "=== ALL USB COMPOSITE (potential Pixel) ==="
Get-PnpDevice -Class USB | Where-Object { $_.FriendlyName -match 'Composite' } |
    ForEach-Object {
        $hwid = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_HardwareIds' -ErrorAction SilentlyContinue).Data
        Write-Output "  $($_.FriendlyName) [$($_.Status)] HW: $($hwid -join ' | ')"
    }

Write-Output ""
Write-Output "=== PORTABLE DEVICES (MTP) ==="
Get-PnpDevice -Class WPD -ErrorAction SilentlyContinue | Format-Table FriendlyName,Status -AutoSize
