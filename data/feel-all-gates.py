#!/usr/bin/env python3
"""FEEL ALL GATES — full mesh sweep after massive rewire"""
import subprocess, concurrent.futures, socket, time

KNOWN = {
    '192.168.4.1': 'router',
    '192.168.4.2': 'mikrotik', 
    '192.168.4.3': 'sporeGate',
    '192.168.4.100': 'blueGate',
    '192.168.4.107': 'graftGate',
    '192.168.4.147': 'northGate',
    '192.168.4.148': 'southGate',
    '192.168.4.176': 'deckGate',
    '192.168.4.200': 'EPSON',
    '192.168.4.237': 'ironGate',
    '192.168.4.244': 'eastGate',
    '192.168.4.246': 'northGate-wifi',
    '192.168.9.1': 'router-LAN2',
    '192.168.9.203': 'frameGate',
    '192.168.9.217': 'grapheneGate',
    '192.168.1.254': 'ATT-modem',
}

KEY_PORTS = [22, 80, 443, 3389, 5900, 8080, 8443, 11434, 11436, 21115, 21116]

def ping(ip):
    try:
        r = subprocess.run(['ping','-n','1','-w','500',ip], capture_output=True, text=True, timeout=3)
        if f'Reply from {ip}' in r.stdout and 'unreachable' not in r.stdout:
            for line in r.stdout.split('\n'):
                if 'TTL=' in line:
                    ttl = line.split('TTL=')[1].strip()
                    ms = line.split('time=')[1].split('ms')[0].strip() if 'time=' in line else '<1'
                    return (ip, ms, ttl)
    except: pass
    return None

def scan_ports(ip):
    open_ports = []
    for p in KEY_PORTS:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((ip, p))
            s.close()
            open_ports.append(p)
        except: pass
    return open_ports

def get_ssh_banner(ip):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((ip, 22))
        banner = s.recv(256).decode('utf-8', errors='replace').strip()
        s.close()
        return banner
    except:
        return None

print("=" * 70)
print("  GAIA MESH SWEEP — FEELING ALL GATES")
print("=" * 70)

subnets = {
    'LAN 1 (192.168.4.x)': [f'192.168.4.{i}' for i in range(1, 255)],
    'LAN 2 (192.168.9.x)': [f'192.168.9.{i}' for i in range(1, 255)],
    'ATT (192.168.1.x)': [f'192.168.1.{i}' for i in range(1, 255)],
    'Router Admin (192.168.8.x)': [f'192.168.8.{i}' for i in range(1, 255)],
}

all_alive = []

for subnet_name, ips in subnets.items():
    print(f"\n{'─' * 60}")
    print(f"  {subnet_name}")
    print(f"{'─' * 60}")
    
    found = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=80) as ex:
        for r in ex.map(ping, ips):
            if r:
                found.append(r)
    
    if not found:
        print("  (empty)")
        continue
    
    for ip, ms, ttl in sorted(found, key=lambda x: [int(o) for o in x[0].split('.')]):
        name = KNOWN.get(ip, '')
        tag = f" = {name}" if name else " <<< NEW GATE"
        
        # Port scan
        ports = scan_ports(ip)
        port_str = ', '.join(str(p) for p in ports) if ports else 'none'
        
        # SSH banner if port 22 open
        banner = ''
        if 22 in ports:
            b = get_ssh_banner(ip)
            if b:
                banner = f" [{b}]"
        
        print(f"  {ip:20s} {ms:>5s}ms TTL={ttl:3s}{tag}")
        print(f"    ports: {port_str}{banner}")
        all_alive.append((ip, name, ms, ttl, ports))

print(f"\n{'=' * 70}")
print(f"  TOTAL: {len(all_alive)} devices alive across all subnets")
print(f"{'=' * 70}")

# Summary of gates
print("\n  GATE STATUS:")
gate_names = ['eastGate', 'northGate', 'blueGate', 'ironGate', 'southGate', 
              'sporeGate', 'graftGate', 'deckGate', 'frameGate', 'grapheneGate']
found_gates = {name for _, name, _, _, _ in all_alive}
for g in gate_names:
    status = "ALIVE" if g in found_gates else "NOT FOUND"
    ip = next((ip for ip, name, _, _, _ in all_alive if name == g), '?')
    print(f"    {g:20s} {status:10s} {ip}")

# Check for NEW devices (potential westGate, milkyGate)
new_devices = [(ip, ms, ttl, ports) for ip, name, ms, ttl, ports in all_alive if not name]
if new_devices:
    print(f"\n  NEW DEVICES (potential westGate / milkyGate):")
    for ip, ms, ttl, ports in new_devices:
        print(f"    {ip} — {ms}ms TTL={ttl} ports={ports}")
