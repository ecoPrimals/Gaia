# FIX DISPLAY — Detect LG on RTX + map USB-C spine
Write-Host "=" * 60
Write-Host "  DISPLAY FIX + USB-C SPINE"
Write-Host "=" * 60

# Force extend
Write-Host "`n--- Forcing extend mode ---"
displayswitch.exe /extend
Start-Sleep 3

# Check what RTX outputs are connected
Write-Host "`n--- RTX 5090 outputs (NVIDIA) ---"
$nv = Get-CimInstance -Namespace root/cimv2 -ClassName Win32_DesktopMonitor -ErrorAction SilentlyContinue
foreach ($m in $nv) {
    Write-Host "  $($m.Name) PNPId=$($m.PNPDeviceID) Status=$($m.Status)"
}

# Get NVIDIA display info
Write-Host "`n--- NVIDIA connected displays ---"
nvidia-smi --query-gpu=name,display_mode,display_active --format=csv,noheader 2>&1

Write-Host "`n--- All screens ---"
Add-Type -AssemblyName System.Windows.Forms
$screens = [System.Windows.Forms.Screen]::AllScreens
Write-Host "  Count: $($screens.Count)"
foreach ($s in $screens) {
    Write-Host "  $($s.DeviceName) $($s.Bounds.Width)x$($s.Bounds.Height) Primary=$($s.Primary)"
}

# What's plugged into what on the RTX?
Write-Host "`n--- Monitor connection status ---"
Get-PnpDevice -Class Monitor | ForEach-Object {
    $props = Get-PnpDeviceProperty -InstanceId $_.InstanceId -ErrorAction SilentlyContinue
    $parent = ($props | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_Parent' }).Data
    $loc = ($props | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_LocationInfo' }).Data
    Write-Host "  $($_.FriendlyName) [$($_.Status)] Parent=$parent"
}

# USB-C SPINE — what's in each port?
Write-Host "`n--- USB-C SPINE MAP ---"
Write-Host "  USB Controllers and their children:"
$controllers = Get-PnpDevice -Class USB -Status OK | Where-Object { $_.FriendlyName -match 'Host Controller|USB4' }
foreach ($ctrl in $controllers) {
    $busType = ""
    if ($ctrl.InstanceId -match '15B6') { $busType = "(CPU 10Gbps)" }
    elseif ($ctrl.InstanceId -match '15B7') { $busType = "(CPU 5Gbps)" }  
    elseif ($ctrl.InstanceId -match '15B8') { $busType = "(CPU USB2)" }
    elseif ($ctrl.InstanceId -match '43FD') { $busType = "(Chipset 10Gbps)" }
    elseif ($ctrl.InstanceId -match '2425') { $busType = "(USB4 40Gbps)" }
    elseif ($ctrl.InstanceId -match '2426') { $busType = "(ASMedia 20Gbps)" }
    Write-Host "  $($ctrl.FriendlyName) $busType"
    
    # Find devices under this controller
    $children = Get-PnpDevice -Status OK | Where-Object { 
        $_.InstanceId -match $ctrl.InstanceId.Split('\')[-1].Substring(0,8) -and
        $_.InstanceId -ne $ctrl.InstanceId -and
        $_.Class -ne 'USB'
    }
}

# What is the Keychron plugged into?
Write-Host "`n--- Keychron (VID_3434) location ---"
$kb = Get-PnpDevice -Status OK | Where-Object { $_.InstanceId -match 'VID_3434' }
foreach ($k in $kb) {
    $parent = (Get-PnpDeviceProperty -InstanceId $k.InstanceId -ErrorAction SilentlyContinue | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_Parent' }).Data
    Write-Host "  $($k.FriendlyName) Parent=$parent"
}

Write-Host "`n--- LG cable check ---"
Write-Host "  Is LG on HDMI or DP on the RTX?"
Write-Host "  RTX 5090 has: 1x HDMI 2.1 + 3x DisplayPort 2.1"
Write-Host "  If LG is on HDMI: try DP cable instead"
Write-Host "  If LG is on DP: check cable is seated fully"
