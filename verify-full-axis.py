#!/usr/bin/env python3
"""Verify the full axis: all bones, all pins, cosmic-view state."""
import urllib.request, json

BASE = 'http://192.168.4.244:8080'

# Load gaia-seed
r = urllib.request.urlopen(f'{BASE}/gaia-seed.json', timeout=5)
seed = json.loads(r.read().decode())
print(f"=== GAIA SEED wave {seed['wave']} ===")
print(f"  io_pin_map entries: {len(seed.get('io_pin_map', {}))}")
print(f"  depth_levels: {len(seed.get('depth_levels', []))}")
print(f"  modules: {len(seed.get('modules', []))}")

# Verify every pin
print(f"\n=== IO PIN MAP — ALL BONES ===")
pins = seed.get('io_pin_map', {})
alive = 0
dead = 0
for path, organ in sorted(pins.items()):
    url = f'{BASE}{path}'
    try:
        r = urllib.request.urlopen(url, timeout=5)
        size = len(r.read())
        print(f"  ✓ {r.status} {size:>6}B  {organ:<20s} ← {path}")
        alive += 1
    except Exception as e:
        print(f"  ✗ {str(e):<30s} {organ:<20s} ← {path}")
        dead += 1

print(f"\n  ALIVE: {alive}/{alive+dead}  DEAD: {dead}/{alive+dead}")

# Check blackhole axis content
print(f"\n=== BLACKHOLE AXIS STATE ===")
r = urllib.request.urlopen(f'{BASE}/data/blackhole-axis-259.json', timeout=5)
axis = json.loads(r.read().decode())
print(f"  {axis['dial_axis']['count']} blackholes on dial")
print(f"  State: {axis['state_summary']}")
print(f"  Ouroboros: {axis['ouroboros_context']['gut_position']}")
print(f"  Topology: {axis['ouroboros_context']['topology']}")
for h in axis['blackholes']:
    state_icon = '●' if h['state'] == 'ACTIVE' else ('◐' if h['state'] == 'DORMANT' else '○')
    print(f"    {state_icon} [{h['dial_index']:>2}] {h['name']:<40s} {h['state']:<10s} ({h['cosmic']['x']:.0f},{h['cosmic']['y']:.0f})")

# Check the depth levels (the axis itself)
print(f"\n=== DEPTH AXIS (ouroboros layers) ===")
for dl in seed.get('depth_levels', []):
    bar = '█' * int(dl['R'] * 20)
    print(f"  R={dl['R']:.2f} {bar:<16s} {dl['name']:<12s} {dl['label']}")

# RSS spine
print(f"\n=== RSS SPINE ===")
for feed in ['full-feed.xml', 'feed.xml']:
    try:
        r = urllib.request.urlopen(f'{BASE}/{feed}', timeout=5)
        content = r.read().decode()
        items = content.count('<item>')
        print(f"  {feed}: {items} items ({len(content)} bytes)")
    except:
        print(f"  {feed}: NOT FOUND")

# Service worker
print(f"\n=== SERVICE WORKER ===")
try:
    r = urllib.request.urlopen(f'{BASE}/sw.js', timeout=5)
    sw = r.read().decode()
    print(f"  sw.js: {r.status} {len(sw)}B")
    if 'gaia-klein' in sw:
        print(f"  Cache name: gaia-klein-v259")
except:
    print(f"  sw.js: NOT FOUND")

# Klein body
try:
    r = urllib.request.urlopen(f'{BASE}/klein-body.html', timeout=5)
    print(f"  klein-body.html: {r.status} {len(r.read())}B")
except:
    print(f"  klein-body.html: NOT FOUND")

print(f"""
=== FULL AXIS SUMMARY ===
  Seed: wave {seed['wave']}
  Pins: {alive} alive / {dead} dead of {alive+dead} total
  Depth: {len(seed.get('depth_levels',[]))} layers (Pluto → Core)
  Blackholes: {axis['state_summary']['total']} ({axis['state_summary']['active']} active)
  Ouroboros position: GUT TOP (intake)
  
  The axis IS the ouroboros:
    Outside → Pluto → Jupiter → Moon → Atmosphere → Membrane → Gut → Brain → Core
    Deep    → 0.12  → 0.18   → 0.25 → 0.32       → 0.38     → 0.5 → 0.62  → 0.78
    
  Blackholes sit at R=0.5 (Gut) — they're the intake mouths.
  The cosmic view renders them with bh-glow.
  The Frame dial scrolls through 13 holes.
  boot.js loads seed → pins tell instruments where to fetch.
""")
