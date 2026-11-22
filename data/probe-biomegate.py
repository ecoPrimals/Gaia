"""probe-biomegate.py — Deep probe of .4.248 (possible biomegate in boot loop)."""
import socket
import subprocess
import time

IP = "192.168.4.248"
MAC = "c8:5e:a9:c9:6f:80"

print(f"=== DEEP PROBE: {IP} (MAC {MAC}) ===")
print(f"OUI c8:5e:a9 — checking manufacturer...")

# Full port scan — boot loop devices might have random ports briefly open
print("\n--- FULL PORT SCAN (top 100 ports) ---")
common = [
    20, 21, 22, 23, 25, 53, 67, 68, 69, 80, 110, 111, 123, 135, 137, 138, 139,
    143, 161, 179, 389, 443, 445, 465, 514, 515, 548, 554, 587, 631, 636,
    873, 993, 995, 1080, 1433, 1434, 1521, 1723, 2049, 2222, 3000, 3306,
    3389, 4000, 5000, 5060, 5222, 5432, 5900, 5901, 6000, 6379, 6667,
    7741, 8000, 8080, 8443, 8888, 9090, 9100, 9200, 9418, 11434, 27017,
]

open_ports = []
for port in common:
    try:
        s = socket.create_connection((IP, port), timeout=0.3)
        s.close()
        open_ports.append(port)
        print(f"  :{port} OPEN!")
    except (ConnectionRefusedError, ConnectionResetError):
        # Refused = host is UP but port closed (good sign!)
        print(f"  :{port} refused (host alive, port closed)")
        if port == common[0]:
            print("  ** Connection REFUSED means the OS is UP! **")
    except socket.timeout:
        pass
    except OSError:
        pass

if open_ports:
    print(f"\nOpen ports: {open_ports}")
else:
    print("\nNo ports open — checking if host responds at all...")

# Try different protocols
print("\n--- UDP PROBE ---")
for port in [67, 68, 123, 137, 161, 5353]:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        s.sendto(b"\x00" * 8, (IP, port))
        try:
            data, addr = s.recvfrom(1024)
            print(f"  UDP :{port} responded! ({len(data)} bytes from {addr})")
        except socket.timeout:
            pass
        s.close()
    except:
        pass

# Monitor for 15 seconds — boot loop devices appear and disappear
print("\n--- BOOT LOOP MONITOR (15s) ---")
print("  Pinging every 2s to detect reboot cycling...")
up_count = 0
down_count = 0
transitions = []
last_state = None

for i in range(8):
    r = subprocess.run(f"ping -n 1 -w 500 {IP}", capture_output=True, text=True, shell=True, timeout=3)
    alive = "TTL=" in r.stdout
    state = "UP" if alive else "DOWN"
    if last_state is not None and state != last_state:
        transitions.append(f"  t={i*2}s: {last_state} → {state}")
    if alive:
        up_count += 1
    else:
        down_count += 1
    last_state = state
    print(f"  t={i*2:2d}s: {state}")
    time.sleep(2)

print(f"\n  Result: UP {up_count}/8, DOWN {down_count}/8")
if transitions:
    print(f"  TRANSITIONS (boot loop indicator):")
    for t in transitions:
        print(t)
    print("  ** BOOT LOOP DETECTED! **")
elif up_count == 8:
    print("  STABLE UP — not in boot loop, just slow to start services")
elif down_count == 8:
    print("  STABLE DOWN — might have powered off")
else:
    print("  INTERMITTENT — possible boot loop")

# OUI lookup
print(f"\n--- OUI: c8:5e:a9 ---")
print("  Checking against known Gaia ecosystem MACs...")
known = {
    "bc:fc:e7:ea:d9:34": "northGate (from DHCP DUID)",
    "b4:2e:99:a7:91:a3": "biomegate (ATT device list)",
    "c8:5e:a9:c9:6f:80": "THIS device — appeared at .4.248",
    "1c:86:0b:37:63:19": "eastGate (Intel NIC)",
    "04:f4:1c:e6:7c:e8": "MikroTik",
    "4c:50:dd:9b:c1:ec": "sporeGate",
}
for mac, name in known.items():
    print(f"  {mac} = {name}")
