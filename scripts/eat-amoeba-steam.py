import paramiko
import json

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10)

# Read all the AMOEBA and Steam files
files = [
    '/opt/Gaia/data/amoeba-config.json',
    '/opt/Gaia/data/amoeba-mesh.json',
    '/opt/Gaia/data/body/amoeba-address-book.json',
    '/opt/Gaia/data/body/amoeba-eye-handoff.json',
    '/opt/Gaia/data/body/steam-absorption.json',
    '/opt/Gaia/data/body/polaris-steam.json',
    '/opt/Gaia/membrane/amoeba-bridge.sh',
    '/opt/Gaia/runtime/amoeba-hands.sh',
    '/opt/Gaia/runtime/amoeba_bootstrap.sh',
    '/opt/Gaia/infra/framegate-eat.sh',
    '/opt/Gaia/static/frame.html',
]

for f in files:
    print(f'\n{"="*60}')
    print(f'=== {f} ===')
    print(f'{"="*60}')
    _, out, err = c.exec_command(f'cat {f} 2>/dev/null | head -60', timeout=5)
    content = out.read().decode().strip()
    if content:
        print(content)
    else:
        print('  (empty or not found)')

# Check SteamOS / frameGate specific
print('\n' + '='*60)
print('=== FRAMEGATE / STEAMOS KNOWLEDGE ===')
_, out, _ = c.exec_command('find /opt/Gaia -name "*.json" -exec grep -l -i "framegate\\|steamframe\\|steamos\\|arm64\\|snapdragon" {} \\; 2>/dev/null | head -10', timeout=10)
frame_files = out.read().decode().strip()
print(frame_files)

for ff in frame_files.split('\n')[:5]:
    if ff.strip():
        print(f'\n--- {ff} (frame-related excerpt) ---')
        _, out, _ = c.exec_command(f'grep -i "frame\\|steam.*os\\|arm64\\|snapdragon" {ff} | head -10', timeout=5)
        print(out.read().decode().strip())

c.close()
print('\nAMOEBA + STEAM fully digested!')
