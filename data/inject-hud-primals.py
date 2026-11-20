#!/usr/bin/env python3
"""Inject GAIA@HOME into hud.primals.eco via dromedary static root"""

import paramiko
import os

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.213', username='eastgate', password='eastgate', timeout=10)

def run(cmd):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=10)
    return stdout.read().decode('utf-8', errors='replace').strip()

# The gaia-web root IS the dromedary static root
# (dromedary proxies to :8080 for these hostnames)
# We already replaced index.html there.

# But also copy to the gaia-web root explicitly
serve_root = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'
html_path = os.path.join(os.path.dirname(__file__), 'gaia-home.html')

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

sftp = c.open_sftp()

# Write as index.html (the ROOT page)
with sftp.open(f'{serve_root}/index.html', 'w') as f:
    f.write(html)
print(f'ROOT: {serve_root}/index.html')

# Also write as home.html and gaia-home.html
for name in ['home.html', 'gaia-home.html']:
    with sftp.open(f'{serve_root}/{name}', 'w') as f:
        f.write(html)
    print(f'ALIAS: {serve_root}/{name}')

# Write to data subdir too
with sftp.open(f'{serve_root}/data/gaia-home.html', 'w') as f:
    f.write(html)
print(f'DATA: {serve_root}/data/gaia-home.html')

sftp.close()

# Verify via dromedary with Host header
print()
print('=== VERIFY DROMEDARY SUBDOMAINS ===')
hosts = ['primals.eco', 'hud.primals.eco', 'gaia.primals.eco', 'senses.primals.eco']
for host in hosts:
    title = run(f'curl -s -H "Host: {host}" http://127.0.0.1:80/ 2>/dev/null | grep -o "<title>[^<]*</title>"')
    print(f'  {host:25s} → {title}')

# Also check hud.primals.eco/home and /data/gaia-home.html
for path in ['/home', '/gaia-home.html', '/data/gaia-home.html']:
    title = run(f'curl -s -H "Host: hud.primals.eco" http://127.0.0.1:80{path} 2>/dev/null | grep -o "<title>[^<]*</title>"')
    print(f'  hud.primals.eco{path:25s} → {title}')

c.close()
print()
print('=== HUD.PRIMALS.ECO TRIANGULATING ===')
