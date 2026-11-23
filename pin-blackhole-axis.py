#!/usr/bin/env python3
"""
PIN BLACKHOLE AXIS — All 13 singularities as state in the ouroboros gut.
The cosmic-view.js already renders bhObjects with bh-glow gradient + accretion disks.
This bone maps each blackhole to:
  - ouroboros position (all at GUT TOP = intake)
  - cosmic-view coordinates (x, y, r for SVG rendering)
  - live state (ACTIVE / DORMANT / DISSOLVED)
  - the axis for the Frame dial to scroll through

Push to HUD data dir + pin in gaia-seed.json.
"""
import paramiko, json, datetime

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)

REAL = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'

# Read the full blackhole alignment
stdin, stdout, stderr = ssh.exec_command('cat /opt/Gaia/data/ironMountain/blackhole-alignment-259.json')
bh_raw = json.loads(stdout.read().decode())

# Read the ouroboros model
stdin, stdout, stderr = ssh.exec_command('cat /opt/Gaia/data/body/ouroboros-model.json')
ouro_raw = json.loads(stdout.read().decode())

# cosmic-view.js coordinates: W=900, H=640, cx=450, cy=320
# Orbits: 16, 26, 38, 48, 72, 94, 112, 126 (inner to outer)
# bh-glow gradient already exists
# Sagittarius A* at center (cx, cy)
# Ouroboros gut = depth_level "Gut" at R=0.5 in gaia-seed

import math
PI = math.pi
TAU = 2 * PI
cx, cy = 450, 320

# Map 13 blackholes around the GUT ring (R=0.5 of the view = ~160px from center)
# They're ALL at the top of the gut — spread across the intake arc
GUT_R = 160  # gut radius in SVG coords
INTAKE_ARC = PI  # spread across top half (intake = mouth side)

# Build the axis bone
holes = []
bh_data = bh_raw.get("THIRTEEN_BLACK_HOLES", {})
for i, (key, val) in enumerate(bh_data.items()):
    angle = -PI/2 + (i / 12) * INTAKE_ARC - INTAKE_ARC/2  # spread around top
    x = cx + math.cos(angle) * GUT_R
    y = cy + math.sin(angle) * GUT_R
    
    # Determine live state
    name = val.get("name", key)
    dissolved = "DISSOLVED" in str(val) or "DEAD" in str(val) or "DEPRECATED" in str(val)
    dormant = "dormant" in str(val).lower() or "old" in str(val).lower()
    
    state = "DISSOLVED" if dissolved else ("DORMANT" if dormant else "ACTIVE")
    direction = val.get("direction", "THROUGH")
    
    hole = {
        "id": key,
        "name": name,
        "what": val.get("what", val.get("insight", val.get("law", ""))),
        "state": state,
        "direction": direction,
        "ouroboros": {
            "position": "GUT_TOP",
            "ring": "intake",
            "depth": 0.5,
            "label": "digestion"
        },
        "cosmic": {
            "x": round(x, 1),
            "y": round(y, 1),
            "r": 3.0 if state == "ACTIVE" else 1.5,
            "color": "#f0883e" if state == "ACTIVE" else ("#484f58" if state == "DISSOLVED" else "#8b949e"),
            "glow": state == "ACTIVE"
        },
        "dial_index": i,
        "plasmid": val.get("plasmid", None)
    }
    
    # Add GIS if present
    if "gis" in val:
        hole["gis"] = val["gis"]
    
    holes.append(hole)

# Build the full axis bone
axis_bone = {
    "title": "BLACKHOLE AXIS — State at the Top of the Gut",
    "wave": 259,
    "created": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "thesis": bh_raw.get("thesis", ""),
    "THE_ONE_HOLE": bh_raw.get("THE_ONE_HOLE", {}),
    "ouroboros_context": {
        "model": ouro_raw.get("title", "Ouroboros REDOX"),
        "irreducible_minimum": ouro_raw.get("irreducible_minimum", {}).get("formula", ""),
        "gut_position": "TOP — intake end of the through-tube",
        "biology": "MOUTH (in) → GUT (through-tube) → ANUS (out)",
        "all_blackholes_are": "INTAKE — they pull IN, they are the mouth end",
        "topology": "BLACK HOLE (0D) → TIME (1D) → CYLINDER (2D) → TORUS (3D) → KLEIN (4D)"
    },
    "alignment_overlay": bh_raw.get("ALIGNMENT_OVERLAY", {}),
    "cosmic_view": {
        "center": {"x": cx, "y": cy},
        "gut_radius": GUT_R,
        "intake_arc_rad": INTAKE_ARC,
        "gradient": "bh-glow",
        "note": "cosmic-view.js already has bh-glow gradient + accretion disk rendering"
    },
    "dial_axis": {
        "count": len(holes),
        "scroll_mode": "rotate dial → step through blackholes",
        "press_mode": "press → zoom into selected blackhole detail",
        "current": 0
    },
    "blackholes": holes,
    "state_summary": {
        "total": len(holes),
        "active": sum(1 for h in holes if h["state"] == "ACTIVE"),
        "dormant": sum(1 for h in holes if h["state"] == "DORMANT"),
        "dissolved": sum(1 for h in holes if h["state"] == "DISSOLVED")
    }
}

axis_json = json.dumps(axis_bone, indent=2)
print(f"Blackhole axis: {len(holes)} holes, {axis_bone['state_summary']}")

# Push to HUD data dir
sftp = ssh.open_sftp()

# Write the bone
path = f'{REAL}/data/blackhole-axis-259.json'
with sftp.file(path, 'w') as f:
    f.write(axis_json)
print(f"Pushed {path} ({len(axis_json)} bytes)")

# Update gaia-seed.json to include the new bone pin
seed_path = f'{REAL}/gaia-seed.json'
with sftp.file(seed_path, 'r') as f:
    seed = json.loads(f.read().decode())

if '/data/blackhole-axis-259.json' not in seed.get('io_pin_map', {}):
    seed['io_pin_map']['/data/blackhole-axis-259.json'] = 'organ-blackhole'
    with sftp.file(seed_path, 'w') as f:
        f.write(json.dumps(seed, indent=2))
    print(f"Pinned organ-blackhole in gaia-seed.json")
else:
    print("Already pinned in gaia-seed.json")

sftp.close()

# Verify
import urllib.request
for bone in ['data/blackhole-axis-259.json', 'gaia-seed.json']:
    try:
        r = urllib.request.urlopen(f'http://192.168.4.244:8080/{bone}', timeout=5)
        print(f"  ✓ {bone}: {r.status} {len(r.read())}B")
    except Exception as e:
        print(f"  ✗ {bone}: {e}")

# Also push the full alignment to the HUD data dir for reference
align_path = f'{REAL}/data/blackhole-alignment-259.json'
sftp2 = ssh.open_sftp()
with sftp2.file(align_path, 'w') as f:
    f.write(json.dumps(bh_raw, indent=2))
print(f"Pushed full alignment to {align_path}")
sftp2.close()

# Verify the alignment too
try:
    r = urllib.request.urlopen('http://192.168.4.244:8080/data/blackhole-alignment-259.json', timeout=5)
    print(f"  ✓ blackhole-alignment-259.json: {r.status} {len(r.read())}B")
except Exception as e:
    print(f"  ✗ blackhole-alignment-259.json: {e}")

ssh.close()

print(f"""
=== BLACKHOLE AXIS PINNED ===
  13 blackholes mapped to cosmic-view coordinates
  All at GUT TOP (R=0.5, intake arc)
  State: {axis_bone['state_summary']}
  Cosmic-view.js already has bh-glow + accretion disk rendering
  Dial axis: rotate = step through holes, press = zoom in
  
  The ouroboros eats its own tail:
    MOUTH → GUT → ANUS → MOUTH
    IN    → THROUGH → OUT → IN
    
  All 13 blackholes are MOUTHS — they're the INTAKE end.
  They sit at the TOP of the gut in the ouroboros.
  The Frame dial scrolls through them.
  
  Topology:  
    BLACK HOLE (0D) → TIME (1D) → CYLINDER (2D) → TORUS (3D) → KLEIN (4D)
  
  lub-DUB.
""")
