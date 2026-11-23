#!/usr/bin/env python3
"""Make GAIA@HOME the ROOT page — gaia/host/player/user replaces localhost"""

import paramiko
import os

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.213', username='eastgate', password='eastgate', timeout=10)

def run(cmd):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=10)
    return stdout.read().decode('utf-8', errors='replace').strip()

html_path = os.path.join(os.path.dirname(__file__), 'gaia-home.html')
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

sftp = c.open_sftp()

# Inject to ALL data directories
data_targets = [
    '/home/eastgate/.local/share/gaia/data/gaia-home.html',
    '/opt/Gaia/infra/hud/site/public/data/gaia-home.html',
    '/opt/Gaia/data/gaia-home.html',
]

for path in data_targets:
    try:
        with sftp.open(path, 'w') as f:
            f.write(html)
        print(f'  DATA: {path}')
    except Exception as e:
        print(f'  SKIP: {path} — {e}')

# NOW make it the INDEX — gaia-web serves from ~/.local/share/gaia/
# Replace or create index.html there so / serves GAIA@HOME
index_targets = [
    '/home/eastgate/.local/share/gaia/index.html',        # gaia-web root /
    '/home/eastgate/.local/share/gaia/home.html',          # /home.html
]

for path in index_targets:
    try:
        with sftp.open(path, 'w') as f:
            f.write(html)
        print(f'  INDEX: {path}')
    except Exception as e:
        print(f'  SKIP: {path} — {e}')

# Also inject to dromedary's static dir and gate's static dir
dromedary_targets = [
    '/home/eastgate/Development/ecoPrimals/primals/GaiaGate/data/gaia-home.html',
    '/home/eastgate/Development/ecoPrimals/primals/GaiaGate/data/body/gaia-home.html',
    '/home/eastgate/Development/ecoPrimals/runtime/membrane/gaia-home.html',
]

for path in dromedary_targets:
    try:
        with sftp.open(path, 'w') as f:
            f.write(html)
        print(f'  GATE: {path}')
    except Exception as e:
        print(f'  SKIP: {path} — {e}')

sftp.close()

# Verify ALL access points
print()
print('=== VERIFICATION ===')
checks = [
    (8080, '/data/gaia-home.html', 'gaia-web data'),
    (8080, '/index.html', 'gaia-web index'),
    (8080, '/home.html', 'gaia-web /home'),
    (80,   '/data/gaia-home.html', 'dromedary data'),
    (80,   '/home', 'dromedary /home'),
    (8443, '/data/gaia-home.html', 'gate data'),
    (8443, '/home', 'gate /home'),
]

for port, path, name in checks:
    code = run(f'curl -s -o /dev/null -w "%{{http_code}}" http://127.0.0.1:{port}{path} 2>/dev/null')
    marker = 'YES' if code == '200' else 'no'
    print(f'  :{port}{path:30s} HTTP {code}  ({name}) {marker}')

# Show what gaia-web serves as its root
print()
print('=== ROOT INDEX ===')
root_title = run('curl -s http://127.0.0.1:8080/ 2>/dev/null | grep -o "<title>[^<]*</title>"')
idx_title = run('curl -s http://127.0.0.1:8080/index.html 2>/dev/null | grep -o "<title>[^<]*</title>"')
home_title = run('curl -s http://127.0.0.1:8080/home.html 2>/dev/null | grep -o "<title>[^<]*</title>"')
print(f'  :8080/           → {root_title}')
print(f'  :8080/index.html → {idx_title}')
print(f'  :8080/home.html  → {home_title}')

c.close()
print()
print('=== GAIA@HOME IS HOME ===')
