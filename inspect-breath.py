#!/usr/bin/env python3
"""Inspect the green waveform on outer-face.html — what makes it breathe?"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10)

# What generates the green waveform?
_, o, _ = ssh.exec_command('grep -n -i "canvas\\|wave\\|mesh\\|breath\\|oscillat\\|requestAnim\\|WebGL\\|THREE\\|gl_\\|vertex\\|shader" /opt/Gaia/static/outer-face.html | head -40')
print("=== Waveform source clues ===")
print(o.read().decode())

# Check for external JS files loaded
_, o, _ = ssh.exec_command('grep -n "script.*src" /opt/Gaia/static/outer-face.html')
print("=== Script tags ===")
print(o.read().decode())

# Check pulse data
_, o, _ = ssh.exec_command('curl -s http://localhost:8080/pulse 2>/dev/null | head -30')
print("=== Pulse data ===")
print(o.read().decode())

# Check breathe count from pulse
_, o, _ = ssh.exec_command('curl -s http://localhost:8443/pulse 2>/dev/null | head -30')
print("=== Gate pulse ===")
print(o.read().decode())

# How big is outer-face.html?
_, o, _ = ssh.exec_command('wc -l /opt/Gaia/static/outer-face.html')
print("=== Size ===")
print(o.read().decode())

ssh.close()
