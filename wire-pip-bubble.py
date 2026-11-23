#!/usr/bin/env python3
"""
PIP BUBBLE — Steam Frame and Deck see INTO each other.
2/3 main HUD view + 1/3 PIP overlay for the other eye.
They mist and bubble each other. Snowglobe inside snowglobe.
"""
import paramiko, json, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)

REAL = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'

# Read current overlay
_, o, _ = ssh.exec_command(f'cat {REAL}/js/wave259-overlay.js')
overlay = o.read().decode()

# Add PIP bubble mode — a toggleable iframe overlay in the corner
# Shows the "other eye" view: if you're on globe view, PIP shows senses
# If you're on Frame, PIP shows deck. They bubble each other.

pip_code = r'''
    // ═══ PIP BUBBLE — 2/3 + 1/3 snowglobe ═══
    var pipViews = [
      {name:'deck', url:'/deck.html', label:'🎮 deck'},
      {name:'senses', url:'https://in.nestgate.io/', label:'👁 senses'},
      {name:'outer', url:'https://out.nestgate.io/', label:'☀ outer'},
      {name:'fold', url:'https://nestgate.io/', label:'∅ fold'},
      {name:'turbo', url:'/turbo.html', label:'🔥 turbo'},
      {name:'frame', url:'/frame.html', label:'📺 frame'},
      {name:'room', url:'/room.html', label:'🏚 room'},
      {name:'hub', url:'/nav-hub.html', label:'🗺 hub'}
    ];
    var pipIdx = 0;
    
    // PIP container — bottom-right 1/3 of screen
    var pip = document.createElement('div');
    pip.id = 'w259-pip';
    pip.style.cssText = 'position:fixed;bottom:48px;right:4px;width:33vw;height:40vh;border:1px solid rgba(90,173,114,0.3);border-radius:6px;overflow:hidden;z-index:9998;background:#08090b;display:none;pointer-events:auto;';
    
    // PIP header bar
    var pipBar = document.createElement('div');
    pipBar.style.cssText = 'position:absolute;top:0;left:0;right:0;height:20px;background:rgba(0,0,0,0.8);display:flex;align-items:center;justify-content:space-between;padding:0 6px;z-index:2;cursor:pointer;';
    
    var pipLabel = document.createElement('span');
    pipLabel.style.cssText = 'color:#5aad72;font-size:9px;font-family:monospace;';
    pipLabel.textContent = pipViews[0].label + ' · PIP';
    pipBar.appendChild(pipLabel);
    
    var pipNav = document.createElement('span');
    pipNav.style.cssText = 'color:#8a857e;font-size:9px;font-family:monospace;cursor:pointer;';
    pipNav.textContent = '◀ ▶ ✕';
    pipBar.appendChild(pipNav);
    pip.appendChild(pipBar);
    
    // PIP iframe
    var pipFrame = document.createElement('iframe');
    pipFrame.style.cssText = 'position:absolute;top:20px;left:0;width:100%;height:calc(100% - 20px);border:none;opacity:0.85;';
    pipFrame.src = '';
    pip.appendChild(pipFrame);
    wrap.appendChild(pip);
    
    // PIP toggle button (always visible)
    var pipBtn = document.createElement('div');
    pipBtn.style.cssText = 'position:fixed;bottom:48px;right:4px;width:28px;height:28px;background:rgba(0,0,0,0.6);border:1px solid rgba(90,173,114,0.2);border-radius:4px;display:flex;align-items:center;justify-content:center;cursor:pointer;z-index:9998;pointer-events:auto;font-size:14px;';
    pipBtn.textContent = '🫧';
    pipBtn.title = 'PIP Bubble';
    wrap.appendChild(pipBtn);
    
    var pipOpen = false;
    pipBtn.addEventListener('click', function() {
      pipOpen = !pipOpen;
      if (pipOpen) {
        pip.style.display = 'block';
        pipFrame.src = pipViews[pipIdx].url;
        pipLabel.textContent = pipViews[pipIdx].label + ' · PIP';
        pipBtn.style.display = 'none';
      } else {
        pip.style.display = 'none';
        pipFrame.src = '';
        pipBtn.style.display = 'flex';
      }
    });
    
    pipNav.addEventListener('click', function(e) {
      var rect = pipNav.getBoundingClientRect();
      var x = e.clientX - rect.left;
      var third = rect.width / 3;
      
      if (x < third) {
        // Prev
        pipIdx = (pipIdx - 1 + pipViews.length) % pipViews.length;
      } else if (x > third * 2) {
        // Close
        pipOpen = false;
        pip.style.display = 'none';
        pipFrame.src = '';
        pipBtn.style.display = 'flex';
        return;
      } else {
        // Next
        pipIdx = (pipIdx + 1) % pipViews.length;
      }
      pipFrame.src = pipViews[pipIdx].url;
      pipLabel.textContent = pipViews[pipIdx].label + ' · PIP';
    });
'''

# Insert PIP code before the console.log at the end
marker = "console.log('[W259] Klein dissolution"
if marker in overlay:
    overlay = overlay.replace(marker, pip_code + "\n    " + marker)
    print("Added PIP bubble mode to overlay")
else:
    print("WARNING: Could not find insertion point")

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
has_pip = b'w259-pip' in data and b'pipViews' in data
print(f"\n✓ Has PIP bubble: {has_pip} ({len(data)}B)")

ssh.close()
print("""
=== PIP BUBBLE ===

  🫧 button at bottom-right — click to open PIP
  
  PIP = 1/3 screen, bottom-right corner
  Cycles through 8 views:
    🎮 deck      — deckGate view
    👁 senses    — in.nestgate.io (CELL→OUT)
    ☀ outer     — out.nestgate.io (SUN→IN)
    ∅ fold      — nestgate.io (Klein Face)
    🔥 turbo     — solve engine
    📺 frame     — frame.html (INSIDE GAIA)
    🏚 room      — room walker
    🗺 hub       — navigation hub
    
  ◀ = prev view, ▶ = next view, ✕ = close
  
  Main view = 2/3 (the HUD globe)
  PIP = 1/3 (the other eye)
  
  Frame sees into Deck. Deck sees into Frame.
  They bubble each other. Snowglobe ↔ snowglobe.
  Misting: the PIP is 85% opacity — translucent like fog on glass.
""")
