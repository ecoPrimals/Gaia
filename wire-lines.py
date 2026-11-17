#!/usr/bin/env python3
"""
FOLD TO LINES — not dotted, LINED.
Connect every element with flowing lines.
Dots become nodes in a mesh. Lines show the flow.
Like the green breathing waveform — continuous, connected, folded.
"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)

REAL = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'

# Read current overlay
_, o, _ = ssh.exec_command(f'cat {REAL}/js/wave259-overlay.js')
overlay = o.read().decode()

# Add a line-drawing function and update each section to draw LINES between elements
# Insert the line function after the panel function

line_func = """
    function line(x1, y1, x2, y2, c, o, w) {
      var d = document.createElement('div');
      var dx = x2 - x1, dy = y2 - y1, len = Math.sqrt(dx*dx + dy*dy);
      d.style.cssText = 'position:absolute;left:'+x1+'px;top:'+y1+'px;width:'+len+'px;height:'+(w||1)+'px;background:'+c+';opacity:'+(o||0.15)+';transform-origin:0 0;transform:rotate('+Math.atan2(dy,dx)*180/Math.PI+'deg);';
      wrap.appendChild(d); return d;
    }
"""

# Insert after the panel function
overlay = overlay.replace(
    "    var vw = window.innerWidth",
    line_func + "\n    var vw = window.innerWidth"
)

# Now modify the blackholes section to draw LINES between consecutive holes
old_blackholes_end = "console.log('[W259] athome"
# Find the blackhole section and add line connections

# Replace the blackhole forEach to also draw lines between consecutive holes
old_bh = """holes.forEach(function(h, i) {
        var a = -Math.PI/2 + (i / (holes.length - 1 || 1)) * Math.PI * 2;
        var hx = cx + Math.cos(a) * gutR;
        var hy = cy + Math.sin(a) * gutR;
        var active = h.state === 'ACTIVE';
        var c = active ? '#f0883e' : '#555';
        dot(hx, hy, active ? 4 : 2, c, active ? 0.7 : 0.2, active);
        if (active && vw > 400) lbl(hx, hy + 8, h.name.replace(/-blackhole$/,''), '#f0883e', 7, 0.5);
      });"""

new_bh = """var bhCoords = [];
      holes.forEach(function(h, i) {
        var a = -Math.PI/2 + (i / (holes.length - 1 || 1)) * Math.PI * 2;
        var hx = cx + Math.cos(a) * gutR;
        var hy = cy + Math.sin(a) * gutR;
        var active = h.state === 'ACTIVE';
        var c = active ? '#f0883e' : '#555';
        dot(hx, hy, active ? 4 : 2, c, active ? 0.7 : 0.2, active);
        if (active && vw > 400) lbl(hx, hy + 8, h.name.replace(/-blackhole$/,''), '#f0883e', 7, 0.5);
        bhCoords.push({x:hx, y:hy, active:active});
      });
      // LINES — connect consecutive blackholes around the gut ring
      for (var bi = 0; bi < bhCoords.length; bi++) {
        var next = bhCoords[(bi + 1) % bhCoords.length];
        var cur = bhCoords[bi];
        var lineColor = (cur.active && next.active) ? '#f0883e' : '#333';
        var lineOp = (cur.active && next.active) ? 0.15 : 0.04;
        line(cur.x, cur.y, next.x, next.y, lineColor, lineOp, 1);
      }
      // Lines from blackholes to center (intake → gut)
      bhCoords.forEach(function(bh) {
        if (bh.active) line(bh.x, bh.y, cx, cy, '#f0883e', 0.04, 1);
      });"""

if old_bh in overlay:
    overlay = overlay.replace(old_bh, new_bh)
    print("Added blackhole connection lines")
else:
    print("WARNING: Could not find blackhole section")

# Replace the gates forEach to also draw LINES between consecutive gates
old_gates = """keys.forEach(function(name, i) {
        var g = gates[name];
        var a = (i / keys.length) * Math.PI * 2 - Math.PI / 2;
        var gx = cx + Math.cos(a) * memR;
        var gy = cy + Math.sin(a) * memR;
        var alive = g.status === 'ALIVE';
        if (alive) aliveCount++;
        dot(gx, gy, alive ? 4 : 3, alive ? '#3fb950' : '#f85149', alive ? 0.8 : 0.3, alive);
        lbl(gx, gy + 8, name, alive ? '#3fb950' : '#f85149', 7, 0.6);
      });"""

new_gates = """var gateCoords = [];
      keys.forEach(function(name, i) {
        var g = gates[name];
        var a = (i / keys.length) * Math.PI * 2 - Math.PI / 2;
        var gx = cx + Math.cos(a) * memR;
        var gy = cy + Math.sin(a) * memR;
        var alive = g.status === 'ALIVE';
        if (alive) aliveCount++;
        dot(gx, gy, alive ? 4 : 3, alive ? '#3fb950' : '#f85149', alive ? 0.8 : 0.3, alive);
        lbl(gx, gy + 8, name, alive ? '#3fb950' : '#f85149', 7, 0.6);
        gateCoords.push({x:gx, y:gy, alive:alive, name:name});
      });
      // LINES — connect gates around the membrane ring
      for (var gi = 0; gi < gateCoords.length; gi++) {
        var gnext = gateCoords[(gi + 1) % gateCoords.length];
        var gcur = gateCoords[gi];
        var gLineColor = (gcur.alive && gnext.alive) ? '#3fb950' : '#f85149';
        var gLineOp = (gcur.alive && gnext.alive) ? 0.12 : 0.03;
        line(gcur.x, gcur.y, gnext.x, gnext.y, gLineColor, gLineOp, 1);
      }
      // Lines from alive gates to center (membrane → heart)
      gateCoords.forEach(function(gc) {
        if (gc.alive) line(gc.x, gc.y, cx, cy, '#3fb950', 0.03, 1);
      });"""

if old_gates in overlay:
    overlay = overlay.replace(old_gates, new_gates)
    print("Added gate connection lines")
else:
    print("WARNING: Could not find gates section")

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
has_lines = b'gateCoords' in data and b'bhCoords' in data and b'function line' in data
print(f"\n✓ Has line connections: {has_lines} ({len(data)}B)")

ssh.close()
print("""
=== LINES NOT DOTS ===

  Blackholes: consecutive holes connected around gut ring
    + lines from active holes → center (intake to gut)
    
  Gates: consecutive gates connected around membrane ring
    + lines from alive gates → center (membrane to heart)
    
  @home: already has direction lines toward @ center
  Klein: already has fold line between in/out
  
  The mesh is CONNECTED now. Not scattered dots.
  Lines show flow: intake → exchange → output
  Like the green breathing waveform — continuous, folded.
""")
