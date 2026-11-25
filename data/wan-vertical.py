#!/usr/bin/env python3
"""WAN VERTICAL SOLVE — add minimal port forwards for web traffic

The vertical team (northGate/Cursor) gets LOW to HIGH in the WAN clouds.
eastGate is the lateral team (LAN).

DNS already resolves:
  nestgate.io    → [home IP]
  primals.eco    → [home IP]
  hud.primals.eco → [home IP]

We need: router port 80+443 → eastGate .244 (dromedary)
That's 2 forwards, not 10 torpedoes.
"""

import paramiko

ROUTER_IP = '192.168.4.1'
ROUTER_USER = 'root'
ROUTER_PASS = '***'
EASTGATE_IP = '192.168.4.244'

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())

print('=== WAN VERTICAL SOLVE ===')
print()

# Connect directly to router from northGate
print(f'Connecting to router at {ROUTER_IP}...')
c.connect(ROUTER_IP, username=ROUTER_USER, password=ROUTER_PASS, timeout=10)
print('Connected to router')

def run(cmd):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=15)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    return out, err

# Check if eastGate is reachable from router
print()
print('=== CHECK EASTGATE FROM ROUTER ===')
out, _ = run(f'ping -c 1 -W 2 {EASTGATE_IP}')
if '1 received' in out or 'bytes from' in out:
    print(f'eastGate {EASTGATE_IP}: REACHABLE from router')
else:
    print(f'eastGate {EASTGATE_IP}: NOT reachable from router')
    print(out)

# Check if dromedary is responding on eastGate
out, _ = run(f'wget -q -O /dev/null --timeout=3 -S http://{EASTGATE_IP}:80/ 2>&1 | head -3')
print(f'eastGate :80 → {out}')
out, _ = run(f'wget -q -O /dev/null --timeout=3 -S http://{EASTGATE_IP}:8443/ 2>&1 | head -3')
print(f'eastGate :8443 → {out}')

# Check current port forwards
print()
print('=== CURRENT PORT FORWARDS ===')
out, _ = run('uci show firewall | grep redirect | grep "name\\|src_dport\\|dest_ip\\|dest_port"')
if out:
    print(out)
else:
    print('NONE — all torpedoes drained')

# Check current WAN IP
print()
print('=== WAN IP ===')
out, _ = run('ip addr show eth1 2>/dev/null | grep "inet "')
print(f'Router WAN: {out.strip()}')

# Add 2 minimal port forwards: HTTP (80) and HTTPS (443)
print()
print('=== ADDING WAN VERTICAL FORWARDS ===')

# HTTP: port 80 → eastGate .244:80 (dromedary)
out, err = run(f'''
uci add firewall redirect
uci set firewall.@redirect[-1].name='WAN-HTTP-VERTICAL'
uci set firewall.@redirect[-1].src='wan'
uci set firewall.@redirect[-1].src_dport='80'
uci set firewall.@redirect[-1].dest='lan'
uci set firewall.@redirect[-1].dest_ip='{EASTGATE_IP}'
uci set firewall.@redirect[-1].dest_port='80'
uci set firewall.@redirect[-1].proto='tcp'
uci set firewall.@redirect[-1].target='DNAT'
uci set firewall.@redirect[-1].enabled='1'
''')
print(f'Added WAN-HTTP-VERTICAL (80 → {EASTGATE_IP}:80)')

# HTTPS: port 443 → eastGate .244:443 (dromedary TLS)
out, err = run(f'''
uci add firewall redirect
uci set firewall.@redirect[-1].name='WAN-HTTPS-VERTICAL'
uci set firewall.@redirect[-1].src='wan'
uci set firewall.@redirect[-1].src_dport='443'
uci set firewall.@redirect[-1].dest='lan'
uci set firewall.@redirect[-1].dest_ip='{EASTGATE_IP}'
uci set firewall.@redirect[-1].dest_port='443'
uci set firewall.@redirect[-1].proto='tcp'
uci set firewall.@redirect[-1].target='DNAT'
uci set firewall.@redirect[-1].enabled='1'
''')
print(f'Added WAN-HTTPS-VERTICAL (443 → {EASTGATE_IP}:443)')

# Commit and reload
print()
print('=== COMMIT + RELOAD ===')
out, _ = run('uci commit firewall')
print(f'Commit: {out or "OK"}')
out, _ = run('/etc/init.d/firewall reload 2>&1')
print(f'Reload: {out[:200] if out else "OK"}')

# Verify
print()
print('=== VERIFY ===')
out, _ = run('uci show firewall | grep redirect | grep "name"')
print(out)

# Check from router if WAN works (loopback test)
print()
out, _ = run('iptables -t nat -L PREROUTING -n | grep -E "80|443"')
print('iptables PREROUTING:')
print(out)

c.close()
print()
print('=== WAN VERTICAL ACTIVE ===')
print('nestgate.io:80  → router → eastGate:80  (dromedary)')
print('nestgate.io:443 → router → eastGate:443 (dromedary TLS)')
print('primals.eco:80  → router → eastGate:80  (dromedary)')
print('primals.eco:443 → router → eastGate:443 (dromedary TLS)')
