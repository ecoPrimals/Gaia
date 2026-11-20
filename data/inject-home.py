#!/usr/bin/env python3
"""Inject GAIA@HOME unified bubble into eastGate — all paths serve it"""

import paramiko
import os

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10)

def run(cmd):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=10)
    return stdout.read().decode('utf-8', errors='replace').strip()

# Read the HTML file
html_path = os.path.join(os.path.dirname(__file__), 'gaia-home.html')
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Target directories where the web servers serve from
targets = [
    '/home/eastgate/.local/share/gaia/data',      # gaia-web :8080 /data/
    '/home/eastgate/.local/share/gaia',            # gaia-web :8080 /
    '/opt/Gaia/infra/hud/site/public/data',        # git-tracked data
    '/opt/Gaia/data',                              # git data
]

print('=== INJECTING GAIA@HOME ===')
sftp = c.open_sftp()

for tgt in targets:
    exists = run(f'test -d {tgt} && echo YES || echo NO')
    if exists == 'YES':
        path = f'{tgt}/gaia-home.html'
        try:
            with sftp.open(path, 'w') as f:
                f.write(html)
            print(f'  INJECTED: {path}')
        except Exception as e:
            print(f'  FAILED: {path} — {e}')
    else:
        print(f'  SKIP: {tgt} (not found)')

sftp.close()

# Verify served
print()
print('=== VERIFY SERVED ===')
for port, name in [(8080, 'gaia-web'), (80, 'dromedary'), (8443, 'gate')]:
    for path in ['/data/gaia-home.html', '/gaia-home.html', '/home']:
        code = run(f'curl -s -o /dev/null -w "%{{http_code}}" http://127.0.0.1:{port}{path} 2>/dev/null')
        if code == '200':
            print(f'  :{port}{path} -> HTTP {code} ({name}) ✓')

# Also check if there's an index route we can hook into
print()
print('=== CURRENT INDEX ROUTES ===')
# Check what gaia-web Python script serves
print(run('ps aux | grep "python3.*8080" | grep -v grep | head -3'))
print()
# Find the gaia-web script
gw_path = run("find /home/eastgate -name '*.py' -path '*/gaia*' 2>/dev/null | xargs grep -l '8080' 2>/dev/null | head -5")
print(f'gaia-web scripts: {gw_path}')
print()
# Show the serve root
if gw_path:
    first = gw_path.split('\n')[0]
    print(f'=== {first} (first 50 lines) ===')
    print(run(f'head -50 {first}'))

c.close()
print()
print('=== DONE ===')
