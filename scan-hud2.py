#!/usr/bin/env python3
"""Scan for gaia-seed.json, existing SW, and the cosmic-view.js (solar system)."""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)

HUD = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'

cmds = [
    ('SEED JSON', f'cat {HUD}/gaia-seed.json 2>/dev/null'),
    ('COSMIC VIEW HEAD', f'head -60 {HUD}/js/cosmic-view.js 2>/dev/null'),
    ('INDEX TAIL', f'tail -80 {HUD}/index.html 2>/dev/null'),
    ('KLEIN FILES', f'find {HUD} -name "*klein*" -o -name "*bottle*" 2>/dev/null'),
    ('NULL FILES', f'find {HUD} -maxdepth 1 -name "*null*" -o -name "*klein*" -o -name "*cross*" -o -name "*ouroboros*" 2>/dev/null'),
    ('SENSES PAGE', f'head -30 {HUD}/senses.html 2>/dev/null || echo "no senses.html"'),
    ('GAIA-GLOBE-CORE HEAD', f'head -40 {HUD}/js/gaia-globe-core.js 2>/dev/null'),
]

for label, cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    print(f'=== {label} ===')
    print(out[:2000] if out else '(empty)')
    print()

ssh.close()
