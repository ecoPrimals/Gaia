"""Wake the iGPU for Display 2"""
import subprocess

print("=" * 50)
print("WAKING iGPU FOR DISPLAY 2")
print("=" * 50)

# 1. Check iGPU status
print("\n=== iGPU Current Status ===\n")
cmd1 = '''
$igpu = Get-PnpDevice | Where-Object { $_.InstanceId -like "*VEN_1002&DEV_13C0*" }
foreach ($d in $igpu) {
    Write-Output "Name: $($d.FriendlyName)"
    Write-Output "Status: $($d.Status)"
    Write-Output "Class: $($d.Class)"
    Write-Output "InstanceId: $($d.InstanceId)"
    $prob = (Get-PnpDeviceProperty -InstanceId $d.InstanceId -KeyName DEVPKEY_Device_ProblemCode -ErrorAction SilentlyContinue).Data
    $desc = (Get-PnpDeviceProperty -InstanceId $d.InstanceId -KeyName DEVPKEY_Device_ProblemStatus -ErrorAction SilentlyContinue).Data
    Write-Output "ProblemCode: $prob"
    Write-Output "ProblemStatus: $desc"
    
    $driver = (Get-PnpDeviceProperty -InstanceId $d.InstanceId -KeyName DEVPKEY_Device_DriverVersion -ErrorAction SilentlyContinue).Data
    $inf = (Get-PnpDeviceProperty -InstanceId $d.InstanceId -KeyName DEVPKEY_Device_DriverInfPath -ErrorAction SilentlyContinue).Data
    Write-Output "DriverVersion: $driver"
    Write-Output "DriverInf: $inf"
}
'''
r1 = subprocess.run(['powershell', '-Command', cmd1], capture_output=True, text=True, timeout=15)
print(r1.stdout)

# 2. Try to enable it
print("\n=== Attempting to Enable iGPU ===\n")
cmd2 = '''
$igpu = Get-PnpDevice | Where-Object { $_.InstanceId -like "*VEN_1002&DEV_13C0*" }
foreach ($d in $igpu) {
    if ($d.Status -ne "OK") {
        Write-Output "Enabling $($d.FriendlyName)..."
        try {
            Enable-PnpDevice -InstanceId $d.InstanceId -Confirm:$false -ErrorAction Stop
            Write-Output "  -> Enabled!"
        } catch {
            Write-Output "  -> Enable failed: $($_.Exception.Message)"
        }
    } else {
        Write-Output "$($d.FriendlyName) already OK"
    }
}
'''
r2 = subprocess.run(['powershell', '-Command', cmd2], capture_output=True, text=True, timeout=15)
print(r2.stdout)
if r2.stderr: print("ERR:", r2.stderr[:300])

# 3. Check if there's an AMD display driver available
print("\n=== AMD Driver Check ===\n")
cmd3 = '''
$drivers = Get-WindowsDriver -Online | Where-Object { $_.ProviderName -like "*AMD*" -or $_.ProviderName -like "*Advanced Micro*" }
$drivers | Select-Object Driver, ProviderName, ClassName, Version | Format-Table -AutoSize
'''
r3 = subprocess.run(['powershell', '-Command', cmd3], capture_output=True, text=True, timeout=30)
print(r3.stdout if r3.stdout.strip() else "No AMD drivers found in driver store")
if r3.stderr and 'denied' in r3.stderr.lower():
    print("(Need admin for driver scan)")

# 4. Check BIOS setting for iGPU — NB Configuration
print("\n=== BIOS iGPU hint ===\n")
print("The iGPU needs BIOS: Advanced -> NB Configuration -> Primary Video Device")
print("Options: [IGFX Video] or [PCIE Video]")
print("For DUAL display: set to [PCIE Video] (5090 primary)")
print("The iGPU should auto-enable as secondary IF the driver is loaded")
print()
print("Also check: Advanced -> NB Configuration -> iGPU Multi-Monitor")
print("  -> Set to [Enabled] if available")

# 5. Recheck after enable attempt
print("\n=== Post-enable Status ===\n")
cmd5 = '''
Get-PnpDevice -Class Display | Format-Table FriendlyName, Status, InstanceId -AutoSize -Wrap
'''
r5 = subprocess.run(['powershell', '-Command', cmd5], capture_output=True, text=True, timeout=10)
print(r5.stdout)

# 6. Check all monitors
print("\n=== All Monitors ===\n")
cmd6 = '''
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Screen]::AllScreens | ForEach-Object {
    Write-Output "  $($_.DeviceName) | Primary=$($_.Primary) | $($_.Bounds.Width)x$($_.Bounds.Height)"
}
'''
r6 = subprocess.run(['powershell', '-Command', cmd6], capture_output=True, text=True, timeout=10)
print(r6.stdout)

print("Done!")
