"""Probe ASUS WMI to read/set BIOS settings"""
import subprocess

print("=== ASUS WMI BIOS PROBE ===\n")

# 1. Enumerate ASUSManagement methods
print("[1] ASUSManagement WMI methods...\n")
cmd1 = '''
$cls = Get-CimClass -Namespace root/WMI -ClassName ASUSManagement -ErrorAction SilentlyContinue
if ($cls) {
    Write-Output "Properties:"
    $cls.CimClassProperties | ForEach-Object { Write-Output "  $($_.Name) ($($_.CimType))" }
    Write-Output "`nMethods:"
    $cls.CimClassMethods | ForEach-Object { 
        Write-Output "  $($_.Name)"
        $_.Parameters | ForEach-Object { Write-Output "    param: $($_.Name) ($($_.CimType))" }
    }
}
'''
r1 = subprocess.run(['powershell', '-Command', cmd1], capture_output=True, text=True, timeout=15)
print(r1.stdout)

# 2. Try all ASUS WMI classes  
print("[2] All ASUS-related WMI classes...\n")
cmd2 = '''
Get-CimClass -Namespace root/WMI -ErrorAction SilentlyContinue | Where-Object { $_.CimClassName -like "*ASUS*" -or $_.CimClassName -like "*Asus*" -or $_.CimClassName -like "*ROG*" } | ForEach-Object {
    Write-Output "$($_.CimClassName)"
    $_.CimClassMethods | ForEach-Object { Write-Output "  method: $($_.Name)" }
}
'''
r2 = subprocess.run(['powershell', '-Command', cmd2], capture_output=True, text=True, timeout=15)
print(r2.stdout)

# 3. Try to read BIOS settings via ASUS ACPI/WMI
print("[3] Try reading BIOS config...\n")
cmd3 = '''
# Method 1: ASUSManagement
try {
    $mgmt = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement -ErrorAction Stop
    $mgmt | Get-Member -MemberType Method | ForEach-Object {
        Write-Output "Method available: $($_.Name)"
    }
} catch {
    Write-Output "  ASUSManagement: $($_.Exception.Message)"
}

# Method 2: Check for ASUS BIOS config tool
$asusPaths = @(
    "C:\Program Files\ASUS\ArmouryCrate",
    "C:\Program Files (x86)\ASUS\ArmouryCrate",
    "C:\Program Files\ASUS\AsusBiosConfig",
    "${env:ProgramFiles}\ASUS"
)
foreach ($p in $asusPaths) {
    if (Test-Path $p) { Write-Output "ASUS software: $p" }
}

# Method 3: WMI BIOS query
try {
    $bios = Get-CimInstance -Namespace root/WMI -ClassName AsusMbSwInterface -ErrorAction Stop
    Write-Output "AsusMbSwInterface found!"
    $bios | Format-List | Out-String | Write-Output
} catch {}

# Method 4: Direct WMI method call
try {
    $inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement
    # Try to call GetDeviceStatus or similar
    $result = Invoke-CimMethod -InputObject $inst -MethodName "device_status" -ErrorAction SilentlyContinue
    Write-Output "device_status: $($result | Out-String)"
} catch {
    Write-Output "  Method call: $($_.Exception.Message)"
}
'''
r3 = subprocess.run(['powershell', '-Command', cmd3], capture_output=True, text=True, timeout=15)
print(r3.stdout)

# 4. Check if we can use setupapi to force-enumerate the iGPU
print("[4] Searching for iGPU on bus 123...\n")
cmd4 = '''
# List everything at bus 123 with all details
pnputil /enum-devices /bus PCI /location | Select-String -Pattern "123" -Context 3,3
'''
r4 = subprocess.run(['powershell', '-Command', cmd4], capture_output=True, text=True, timeout=15)
print(r4.stdout[:2000])

print("\nDone!")
