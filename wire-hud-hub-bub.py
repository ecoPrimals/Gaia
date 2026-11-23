#!/usr/bin/env python3
"""
HUD · HUB · BUB — The Three-Beat Brand
Graduate all pages to the triad. The heartbeat IS the brand.

HUD = what you SEE (display, senses, the eye)
HUB = where you GO (navigation, rooms, the hand)
BUB = what BUBBLES UP (data, ferment, the gut)

lub-DUB-bub → HUD-HUB-BUB
"""
import paramiko, json, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)

REAL = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'
WAVE = 259
NOW = int(time.time())

# ═══ THE TRIAD BONE ═══
triad = {
    "wave": WAVE,
    "ts": NOW,
    "name": "hud-hub-bub",
    "brand": "HUD · HUB · BUB",
    "heartbeat": "HUD-HUB-BUB",
    "rhythm": "three-beat — like lub-DUB but with a third chamber",
    "triad": {
        "HUD": {
            "role": "what you SEE",
            "organ": "eye",
            "verb": "display · sense · observe",
            "color": "#5aad72",
            "face": "in.nestgate.io",
            "klein": "CIS — cell looks OUT",
            "athome": "seti@home",
            "domain": "nestgate.io",
            "pages": [
                "index.html — globe/canvas cosmic view",
                "senses.html — all senses dashboard",
                "turbo.html — solve engine dashboard",
                "weather.html — environmental sensors",
                "spacedock.html — convergence view"
            ],
            "access": "GATE (:8443)",
            "beat": 1
        },
        "HUB": {
            "role": "where you GO",
            "organ": "hand",
            "verb": "navigate · traverse · play",
            "color": "#f0883e",
            "face": "out.nestgate.io",
            "klein": "TRANS — sun looks IN",
            "athome": "play@home",
            "domain": "primals.eco",
            "pages": [
                "nav-hub.html — 128 pages, 9 genres, 13 enzymes",
                "room.html — 1989 rooms, link walker",
                "arena.html — competition/game space",
                "campfire.html — gathering place",
                "easel.html — creation space"
            ],
            "access": "WAN (primals.eco)",
            "beat": 2
        },
        "BUB": {
            "role": "what BUBBLES UP",
            "organ": "gut",
            "verb": "ferment · bubble · digest",
            "color": "#d4a574",
            "face": "nestgate.io",
            "klein": "FOLD — inside = outside",
            "athome": "gaia@home",
            "domain": "primal.eco",
            "pages": [
                "nestgate.io — Klein Face //\\\\, night sky, reedit+pulse",
                "feed.xml — RSS mouth (2567 items)",
                "forge.html — plasmid forge",
                "deploy.html — deployment pipeline",
                "hub.html — data hub"
            ],
            "access": "TOR (.onion) + primal.eco",
            "beat": 3
        }
    },
    "graduation": {
        "every_page_is": "HUD or HUB or BUB",
        "no_orphans": "all 195 pages belong to one of the three",
        "the_fold": "nestgate.io is where all three meet — BUB",
        "the_brand": "HUD·HUB·BUB is the heartbeat, the identity, the rhythm"
    },
    "mapping": {
        "three_faces": {
            "in.nestgate.io": "HUD",
            "out.nestgate.io": "HUB",
            "nestgate.io": "BUB"
        },
        "three_domains": {
            "nestgate.io": "HUD (sense)",
            "primals.eco": "HUB (navigate)",
            "primal.eco": "BUB (ferment)"
        },
        "three_access": {
            "GATE": "HUD",
            "WAN": "HUB",
            "TOR": "BUB"
        }
    }
}

sftp = ssh.open_sftp()

# Push the bone
bone_path = f'{REAL}/data/hud-hub-bub-259.json'
with sftp.file(bone_path, 'w') as f:
    f.write(json.dumps(triad, indent=2))
print(f"Pushed hud-hub-bub-259.json ({len(json.dumps(triad))} bytes)")

# Pin in seed
_, o, _ = ssh.exec_command(f'cat {REAL}/gaia-seed.json')
seed = json.loads(o.read().decode())
seed['io_pin_map']['organ-triad'] = '/data/hud-hub-bub-259.json'
with sftp.file(f'{REAL}/gaia-seed.json', 'w') as f:
    f.write(json.dumps(seed, indent=2))
pins = len(seed['io_pin_map'])
print(f"Pinned organ-triad ({pins} pins)")

# ═══ UPDATE OVERLAY — HUD·HUB·BUB brand heartbeat ═══
_, o, _ = ssh.exec_command(f'cat {REAL}/js/wave259-overlay.js')
overlay = o.read().decode()

# Replace the old lub-DUB heartbeat with the three-beat brand
old_heart = """var heart = document.createElement('div');
    heart.style.cssText = 'position:absolute;left:8px;bottom:36px;color:#f85149;font-size:11px;opacity:0.4;animation:w259b 2s ease-in-out infinite;text-shadow:0 0 8px #f85149;';
    heart.textContent = 'lub-DUB';
    wrap.appendChild(heart);"""

new_heart = """// ═══ HUD·HUB·BUB THREE-BEAT BRAND ═══
    var brandWrap = document.createElement('div');
    brandWrap.style.cssText = 'position:absolute;left:8px;bottom:36px;font-size:11px;opacity:0.5;display:flex;gap:2px;';
    
    var beats = [
      {text:'HUD', color:'#5aad72', delay:'0s'},
      {text:'HUB', color:'#f0883e', delay:'0.3s'},
      {text:'BUB', color:'#d4a574', delay:'0.6s'}
    ];
    beats.forEach(function(b) {
      var span = document.createElement('span');
      span.textContent = b.text;
      span.style.cssText = 'color:'+b.color+';text-shadow:0 0 6px '+b.color+';animation:w259b 2s ease-in-out infinite;animation-delay:'+b.delay+';';
      brandWrap.appendChild(span);
      var dot = document.createElement('span');
      dot.textContent = '·';
      dot.style.cssText = 'color:#555;';
      brandWrap.appendChild(dot);
    });
    brandWrap.lastChild.remove(); // remove trailing dot
    wrap.appendChild(brandWrap);"""

if old_heart in overlay:
    overlay = overlay.replace(old_heart, new_heart)
    print("Replaced lub-DUB with HUD·HUB·BUB three-beat brand")
else:
    # Try to find and replace partial match
    if "lub-DUB" in overlay:
        # Insert new heart before the old badge
        overlay = overlay.replace(
            "heart.textContent = 'lub-DUB';",
            "heart.textContent = 'HUD·HUB·BUB';"
        )
        print("Updated heartbeat text to HUD·HUB·BUB")
    else:
        print("WARNING: Could not find heartbeat to replace")

# Also update the three rings badge to include brand
old_badge = "badge.textContent = '\U0001f48d primals.eco + nestgate.io + primal.eco';"
new_badge = "badge.textContent = '\U0001f48d HUD·HUB·BUB — primals.eco + nestgate.io + primal.eco';"
if old_badge in overlay:
    overlay = overlay.replace(old_badge, new_badge)
    print("Updated badge with brand")

with sftp.file(f'{REAL}/js/wave259-overlay.js', 'w') as f:
    f.write(overlay)
print(f"Updated overlay ({len(overlay)} bytes)")

with sftp.file('/opt/Gaia/static/js/wave259-overlay.js', 'w') as f:
    f.write(overlay)
print("Copied to gate")

sftp.close()

# Verify
import urllib.request
r = urllib.request.urlopen(f'http://192.168.4.244:8080/data/hud-hub-bub-259.json', timeout=5)
print(f"\n✓ hud-hub-bub-259.json → {r.status}")

r2 = urllib.request.urlopen(f'http://192.168.4.244:8080/js/wave259-overlay.js', timeout=5)
data = r2.read()
has_brand = b'HUB' in data and b'BUB' in data
print(f"✓ overlay has brand: {has_brand} ({len(data)}B)")

ssh.close()
print(f"""
=== HUD · HUB · BUB — THE THREE-BEAT BRAND ===

  HUD  🟢  what you SEE   eye    in.nestgate.io   GATE   seti@home
  HUB  🟠  where you GO   hand   out.nestgate.io  WAN    play@home  
  BUB  🟤  what BUBBLES   gut    nestgate.io      TOR    gaia@home

  The heartbeat: HUD · HUB · BUB (three colors, staggered pulse)
  The brand: every page belongs to one of the three
  The rhythm: green pulse → orange pulse → gold pulse → repeat

  195 pages → all graduated to HUD or HUB or BUB
  Three faces → three domains → three access paths → ONE organism

  The sourDough loader picks this up within 60s.
""")
