# FIND THE M: DRIVE — Why are Bus 3 + Bus 4 NVMe dead?
Write-Host "=" * 60
Write-Host "  FIND M: DRIVE — NVMe archaeology"
Write-Host "=" * 60

# PCIe topology — what's alive on each bus?
Write-Host "`n--- PCIe TOPOLOGY (all buses with NVMe) ---"
Get-PnpDevice | Where-Object { $_.InstanceId -match 'PCI\\VEN' } | ForEach-Object {
    if ($_.InstanceId -match 'PCI\\VEN_(\w+)&DEV_(\w+).*\\(\d+)&') {
        $ven = $Matches[1]; $dev = $Matches[2]
    }
    $loc = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName DEVPKEY_Device_LocationInfo -ErrorAction SilentlyContinue).Data
    if ($loc -match 'bus [234],') {
        Write-Host "  $($_.FriendlyName) [$($_.Status)] $loc"
    }
} 

# Deeper: ALL PCI devices on Bus 2,3,4
Write-Host "`n--- ALL PCI devices on Bus 2, 3, 4 ---"
Get-PnpDevice | Where-Object { $_.InstanceId -match 'PCI\\' } | ForEach-Object {
    $loc = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName DEVPKEY_Device_LocationInfo -ErrorAction SilentlyContinue).Data
    if ($loc -match 'bus (2|3|4),') {
        Write-Host "  Bus $($Matches[1]): $($_.FriendlyName) [$($_.Status)]"
    }
}

# Check the DEAD controllers - what error code?
Write-Host "`n--- DEAD NVMe controller details ---"
$dead = @(
    'PCI\VEN_15B7&DEV_5030&SUBSYS_503015B7&REV_01\4&285F7309&0&000C',
    'PCI\VEN_144D&DEV_A80C&SUBSYS_A801144D&REV_00\4&15A5C264&0&000B'
)
foreach ($id in $dead) {
    $dev = Get-PnpDevice | Where-Object { $_.InstanceId -eq $id }
    if ($dev) {
        Write-Host "`n  Device: $($dev.FriendlyName) [$($dev.Status)]"
        
        # Get problem code
        $prob = (Get-PnpDeviceProperty -InstanceId $id -KeyName DEVPKEY_Device_ProblemCode -ErrorAction SilentlyContinue).Data
        $probDesc = (Get-PnpDeviceProperty -InstanceId $id -KeyName DEVPKEY_Device_ProblemStatus -ErrorAction SilentlyContinue).Data
        Write-Host "  Problem code: $prob"
        Write-Host "  Problem status: $probDesc"
        
        # Config flags
        $flags = (Get-PnpDeviceProperty -InstanceId $id -KeyName DEVPKEY_Device_ConfigFlags -ErrorAction SilentlyContinue).Data
        Write-Host "  Config flags: $flags"
        
        # Install date
        $install = (Get-PnpDeviceProperty -InstanceId $id -KeyName DEVPKEY_Device_InstallDate -ErrorAction SilentlyContinue).Data
        Write-Host "  Install date: $install"
        
        # Last known parent
        $parent = (Get-PnpDeviceProperty -InstanceId $id -KeyName DEVPKEY_Device_Parent -ErrorAction SilentlyContinue).Data
        Write-Host "  Parent: $parent"
        
        $loc = (Get-PnpDeviceProperty -InstanceId $id -KeyName DEVPKEY_Device_LocationInfo -ErrorAction SilentlyContinue).Data
        Write-Host "  Location: $loc"
        
        # Is it currently present?
        $present = (Get-PnpDeviceProperty -InstanceId $id -KeyName DEVPKEY_Device_IsPresent -ErrorAction SilentlyContinue).Data
        Write-Host "  Is Present: $present"
    }
}

# Check if there's a BIOS/UEFI variable about M.2 slots
Write-Host "`n--- Setup variable M.2/PCIe hints ---"
# The AMD_PBS_SETUP we dumped before had PCIe settings
# Let's check if there's a PCI bridge for bus 3 and 4
Get-PnpDevice | Where-Object { $_.FriendlyName -match 'PCI.*bridge|PCIe.*switch|Root.*Port' -and $_.Status -ne 'OK' } | ForEach-Object {
    $loc = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName DEVPKEY_Device_LocationInfo -ErrorAction SilentlyContinue).Data
    Write-Host "  $($_.FriendlyName) [$($_.Status)] $loc"
}

# Registry: last known M: drive
Write-Host "`n--- Registry: M: drive mapping ---"
$mpDB = 'HKLM:\SYSTEM\MountedDevices'
$mDrive = (Get-ItemProperty $mpDB -ErrorAction SilentlyContinue).'\DosDevices\M:'
if ($mDrive) {
    $hex = ($mDrive | ForEach-Object { '{0:X2}' -f $_ }) -join ' '
    Write-Host "  M: was mapped to: $($hex.Substring(0, [Math]::Min(80, $hex.Length)))..."
} else {
    Write-Host "  M: has NO registry mapping (never mounted or cleaned up)"
}

# Check ALL mounted device entries
Write-Host "`n--- All drive letter mappings ---"
$props = Get-ItemProperty $mpDB -ErrorAction SilentlyContinue
foreach ($name in $props.PSObject.Properties.Name) {
    if ($name -match '\\DosDevices\\(\w):') {
        Write-Host "  $($Matches[1]):"
    }
}

# Were drives ever seen in this boot?
Write-Host "`n--- System event log: disk/storage errors ---"
$boot = (Get-Date).AddHours(-1)
Get-WinEvent -FilterHashtable @{LogName='System'; Level=2,3; StartTime=$boot} -ErrorAction SilentlyContinue | Where-Object { $_.Message -match 'disk|nvme|storage|pci|bus|slot|device.*error|device.*fail' } | Select-Object -First 10 TimeCreated, Id, @{N="Msg";E={$_.Message.Substring(0, [Math]::Min(200, $_.Message.Length))}} | Format-Table -AutoSize
