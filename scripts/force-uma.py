"""Force UMA Frame Buffer — try every path to wake the iGPU"""
import subprocess, ctypes

print("=== FORCING THE LEFT EYE OPEN ===\n")

# 1. Check if ASUS WMI exposes BIOS settings
print("[1] ASUS WMI BIOS Interface...\n")
cmd1 = '''
$wmiClasses = @(
    "root/WMI:ASUSHW",
    "root/WMI:ASUSManagement", 
    "root/WMI:ASUS_ACPI",
    "root/CIMV2:Win32_SystemBIOS"
)
foreach ($cls in $wmiClasses) {
    $parts = $cls -split ":"
    try {
        $instances = Get-CimInstance -Namespace $parts[0] -ClassName $parts[1] -ErrorAction Stop
        Write-Output "FOUND: $cls"
        $instances | Format-List | Out-String | Write-Output
    } catch {
        Write-Output "  $cls - not found"
    }
}

# Try ASUS ATK
try {
    $atk = Get-CimInstance -Namespace root/WMI -ClassName AsusAtkWmi_WMNB -ErrorAction Stop
    Write-Output "ASUS ATK WMI found!"
    $atk | Format-List | Out-String | Write-Output
} catch {
    Write-Output "  No ASUS ATK WMI"
}
'''
r1 = subprocess.run(['powershell', '-Command', cmd1], capture_output=True, text=True, timeout=15)
print(r1.stdout)

# 2. Check UEFI variables for iGPU/UMA settings
print("[2] UEFI Variable scan for iGPU/UMA...\n")
cmd2 = '''
try {
    $privilege = [System.Security.Principal.WindowsPrincipal][System.Security.Principal.WindowsIdentity]::GetCurrent()
    $admin = $privilege.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)
    Write-Output "Running as admin: $admin"
} catch {}

# Try to enumerate firmware environment variables
$sig = @"
[DllImport("kernel32.dll", SetLastError=true)]
public static extern uint GetFirmwareEnvironmentVariableEx(
    string lpName,
    string lpGuid,
    byte[] pBuffer,
    uint nSize,
    out uint pdwAttribubable);
"@
try {
    Add-Type -MemberDefinition $sig -Name FirmwareEnv -Namespace Win32
    Write-Output "Firmware API loaded"
    
    # Try to read common UEFI iGPU variables
    $guids = @(
        "{4570b7f1-ade8-4943-8dc3-406472842f0d}",
        "{ec87d643-eba4-4bb5-a1e5-3f3e36b20da9}",
        "{a1aff049-fdeb-11d3-b171-00a0c9062802}"
    )
    $names = @("Setup", "PlatformSetup", "IntelSetup", "AMDSetup", "AmdSetup", "UMASize", "IGDConfig")
    foreach ($g in $guids) {
        foreach ($n in $names) {
            $buf = New-Object byte[] 4096
            $attr = [uint32]0
            try {
                $size = [Win32.FirmwareEnv]::GetFirmwareEnvironmentVariableEx($n, $g, $buf, 4096, [ref]$attr)
                if ($size -gt 0) {
                    Write-Output "FOUND: $n in $g ($size bytes, attr=$attr)"
                }
            } catch {}
        }
    }
} catch {
    Write-Output "  Firmware API: $($_.Exception.Message)"
}
'''
r2 = subprocess.run(['powershell', '-Command', cmd2], capture_output=True, text=True, timeout=15)
print(r2.stdout)

# 3. Check for AMD Software / Adrenalin
print("[3] AMD Software check...\n")
import os, glob
amd_paths = [
    r"C:\Program Files\AMD\CNext\CNext\amdow.exe",
    r"C:\Program Files\AMD\CNext\CNext\RadeonSoftware.exe",
    r"C:\Windows\System32\atioglxx.dll",
    r"C:\Windows\System32\drivers\atikmdag.sys",
    r"C:\Windows\System32\drivers\amdkmdap.sys",
]
for p in amd_paths:
    exists = os.path.exists(p)
    size = os.path.getsize(p) if exists else 0
    print(f"  {'YES' if exists else 'NO ':3} {p} ({size//1024}KB)" if exists else f"  NO  {p}")

# 4. Check driver store for AMD display driver
print("\n[4] AMD Display driver in store...\n")
cmd4 = 'pnputil /enum-drivers /class Display'
r4 = subprocess.run(['powershell', '-Command', cmd4], capture_output=True, text=True, timeout=15)
print(r4.stdout)

# 5. Try to force-install the AMD driver on the PCI device
print("[5] Force-install AMD driver on bus 123 device...\n")
# The PCI Device at bus 123 func 0 (1022:14DE) - this might be the iGPU endpoint
cmd5 = '''
# Check what 14DE actually is
Write-Output "Device 1022:14DE at bus 123:"
$dev = Get-PnpDevice | Where-Object { $_.InstanceId -like "*VEN_1022&DEV_14DE*" }
foreach ($d in $dev) {
    Write-Output "  Name: $($d.FriendlyName)"
    Write-Output "  Status: $($d.Status)"
    Write-Output "  Class: $($d.Class)"
    $hwids = (Get-PnpDeviceProperty -InstanceId $d.InstanceId -KeyName DEVPKEY_Device_HardwareIds -ErrorAction SilentlyContinue).Data
    Write-Output "  HardwareIds: $($hwids -join ', ')"
}
'''
r5 = subprocess.run(['powershell', '-Command', cmd5], capture_output=True, text=True, timeout=15)
print(r5.stdout)

print("\nDone!")
