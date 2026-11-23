#!/usr/bin/env python3
"""
Fix CORS: pulse data can't be fetched cross-origin.
Solution: snapshot pulse.json to HUD data dir (same-origin fetch).
The existing heartbeat cron already updates data — we just need a symlink
or a one-time snapshot that gets refreshed by the overlay's 30s rebuild.
"""
import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10)

REAL = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'

# 1. Snapshot current pulse to HUD data dir
_, o, _ = ssh.exec_command('curl -s http://localhost:8443/pulse')
pulse = o.read().decode()
print(f"Gate pulse: {len(pulse)} bytes")

if pulse and pulse.strip().startswith('{'):
    sftp = ssh.open_sftp()
    with sftp.file(f'{REAL}/data/pulse.json', 'w') as f:
        f.write(pulse)
    print("Saved pulse.json to HUD data/")
    sftp.close()
    
    # Show what we got
    p = json.loads(pulse)
    if 'heart' in p:
        print(f"  Heart: {p['heart']['total_beats']} beats, {p['heart']['bpm']:.0f} bpm")
    if 'lung' in p:
        print(f"  Lung: {p['lung']['total_breaths']} breaths, {p['lung']['brpm']:.0f} brpm, ratio {p['lung']['ratio']}")
    if 'sun' in p:
        print(f"  Sun: {p['sun']['elevation_deg']:.1f}° el, chord={p['sun']['chord']}")

# 2. Add a tiny cron-like refresh: the existing eastgate-pulse cron 
# runs every 2 min. Let's have it also write to HUD.
# BUT: 0 new crons rule. So instead, let's add it to an EXISTING mushroom.
# The membrane-pulse mushroom runs every 2 min and already writes data.
# Let's just add one line to it.

# Actually, simplest: make the overlay fetch from /data/pulse.json
# and add a curl to the existing eastgate-pulse cron to update it.

# Check if eastgate-pulse already writes anywhere
_, o, _ = ssh.exec_command('crontab -l 2>/dev/null | grep eastgate-pulse')
cron_line = o.read().decode().strip()
print(f"\nExisting cron: {cron_line}")

# Instead of modifying cron, let's have the gate itself write pulse.json
# when it generates pulse data. Or simpler: create a tiny shell append
# to the EXISTING eastgate-pulse that also copies to HUD.

# Actually the ABSOLUTE simplest: just pipe it in the existing cron line
# The cron calls a mushroom script. Let's check what it does.
_, o, _ = ssh.exec_command('cat /opt/Gaia/mushrooms/eastgate-pulse.sh 2>/dev/null | head -20')
mushroom = o.read().decode()
print(f"\nMushroom:\n{mushroom}")

# 3. For NOW: update the overlay to fetch /data/pulse.json (same origin)
_, o, _ = ssh.exec_command(f'cat {REAL}/js/wave259-overlay.js')
overlay = o.read().decode()

# Replace the cross-origin pulse fetch
old_fetch = "fetch('https://primals.eco/pulse')"
new_fetch = "fetch('/data/pulse.json')"

if old_fetch in overlay:
    overlay = overlay.replace(old_fetch, new_fetch)
    print("\nFixed pulse fetch: /data/pulse.json (same-origin)")

sftp = ssh.open_sftp()
with sftp.file(f'{REAL}/js/wave259-overlay.js', 'w') as f:
    f.write(overlay)
with sftp.file('/opt/Gaia/static/js/wave259-overlay.js', 'w') as f:
    f.write(overlay)
sftp.close()
print("Updated overlay + gate copy")

# 4. Add pulse snapshot to the existing eastgate-pulse mushroom
# Just append one curl line that writes to HUD data dir
_, o, _ = ssh.exec_command('grep -c "pulse.json" /opt/Gaia/mushrooms/eastgate-pulse.sh 2>/dev/null')
already = o.read().decode().strip()
if already == '0':
    # Append the snapshot line
    cmd = '''echo '# Snapshot pulse to HUD for same-origin overlay fetch
curl -s http://localhost:8443/pulse > /home/eastgate/Development/ecoPrimals/infra/hud/site/public/data/pulse.json 2>/dev/null' >> /opt/Gaia/mushrooms/eastgate-pulse.sh'''
    ssh.exec_command(cmd)
    print("Appended pulse snapshot to eastgate-pulse mushroom (runs every 2 min)")
else:
    print("Pulse snapshot already in mushroom")

ssh.close()
print("\nDone — pulse.json now same-origin, refreshed every 2 min by existing cron")
