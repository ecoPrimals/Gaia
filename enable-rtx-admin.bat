@echo off
echo Enabling RTX 5090...
powershell -Command "Start-Process powershell -ArgumentList '-Command Enable-PnpDevice -InstanceId \"PCI\VEN_10DE&DEV_2B85&SUBSYS_1446196E&REV_A1\2E6615A7EF2DB04800\" -Confirm:$false; Start-Sleep 3; Get-PnpDevice -Class Display | Format-Table FriendlyName,Status,Problem -AutoSize' -Verb RunAs -Wait"
echo Done. Check Device Manager.
pause
