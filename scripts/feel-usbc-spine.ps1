# FEEL THE USB-C SPINE — Map every port, every device, every speed
Write-Host "=" * 60
Write-Host "  USB-C SPINE — Feel every port"
Write-Host "=" * 60

# All USB controllers with bus info
Write-Host "`n--- USB CONTROLLERS (the spine vertebrae) ---"
$controllers = Get-PnpDevice -Class USB -Status OK | Where-Object { $_.FriendlyName -match 'Host Controller|USB4' }
foreach ($ctrl in $controllers) {
    $loc = (Get-PnpDeviceProperty -InstanceId $ctrl.InstanceId -KeyName DEVPKEY_Device_LocationInfo -ErrorAction SilentlyContinue).Data
    $busType = ""
    if ($ctrl.InstanceId -match 'DEV_15B6') { $busType = "CPU USB3.1 10Gbps" }
    elseif ($ctrl.InstanceId -match 'DEV_15B7') { $busType = "CPU USB3.1 5Gbps" }
    elseif ($ctrl.InstanceId -match 'DEV_15B8') { $busType = "CPU USB2.0 480Mbps" }
    elseif ($ctrl.InstanceId -match 'DEV_43FD') { $busType = "Chipset USB3.2 10Gbps" }
    elseif ($ctrl.InstanceId -match 'DEV_2425') { $busType = "USB4 40Gbps (DP Alt!)" }
    elseif ($ctrl.InstanceId -match 'DEV_2426') { $busType = "ASMedia USB3.2 20Gbps" }
    Write-Host "`n  [$busType] $($ctrl.FriendlyName)"
    Write-Host "    Location: $loc"
    Write-Host "    ID: $($ctrl.InstanceId)"
    
    # Find root hub under this controller
    $shortId = $ctrl.InstanceId.Split('\')[-1]
    $rootHubs = Get-PnpDevice -Class USB -Status OK | Where-Object { 
        $_.FriendlyName -match 'Root Hub' -and
        (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName DEVPKEY_Device_Parent -ErrorAction SilentlyContinue).Data -eq $ctrl.InstanceId
    }
    foreach ($hub in $rootHubs) {
        Write-Host "    Root Hub: $($hub.InstanceId)"
        
        # Find ALL devices under this root hub (recursive)
        $children = Get-PnpDevice -Status OK | Where-Object {
            $parent = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName DEVPKEY_Device_Parent -ErrorAction SilentlyContinue).Data
            $parent -eq $hub.InstanceId -or $parent -match $hub.InstanceId.Split('\')[-1]
        }
        foreach ($child in $children) {
            if ($child.FriendlyName -notmatch 'Root Hub') {
                $speed = ""
                if ($child.InstanceId -match 'VID_3434') { $speed = "Keychron KB" }
                elseif ($child.InstanceId -match 'VID_046D') { $speed = "Logitech Mouse" }
                elseif ($child.InstanceId -match 'VID_0489') { $speed = "Bluetooth" }
                elseif ($child.InstanceId -match 'VID_0B05.*1B9B') { $speed = "ASUS Device" }
                elseif ($child.InstanceId -match 'VID_0B05.*1AA6') { $speed = "ASUS Aura" }
                elseif ($child.InstanceId -match 'VID_174C') { $speed = "ASMedia Hub" }
                elseif ($child.InstanceId -match 'VID_28DE') { $speed = "Valve/Steam" }
                elseif ($child.InstanceId -match 'VID_1B1C') { $speed = "Corsair iCUE" }
                Write-Host "      -> $($child.FriendlyName) $speed"
            }
        }
    }
}

# ITE USB-C connector (CC/PD negotiation chip)
Write-Host "`n--- ITE USB-C Connector (PD/CC chip) ---"
$ite = Get-PnpDevice -Status OK | Where-Object { $_.FriendlyName -match 'ITE' }
foreach ($i in $ite) {
    $loc = (Get-PnpDeviceProperty -InstanceId $i.InstanceId -KeyName DEVPKEY_Device_LocationInfo -ErrorAction SilentlyContinue).Data
    Write-Host "  $($i.FriendlyName) Location=$loc ID=$($i.InstanceId)"
}

# USB4 tunnel status
Write-Host "`n--- USB4 Tunnel Status ---"
Get-PnpDevice -Status OK | Where-Object { $_.InstanceId -match 'USB4' } | ForEach-Object {
    Write-Host "  $($_.FriendlyName) [$($_.Status)]"
}

# Power delivery
Write-Host "`n--- USB Power Delivery ---"
Get-PnpDevice | Where-Object { $_.FriendlyName -match 'Power|PD|Charger|Battery' -and $_.Class -match 'USB|Battery|Power' } | ForEach-Object {
    Write-Host "  $($_.FriendlyName) [$($_.Status)]"
}

# Summary
Write-Host "`n" + "=" * 60
Write-Host "  USB-C SPINE SUMMARY"
Write-Host "=" * 60
Write-Host @"

  REAR I/O (ASUS ROG STRIX X870E-E):
  ┌──────────────────────────────────────────────┐
  │  [USB-C 40G]  [USB-C 20G]  [USB-A] [USB-A]  │
  │   USB4/DP      ASMedia      3.2     3.2      │
  │                                               │
  │  [USB-A] [USB-A] [USB-A] [USB-A] [USB-C 10G] │
  │   3.2    3.2     2.0     2.0      CPU         │
  │                                               │
  │  [HDMI]  [WiFi]  [2.5GbE]  [Audio]           │
  │  iGPU    AX WiFi  Realtek   Codec             │
  └──────────────────────────────────────────────┘

  Currently plugged in:
    USB4 40G  → (check what's here - Steam Deck?)
    ASM 20G   → (check what's here - Keychron?)
    CPU 10G   → (check)
    HDMI      → Dummy plug (iGPU probe)
"@
