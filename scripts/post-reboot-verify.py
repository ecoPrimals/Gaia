
"""POST-REBOOT VERIFY — Check if left eye opened."""
import subprocess, socket

print("=" * 50)
print("POST-REBOOT — Did the left eye open?")
print("=" * 50)

# Check UMA
cmd = 'powershell -Command "$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement; $r = Invoke-CimMethod -InputObject $inst -MethodName GetOptionData -Arguments @{OptionName=\'UmaFrameBufferSize\'}; Write-Output $r.Value"'
import os
r = os.popen(cmd).read().strip()
uma = int(r) if r.isdigit() else -1
if uma == 4294967295:
    print("  UMA: STILL 0xFFFFFFFF (not set) :(")
elif uma > 0:
    print(f"  UMA: {uma} ({uma/1024/1024:.0f}MB) — SET!")
else:
    print(f"  UMA: {r}")

# Check CSM
cmd2 = 'powershell -Command "$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement; $r = Invoke-CimMethod -InputObject $inst -MethodName GetOptionData -Arguments @{OptionName=\'CsmSupport\'}; Write-Output $r.Value"'
csm = os.popen(cmd2).read().strip()
print(f"  CSM: {csm} ({'ENABLED (bad)' if csm == '1' else 'DISABLED (good!)'})")

# Check AMD GPU
cmd3 = 'powershell -Command "Get-PnpDevice -Class Display | Format-Table FriendlyName,Status -AutoSize"'
gpus = os.popen(cmd3).read()
print(f"\n  GPUs:\n{gpus}")

# Check monitors
cmd4 = 'powershell -Command "Get-PnpDevice -Class Monitor | Format-Table FriendlyName,Status -AutoSize"'
mons = os.popen(cmd4).read()
print(f"  Monitors:\n{mons}")

print("=" * 50)
if uma != 4294967295 and csm != '1':
    print("LEFT EYE SHOULD BE OPEN! Check Display 2!")
else:
    print("Left eye still blocked. Next reboot.")
print("=" * 50)
