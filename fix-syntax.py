#!/usr/bin/env python3
"""Fix the syntax error — missing quote in style array."""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10)

REAL = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'

_, o, _ = ssh.exec_command(f'cat {REAL}/js/wave259-overlay.js')
overlay = o.read().decode()

# The bug: panel line is missing closing quote, breathe line concatenated
# Line 23: ...padding:4px 8px}\n      @keyframes w259breathe...
# Should be: ...padding:4px 8px}',\n      '@keyframes w259breathe...

bad = "#w259 .panel{position:absolute;background:rgba(0,0,0,0.6);border:1px solid rgba(255,255,255,0.08);border-radius:4px;padding:4px 8px}\n      @keyframes w259breathe"
good = "#w259 .panel{position:absolute;background:rgba(0,0,0,0.6);border:1px solid rgba(255,255,255,0.08);border-radius:4px;padding:4px 8px}',\n      '@keyframes w259breathe"

if bad in overlay:
    overlay = overlay.replace(bad, good)
    print("Fixed missing quote between panel and breathe keyframes")
else:
    print("Trying alt pattern...")
    # Maybe it's on one line
    bad2 = "padding:4px 8px}\n      @keyframes"
    good2 = "padding:4px 8px}',\n      '@keyframes"
    if bad2 in overlay:
        overlay = overlay.replace(bad2, good2)
        print("Fixed alt pattern")
    else:
        print("ERROR: Cannot find the broken pattern")
        # Show what's around the panel line
        idx = overlay.find('padding:4px 8px}')
        if idx > -1:
            print(f"Context: ...{repr(overlay[idx:idx+120])}...")

sftp = ssh.open_sftp()
with sftp.file(f'{REAL}/js/wave259-overlay.js', 'w') as f:
    f.write(overlay)
print(f"Updated overlay ({len(overlay)} bytes)")
with sftp.file('/opt/Gaia/static/js/wave259-overlay.js', 'w') as f:
    f.write(overlay)
print("Copied to gate")
sftp.close()

# Quick verify — try to find syntax issues
import urllib.request
r = urllib.request.urlopen(f'http://192.168.4.244:8080/js/wave259-overlay.js', timeout=5)
js = r.read().decode()
# Check the style array is properly formed
style_start = js.find("style.textContent = [")
style_end = js.find("].join('\\n');")
if style_start > -1 and style_end > -1:
    style_block = js[style_start:style_end+13]
    # Count quotes in the array
    in_array = js[style_start+21:style_end]
    single_quotes = in_array.count("'")
    print(f"Style array: {single_quotes} single quotes (should be even: {single_quotes % 2 == 0})")

ssh.close()
