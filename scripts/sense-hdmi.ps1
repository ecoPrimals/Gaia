
# Check EDID on the BasicDisplay-connected LG
$lg_basic = Get-PnpDevice -Class Monitor | Where-Object { 
    $_.Status -eq "Unknown" -and $_.FriendlyName -like "*LG*"
}
foreach ($lg in $lg_basic) {
    $parent = (Get-PnpDeviceProperty -InstanceId $lg.InstanceId -KeyName DEVPKEY_Device_Parent -ErrorAction SilentlyContinue).Data
    $locpath = (Get-PnpDeviceProperty -InstanceId $lg.InstanceId -KeyName DEVPKEY_Device_LocationPaths -ErrorAction SilentlyContinue).Data
    Write-Output ("LG: " + $lg.InstanceId)
    Write-Output ("  Status: " + $lg.Status)
    Write-Output ("  Parent: " + $parent)
    Write-Output ("  Path: " + ($locpath -join " | "))
    
    # Read EDID from registry — this proves DDC/I2C is working
    $regPath = "HKLM:\SYSTEM\CurrentControlSet\Enum\" + $lg.InstanceId + "\Device Parameters"
    $edid = Get-ItemProperty $regPath -Name EDID -ErrorAction SilentlyContinue
    if ($null -ne $edid -and $null -ne $edid.EDID) {
        $edidHex = ($edid.EDID | ForEach-Object { "{0:X2}" -f $_ }) -join " "
        Write-Output ("  EDID: " + $edidHex.Substring(0, [Math]::Min(80, $edidHex.Length)) + "...")
        Write-Output ("  EDID length: " + $edid.EDID.Length + " bytes — DDC ALIVE!")
        
        # Parse manufacturer from EDID bytes 8-9
        $mfg1 = $edid.EDID[8]
        $mfg2 = $edid.EDID[9]
        $c1 = [char](64 + (($mfg1 -shr 2) -band 0x1F))
        $c2 = [char](64 + ((($mfg1 -band 0x03) -shl 3) -bor (($mfg2 -shr 5) -band 0x07)))
        $c3 = [char](64 + ($mfg2 -band 0x1F))
        Write-Output ("  Manufacturer: " + $c1 + $c2 + $c3)
        
        # Resolution from detailed timing (bytes 54+)
        if ($edid.EDID.Length -gt 58) {
            $hActive = $edid.EDID[56] + (($edid.EDID[58] -shr 4) * 256)
            $vActive = $edid.EDID[59] + (($edid.EDID[61] -shr 4) * 256)
            Write-Output ("  Native: " + $hActive + "x" + $vActive)
        }
    } else {
        Write-Output "  EDID: not found"
    }
}

# Compare with the working RTX-connected displays
Write-Output "`n--- RTX 5090 displays (right eye) ---"
$rtx_mons = Get-PnpDevice -Class Monitor | Where-Object { $_.Status -eq "OK" }
foreach ($m in $rtx_mons) {
    $parent = (Get-PnpDeviceProperty -InstanceId $m.InstanceId -KeyName DEVPKEY_Device_Parent -ErrorAction SilentlyContinue).Data
    Write-Output ($m.FriendlyName + " Status=" + $m.Status + " Parent=" + $parent)
}
