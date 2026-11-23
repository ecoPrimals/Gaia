#!/usr/bin/env python3
"""Fix emoji rendering in the triangulation overlay on senses.html"""

import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10)

sftp = c.open_sftp()
path = '/opt/Gaia/static/senses.html'

with sftp.open(path, 'r') as f:
    content = f.read().decode('utf-8', errors='replace')

# Fix the escaped emoji
content = content.replace('\\U0001F441', '\U0001F441')

with sftp.open(path, 'w') as f:
    f.write(content)

print(f'Fixed emoji in senses.html ({len(content)} chars)')

# Also fix in gaia-home.html on eastGate if needed
for p in [
    '/home/eastgate/Development/ecoPrimals/infra/hud/site/public/index.html',
    '/home/eastgate/Development/ecoPrimals/infra/hud/site/public/data/gaia-home.html',
]:
    try:
        with sftp.open(p, 'r') as f:
            d = f.read().decode('utf-8', errors='replace')
        if '\\U0001F441' in d:
            d = d.replace('\\U0001F441', '\U0001F441')
            with sftp.open(p, 'w') as f:
                f.write(d)
            print(f'Fixed emoji in {p}')
    except:
        pass

sftp.close()
c.close()
print('Done')
