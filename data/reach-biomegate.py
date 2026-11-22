"""reach-biomegate.py — Reach biomegate at 192.168.1.233 and diagnose boot loop."""
import socket
import subprocess
import time

IP = "192.168.1.233"
IP2 = "192.168.1.232"  # other MAC's last known IP

print(f"=== REACHING FOR BIOMEGATE ===")
print(f"  Primary:   {IP} (MAC b4:2e:99:a7:91:a5)")
print(f"  Secondary: {IP2} (MAC b4:2e:99:a7:91:a3)")

# Try both IPs
for target in [IP, IP2]:
    print(f"\n--- Probing {target} ---")
    r = subprocess.run(f"ping -n 3 -w 1000 {target}", capture_output=True, text=True, shell=True, timeout=10)
    if "TTL=" in r.stdout:
        for line in r.stdout.split("\n"):
            if "TTL=" in line or "Reply" in line or "Ping" in line:
                print(f"  {line.strip()}")
    else:
        print(f"  No ping response")

# Full port scan on .233
print(f"\n--- PORT SCAN {IP} ---")
all_ports = [
    21, 22, 23, 25, 53, 67, 68, 69, 80, 111, 123, 135, 137, 139, 161, 443,
    445, 548, 554, 631, 873, 993, 1080, 1433, 2049, 2222, 3000, 3306, 3389,
    4000, 5000, 5060, 5222, 5432, 5900, 6000, 6379, 7741, 8000, 8080, 8443,
    8888, 9090, 9100, 9200, 9418, 11434, 11436, 27017,
]

open_ports = []
refused_ports = []
timeout_ports = []
for port in all_ports:
    try:
        s = socket.create_connection((IP, port), timeout=0.5)
        s.close()
        open_ports.append(port)
        print(f"  :{port} OPEN!")
    except ConnectionRefusedError:
        refused_ports.append(port)
    except (socket.timeout, OSError):
        timeout_ports.append(port)

if open_ports:
    print(f"\n  OPEN: {open_ports}")
if refused_ports:
    print(f"  REFUSED (OS up, port closed): {refused_ports[:10]}{'...' if len(refused_ports) > 10 else ''}")
print(f"  TIMEOUT (filtered/down): {len(timeout_ports)} ports")

# If SSH is open, we could talk to it
if 22 in open_ports:
    print(f"\n  ** SSH IS OPEN! biomegate is booted enough for SSH **")
    print(f"  Try: ssh root@{IP}")

# If HTTP is open, check what it says
for port in [80, 443, 8080, 8443]:
    if port in open_ports:
        print(f"\n  ** HTTP at :{port} — checking...")
        try:
            import urllib.request
            url = f"http{'s' if port == 443 else ''}://{IP}:{port}/"
            req = urllib.request.Request(url, headers={"User-Agent": "Gaia"})
            r = urllib.request.urlopen(req, timeout=3)
            print(f"    Status: {r.status}")
            data = r.read(500).decode(errors="replace")
            print(f"    Body: {data[:200]}")
        except Exception as e:
            print(f"    Error: {e}")

# Monitor for 30 seconds — watch if it stays or vanishes
print(f"\n--- STABILITY WATCH (30s) ---")
for i in range(10):
    r = subprocess.run(f"ping -n 1 -w 500 {IP}", capture_output=True, text=True, shell=True, timeout=3)
    alive = "TTL=" in r.stdout
    ttl = ""
    if alive:
        for line in r.stdout.split("\n"):
            if "TTL=" in line:
                ttl = line.strip()
    
    # Also check ARP for MAC
    r2 = subprocess.run("arp -a", capture_output=True, text=True, shell=True)
    mac = "?"
    for line in r2.stdout.split("\n"):
        if IP in line and "dynamic" in line.lower():
            parts = line.strip().split()
            if len(parts) >= 2:
                mac = parts[1]
    
    t = time.time()
    state = "UP" if alive else "DOWN"
    print(f"  t={i*3:2d}s: {state}  mac={mac}  {ttl}")
    time.sleep(3)

# Check if biomegate also appeared on .4.x
print(f"\n--- CHECK .4.x FOR BIOMEGATE ---")
r = subprocess.run("arp -a", capture_output=True, text=True, shell=True)
for line in r.stdout.split("\n"):
    l = line.strip()
    if "dynamic" in l.lower():
        if "b4-2e-99" in l.lower():
            print(f"  BIOMEGATE: {l}")
        elif "192.168" in l:
            print(f"  {l}")
