"""
POKE ATT BGW320 — HUMAN PUBLIC PIN: 579163
Configure IP passthrough so eastGate gets a real public IP
"""
import socket

# ATT modem is at 192.168.1.254 (accessible from router WAN side)
# But we might be able to reach it from LAN too
modem_ip = '192.168.1.254'

print('='*60)
print(f'  ATT BGW320 MODEM ({modem_ip})')
print(f'  HUMAN PUBLIC PIN: 579163')
print('='*60)

# Check if we can reach it from northGate
print('\nPort scan:')
ports = {80: 'HTTP', 443: 'HTTPS', 22: 'SSH', 8080: 'HTTP-ALT', 9443: 'HTTPS-ALT'}
for port, name in ports.items():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        result = s.connect_ex((modem_ip, port))
        s.close()
        if result == 0:
            print(f'  ✅ PORT {port} OPEN ({name})')
        else:
            print(f'  PORT {port} closed')
    except Exception as e:
        print(f'  PORT {port} error: {e}')

# Can we reach it?
print(f'\nPing:')
import subprocess
r = subprocess.run(['ping', '-n', '1', '-w', '2000', modem_ip], capture_output=True, text=True, timeout=5)
if 'Reply from' in r.stdout:
    print(f'  ALIVE!')
else:
    print(f'  Not reachable from northGate directly')
    print(f'  Need to go through router: ssh root@192.168.4.1 → curl http://192.168.1.254')

# Try via eastGate (router has WAN on 192.168.1.x)
print('\n--- Via eastGate → router → modem ---')
import paramiko
try:
    east = paramiko.SSHClient()
    east.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    east.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=5)
    
    # Router can reach modem
    _, out, _ = east.exec_command(
        'sshpass -p "***" ssh -o StrictHostKeyChecking=no root@192.168.4.1 '
        '"ping -c1 -W1 192.168.1.254 2>/dev/null && echo MODEM-ALIVE; '
        'curl -sk --connect-timeout 3 https://192.168.1.254/ 2>&1 | head -5" 2>&1',
        timeout=10
    )
    result = out.read().decode().strip()
    print(f'  Router→Modem: {result[:200]}')
    
    east.close()
except Exception as e:
    print(f'  Error: {e}')

print(f'''
=== ATT BGW320 IP PASSTHROUGH CONFIG ===

To configure (from browser):
1. Navigate to https://192.168.1.254
2. Login with Device Access Code: 579163
3. Go to: Firewall > IP Passthrough
4. Allocation Mode: Passthrough
5. Passthrough Mode: DHCPS-fixed
6. Device: select GL-MT6000 router MAC (94:83:c4:e0:62:b0)
7. Save

This gives the GL-MT6000 a REAL public IP instead of double-NAT.
eastGate then gets direct WAN access through the router.

Or from swiftGate console (if accessible):
  - Open browser → https://192.168.1.254
  - PIN: 579163
  - Configure passthrough
''')
