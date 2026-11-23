#!/usr/bin/env python3
"""Check Tor hidden service and RSS spine on eastGate"""

import paramiko

east = paramiko.SSHClient()
east.set_missing_host_key_policy(paramiko.AutoAddPolicy())
east.connect('192.168.1.131', username='eastgate', password='eastgate', timeout=10)

def run(cmd):
    stdin, stdout, stderr = east.exec_command(cmd, timeout=10)
    return stdout.read().decode('utf-8', errors='replace').strip()

print('=== TOR SERVICE ===')
print(run('systemctl status tor 2>/dev/null | head -15'))

print()
print('=== TORRC (non-comment lines) ===')
print(run("grep -v '^#' /etc/tor/torrc 2>/dev/null | grep -v '^$' | head -30"))

print()
print('=== HIDDEN SERVICE DIR ===')
print(run('ls -la /var/lib/tor/ 2>/dev/null'))

print()
print('=== TOR PROCESS ===')
print(run('ps aux | grep tor | grep -v grep'))

print()
print('=== TOR SOCKS PORT ===')
print(run('ss -tlnp | grep 9050'))

print()
print('=== RSS FEED LOCATION ===')
print(run('find /opt/Gaia -name feed.xml -type f 2>/dev/null | head -5'))
print(run('find /home -name feed.xml -type f 2>/dev/null | head -5'))
# Also check the data directory
print(run('ls -la /opt/Gaia/infra/hud/site/public/ 2>/dev/null | head -20'))

print()
print('=== DROMEDARY CONFIG ===')
print(run('systemctl cat dromedary.service 2>/dev/null | head -20'))
print()
print(run('ps aux | grep dromedary | grep -v grep'))

print()
print('=== HIDDEN SERVICE HOSTNAME ===')
# Check all possible locations
for path in ['/var/lib/tor/hidden_service/hostname',
             '/var/lib/tor/gaia_hidden/hostname',
             '/var/lib/tor/hs/hostname']:
    result = run(f'cat {path} 2>/dev/null')
    if result:
        print(f'{path}: {result[:30]}...')

# Check the actual tor data dir
print()
print('=== TOR DATA DIR CONTENTS ===')
print(run('find /var/lib/tor -type f -name hostname 2>/dev/null'))
print(run('ls -laR /var/lib/tor/ 2>/dev/null | head -30'))

east.close()
