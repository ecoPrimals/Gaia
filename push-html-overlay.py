#!/usr/bin/env python3
"""
Rewrite overlay as HTML elements — works on Canvas OR SVG pages.
Creates absolute-positioned dots/labels over the viewport.
"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)

REAL = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'

overlay_js = r'''// wave259-overlay.js v2 — HTML overlay, works on Canvas OR SVG
// Renders bone data as positioned HTML elements over the viewport
(function() {
  'use strict';

  function build() {
    // Create overlay container
    var wrap = document.createElement('div');
    wrap.id = 'w259';
    wrap.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:50;overflow:hidden;';
    document.body.appendChild(wrap);

    var vw = window.innerWidth, vh = window.innerHeight;
    var cx = vw * 0.5, cy = vh * 0.5;

    function dot(x, y, r, color, opacity, pulse) {
      var d = document.createElement('div');
      d.style.cssText = 'position:absolute;border-radius:50%;transform:translate(-50%,-50%);' +
        'left:' + x + 'px;top:' + y + 'px;width:' + (r*2) + 'px;height:' + (r*2) + 'px;' +
        'background:' + color + ';opacity:' + opacity + ';';
      if (pulse) d.style.animation = 'w259pulse ' + (2 + Math.random()*2) + 's ease-in-out infinite';
      wrap.appendChild(d);
      return d;
    }

    function ring(x, y, r, color, opacity) {
      var d = document.createElement('div');
      d.style.cssText = 'position:absolute;border-radius:50%;transform:translate(-50%,-50%);' +
        'left:' + x + 'px;top:' + y + 'px;width:' + (r*2) + 'px;height:' + (r*2) + 'px;' +
        'border:1px solid ' + color + ';opacity:' + opacity + ';background:transparent;';
      wrap.appendChild(d);
      return d;
    }

    function label(x, y, text, color, size, opacity) {
      var l = document.createElement('div');
      l.style.cssText = 'position:absolute;transform:translate(-50%,0);white-space:nowrap;' +
        'left:' + x + 'px;top:' + y + 'px;color:' + color + ';font-size:' + size + 'px;' +
        'font-family:monospace;opacity:' + opacity + ';pointer-events:none;';
      l.textContent = text;
      wrap.appendChild(l);
      return l;
    }

    // Inject pulse animation
    var style = document.createElement('style');
    style.textContent = '@keyframes w259pulse{0%,100%{opacity:0.4;transform:translate(-50%,-50%) scale(1)}50%{opacity:0.8;transform:translate(-50%,-50%) scale(1.5)}}' +
      '@keyframes w259breathe{0%,100%{opacity:0.15}50%{opacity:0.4}}';
    document.head.appendChild(style);

    // Scale factor — map cosmic coords (900x640) to viewport
    var sx = vw / 900, sy = vh / 640;
    function mx(x) { return x * sx; }
    function my(y) { return y * sy; }

    // ═══ 1. DEPTH RINGS ═══
    fetch('/gaia-seed.json').then(function(r){return r.json()}).then(function(seed) {
      var levels = seed.depth_levels || [];
      var maxR = Math.min(vw, vh) * 0.42;
      levels.forEach(function(dl) {
        var r2 = dl.R * maxR;
        ring(cx, cy, r2, '#2a3040', 0.06);
        label(cx + r2 + 4, cy - 2, dl.name, '#484f58', 8, 0.1);
      });
      // Pin count badge
      var pins = Object.keys(seed.io_pin_map || {}).length;
      label(12, vh - 50, 'wave ' + seed.wave + ' · ' + pins + ' pins', '#f0883e', 10, 0.2);
    }).catch(function(){});

    // ═══ 2. BLACKHOLES on gut ring ═══
    fetch('/data/blackhole-axis-259.json').then(function(r){return r.json()}).then(function(axis) {
      var gutR = Math.min(vw, vh) * 0.26;
      ring(cx, cy, gutR, '#f0883e', 0.04);
      label(cx + gutR + 4, cy - 2, 'gut · intake', '#f0883e', 8, 0.08);

      var holes = axis.blackholes || [];
      holes.forEach(function(h) {
        var angle = -Math.PI/2 + (h.dial_index / 12) * Math.PI - Math.PI/2;
        var hx = cx + Math.cos(angle) * gutR;
        var hy = cy + Math.sin(angle) * gutR;
        var active = h.state === 'ACTIVE';
        var c = active ? '#f0883e' : (h.state === 'DISSOLVED' ? '#333' : '#666');
        var sz = active ? 4 : 2;

        dot(hx, hy, sz, '#000', 0.7, false);
        dot(hx, hy, sz + 2, c, active ? 0.3 : 0.1, active);
        
        // Only label a few key ones to avoid clutter
        if (h.dial_index % 3 === 0 || h.state !== 'ACTIVE') {
          var short = h.name.length > 20 ? h.name.substring(0,18) + '..' : h.name;
          label(hx, hy + sz + 4, short, c, 7, active ? 0.3 : 0.12);
        }
      });

      // Summary
      var s = axis.state_summary;
      label(12, vh - 38, s.active + ' active · ' + s.dormant + ' dormant · ' + s.dissolved + ' dissolved', '#f0883e', 8, 0.15);
    }).catch(function(){});

    // ═══ 3. GATES on membrane ring ═══
    fetch('/data/organism-census.json').then(function(r){return r.json()}).then(function(census) {
      var memR = Math.min(vw, vh) * 0.2;
      ring(cx, cy, memR, '#5aad72', 0.04);

      var gates = census.gates || {};
      var keys = Object.keys(gates);
      keys.forEach(function(name, i) {
        var g = gates[name];
        var angle = (i / keys.length) * Math.PI * 2 - Math.PI / 2;
        var gx = cx + Math.cos(angle) * memR;
        var gy = cy + Math.sin(angle) * memR;
        var alive = g.status === 'ALIVE';
        var c = alive ? '#3fb950' : '#f85149';
        
        dot(gx, gy, 3, c, alive ? 0.5 : 0.2, alive);
        label(gx, gy + 6, name, c, 7, 0.3);
      });
    }).catch(function(){});

    // ═══ 4. KLEIN FACES ═══
    fetch('/data/klein-faces-259.json').then(function(r){return r.json()}).then(function(kf) {
      // OUT — top right
      var outX = cx + vw * 0.22, outY = cy - vh * 0.3;
      dot(outX, outY, 5, '#f0e68c', 0.3, true);
      label(outX, outY + 10, 'out.nestgate.io', '#f0e68c', 9, 0.3);
      label(outX, outY + 22, 'SUN → IN', '#f0e68c', 7, 0.15);

      // IN — bottom left
      var inX = cx - vw * 0.22, inY = cy + vh * 0.3;
      dot(inX, inY, 5, '#5aad72', 0.3, true);
      label(inX, inY + 10, 'in.nestgate.io', '#5aad72', 9, 0.3);
      label(inX, inY + 22, 'CELL → OUT', '#5aad72', 7, 0.15);

      // Fold line (CSS)
      var line = document.createElement('div');
      var dx = outX - inX, dy = outY - inY;
      var len = Math.sqrt(dx*dx + dy*dy);
      var angle = Math.atan2(dy, dx) * 180 / Math.PI;
      line.style.cssText = 'position:absolute;left:' + inX + 'px;top:' + inY + 'px;' +
        'width:' + len + 'px;height:1px;background:linear-gradient(90deg,#5aad72,transparent,#f0e68c);' +
        'opacity:0.06;transform-origin:0 0;transform:rotate(' + angle + 'deg);';
      wrap.appendChild(line);

      // Fold point at center
      dot(cx, cy, 2, '#fff', 0.1, false);
      label(cx + 6, cy - 8, '//\\\\ fold', '#888', 7, 0.12);
    }).catch(function(){});

    // ═══ 5. HEARTBEAT ═══
    var heart = document.createElement('div');
    heart.style.cssText = 'position:absolute;left:12px;bottom:12px;color:#f85149;font-size:10px;' +
      'font-family:monospace;opacity:0.15;animation:w259breathe 2s ease-in-out infinite;pointer-events:none;';
    heart.textContent = 'lub-DUB';
    wrap.appendChild(heart);

    console.log('[W259] HTML overlay rendered — bones IN the HUD');
  }

  // Wait for page to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { setTimeout(build, 2000); });
  } else {
    setTimeout(build, 2000);
  }

  // Rebuild on resize
  window.addEventListener('resize', function() {
    var old = document.getElementById('w259');
    if (old) old.remove();
    setTimeout(build, 500);
  });
})();
'''

# Push the updated overlay
sftp = ssh.open_sftp()
js_path = f'{REAL}/js/wave259-overlay.js'
with sftp.file(js_path, 'w') as f:
    f.write(overlay_js)
print(f"Pushed wave259-overlay.js v2 ({len(overlay_js)} bytes)")

# Also copy to gate static
with sftp.file('/opt/Gaia/static/js/wave259-overlay.js', 'w') as f:
    f.write(overlay_js)
print("Copied to gate static/js/")
sftp.close()

# Verify
import urllib.request
r = urllib.request.urlopen('http://192.168.4.244:8080/js/wave259-overlay.js', timeout=5)
print(f"\n✓ :8080/js/wave259-overlay.js: {r.status} {len(r.read())}B")

ssh.close()

print("""
=== OVERLAY v2 — HTML ELEMENTS OVER VIEWPORT ===

  Works on Canvas AND SVG pages.
  No dependency on _cosmicView or specific SVG.
  Creates positioned HTML dots/labels/rings over the viewport.
  
  Reload hud.primals.eco — bones will appear as:
  
    ◯ Depth rings (8 concentric, grey-blue)
    ● Blackholes on gut ring (orange glow, pulsing)  
    ● Gates on membrane ring (green=alive, red=down)
    ● Klein faces (gold=out, green=in, fold line)
    └ lub-DUB heartbeat at bottom left
    
  Responsive — rebuilds on window resize.
""")
