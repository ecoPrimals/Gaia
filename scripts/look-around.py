"""Look around — sense what's reachable from northGate across both LANs."""
import subprocess, json, socket, urllib.request, ssl

print("=" * 60)
print("LOOKING AROUND — What can northGate feel?")
print("=" * 60)

# ─── Ping sweep ───
print("\n[1] Pinging all gates...\n")
gates = {
    "eastGate (.244)": "192.168.4.244",
    "sporeGate (.3)": "192.168.4.3",
    "ironGate (.237)": "192.168.4.237",
    "graftGate (.107)": "192.168.4.107",
    "blueGate (.100)": "192.168.4.100",
    "router (.1)": "192.168.4.1",
    "deckGate (.176)": "192.168.4.176",
    "grapheneGate (.9.217)": "192.168.9.217",
    "LAN2 router (.9.1)": "192.168.9.1",
    "frameGate (.9.203)": "192.168.9.203",
    "JetStream (.111)": "192.168.4.111",
}

for name, ip in gates.items():
    r = subprocess.run(['ping', '-n', '1', '-w', '300', ip], capture_output=True, text=True, timeout=3)
    alive = 'Reply from' in r.stdout and 'TTL=' in r.stdout
    ms = ""
    if alive:
        for part in r.stdout.split():
            if 'time' in part.lower() and '=' in part:
                ms = part
    status = f"✅ ALIVE {ms}" if alive else "❌ DOWN"
    print(f"  {name:30s} {status}")

# ─── HTTP probes ───
print("\n[2] HTTP/HTTPS service probes...\n")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

services = [
    ("eastGate data :8080", "http://192.168.4.244:8080/data/now.json"),
    ("eastGate gate :8443", "https://192.168.4.244:8443/pulse"),
    ("eastGate Forgejo :3000", "http://192.168.4.244:3000/"),
    ("Tor onion (via eastGate)", "http://iqwvbmlgvoiilj2hr43anj2keseao2lptquad36je5p5p2etw5e3riid.onion"),
    ("grapheneGate llama :8082", "http://192.168.9.217:8082/"),
    ("ironGate ollama :11434", "http://192.168.4.237:11434/"),
    ("graftGate ollama :11434", "http://192.168.4.107:11434/"),
]

for name, url in services:
    try:
        req = urllib.request.Request(url, method='GET')
        if url.startswith('https'):
            resp = urllib.request.urlopen(req, timeout=3, context=ctx)
        else:
            resp = urllib.request.urlopen(req, timeout=3)
        body = resp.read(500).decode('utf-8', errors='replace')
        print(f"  ✅ {name:35s} HTTP {resp.status} ({len(body)}B)")
        if 'now.json' in name and body:
            try:
                data = json.loads(body)
                print(f"     → {json.dumps(data, indent=None)[:200]}")
            except:
                print(f"     → {body[:150]}")
        elif body:
            print(f"     → {body[:120].strip()}")
    except Exception as e:
        err_str = str(e)[:80]
        print(f"  ❌ {name:35s} {err_str}")

# ─── TCP port scan for key services ───
print("\n[3] TCP port scan (key services)...\n")
port_checks = [
    ("eastGate", "192.168.4.244", [22, 80, 443, 3000, 8080, 8443, 9418, 11436]),
    ("grapheneGate", "192.168.9.217", [8082, 5555]),
    ("sporeGate", "192.168.4.3", [22, 53, 80]),
    ("ironGate", "192.168.4.237", [22, 11434]),
]

for name, ip, ports in port_checks:
    open_ports = []
    for port in ports:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            result = s.connect_ex((ip, port))
            if result == 0:
                open_ports.append(str(port))
            s.close()
        except:
            pass
    status = ', '.join(open_ports) if open_ports else 'none reachable'
    print(f"  {name:20s} open ports: {status}")

# ─── RSS feed check ───
print("\n[4] RSS feed...\n")
try:
    resp = urllib.request.urlopen("http://192.168.4.244:8080/data/feed.xml", timeout=5)
    body = resp.read(2000).decode('utf-8', errors='replace')
    lines = body.split('\n')
    for line in lines[:8]:
        print(f"  {line.strip()}")
    # Count items
    item_count = body.count('<item>') + body.count('<entry>')
    print(f"  ... ({item_count}+ items in first 2KB)")
except Exception as e:
    print(f"  ❌ {e}")

# ─── Tor check (local) ───  
print("\n[5] Tor reachability...\n")
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    result = s.connect_ex(("192.168.4.244", 9050))
    s.close()
    print(f"  Tor SOCKS5 port 9050: {'✅ OPEN' if result == 0 else '❌ closed'}")
except:
    print("  Tor SOCKS5: unreachable")

print("\n" + "=" * 60)
print("DONE — northGate can see the organism from here")
