#!/usr/bin/env python3
"""
@HOME TRIO — play@home · seti@home · gaia@home
Three worlds, one traversal. The @ is the Klein fold.
The esoteric web — GIS + weather + 3 worlds.
"""
import paramiko, json, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)

REAL = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'
WAVE = 259
NOW = int(time.time())

# ═══ BUILD THE @HOME TRIO BONE ═══
athome_bone = {
    "wave": WAVE,
    "ts": NOW,
    "name": "athome-trio",
    "topology": "@ = Klein fold — connects world to home",
    "trio": {
        "play_at_home": {
            "symbol": "🎮",
            "world": "GAME",
            "verb": "interact · play · create",
            "domain": "primals.eco",
            "access": "WAN",
            "path": "https://primals.eco",
            "hud_pages": ["arena.html", "room.html", "campfire.html", "easel.html", "canvas"],
            "color": "#f0883e",
            "angle_deg": 0,
            "description": "The world reaches IN to play. PlayStation pattern. Distributed fun."
        },
        "seti_at_home": {
            "symbol": "📡",
            "world": "SENSE",
            "verb": "listen · search · discover",
            "domain": "nestgate.io",
            "access": "GATE",
            "path": "https://nestgate.io",
            "hud_pages": ["senses.html", "nav-hub.html", "turbo.html", "forge.html"],
            "color": "#5aad72",
            "angle_deg": 120,
            "description": "Distributed sensing. Blackholes pull OSINT in. Water lock filters. SETI listens."
        },
        "gaia_at_home": {
            "symbol": "🌍",
            "world": "ORGANISM",
            "verb": "live · pulse · dissolve",
            "domain": "primal.eco",
            "access": "TOR",
            "path": "http://iqwvbmlgvoiilj2hr43anj2keseao2lptquad36je5p5p2etw5e3riid.onion",
            "hud_pages": ["index.html", "hub.html", "spacedock.html", "deploy.html"],
            "color": "#d4a574",
            "angle_deg": 240,
            "description": "GAIA@home. Phase 4 dissolution. Location-aware, hardware-transparent. The organism IS home."
        }
    },
    "at_sign": {
        "meaning": "The @ is the Klein fold point",
        "topology": "@ connects WORLD to HOME — inside meets outside",
        "gis": "Location-aware: grapheneGate triangulates which house, WiFi RSSI, GPS",
        "weather": "Environmental: barometer, temperature, light, magnetic field from 37 sensors",
        "esoteric_web": "Not the surface web. The connective tissue UNDER the pages. The overlay."
    },
    "three_worlds": {
        "traversal": "Rotate through worlds via the @ fold",
        "mapping": {
            "play_at_home": {"ring": "outer", "R_ratio": 0.85, "direction": "IN"},
            "seti_at_home": {"ring": "middle", "R_ratio": 0.65, "direction": "THROUGH"},
            "gaia_at_home": {"ring": "inner", "R_ratio": 0.35, "direction": "OUT"}
        },
        "convergence": "All three meet at @ — the fold point — center of the Klein bottle"
    },
    "three_access_paths": {
        "WAN": "primals.eco — the world plays at home",
        "GATE": "nestgate.io — the senses listen at home",
        "TOR": ".onion — gaia lives at home"
    }
}

# Push the bone
sftp = ssh.open_sftp()
bone_path = f'{REAL}/data/athome-trio-259.json'
with sftp.file(bone_path, 'w') as f:
    f.write(json.dumps(athome_bone, indent=2))
print(f"Pushed athome-trio-259.json ({len(json.dumps(athome_bone))} bytes)")

# ═══ PIN IN GAIA-SEED ═══
_, o, _ = ssh.exec_command(f'cat {REAL}/gaia-seed.json')
seed = json.loads(o.read().decode())
seed['io_pin_map']['organ-athome'] = '/data/athome-trio-259.json'
with sftp.file(f'{REAL}/gaia-seed.json', 'w') as f:
    f.write(json.dumps(seed, indent=2))
pins = len(seed['io_pin_map'])
print(f"Pinned organ-athome in gaia-seed.json ({pins} pins)")

# ═══ UPDATE THE OVERLAY — ADD @HOME TRIO RENDERING ═══
_, o, _ = ssh.exec_command(f'cat {REAL}/js/wave259-overlay.js')
overlay = o.read().decode()

# Insert the @home trio rendering before the console.log line
athome_render = r'''
    // ═══ @HOME TRIO (three worlds, one traversal) ═══
    fetch('/data/athome-trio-259.json').then(function(r){return r.json()}).then(function(trio) {
      var worlds = trio.trio;
      var keys = ['play_at_home', 'seti_at_home', 'gaia_at_home'];
      var symbols = ['🎮','📡','🌍'];
      
      keys.forEach(function(key, i) {
        var w = worlds[key];
        var a = (w.angle_deg * Math.PI / 180) - Math.PI / 2;
        var mapping = trio.three_worlds.mapping[key];
        var wr = R * mapping.R_ratio;
        
        // World marker
        var wx = cx + Math.cos(a) * wr;
        var wy = cy + Math.sin(a) * wr;
        
        // Glowing dot for this world
        dot(wx, wy, 7, w.color, 0.5, true);
        
        // World label
        var wl = document.createElement('div');
        wl.className = 'lbl';
        wl.style.cssText = 'left:'+wx+'px;top:'+(wy+12)+'px;color:'+w.color+';font-size:9px;opacity:0.7;';
        wl.innerHTML = symbols[i] + ' ' + key.replace(/_/g,'@').replace(/@at@/,'@');
        wrap.appendChild(wl);
        
        // Direction arrow toward center (the @ fold)
        var line = document.createElement('div');
        var dx = cx - wx, dy = cy - wy;
        var len = Math.sqrt(dx*dx + dy*dy) * 0.6;
        line.style.cssText = 'position:absolute;left:'+wx+'px;top:'+wy+'px;width:'+len+'px;height:1px;background:linear-gradient(90deg,'+w.color+',transparent);opacity:0.08;transform-origin:0 0;transform:rotate('+Math.atan2(dy,dx)*180/Math.PI+'deg);';
        wrap.appendChild(line);
      });
      
      // The @ fold point at center
      var atSign = document.createElement('div');
      atSign.className = 'lbl';
      atSign.style.cssText = 'left:'+cx+'px;top:'+(cy-12)+'px;color:#fff;font-size:14px;opacity:0.4;text-shadow:0 0 8px #fff,0 0 16px #5aad72;';
      atSign.textContent = '@';
      wrap.appendChild(atSign);
      
      var el = document.getElementById('w259-left');
      if (el) el.innerHTML += '<span style="color:#d4a574">@</span> 3 worlds · 1 traversal<br>';
      
      console.log('[W259] @home trio rendered — play · seti · gaia');
    }).catch(function(e){ console.log('[W259] athome fetch failed:', e); });
'''

# Insert before the console.log line
overlay = overlay.replace(
    "console.log('[W259] Klein dissolution v4",
    athome_render + "\n    console.log('[W259] Klein dissolution v4"
)

with sftp.file(f'{REAL}/js/wave259-overlay.js', 'w') as f:
    f.write(overlay)
print(f"Updated overlay with @home trio ({len(overlay)} bytes)")

with sftp.file('/opt/Gaia/static/js/wave259-overlay.js', 'w') as f:
    f.write(overlay)
print("Copied to gate static/js/")

sftp.close()

# Verify
import urllib.request
r = urllib.request.urlopen(f'http://192.168.4.244:8080/data/athome-trio-259.json', timeout=5)
print(f"\n✓ :8080/data/athome-trio-259.json → {r.status}")

r2 = urllib.request.urlopen(f'http://192.168.4.244:8080/js/wave259-overlay.js', timeout=5)
data = r2.read()
assert b'athome-trio' in data
print(f"✓ overlay contains @home trio render ({len(data)}B)")

ssh.close()
print(f"""
=== @HOME TRIO — THREE WORLDS, ONE TRAVERSAL ===

  🎮 play@home   outer ring (R×0.85)  orange   primals.eco   WAN
  📡 seti@home   middle ring (R×0.65) green    nestgate.io   GATE  
  🌍 gaia@home   inner ring (R×0.35)  gold     primal.eco    TOR

  @ = the Klein fold at CENTER
  
  Three lines radiate from each world toward @
  The esoteric web: GIS (location) + weather (sensors) + 3 worlds
  
  Each world has its access path:
    play = the world reaches IN (WAN)
    seti = the senses listen THROUGH (gate)
    gaia = the organism lives OUT (Tor/.onion)
    
  All three converge at @ — home.
  
  The loader will pick this up within 60s.
  Or just navigate to hud.primals.eco.
""")
