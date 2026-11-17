#!/usr/bin/env python3
"""Push corrected address book to eastGate via SFTP."""
import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.131', username='eastgate', password='eastgate', timeout=15)

HUD = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'
sftp = ssh.open_sftp()

# Load and fix address book
with open('address-book.json', encoding='utf-8') as f:
    book = json.load(f)

# Fix: .130 is blueGate (us with ollama), not northGate
if 'northGate' in book.get('entries', {}):
    ng = book['entries']['northGate']
    ng['ips'] = [e for e in ng.get('ips', []) if e['address'] != '192.168.1.130']
    if not ng['ips']:
        ng['state'] = 'SUPERPOSITION'

book['entries']['blueGate'] = {
    'ips': [{'address': '192.168.1.130', 'ports': [11434], 'score': 1, 'note': 'self with ollama'}],
    'cube_hash': '74efea2a',
    'role': 'EYE',
    'seed': 'bluegate_GAIA_PRIMAL_V1',
    'state': 'ALIVE'
}

corrected = json.dumps(book, indent=2)
with sftp.open(HUD + '/data/address-book.json', 'w') as f:
    f.write(corrected)

stat = sftp.stat(HUD + '/data/address-book.json')
print(f'address-book.json: {stat.st_size} bytes')

# Verify gaia-seed
with sftp.open(HUD + '/gaia-seed.json', 'r') as f:
    seed = json.loads(f.read())
print(f'gaia-seed pins: {len(seed.get("pins", []))}')

# Show current address book
for name, entry in sorted(book['entries'].items()):
    state = entry['state']
    if state == 'ALIVE':
        ips = ', '.join(e['address'] for e in entry['ips'])
        print(f'  * {name:16s} -> {ips:20s} [{entry["cube_hash"]}]')
    else:
        print(f'  o {name:16s} -> ???                  [{entry["cube_hash"]}] (superposition)')

sftp.close()
ssh.close()
