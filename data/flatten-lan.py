"""flatten-lan.py — Map the current LAN topology and plan the FLAT path.

Current (treacherous):
  ATT BGW320 (192.168.1.254) → GL-MT6000 (192.168.4.1) → MikroTik → devices
  Double-NAT, hairpin broken, 3+ subnets

Flat target:
  ATT in IP PASSTHROUGH → GL-MT6000 gets public IP → ONE flat subnet → all gates
"""
import subprocess
import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

OUT = Path(__file__).parent

def run(cmd, timeout=10):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=True)
    return r.stdout + r.stderr

def ping(ip):
    try:
        r = subprocess.run(f"ping -n 1 -w 500 {ip}", capture_output=True, text=True, timeout=3, shell=True)
        return ip if "TTL=" in r.stdout else None
    except:
        return None

def tracert(ip):
    try:
        r = subprocess.run(f"tracert -d -w 500 -h 5 {ip}", capture_output=True, text=True, timeout=15, shell=True)
        hops = []
        for line in r.stdout.split("\n"):
            line = line.strip()
            if "ms" in line or "*" in line:
                hops.append(line)
        return hops
    except:
        return []

print("=" * 70)
print("  FLATTEN THE LAN — Topology Scout")
print("=" * 70)

# 1. OUR INTERFACES
print("\n--- INTERFACES ---")
ipcfg = run("ipconfig /all")
current_section = ""
for line in ipcfg.split("\n"):
    l = line.strip()
    if "adapter" in l.lower():
        current_section = l
    if any(k in l for k in ["IPv4", "Default Gateway", "DNS Servers", "DHCP Server", "Subnet Mask"]):
        if current_section:
            print(f"  [{current_section}]")
            current_section = ""
        print(f"    {l}")
print()

# 2. ROUTE TABLE
print("--- ROUTE TABLE ---")
routes = run("route print -4")
for line in routes.split("\n"):
    l = line.strip()
    if l and any(l.startswith(p) for p in ["0.0.0.0", "192.168", "10.", "172.", "255."]):
        print(f"  {l}")
print()

# 3. ARP TABLE
print("--- ARP TABLE ---")
arp_out = run("arp -a")
arp_entries = []
for line in arp_out.split("\n"):
    l = line.strip()
    if "192.168" in l and "dynamic" in l.lower():
        arp_entries.append(l)
        print(f"  {l}")
print(f"  Total: {len(arp_entries)} dynamic entries")
print()

# 4. PING SWEEP — all three subnets
print("--- PING SWEEP ---")
subnets = {
    "192.168.4": "LAN1 (Gaia brain)",
    "192.168.9": "LAN2 (South Pole)",
    "192.168.1": "ATT modem layer",
}

alive_map = {}
for prefix, label in subnets.items():
    targets = [f"{prefix}.{i}" for i in range(1, 255)]
    with ThreadPoolExecutor(50) as ex:
        alive = sorted([ip for ip in ex.map(ping, targets) if ip],
                      key=lambda x: int(x.split(".")[-1]))
    alive_map[prefix] = alive
    print(f"  {label} ({prefix}.x): {len(alive)} alive")
    for ip in alive:
        print(f"    {ip}")
    print()

# 5. TRACEROUTE — how many hops to key targets?
print("--- HOP COUNT ---")
key_targets = [
    ("ATT modem", "192.168.1.254"),
    ("Router", "192.168.4.1"),
    ("MikroTik", "192.168.4.2"),
    ("eastGate", "192.168.4.244"),
    ("South Pole router", "192.168.9.1"),
    ("Internet (Google)", "8.8.8.8"),
]
for name, ip in key_targets:
    alive = ping(ip)
    if alive:
        hops = tracert(ip)
        print(f"  {name} ({ip}): ALIVE — {len(hops)} hops")
        for h in hops[:3]:
            print(f"    {h}")
    else:
        print(f"  {name} ({ip}): UNREACHABLE")

# 6. DNS CHECK
print("\n--- DNS ---")
dns_out = run("nslookup primals.eco")
for line in dns_out.split("\n"):
    l = line.strip()
    if l:
        print(f"  {l}")

# 7. FLATTEN PLAN
print("\n" + "=" * 70)
print("  FLATTEN PLAN")
print("=" * 70)

att_alive = alive_map.get("192.168.1", [])
lan1_alive = alive_map.get("192.168.4", [])
lan2_alive = alive_map.get("192.168.9", [])

print(f"""
  CURRENT SHAPE (treacherous):
    Internet → ATT BGW320 (.1.254) → NAT → GL-MT6000 (.4.1) → NAT → devices
    Three subnets: .1.x (ATT), .4.x (LAN1), .9.x (LAN2/guest)
    Double-NAT breaks: hairpin, port forwards, Tor, inbound
    ATT layer has {len(att_alive)} devices, LAN1 has {len(lan1_alive)}, LAN2 has {len(lan2_alive)}

  FLAT TARGET:
    Internet → ATT BGW320 (IP PASSTHROUGH) → GL-MT6000 (PUBLIC IP) → ONE subnet
    - ATT modem becomes dumb bridge (passes public IP to router)
    - GL-MT6000 gets 162.226.225.148 directly on WAN
    - ONE subnet: 192.168.4.0/24 for everything
    - 192.168.9.x (LAN2) stays as guest VLAN for House 2 WiFi
    - Port forwards work DIRECTLY (no double-NAT)
    - Hairpin NAT works (router handles it)
    - Tor hidden service works clean

  HOW TO DO IT:
    1. Log into ATT BGW320 at http://192.168.1.254 (device access code on modem label)
    2. Go to Firewall → IP Passthrough
    3. Set Allocation Mode: Passthrough
    4. Set Passthrough Mode: DHCPS-fixed
    5. Select the GL-MT6000 MAC (94:83:c4:e0:62:xx) as passthrough device
    6. Save → ATT modem passes public IP to GL-MT6000
    7. GL-MT6000 WAN interface now gets 162.226.225.148 directly
    8. All port forwards go through ONE NAT layer
    9. Flint drops out of the path — ATT becomes transparent

  RESULT:
    Internet → [ATT bridge] → GL-MT6000 (162.226.225.148) → 192.168.4.x (all gates)
    ONE hop. ONE NAT. FLAT.
""")

# Save results
result = {
    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "subnets": {k: v for k, v in alive_map.items()},
    "arp_count": len(arp_entries),
    "plan": "ATT IP Passthrough → GL-MT6000 gets public IP → flat single-NAT",
}
(OUT / "flatten-topology.json").write_text(json.dumps(result, indent=2))
print("  Saved: flatten-topology.json")
