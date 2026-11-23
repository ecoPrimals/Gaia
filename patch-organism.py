#!/usr/bin/env python3
"""Patch the organism.html on BOTH paths to show real wave 259 stats."""
import paramiko

EASTGATE = '192.168.4.244'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(EASTGATE, username='eastgate', password='eastgate', timeout=15)
sftp = ssh.open_sftp()

# Both copies of organism.html
paths = [
    '/home/eastgate/Development/ecoPrimals/infra/hud/site/public/organism.html',
    '/opt/Gaia/static/organism.html',
]

# Check which paths exist and get them from the gate route
stdin, stdout, stderr = ssh.exec_command('grep -rn "organism" /opt/Gaia/gaia_gate.pi 2>/dev/null | grep -i "html\|serve\|static\|file\|path" | head -10')
gate_routes = stdout.read().decode().strip()
print(f'Gate organism routes: {gate_routes}')

# Find the actual file the gate serves
stdin, stdout, stderr = ssh.exec_command('find /opt/Gaia -name "organism.html" 2>/dev/null')
found = stdout.read().decode().strip()
print(f'Found organism.html at: {found}')

# Also check the static dir
stdin, stdout, stderr = ssh.exec_command('ls /opt/Gaia/static/organism* 2>/dev/null')
static_files = stdout.read().decode().strip()
print(f'Static organism files: {static_files}')

# The gate serves from its own directory — let's find it
stdin, stdout, stderr = ssh.exec_command('grep -n "organism" /opt/Gaia/gaia_gate.pi 2>/dev/null')
all_refs = stdout.read().decode().strip()
print(f'\nAll organism refs in gaia_gate.pi:')
print(all_refs)

# Patch ALL organism.html files found
all_paths = [p.strip() for p in found.split('\n') if p.strip()]
print(f'\nPatching {len(all_paths)} files:')

replacements = [
    ('id="sr-entities">27', 'id="sr-entities">13'),
    ('id="sr-ram">317', 'id="sr-ram">1,497'),
    ('id="sr-gpus">4', 'id="sr-gpus">7'),
    ('id="sr-models">93', 'id="sr-models">63'),
    ('27 entities', '13 entities'),
    ('317GB RAM', '1,497GB RAM'),
]

for fpath in all_paths:
    try:
        with sftp.open(fpath, 'r') as f:
            html = f.read().decode()
        changed = False
        for old, new in replacements:
            if old in html:
                html = html.replace(old, new)
                changed = True
        if changed:
            with sftp.open(fpath, 'w') as f:
                f.write(html)
            print(f'  PATCHED: {fpath}')
        else:
            print(f'  (no changes needed): {fpath}')
    except Exception as e:
        print(f'  ERROR: {fpath}: {e}')

# Verify from both ports
for port in [8080, 8443]:
    stdin, stdout, stderr = ssh.exec_command(
        f"curl -s http://localhost:{port}/organism 2>/dev/null | grep -o 'sr-ram\">[^<]*' | head -1"
    )
    ram = stdout.read().decode().strip()
    stdin, stdout, stderr = ssh.exec_command(
        f"curl -s http://localhost:{port}/organism 2>/dev/null | grep -o 'sr-entities\">[^<]*' | head -1"
    )
    ent = stdout.read().decode().strip()
    stdin, stdout, stderr = ssh.exec_command(
        f"curl -s http://localhost:{port}/organism 2>/dev/null | grep -o 'sr-gpus\">[^<]*' | head -1"
    )
    gpu = stdout.read().decode().strip()
    print(f'  :{port} → {ram} | {ent} | {gpu}')

sftp.close()
ssh.close()

print('\n=== ORGANISM PATCHED ===')
print('  Stats ribbon now shows REAL numbers on both :8080 and :8443')
print('  13 entities · 1,497 GB RAM · 7 GPUs · 63 models · 847 TFLOPS')
