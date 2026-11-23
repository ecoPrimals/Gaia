# NULL PORT TRACE — Find the origin of the dead PCIe links
# Why are RP05/RP06 null? Trace to source.

Write-Host "=== NULL PORT TRACE — FIND THE ORIGIN ==="

# 1. Get device error codes for the ghost controllers
Write-Host "`n--- Ghost controller error codes ---"
$ghosts = @(
    "PCI\VEN_15B7&DEV_5030&SUBSYS_503015B7&REV_01\4&285F7309&0&000C",
    "PCI\VEN_144D&DEV_A80C&SUBSYS_A801144D&REV_00\4&15A5C264&0&000B"
)
foreach ($id in $ghosts) {
    $dev = Get-PnpDevice -InstanceId $id -ErrorAction SilentlyContinue
    if ($dev) {
        $prop = Get-PnpDeviceProperty -InstanceId $id -ErrorAction SilentlyContinue
        $configFlags = ($prop | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_ConfigFlags' }).Data
        $problem = ($prop | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_ProblemCode' }).Data
        $problemStatus = ($prop | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_ProblemStatus' }).Data
        $installState = ($prop | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_InstallState' }).Data
        $removalPolicy = ($prop | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_RemovalPolicy' }).Data
        $parentId = ($prop | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_Parent' }).Data
        $locationInfo = ($prop | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_LocationInfo' }).Data
        $busNum = ($prop | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_BusNumber' }).Data
        $address = ($prop | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_Address' }).Data
        
        Write-Host "  Device: $($dev.FriendlyName)"
        Write-Host "  Status: $($dev.Status)"
        Write-Host "  ProblemCode: $problem"
        Write-Host "  ProblemStatus: $problemStatus"
        Write-Host "  ConfigFlags: $configFlags"
        Write-Host "  InstallState: $installState"
        Write-Host "  Parent: $parentId"
        Write-Host "  Location: $locationInfo"
        Write-Host "  BusNumber: $busNum"
        Write-Host "  Address: $address"
        Write-Host ""
    }
}

# 2. Trace PARENT devices — who owns these controllers?
Write-Host "--- Parent chain (trace to root) ---"
foreach ($id in $ghosts) {
    Write-Host "  Tracing: $id"
    $current = $id
    for ($i = 0; $i -lt 5; $i++) {
        $props = Get-PnpDeviceProperty -InstanceId $current -ErrorAction SilentlyContinue
        $parent = ($props | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_Parent' }).Data
        if ($parent) {
            $pdev = Get-PnpDevice -InstanceId $parent -ErrorAction SilentlyContinue
            Write-Host "    L$i -> $($pdev.FriendlyName) [$($pdev.Status)] $parent"
            $current = $parent
        } else {
            Write-Host "    L$i -> (ROOT)"
            break
        }
    }
    Write-Host ""
}

# 3. Compare working vs ghost NVMe parent chains
Write-Host "--- Working NVMe parent chain ---"
$working = "PCI\VEN_144D&DEV_A80C&SUBSYS_A801144D&REV_00\4&2EC11BF&0&000A"
$current = $working
for ($i = 0; $i -lt 5; $i++) {
    $props = Get-PnpDeviceProperty -InstanceId $current -ErrorAction SilentlyContinue
    $parent = ($props | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_Parent' }).Data
    $loc = ($props | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_LocationInfo' }).Data
    $bus = ($props | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_BusNumber' }).Data
    if ($parent) {
        $pdev = Get-PnpDevice -InstanceId $parent -ErrorAction SilentlyContinue
        Write-Host "  L$i -> $($pdev.FriendlyName) [$($pdev.Status)] Bus=$bus Loc=$loc"
        $current = $parent
    } else {
        break
    }
}

# 4. ALL PCI Express Root Ports with their children
Write-Host "`n--- ALL Root Ports + Children ---"
$rootPorts = Get-PnpDevice | Where-Object { $_.FriendlyName -match 'PCI Express Root Port' -and $_.Class -eq 'System' }
foreach ($rp in $rootPorts) {
    $rpProps = Get-PnpDeviceProperty -InstanceId $rp.InstanceId -ErrorAction SilentlyContinue
    $rpLoc = ($rpProps | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_LocationInfo' }).Data
    $rpBus = ($rpProps | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_BusNumber' }).Data
    $rpAddr = ($rpProps | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_Address' }).Data
    
    # Find children
    $children = Get-PnpDevice | Where-Object { 
        $cProps = Get-PnpDeviceProperty -InstanceId $_.InstanceId -ErrorAction SilentlyContinue
        $cParent = ($cProps | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_Parent' }).Data
        $cParent -eq $rp.InstanceId
    }
    
    $childStr = if ($children) { ($children | ForEach-Object { "$($_.FriendlyName)[$($_.Status)]" }) -join ", " } else { "(EMPTY)" }
    
    Write-Host "  RP Bus=$rpBus Addr=$rpAddr Loc=$rpLoc [$($rp.Status)]"
    Write-Host "     -> $childStr"
}

# 5. Check for disabled devices in registry
Write-Host "`n--- Registry: Disabled NVMe entries ---"
$nvmeKeys = Get-ChildItem "HKLM:\SYSTEM\CurrentControlSet\Enum\PCI" -ErrorAction SilentlyContinue | 
    Where-Object { $_.Name -match '15B7|144D' }
foreach ($k in $nvmeKeys) {
    $subkeys = Get-ChildItem $k.PSPath -ErrorAction SilentlyContinue
    foreach ($sk in $subkeys) {
        $configFlags = (Get-ItemProperty $sk.PSPath -Name ConfigFlags -ErrorAction SilentlyContinue).ConfigFlags
        $problemCode = (Get-ItemProperty $sk.PSPath -Name ConfigFlags -ErrorAction SilentlyContinue).ConfigFlags
        Write-Host "  $($sk.PSChildName): ConfigFlags=$configFlags"
    }
}

# 6. Check power state
Write-Host "`n--- Device power state ---"
foreach ($id in $ghosts) {
    $props = Get-PnpDeviceProperty -InstanceId $id -ErrorAction SilentlyContinue
    $powerState = ($props | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_PowerData' }).Data
    $powerRelations = ($props | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_PowerRelations' }).Data
    Write-Host "  $id"
    Write-Host "    PowerData: $powerState"
    Write-Host "    PowerRelations: $powerRelations"
}

Write-Host "`n=== TRACE COMPLETE ==="
