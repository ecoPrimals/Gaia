# GAIA USER + DRIVE HISTORY
Write-Host "=" * 60
Write-Host "  GAIA USER + DRIVE ARCHAEOLOGY"
Write-Host "=" * 60

# Who is the gaia user?
Write-Host "`n--- GAIA LOCAL USER ---"
Get-LocalUser -Name 'gaia' | Select-Object Name, Enabled, PasswordRequired, LastLogon, Description, SID | Format-List

# Does gaia have a profile folder?
Write-Host "--- GAIA PROFILE ---"
if (Test-Path 'C:\Users\gaia') {
    Get-ChildItem 'C:\Users\gaia' -Depth 1 -ErrorAction SilentlyContinue | Select-Object Name, LastWriteTime | Format-Table -AutoSize
} else {
    Write-Host "  No C:\Users\gaia folder exists (never logged in)"
}

# When was gaia user created?
Write-Host "`n--- GAIA user creation event ---"
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4720} -ErrorAction SilentlyContinue | Where-Object { $_.Message -match 'gaia' } | Select-Object -First 3 TimeCreated, Message | Format-List

# Where was the M: drive?
Write-Host "`n--- DRIVE LETTER HISTORY (Registry) ---"
$mountPoints = Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\MountPoints2\*' -ErrorAction SilentlyContinue
foreach ($mp in $mountPoints) {
    $name = Split-Path $mp.PSPath -Leaf
    Write-Host "  $name"
}

# Check if M: was a volume mount
Write-Host "`n--- Volume mount points ---"
mountvol 2>&1 | Select-String -Pattern 'M:\\|Volume|mount' -Context 0,1

# Were the 4TB drives EVER online? Check event logs
Write-Host "`n--- Disk arrival history (last 7 days) ---"
$weekAgo = (Get-Date).AddDays(-7)
Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Kernel-PnP/Device Configuration'; StartTime=$weekAgo} -ErrorAction SilentlyContinue | Where-Object { $_.Message -match 'SN850X|990 PRO 4TB|NVMe' } | Select-Object -First 10 TimeCreated, Message | Format-List

# Were they ever mounted as volumes?
Write-Host "`n--- All volume GUIDs (including ghost) ---"
Get-CimInstance Win32_Volume | Select-Object Name, Label, DriveLetter, @{N="SizeGB";E={[math]::Round($_.Capacity/1GB,1)}}, FileSystem | Format-Table -AutoSize

# Check if drives are physically present or ghost PnP entries
Write-Host "`n--- NVMe PHYSICAL presence (devcon) ---"
Get-PnpDevice -Class SCSIAdapter | Where-Object { $_.InstanceId -match 'VEN_144D|VEN_15B7' } | ForEach-Object {
    $loc = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName DEVPKEY_Device_LocationInfo -ErrorAction SilentlyContinue).Data
    Write-Host "  $($_.FriendlyName) [$($_.Status)] Location: $loc"
}

# Steam library config (where was M:?)
Write-Host "`n--- Steam library folders ---"
$steamConfig = 'C:\Program Files (x86)\Steam\config\libraryfolders.vdf'
if (Test-Path $steamConfig) {
    Get-Content $steamConfig
} else {
    Write-Host "  No Steam library config found"
}
