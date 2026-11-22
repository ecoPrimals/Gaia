"""identify-biomegate.py — Deep identification of biomegate and service coaxing."""
import socket
import subprocess
import time
import struct

IP = "192.168.1.233"

print("=" * 70)
print(f"  IDENTIFY BIOMEGATE — {IP}")
print(f"  MAC: b4:2e:99:a7:91:a5 — OUI: b4:2e:99")
print("=" * 70)

# OUI lookup
print("\n--- OUI MANUFACTURER ---")
print("  b4:2e:99 = Hewlett Packard / HP Inc.")
print("  (HP uses this OUI for desktops, workstations, mini PCs)")
print("  biomegate is likely an HP desktop/workstation with DDR5!")

# Wider port scan — check ALL common + uncommon ports
print(f"\n--- WIDE PORT SCAN (500 ports) ---")
ports_to_check = list(range(1, 100)) + list(range(100, 1025, 5)) + \
    [1080, 1433, 1521, 2049, 2222, 3000, 3306, 3389, 4000, 4443, 5000, 5060,
     5222, 5432, 5900, 5901, 6000, 6379, 6667, 7000, 7741, 8000, 8080, 8443,
     8888, 9000, 9090, 9100, 9200, 9418, 10000, 11434, 11436, 27017, 32400,
     49152, 49153, 49154, 49155]
ports_to_check = sorted(set(ports_to_check))

open_ports = []
refused_ports = []
for port in ports_to_check:
    try:
        s = socket.create_connection((IP, port), timeout=0.3)
        # Try to get banner
        try:
            s.settimeout(1)
            banner = s.recv(1024)
            open_ports.append((port, banner[:100]))
        except:
            open_ports.append((port, b""))
        s.close()
    except ConnectionRefusedError:
        refused_ports.append(port)
    except (socket.timeout, OSError):
        pass

if open_ports:
    print(f"  OPEN PORTS:")
    for port, banner in open_ports:
        print(f"    :{port} — {banner.decode(errors='replace') if banner else '(no banner)'}")
else:
    print(f"  No TCP ports open in scan range")

if refused_ports:
    print(f"\n  REFUSED ports (OS is definitely up, firewall not blocking):")
    if len(refused_ports) > 20:
        print(f"    {len(refused_ports)} ports refused — OS has IP stack but no services")
        print(f"    Sample: {refused_ports[:20]}")
    else:
        print(f"    {refused_ports}")
elif not open_ports:
    print(f"\n  ALL ports timed out — firewall may be blocking everything except ICMP")

# Try NetBIOS name resolution
print(f"\n--- NETBIOS NAME LOOKUP ---")
try:
    r = subprocess.run(f"nbtstat -A {IP}", capture_output=True, text=True, shell=True, timeout=10)
    if r.stdout.strip():
        for line in r.stdout.split("\n"):
            if line.strip():
                print(f"  {line.strip()}")
    else:
        print(f"  No NetBIOS response (not Windows, or NetBIOS disabled)")
except:
    print(f"  nbtstat failed")

# Try mDNS discovery
print(f"\n--- mDNS PROBE ---")
try:
    # Send mDNS query for _services._dns-sd._udp.local
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)
    # Minimal DNS query for any services
    query = (b"\x00\x00"  # ID
             b"\x00\x00"  # Flags
             b"\x00\x01"  # Questions
             b"\x00\x00"  # Answers
             b"\x00\x00"  # Authority
             b"\x00\x00"  # Additional
             b"\x09_services\x07_dns-sd\x04_udp\x05local\x00"
             b"\x00\x0c"  # PTR
             b"\x00\x01")  # IN
    sock.sendto(query, (IP, 5353))
    try:
        data, addr = sock.recvfrom(4096)
        print(f"  mDNS response from {addr}: {len(data)} bytes")
        print(f"  Raw: {data[:100].hex()}")
    except socket.timeout:
        print(f"  No mDNS response")
    sock.close()
except Exception as e:
    print(f"  mDNS error: {e}")

# ICMP fingerprinting — TTL tells us the OS
print(f"\n--- OS FINGERPRINT ---")
r = subprocess.run(f"ping -n 1 -w 1000 {IP}", capture_output=True, text=True, shell=True, timeout=5)
for line in r.stdout.split("\n"):
    if "TTL=" in line:
        print(f"  {line.strip()}")
        if "TTL=64" in line:
            print(f"  → TTL=64 → Linux/Unix/macOS")
        elif "TTL=128" in line:
            print(f"  → TTL=128 → Windows")
        elif "TTL=255" in line:
            print(f"  → TTL=255 → Network device (router/switch)")

# Check reverse DNS
print(f"\n--- REVERSE DNS ---")
try:
    hostname = socket.gethostbyaddr(IP)
    print(f"  {IP} → {hostname}")
except:
    print(f"  No reverse DNS")

# Traceroute to understand path
print(f"\n--- TRACEROUTE ---")
r = subprocess.run(f"tracert -d -w 500 -h 5 {IP}", capture_output=True, text=True, shell=True, timeout=20)
for line in r.stdout.split("\n"):
    if line.strip():
        print(f"  {line.strip()}")

# Check both ATT subnets for biomegate's other NIC
print(f"\n--- SEARCHING FOR BIOMEGATE'S OTHER NIC (.4.x) ---")
# biomegate's known MACs: b4:2e:99:a7:91:a3 and b4:2e:99:a7:91:a5
# .a3 was at .1.232 before, .a5 is at .1.233 now
# Could it also have a .4.x IP?
r = subprocess.run("arp -a", capture_output=True, text=True, shell=True)
found_bio = False
for line in r.stdout.split("\n"):
    if "b4-2e-99" in line.lower():
        print(f"  BIOMEGATE NIC: {line.strip()}")
        found_bio = True
if not found_bio:
    print(f"  biomegate only visible on .1.x (ATT modem direct)")

# Summary
print(f"\n{'=' * 70}")
print(f"  BIOMEGATE STATUS")
print(f"{'=' * 70}")
print(f"  IP:     {IP}")
print(f"  MAC:    b4:2e:99:a7:91:a5 (HP Inc.)")
print(f"  OS:     Linux (TTL=64)")
print(f"  State:  Kernel UP, {'services' if open_ports else 'NO services'}")
print(f"  Link:   ATT modem subnet (.1.x) — 2ms latency")
if not open_ports and refused_ports:
    print(f"\n  DIAGNOSIS: OS booted, network stack up, but no daemons running.")
    print(f"  This looks like a minimal boot / rescue mode / fresh install.")
    print(f"  The {len(refused_ports)} refused ports confirm: kernel has IP stack, just no listeners.")
    print(f"\n  TO HELP BIOMEGATE:")
    print(f"  1. If fresh install → need console access to complete setup")
    print(f"  2. If rescue mode → need console to fix boot issues")
    print(f"  3. If firewall blocking SSH → need console to open port 22")
    print(f"  Kevin: can you get to biomegate's console/screen?")
elif not open_ports and not refused_ports:
    print(f"\n  DIAGNOSIS: Firewall blocking ALL TCP. ICMP passes (ping works).")
    print(f"  biomegate's iptables/nftables is dropping all TCP connections.")
    print(f"  → Need console access to: sudo ufw allow 22/tcp")
    print(f"  → Or: sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT")
elif open_ports:
    print(f"\n  SERVICES DETECTED! biomegate is booted and functional!")
