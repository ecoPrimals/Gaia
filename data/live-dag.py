"""live-dag.py — Full live mesh map, distances, and DAG topology."""
import subprocess
import socket
import time
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor

print("=" * 70)
print("  LIVE DAG — Full Mesh Map")
print("  " + time.strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 70)

# ============================================================
# 1. DISCOVER — ping sweep both subnets
# ============================================================
def ping_one(ip):
    try:
        r = subprocess.run(f"ping -n 2 -w 500 {ip}", capture_output=True, text=True, shell=True, timeout=5)
        if "TTL=" in r.stdout:
            times = []
            ttl = "?"
            for line in r.stdout.split("\n"):
                if "time=" in line:
                    t = float(line.split("time=")[1].split("ms")[0])
                    times.append(t)
                elif "time<" in line:
                    times.append(0.5)
                if "TTL=" in line:
                    ttl = line.split("TTL=")[1].strip()
            avg = sum(times)/len(times) if times else 0
            return ip, avg, ttl
        return ip, None, None
    except:
        return ip, None, None

print("\n--- SWEEP: .1.x (ATT subnet) + .4.x (LAN backbone) ---")
targets_1 = [f"192.168.1.{i}" for i in range(1, 255)]
targets_4 = [f"192.168.4.{i}" for i in range(1, 255)]
wan_targets = [("8.8.8.8", "Google"), ("1.1.1.1", "Cloudflare"), ("162.226.225.148", "primals.eco")]

with ThreadPoolExecutor(80) as ex:
    results_1 = {r[0]: r for r in ex.map(ping_one, targets_1) if r[1] is not None}
    
with ThreadPoolExecutor(80) as ex:
    results_4 = {r[0]: r for r in ex.map(ping_one, targets_4) if r[1] is not None}

with ThreadPoolExecutor(5) as ex:
    results_wan = {ip: ping_one(ip) for ip, _ in wan_targets}

# ARP for MACs
time.sleep(0.5)
r = subprocess.run("arp -a", capture_output=True, text=True, shell=True)
arp = {}
for line in r.stdout.split("\n"):
    l = line.strip()
    if "dynamic" in l.lower() and "192.168" in l:
        parts = l.split()
        if len(parts) >= 2:
            arp[parts[0]] = parts[1].replace("-", ":").lower()

# Known MAC → name mapping
mac_names = {
    "b4:2e:99:a7:91:a3": "biomegate-1",
    "b4:2e:99:a7:91:a5": "biomegate-2",
    "c8:5e:a9:c9:6f:80": "eastGate",
    "04:f4:1c:e6:7c:e8": "MikroTik",
    "4c:50:dd:9b:c1:ec": "sporeGate",
    "bc:fc:e7:ea:d9:34": "northGate-eth",
    "ac:f2:3c:25:fc:c1": "northGate-wifi",
    "ec:c3:02:e1:11:81": "ATT-modem",
    "1c:86:0b:37:63:19": "eastGate-intel",
}

# ============================================================
# 2. MAP — identify all nodes
# ============================================================
print(f"\n{'=' * 70}")
print("  NODES ON .1.x (ATT modem direct)")
print(f"{'=' * 70}")
for ip in sorted(results_1.keys(), key=lambda x: int(x.split(".")[-1])):
    _, avg, ttl = results_1[ip]
    mac = arp.get(ip, "unknown")
    name = mac_names.get(mac, "?")
    os_guess = "Linux" if ttl == "64" else ("Windows" if ttl == "128" else ("Router" if ttl == "255" else "?"))
    print(f"  {ip:18s} {avg:>7.1f}ms TTL={ttl:3s} MAC={mac:20s} → {name} ({os_guess})")

print(f"\n{'=' * 70}")
print("  NODES ON .4.x (LAN backbone)")
print(f"{'=' * 70}")
for ip in sorted(results_4.keys(), key=lambda x: int(x.split(".")[-1])):
    _, avg, ttl = results_4[ip]
    mac = arp.get(ip, "unknown")
    name = mac_names.get(mac, "?")
    os_guess = "Linux" if ttl == "64" else ("Windows" if ttl == "128" else ("Router" if ttl == "255" else "?"))
    print(f"  {ip:18s} {avg:>7.1f}ms TTL={ttl:3s} MAC={mac:20s} → {name} ({os_guess})")

print(f"\n{'=' * 70}")
print("  WAN DISTANCES")
print(f"{'=' * 70}")
for ip, label in wan_targets:
    if ip in results_wan and results_wan[ip][1] is not None:
        _, avg, ttl = results_wan[ip]
        print(f"  {label:18s} {ip:18s} {avg:>7.1f}ms TTL={ttl}")
    else:
        print(f"  {label:18s} {ip:18s}    DOWN")

# ============================================================
# 3. eastGate data pull
# ============================================================
print(f"\n{'=' * 70}")
print("  EASTGATE SERVICE CHECK (.1.81)")
print(f"{'=' * 70}")

services = {
    ":80 HTTP": "http://192.168.1.81",
    ":3000 Forgejo": "http://192.168.1.81:3000",
    ":8080 Data": "http://192.168.1.81:8080",
    ":8443 Gate": "http://192.168.1.81:8443",
    ":8443/pulse": "http://192.168.1.81:8443/pulse",
}

for name, url in services.items():
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Gaia-northGate"})
        r = urllib.request.urlopen(req, timeout=3)
        body = r.read(100).decode(errors='replace')
        print(f"  {name:20s} → {r.status} ({body[:60]}...)")
    except Exception as e:
        print(f"  {name:20s} → {str(e)[:60]}")

# ============================================================
# 4. DISTANCE MATRIX
# ============================================================
print(f"\n{'=' * 70}")
print("  INNER/OUTER DISTANCE MATRIX (from northGate)")
print(f"{'=' * 70}")

all_nodes = {}
for ip, (_, avg, ttl) in results_1.items():
    mac = arp.get(ip, "?")
    name = mac_names.get(mac, ip.split(".")[-1])
    all_nodes[name] = {"ip": ip, "dist": avg, "ttl": ttl, "subnet": ".1.x"}

for ip, (_, avg, ttl) in results_4.items():
    mac = arp.get(ip, "?")
    name = mac_names.get(mac, ip.split(".")[-1])
    if name not in all_nodes or avg < all_nodes[name]["dist"]:
        all_nodes[name] = {"ip": ip, "dist": avg, "ttl": ttl, "subnet": ".4.x"}

# Add WAN
for ip, label in wan_targets:
    if ip in results_wan and results_wan[ip][1] is not None:
        _, avg, ttl = results_wan[ip]
        all_nodes[label] = {"ip": ip, "dist": avg, "ttl": ttl, "subnet": "WAN"}

# Sort by distance
for name, info in sorted(all_nodes.items(), key=lambda x: x[1]["dist"]):
    zone = "CORE" if info["dist"] < 1 else ("INNER" if info["dist"] < 10 else ("NEAR" if info["dist"] < 50 else "OUTER"))
    print(f"  {info['dist']:>8.1f}ms  {zone:5s}  {name:20s} {info['ip']:18s} {info['subnet']}")

# ============================================================
# 5. DAG SHAPE
# ============================================================
print(f"\n{'=' * 70}")
print("  DAG TOPOLOGY")
print(f"{'=' * 70}")

alive_1 = len(results_1) - 1  # subtract ourselves
alive_4 = len(results_4) - 1
print(f"  .1.x nodes: {alive_1}")
print(f"  .4.x nodes: {alive_4}")
print(f"  WAN hops: 10 (traced earlier)")
print(f"  Cross-links: northGate bridges .1.x ↔ .4.x (forwarding+NAT)")
print(f"""
  DAG SHAPE:
  
  WAN ─── ATT modem (.1.254, 2ms)
           │
           ├── eastGate (.1.81, ~100ms WiFi, BRAIN)
           │     SSH | HTTP | Forgejo | Gate | Data
           │
           ├── biomegate (.1.232/.233, ~3ms wired, BOOT LOOP)
           │     ICMP only — firewall blocks all TCP
           │
           └── northGate (.1.231 WiFi, BRIDGE)
                 │
                 ═══ DAG BRIDGE (IP forwarding + NAT) ═══
                 │
                 northGate (.4.147 Ethernet, 2.5Gbps)
                 │
                 └── MikroTik (.4.2, <1ms, L2 backbone)
                       │
                       └── [GL-MT6000 (.4.1) DARK — passthrough configured]
                       └── [sporeGate (.4.3) FLUX — in ARP, not responding]
""")
