#!/usr/bin/env python3
"""Scan the HUD site on eastGate to understand current structure."""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)

HUD = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'

cmds = [
    ('INDEX', f'head -80 {HUD}/index.html 2>/dev/null'),
    ('MANIFEST', f'cat {HUD}/app.webmanifest 2>/dev/null'),
    ('JS COUNT', f'ls {HUD}/js/*.js 2>/dev/null | wc -l'),
    ('JS FILES', f'ls -S {HUD}/js/*.js 2>/dev/null | head -30'),
    ('HTML PAGES', f'find {HUD} -maxdepth 1 -name "*.html" | wc -l'),
    ('DATA JSON', f'find {HUD}/data -name "*.json" | wc -l'),
    ('SERVICE WORKER', f'cat {HUD}/sw.js 2>/dev/null | head -20'),
    ('BOOT.JS', f'cat {HUD}/js/boot.js 2>/dev/null'),
    ('TOP HTML', f'ls -S {HUD}/*.html 2>/dev/null | head -20'),
]

for label, cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    print(f'=== {label} ===')
    print(out[:2000] if out else '(empty)')
    print()

ssh.close()
