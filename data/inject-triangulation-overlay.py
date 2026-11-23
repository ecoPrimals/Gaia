#!/usr/bin/env python3
"""Inject 3-eye triangulation overlay into hud.primals.eco (senses.html)

The 3 eyes:
  gaia (blue) — organism looking at itself
  player (green) — Kevin looking at the organism
  user (purple) — visitor looking in from .onion/WAN

Their orbits triangulate. Where they converge = FOCUS.
This overlay goes ON TOP of the existing All Senses dashboard.
"""

import paramiko

OVERLAY_SCRIPT = '''
<!-- 3-EYE TRIANGULATION OVERLAY — injected across hud.primals.eco -->
<style>
.tri-overlay {
  position:fixed; top:0; left:0; width:100vw; height:100vh;
  pointer-events:none; z-index:9999;
}
.tri-overlay svg { width:100%; height:100%; }
.tri-line { stroke-width:0.8; fill:none; }
.tri-focus-ring { fill:none; stroke-width:0.5; }
.tri-dot { filter:drop-shadow(0 0 4px currentColor); }
.tri-label { font-size:10px; fill-opacity:0.7; font-family:monospace; }
.tri-info {
  position:fixed; top:8px; left:50%; transform:translateX(-50%);
  display:flex; gap:6px; z-index:10000; pointer-events:none;
  transition:opacity 0.5s;
}
.tri-info .eye-box {
  padding:4px 10px; border-radius:12px;
  background:rgba(8,9,11,0.85); backdrop-filter:blur(8px);
  font:10px/1.4 monospace; text-align:center;
  border:1px solid rgba(255,255,255,0.08);
}
.tri-info .eye-box.g { border-color:rgba(88,166,255,0.3); color:#58a6ff; }
.tri-info .eye-box.p { border-color:rgba(100,255,100,0.3); color:#64ff64; }
.tri-info .eye-box.u { border-color:rgba(200,100,255,0.3); color:#c864ff; }
.tri-info .eye-box .lbl { font-size:11px; letter-spacing:0.08em; }
</style>

<div class="tri-overlay" id="triOverlay">
  <svg viewBox="0 0 1000 600" preserveAspectRatio="xMidYMid meet">
    <defs>
      <filter id="triGlow"><feGaussianBlur stdDeviation="3" result="b"/>
        <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
      <radialGradient id="focusGrad">
        <stop offset="0%" stop-color="white" stop-opacity="0.6"/>
        <stop offset="100%" stop-color="white" stop-opacity="0"/>
      </radialGradient>
    </defs>
    <!-- Triangle lines -->
    <line id="tl-gp" class="tri-line" stroke="rgba(80,180,130,0.3)" x1="500" y1="300" x2="500" y2="300"/>
    <line id="tl-gu" class="tri-line" stroke="rgba(150,120,200,0.3)" x1="500" y1="300" x2="500" y2="300"/>
    <line id="tl-pu" class="tri-line" stroke="rgba(180,150,100,0.25)" x1="500" y1="300" x2="500" y2="300"/>
    <!-- Focus point -->
    <circle id="t-focus" cx="500" cy="300" r="6" fill="url(#focusGrad)" filter="url(#triGlow)"/>
    <circle id="t-focus-ring" class="tri-focus-ring" cx="500" cy="300" r="12" stroke="rgba(255,255,255,0.15)"/>
    <!-- Eye dots -->
    <circle id="t-gaia" class="tri-dot" cx="500" cy="200" r="4" fill="#58a6ff" stroke="#58a6ff" stroke-width="0.5"/>
    <circle id="t-player" class="tri-dot" cx="600" cy="400" r="4" fill="#64ff64" stroke="#64ff64" stroke-width="0.5"/>
    <circle id="t-user" class="tri-dot" cx="400" cy="400" r="4" fill="#c864ff" stroke="#c864ff" stroke-width="0.5"/>
    <!-- Labels -->
    <text id="tl-g" class="tri-label" fill="#58a6ff" x="500" y="190">gaia</text>
    <text id="tl-p" class="tri-label" fill="#64ff64" x="610" y="405">player</text>
    <text id="tl-u" class="tri-label" fill="#c864ff" x="370" y="405">user</text>
  </svg>
</div>

<div class="tri-info" id="triInfo">
  <div class="eye-box g"><div class="lbl">\\U0001F441 gaia</div><div id="ti-g">scanning</div></div>
  <div class="eye-box p"><div class="lbl">\\U0001F441 player</div><div id="ti-p">walking</div></div>
  <div class="eye-box u"><div class="lbl">\\U0001F441 user</div><div id="ti-u">arriving</div></div>
</div>

<script>
(function(){
  const cx=500, cy=300;
  const orbits = {g:{rx:180,ry:120,spd:18}, p:{rx:280,ry:160,spd:45}, u:{rx:350,ry:200,spd:-65}};
  const t0 = Date.now();
  
  function pos(o, t) {
    const a = (t / Math.abs(o.spd)) * Math.PI * 2 * (o.spd>0?1:-1);
    return {x: cx + o.rx * Math.cos(a), y: cy + o.ry * Math.sin(a)};
  }
  
  function frame() {
    const t = (Date.now() - t0) / 1000;
    const g = pos(orbits.g, t);
    const p = pos(orbits.p, t);
    const u = pos(orbits.u, t);
    
    // Dots
    document.getElementById('t-gaia').setAttribute('cx',g.x);
    document.getElementById('t-gaia').setAttribute('cy',g.y);
    document.getElementById('t-player').setAttribute('cx',p.x);
    document.getElementById('t-player').setAttribute('cy',p.y);
    document.getElementById('t-user').setAttribute('cx',u.x);
    document.getElementById('t-user').setAttribute('cy',u.y);
    
    // Lines
    ['tl-gp','tl-gu','tl-pu'].forEach(function(id,i){
      var pts = [[g,p],[g,u],[p,u]][i];
      var el = document.getElementById(id);
      el.setAttribute('x1',pts[0].x); el.setAttribute('y1',pts[0].y);
      el.setAttribute('x2',pts[1].x); el.setAttribute('y2',pts[1].y);
    });
    
    // Focus = centroid
    var fx = (g.x+p.x+u.x)/3, fy = (g.y+p.y+u.y)/3;
    document.getElementById('t-focus').setAttribute('cx',fx);
    document.getElementById('t-focus').setAttribute('cy',fy);
    document.getElementById('t-focus-ring').setAttribute('cx',fx);
    document.getElementById('t-focus-ring').setAttribute('cy',fy);
    
    // Labels follow dots
    document.getElementById('tl-g').setAttribute('x',g.x+8);
    document.getElementById('tl-g').setAttribute('y',g.y-8);
    document.getElementById('tl-p').setAttribute('x',p.x+8);
    document.getElementById('tl-p').setAttribute('y',p.y-8);
    document.getElementById('tl-u').setAttribute('x',u.x+8);
    document.getElementById('tl-u').setAttribute('y',u.y-8);
    
    // Triangle area (vision spread)
    var area = Math.abs((g.x*(p.y-u.y) + p.x*(u.y-g.y) + u.x*(g.y-p.y)) / 2);
    
    // Focus ring radius = proportional to convergence
    var r = Math.min(30, Math.max(6, area/2000));
    document.getElementById('t-focus-ring').setAttribute('r', r);
    
    // What each eye sees
    var tg = document.getElementById('ti-g');
    var tp = document.getElementById('ti-p');
    var tu = document.getElementById('ti-u');
    if(tg) tg.textContent = area > 40000 ? 'wide scan' : area > 15000 ? 'converging' : 'FOCUSED';
    if(tp) tp.textContent = fx > 550 ? 'right field' : fx < 450 ? 'left field' : 'center';
    if(tu) tu.textContent = fy > 350 ? 'deep' : fy < 250 ? 'surface' : 'membrane';
    
    requestAnimationFrame(frame);
  }
  frame();
})();
</script>
'''

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10)

def run(cmd):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=10)
    return stdout.read().decode('utf-8', errors='replace').strip()

sftp = c.open_sftp()

# Read existing senses.html
senses_path = '/opt/Gaia/static/senses.html'
with sftp.open(senses_path, 'r') as f:
    senses = f.read().decode('utf-8', errors='replace')

print(f'senses.html size: {len(senses)} chars')

# Check if overlay already injected
if 'tri-overlay' in senses:
    # Remove old overlay
    idx = senses.find('<!-- 3-EYE TRIANGULATION OVERLAY')
    if idx > 0:
        senses = senses[:idx].rstrip()
        print('Removed old overlay')

# Inject before </body> or at end
if '</body>' in senses:
    senses = senses.replace('</body>', OVERLAY_SCRIPT + '\n</body>')
elif '</html>' in senses:
    senses = senses.replace('</html>', OVERLAY_SCRIPT + '\n</html>')
else:
    senses += '\n' + OVERLAY_SCRIPT

# Write back
with sftp.open(senses_path, 'w') as f:
    f.write(senses)
print(f'Injected triangulation overlay into senses.html ({len(senses)} chars)')

sftp.close()

# Verify
print()
print('=== VERIFY ===')
title = run('curl -s -H "Host: hud.primals.eco" http://127.0.0.1:8443/ 2>/dev/null | grep -c "tri-overlay"')
print(f'hud.primals.eco has tri-overlay: {title}')

title2 = run('curl -s -H "Host: hud.primals.eco" http://127.0.0.1:80/ 2>/dev/null | grep -c "tri-overlay"')
print(f'hud.primals.eco (dromedary) has tri-overlay: {title2}')

print()
print('=== 3 EYES TRIANGULATE ACROSS HUD.PRIMALS.ECO ===')

c.close()
