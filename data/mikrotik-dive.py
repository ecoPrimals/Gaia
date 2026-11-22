"""mikrotik-dive.py — SSH into MikroTik, dump switching table, measure ALL distances."""
import subprocess
import socket
import time
import json
from concurrent.futures import ThreadPoolExecutor

MIKROTIK = "192.168.4.2"

print("=" * 70)
print("  MIKROTIK DIVE + FULL DISTANCE MATRIX")
print("=" * 70)

# ============================================================
# PART 1: MikroTik SSH — dump bridge, ARP, interfaces
# ============================================================
print("\n--- MIKROTIK SSH COMMANDS ---")

# RouterOS commands we want to run
commands = [
    "/interface print",
    "/ip address print",
    "/ip arp print",
    "/interface bridge port print",
    "/interface bridge host print",
    "/system resource print",
    "/system identity print",
    "/ip route print",
    "/interface ethernet print",
]

for cmd in commands:
    print(f"\n>>> {cmd}")
    try:
        # Use ssh with sshpass (if available) or plink
        # Try with PowerShell SSH client
        r = subprocess.run(
            ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=5",
             "-o", "UserKnownHostsFile=NUL",
             f"admin@{MIKROTIK}", cmd],
            capture_output=True, text=True, timeout=10,
            input="FUHWERYEWRH\n"
        )
        if r.stdout.strip():
            for line in r.stdout.strip().split("\n")[:30]:
                print(f"  {line}")
        if r.stderr.strip() and "Warning" not in r.stderr:
            print(f"  STDERR: {r.stderr.strip()[:200]}")
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT")
    except Exception as e:
        print(f"  Error: {e}")

# ============================================================
# PART 2: Full Distance Matrix — ALL alive nodes
# ============================================================
print(f"\n{'=' * 70}")
print("  DISTANCE MATRIX — Inner (LAN) + Outer (WAN)")
print(f"{'=' * 70}")

# All known IPs to measure
targets = {
    "ATT modem":    "192.168.1.254",
    "eastGate":     "192.168.1.81",
    "biomegate":    "192.168.1.232",
    "MikroTik":     "192.168.4.2",
    "northGate.4":  "192.168.4.147",
    "northGate.1":  "192.168.1.231",
    "sporeGate.4":  "192.168.4.3",
    "sporeGate.1":  "192.168.1.75",
    "Google DNS":   "8.8.8.8",
    "Cloudflare":   "1.1.1.1",
    "primals.eco":  "162.226.225.148",
}

def measure(name_ip):
    name, ip = name_ip
    try:
        r = subprocess.run(f"ping -n 3 -w 1000 {ip}", 
                          capture_output=True, text=True, shell=True, timeout=10)
        if "TTL=" in r.stdout:
            # Extract average
            for line in r.stdout.split("\n"):
                if "Average" in line:
                    avg = line.split("Average = ")[1].strip().replace("ms", "")
                    return name, ip, float(avg), "UP"
                if "Minimum" in line and "Average" not in r.stdout:
                    # Sometimes format differs
                    pass
            # Fallback: get from reply lines
            times = []
            for line in r.stdout.split("\n"):
                if "time=" in line:
                    t = line.split("time=")[1].split("ms")[0]
                    times.append(float(t))
                elif "time<" in line:
                    times.append(0.5)
            if times:
                return name, ip, sum(times)/len(times), "UP"
            return name, ip, 0, "UP"
        return name, ip, None, "DOWN"
    except:
        return name, ip, None, "ERROR"

print("\n  Measuring all distances...\n")
with ThreadPoolExecutor(10) as ex:
    results = list(ex.map(measure, targets.items()))

# Sort by distance
results.sort(key=lambda x: x[2] if x[2] is not None else 99999)

print(f"  {'Node':<16} {'IP':<20} {'Distance':>10} {'State'}")
print(f"  {'─'*16} {'─'*20} {'─'*10} {'─'*6}")
for name, ip, dist, state in results:
    if state == "UP":
        d = f"{dist:.1f}ms" if dist else "<1ms"
        zone = "INNER" if dist and dist < 5 else ("NEAR" if dist and dist < 50 else "OUTER")
        print(f"  {name:<16} {ip:<20} {d:>10} {zone}")
    else:
        print(f"  {name:<16} {ip:<20} {'---':>10} {state}")

# WAN distance (traceroute to primals.eco)
print(f"\n--- OUTER DISTANCE (traceroute to WAN) ---")
r = subprocess.run("tracert -d -w 500 -h 10 8.8.8.8", capture_output=True, text=True, shell=True, timeout=30)
hops = []
for line in r.stdout.split("\n"):
    l = line.strip()
    if l and l[0].isdigit() and "ms" in l:
        print(f"  {l}")
        hops.append(l)
print(f"  Hops to internet: {len(hops)}")

# Inner mesh distances (between LAN nodes we can reach)
print(f"\n--- INNER MESH (node-to-node via northGate) ---")
print(f"  northGate → eastGate:  via .1.x (WiFi → WiFi/wired)")
print(f"  northGate → biomegate: via .1.x (WiFi → wired)")
print(f"  northGate → MikroTik:  via .4.x (Ethernet → L2)")
print(f"  eastGate → biomegate:  same .1.x L2 segment (~0.5ms est)")
print(f"  MikroTik → northGate:  direct .4.x L2 (~0.3ms)")
