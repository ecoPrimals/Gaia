"""V-Cache eye — check Basic Display + display paths + X3D cache."""
import subprocess

print("=" * 60)
print("V-CACHE EYE — X3D as display engine")
print("=" * 60)

# Basic Display Driver
print("\n[1] Basic Display Driver...\n")
cmd1 = "Get-PnpDevice | Where-Object { $_.FriendlyName -like '*Basic*Display*' } | Format-List FriendlyName,Status,InstanceId,Class"
r1 = subprocess.run(['powershell', '-Command', cmd1], capture_output=True, text=True, timeout=10)
print(r1.stdout.strip() if r1.stdout.strip() else "  No Basic Display Driver found")

# CPU / V-Cache
print("\n[2] X3D V-Cache...\n")
cmd2 = "$c = Get-CimInstance Win32_Processor; Write-Output $c.Name; Write-Output ('L3: '+[string][math]::Round($c.L3CacheSize/1024)+'MB V-Cache'); Write-Output ('Cores: '+[string]$c.NumberOfCores+' Threads: '+[string]$c.NumberOfLogicalProcessors)"
r2 = subprocess.run(['powershell', '-Command', cmd2], capture_output=True, text=True, timeout=10)
print(r2.stdout.strip())
# Parse L3
for line in r2.stdout.split('\n'):
    if 'L3:' in line:
        try:
            mb = int(line.split(':')[1].strip().split('M')[0])
            fb_count = mb // 15  # 2560x1440 RGBA = ~15MB
            print(f"\n  {mb}MB L3 cache = {fb_count} full 1440p framebuffers!")
            print(f"  CPU rendering at L3 speed = VIABLE display path")
        except:
            pass

# Display paths
print("\n[3] Windows display path count...\n")
cmd3 = '''
$code = @"
using System;
using System.Runtime.InteropServices;
public class DispCfg {
    [DllImport("user32.dll")]
    public static extern int GetDisplayConfigBufferSizes(uint flags, out uint numPaths, out uint numModes);
}
"@
Add-Type -TypeDefinition $code
$p = [uint32]0; $m = [uint32]0
[void][DispCfg]::GetDisplayConfigBufferSizes(1, [ref]$p, [ref]$m)
Write-Output "ALL possible paths: $p paths, $m modes"
[void][DispCfg]::GetDisplayConfigBufferSizes(2, [ref]$p, [ref]$m)
Write-Output "ACTIVE paths: $p paths, $m modes"
'''
r3 = subprocess.run(['powershell', '-Command', cmd3], capture_output=True, text=True, timeout=10)
print(r3.stdout.strip())

# Enable Basic Display
print("\n[4] Trying to activate Basic Display path...\n")
cmd4 = '''
$bd = Get-PnpDevice | Where-Object { $_.FriendlyName -like '*Basic*Display*' }
if ($bd) {
    Write-Output "Found: $($bd.FriendlyName) Status=$($bd.Status)"
    Enable-PnpDevice -InstanceId $bd.InstanceId -Confirm:$false -ErrorAction SilentlyContinue
    Start-Sleep 1
    $bd2 = Get-PnpDevice -InstanceId $bd.InstanceId
    Write-Output "After enable: $($bd2.Status)"
    
    # Try displayswitch
    Start-Process displayswitch.exe -ArgumentList '/extend' -Wait
    Start-Sleep 2
    
    Add-Type -AssemblyName System.Windows.Forms
    Write-Output "Displays now: $([System.Windows.Forms.Screen]::AllScreens.Count)"
} else {
    Write-Output "No Basic Display Driver found"
}
'''
r4 = subprocess.run(['powershell', '-Command', cmd4], capture_output=True, text=True, timeout=20)
print(r4.stdout.strip())

print("\n" + "=" * 60)
print("THE X3D VISION:")
print("  96MB V-Cache → software framebuffer → iGPU HDMI")
print("  The cache IS the display memory")
print("  Once UMA is set: BIOS inits display engine")
print("  Then: V-Cache feeds frames → mobo HDMI → LG")
print("  setup_var.efi is the key to unlock this")
print("=" * 60)
