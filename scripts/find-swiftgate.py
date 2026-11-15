import paramiko

east = paramiko.SSHClient()
east.set_missing_host_key_policy(paramiko.AutoAddPolicy())
east.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=5)
print('eastGate bridge connected\n')

# Full ARP + ping sweep from eastGate (sees both subnets)
print('=== eastGate ARP ===')
_, out, _ = east.exec_command('arp -a | grep -v incomplete', timeout=5)
print(out.read().decode())

# Check DHCP leases
print('=== DHCP leases ===')
_, out, _ = east.exec_command('cat /var/lib/dhcp/dhclient.leases 2>/dev/null | tail -20; cat /tmp/dhcp.leases 2>/dev/null', timeout=3)
print(out.read().decode()[:500])

# Ping sweep Gaia WiFi subnet for swiftGate
print('=== Ping sweep 192.168.9.x ===')
_, out, _ = east.exec_command('for i in $(seq 1 254); do ping -c1 -W1 192.168.9.$i &>/dev/null && echo "ALIVE: 192.168.9.$i"; done', timeout=60)
print(out.read().decode())

# Also check .4.148 — it's ALIVE and has a 1c:86:0b MAC (like ironGate .237 and eastGate .244)
# southGate was supposed to be .148 (iPhone) but 1c:86:0b is a server NIC!
print('=== .148 identity ===')
_, out, _ = east.exec_command('ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 -o BatchMode=yes root@192.168.4.148 "hostname; uname -a" 2>&1', timeout=8)
print(f'.148 SSH: {out.read().decode().strip()}')

# Check .181 (appeared in ARP, 90:82:c3 = Apple!)
print('\n=== .181 identity (Apple MAC!) ===')
_, out, _ = east.exec_command('ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 -o BatchMode=yes root@192.168.4.181 "hostname" 2>&1', timeout=5)
r181 = out.read().decode().strip()
print(f'.181 SSH: {r181}')

# .203 appeared! 14:13:33 = frameGate MAC!
print('\n=== .203 → frameGate! (14:13:33) ===')
_, out, _ = east.exec_command('ping -c1 -W1 192.168.4.203 2>/dev/null && echo ALIVE || echo DOWN', timeout=3)
print(f'.203 ping: {out.read().decode().strip()}')

east.close()
print('\nDone!')
