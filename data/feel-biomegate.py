"""feel-biomegate.py — Find biomegate on the wire, detect boot loop, begin DAG."""
import subprocess
import socket
import time
from concurrent.futures import ThreadPoolExecutor

def ping(ip):
    try:
        r = subprocess.run(f"ping -n 1 -w 300 {ip}", capture_output=True, text=True, timeout=2, shell=True)
        return ip if "TTL=" in r.stdout else None
    except:
        return None

def tcp_probe(ip, ports):
    open_ports = []
    for port in ports:
        try:
            s = socket.create_connection((ip, port), timeout=0.5)
            s.close()
            open_ports.append(port)
        except:
            pass
    return open_ports

print("=" * 70)
print("  FEEL BIOMEGATE — DDR5 sibling on the RJ wire")
print("=" * 70)

# 1. Flush ARP and re-ping ALL local subnets to force fresh discovery
print("\n--- FLUSHING ARP + SWEEP ---")
subprocess.run("arp -d *", capture_output=True, shell=True)

# Ping sweep ALL subnets — biomegate could be anywhere
subnets = ["192.168.4", "192.168.1", "192.168.9", "192.168.8"]
all_alive = []

for prefix in subnets:
    targets = [f"{prefix}.{i}" for i in range(1, 255)]
    with ThreadPoolExecutor(80) as ex:
        alive = sorted([ip for ip in ex.map(ping, targets) if ip],
                       key=lambda x: int(x.split(".")[-1]))
    if alive:
        print(f"  {prefix}.x: {len(alive)} alive — {alive}")
        all_alive.extend(alive)

# 2. Fresh ARP table
print("\n--- FRESH ARP TABLE ---")
time.sleep(1)
r = subprocess.run("arp -a", capture_output=True, text=True, shell=True)
arp_entries = []
for line in r.stdout.split("\n"):
    l = line.strip()
    if "dynamic" in l.lower() and "192.168" in l:
        arp_entries.append(l)
        print(f"  {l}")

# 3. Known biomegate MAC: b4:2e:99:a7:91:a3 and b4:2e:99:a7:91:a5
print("\n--- SEARCHING FOR BIOMEGATE MACs ---")
biomegate_macs = ["b4-2e-99-a7-91-a3", "b4-2e-99-a7-91-a5", "b4:2e:99:a7:91:a3", "b4:2e:99:a7:91:a5"]
for entry in arp_entries:
    for mac in biomegate_macs:
        if mac.lower() in entry.lower():
            print(f"  *** BIOMEGATE FOUND: {entry} ***")

# 4. Probe ALL alive IPs for boot-loop signatures
print("\n--- PROBING ALIVE HOSTS ---")
common_ports = [22, 80, 443, 67, 68, 69, 3000, 5000, 8080, 8443, 9090]
for ip in all_alive:
    if ip.endswith(".147"):  # skip ourselves
        continue
    ports = tcp_probe(ip, common_ports)
    # Also check DHCP traffic (port 67/68 would indicate boot loop DHCP requests)
    print(f"  {ip:16s} ports: {ports if ports else 'none open'}")

# 5. Check for DHCP activity (biomegate in boot loop would spam DHCP)
print("\n--- DHCP LEASE CHECK ---")
# Check our own DHCP info for recent activity
r = subprocess.run("ipconfig /all", capture_output=True, text=True, shell=True)
for line in r.stdout.split("\n"):
    if any(k in line for k in ["DHCP", "Lease", "Server"]):
        print(f"  {line.strip()}")

# 6. Listen for broadcast traffic (boot loop devices often broadcast)
print("\n--- LISTENING FOR BROADCASTS (3s) ---")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", 67))  # DHCP server port — hear DHCP requests
    sock.settimeout(3)
    heard = []
    start = time.time()
    while time.time() - start < 3:
        try:
            data, addr = sock.recvfrom(4096)
            heard.append(f"  DHCP from {addr}: {len(data)} bytes")
        except socket.timeout:
            break
    sock.close()
    if heard:
        for h in heard:
            print(h)
        print("  *** Boot loop device detected! ***")
    else:
        print("  No DHCP broadcasts heard (biomegate may not be DHCP-looping)")
except PermissionError:
    print("  Cannot bind DHCP port (need admin)")
except Exception as e:
    print(f"  Broadcast listen: {e}")

# 7. Try biomegate's last known IPs
print("\n--- TRYING KNOWN BIOMEGATE IPs ---")
known_ips = ["192.168.1.232", "192.168.1.233", "192.168.4.232", "192.168.4.233"]
for ip in known_ips:
    alive = ping(ip)
    if alive:
        ports = tcp_probe(ip, [22, 80, 443, 8080, 5000, 9090])
        print(f"  {ip}: ALIVE! ports={ports}")
    else:
        print(f"  {ip}: dark")

# 8. Wider sweep — check .4.x range more thoroughly (biomegate might be on a new IP)
print("\n--- WIDER .4.x SWEEP (100-250) ---")
targets = [f"192.168.4.{i}" for i in range(100, 251)]
with ThreadPoolExecutor(50) as ex:
    alive_4 = sorted([ip for ip in ex.map(ping, targets) if ip],
                     key=lambda x: int(x.split(".")[-1]))
print(f"  Found: {alive_4 if alive_4 else 'nobody but us'}")

print("\n" + "=" * 70)
print("  DAG TOPOLOGY PLAN")
print("=" * 70)
print("""
  CURRENT: Tree (ATT → Router → MikroTik → devices)
           Most gates DARK. Single point of failure at router.

  DAG TARGET: Multiple paths, no loops, directed flow:
    ATT modem (passthrough) → GL-MT6000 (edge router)
                            → MikroTik (L2 backbone) → wired gates
                            → WiFi (Aperture/BlackMesa) → wireless gates
    Each gate can reach any other WITHOUT going through a single choke.
    No spanning tree needed — topology is acyclic by design.

  TO BUILD THE DAG:
    1. Remove redundant wires (simplify physical layer)
    2. Each gate gets ONE uplink (no loops)
    3. Cross-links via WiFi as backup (Aperture for IoT, BlackMesa for data)
    4. Biomegate + northGate on same switch = direct L2 path
""")
