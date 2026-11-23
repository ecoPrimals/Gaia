#!/usr/bin/env python3
"""Fix the pulse section — wire real lung data from gate."""
import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10)

REAL = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'

# Find what's in the pulse section
_, o, _ = ssh.exec_command(f'grep -n "pulse\\|PULSE\\|breath\\|lung\\|LUNG\\|Heart\\|heart" {REAL}/js/wave259-overlay.js')
lines = o.read().decode()
print("Current pulse/breath refs:")
print(lines)

# Read the overlay
_, o, _ = ssh.exec_command(f'cat {REAL}/js/wave259-overlay.js')
overlay = o.read().decode()

# The old pulse was replaced partially. Let me add the gate pulse fetch
# AFTER the dock fetch section, before the RSS section
# Find a good insertion point

# Add gate pulse + lung data fetch after the RSS section
rss_marker = "console.log('[W259] @home trio rendered"
if rss_marker not in overlay:
    rss_marker = "console.log('[W259] Klein dissolution"

lung_fetch = """
    // ═══ REAL PULSE + LUNG from gate :8443 ═══
    fetch('https://primals.eco/pulse').then(function(r){return r.json()}).then(function(p) {
      var el = document.getElementById('w259-right');
      if (!el) return;
      
      if (p.heart) {
        el.innerHTML += '<br><span style="color:#f85149">❤</span> ' + 
          p.heart.total_beats.toLocaleString() + ' beats · ' + Math.round(p.heart.bpm) + ' bpm';
      }
      if (p.lung) {
        el.innerHTML += '<br><span style="color:#d4a574">🫁</span> ' + 
          p.lung.total_breaths.toLocaleString() + ' breaths · ' + Math.round(p.lung.brpm) + ' brpm';
        el.innerHTML += '<br><span style="color:#d4a574">🫁</span> ratio ' + p.lung.ratio + ':1';
        
        // Make breathing ring match real ratio
        var br = wrap.querySelector('[style*="w259breathe"]');
        if (br) br.style.animationDuration = Math.max(3, p.lung.ratio) + 's';
      }
      if (p.sun) {
        el.innerHTML += '<br><span style="color:#f0e68c">☀</span> sun ' + 
          Math.round(p.sun.elevation_deg) + '° · ' + p.sun.chord;
      }
      
      console.log('[W259] Gate pulse: bpm=' + (p.heart?p.heart.bpm:'?') + 
        ', brpm=' + (p.lung?p.lung.brpm:'?'));
    }).catch(function(e){ console.log('[W259] gate pulse:', e); });
"""

overlay = overlay.replace(
    rss_marker,
    lung_fetch + "\n    " + rss_marker
)
print(f"\nInserted gate pulse + lung fetch")

# Remove old static pulse if still there
if "pulse unreachable" in overlay:
    # Remove the old unreachable line
    overlay = overlay.replace(
        """stat(vw-10, 10, '❤ pulse unreachable', '#f85149', 9, 0.15, 'right');""",
        "// old pulse removed — using gate pulse now"
    )
    print("Removed old static pulse")

sftp = ssh.open_sftp()
with sftp.file(f'{REAL}/js/wave259-overlay.js', 'w') as f:
    f.write(overlay)
print(f"Updated overlay ({len(overlay)} bytes)")

with sftp.file('/opt/Gaia/static/js/wave259-overlay.js', 'w') as f:
    f.write(overlay)
print("Copied to gate")

sftp.close()

# Verify
import urllib.request
r = urllib.request.urlopen(f'http://192.168.4.244:8080/js/wave259-overlay.js', timeout=5)
data = r.read()
has_lung = b'brpm' in data and b'lung' in data
has_sine = b'drawBreath' in data
print(f"\n✓ Has lung data: {has_lung}")
print(f"✓ Has sine wave: {has_sine}")
print(f"✓ Size: {len(data)}B")

ssh.close()
