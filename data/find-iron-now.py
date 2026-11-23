#!/usr/bin/env python3
"""Find ironGate after rewire — scan from ALL vantage points"""
import paramiko, socket, subprocess, concurrent.futures, time

KNOWN = {'.1':'router', '.2':'mikrotik', '.147':'northGate', '.244':'eastGate-wifi', '.246':'northGate-wifi'}

def scan_port(ip, port, timeout=1):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
        s.close()
        return True
    except:
        return False

def ping_local(ip):
    try:
        r = subprocess.run(['ping','-n','1','-w','500',ip], capture_output=True, text=True, timeout=3)
        return f'Reply from {ip}' in r.stdout and 'Destination host unreachable' not in r.stdout
    except:
        return False

# === LOCAL SWEEP ===
print("=== SWEEP FROM blueGate (local) ===")
alive = []
def check_ip(ip):
    if ping_local(ip):
        tag = KNOWN.get(f'.{ip.split(".")[-1]}', '')
        ports = []
        for p in [22, 80, 443, 3389, 8080, 8443, 11434]:
            if scan_port(ip, p): ports.append(str(p))
        return (ip, tag, ports)
    return None

with concurrent.futures.ThreadPoolExecutor(max_workers=80) as ex:
    ips = [f'192.168.4.{i}' for i in range(1,255)]
    for r in ex.map(check_ip, ips):
        if r:
            ip, tag, ports = r
            mark = f" ({tag})" if tag else " <<< NEW"
            print(f"  {ip}{mark} ports: {ports}")
            alive.append(r)

# === SWEEP 1.x ===
print("\n=== ATT SUBNET (192.168.1.x) ===")
with concurrent.futures.ThreadPoolExecutor(max_workers=80) as ex:
    ips = [f'192.168.1.{i}' for i in range(1,255)]
    for r in ex.map(check_ip, ips):
        if r:
            ip, tag, ports = r
            print(f"  {ip} ports: {ports}")

# === SWEEP 8.x (router admin) ===
print("\n=== ROUTER ADMIN SUBNET (192.168.8.x) ===")
with concurrent.futures.ThreadPoolExecutor(max_workers=80) as ex:
    ips = [f'192.168.8.{i}' for i in range(1,255)]
    for r in ex.map(check_ip, ips):
        if r:
            ip, tag, ports = r
            print(f"  {ip} ports: {ports}")

# === ASK NORTHGATE ===
print("\n=== SWEEP FROM northGate (.147) ===")
try:
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect('192.168.4.147', username='kevin', timeout=5)
    
    # ARP table
    _, o, _ = c.exec_command('ip neigh show', timeout=5)
    print("  ARP table:")
    for line in o.read().decode().strip().split('\n'):
        if line.strip():
            print(f"    {line.strip()}")
    
    # Ping sweep from northGate
    cmd = """for i in $(seq 1 254); do ping -c1 -W1 192.168.4.$i &>/dev/null && echo "ALIVE 192.168.4.$i" & done; wait"""
    _, o, _ = c.exec_command(cmd, timeout=30)
    results = o.read().decode().strip()
    print("  Ping sweep:")
    for line in results.split('\n'):
        if line.strip():
            octet = line.strip().split('.')[-1] if '.' in line else ''
            tag = KNOWN.get(f'.{octet}', '')
            mark = f" ({tag})" if tag else " <<< NEW"
            print(f"    {line.strip()}{mark}")
    c.close()
except Exception as e:
    print(f"  northGate error: {e}")

# === ASK EASTGATE ===
print("\n=== SWEEP FROM eastGate (.244) ===")
try:
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect('192.168.4.244', username='gaia', timeout=5)
    
    # Show all interfaces
    _, o, _ = c.exec_command('ip -4 addr show | grep inet', timeout=5)
    print("  Interfaces:")
    for line in o.read().decode().strip().split('\n'):
        print(f"    {line.strip()}")
    
    # ARP table
    _, o, _ = c.exec_command('ip neigh show', timeout=5)
    print("  ARP table:")
    for line in o.read().decode().strip().split('\n'):
        if line.strip():
            print(f"    {line.strip()}")
    
    # Ping sweep from eastGate
    cmd = """for i in $(seq 1 254); do ping -c1 -W1 192.168.4.$i &>/dev/null && echo "ALIVE 192.168.4.$i" & done; wait"""
    _, o, _ = c.exec_command(cmd, timeout=30)
    results = o.read().decode().strip()
    print("  Ping sweep:")
    for line in results.split('\n'):
        if line.strip():
            octet = line.strip().split('.')[-1] if '.' in line else ''
            tag = KNOWN.get(f'.{octet}', '')
            mark = f" ({tag})" if tag else " <<< NEW"
            print(f"    {line.strip()}{mark}")
    
    # Check all subnets eastGate is on
    _, o, _ = c.exec_command('ip route', timeout=5)
    print("  Routes:")
    for line in o.read().decode().strip().split('\n'):
        print(f"    {line.strip()}")
    c.close()
except Exception as e:
    print(f"  eastGate error: {e}")

print("\n=== DONE ===")
print("Looking for ironGate: i9-14900K, Pop!_OS, was .237")
print("Any 'NEW' entry above could be ironGate")
