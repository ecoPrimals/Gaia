#!/usr/bin/env python3
"""
Push a JS overlay that fetches our bones and renders them INTO the cosmic view.
cosmic-surfaces.js is the pattern — it hooks into cosmic-view.js after build.
Our bones: blackhole-axis, space-dock, klein-faces, organism-census.
"""
import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)

REAL = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'

# The JS overlay that loads our wave 259 bones into the cosmic view
overlay_js = r'''// wave259-overlay.js — render bones into the cosmic view
// Loads blackhole-axis, space-dock, klein-faces, organism-census
// Uses existing bh-glow gradient + accretion disk from cosmic-view.js
// Pattern: same as cosmic-surfaces.js — hooks into _cosmicView after build
(function() {
  'use strict';
  var NS = 'http://www.w3.org/2000/svg';
  var W = 900, H = 640, cx = 450, cy = 320;

  function el(tag, attrs) {
    var e = document.createElementNS(NS, tag);
    if (attrs) for (var k in attrs) e.setAttribute(k, '' + attrs[k]);
    return e;
  }

  function injectWhenReady() {
    var cv = window._cosmicView;
    if (!cv) { setTimeout(injectWhenReady, 500); return; }
    var svg = document.querySelector('#cosmic-overlay svg, #chipmunk-overlay svg');
    if (!svg) { setTimeout(injectWhenReady, 500); return; }

    console.log('[W259] Injecting wave 259 bones into cosmic view');

    // Create our layer group
    var g259 = el('g', { id: 'wave259-layer', opacity: 0.9 });

    // ═══ 1. BLACKHOLE AXIS — 13 singularities at GUT ring ═══
    fetch('/data/blackhole-axis-259.json').then(function(r) { return r.json(); }).then(function(axis) {
      var bhGroup = el('g', { id: 'w259-blackholes' });
      var holes = axis.blackholes || [];
      
      holes.forEach(function(h) {
        var x = h.cosmic.x, y = h.cosmic.y, r2 = h.cosmic.r;
        var c = h.cosmic.color;
        var active = h.state === 'ACTIVE';
        
        // Black hole core
        bhGroup.appendChild(el('circle', { cx: x, cy: y, r: r2,
          fill: '#000000', stroke: c, 'stroke-width': 0.5, opacity: active ? 0.8 : 0.3 }));
        
        // Glow ring
        if (h.cosmic.glow) {
          bhGroup.appendChild(el('circle', { cx: x, cy: y, r: r2 * 2.5,
            fill: 'url(#bh-glow)', opacity: 0.25 }));
          // Mini accretion disk
          bhGroup.appendChild(el('ellipse', { cx: x, cy: y, rx: r2 * 2, ry: r2 * 0.6,
            fill: 'none', stroke: c, 'stroke-width': 0.3, opacity: 0.15 }));
        }
        
        // Label
        var lbl = el('text', { x: x, y: y + r2 * 2.5 + 6, 'text-anchor': 'middle',
          fill: c, 'font-size': '3px', 'font-family': 'monospace', opacity: active ? 0.5 : 0.2 });
        lbl.textContent = h.name.length > 25 ? h.name.substring(0, 22) + '...' : h.name;
        bhGroup.appendChild(lbl);
        
        // Dial index badge
        var badge = el('text', { x: x - r2 - 2, y: y + 1, 'text-anchor': 'end',
          fill: c, 'font-size': '2.5px', 'font-family': 'monospace', opacity: 0.3 });
        badge.textContent = h.dial_index;
        bhGroup.appendChild(badge);
      });
      
      // Gut ring outline (R=160 from center)
      bhGroup.appendChild(el('circle', { cx: cx, cy: cy, r: 160,
        fill: 'none', stroke: '#f0883e', 'stroke-width': 0.3,
        'stroke-dasharray': '2 4', opacity: 0.08 }));
      var gutLabel = el('text', { x: cx + 162, y: cy - 4, 'text-anchor': 'start',
        fill: '#f0883e', 'font-size': '4px', 'font-family': 'monospace', opacity: 0.15 });
      gutLabel.textContent = 'gut · blackhole intake · R=0.5';
      bhGroup.appendChild(gutLabel);
      
      g259.appendChild(bhGroup);
      console.log('[W259] ' + holes.length + ' blackholes rendered');
    }).catch(function(e) { console.warn('[W259] blackhole-axis:', e); });

    // ═══ 2. KLEIN FACES — in/out/fold markers ═══
    fetch('/data/klein-faces-259.json').then(function(r) { return r.json(); }).then(function(kf) {
      var kleinGroup = el('g', { id: 'w259-klein' });
      var faces = kf.faces || {};
      
      // OUT face — top right (sun position)
      var outX = cx + 200, outY = cy - 120;
      kleinGroup.appendChild(el('circle', { cx: outX, cy: outY, r: 4,
        fill: '#f0e68c', opacity: 0.4 }));
      kleinGroup.appendChild(el('circle', { cx: outX, cy: outY, r: 8,
        fill: 'none', stroke: '#f0e68c', 'stroke-width': 0.3, opacity: 0.15 }));
      var outLbl = el('text', { x: outX, y: outY + 14, 'text-anchor': 'middle',
        fill: '#f0e68c', 'font-size': '4px', 'font-family': 'monospace', opacity: 0.4 });
      outLbl.textContent = 'out.nestgate.io';
      kleinGroup.appendChild(outLbl);
      var outSub = el('text', { x: outX, y: outY + 20, 'text-anchor': 'middle',
        fill: '#f0e68c', 'font-size': '3px', 'font-family': 'monospace', opacity: 0.25 });
      outSub.textContent = 'SUN → IN (TRANS)';
      kleinGroup.appendChild(outSub);
      
      // IN face — bottom left (cell position)
      var inX = cx - 200, inY = cy + 120;
      kleinGroup.appendChild(el('circle', { cx: inX, cy: inY, r: 4,
        fill: '#5aad72', opacity: 0.4 }));
      kleinGroup.appendChild(el('circle', { cx: inX, cy: inY, r: 8,
        fill: 'none', stroke: '#5aad72', 'stroke-width': 0.3, opacity: 0.15 }));
      var inLbl = el('text', { x: inX, y: inY + 14, 'text-anchor': 'middle',
        fill: '#5aad72', 'font-size': '4px', 'font-family': 'monospace', opacity: 0.4 });
      inLbl.textContent = 'in.nestgate.io';
      kleinGroup.appendChild(inLbl);
      var inSub = el('text', { x: inX, y: inY + 20, 'text-anchor': 'middle',
        fill: '#5aad72', 'font-size': '3px', 'font-family': 'monospace', opacity: 0.25 });
      inSub.textContent = 'CELL → OUT (CIS)';
      kleinGroup.appendChild(inSub);
      
      // Fold line connecting them (the Klein crossing)
      kleinGroup.appendChild(el('line', { x1: outX, y1: outY, x2: inX, y2: inY,
        stroke: '#888', 'stroke-width': 0.2, 'stroke-dasharray': '1 3', opacity: 0.1 }));
      // Cross point at center
      kleinGroup.appendChild(el('circle', { cx: cx, cy: cy, r: 1.5,
        fill: '#ffffff', opacity: 0.15 }));
      var crossLbl = el('text', { x: cx + 4, y: cy - 4, 'text-anchor': 'start',
        fill: '#888', 'font-size': '3px', 'font-family': 'monospace', opacity: 0.2 });
      crossLbl.textContent = '//\\\\ fold';
      kleinGroup.appendChild(crossLbl);
      
      g259.appendChild(kleinGroup);
      console.log('[W259] Klein faces rendered');
    }).catch(function(e) { console.warn('[W259] klein-faces:', e); });

    // ═══ 3. ORGANISM CENSUS — gate dots with real status ═══
    fetch('/data/organism-census.json').then(function(r) { return r.json(); }).then(function(census) {
      var orgGroup = el('g', { id: 'w259-organism' });
      var gates = census.gates || {};
      var gateList = Object.keys(gates);
      
      // Spread gates around the membrane ring (R=0.38 = ~120px)
      var memR = 120;
      gateList.forEach(function(name, i) {
        var g = gates[name];
        var angle = (i / gateList.length) * Math.PI * 2 - Math.PI / 2;
        var gx = cx + Math.cos(angle) * memR;
        var gy = cy + Math.sin(angle) * memR;
        var alive = g.status === 'ALIVE';
        var color = alive ? '#3fb950' : '#f85149';
        
        // Gate dot
        orgGroup.appendChild(el('circle', { cx: gx.toFixed(0), cy: gy.toFixed(0), r: 2,
          fill: color, opacity: alive ? 0.6 : 0.3 }));
        
        // Pulse animation for alive gates
        if (alive) {
          var pulse = el('circle', { cx: gx.toFixed(0), cy: gy.toFixed(0), r: 2,
            fill: 'none', stroke: color, 'stroke-width': 0.3, opacity: 0.3 });
          pulse.appendChild(el('animate', { attributeName: 'r', values: '2;5;2',
            dur: (3 + i * 0.5) + 's', repeatCount: 'indefinite' }));
          pulse.appendChild(el('animate', { attributeName: 'opacity', values: '0.3;0;0.3',
            dur: (3 + i * 0.5) + 's', repeatCount: 'indefinite' }));
          orgGroup.appendChild(pulse);
        }
        
        // Label
        var lbl = el('text', { x: gx.toFixed(0), y: (gy + 6).toFixed(0), 'text-anchor': 'middle',
          fill: color, 'font-size': '3px', 'font-family': 'monospace', opacity: 0.4 });
        lbl.textContent = name;
        orgGroup.appendChild(lbl);
      });
      
      // Membrane ring
      orgGroup.appendChild(el('circle', { cx: cx, cy: cy, r: memR,
        fill: 'none', stroke: '#5aad72', 'stroke-width': 0.3,
        'stroke-dasharray': '1 2', opacity: 0.06 }));
      var memLbl = el('text', { x: cx - memR - 4, y: cy, 'text-anchor': 'end',
        fill: '#5aad72', 'font-size': '3.5px', 'font-family': 'monospace', opacity: 0.12 });
      memLbl.textContent = 'membrane · R=0.38';
      orgGroup.appendChild(memLbl);
      
      g259.appendChild(orgGroup);
      console.log('[W259] ' + gateList.length + ' gates rendered on membrane');
    }).catch(function(e) { console.warn('[W259] organism-census:', e); });

    // ═══ 4. DEPTH AXIS — the ouroboros layers ═══
    fetch('/gaia-seed.json').then(function(r) { return r.json(); }).then(function(seed) {
      var depthGroup = el('g', { id: 'w259-depth' });
      var levels = seed.depth_levels || [];
      var maxR = 260; // outer edge of view
      
      levels.forEach(function(dl) {
        var r2 = dl.R * maxR;
        depthGroup.appendChild(el('circle', { cx: cx, cy: cy, r: r2,
          fill: 'none', stroke: '#2a3040', 'stroke-width': 0.15,
          'stroke-dasharray': '0.5 3', opacity: 0.08 }));
        // Label at right edge
        var lx = cx + r2 + 2, ly = cy;
        var lbl = el('text', { x: lx, y: ly, 'text-anchor': 'start',
          fill: '#484f58', 'font-size': '2.5px', 'font-family': 'monospace', opacity: 0.12 });
        lbl.textContent = dl.name + ' · ' + dl.label;
        depthGroup.appendChild(lbl);
      });
      
      g259.appendChild(depthGroup);
      console.log('[W259] ' + levels.length + ' depth levels rendered');
    }).catch(function(e) { console.warn('[W259] gaia-seed:', e); });

    // ═══ 5. WAVE 259 BADGE ═══
    var badge259 = el('g', { id: 'w259-badge' });
    var badgeText = el('text', { x: 20, y: H - 20, 'text-anchor': 'start',
      fill: '#f0883e', 'font-size': '5px', 'font-family': 'monospace', opacity: 0.2 });
    badgeText.textContent = 'wave 259 · 28 pins · 13 blackholes · 3 rings';
    badge259.appendChild(badgeText);
    var badgeHeart = el('text', { x: 20, y: H - 12, 'text-anchor': 'start',
      fill: '#f85149', 'font-size': '4px', 'font-family': 'monospace', opacity: 0.15 });
    badgeHeart.textContent = 'lub-DUB';
    badgeHeart.appendChild(el('animate', { attributeName: 'opacity', values: '0.15;0.4;0.15',
      dur: '2s', repeatCount: 'indefinite' }));
    badge259.appendChild(badgeHeart);
    g259.appendChild(badge259);

    // Insert into the SVG
    svg.appendChild(g259);
    console.log('[W259] Wave 259 overlay complete');
  }

  // Wait for DOM + cosmic view
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { setTimeout(injectWhenReady, 1000); });
  } else {
    setTimeout(injectWhenReady, 1000);
  }
})();
'''

# Push the overlay JS
sftp = ssh.open_sftp()
js_path = f'{REAL}/js/wave259-overlay.js'
with sftp.file(js_path, 'w') as f:
    f.write(overlay_js)
print(f"Pushed wave259-overlay.js ({len(overlay_js)} bytes)")

# Now inject the script tag into senses.html on the gate
# The gate serves senses.html from /opt/Gaia/static/senses.html
print("\n=== INJECTING SCRIPT TAG INTO SENSES.HTML ===")
stdin, stdout, stderr = ssh.exec_command('cat /opt/Gaia/static/senses.html')
senses = stdout.read().decode()

if 'wave259-overlay' in senses:
    print("  Already injected")
else:
    # Find the last </script> or a good injection point
    # cosmic-surfaces.js is loaded at line ~2432, inject after it
    marker = '<script defer src=/js/cosmic-surfaces.js?v=3></script>'
    if marker in senses:
        new_tag = marker + '\n    <script defer src=/js/wave259-overlay.js?v=1></script><!-- WAVE 259 BONES -->'
        senses_new = senses.replace(marker, new_tag)
        
        with sftp.file('/opt/Gaia/static/senses.html', 'w') as f:
            f.write(senses_new)
        print("  ✓ Injected after cosmic-surfaces.js")
    else:
        # Try injecting before </body>
        senses_new = senses.replace('</body>', '    <script defer src=/js/wave259-overlay.js?v=1></script>\n</body>')
        with sftp.file('/opt/Gaia/static/senses.html', 'w') as f:
            f.write(senses_new)
        print("  ✓ Injected before </body>")

# Also push to the HUD data server path (for hud.primals.eco which serves from :8080)
hud_senses = f'{REAL}/senses.html'
stdin, stdout, stderr = ssh.exec_command(f'test -f {hud_senses} && echo EXISTS')
if 'EXISTS' in stdout.read().decode():
    stdin, stdout, stderr = ssh.exec_command(f'cat {hud_senses}')
    hud_s = stdout.read().decode()
    if 'wave259-overlay' not in hud_s:
        if marker in hud_s:
            hud_s = hud_s.replace(marker, marker + '\n    <script defer src=/js/wave259-overlay.js?v=1></script>')
        else:
            hud_s = hud_s.replace('</body>', '    <script defer src=/js/wave259-overlay.js?v=1></script>\n</body>')
        with sftp.file(hud_senses, 'w') as f:
            f.write(hud_s)
        print(f"  ✓ Also injected into HUD copy")

sftp.close()

# Verify the JS is accessible
import urllib.request
try:
    r = urllib.request.urlopen('http://192.168.4.244:8080/js/wave259-overlay.js', timeout=5)
    print(f"\n  wave259-overlay.js on :8080: {r.status} {len(r.read())}B")
except Exception as e:
    print(f"\n  :8080: {e}")

try:
    r = urllib.request.urlopen('http://192.168.4.244:8443/js/wave259-overlay.js', timeout=5)
    print(f"  wave259-overlay.js on :8443: {r.status} {len(r.read())}B")
except Exception as e:
    print(f"  :8443: {e}")

ssh.close()

print("""
=== WAVE 259 OVERLAY PUSHED ===

  Renders INTO the cosmic view:
  
  1. 🕳️ 13 BLACKHOLES — bh-glow + accretion disks at gut ring (R=160)
     Active holes glow orange, dissolved fade grey
     Dial index badges on each hole
     
  2. 🌞🔬 KLEIN FACES — out/in/fold markers
     out.nestgate.io (gold, top right) = SUN → IN
     in.nestgate.io (green, bottom left) = CELL → OUT  
     Fold line crosses at center (//\\\\)
     
  3. 🟢 ORGANISM GATES — census dots on membrane ring (R=120)
     Alive = green pulse, Down = red static
     Gate names labeled
     
  4. 📏 DEPTH AXIS — 8 ouroboros layers as concentric rings
     Pluto→Jupiter→Moon→Atmosphere→Membrane→Gut→Brain→Core
     
  5. 🏷️ WAVE 259 BADGE — bottom left, lub-DUB heartbeat

  The bones are no longer just data. They're IN the HUD.
""")
