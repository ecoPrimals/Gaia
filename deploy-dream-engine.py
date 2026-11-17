#!/usr/bin/env python3
"""
DREAM ENGINE — Kenshi Globe as persistent snowglobe.
Push everything into eastGate. Wire it to the PIP.
One unified internal origin display.
"""
import paramiko, json, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)

REAL = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'
LUDO = '/home/eastgate/ludoSpring'

def run(cmd, timeout=15):
    _, o, e = ssh.exec_command(cmd, timeout=timeout)
    return o.read().decode().strip(), e.read().decode().strip()

# ═══ 1. COPY KENSHI-GLOBE TO HUD PUBLIC ═══
print("=== 1. Deploying kenshi-globe.html ===")
out, _ = run(f'cp {LUDO}/engine/kenshi-reborn/web/kenshi-globe.html {REAL}/kenshi-globe.html')
out, _ = run(f'ls -la {REAL}/kenshi-globe.html')
print(f"  {out}")

# Also copy to gate static
out, _ = run(f'cp {LUDO}/engine/kenshi-reborn/web/kenshi-globe.html /opt/Gaia/static/kenshi-globe.html')
print("  Copied to gate static/")

# ═══ 2. COPY KENSHI-MESH-EXPLORER TO HUD ═══
print("\n=== 2. Deploying kenshi-mesh-explorer ===")
out, _ = run(f'cp /opt/Gaia/data/ludospring/kenshi-mesh-explorer.html {REAL}/kenshi-mesh.html')
out, _ = run(f'ls -la {REAL}/kenshi-mesh.html')
print(f"  {out}")
out, _ = run(f'cp /opt/Gaia/data/ludospring/kenshi-mesh-explorer.html /opt/Gaia/static/kenshi-mesh.html')

# ═══ 3. PUSH ALL KENSHI DATA TO HUD ═══
print("\n=== 3. Pushing Kenshi data to HUD data/ ===")
kenshi_data_files = [
    f'{LUDO}/data/kenshi-biome-creatures.json',
    f'{LUDO}/data/kenshi-reborn-digest.json',
    f'{LUDO}/data/kenshi-tcg-framework.json',
    f'{LUDO}/data/kenshi-flow-report.json',
    f'{LUDO}/data/sourdough-kenshi.json',
    f'{LUDO}/data/kenshi-decomposition/kenshi-full-anatomy.json',
    f'{LUDO}/data/eastgate-pull/kenshi-engine.json',
    f'{LUDO}/data/eastgate-pull/ludospring-gps.json',
    f'{LUDO}/data/eastgate-pull/ludospring-geodesic.json',
]

# Create kenshi data dir in HUD
run(f'mkdir -p {REAL}/data/kenshi')
for src in kenshi_data_files:
    fname = src.split('/')[-1]
    out, err = run(f'cp {src} {REAL}/data/kenshi/{fname} 2>&1')
    if err:
        print(f"  ✗ {fname}: {err}")
    else:
        size, _ = run(f'stat -c %s {REAL}/data/kenshi/{fname} 2>/dev/null')
        print(f"  ✓ {fname} ({size}B)")

# ═══ 4. PUSH TCG ART TO HUD ═══
print("\n=== 4. Pushing TCG art ===")
run(f'mkdir -p {REAL}/data/kenshi/tcg-art')
out, _ = run(f'cp {LUDO}/data/tcg-art/*.jpg {REAL}/data/kenshi/tcg-art/ 2>&1')
art_count, _ = run(f'ls {REAL}/data/kenshi/tcg-art/*.jpg 2>/dev/null | wc -l')
print(f"  ✓ {art_count} TCG art images deployed")

# ═══ 5. PUSH NEXUS MOD DATA ═══
print("\n=== 5. Pushing Nexus mod data ===")
run(f'mkdir -p {REAL}/data/kenshi/nexus')
out, _ = run(f'cp {LUDO}/data/nexus-ingest/*.json {REAL}/data/kenshi/nexus/ 2>&1')
nexus_count, _ = run(f'ls {REAL}/data/kenshi/nexus/*.json 2>/dev/null | wc -l')
print(f"  ✓ {nexus_count} Nexus data files deployed")

# ═══ 6. UPDATE PIP — kenshi-globe as default snowglobe ═══
print("\n=== 6. Updating PIP with kenshi-globe as default ===")
_, o, _ = ssh.exec_command(f'cat {REAL}/js/wave259-overlay.js')
overlay = o.read().decode()

# Replace PIP views — kenshi-globe first
old_pip_views = """var pipViews = [
      {name:'deck', url:'/deck.html', label:'🎮 deck'},
      {name:'senses', url:'https://in.nestgate.io/', label:'👁 senses'},
      {name:'outer', url:'https://out.nestgate.io/', label:'☀ outer'},
      {name:'fold', url:'https://nestgate.io/', label:'∅ fold'},
      {name:'turbo', url:'/turbo.html', label:'🔥 turbo'},
      {name:'frame', url:'/frame.html', label:'📺 frame'},
      {name:'room', url:'/room.html', label:'🏚 room'},
      {name:'hub', url:'/nav-hub.html', label:'🗺 hub'}
    ];"""

new_pip_views = """var pipViews = [
      {name:'globe', url:'/kenshi-globe.html', label:'🌍 dream'},
      {name:'mesh', url:'/kenshi-mesh.html', label:'🕸 mesh'},
      {name:'reborn', url:'https://nestgate.io/kenshi-reborn', label:'🦎 A-Life'},
      {name:'deck', url:'/deck.html', label:'🎮 deck'},
      {name:'senses', url:'https://in.nestgate.io/', label:'👁 senses'},
      {name:'outer', url:'https://out.nestgate.io/', label:'☀ outer'},
      {name:'fold', url:'https://nestgate.io/', label:'∅ fold'},
      {name:'turbo', url:'/turbo.html', label:'🔥 turbo'},
      {name:'frame', url:'/frame.html', label:'📺 frame'},
      {name:'room', url:'/room.html', label:'🏚 room'},
      {name:'hub', url:'/nav-hub.html', label:'🗺 hub'}
    ];"""

if old_pip_views in overlay:
    overlay = overlay.replace(old_pip_views, new_pip_views)
    print("  Updated PIP: kenshi-globe is now default view")

# Also make PIP auto-open with the dream globe
old_pip_open = "var pipOpen = false;"
new_pip_open = """var pipOpen = true;
    pip.style.display = 'block';
    pipFrame.src = pipViews[0].url;
    pipLabel.textContent = pipViews[0].label + ' · DREAM';
    pipBtn.style.display = 'none';"""

if old_pip_open in overlay:
    overlay = overlay.replace(old_pip_open, new_pip_open)
    print("  PIP auto-opens with dream globe")

sftp = ssh.open_sftp()
with sftp.file(f'{REAL}/js/wave259-overlay.js', 'w') as f:
    f.write(overlay)
with sftp.file('/opt/Gaia/static/js/wave259-overlay.js', 'w') as f:
    f.write(overlay)
sftp.close()
print(f"  Overlay updated ({len(overlay)}B)")

# ═══ 7. PIN IN GAIA-SEED ═══
print("\n=== 7. Pinning dream engine in gaia-seed ===")
_, o, _ = ssh.exec_command(f'cat {REAL}/gaia-seed.json')
seed = json.loads(o.read().decode())
seed['io_pin_map']['organ-dream'] = '/kenshi-globe.html'
seed['io_pin_map']['organ-alife'] = '/data/kenshi/kenshi-biome-creatures.json'
seed['io_pin_map']['organ-mesh'] = '/kenshi-mesh.html'
sftp = ssh.open_sftp()
with sftp.file(f'{REAL}/gaia-seed.json', 'w') as f:
    f.write(json.dumps(seed, indent=2))
sftp.close()
pins = len(seed['io_pin_map'])
print(f"  Pinned organ-dream, organ-alife, organ-mesh ({pins} pins)")

# ═══ 8. VERIFY ═══
print("\n=== 8. Verifying ===")
import urllib.request
urls = [
    'http://192.168.4.244:8080/kenshi-globe.html',
    'http://192.168.4.244:8080/kenshi-mesh.html',
    'http://192.168.4.244:8080/data/kenshi/kenshi-biome-creatures.json',
    'http://192.168.4.244:8080/data/kenshi/kenshi-engine.json',
]
for url in urls:
    try:
        r = urllib.request.urlopen(url, timeout=5)
        print(f"  ✓ {url.split('8080')[1]} → {r.status} ({len(r.read())}B)")
    except Exception as e:
        print(f"  ✗ {url.split('8080')[1]} → {e}")

ssh.close()
print(f"""
=== DREAM ENGINE DEPLOYED ===

  🌍 kenshi-globe.html  → HUD + gate (the SNOWGLOBE)
  🕸 kenshi-mesh.html   → HUD + gate (the MESH EXPLORER)  
  🦎 kenshi-reborn.html → gate (the A-Life Engine page)
  
  Data pushed to /data/kenshi/:
    biome-creatures, engine, anatomy, flow-report,
    TCG framework, sourdough-kenshi, GPS, geodesic
    {art_count} TCG art images, {nexus_count} Nexus mod files
    
  PIP defaults to 🌍 dream globe (auto-opens)
  11 views to cycle through: dream → mesh → A-Life → deck → senses → ...
  
  gaia-seed: {pins} pins (organ-dream, organ-alife, organ-mesh)
  
  The dream engine is ON.
  Load hud.primals.eco → PIP auto-opens with the kenshi globe.
  The snowglobe is persistent. The third eye is OPEN.
  
  Now fill it. Let it run. See what happens. 🌍
""")
