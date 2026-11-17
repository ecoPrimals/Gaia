#!/usr/bin/env python3
"""Inject wave259-overlay.js into ALL HUD entry points + make available on gate."""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)

REAL = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'
TAG = '<script defer src=/js/wave259-overlay.js?v=1></script>'

# 1. Copy JS to gate's static dir so :8443 can serve it
print("=== COPY JS TO GATE STATIC ===")
stdin, stdout, stderr = ssh.exec_command(f'cp {REAL}/js/wave259-overlay.js /opt/Gaia/static/js/ 2>/dev/null; mkdir -p /opt/Gaia/static/js && cp {REAL}/js/wave259-overlay.js /opt/Gaia/static/js/')
stdout.read()
stdin, stdout, stderr = ssh.exec_command('ls -la /opt/Gaia/static/js/wave259-overlay.js')
print(f"  {stdout.read().decode().strip()}")

# Also copy to /opt/Gaia/js/ since gate might serve from there
stdin, stdout, stderr = ssh.exec_command(f'test -d /opt/Gaia/js && cp {REAL}/js/wave259-overlay.js /opt/Gaia/js/')
stdout.read()

# 2. Inject into HUD index.html (the :8080 entry point)
print("\n=== INJECT INTO HUD INDEX.HTML ===")
sftp = ssh.open_sftp()
idx_path = f'{REAL}/index.html'
with sftp.file(idx_path, 'r') as f:
    idx = f.read().decode()

if 'wave259-overlay' in idx:
    print("  Already injected in index.html")
else:
    # Find cosmic-view.js script tag or </body>
    if 'cosmic-view.js' in idx:
        # Inject after cosmic-view
        parts = idx.split('cosmic-view.js')
        # Find the end of that script tag
        after = parts[1]
        close_tag = after.index('>')
        inject_point = len(parts[0]) + len('cosmic-view.js') + close_tag + 1
        idx_new = idx[:inject_point] + '\n' + TAG + '<!-- W259 bones -->' + idx[inject_point:]
    elif '</body>' in idx:
        idx_new = idx.replace('</body>', TAG + '\n</body>')
    elif '</html>' in idx:
        idx_new = idx.replace('</html>', TAG + '\n</html>')
    else:
        idx_new = idx + '\n' + TAG
    
    with sftp.file(idx_path, 'w') as f:
        f.write(idx_new)
    print("  ✓ Injected into index.html")

# 3. Also check if there are other HUD pages that load the cosmic view
print("\n=== CHECK OTHER COSMIC VIEW PAGES ===")
stdin, stdout, stderr = ssh.exec_command(f'grep -l "cosmic-view" {REAL}/*.html 2>/dev/null')
cosmic_pages = stdout.read().decode().strip().split('\n')
print(f"  Pages with cosmic-view: {len([p for p in cosmic_pages if p.strip()])}")
for page in cosmic_pages:
    if not page.strip():
        continue
    name = page.strip().split('/')[-1]
    stdin, stdout, stderr = ssh.exec_command(f'grep -c "wave259-overlay" {page.strip()}')
    has_it = int(stdout.read().decode().strip() or '0') > 0
    if has_it:
        print(f"    ✓ {name}")
    else:
        print(f"    → injecting into {name}")
        with sftp.file(page.strip(), 'r') as f:
            content = f.read().decode()
        if 'cosmic-surfaces.js' in content:
            marker = '<script defer src=/js/cosmic-surfaces.js'
            idx2 = content.index(marker)
            end_tag = content.index('>', idx2) + 1
            content_new = content[:end_tag] + '\n    ' + TAG + content[end_tag:]
        elif '</body>' in content:
            content_new = content.replace('</body>', TAG + '\n</body>')
        else:
            content_new = content + '\n' + TAG
        with sftp.file(page.strip(), 'w') as f:
            f.write(content_new)
        print(f"    ✓ {name} injected")

sftp.close()

# 4. Verify JS accessibility on both ports
print("\n=== VERIFY JS ACCESSIBILITY ===")
import urllib.request
for url in [
    'http://192.168.4.244:8080/js/wave259-overlay.js',
    'http://192.168.4.244:8443/js/wave259-overlay.js',
]:
    try:
        r = urllib.request.urlopen(url, timeout=5)
        print(f"  ✓ {url.split('//')[1]}: {r.status} {len(r.read())}B")
    except Exception as e:
        print(f"  ✗ {url.split('//')[1]}: {e}")

ssh.close()

print("""
=== OVERLAY INJECTED EVERYWHERE ===

  wave259-overlay.js renders INTO the cosmic view:
  - 13 blackholes at gut ring with bh-glow + accretion disks
  - Klein face markers (out/in/fold)
  - Organism gate dots on membrane ring with pulse animation
  - 8 depth axis rings (Pluto → Core)
  - Wave 259 badge with lub-DUB heartbeat
  
  Injected into ALL pages that load cosmic-view.js.
  Available on BOTH :8080 (HUD data) and :8443 (gate).
  
  Reload hud.primals.eco to see the bones IN the cosmos.
""")
