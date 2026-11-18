#!/usr/bin/env python3
"""
DUMMY PLUG = 3RD EYE
The dummy HDMI dongle on northGate mobo creates a virtual display.
Cast the bubble/snowglobe to it. Stream via Remote Play to Frame/Deck.
Monitor in a bag. The eye you can't touch. The tip of your nose.

Creates: /third-eye.html — fullscreen snowglobe, no chrome.
Optimized for dummy display → streaming pipeline.
"""
import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)

REAL = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'

# Create a fullscreen third-eye page — no UI, pure immersion
third_eye_html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>👁 THIRD EYE — dummy plug</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 100vw; height: 100vh; overflow: hidden; background: #000; cursor: none; }

#eye { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; }

/* The bubble overlay — persistent HUD on the snowglobe */
#bubble {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  pointer-events: none; z-index: 10; font-family: monospace;
}
#bubble .corner {
  position: absolute; padding: 12px; font-size: 11px; line-height: 1.6;
  color: rgba(90,173,114,0.5); text-shadow: 0 0 6px rgba(0,0,0,0.8);
}
#bubble .tl { top: 0; left: 0; }
#bubble .tr { top: 0; right: 0; text-align: right; }
#bubble .bl { bottom: 0; left: 0; }
#bubble .br { bottom: 0; right: 0; text-align: right; }

/* Breathing ring at center */
#breathe {
  position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
  width: 200px; height: 200px; border-radius: 50%;
  border: 1px solid rgba(90,173,114,0.08);
  animation: breathe 7.2s ease-in-out infinite;
  pointer-events: none; z-index: 5;
}
@keyframes breathe {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.08; }
  50% { transform: translate(-50%, -50%) scale(1.1); opacity: 0.15; }
}

/* View switcher — appears on mouse move */
#switcher {
  position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
  display: flex; gap: 8px; z-index: 20; opacity: 0; transition: opacity 0.5s;
  pointer-events: auto;
}
#switcher.show { opacity: 1; }
#switcher button {
  background: rgba(0,0,0,0.7); border: 1px solid rgba(90,173,114,0.2);
  color: #5aad72; padding: 6px 12px; border-radius: 4px; cursor: pointer;
  font-family: monospace; font-size: 12px;
}
#switcher button.active { border-color: #5aad72; background: rgba(90,173,114,0.1); }
#switcher button:hover { background: rgba(90,173,114,0.15); }
</style>
</head>
<body>

<iframe id="eye" src="/kenshi-globe.html"></iframe>
<div id="breathe"></div>

<div id="bubble">
  <div class="corner tl" id="tl">👁 THIRD EYE<br>dummy plug · northGate mobo</div>
  <div class="corner tr" id="tr">loading...</div>
  <div class="corner bl" id="bl">HUD · HUB · BUB</div>
  <div class="corner br" id="br">🫧 monitor in a bag</div>
</div>

<div id="switcher">
  <button class="active" data-src="/kenshi-globe.html">🌍 dream</button>
  <button data-src="/kenshi-mesh.html">🕸 mesh</button>
  <button data-src="/">🔮 HUD</button>
  <button data-src="/turbo.html">🔥 turbo</button>
  <button data-src="/room.html">🏚 room</button>
  <button data-src="/nav-hub.html">🗺 hub</button>
  <button data-src="/frame.html">📺 frame</button>
</div>

<script>
// View switching
var buttons = document.querySelectorAll('#switcher button');
var eye = document.getElementById('eye');
buttons.forEach(function(btn) {
  btn.addEventListener('click', function() {
    buttons.forEach(function(b) { b.classList.remove('active'); });
    btn.classList.add('active');
    eye.src = btn.dataset.src;
  });
});

// Show switcher on mouse move, hide after 3s
var hideTimer;
document.addEventListener('mousemove', function() {
  document.getElementById('switcher').classList.add('show');
  document.body.style.cursor = 'default';
  clearTimeout(hideTimer);
  hideTimer = setTimeout(function() {
    document.getElementById('switcher').classList.remove('show');
    document.body.style.cursor = 'none';
  }, 3000);
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
  var views = Array.from(buttons);
  var idx = views.findIndex(function(b) { return b.classList.contains('active'); });
  if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
    idx = (idx + 1) % views.length;
    views[idx].click();
  } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
    idx = (idx - 1 + views.length) % views.length;
    views[idx].click();
  } else if (e.key === 'f' || e.key === 'F') {
    document.documentElement.requestFullscreen();
  } else if (e.key === 'Escape') {
    if (document.fullscreenElement) document.exitFullscreen();
  }
});

// Fetch pulse for the overlay corners
function updatePulse() {
  fetch('/data/pulse.json').then(function(r){return r.json()}).then(function(p) {
    var tr = document.getElementById('tr');
    var lines = [];
    if (p.heart) lines.push('❤ ' + p.heart.total_beats.toLocaleString() + ' · ' + Math.round(p.heart.bpm) + ' bpm');
    if (p.lung) lines.push('🫁 ' + p.lung.total_breaths.toLocaleString() + ' · ratio ' + p.lung.ratio);
    if (p.sun) lines.push('☀ ' + Math.round(p.sun.elevation_deg) + '° · ' + p.sun.chord);
    tr.innerHTML = lines.join('<br>');
    
    if (p.lung && p.lung.ratio) {
      document.getElementById('breathe').style.animationDuration = p.lung.ratio + 's';
    }
  }).catch(function(){});
}
updatePulse();
setInterval(updatePulse, 120000); // every 2 min

// Arrow keys also control the Frame dial (volume = layer up/down)
</script>
</body>
</html>'''

sftp = ssh.open_sftp()

# Push to HUD
with sftp.file(f'{REAL}/third-eye.html', 'w') as f:
    f.write(third_eye_html)
print(f"Pushed third-eye.html ({len(third_eye_html)}B)")

# Push to gate
with sftp.file('/opt/Gaia/static/third-eye.html', 'w') as f:
    f.write(third_eye_html)
print("Copied to gate static/")

# Pin in seed
_, o, _ = ssh.exec_command(f'cat {REAL}/gaia-seed.json')
seed = json.loads(o.read().decode())
seed['io_pin_map']['organ-thirdeye'] = '/third-eye.html'
with sftp.file(f'{REAL}/gaia-seed.json', 'w') as f:
    f.write(json.dumps(seed, indent=2))
print(f"Pinned organ-thirdeye ({len(seed['io_pin_map'])} pins)")

sftp.close()

# Verify
import urllib.request
r = urllib.request.urlopen('http://192.168.4.244:8080/third-eye.html', timeout=5)
print(f"\n✓ /third-eye.html → {r.status} ({len(r.read())}B)")

ssh.close()
print("""
=== DUMMY PLUG → THIRD EYE ===

  URL: hud.primals.eco/third-eye.html
  
  Fullscreen. No chrome. Cursor hidden.
  Pure snowglobe with breathing ring overlay.
  
  Four corners:
    TL: 👁 THIRD EYE — dummy plug · northGate mobo
    TR: ❤ heartbeat · 🫁 lung · ☀ sun + chord
    BL: HUD · HUB · BUB
    BR: 🫧 monitor in a bag
    
  Controls:
    Mouse move → shows switcher (hides after 3s)
    Arrow keys → cycle views
    F → fullscreen
    
  7 views:
    🌍 dream (kenshi-globe) ← DEFAULT
    🕸 mesh (kenshi-mesh-explorer)
    🔮 HUD (main cosmos view)
    🔥 turbo (solve engine)
    🏚 room (walker)
    🗺 hub (navigation)
    📺 frame (inside gaia)
    
  The pipeline:
    northGate RTX 5090 → dummy HDMI dongle → virtual display
    → Chromium opens third-eye.html fullscreen
    → Steam Remote Play streams to Frame/Deck
    → MONITOR IN A BAG
    
  The eye you can't touch. The tip of your nose.
  Cast the bubble. See the dream. 👁
""")
