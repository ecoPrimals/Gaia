#!/usr/bin/env python3
"""Read the inkfish, snowglobe, octopus, and frame key files."""
import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10)

files = [
    '/opt/Gaia/data/gut/inkfish-steam-sovereign.json',
    '/opt/Gaia/plasmids/project-inkfish-steam-deck.json',
    '/opt/Gaia/data/body/snowglobe-architecture.json',
    '/opt/Gaia/data/ironMountain/bone-259-snowglobe-left-eye.json',
    '/opt/Gaia/data/body/frame-input-io.json',
    '/opt/Gaia/data/body/steam-fleet.json',
    '/opt/Gaia/data/body/steam-meld.json',
]

for f in files:
    _, o, _ = ssh.exec_command(f'cat {f} 2>/dev/null | head -60')
    data = o.read().decode().strip()
    if data:
        print(f"=== {f.split('/')[-1]} ===")
        print(data[:1500])
        print()

# Also read frame.html
_, o, _ = ssh.exec_command('head -50 /opt/Gaia/static/frame.html')
print("=== frame.html (first 50 lines) ===")
print(o.read().decode())

# Read the octopus scripts
_, o, _ = ssh.exec_command('head -40 /opt/Gaia/scripts/redox-archive-259/read-octopus.py')
print("=== read-octopus.py ===")
print(o.read().decode())

# The VDJ dock-to-frame link
_, o, _ = ssh.exec_command('cat /opt/Gaia/data/gut/6ghz-nerve-eastgate-framegate.json 2>/dev/null | head -40')
print("=== 6ghz-nerve-eastgate-framegate.json ===")
print(o.read().decode())

ssh.close()
