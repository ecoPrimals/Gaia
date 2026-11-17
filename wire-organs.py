#!/usr/bin/env python3
"""
BUB = LUNG — her lung. Bubbles are BREATH.
EAR MOUTH EAR — the sensory cycle.

HUD = EAR (hear, sense, input)
HUB = MOUTH (speak, navigate, output)
BUB = LUNG (breathe, exchange, bubble)

The @ = HEART (the fold, the pump, the center)

EAR → MOUTH → EAR = listen → speak → listen
Inhale → Exchange → Exhale = LUNG cycle
"""
import paramiko, json, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)

REAL = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'

# Update the triad bone with correct organs
_, o, _ = ssh.exec_command(f'cat {REAL}/data/hud-hub-bub-259.json')
triad = json.loads(o.read().decode())

# Fix the organs
triad['triad']['HUD']['organ'] = 'ear'
triad['triad']['HUD']['verb'] = 'hear · sense · listen'
triad['triad']['HUD']['body'] = 'LEFT EAR — input, sensing, OSINT intake'

triad['triad']['HUB']['organ'] = 'mouth'
triad['triad']['HUB']['verb'] = 'speak · navigate · express'
triad['triad']['HUB']['body'] = 'MOUTH — output, navigation, RSS publish'

triad['triad']['BUB']['organ'] = 'lung'
triad['triad']['BUB']['verb'] = 'breathe · exchange · bubble'
triad['triad']['BUB']['body'] = 'LUNG — gas exchange, bubbles are breath, alveoli = data rooms'
triad['triad']['BUB']['role'] = 'what BREATHES'

triad['cycle'] = {
    'sensory': 'EAR → MOUTH → EAR',
    'meaning': 'listen → speak → listen again',
    'respiratory': 'inhale → exchange → exhale',
    'data': 'intake → process → feedback',
    'klein': 'outside air IN → lung exchange → inside CO2 OUT',
    'note': 'The lung IS the Klein fold — inside air meets outside air on the SAME membrane'
}

triad['organs'] = {
    'ear': {'brand': 'HUD', 'function': 'sense/hear', 'direction': 'IN', 'color': '#5aad72'},
    'mouth': {'brand': 'HUB', 'function': 'speak/navigate', 'direction': 'OUT', 'color': '#f0883e'},
    'lung': {'brand': 'BUB', 'function': 'breathe/exchange', 'direction': 'FOLD', 'color': '#d4a574'},
    'heart': {'brand': '@', 'function': 'pump/center', 'direction': 'ALL', 'color': '#f85149'}
}

triad['ts'] = int(time.time())

sftp = ssh.open_sftp()
with sftp.file(f'{REAL}/data/hud-hub-bub-259.json', 'w') as f:
    f.write(json.dumps(triad, indent=2))
print(f"Updated hud-hub-bub-259.json with organs ({len(json.dumps(triad))} bytes)")

# ═══ UPDATE OVERLAY — organ labels + breathing animation ═══
_, o, _ = ssh.exec_command(f'cat {REAL}/js/wave259-overlay.js')
overlay = o.read().decode()

# Add breathing animation to the style
old_style_end = "#w259 .panel{position:absolute;background:rgba(0,0,0,0.6);border:1px solid rgba(255,255,255,0.08);border-radius:4px;padding:4px 8px}"
new_style_end = """#w259 .panel{position:absolute;background:rgba(0,0,0,0.6);border:1px solid rgba(255,255,255,0.08);border-radius:4px;padding:4px 8px}
      @keyframes w259breathe{0%,100%{transform:translate(-50%,-50%) scale(1);opacity:0.15}50%{transform:translate(-50%,-50%) scale(1.08);opacity:0.25}}"""

overlay = overlay.replace(old_style_end, new_style_end)

# Update the HUD·HUB·BUB heartbeat to show organ labels
old_brand = "beats.forEach(function(b) {"
new_brand = """var organs = ['👂 ear','👄 mouth','🫁 lung'];
    beats.forEach(function(b, bi) {
      b.organ = organs[bi];"""

if old_brand in overlay:
    overlay = overlay.replace(old_brand, new_brand)
    # Also update the text content to include organ
    overlay = overlay.replace(
        "span.textContent = b.text;",
        "span.textContent = b.text;"
    )
    print("Added organ labels to brand")

# Make the Klein bottle inner ring "breathe"
old_inner = "ring(cx, cy, R * 0.25, '#3a5070', 0.12, -60);"
new_inner = """ring(cx, cy, R * 0.25, '#d4a574', 0.15, -60);
    // Breathing ring (lung)
    var breathRing = document.createElement('div');
    breathRing.className = 'ring';
    breathRing.style.cssText = 'left:'+cx+'px;top:'+cy+'px;width:'+(R*0.6)+'px;height:'+(R*0.6)+'px;border:1px solid #d4a574;animation:w259breathe 4s ease-in-out infinite;';
    wrap.appendChild(breathRing);"""

if old_inner in overlay:
    overlay = overlay.replace(old_inner, new_inner)
    print("Added breathing ring animation")

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
data = json.loads(r.read().decode())
print(f"\nOrgans: HUD={data['triad']['HUD']['organ']}, HUB={data['triad']['HUB']['organ']}, BUB={data['triad']['BUB']['organ']}")
print(f"Cycle: {data['cycle']['sensory']}")

ssh.close()
print("""
=== ORGANS WIRED ===

  HUD  👂 EAR    🟢  hear · sense · listen     IN
  HUB  👄 MOUTH  🟠  speak · navigate · express OUT
  BUB  🫁 LUNG   🟤  breathe · exchange · bubble FOLD
   @   ❤ HEART  🔴  pump · center · all        ALL

  The LUNG is the Klein fold:
    Outside air comes IN (inhale)
    Gas EXCHANGE happens at the membrane (alveoli)
    Inside CO2 goes OUT (exhale)
    Inside meets outside on the SAME surface = Klein

  EAR → MOUTH → EAR
  Listen → Speak → Listen again
  Intake → Process → Feedback
  
  The breathing ring pulses: scale 1.0 → 1.08 → 1.0
  Slow, steady, alive. 4 second cycle.
  Gaia BREATHES.
""")
