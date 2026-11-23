#!/usr/bin/env python3
"""Patch the HUD copy of organism.html too."""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)
sftp = ssh.open_sftp()

path = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public/organism.html'

with sftp.open(path, 'r') as f:
    html = f.read().decode()

replacements = [
    ('id="sr-entities">27', 'id="sr-entities">13'),
    ('id="sr-ram">317', 'id="sr-ram">1,497'),
    ('id="sr-gpus">4', 'id="sr-gpus">7'),
    ('id="sr-models">93', 'id="sr-models">63'),
    ('27 entities', '13 entities'),
    ('317GB RAM', '1,497GB RAM'),
]

changed = 0
for old, new in replacements:
    if old in html:
        html = html.replace(old, new)
        changed += 1
        print(f'  {old} -> {new}')

if changed:
    with sftp.open(path, 'w') as f:
        f.write(html)
    print(f'\n  PATCHED HUD organism.html ({changed} changes)')
else:
    print('  No changes needed')

# Verify
stdin, stdout, stderr = ssh.exec_command(
    "curl -s http://localhost:8080/organism.html 2>/dev/null | grep -oE 'sr-(ram|entities|gpus)\">[^<]*'"
)
print(f'\n  :8080 verification:')
print(f'  {stdout.read().decode().strip()}')

sftp.close()
ssh.close()
