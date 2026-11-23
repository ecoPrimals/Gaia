# MILK-V JUPITER 2 SENSE — Feel the RISC-V hardware
Write-Host "=" * 60
Write-Host "  MILK-V JUPITER SENSE — Can we feel the RISC-V body?"
Write-Host "=" * 60

Write-Host "`n--- ALL USB DEVICES (active) ---"
Get-PnpDevice -Class USB -Status OK | Select-Object FriendlyName, InstanceId | Format-Table -AutoSize

Write-Host "`n--- USB HUBS ---"
Get-PnpDevice -Class USB -Status OK | Where-Object { $_.FriendlyName -like '*Hub*' } | Select-Object FriendlyName, InstanceId | Format-Table -AutoSize

Write-Host "`n--- NEW/UNKNOWN USB (last 30 min) ---"
$cutoff = (Get-Date).AddMinutes(-30)
Get-WinEvent -FilterHashtable @{LogName='System'; ProviderName='Microsoft-Windows-Kernel-PnP'; StartTime=$cutoff} -ErrorAction SilentlyContinue | Select-Object -First 15 TimeCreated, Message | Format-Table -AutoSize

Write-Host "`n--- USB SERIAL / CDC / RNDIS (RISC-V boards show as these) ---"
Get-PnpDevice -Status OK | Where-Object { $_.FriendlyName -match 'Serial|CDC|RNDIS|Gadget|RISC|Milk|Jupiter|StarFive|SiFive|SpacemiT|Ethernet.*USB|Network.*USB' } | Select-Object FriendlyName, Class, InstanceId | Format-Table -AutoSize

Write-Host "`n--- NETWORK ADAPTERS (USB link would show here) ---"
Get-NetAdapter | Select-Object Name, InterfaceDescription, Status, LinkSpeed, MacAddress | Format-Table -AutoSize

Write-Host "`n--- USB COMPOSITE / MASS STORAGE ---"
Get-PnpDevice -Status OK | Where-Object { $_.Class -eq 'USB' -or $_.Class -eq 'DiskDrive' -or $_.Class -eq 'Ports' -or $_.Class -eq 'Net' } | Select-Object FriendlyName, Class, Status, InstanceId | Format-Table -AutoSize

Write-Host "`n--- DISK DRIVES (Milk-V might show as USB disk) ---"
Get-Disk | Select-Object Number, FriendlyName, BusType, Size, OperationalStatus | Format-Table -AutoSize

Write-Host "`n--- USB-C / Thunderbolt ---"
Get-PnpDevice -Status OK | Where-Object { $_.FriendlyName -match 'Thunderbolt|USB4|TypeC|USB-C|Billboard' } | Select-Object FriendlyName, Class, InstanceId | Format-Table -AutoSize

Write-Host "`n--- DANGER CHECK: Power draw ---"
$usbControllers = Get-CimInstance Win32_USBController
foreach ($c in $usbControllers) {
    Write-Host "  Controller: $($c.Name) [$($c.Status)]"
}

Write-Host "`n--- ALL PnP events last 10 min ---"
$cutoff2 = (Get-Date).AddMinutes(-10)
Get-WinEvent -FilterHashtable @{LogName='System'; StartTime=$cutoff2} -ErrorAction SilentlyContinue | Where-Object { $_.Message -match 'USB|device|plug|connect' } | Select-Object -First 20 TimeCreated, Id, Message | Format-List
