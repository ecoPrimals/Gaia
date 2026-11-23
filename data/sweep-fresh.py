#!/usr/bin/env python3
"""Fresh sweep + OUI lookup + ARP refresh"""
import subprocess, socket, concurrent.futures, urllib.request

def ping(ip):
    try:
        r = subprocess.run(['ping','-n','1','-w','600',ip], capture_output=True, text=True, timeout=3)
        if f'Reply from {ip}' in r.stdout and 'unreachable' not in r.stdout:
            for line in r.stdout.split('\n'):
                if 'TTL=' in line:
                    ttl = line.split('TTL=')[1].strip()
                    ms = line.split('time=')[1].split('ms')[0].strip() if 'time=' in line else '<1'
                    return (ip, ms, ttl)
    except: pass
    return None

print("=== FRESH SWEEP (all subnets) ===\n")
all_found = []
for subnet in ['192.168.4', '192.168.9', '192.168.8']:
    ips = [f'{subnet}.{i}' for i in range(1, 255)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=80) as ex:
        for r in ex.map(ping, ips):
            if r:
                all_found.append(r)
                print(f"  {r[0]:20s} {r[1]:>5s}ms TTL={r[2]}")

print(f"\nTotal: {len(all_found)} devices")

# Refresh ARP
print("\n=== FRESH ARP ===")
r = subprocess.run(['arp', '-a'], capture_output=True, text=True, timeout=5)
for line in r.stdout.split('\n'):
    if '192.168' in line and 'dynamic' in line.lower():
        print(f"  {line.strip()}")

# OUI lookup via macvendors.com for unknown MACs
print("\n=== OUI LOOKUP ===")
unknown_macs = {
    '50:0a:52': '.183',
    '1c:1b:0d': '.230',
}
for oui, ip in unknown_macs.items():
    mac_clean = oui.replace(':', '')
    try:
        req = urllib.request.Request(
            f'https://api.macvendors.com/{oui}',
            headers={'User-Agent': 'Gaia/1.0'}
        )
        r = urllib.request.urlopen(req, timeout=5)
        vendor = r.read().decode().strip()
        print(f"  {oui} ({ip}): {vendor}")
    except Exception as e:
        print(f"  {oui} ({ip}): lookup failed — {e}")

# Try ADB check on eastGate
print("\n=== ADB CHECK (via eastGate) ===")
try:
    import paramiko
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect('192.168.4.244', username='gaia', timeout=5, auth_timeout=8)
    
    # Check if ADB device is connected
    _, o, _ = c.exec_command('adb devices 2>/dev/null', timeout=5)
    out = o.read().decode().strip()
    print(f"  ADB devices: {out}")
    
    # Check eastGate ARP for more info
    _, o, _ = c.exec_command('ip neigh show | grep -v FAILED', timeout=5)
    out = o.read().decode().strip()
    print(f"  eastGate ARP:")
    for line in out.split('\n'):
        if line.strip():
            print(f"    {line.strip()}")
    
    # Check DHCP leases if available
    _, o, _ = c.exec_command('cat /var/lib/dhcp/dhclient.leases 2>/dev/null; cat /var/lib/NetworkManager/*.lease 2>/dev/null | head -30', timeout=5)
    out = o.read().decode().strip()
    if out:
        print(f"  DHCP leases: {out[:500]}")
    
    c.close()
except Exception as e:
    print(f"  eastGate SSH: {e}")
