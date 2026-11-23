#!/usr/bin/env python3
"""Consolidate 3 leaking IPs to 1 drip out, turn rest BACK inward

Current state:
  .213 (eno1 wired)     → LAN spine to northGate (KEEP INWARD)
  .131 (enp3s0 wired)   → ATT WAN, default route, cursor uses (1 DRIP OUT)
  .220 (wlp0s20f3 WiFi) → ATT WiFi, Steam uses (TURN INWARD)

Goal:
  1 drip out: .131 via enp3s0 (ATT wired) — the single WAN egress
  Inward: .213 (LAN spine), .220 → rejoin LAN WiFi or disable
"""

import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.213', username='eastgate', password='eastgate', timeout=5)

def run(cmd):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=15)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    return out, err

print('=== CONSOLIDATE 3 IPs → 1 DRIP ===')
print()

# Show current state
print('BEFORE:')
out, _ = run('ip -4 addr show | grep "inet " | grep -v 127.0.0.1 | grep -v virbr | grep -v "10.13"')
print(out)
print()

out, _ = run('ip route show default')
print(f'Default routes: {out}')
print()

# The WiFi interface (.220) is connected to ATT instead of LAN
# Check what SSID it's connected to
out, _ = run('iwconfig wlp0s20f3 2>/dev/null | grep ESSID')
print(f'WiFi SSID: {out.strip()}')
print()

# Check available WiFi networks (LAN ones)
out, _ = run('nmcli -t -f SSID,SIGNAL dev wifi list 2>/dev/null | head -10')
print(f'Available WiFi: {out}')
print()

# Report
print('=== THE 1 DRIP ===')
print('  OUT: .131 (enp3s0 ATT wired) → default route to WAN')
print('  IN:  .213 (eno1) → LAN spine to northGate')
print('  IN:  .220 (wlp0s20f3) → on ATT WiFi, should rejoin LAN')
print()

# Don't auto-disconnect WiFi — just report the state
# Kevin can decide whether to switch the WiFi back to Aperture Science
print('=== WiFi could reconnect to "Aperture Science" (LAN) ===')
print('  Currently on ATT network (192.168.1.x)')
print('  If reconnected to Aperture Science → would get 192.168.4.x IP')
print('  That would restore .244 or similar LAN address')
print()

# Show the consolidation
print('=== IP DRIP MODEL ===')
print('  TERRA (Earth/O) → .213 spine → northGate (inner, walking)')
print('  TERRA (Earth/O) → .131 drip  → WAN (outer, celestial)')
print('  TERRA (Earth/O) → .220 WiFi  → ATT (leak, should be inward)')

c.close()
