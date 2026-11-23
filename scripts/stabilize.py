"""Stabilize check — get back to pre-surgery face"""
import subprocess

print("=" * 50)
print("STABILIZATION CHECK — Pre-surgery face")
print("=" * 50)

# 1. Displays
print("\n=== Monitors Connected ===\n")
cmd = '''
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Screen]::AllScreens | ForEach-Object {
    Write-Output "Display: $($_.DeviceName) | Primary=$($_.Primary) | $($_.Bounds.Width)x$($_.Bounds.Height)"
}
'''
r = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, timeout=10)
print(r.stdout)

# 2. GPU adapters
print("=== Display Adapters ===\n")
cmd2 = 'Get-PnpDevice -Class Display | Format-Table FriendlyName, Status -AutoSize'
r2 = subprocess.run(['powershell', '-Command', cmd2], capture_output=True, text=True, timeout=10)
print(r2.stdout)

# 3. nvidia-smi
print("=== NVIDIA Status ===\n")
r3 = subprocess.run([
    'nvidia-smi', 
    '--query-gpu=name,pci.bus_id,pcie.link.gen.current,pcie.link.width.current,display_mode,display_active,temperature.gpu,power.draw',
    '--format=csv'
], capture_output=True, text=True, timeout=10)
print(r3.stdout)

# 4. Network adapters
print("=== Network (UP) ===\n")
cmd4 = 'Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | Select-Object Name, InterfaceDescription, LinkSpeed | Format-Table -AutoSize'
r4 = subprocess.run(['powershell', '-Command', cmd4], capture_output=True, text=True, timeout=10)
print(r4.stdout)

# 5. Connectivity
print("=== Connectivity ===\n")
for target, name in [('192.168.4.1', 'Gateway'), ('192.168.4.244', 'eastGate'), ('8.8.8.8', 'Internet')]:
    r = subprocess.run(['ping', '-n', '1', '-w', '2000', target], capture_output=True, text=True, timeout=5)
    status = 'OK' if r.returncode == 0 else 'FAIL'
    print(f"  {name} ({target}): {status}")

# 6. Resolution and refresh
print("\n=== Display Config ===\n")
cmd6 = '''
Get-CimInstance -ClassName Win32_VideoController | ForEach-Object {
    Write-Output "$($_.Name): $($_.CurrentHorizontalResolution)x$($_.CurrentVerticalResolution) @ $($_.CurrentRefreshRate)Hz | Status=$($_.Status)"
}
'''
r6 = subprocess.run(['powershell', '-Command', cmd6], capture_output=True, text=True, timeout=10)
print(r6.stdout)

# 7. biomeOS primals — are any alive?
print("=== biomeOS Primals ===\n")
cmd7 = '''
Get-Process | Where-Object { $_.ProcessName -match "biomeOS|nestGate|squirrel|barracuda|sweetGrass|bearDog|toadStool|songBird|skunkBat|dromedary|petalTongue|rhizoCrypt|loamSpine|bingoCube|sourDough|swarmVine|coralReef|neuralAPI" } | Select-Object ProcessName, Id, CPU | Format-Table -AutoSize
'''
r7 = subprocess.run(['powershell', '-Command', cmd7], capture_output=True, text=True, timeout=10)
print(r7.stdout if r7.stdout.strip() else "  No primals running (clean slate)")

print("\n=== Summary ===")
print("Goal: match pre-surgery state")
print("  Display: check above")
print("  Network: check above") 
print("  PCIe: Gen2 x8 (improved! BIOS GEN 5 force needed)")
print("  AKD1000: next reboot reseat")
print("  Primals: restart after stable")
