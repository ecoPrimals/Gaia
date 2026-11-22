"""dag-map.py — Map current mesh topology and identify DAG paths."""
import subprocess
import socket
import time
from concurrent.futures import ThreadPoolExecutor

def ping(ip):
    try:
        r = subprocess.run(f"ping -n 1 -w 400 {ip}", capture_output=True, text=True, shell=True, timeout=3)
        if "TTL=" in r.stdout:
            for line in r.stdout.split("\n"):
                if "TTL=" in line:
                    ms = line.split("time=")[1].split("ms")[0] if "time=" in line else "?"
                    ttl = line.split("TTL=")[1].strip() if "TTL=" in line else "?"
                    return ip, ms, ttl
        return ip, None, None
    except:
        return ip, None, None

print("=" * 70)
print("  DAG TOPOLOGY MAP — All nodes, all paths")
print("=" * 70)

# Sweep both subnets fresh
print("\n--- PING ALL KNOWN + SWEEP ---")
known = {
    "192.168.1.233": "biomegate (HP, DDR5, Linux)",
    "192.168.1.232": "biomegate NIC2?",
    "192.168.1.231": "northGate WiFi (us)",
    "192.168.1.254": "ATT modem",
    "192.168.1.75":  "sporeGate WiFi?",
    "192.168.1.81":  "eastGate WiFi?",
    "192.168.1.221": "sporeGate WiFi2?",
    "192.168.4.147": "northGate ETH (us)",
    "192.168.4.2":   "MikroTik",
    "192.168.4.3":   "sporeGate",
    "192.168.4.248": "mystery (c8:5e:a9)",
    "192.168.4.244": "eastGate (expected)",
    "192.168.4.1":   "GL-MT6000 (router)",
}

for ip, name in sorted(known.items()):
    _, ms, ttl = ping(ip)
    if ms:
        print(f"  {ip:18s} {ms:>5s}ms TTL={ttl:3s}  {name}")
    else:
        print(f"  {ip:18s}  DARK          {name}")

# Full ARP after pings
print("\n--- ARP TABLE (all entries) ---")
time.sleep(0.5)
r = subprocess.run("arp -a", capture_output=True, text=True, shell=True)
arp = {}
for line in r.stdout.split("\n"):
    l = line.strip()
    if "dynamic" in l.lower() and "192.168" in l:
        parts = l.split()
        if len(parts) >= 2:
            arp[parts[0]] = parts[1]
            print(f"  {parts[0]:18s} {parts[1]}")

# Discover any new IPs on .1.x (biomegate's subnet)
print("\n--- QUICK .1.x SWEEP (220-250) ---")
targets = [f"192.168.1.{i}" for i in range(220, 251)]
with ThreadPoolExecutor(30) as ex:
    results = list(ex.map(ping, targets))
for ip, ms, ttl in results:
    if ms:
        mac = arp.get(ip, "?")
        print(f"  {ip}: {ms}ms TTL={ttl} MAC={mac}")

# northGate's own interfaces
print("\n--- NORTHGATE INTERFACES (our paths) ---")
r = subprocess.run("ipconfig", capture_output=True, text=True, shell=True)
current_adapter = ""
for line in r.stdout.split("\n"):
    l = line.strip()
    if "adapter" in line.lower() and ":" in line:
        current_adapter = l
    elif "IPv4" in l and "192.168" in l:
        print(f"  {current_adapter}")
        print(f"    {l}")

# northGate routing table
print("\n--- ROUTING TABLE (paths to world) ---")
r = subprocess.run("route print -4 192.168.*", capture_output=True, text=True, shell=True)
in_routes = False
for line in r.stdout.split("\n"):
    l = line.strip()
    if "Active Routes" in l or "Network Dest" in l:
        in_routes = True
    if in_routes and l and ("0.0.0.0" in l or "192.168" in l):
        print(f"  {l}")

# DAG Analysis
print(f"\n{'=' * 70}")
print("  DAG ANALYSIS — Current mesh paths")
print(f"{'=' * 70}")
print("""
  NODES ALIVE:
    ATT modem (.1.254) — WAN gateway, DHCP
    MikroTik (.4.2) — L2 backbone
    northGate (.4.147 + .1.231) — DUAL-HOMED, DAG vertex!
    sporeGate (.4.3 + .1.75 + .1.221) — TRIPLE-HOMED, DAG vertex!
    biomegate (.1.233) — SINGLE-HOMED, needs 2nd path for DAG

  CURRENT EDGES (directed, toward WAN):
    biomegate → ATT modem (wired .1.x)
    northGate → ATT modem (WiFi .1.x)
    northGate → MikroTik (wired .4.x) → [router DARK] → ??
    sporeGate → ATT modem (WiFi .1.x)
    sporeGate → MikroTik (wired .4.x) → [router DARK] → ??

  CROSS-EDGES (DAG lateral, peer-to-peer):
    northGate ↔ MikroTik (wired, 0.25ms)
    northGate ↔ biomegate (through ATT modem, 2ms)
    northGate ↔ sporeGate (.4.x: through MikroTik OR .1.x: through ATT)
    
  TO MAKE FULL DAG:
    1. biomegate needs 2nd NIC on .4.x (plug into MikroTik)
       → Creates: biomegate → MikroTik → northGate (redundant path!)
    2. GL-MT6000 needs to come UP 
       → Creates: .4.x → router → ATT → WAN (the original tree path)
    3. With router UP + biomegate dual-homed:
       biomegate → ATT (direct) OR biomegate → MikroTik → router → ATT
       = TWO paths to WAN = DAG!

  CURRENT SHAPE:
    ATT ←── biomegate (wired)
     ↑
     ├── northGate (WiFi) ←── MikroTik ←── [router DARK]
     │                         ↑
     └── sporeGate (WiFi) ─────┘
         (also wired to MikroTik)
""")
