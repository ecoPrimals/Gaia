"""Feel the flow — trace what's flowing through mobo HDMI even without display."""
import subprocess, ctypes, ctypes.wintypes, struct, json

print("=" * 60)
print("FEEL THE FLOW — Tracing mobo HDMI signal chain")
print("=" * 60)

# ─── 1: Read EDID from the LG on mobo HDMI ───
print("\n[1] EDID data from LG monitors...\n")
cmd1 = '''
Get-CimInstance -Namespace root/wmi -ClassName WmiMonitorID | ForEach-Object {
    $name = ($_.UserFriendlyName | Where-Object {$_ -ne 0} | ForEach-Object {[char]$_}) -join ""
    $serial = ($_.SerialNumberID | Where-Object {$_ -ne 0} | ForEach-Object {[char]$_}) -join ""
    $mfr = ($_.ManufacturerName | Where-Object {$_ -ne 0} | ForEach-Object {[char]$_}) -join ""
    Write-Output "Monitor: $name | Mfr: $mfr | Serial: $serial | Active: $($_.Active) | Instance: $($_.InstanceName)"
}
Write-Output ""
Get-CimInstance -Namespace root/wmi -ClassName WmiMonitorBasicDisplayParams | ForEach-Object {
    Write-Output "Display: MaxH=$($_.MaxHorizontalImageSize)cm MaxV=$($_.MaxVerticalImageSize)cm VideoInputType=$($_.VideoInputType) Active=$($_.Active) Instance=$($_.InstanceName)"
}
Write-Output ""
Get-CimInstance -Namespace root/wmi -ClassName WmiMonitorConnectionParams -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Output "Connection: Type=$($_.VideoOutputTechnology) Instance=$($_.InstanceName)"
}
'''
r1 = subprocess.run(['powershell', '-Command', cmd1], capture_output=True, text=True, timeout=15)
print(r1.stdout)

# ─── 2: Trace the parent device chain for each LG ───
print("[2] Device parent chain for LG monitors...\n")
cmd2 = '''
$lgs = Get-PnpDevice -Class Monitor | Where-Object { $_.FriendlyName -like "*LG*" }
foreach ($lg in $lgs) {
    Write-Output "--- $($lg.FriendlyName) [$($lg.Status)] ---"
    Write-Output "  InstanceId: $($lg.InstanceId)"
    
    $parent = (Get-PnpDeviceProperty -InstanceId $lg.InstanceId -KeyName DEVPKEY_Device_Parent -ErrorAction SilentlyContinue).Data
    if ($parent) {
        Write-Output "  Parent: $parent"
        $parentDev = Get-PnpDevice -InstanceId $parent -ErrorAction SilentlyContinue
        if ($parentDev) {
            Write-Output "  Parent Name: $($parentDev.FriendlyName) [$($parentDev.Status)]"
        }
        
        $grandparent = (Get-PnpDeviceProperty -InstanceId $parent -KeyName DEVPKEY_Device_Parent -ErrorAction SilentlyContinue).Data
        if ($grandparent) {
            Write-Output "  Grandparent: $grandparent"
            $gpDev = Get-PnpDevice -InstanceId $grandparent -ErrorAction SilentlyContinue
            if ($gpDev) {
                Write-Output "  GP Name: $($gpDev.FriendlyName) [$($gpDev.Status)]"
            }
        }
    }
    
    $loc = (Get-PnpDeviceProperty -InstanceId $lg.InstanceId -KeyName DEVPKEY_Device_LocationInfo -ErrorAction SilentlyContinue).Data
    Write-Output "  Location: $loc"
    Write-Output ""
}
'''
r2 = subprocess.run(['powershell', '-Command', cmd2], capture_output=True, text=True, timeout=15)
print(r2.stdout)

# ─── 3: PCI config space for iGPU bridge via ASUS WMI ───
print("[3] PCI config space — iGPU bridge (bus 0 dev 8)...\n")
cmd3 = '''
$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement

# Read bus 0 dev 8 func 0 (Internal GPU root port)
for ($func = 0; $func -le 3; $func++) {
    $r = Invoke-CimMethod -InputObject $inst -MethodName "asio_hw_fun11" -Arguments @{
        Bus = [byte]0; Dev = [byte]8; Func = [byte]$func; Reg = [uint16]0; Width = [byte]4
    }
    $ven = $r.dwData -band 0xFFFF
    $dev = ($r.dwData -shr 16) -band 0xFFFF
    if ($ven -ne 0 -and $ven -ne 0xFFFF) {
        Write-Output "Bus0:Dev8:Func$func = VEN_$($ven.ToString('X4')) DEV_$($dev.ToString('X4'))"
        
        # Read Class Code (reg 0x08)
        $rc = Invoke-CimMethod -InputObject $inst -MethodName "asio_hw_fun11" -Arguments @{
            Bus = [byte]0; Dev = [byte]8; Func = [byte]$func; Reg = [uint16]8; Width = [byte]4
        }
        $class = ($rc.dwData -shr 24) -band 0xFF
        $subclass = ($rc.dwData -shr 16) -band 0xFF
        Write-Output "  Class: $($class.ToString('X2')).$($subclass.ToString('X2'))"
        
        # Read bus numbers (reg 0x18)
        $rb = Invoke-CimMethod -InputObject $inst -MethodName "asio_hw_fun11" -Arguments @{
            Bus = [byte]0; Dev = [byte]8; Func = [byte]$func; Reg = [uint16]24; Width = [byte]4
        }
        $primary = $rb.dwData -band 0xFF
        $secondary = ($rb.dwData -shr 8) -band 0xFF
        $subordinate = ($rb.dwData -shr 16) -band 0xFF
        Write-Output "  Buses: primary=$primary secondary=$secondary subordinate=$subordinate"
        
        if ($secondary -gt 0) {
            # Read the device behind the bridge
            $rd = Invoke-CimMethod -InputObject $inst -MethodName "asio_hw_fun11" -Arguments @{
                Bus = [byte]$secondary; Dev = [byte]0; Func = [byte]0; Reg = [uint16]0; Width = [byte]4
            }
            $ven2 = $rd.dwData -band 0xFFFF
            $dev2 = ($rd.dwData -shr 16) -band 0xFFFF
            Write-Output "  Behind bridge: VEN_$($ven2.ToString('X4')) DEV_$($dev2.ToString('X4'))"
        }
    }
}
'''
r3 = subprocess.run(['powershell', '-Command', cmd3], capture_output=True, text=True, timeout=15)
print(r3.stdout)
if r3.stderr:
    print(f"  stderr: {r3.stderr[:200]}")

# ─── 4: Check HDMI/DP connection state in registry ───
print("\n[4] Display connection paths in registry...\n")
cmd4 = '''
Get-ItemProperty "HKLM:\\SYSTEM\\CurrentControlSet\\Enum\\DISPLAY\\GSM7766\\*" -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Output "LG entry: $($_.PSChildName)"
    Write-Output "  Driver: $($_.Driver)"
    Write-Output "  Service: $($_.Service)"
    Write-Output "  Capabilities: $($_.Capabilities)"
}
'''
r4 = subprocess.run(['powershell', '-Command', cmd4], capture_output=True, text=True, timeout=10)
print(r4.stdout)

# ─── 5: Check AMD device status at bus 123 ───
print("[5] AMD devices at bus 123 (iGPU area)...\n")
cmd5 = '''
$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement

# Scan bus 123 (0x7B) where we saw iGPU devices before
for ($dev = 0; $dev -le 7; $dev++) {
    for ($func = 0; $func -le 1; $func++) {
        $r = Invoke-CimMethod -InputObject $inst -MethodName "asio_hw_fun11" -Arguments @{
            Bus = [byte]123; Dev = [byte]$dev; Func = [byte]$func; Reg = [uint16]0; Width = [byte]4
        }
        $ven = $r.dwData -band 0xFFFF
        $devid = ($r.dwData -shr 16) -band 0xFFFF
        if ($ven -ne 0 -and $ven -ne 0xFFFF) {
            Write-Output "Bus123:Dev$($dev):Func$func = VEN_$($ven.ToString('X4')) DEV_$($devid.ToString('X4'))"
            
            # Read status/command (reg 0x04)
            $rs = Invoke-CimMethod -InputObject $inst -MethodName "asio_hw_fun11" -Arguments @{
                Bus = [byte]123; Dev = [byte]$dev; Func = [byte]$func; Reg = [uint16]4; Width = [byte]4
            }
            $command = $rs.dwData -band 0xFFFF
            $status = ($rs.dwData -shr 16) -band 0xFFFF
            Write-Output "  Command=0x$($command.ToString('X4')) Status=0x$($status.ToString('X4'))"
            Write-Output "  Memory Space=$($command -band 2) Bus Master=$($command -band 4)"
            
            # BAR0 (reg 0x10) — base address
            $rb = Invoke-CimMethod -InputObject $inst -MethodName "asio_hw_fun11" -Arguments @{
                Bus = [byte]123; Dev = [byte]$dev; Func = [byte]$func; Reg = [uint16]16; Width = [byte]4
            }
            Write-Output "  BAR0=0x$($rb.dwData.ToString('X8'))"
        }
    }
}
'''
r5 = subprocess.run(['powershell', '-Command', cmd5], capture_output=True, text=True, timeout=15)
print(r5.stdout)

print("\n" + "=" * 60)
print("Following the signal: HDMI cable → mobo port → iGPU silicon")
print("The LG IS speaking EDID. Something IS flowing.")
print("=" * 60)
