"""Snowglobe — Get Display 2 live + pull KenshiReborn from Forgejo."""
import subprocess, socket, urllib.request, json, os

print("=" * 60)
print("SNOWGLOBE — Kenshi Reborn on Display 2")
print("=" * 60)

# ─── 1: Display status ───
print("\n[1] Current displays...\n")
r1 = subprocess.run(['powershell', '-Command',
    'Add-Type -AssemblyName System.Windows.Forms; $s = [System.Windows.Forms.Screen]::AllScreens; Write-Output "DISPLAYS: $($s.Count)"; foreach ($scr in $s) { Write-Output "  $($scr.DeviceName) $($scr.Bounds.Width)x$($scr.Bounds.Height) Primary=$($scr.Primary)" }'],
    capture_output=True, text=True, timeout=10)
print(r1.stdout.strip())

# Check monitors
r2 = subprocess.run(['powershell', '-Command',
    'Get-PnpDevice -Class Monitor -ErrorAction SilentlyContinue | Format-Table FriendlyName,Status -AutoSize'],
    capture_output=True, text=True, timeout=10)
print(r2.stdout.strip())

# NVIDIA outputs
r3 = subprocess.run(['nvidia-smi', '-q', '-d', 'DISPLAY'], capture_output=True, text=True, timeout=5)
for line in r3.stdout.split('\n'):
    if 'Display' in line or 'Connected' in line or 'Active' in line:
        print(f"  {line.strip()}")

# ─── 2: Try to enable the second display ───
print("\n[2] Attempting to detect/enable Display 2...\n")
# Use displayswitch to extend
r4 = subprocess.run(['displayswitch.exe', '/extend'], capture_output=True, text=True, timeout=5)
print(f"  displayswitch /extend: done")

import time
time.sleep(3)

# Check again
r5 = subprocess.run(['powershell', '-Command',
    'Add-Type -AssemblyName System.Windows.Forms; Write-Output "DISPLAYS NOW: $([System.Windows.Forms.Screen]::AllScreens.Count)"'],
    capture_output=True, text=True, timeout=10)
print(f"  {r5.stdout.strip()}")

# ─── 3: Pull KenshiReborn from Forgejo ───
print("\n[3] KenshiReborn on Forgejo...\n")
try:
    resp = urllib.request.urlopen("http://192.168.4.244:3000/api/v1/repos/esotericWebb/KenshiReborn", timeout=5)
    data = json.loads(resp.read().decode())
    print(f"  Repo: {data.get('full_name')}")
    print(f"  Description: {data.get('description', 'none')}")
    print(f"  Updated: {data.get('updated_at', '?')[:19]}")
    print(f"  Size: {data.get('size', 0)} KB")
    print(f"  Clone: {data.get('clone_url', '?')}")
    print(f"  Stars: {data.get('stars_count', 0)}")
except Exception as e:
    print(f"  Error: {e}")

# Check if already cloned
kenshi_paths = [
    r"C:\Users\mokke\Desktop\KenshiReborn",
    r"C:\Users\mokke\Desktop\Gaia\gardens\KenshiReborn",
    r"C:\Users\mokke\Desktop\kenshi-reborn",
]
for kp in kenshi_paths:
    if os.path.exists(kp):
        print(f"\n  Already cloned at: {kp}")
        # Show structure
        for f in os.listdir(kp)[:15]:
            full = os.path.join(kp, f)
            if os.path.isdir(full):
                print(f"    {f}/")
            else:
                size = os.path.getsize(full)
                print(f"    {f} ({size}B)")
        break
else:
    print("\n  Not cloned locally yet")

# ─── 4: Check for Kenshi game ───
print("\n[4] Kenshi on this machine...\n")
cmd4 = '''
Get-ItemProperty "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*" -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName -like "*Kenshi*" } | Select-Object DisplayName,InstallLocation
Get-ItemProperty "HKLM:\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*" -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName -like "*Kenshi*" } | Select-Object DisplayName,InstallLocation
'''
r6 = subprocess.run(['powershell', '-Command', cmd4], capture_output=True, text=True, timeout=10)
print(r6.stdout.strip() if r6.stdout.strip() else "  Kenshi not in registry")

# Check Steam library
steam_paths = [
    r"C:\Program Files (x86)\Steam\steamapps\common\Kenshi",
    r"D:\Steam\steamapps\common\Kenshi",
    r"E:\Steam\steamapps\common\Kenshi",
    r"D:\SteamLibrary\steamapps\common\Kenshi",
]
for sp in steam_paths:
    if os.path.exists(sp):
        print(f"  Found Kenshi at: {sp}")
        break

# Also search all drives
cmd5 = 'Get-ChildItem -Path C:\\,D:\\,E:\\ -Filter "kenshi*.exe" -Recurse -ErrorAction SilentlyContinue -Depth 4 | Select-Object FullName -First 5'
r7 = subprocess.run(['powershell', '-Command', cmd5], capture_output=True, text=True, timeout=15)
if r7.stdout.strip():
    print(r7.stdout.strip())

# ─── 5: RustDesk status ───
print("\n[5] RustDesk/amoeba...\n")
for port in [21118, 21116, 21117]:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        result = s.connect_ex(("127.0.0.1", port))
        s.close()
        if result == 0:
            print(f"  :{port} OPEN (RustDesk)")
    except:
        pass

# Check for rustdesk process
r8 = subprocess.run(['powershell', '-Command', 
    'Get-Process rustdesk* -ErrorAction SilentlyContinue | Select-Object Name,Id'],
    capture_output=True, text=True, timeout=5)
print(r8.stdout.strip() if r8.stdout.strip() else "  RustDesk not running (need to install/start)")

print("\n" + "=" * 60)
print("SNOWGLOBE: Kenshi world visible through the left eye")
print("RustDesk streams Display 2 → all gates see the snowglobe")
print("=" * 60)
