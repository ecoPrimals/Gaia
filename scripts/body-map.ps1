# Gaia Body Map — northGate peripherals as organs
Write-Output "==========================================="
Write-Output "  GAIA BODY MAP — northGate Peripherals"
Write-Output "==========================================="

Write-Output "`n=== HANDS (Keyboards) ==="
Get-PnpDevice | Where-Object { $_.FriendlyName -match 'Keychron|K100|Keyboard|HID Keyboard' -and $_.Class -eq 'Keyboard' } | 
    Format-Table FriendlyName,Status,InstanceId -AutoSize
# Raw USB for Keychron
Get-PnpDevice -Class USB | Where-Object { $_.InstanceId -match '3434' } |
    ForEach-Object {
        $loc = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_LocationInfo' -ErrorAction SilentlyContinue).Data
        $bt = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_BusReportedDeviceDesc' -ErrorAction SilentlyContinue).Data
        Write-Output "  Keychron USB: [$($_.Status)] $bt Location=$loc $($_.InstanceId)"
    }

Write-Output "`n=== EARS + VOICE (Audio) ==="
Get-PnpDevice | Where-Object { $_.FriendlyName -match 'Corsair|HS80|Headset|Microphone|Audio' -and $_.Class -match 'Audio|Media' } |
    Format-Table FriendlyName,Status -AutoSize
# Corsair USB dongle
Get-PnpDevice -Class USB | Where-Object { $_.InstanceId -match '1B1C' } |
    ForEach-Object {
        $bt = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_BusReportedDeviceDesc' -ErrorAction SilentlyContinue).Data
        Write-Output "  Corsair USB: [$($_.Status)] $bt $($_.InstanceId)"
    }

Write-Output "`n=== GRIP (Mouse) ==="
Get-PnpDevice | Where-Object { $_.FriendlyName -match 'G502|Mouse|Pointing' -and $_.Class -match 'Mouse|HIDClass' } |
    Format-Table FriendlyName,Status -AutoSize

Write-Output "`n=== EYES (Displays + Cameras) ==="
Get-PnpDevice -Class Display | Format-Table FriendlyName,Status -AutoSize
Get-PnpDevice -Class Camera -ErrorAction SilentlyContinue | Format-Table FriendlyName,Status -AutoSize
Get-PnpDevice -Class Monitor | Where-Object { $_.Status -eq 'OK' } | Format-Table FriendlyName,Status -AutoSize

Write-Output "`n=== TAIL (Steam Deck / USB displays) ==="
Get-PnpDevice | Where-Object { $_.FriendlyName -match 'Steam|Mobile Monitor|USB.*Display' } |
    Format-Table FriendlyName,Status,Class -AutoSize

Write-Output "`n=== BLUETOOTH ==="
Get-PnpDevice | Where-Object { $_.FriendlyName -match 'Bluetooth' } |
    Format-Table FriendlyName,Status -AutoSize

Write-Output "`n=== SPINE (Network) ==="
Get-PnpDevice | Where-Object { $_.Class -eq 'Net' -and $_.Status -eq 'OK' } |
    Format-Table FriendlyName,Status -AutoSize

Write-Output "`n=== ALL USB HID (input devices) ==="
Get-PnpDevice -Class HIDClass -ErrorAction SilentlyContinue | Where-Object { $_.Status -eq 'OK' } |
    Format-Table FriendlyName,Status -AutoSize
