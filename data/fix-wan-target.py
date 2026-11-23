#!/usr/bin/env python3
"""Fix WAN forwards to point to eastGate .213 (wired) not .244 (WiFi gone)

eastGate interfaces:
  eno1 (wired):    192.168.4.213  ← ALIVE on LAN, spine-to-spine
  wlp0s20f3 (WiFi): 192.168.1.220  ← jumped to ATT subnet, NOT on LAN
  .244: GONE from LAN

Router needs to forward to .213, not .244
"""

import paramiko

# First: check if router can reach .213
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.1', username='root', password='***', timeout=10)

def run(cmd):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=10)
    return stdout.read().decode('utf-8', errors='replace').strip()

print('=== ROUTER → EASTGATE .213 ===')
# First arping to populate ARP
out = run('arping -I br-lan -c 2 192.168.4.213 2>&1')
print(f'arping .213: {out}')

out = run('ping -c 2 -W 2 192.168.4.213 2>&1 | tail -3')
up = '1 received' in out or '2 received' in out
print(f'ping .213: {"UP" if up else "DOWN"} — {out}')

if not up:
    # Try adding a static ARP entry or route
    print('Trying static ARP...')
    # Get eastGate's wired MAC from northGate connection
    
print()
print('=== UPDATE PORT FORWARDS → .213 ===')

# Delete current forwards
out = run('uci show firewall | grep "redirect.*name"')
print(f'Current: {out}')

# Count redirects
lines = [l for l in out.split('\n') if l.strip()]
for i in range(len(lines)-1, -1, -1):
    run(f'uci delete firewall.@redirect[{i}]')
    print(f'Deleted redirect[{i}]')

# Add new forwards pointing to .213
EASTGATE = '192.168.4.213'

run(f"""
uci add firewall redirect
uci set firewall.@redirect[-1].name='WAN-HTTP-VERTICAL'
uci set firewall.@redirect[-1].src='wan'
uci set firewall.@redirect[-1].src_dport='80'
uci set firewall.@redirect[-1].dest='lan'
uci set firewall.@redirect[-1].dest_ip='{EASTGATE}'
uci set firewall.@redirect[-1].dest_port='80'
uci set firewall.@redirect[-1].proto='tcp'
uci set firewall.@redirect[-1].target='DNAT'
uci set firewall.@redirect[-1].enabled='1'
""")
print(f'Added WAN-HTTP-VERTICAL (80 → {EASTGATE}:80)')

run(f"""
uci add firewall redirect
uci set firewall.@redirect[-1].name='WAN-HTTPS-VERTICAL'
uci set firewall.@redirect[-1].src='wan'
uci set firewall.@redirect[-1].src_dport='443'
uci set firewall.@redirect[-1].dest='lan'
uci set firewall.@redirect[-1].dest_ip='{EASTGATE}'
uci set firewall.@redirect[-1].dest_port='443'
uci set firewall.@redirect[-1].proto='tcp'
uci set firewall.@redirect[-1].target='DNAT'
uci set firewall.@redirect[-1].enabled='1'
""")
print(f'Added WAN-HTTPS-VERTICAL (443 → {EASTGATE}:443)')

run('uci commit firewall')
run('/etc/init.d/firewall reload 2>&1')
print('Committed + reloaded')

# Verify
print()
print('=== VERIFY ===')
print(run('uci show firewall | grep "redirect.*name\\|redirect.*dest_ip\\|redirect.*dest_port\\|redirect.*src_dport"'))

# Check iptables
print()
print(run('iptables -t nat -L PREROUTING -n 2>/dev/null | grep -E "DNAT.*tcp.*dpt:(80|443)"'))

c.close()

# Now check dromedary on eastGate via .213
print()
print('=== CHECK DROMEDARY ON .213 ===')
c2 = paramiko.SSHClient()
c2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c2.connect('192.168.4.213', username='eastgate', password='eastgate', timeout=5)
def run2(cmd):
    stdin, stdout, stderr = c2.exec_command(cmd, timeout=10)
    return stdout.read().decode('utf-8', errors='replace').strip()

# Is dromedary listening on .213?
print(run2('ss -tlnp | grep -E ":80 |:443 |:8080 |:8443 "'))
print()
# Is dromedary bound to 0.0.0.0 or specific IP?
print(run2('ss -tlnp | grep dromedary'))
print(run2('ss -tlnp | grep python'))

c2.close()
print()
print('=== WAN VERTICAL: .213 TARGET SET ===')
