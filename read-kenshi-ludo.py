#!/usr/bin/env python3
"""
Read ALL Kenshi Reborn + Ludo Spring work across the ecosystem.
This is the engine for the persistent snowglobe.
"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)

def run(cmd):
    _, o, e = ssh.exec_command(cmd, timeout=15)
    return o.read().decode().strip()

# Find ALL kenshi references
print("=== KENSHI REBORN FILES ===")
print(run('find /opt/Gaia -iname "*kenshi*" -type f 2>/dev/null'))
print(run('find /home/eastgate -maxdepth 5 -iname "*kenshi*" -type f 2>/dev/null | head -30'))
print()

# Find Ork references
print("=== ORK FILES ===")
print(run('find /opt/Gaia -iname "*ork*" -type f 2>/dev/null | head -20'))
print(run('find /home/eastgate -maxdepth 5 -iname "*ork*" -type f 2>/dev/null | head -20'))
print()

# Ludo Spring full directory
print("=== LUDO SPRING DIRECTORY ===")
print(run('find /home/eastgate/ludoSpring -type f 2>/dev/null | head -40'))
print()

# Kenshi Reborn HTML page
print("=== kenshi-reborn.html ===")
print(run('cat /opt/Gaia/static/kenshi-reborn.html 2>/dev/null | head -80'))
print()

# Recent git commits mentioning kenshi or ludo
print("=== GIT LOG — kenshi/ludo ===")
print(run('cd /opt/Gaia && git log --oneline --all --grep="kenshi\\|Kenshi\\|ludo\\|Ludo\\|reborn\\|Reborn" | head -20'))
print()

# Plasmids related to gaming/engine
print("=== GAMING PLASMIDS ===")
print(run('ls /opt/Gaia/plasmids/ | grep -i "kenshi\\|game\\|engine\\|reborn\\|ludo\\|ork\\|godot\\|unity\\|steam"'))
print()

# Check data dirs
print("=== DATA — gaming/engine ===")
print(run('find /opt/Gaia/data -iname "*kenshi*" -o -iname "*reborn*" -o -iname "*ludo*" -o -iname "*engine*" -o -iname "*ork*" 2>/dev/null | head -20'))
print()

# Eaten data (digested games)
print("=== EATEN — tr49 (Godot project?) ===")
print(run('ls /opt/Gaia/data/eaten/tr49/ 2>/dev/null | head -20'))
print()

# Check what's in the ludoSpring data
print("=== LUDO SPRING DATA ===")
for f in run('find /home/eastgate/ludoSpring -name "*.json" -type f 2>/dev/null').split('\n'):
    if f:
        print(f"--- {f.split('/')[-1]} ---")
        print(run(f'head -30 {f}'))
        print()

# Springs page
print("=== springs.html ===")
print(run('head -60 /opt/Gaia/static/springs.html 2>/dev/null'))
print()

# Play pages
print("=== play.html / play-gaia.html ===")
print(run('head -30 /opt/Gaia/static/play-gaia.html 2>/dev/null'))

ssh.close()
