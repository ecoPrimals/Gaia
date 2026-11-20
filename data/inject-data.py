#!/usr/bin/env python3
"""Inject walk-route and lake-balance to ALL data directories on eastGate"""

import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10)

def run(cmd):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=10)
    return stdout.read().decode('utf-8', errors='replace').strip()

print('=== PORT 8080 PROCESS ===')
print(run('ss -tlnp | grep 8080'))

print()
print('=== GAIA LOCAL DATA ===')
print(run('ls /home/eastgate/.local/share/gaia/data/*.json 2>/dev/null | head -20'))

print()
print('=== DROMEDARY TOML (first 40 lines) ===')
toml = run('cat /home/eastgate/Development/ecoPrimals/primals/dromedary/dromedary.toml 2>/dev/null | head -40')
print(toml[:800] if toml else 'not found')

print()
# Copy files to ALL relevant data directories
src_dir = '/opt/Gaia/infra/hud/site/public/data'
targets = [
    '/home/eastgate/.local/share/gaia/data',
    '/home/eastgate/Development/ecoPrimals/runtime/membrane',
    '/home/eastgate/Development/ecoPrimals/primals/GaiaGate/data',
    '/home/eastgate/Development/ecoPrimals/primals/GaiaGate/data/body',
]

for f in ['walk-route.json', 'lake-balance.json']:
    for tgt in targets:
        result = run(f'test -d {tgt} && cp {src_dir}/{f} {tgt}/{f} 2>&1 && echo OK || echo SKIP')
        status = 'INJECTED' if 'OK' in result else 'skipped'
        print(f'  {status}: {tgt}/{f}')

# Now test if the served data endpoint picks them up
print()
print('=== VERIFY SERVED ===')
for path in ['/data/walk-route.json', '/data/lake-balance.json', '/data/now.json']:
    code = run(f'curl -s -o /dev/null -w "%{{http_code}}" http://127.0.0.1:8080{path} 2>/dev/null')
    print(f'  :8080{path} -> HTTP {code}')

# Check via dromedary
for path in ['/data/walk-route.json', '/data/lake-balance.json']:
    code = run(f'curl -s -o /dev/null -w "%{{http_code}}" http://127.0.0.1:80{path} 2>/dev/null')
    print(f'  :80{path} -> HTTP {code}')
    code2 = run(f'curl -s -o /dev/null -w "%{{http_code}}" http://127.0.0.1:8443{path} 2>/dev/null')
    print(f'  :8443{path} -> HTTP {code2}')

c.close()
print()
print('=== DONE ===')
