# SPLIT BRAIN CHECK - Where's the rest of the NVMe? Who's the other user?
Write-Host "=" * 60
Write-Host "  SPLIT BRAIN CHECK"
Write-Host "=" * 60

Write-Host "`n--- DISK PARTITIONS (where's the missing space?) ---"
Get-Partition | Select-Object DiskNumber, PartitionNumber, DriveLetter, @{N="SizeGB";E={[math]::Round($_.Size/1GB,2)}}, Type, IsSystem, IsBoot | Format-Table -AutoSize

Write-Host "`n--- ALL DISKS ---"
Get-Disk | Select-Object Number, FriendlyName, @{N="SizeGB";E={[math]::Round($_.Size/1GB,1)}}, PartitionStyle, OperationalStatus | Format-Table -AutoSize

Write-Host "`n--- VOLUMES ---"
Get-Volume | Select-Object DriveLetter, FileSystemLabel, FileSystem, @{N="SizeGB";E={[math]::Round($_.Size/1GB,2)}}, @{N="FreeGB";E={[math]::Round($_.SizeRemaining/1GB,2)}}, DriveType | Format-Table -AutoSize

Write-Host "`n--- USER ACCOUNTS ---"
Get-LocalUser | Select-Object Name, Enabled, LastLogon, Description | Format-Table -AutoSize

Write-Host "`n--- USER PROFILES ---"
Get-CimInstance Win32_UserProfile | Where-Object { -not $_.Special } | Select-Object LocalPath, @{N="SizeGB";E={[math]::Round($_.Size/1GB,2) }}, LastUseTime, Loaded | Format-Table -AutoSize

Write-Host "`n--- WHO IS LOGGED IN ---"
query user 2>&1

Write-Host "`n--- WSL (Linux in sidebar?) ---"
wsl --list --verbose 2>&1
