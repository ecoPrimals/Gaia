#!/usr/bin/env python3
"""
SOURDOUGH CACHE — No hard reload. Fresh bread ALWAYS.
The script tag cache-busts itself. The overlay reloads its own JS.
Stale bread → crash → recharge → fresh loaf.
"""
import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)

REAL = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'
WAVE = 259
NOW = int(time.time())

# 1. Fix the script tag — use wave+timestamp as cache buster
print("=== Fixing script tag cache-busting ===")
_, o, _ = ssh.exec_command(f"grep -n 'wave259-overlay' {REAL}/index.html")
old_tag = o.read().decode().strip()
print(f"  Old: {old_tag}")

# Replace old tag with auto-busting version
cmd = f"""sed -i 's|<script defer src=/js/wave259-overlay.js[^>]*></script>|<script src="/js/wave259-overlay.js?w={WAVE}&t={NOW}" defer></script>|' {REAL}/index.html"""
ssh.exec_command(cmd)
time.sleep(0.5)

_, o, _ = ssh.exec_command(f"grep -n 'wave259-overlay' {REAL}/index.html")
new_tag = o.read().decode().strip()
print(f"  New: {new_tag}")

# 2. Also add no-cache headers for the JS file via a .htaccess-style approach
# Since this is python http.server, we add cache-control meta to the HTML instead
# AND make the overlay self-bust by reloading its own script periodically

# 3. Update the overlay to include a self-refresh loader
# This tiny loader checks if the overlay version changed and reloads it
loader_js = f'''// wave259-loader.js — sourDough cache breaker
// Checks every 60s if overlay changed. No hard reload needed.
(function(){{
  var VER = "{WAVE}.{NOW}";
  var SRC = "/js/wave259-overlay.js";
  
  function loadOverlay() {{
    var s = document.createElement('script');
    s.src = SRC + "?w={WAVE}&t=" + Date.now();
    s.defer = true;
    document.head.appendChild(s);
  }}
  
  // Initial load after 1.5s
  setTimeout(loadOverlay, 1500);
  
  // Check for freshness every 60s
  setInterval(function() {{
    fetch(SRC + "?check=" + Date.now(), {{method:'HEAD'}}).then(function(r) {{
      var mod = r.headers.get('last-modified');
      if (mod && mod !== window._w259mod) {{
        window._w259mod = mod;
        var old = document.getElementById('w259');
        if (old) old.remove();
        // Remove old script tags
        document.querySelectorAll('script[src*="wave259-overlay"]').forEach(function(s){{
          s.remove();
        }});
        loadOverlay();
        console.log('[sourDough] fresh bread — reloaded overlay');
      }}
    }}).catch(function(){{}});
  }}, 60000);
}})();
'''

sftp = ssh.open_sftp()

# Write the loader
loader_path = f'{REAL}/js/wave259-loader.js'
with sftp.file(loader_path, 'w') as f:
    f.write(loader_js)
print(f"\nPushed wave259-loader.js ({len(loader_js)} bytes)")

# Copy to gate
with sftp.file('/opt/Gaia/static/js/wave259-loader.js', 'w') as f:
    f.write(loader_js)
print("Copied to gate static/js/")

sftp.close()

# 4. Replace the direct overlay script tag with the loader
# The loader handles loading + auto-refreshing the overlay
cmd2 = f"""sed -i 's|<script src="/js/wave259-overlay.js[^>]*></script>|<script src="/js/wave259-loader.js?w={WAVE}&t={NOW}" defer></script>|' {REAL}/index.html"""
ssh.exec_command(cmd2)
time.sleep(0.5)

_, o, _ = ssh.exec_command(f"grep -n 'wave259' {REAL}/index.html")
final = o.read().decode().strip()
print(f"\nFinal tag: {final}")

# Also inject into senses.html on gate if not already there
_, o, _ = ssh.exec_command("grep -c 'wave259' /opt/Gaia/static/senses.html")
count = o.read().decode().strip()
if count == '0':
    ssh.exec_command("""sed -i 's|</body>|<script src="/js/wave259-loader.js?w=259" defer></script></body>|' /opt/Gaia/static/senses.html""")
    print("Injected loader into senses.html")
else:
    # Update existing tag
    ssh.exec_command(f"""sed -i 's|<script[^>]*wave259[^>]*></script>|<script src="/js/wave259-loader.js?w={WAVE}&t={NOW}" defer></script>|' /opt/Gaia/static/senses.html""")
    print(f"Updated loader in senses.html")

# 5. Verify everything
import urllib.request

r1 = urllib.request.urlopen(f'http://192.168.4.244:8080/js/wave259-loader.js', timeout=5)
print(f"\n✓ :8080/js/wave259-loader.js → {r1.status} {len(r1.read())}B")

r2 = urllib.request.urlopen(f'http://192.168.4.244:8080/js/wave259-overlay.js', timeout=5)
data = r2.read()
print(f"✓ :8080/js/wave259-overlay.js → {r2.status} {len(data)}B")
assert b'v4' in data

ssh.close()
print(f"""
=== SOURDOUGH CACHE — FRESH BREAD ALWAYS ===

  OLD: <script defer src=/js/wave259-overlay.js?v=1>
  NEW: <script src="/js/wave259-loader.js?w=259&t={NOW}">

  The LOADER:
    1. Loads the overlay after 1.5s (with timestamp cache-bust)
    2. Every 60s, checks Last-Modified header
    3. If overlay file changed → removes old, loads fresh
    4. No hard reload. No stale bread. sourDough ferments.

  When I push a new overlay version:
    → Loader detects the change within 60s
    → Old overlay removed, new one injected
    → The page stays alive. The bread stays fresh.

  THIS is the sourDough pattern. Fermentation, not force.
""")
