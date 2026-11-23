#!/usr/bin/env python3
"""Find all inkfish/Steam Frame/octopus/ludo/reef work on eastGate."""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10)

# Search for related files
searches = [
    'find /opt/Gaia -name "*inkfish*" -type f 2>/dev/null',
    'find /opt/Gaia -name "*octop*" -type f 2>/dev/null',
    'find /opt/Gaia -name "*ludo*" -type f 2>/dev/null',
    'find /opt/Gaia -name "*reef*" -type f 2>/dev/null',
    'find /opt/Gaia -name "*frame*" -type f 2>/dev/null',
    'find /opt/Gaia -name "*steam*" -type f 2>/dev/null',
    'find /opt/Gaia -name "*undersea*" -type f 2>/dev/null',
    'find /opt/Gaia -name "*underwater*" -type f 2>/dev/null',
    'find /opt/Gaia -name "*snowglobe*" -type f 2>/dev/null',
    'find /home/eastgate -maxdepth 4 -name "*inkfish*" -type f 2>/dev/null',
    'find /home/eastgate -maxdepth 4 -name "*octop*" -type f 2>/dev/null',
    'find /home/eastgate -maxdepth 4 -name "*ludo*" -type f 2>/dev/null',
    'find /home/eastgate -maxdepth 4 -name "*steam*" -type f 2>/dev/null | head -20',
]

for cmd in searches:
    _, o, _ = ssh.exec_command(cmd)
    r = o.read().decode().strip()
    if r:
        print(f"=== {cmd.split('*')[1] if '*' in cmd else cmd} ===")
        print(r)
        print()

# Check recent HUD data files
print("=== Recent HUD data bones ===")
_, o, _ = ssh.exec_command('ls -lt /home/eastgate/Development/ecoPrimals/infra/hud/site/public/data/ | head -25')
print(o.read().decode())

# Check static pages
print("=== All static pages ===")
_, o, _ = ssh.exec_command('ls /opt/Gaia/static/*.html 2>/dev/null')
print(o.read().decode())

# Check recent git log for inkfish/frame/octopus/ludo
print("=== Recent git mentions ===")
_, o, _ = ssh.exec_command('cd /opt/Gaia && git log --oneline -20')
print(o.read().decode())

# Check frameGate in ecosystem
print("=== frameGate references ===")
_, o, _ = ssh.exec_command('grep -rl "frameGate\\|frame.Gate\\|steam.frame\\|Steam.Frame" /opt/Gaia/data/ 2>/dev/null | head -10')
print(o.read().decode())

# Check Ludo Spring specifically
print("=== Ludo Spring ===")
_, o, _ = ssh.exec_command('grep -rl "ludo\\|Ludo" /opt/Gaia/ 2>/dev/null | head -10')
print(o.read().decode())

ssh.close()
