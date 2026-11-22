"""BUBBLE EYE TEST — Simulate left eye inside right eye.
Test the architecture BEFORE the hardware fix.
Sense mobo HDMI signal, render a bubble, test amoeba sharing."""
import subprocess, socket, json, os

print("=" * 60)
print("BUBBLE EYE — Left eye prototype inside right eye")
print("=" * 60)

# ─── 1: Sense the mobo HDMI — is ANYTHING pulsing? ───
print("\n[1] Sensing mobo HDMI signal...")

cmd_hdmi = r'''
# Check EDID on the BasicDisplay-connected LG
$lg_basic = Get-PnpDevice -Class Monitor | Where-Object { 
    $_.Status -eq "Unknown" -and $_.FriendlyName -like "*LG*"
}
foreach ($lg in $lg_basic) {
    $parent = (Get-PnpDeviceProperty -InstanceId $lg.InstanceId -KeyName DEVPKEY_Device_Parent -ErrorAction SilentlyContinue).Data
    $locpath = (Get-PnpDeviceProperty -InstanceId $lg.InstanceId -KeyName DEVPKEY_Device_LocationPaths -ErrorAction SilentlyContinue).Data
    Write-Output ("LG: " + $lg.InstanceId)
    Write-Output ("  Status: " + $lg.Status)
    Write-Output ("  Parent: " + $parent)
    Write-Output ("  Path: " + ($locpath -join " | "))
    
    # Read EDID from registry — this proves DDC/I2C is working
    $regPath = "HKLM:\SYSTEM\CurrentControlSet\Enum\" + $lg.InstanceId + "\Device Parameters"
    $edid = Get-ItemProperty $regPath -Name EDID -ErrorAction SilentlyContinue
    if ($null -ne $edid -and $null -ne $edid.EDID) {
        $edidHex = ($edid.EDID | ForEach-Object { "{0:X2}" -f $_ }) -join " "
        Write-Output ("  EDID: " + $edidHex.Substring(0, [Math]::Min(80, $edidHex.Length)) + "...")
        Write-Output ("  EDID length: " + $edid.EDID.Length + " bytes — DDC ALIVE!")
        
        # Parse manufacturer from EDID bytes 8-9
        $mfg1 = $edid.EDID[8]
        $mfg2 = $edid.EDID[9]
        $c1 = [char](64 + (($mfg1 -shr 2) -band 0x1F))
        $c2 = [char](64 + ((($mfg1 -band 0x03) -shl 3) -bor (($mfg2 -shr 5) -band 0x07)))
        $c3 = [char](64 + ($mfg2 -band 0x1F))
        Write-Output ("  Manufacturer: " + $c1 + $c2 + $c3)
        
        # Resolution from detailed timing (bytes 54+)
        if ($edid.EDID.Length -gt 58) {
            $hActive = $edid.EDID[56] + (($edid.EDID[58] -shr 4) * 256)
            $vActive = $edid.EDID[59] + (($edid.EDID[61] -shr 4) * 256)
            Write-Output ("  Native: " + $hActive + "x" + $vActive)
        }
    } else {
        Write-Output "  EDID: not found"
    }
}

# Compare with the working RTX-connected displays
Write-Output "`n--- RTX 5090 displays (right eye) ---"
$rtx_mons = Get-PnpDevice -Class Monitor | Where-Object { $_.Status -eq "OK" }
foreach ($m in $rtx_mons) {
    $parent = (Get-PnpDeviceProperty -InstanceId $m.InstanceId -KeyName DEVPKEY_Device_Parent -ErrorAction SilentlyContinue).Data
    Write-Output ($m.FriendlyName + " Status=" + $m.Status + " Parent=" + $parent)
}
'''

with open(r'c:\Users\mokke\Desktop\Gaia\scripts\sense-hdmi.ps1', 'w') as f:
    f.write(cmd_hdmi)

r1 = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File',
                     r'c:\Users\mokke\Desktop\Gaia\scripts\sense-hdmi.ps1'],
                    capture_output=True, text=True, timeout=15)
print(r1.stdout.strip())

# ─── 2: Check what rendering tools are available ───
print("\n\n[2] Rendering tools available...")

tools = {
    "Blender": [r"C:\Program Files\Blender Foundation", r"C:\Program Files (x86)\Steam\steamapps\common\Blender"],
    "KenshiReborn": [r"C:\Users\mokke\Desktop\KenshiReborn"],
    "Kenshi": [r"M:\SteamLibrary\steamapps\common\Kenshi"],
    "Steam": [r"C:\Program Files (x86)\Steam"],
}

for name, paths in tools.items():
    found = False
    for p in paths:
        if os.path.exists(p):
            print(f"  {name}: FOUND at {p}")
            found = True
            break
    if not found:
        # Check via where
        r = subprocess.run(['where', name.lower()], capture_output=True, text=True, timeout=3)
        if r.returncode == 0:
            print(f"  {name}: {r.stdout.strip()}")
        else:
            print(f"  {name}: not found")

# Check if Blender is installed via Steam
r_blender = subprocess.run(['powershell', '-Command', 
    'Get-ChildItem "C:\\Program Files*" -Filter blender.exe -Recurse -Depth 3 -ErrorAction SilentlyContinue | Select-Object -First 1 FullName'],
    capture_output=True, text=True, timeout=10)
if r_blender.stdout.strip():
    print(f"  Blender exe: {r_blender.stdout.strip()}")

# ─── 3: Virtual display / bubble approach ───
print("\n[3] Virtual left eye bubble approaches...")
print("""
  APPROACH A: RustDesk "virtual display"
    - RustDesk can create a virtual monitor
    - Renders at specified resolution  
    - Other gates connect and see it
    - No physical display needed!

  APPROACH B: OBS/NDI window capture
    - Capture a specific window (Kenshi/Blender)
    - Stream as virtual camera / NDI
    - Other gates view the stream

  APPROACH C: Windows virtual display driver
    - Add-Type virtual display adapter
    - Windows sees it as Display 2
    - RustDesk captures it
    - Content rendered by RTX but shown as "left eye"

  APPROACH D: Steam Remote Play
    - deckGate streams from northGate
    - Right eye renders both
    - Deck sees the "left eye" content via Steam
""")

# ─── 4: Check if RustDesk has virtual display support ───
print("[4] RustDesk virtual display check...")
rd_path = r"C:\Program Files\RustDesk"
if not os.path.exists(rd_path):
    rd_path = os.path.expanduser(r"~\AppData\Local\RustDesk")

# Check RustDesk version
r_ver = subprocess.run(['powershell', '-Command',
    'Get-ItemProperty "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\RustDesk" -ErrorAction SilentlyContinue | Select-Object DisplayVersion,InstallLocation'],
    capture_output=True, text=True, timeout=5)
print(f"  {r_ver.stdout.strip()}")

# Check for virtual display plugin
r_vd = subprocess.run(['powershell', '-Command',
    'Get-ChildItem "C:\\Program Files\\RustDesk" -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.Name -like "*virtual*" -or $_.Name -like "*idd*" } | Select-Object FullName'],
    capture_output=True, text=True, timeout=5)
if r_vd.stdout.strip():
    print(f"  Virtual display driver: {r_vd.stdout.strip()}")
else:
    print("  No virtual display driver found in RustDesk")

# ─── 5: Test Steam streaming to Deck as bubble ───
print("\n[5] Steam → Deck bubble test...")
for port in [27036, 27037]:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.3)
    ok = s.connect_ex(("192.168.4.176", port)) == 0
    s.close()
    print(f"  deckGate:{port} {'OPEN' if ok else 'closed'}")

# Local Steam
r_steam = subprocess.run(['powershell', '-Command',
    'Get-Process steam -ErrorAction SilentlyContinue | Select-Object Name,Id'],
    capture_output=True, text=True, timeout=3)
print(f"  Steam local: {r_steam.stdout.strip()}")

print("\n" + "=" * 60)
print("REBOOT 2 PLAN: EXPERIMENT (no BIOS touch)")
print()
print("  1. Sense mobo HDMI — EDID proves wire is live")
print("  2. Create virtual left eye bubble on right eye")
print("  3. Render content (Kenshi/Blender) into bubble")
print("  4. Test amoeba sharing of bubble")
print("  5. Deck looks through bubble (right eye → left eye)")
print()
print("  Reboot 3: Kevin flips CSM → real left eye opens")
print("  The bubble becomes the real display")
print("=" * 60)
