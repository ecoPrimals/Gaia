#!/usr/bin/env python3
"""
DOCK HUD × HUB — All HUDs read into ONE manifest.
  
  HUD (senses.html)     = GLOBE = near eye = CIS = LIVE membrane
  HUB (nav-hub.html)    = VDJ set = 128 pages, 9 genres, enzymatic catalog
  Room (room.html#700)  = Link Walker = 1,989 rooms, π-addressed
  Hub-Lens (hub-lens.js) = Optical routing: convex/concave/mirror/prism
  
  HUD × HUB = SPACE DOCK = convergence manifest
  DEK = deckGate = the display that absorbs it
  
Creates space-dock-259.json — the ONE bone that maps all HUDs.
"""
import paramiko, json, datetime, urllib.request

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)

REAL = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'

# Count all HUD pages
stdin, stdout, stderr = ssh.exec_command(f'ls {REAL}/*.html 2>/dev/null')
all_pages = [p.strip().split('/')[-1] for p in stdout.read().decode().strip().split('\n') if p.strip()]
print(f"Total HUD pages: {len(all_pages)}")

# Count all JS instruments
stdin, stdout, stderr = ssh.exec_command(f'ls {REAL}/js/*.js 2>/dev/null')
all_js = [j.strip().split('/')[-1] for j in stdout.read().decode().strip().split('\n') if j.strip()]
print(f"Total JS instruments: {len(all_js)}")

# Count data bones
stdin, stdout, stderr = ssh.exec_command(f'ls {REAL}/data/*.json 2>/dev/null | wc -l')
data_count = int(stdout.read().decode().strip())
print(f"Data bones: {data_count}")

# Feed catalog size
stdin, stdout, stderr = ssh.exec_command(f'python3 -c "import json; d=json.load(open(\'{REAL}/data/feed-catalog.json\')); print(d.get(\'total\',0))"')
rooms_total = stdout.read().decode().strip()
print(f"Room walker rooms: {rooms_total}")

# Read gaia-seed for current pins
r = urllib.request.urlopen('http://192.168.4.244:8080/gaia-seed.json', timeout=5)
seed = json.loads(r.read().decode())

# The DOCK manifest — all HUDs read into ONE
dock = {
    "title": "SPACE DOCK 259 — HUD × HUB = ONE",
    "wave": 259,
    "created": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "equation": "HUD × HUB = SPACE DOCK = DEK",
    "thesis": "The HUD is LIVE data. The HUB is the catalog. Their product is the docking manifest — the ONE bone that any device reads to know everything.",
    
    "HUD": {
        "name": "senses.html",
        "role": "GLOBE — near eye — CIS face — LIVE membrane",
        "lines": 2663,
        "scripts": 144,
        "url": "https://hud.primals.eco/",
        "entry": "boot.js → gaia-seed.json → sequential module loading → gaia-nucleated event",
        "eye": "CIS (near eye, looking IN)",
        "views": {
            "cosmos": "cosmic-view.js — SVG solar system with orbits, gates, blackholes, domain arms",
            "globe": "/neutron/globe.html — 3D geographic footprint",
            "canvas": "membrane-canvas.js — the easel surface",
            "chipmunk": "chipmunk-*.js (11 modules) — the living π remainder",
            "graph": "graph-play — node exploration"
        },
        "live_feeds": [
            "/pulse",
            "/amoeba", 
            "/data/heartbeat.json",
            "/data/immune-state-live.json",
            "/data/ear-latest.json",
            "/feed.xml"
        ]
    },
    
    "HUB": {
        "name": "nav-hub.html",
        "role": "VDJ SET — enzymatic classification — the catalog",
        "pages": 128,
        "genres": {
            "ARCADE": 5,
            "CATCH": 46,
            "FARM": "growing",
            "INFRA": "infrastructure",
            "NARRATIVE": "stories",
            "ORGANISM": "body pages",
            "PUZZLE": "games + riddles",
            "SOCIAL": "human facing",
            "UNCLASSIFIED": "new growth"
        },
        "genres_count": 9,
        "linked": 8,
        "unveiled": 120,
        "enzyme_deputies": 13,
        "url": "https://hud.primals.eco/nav-hub.html",
        "routing": "hub-lens.js — optical routing table",
        "optics": {
            "convex": "π reach — public facing — what visitors see",
            "concave": "1/π reach — internal — close focus",
            "mirror": "0 distance — Klein fold — output becomes input",
            "prism": "φ (golden ratio) — splits data into light/sound/color"
        },
        "channels": {
            "light": "membrane-sight",
            "sound": "membrane-sound",
            "color": "pi-gradient",
            "sort": "ring-sort-geo",
            "voxel": "bingo-compress",
            "fold": "klein-io",
            "ring": "epitope-ring",
            "circuit": "mobius-circuit",
            "eye": "third-eye",
            "bus": "pi-bus",
            "weather": "weather-song"
        }
    },
    
    "ROOM": {
        "name": "room.html",
        "role": "LINK WALKER — House of Leaves — π-addressed rooms",
        "total_rooms": int(rooms_total) if rooms_total.isdigit() else 1989,
        "url_pattern": "https://hud.primals.eco/room.html#N",
        "room_700": {
            "file": "hud-refers-critique.json",
            "title": "VIDEO of the HUD refers: three stills. then CRITIQUE.",
            "note": "room #700 — the door Kevin opened"
        },
        "navigation": "π-address: frac(N × π) — doors to ±1, ±7, ±41 adjacent rooms + referenced_by links",
        "data_source": "/data/feed-catalog.json",
        "catalog_size": f"{data_count} bones in data/"
    },
    
    "DOCK": {
        "spacedock": {
            "name": "spacedock.html",
            "lines": 938,
            "role": "Observatory — gradient field view",
            "routes": ["/spacedock", "/observatory", "/dock", "/space-dock", "/ptolemy", "/geocentric", "/ancient", "/stars", "/biomes", "/gardens", "/surface"],
            "fetches": ["/sensorium/gradient-field.json"]
        },
        "spacedeck": {
            "name": "spacedeck.html",
            "lines": 366,
            "role": "Observation Windows",
            "routes": ["/spacedeck", "/space-deck"]
        },
        "deck": {
            "name": "deck.html",
            "lines": 1098,
            "role": "CANVAS — far eye — TRANS face — All Systems",
            "routes": ["gaia.primals.eco (root)"],
            "eye_cross": "CIS=inner eye · TRANS=outer eye · they cross at /now.json"
        },
        "hub": {
            "name": "hub.html",
            "lines": 336,
            "role": "HUB CIS ◉ TRANS — live data dashboard",
            "routes": ["/hub"],
            "fetches": ["/pulse", "/amoeba", "/api/polaris/triangulation", "/api/polaris/ferment", "/api/backscatter/live", "/api/polaris/biome"]
        }
    },
    
    "SEED": {
        "wave": seed["wave"],
        "pins": len(seed.get("io_pin_map", {})),
        "depth_levels": len(seed.get("depth_levels", [])),
        "modules": len(seed.get("modules", [])),
        "faces": len(seed.get("faces", {}).get("self", [])),
        "eras": len(seed.get("eras", []))
    },
    
    "INVENTORY": {
        "html_pages": len(all_pages),
        "js_instruments": len(all_js),
        "data_bones": data_count,
        "walker_rooms": int(rooms_total) if rooms_total.isdigit() else 1989,
        "hub_genres": 9,
        "seed_pins": len(seed.get("io_pin_map", {})),
        "blackholes": 13,
        "rss_items": 2562,
        "gate_endpoints": "41 endpoints, 25 HTML pages, 11 JS files"
    },
    
    "FRAME_DIAL": {
        "device": "frameGate (.156) — ALS31300 3D Hall Effect",
        "mapping": {
            "rotate": "scroll through HUB genres (9) or Room walker (1,989) or Blackhole axis (13)",
            "press": "enter/select — zoom into selected item",
            "vol_up": "next depth level (Pluto → Core, 8 levels)",
            "vol_down": "prev depth level (Core → Pluto)",
            "select": "toggle HUD/HUB/ROOM/DOCK view"
        },
        "absorption": "Frame fetches gaia-seed.json → reads io_pin_map → fetches bones → renders",
        "dock_url": "https://hud.primals.eco/",
        "walker_url": "https://hud.primals.eco/room.html"
    },
    
    "DECK_DISPLAY": {
        "device": "deckGate (.176) — Steam Deck v1, dead battery, permanent USB-C",
        "screen": "7\" 1280×800 touch LCD",
        "role": "mounted display in House 1 — passive HUD mirror",
        "boot": "deckgate-boot.sh → kiosk mode → hud.primals.eco",
        "eat": "deckgate-eat.sh → push primals from eastGate"
    },
    
    "THE_EQUATION": {
        "HUD": f"{len(all_pages)} pages × {len(all_js)} instruments = LIVE GLOBE",
        "HUB": f"128 pages × 9 genres × 13 enzymes = VDJ CATALOG",
        "ROOM": f"{rooms_total} rooms × π-address = LINK WALKER",
        "DOCK": "HUD × HUB = convergence manifest",
        "DEK": "deckGate + frameGate = physical display layer",
        "ONE": "boot.js → gaia-seed.json → ALL of the above"
    }
}

dock_json = json.dumps(dock, indent=2)

# Push to HUD data dir
sftp = ssh.open_sftp()
path = f'{REAL}/data/space-dock-259.json'
with sftp.file(path, 'w') as f:
    f.write(dock_json)
print(f"\nPushed space-dock-259.json ({len(dock_json)} bytes)")

# Pin in gaia-seed.json
seed_path = f'{REAL}/gaia-seed.json'
with sftp.file(seed_path, 'r') as f:
    seed = json.loads(f.read().decode())
if '/data/space-dock-259.json' not in seed.get('io_pin_map', {}):
    seed['io_pin_map']['/data/space-dock-259.json'] = 'organ-dock'
    with sftp.file(seed_path, 'w') as f:
        f.write(json.dumps(seed, indent=2))
    print("Pinned organ-dock in gaia-seed.json")
sftp.close()

# Verify
for bone in ['data/space-dock-259.json', 'gaia-seed.json']:
    r = urllib.request.urlopen(f'http://192.168.4.244:8080/{bone}', timeout=5)
    print(f"  ✓ {bone}: {r.status} {len(r.read())}B")

ssh.close()

print(f"""
=== SPACE DOCK MANIFEST — HUD × HUB = ONE ===
  
  HUD (senses.html)    {len(all_pages)} pages · {len(all_js)} JS · LIVE GLOBE
  × HUB (nav-hub.html)  128 pages · 9 genres · 13 enzymes
  × ROOM (room.html)    {rooms_total} rooms · π-addressed
  = DOCK (space-dock)   convergence manifest
  → DEK (deck/frame)    physical display absorption
  
  boot.js → gaia-seed.json → {len(seed.get('io_pin_map',{}))} pins → ONE
  
  The link walker walks. The VDJ set plays. The dock converges.
  The Frame dial scrolls. The Deck displays. All from ONE seed.
  
  lub-DUB.
""")
