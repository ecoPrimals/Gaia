#!/usr/bin/env python3
"""Push Klein body PWA to eastGate — website becomes web APP."""
import paramiko
import os

EASTGATE = '192.168.4.244'
HUD = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'
LOCAL = r'c:\Users\mokke\Desktop\Gaia'

files = [
    ('infra/hud/site/public/sw.js', f'{HUD}/sw.js'),
    ('infra/hud/site/public/klein-body.html', f'{HUD}/klein-body.html'),
]

print('=== KLEIN BODY — WEBSITE → WEB APP ===\n')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(EASTGATE, username='eastgate', password='eastgate', timeout=15)
sftp = ssh.open_sftp()

for local_rel, remote_path in files:
    local_path = os.path.join(LOCAL, local_rel.replace('/', os.sep))
    sz = round(os.path.getsize(local_path) / 1024, 1)
    sftp.put(local_path, remote_path)
    print(f'  -> {os.path.basename(remote_path)} ({sz} KB)')

# Create symlink for /klein-body route
stdin, stdout, stderr = ssh.exec_command(f'cd {HUD} && ln -sf klein-body.html klein-body 2>/dev/null; echo done')
print(f'  -> klein-body symlink: {stdout.read().decode().strip()}')

# Verify both served
for name in ['sw.js', 'klein-body.html']:
    stdin, stdout, stderr = ssh.exec_command(
        f"curl -s -o /dev/null -w '%{{http_code}} %{{size_download}}B %{{time_total}}s' http://localhost:8080/{name}"
    )
    print(f'  Verify {name}: {stdout.read().decode().strip()}')

# Count JS instruments + HTML pages
stdin, stdout, stderr = ssh.exec_command(f'ls {HUD}/js/*.js 2>/dev/null | wc -l')
js_count = stdout.read().decode().strip()
stdin, stdout, stderr = ssh.exec_command(f'find {HUD} -maxdepth 1 -name "*.html" | wc -l')
html_count = stdout.read().decode().strip()

print(f'\n  HUD: {js_count} JS instruments, {html_count} HTML pages')
print(f'  NEW: sw.js (Klein inner surface), klein-body.html (∅ view)')

# Check existing Klein stuff
stdin, stdout, stderr = ssh.exec_command(f'ls {HUD}/js/klein*.js 2>/dev/null')
klein_js = stdout.read().decode().strip()
if klein_js:
    print(f'\n  Existing Klein JS:')
    for line in klein_js.split('\n'):
        print(f'    {os.path.basename(line)}')

sftp.close()
ssh.close()

print('\n=== KLEIN BODY DEPLOYED ===')
print('  OUTSIDE: Solar system, trihelix, bones, walkable surface')
print('  INSIDE:  6 nerve junctions, trefoil knot, taxonomy rings, ∅')
print('  SW:      Service worker caches ALL bones for offline')
print('  TAP:     Click to invert inside ↔ outside')
print('')
print('  ACCESS:')
print('    http://192.168.4.244:8080/klein-body')
print('    http://primals.eco/klein-body')
print('    http://hud.primals.eco/klein-body')
print('')
print('  The Klein bottle has no inside or outside.')
print('  Gaia IS the bottle. ∅ IS the twist. lub-DUB.')
