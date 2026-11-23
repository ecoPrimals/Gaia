#!/usr/bin/env python3
"""Read the organism.html JS to see what fields it expects."""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)

HUD = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'

# Get the JS section of organism.html
stdin, stdout, stderr = ssh.exec_command(f'sed -n "/<script/,/<\\/script>/p" {HUD}/organism.html 2>/dev/null')
js = stdout.read().decode()
print(f'=== ORGANISM JS ({len(js)} chars) ===')
print(js[:5000])
print('...')
print(js[-2000:] if len(js) > 5000 else '')

ssh.close()
