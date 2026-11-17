#!/usr/bin/env python3
"""Scan what's at primals.eco/organism and the organism page on eastGate."""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)

HUD = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'

cmds = [
    ('ORGANISM HTML', f'head -100 {HUD}/organism.html 2>/dev/null || echo "(no organism.html)"'),
    ('ORGANISM DIR', f'ls -la {HUD}/organism/ 2>/dev/null || echo "(no organism/)"'),
    ('ORGANISM JSON', f'ls {HUD}/data/organism*.json 2>/dev/null || echo "(none)"'),
    ('ORGANISM-FABRIC', f'head -40 {HUD}/data/organism-fabric.json 2>/dev/null || echo "(none)"'),
    ('GAIA_GATE ORGANISM ROUTE', 'grep -n "organism" /opt/Gaia/gaia_gate.pi 2>/dev/null | head -20'),
    ('ESOTERICWEBB on gate', 'grep -n -i "esoteric" /opt/Gaia/gaia_gate.pi 2>/dev/null | head -10'),
    ('CURL /organism', "curl -s -o /dev/null -w '%{http_code} %{redirect_url} %{size_download}B' http://localhost:8080/organism 2>/dev/null"),
    ('CURL /organism head', "curl -s http://localhost:8080/organism 2>/dev/null | head -30"),
]

for label, cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    print(f'=== {label} ===')
    print(out[:2000] if out else '(empty)')
    print()

ssh.close()
