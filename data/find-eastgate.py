#!/usr/bin/env python3
"""Find eastGate — it's unreachable at .244 from the router"""

import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.1', username='root', password='ExoticPanda714!!', timeout=10)

def run(cmd):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=10)
    return stdout.read().decode('utf-8', errors='replace').strip()

# Check ARP table for eastGate
print('=== ARP TABLE ===')
print(run('cat /proc/net/arp'))

print()
print('=== DHCP LEASES ===')
print(run('cat /tmp/dhcp.leases'))

print()
print('=== PING SWEEP — .213, .244, .103, .131 ===')
for ip in ['192.168.4.213', '192.168.4.244', '192.168.4.103', '192.168.1.131']:
    out = run(f'ping -c 1 -W 1 {ip} 2>&1 | tail -2')
    status = 'UP' if '1 received' in out else 'DOWN'
    print(f'  {ip}: {status}')

print()
print('=== CONNECTED WIFI CLIENTS ===')
print(run('iwinfo wlan0 assoclist 2>/dev/null | head -20'))
print(run('iwinfo wlan1 assoclist 2>/dev/null | head -20'))

print()
print('=== PORT FORWARDS (DETAIL) ===')
print(run('uci show firewall | grep redirect'))

# Clean up conflicting old HUD rules
print()
print('=== CLEANUP OLD HUD FORWARDS ===')
# List all redirects
out = run('uci show firewall | grep "redirect.*name"')
print('Current redirects:')
print(out)

# Delete old HUD-80 (maps 80→8080, conflicts with our 80→80)
# and HUD-8080 (maps 8080→8080, unnecessary)
lines = out.split('\n')
# Find indices to delete (reverse order)
to_delete = []
for line in lines:
    if 'HUD-8080' in line or 'HUD-80' in line:
        idx = line.split('[')[1].split(']')[0]
        to_delete.append(int(idx))
        print(f'  Will delete redirect[{idx}]: {line.split("=")[1]}')

for idx in sorted(to_delete, reverse=True):
    run(f'uci delete firewall.@redirect[{idx}]')
    print(f'  Deleted redirect[{idx}]')

if to_delete:
    run('uci commit firewall')
    run('/etc/init.d/firewall reload 2>&1')
    print('Committed + reloaded')

# Final state
print()
print('=== FINAL PORT FORWARDS ===')
print(run('uci show firewall | grep "redirect.*name"'))

c.close()
