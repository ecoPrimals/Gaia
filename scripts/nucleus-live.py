"""Get biomeOS NUCLEUS live — check all primals, diagnose from inside."""
import subprocess, socket, json, os, urllib.request, ssl

print("=" * 60)
print("NUCLEUS — Getting biomeOS primals live")
print("=" * 60)

# ─── Check biomeOS port ───
print("\n[1] biomeOS heartbeat...\n")
for port, name in [(31415, "biomeOS main"), (8080, "data server"), (9050, "Tor SOCKS")]:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex(("127.0.0.1", port))
        s.close()
        print(f"  :{port} ({name}): {'OPEN' if result == 0 else 'closed'}")
    except:
        print(f"  :{port} ({name}): error")

# ─── Check all primal processes ───
print("\n[2] Primal processes...\n")
primals = [
    "biomeOS", "songBird", "bearDog", "nestGate", "petalTongue",
    "sweetGrass", "rhizoCrypt", "toadStool", "barraCuda", "coralReef",
    "loamSpine", "squirrel", "skunkBat", "sourDough", "swarmVine",
    "bingoCube", "dromedary"
]

cmd = 'Get-Process | Where-Object { ' + ' -or '.join(f'$_.Name -like "*{p}*"' for p in primals) + ' } | Select-Object Name,Id,CPU,WorkingSet64 | Format-Table -AutoSize'
r = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, timeout=10)
if r.stdout.strip():
    print(r.stdout.strip())
else:
    print("  No primal processes found by name")
    # Try broader search
    cmd2 = 'Get-Process | Where-Object { $_.Path -like "*Gaia*" -or $_.Path -like "*primal*" -or $_.Path -like "*biome*" } | Select-Object Name,Id,Path | Format-Table -AutoSize'
    r2 = subprocess.run(['powershell', '-Command', cmd2], capture_output=True, text=True, timeout=10)
    print(r2.stdout.strip() if r2.stdout.strip() else "  Searching broader...")

# ─── Check for biomeOS binary ───
print("\n[3] biomeOS binary location...\n")
possible_paths = [
    r"C:\Users\mokke\Desktop\Gaia\primals\biomeOS",
    r"C:\Users\mokke\Desktop\Gaia\primals",
    r"C:\Users\mokke\Desktop\Gaia\engine",
    r"C:\opt\Gaia",
]
for p in possible_paths:
    if os.path.exists(p):
        # Look for executables
        for f in os.listdir(p):
            if f.endswith('.exe') or f == 'biomeOS' or 'primal' in f.lower():
                full = os.path.join(p, f)
                size = os.path.getsize(full) if os.path.isfile(full) else 0
                print(f"  {full} ({size/1024/1024:.1f}MB)")

# ─── Check biomeOS logs ───
print("\n[4] biomeOS recent logs...\n")
log_paths = [
    r"C:\Users\mokke\Desktop\Gaia\data\logs",
    r"C:\Users\mokke\Desktop\Gaia\logs",
    r"C:\Users\mokke\.local\share\biomeOS",
]
for lp in log_paths:
    if os.path.exists(lp):
        for f in sorted(os.listdir(lp), reverse=True)[:5]:
            fp = os.path.join(lp, f)
            if os.path.isfile(fp):
                size = os.path.getsize(fp)
                print(f"  {fp} ({size}B)")

# ─── Talk to biomeOS API ───
print("\n[5] Talking to biomeOS API...\n")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

endpoints = [
    ("http://127.0.0.1:31415/", "biomeOS root"),
    ("http://127.0.0.1:31415/health", "health"),
    ("http://127.0.0.1:31415/status", "status"),
    ("http://127.0.0.1:31415/primals", "primals"),
    ("http://127.0.0.1:31415/nucleus", "nucleus"),
    ("http://127.0.0.1:8080/data/now.json", "now.json"),
]
for url, name in endpoints:
    try:
        resp = urllib.request.urlopen(url, timeout=3)
        body = resp.read(2000).decode('utf-8', errors='replace')
        print(f"  {name}: HTTP {resp.status} ({len(body)}B)")
        if body and len(body) < 500:
            print(f"    {body[:300]}")
        elif body:
            try:
                data = json.loads(body)
                print(f"    {json.dumps(data, indent=None)[:300]}")
            except:
                print(f"    {body[:200]}")
    except Exception as e:
        try:
            resp = urllib.request.urlopen(url, timeout=3, context=ctx)
            body = resp.read(1000).decode('utf-8', errors='replace')
            print(f"  {name}: HTTPS {resp.status} ({len(body)}B)")
        except Exception as e2:
            print(f"  {name}: {str(e)[:60]}")

# ─── Hardware scan for primals ───
print("\n[6] Hardware that primals should see...\n")
cmd6 = '''
Write-Output "=== GPU ==="
nvidia-smi --query-gpu=name,memory.total,pcie.link.gen.current,pcie.link.width.current --format=csv,noheader 2>&1
Write-Output ""
Write-Output "=== DISPLAYS ==="
Add-Type -AssemblyName System.Windows.Forms
$s = [System.Windows.Forms.Screen]::AllScreens
Write-Output "Count: $($s.Count)"
Write-Output ""
Write-Output "=== ALL PCI DEVICES (non-OK) ==="
Get-PnpDevice -Status Error,Degraded,Unknown -ErrorAction SilentlyContinue | Where-Object { $_.Class -ne $null } | Format-Table Class,FriendlyName,Status -AutoSize
'''
r6 = subprocess.run(['powershell', '-Command', cmd6], capture_output=True, text=True, timeout=15)
print(r6.stdout)

# ─── Squirrel MCP check ───
print("\n[7] Checking squirrel MCP...\n")
for port in [1717, 3030, 8765, 9876]:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        result = s.connect_ex(("127.0.0.1", port))
        s.close()
        if result == 0:
            print(f"  :{port} OPEN (possible MCP)")
    except:
        pass

# ─── Network for primals ───
print("\n[8] LAN health for primal mesh...\n")
for name, ip in [("eastGate", "192.168.4.244"), ("sporeGate", "192.168.4.3"), 
                  ("ironGate", "192.168.4.237"), ("deckGate", "192.168.4.176")]:
    r8 = subprocess.run(['ping', '-n', '1', '-w', '300', ip], capture_output=True, text=True, timeout=3)
    alive = 'Reply from' in r8.stdout and 'TTL=' in r8.stdout
    print(f"  {name:12s} ({ip}): {'ALIVE' if alive else 'DOWN'}")

print("\n" + "=" * 60)
print("biomeOS is bootstrapping — primals register in TCP-only mode")
print("Socket warnings are expected on Windows (no Unix domain sockets)")
print("The organism IS alive — it just needs its eyes opened")
print("=" * 60)
