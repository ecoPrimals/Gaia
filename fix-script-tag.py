#!/usr/bin/env python3
"""Fix the mangled script tag in index.html on eastGate."""
import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10)

REAL = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'

# Read the damaged line
_, o, _ = ssh.exec_command(f'sed -n 1938p {REAL}/index.html')
damaged = o.read().decode().strip()
print(f"DAMAGED: {damaged[:100]}...")

# Write a python fix script to eastGate and run it there
NOW = int(time.time())
fix_script = f'''
import sys
path = "{REAL}/index.html"
with open(path) as f:
    lines = f.readlines()

clean_tag = '<script src="/js/wave259-loader.js?w=259&t={NOW}" defer></script>\\n'
lines[1937] = clean_tag
    
with open(path, 'w') as f:
    f.writelines(lines)
print("FIXED line 1938 to: " + clean_tag.strip())
'''

sftp = ssh.open_sftp()
with sftp.file('/tmp/fix_tag.py', 'w') as f:
    f.write(fix_script)
sftp.close()

_, o, e = ssh.exec_command('python3 /tmp/fix_tag.py')
print(o.read().decode().strip())
err = e.read().decode().strip()
if err:
    print(f"ERR: {err}")

# Verify
_, o, _ = ssh.exec_command(f'sed -n 1938p {REAL}/index.html')
print(f"CLEAN: {o.read().decode().strip()}")

# Also verify the page loads
import urllib.request
r = urllib.request.urlopen('http://192.168.4.244:8080/', timeout=5)
html = r.read().decode()
if 'wave259-loader' in html:
    print(f"\n✓ index.html serves loader tag")
else:
    print(f"\n✗ loader tag NOT found in served HTML")

ssh.close()
