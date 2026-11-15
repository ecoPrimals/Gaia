"""Deep look — SSL-aware probing + Tor status + cross-LAN routing."""
import urllib.request, ssl, json, socket, subprocess

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

print("=" * 60)
print("DEEP LOOK — Feeling through the organism")
print("=" * 60)

# ─── eastGate data (skip SSL) ───
print("\n[1] eastGate data server (skip SSL)...\n")
try:
    resp = urllib.request.urlopen("https://192.168.4.244:8080/data/now.json", timeout=5, context=ctx)
    body = resp.read(2000).decode('utf-8', errors='replace')
    try:
        data = json.loads(body)
        print(json.dumps(data, indent=2)[:800])
    except:
        print(body[:500])
except Exception as e:
    # Try HTTP
    try:
        resp = urllib.request.urlopen("http://192.168.4.244:8080/data/now.json", timeout=5)
        print(resp.read(500).decode())
    except Exception as e2:
        print(f"  HTTPS: {e}")
        print(f"  HTTP: {e2}")

# ─── RSS feed ───
print("\n[2] RSS feed (skip SSL)...\n")
try:
    resp = urllib.request.urlopen("https://192.168.4.244:8080/data/feed.xml", timeout=5, context=ctx)
    body = resp.read(3000).decode('utf-8', errors='replace')
    for line in body.split('\n')[:15]:
        print(f"  {line.rstrip()}")
    item_count = body.count('<item>')
    print(f"\n  ({item_count}+ items visible)")
except Exception as e:
    print(f"  ❌ {e}")

# ─── gate pulse ───
print("\n[3] Gate pulse :8443...\n")
try:
    resp = urllib.request.urlopen("http://192.168.4.244:8443/pulse", timeout=5)
    print(resp.read(500).decode('utf-8', errors='replace')[:300])
except Exception as e:
    try:
        resp = urllib.request.urlopen("https://192.168.4.244:8443/pulse", timeout=5, context=ctx)
        print(resp.read(500).decode('utf-8', errors='replace')[:300])
    except Exception as e2:
        print(f"  HTTP: {e}")
        print(f"  HTTPS: {e2}")

# ─── Cross-LAN routing ───
print("\n[4] Cross-LAN routing diagnosis...\n")
# Check if we have a route to 192.168.9.0/24
r = subprocess.run(['powershell', '-Command', 'Get-NetRoute -DestinationPrefix 192.168.9.0/24 -ErrorAction SilentlyContinue | Format-Table DestinationPrefix,NextHop,InterfaceAlias,RouteMetric -AutoSize'], capture_output=True, text=True, timeout=5)
if r.stdout.strip():
    print(f"  Route to LAN2: {r.stdout.strip()}")
else:
    print("  No specific route to 192.168.9.0/24!")
    # Check default gateway
    r2 = subprocess.run(['powershell', '-Command', 'Get-NetRoute -DestinationPrefix 0.0.0.0/0 | Format-Table DestinationPrefix,NextHop,InterfaceAlias -AutoSize'], capture_output=True, text=True, timeout=5)
    print(f"  Default routes:\n{r2.stdout.strip()}")
    
    # Try tracert to LAN2
    print("\n  Traceroute to LAN2 (192.168.9.1):")
    r3 = subprocess.run(['tracert', '-d', '-h', '3', '-w', '500', '192.168.9.1'], capture_output=True, text=True, timeout=10)
    for line in r3.stdout.strip().split('\n')[:6]:
        print(f"    {line}")

# ─── Tor hidden service ───
print("\n[5] Tor hidden service...\n")
for port in [9050, 9051]:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex(("192.168.4.244", port))
        s.close()
        print(f"  eastGate port {port}: {'OPEN' if result == 0 else 'closed'}")
    except:
        print(f"  eastGate port {port}: unreachable")

# Can we reach the onion through tor SOCKS?
print("\n  Checking Tor SOCKS proxy...")
for ip in ["192.168.4.244", "127.0.0.1"]:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex((ip, 9050))
        s.close()
        if result == 0:
            print(f"  Tor SOCKS at {ip}:9050 = OPEN")
    except:
        pass

# ─── eastGate ollama ───
print("\n[6] Ollama endpoints...\n")
for name, url in [
    ("eastGate :11436", "http://192.168.4.244:11436/"),
    ("ironGate :11434", "http://192.168.4.237:11434/api/tags"),
]:
    try:
        resp = urllib.request.urlopen(url, timeout=3)
        body = resp.read(500).decode('utf-8', errors='replace')
        print(f"  ✅ {name}: {body[:120]}")
    except Exception as e:
        print(f"  ❌ {name}: {str(e)[:60]}")

# ─── Forgejo check ───
print("\n[7] Forgejo repos...\n")
try:
    resp = urllib.request.urlopen("http://192.168.4.244:3000/api/v1/repos/search?limit=5", timeout=5)
    body = json.loads(resp.read().decode())
    if 'data' in body:
        for repo in body['data'][:5]:
            print(f"  {repo.get('full_name', '?'):40s} {repo.get('updated_at', '?')[:10]}")
except Exception as e:
    print(f"  ❌ {e}")

print("\n" + "=" * 60)
