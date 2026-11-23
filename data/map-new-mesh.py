#!/usr/bin/env python3
"""Map the rewired mesh — ARP, MAC addresses, identify all new gates"""
import subprocess, socket

print("=" * 60)
print("  REWIRED MESH MAP — from northGate (.147)")
print("=" * 60)

# Our own ARP table
print("\n--- ARP TABLE ---")
r = subprocess.run(['arp', '-a'], capture_output=True, text=True, timeout=5)
for line in r.stdout.split('\n'):
    line = line.strip()
    if line and ('192.168' in line or 'dynamic' in line.lower()):
        print(f"  {line}")

# Our own interfaces
print("\n--- OUR INTERFACES ---")
r = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True, timeout=5)
for line in r.stdout.split('\n'):
    line = line.strip()
    if any(k in line.lower() for k in ['ipv4', 'physical', 'adapter', 'description']):
        print(f"  {line}")

# SSH banner for .183 with LONG timeout
print("\n--- SSH BANNER .183 (long timeout) ---")
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)
    s.connect(('192.168.4.183', 22))
    banner = s.recv(512)
    print(f"  Raw: {banner}")
    s.close()
except Exception as e:
    print(f"  {e}")

# Check .183 wider port scan
print("\n--- FULL PORT SCAN .183 ---")
for p in range(1, 1024):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.3)
        s.connect(('192.168.4.183', p))
        s.close()
        print(f"  Port {p}: OPEN")
    except:
        pass
for p in [3000, 3141, 3389, 5000, 5001, 5900, 8080, 8443, 9090, 11434, 11436]:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        s.connect(('192.168.4.183', p))
        s.close()
        print(f"  Port {p}: OPEN")
    except:
        pass

# Check .230 wider port scan
print("\n--- FULL PORT SCAN .230 ---")
for p in [22, 53, 80, 443, 548, 5353, 7000, 8082, 8080, 49152, 62078]:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        s.connect(('192.168.4.230', p))
        s.close()
        print(f"  Port {p}: OPEN")
    except:
        pass

# Check LAN 2 reachability via router
print("\n--- LAN 2 CHECK (via 192.168.9.1) ---")
for ip in ['192.168.9.1', '192.168.9.203', '192.168.9.217', '192.168.9.111']:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((ip, 80))
        s.close()
        print(f"  {ip}:80 OPEN")
    except Exception as e:
        pass
    r = subprocess.run(['ping', '-n', '1', '-w', '1000', ip], capture_output=True, text=True, timeout=3)
    if 'Reply from ' + ip in r.stdout:
        print(f"  {ip}: ALIVE")
    else:
        print(f"  {ip}: no reply")

print("\n--- DONE ---")
