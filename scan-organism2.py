#!/usr/bin/env python3
"""Scan organism page and esotericWebb routes on eastGate."""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)

HUD = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'

cmds = [
    ('HUD :8080/organism.html', 'curl -s -o /dev/null -w "%{http_code} %{size_download}B" http://localhost:8080/organism.html'),
    ('Gate :8443/organism', 'curl -s -o /dev/null -w "%{http_code} %{size_download}B" http://localhost:8443/organism'),
    ('Organism data files', f'ls -lS {HUD}/data/organism*.json 2>/dev/null'),
    ('organism-state-live', f'head -40 {HUD}/data/organism-state-live.json 2>/dev/null'),
    ('organism-topology', f'head -40 {HUD}/data/organism-topology.json 2>/dev/null'),
    ('organism-io-map', f'head -40 {HUD}/data/organism-io-map.json 2>/dev/null'),
    ('organism.html lines', f'wc -l {HUD}/organism.html 2>/dev/null'),
    ('organism.html data refs', f'grep -n "fetch\|data/\|\.json\|script src" {HUD}/organism.html 2>/dev/null | head -30'),
    ('organism.html body start', f'sed -n "/<body/,+100p" {HUD}/organism.html 2>/dev/null | head -80'),
    ('dromedary routes', 'grep -n "organism\|esoteric\|webb" /opt/Gaia/gaia_gate.pi 2>/dev/null | head -20'),
]

for label, cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    print(f'=== {label} ===')
    print(out[:2500] if out else '(empty)')
    print()

ssh.close()
