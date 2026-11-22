"""Diagnose why iGPU driver won't load despite BIOS Force"""
import subprocess

print("=== iGPU DRIVER DIAGNOSIS ===\n")

# 1. Detailed device properties
print("[1] Device Properties...\n")
cmd1 = '''
$dev = Get-PnpDevice | Where-Object { $_.InstanceId -like "*VEN_1002&DEV_13C0*" }
foreach ($d in $dev) {
    Write-Output "Name: $($d.FriendlyName)"
    Write-Output "Status: $($d.Status)"
    Write-Output "Problem: $($d.Problem)"
    Write-Output "InstanceId: $($d.InstanceId)"
    
    $props = @(
        "DEVPKEY_Device_ProblemCode",
        "DEVPKEY_Device_ProblemStatus", 
        "DEVPKEY_Device_DriverVersion",
        "DEVPKEY_Device_DriverInfPath",
        "DEVPKEY_Device_DriverDesc",
        "DEVPKEY_Device_ConfigFlags",
        "DEVPKEY_Device_LocationInfo"
    )
    foreach ($p in $props) {
        $val = (Get-PnpDeviceProperty -InstanceId $d.InstanceId -KeyName $p -ErrorAction SilentlyContinue).Data
        Write-Output "  $p = $val"
    }
}
'''
r1 = subprocess.run(['powershell', '-Command', cmd1], capture_output=True, text=True, timeout=15)
print(r1.stdout)

# 2. Event log — what's the actual error?
print("[2] Recent iGPU Events...\n")
cmd2 = '''
Get-WinEvent -FilterHashtable @{LogName='System'; Level=1,2,3; StartTime=(Get-Date).AddHours(-1)} -MaxEvents 30 -ErrorAction SilentlyContinue | Where-Object { $_.Message -like "*Radeon*" -or $_.Message -like "*1002*" -or $_.Message -like "*display*" -or $_.Message -like "*video*" -or $_.Message -like "*amd*" -or $_.ProviderName -like "*pnp*" } | ForEach-Object {
    Write-Output "[$($_.TimeCreated.ToString('HH:mm:ss'))] $($_.ProviderName): $($_.Message.Substring(0, [Math]::Min($_.Message.Length, 200)))"
    Write-Output ""
}
'''
r2 = subprocess.run(['powershell', '-Command', cmd2], capture_output=True, text=True, timeout=15)
print(r2.stdout if r2.stdout.strip() else "  No relevant events found")

# 3. Try to disable and re-enable
print("[3] Disable → Re-enable cycle...\n")
cmd3 = '''
$dev = Get-PnpDevice | Where-Object { $_.InstanceId -like "*VEN_1002&DEV_13C0*" }
foreach ($d in $dev) {
    Write-Output "Disabling $($d.FriendlyName)..."
    try { Disable-PnpDevice -InstanceId $d.InstanceId -Confirm:$false -ErrorAction Stop; Write-Output "  Disabled" } catch { Write-Output "  Disable: $($_.Exception.Message)" }
    Start-Sleep -Seconds 2
    Write-Output "Re-enabling..."
    try { Enable-PnpDevice -InstanceId $d.InstanceId -Confirm:$false -ErrorAction Stop; Write-Output "  Enabled!" } catch { Write-Output "  Enable: $($_.Exception.Message)" }
    Start-Sleep -Seconds 2
    $d2 = Get-PnpDevice -InstanceId $d.InstanceId
    Write-Output "New status: $($d2.Status)"
}
'''
r3 = subprocess.run(['powershell', '-Command', cmd3], capture_output=True, text=True, timeout=30)
print(r3.stdout)
if r3.stderr: print("ERR:", r3.stderr[:300])

# 4. Check UMA allocation
print("\n[4] Check if iGPU has memory allocated...\n")
cmd4 = '''
Get-CimInstance Win32_VideoController | ForEach-Object {
    Write-Output "$($_.Name)"
    Write-Output "  AdapterRAM: $([math]::Round($_.AdapterRAM / 1MB, 0)) MB"
    Write-Output "  Status: $($_.Status)"
    Write-Output "  Availability: $($_.Availability)"
    Write-Output "  ConfigManagerErrorCode: $($_.ConfigManagerErrorCode)"
}
'''
r4 = subprocess.run(['powershell', '-Command', cmd4], capture_output=True, text=True, timeout=10)
print(r4.stdout)

# 5. Try updating driver from Windows Update
print("[5] Scanning for driver update...\n")
cmd5 = '''
$dev = Get-PnpDevice | Where-Object { $_.InstanceId -like "*VEN_1002&DEV_13C0*" }
foreach ($d in $dev) {
    $hwid = $d.InstanceId
    Write-Output "Attempting driver update for $hwid..."
    $result = pnputil /scan-devices 2>&1
    Write-Output $result
}
'''
r5 = subprocess.run(['powershell', '-Command', cmd5], capture_output=True, text=True, timeout=30)
print(r5.stdout)

print("\nDone!")
