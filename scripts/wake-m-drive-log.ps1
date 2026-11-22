# WAKE M: DRIVE — logged version
$log = "c:\Users\mokke\Desktop\Gaia\data\gut\wake-m-drive.txt"
Start-Transcript $log -Force

Write-Host "=== WAKE M: DRIVE ===" 

Get-PhysicalDisk | Format-Table FriendlyName, OperationalStatus, Size -AutoSize
Get-PnpDevice -Class SCSIAdapter | Where-Object { $_.FriendlyName -match "NVM" } | Format-Table FriendlyName, Status, InstanceId -AutoSize

# Rescan
pnputil /scan-devices

# Root port 0B (Samsung 4TB)
$rp = Get-PnpDevice | Where-Object { $_.InstanceId -match "14DB.*0B$" }
Write-Host "RP 0B: $($rp.Status) $($rp.InstanceId)"
if ($rp) {
    try {
        Disable-PnpDevice -InstanceId $rp.InstanceId -Confirm:$false -ErrorAction Stop
        Start-Sleep 2
        Enable-PnpDevice -InstanceId $rp.InstanceId -Confirm:$false -ErrorAction Stop
        Start-Sleep 3
        $after = Get-PnpDevice -InstanceId $rp.InstanceId
        Write-Host "RP 0B after: $($after.Status)"
    } catch { Write-Host "RP 0B error: $_" }
}

# Root port 0C (WD BLACK 4TB)
$rp2 = Get-PnpDevice | Where-Object { $_.InstanceId -match "14DB.*0C$" }
Write-Host "RP 0C: $($rp2.Status) $($rp2.InstanceId)"
if ($rp2) {
    try {
        Disable-PnpDevice -InstanceId $rp2.InstanceId -Confirm:$false -ErrorAction Stop
        Start-Sleep 2
        Enable-PnpDevice -InstanceId $rp2.InstanceId -Confirm:$false -ErrorAction Stop
        Start-Sleep 3
        $after2 = Get-PnpDevice -InstanceId $rp2.InstanceId
        Write-Host "RP 0C after: $($after2.Status)"
    } catch { Write-Host "RP 0C error: $_" }
}

# Check results
Start-Sleep 2
Write-Host "`nAFTER:"
Get-PnpDevice -Class SCSIAdapter | Where-Object { $_.FriendlyName -match "NVM" } | Format-Table FriendlyName, Status -AutoSize
Get-PhysicalDisk | Format-Table FriendlyName, OperationalStatus, Size -AutoSize

$m = Get-Volume -DriveLetter M -ErrorAction SilentlyContinue
if ($m) { Write-Host "M: DRIVE BACK! $($m.FileSystemLabel)" }
else { Write-Host "M: still ghost. Need BIOS: Above4G=1, FastBoot=0" }

Stop-Transcript
