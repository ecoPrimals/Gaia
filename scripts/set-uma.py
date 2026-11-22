"""SET UMA Frame Buffer Size via ASUS WMI — wake the left eye!"""
import subprocess

print("=== SETTING UMA FRAME BUFFER SIZE ===\n")

# Read current value
cmd_read = '''
$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement
$result = Invoke-CimMethod -InputObject $inst -MethodName "GetOptionData" -Arguments @{ OptionName = "UmaFrameBufferSize" }
Write-Output "Current UmaFrameBufferSize: $($result.Value) (Error=$($result.ErrorCode))"
$result2 = Invoke-CimMethod -InputObject $inst -MethodName "GetOptionData" -Arguments @{ OptionName = "PrimaryVideo" }
Write-Output "Current PrimaryVideo: $($result2.Value) (Error=$($result2.ErrorCode))"
'''
r = subprocess.run(['powershell', '-Command', cmd_read], capture_output=True, text=True, timeout=10)
print(r.stdout)

# Try setting UMA to 512MB
# Value might be: 512 (direct MB), or an index, or hex
attempts = [
    (512, "512 (direct MB value)"),
    (7, "7 (index for 512M in options list)"),
    (0x200, "0x200 (512 in hex)"),
    (256, "256 (try 256MB as fallback)"),
    (5, "5 (index for 256M)"),
]

print("Attempting to set UMA...\n")
for val, desc in attempts:
    cmd_set = f'''
    $inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement
    $result = Invoke-CimMethod -InputObject $inst -MethodName "SetOptionData" -Arguments @{{ OptionName = "UmaFrameBufferSize"; Value = {val} }}
    Write-Output "Set UMA={val} ({desc}): Error=$($result.ErrorCode)"
    '''
    # Fix the desc in the command
    cmd_set_clean = f'''
    $inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement
    $result = Invoke-CimMethod -InputObject $inst -MethodName "SetOptionData" -Arguments @{{ OptionName = "UmaFrameBufferSize"; Value = {val} }}
    Write-Output "Error=$($result.ErrorCode)"
    '''
    r = subprocess.run(['powershell', '-Command', cmd_set_clean], capture_output=True, text=True, timeout=10)
    error = r.stdout.strip()
    print(f"  Set UMA={val} ({desc}): {error}")
    
    # Read back to see if it changed
    r2 = subprocess.run(['powershell', '-Command', '''
    $inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement
    $result = Invoke-CimMethod -InputObject $inst -MethodName "GetOptionData" -Arguments @{ OptionName = "UmaFrameBufferSize" }
    Write-Output "  -> Readback: $($result.Value)"
    '''], capture_output=True, text=True, timeout=10)
    print(r2.stdout.strip())
    
    # If we got error=0 and the value changed, we're done!
    if 'Error=0' in error:
        r3 = subprocess.run(['powershell', '-Command', '''
        $inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement
        $result = Invoke-CimMethod -InputObject $inst -MethodName "GetOptionData" -Arguments @{ OptionName = "UmaFrameBufferSize" }
        $result.Value
        '''], capture_output=True, text=True, timeout=10)
        new_val = r3.stdout.strip()
        if new_val != '4294967295':
            print(f"\n  *** UMA CHANGED! New value: {new_val} ***")
            print(f"  *** REBOOT to apply! The iGPU will get memory! ***")
            break
    print()

print("\nDone!")
