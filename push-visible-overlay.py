#!/usr/bin/env python3
"""
VISIBLE OVERLAY — The Glass. The Pool. The Watchtower. The Origin.
Everything was there but invisible. Now it SHINES.
"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)

REAL = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'

overlay_js = r'''// wave259-overlay.js v4 — THE GLASS · THE WATCHTOWER · ORIGIN
// ALL IO on ONE surface. Klein dissolution. VISIBLE.
(function() {
  'use strict';

  function build() {
    if (document.getElementById('w259')) document.getElementById('w259').remove();

    var wrap = document.createElement('div');
    wrap.id = 'w259';
    wrap.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:9999;overflow:hidden;font-family:monospace;';
    document.body.appendChild(wrap);

    var style = document.createElement('style');
    style.textContent = [
      '@keyframes w259p{0%,100%{opacity:0.5;transform:translate(-50%,-50%) scale(1)}50%{opacity:1;transform:translate(-50%,-50%) scale(1.5)}}',
      '@keyframes w259b{0%,100%{opacity:0.3}50%{opacity:0.8}}',
      '@keyframes w259spin{from{transform:translate(-50%,-50%) rotate(0deg)}to{transform:translate(-50%,-50%) rotate(360deg)}}',
      '#w259 .dot{position:absolute;border-radius:50%;transform:translate(-50%,-50%)}',
      '#w259 .ring{position:absolute;border-radius:50%;transform:translate(-50%,-50%);background:transparent}',
      '#w259 .lbl{position:absolute;transform:translate(-50%,0);white-space:nowrap;text-shadow:0 0 4px #000,0 0 8px #000}',
      '#w259 .stat{position:absolute;white-space:nowrap;text-shadow:0 0 6px #000,0 0 12px #000}',
      '#w259 .panel{position:absolute;background:rgba(0,0,0,0.6);border:1px solid rgba(255,255,255,0.08);border-radius:4px;padding:4px 8px}',
    ].join('\n');
    document.head.appendChild(style);

    var vw = window.innerWidth, vh = window.innerHeight;
    var cx = vw / 2, cy = vh / 2;
    var R = Math.min(vw, vh) * 0.38;

    function dot(x, y, r, c, o, pulse) {
      var d = document.createElement('div');
      d.className = 'dot';
      d.style.cssText = 'left:'+x+'px;top:'+y+'px;width:'+(r*2)+'px;height:'+(r*2)+'px;background:'+c+';opacity:'+o+';box-shadow:0 0 '+(r*2)+'px '+c+';';
      if (pulse) d.style.animation = 'w259p '+(1.5+Math.random()*2)+'s ease-in-out infinite';
      wrap.appendChild(d); return d;
    }
    function ring(x, y, r, c, o, spin) {
      var d = document.createElement('div');
      d.className = 'ring';
      d.style.cssText = 'left:'+x+'px;top:'+y+'px;width:'+(r*2)+'px;height:'+(r*2)+'px;border:1px solid '+c+';opacity:'+o+';';
      if (spin) d.style.animation = 'w259spin '+spin+'s linear infinite';
      wrap.appendChild(d); return d;
    }
    function lbl(x, y, t, c, s, o) {
      var l = document.createElement('div');
      l.className = 'lbl';
      l.style.cssText = 'left:'+x+'px;top:'+y+'px;color:'+c+';font-size:'+s+'px;opacity:'+o+';';
      l.textContent = t;
      wrap.appendChild(l); return l;
    }
    function panel(x, y, html, anchor) {
      var p = document.createElement('div');
      p.className = 'panel';
      var ax = anchor === 'right' ? 'right:'+x+'px;' : 'left:'+x+'px;';
      var ay = anchor === 'bottom' ? 'bottom:'+y+'px;' : 'top:'+y+'px;';
      p.style.cssText = ax + ay + 'color:#c8c8c8;font-size:10px;line-height:1.6;';
      p.innerHTML = html;
      wrap.appendChild(p); return p;
    }

    // ═══ DEPTH RINGS (ouroboros skeleton — visible!) ═══
    var depthColors = ['#1a2a40','#1e3048','#223650','#263c58','#2a4260','#2e4868','#324e70','#366078'];
    for (var i = 0; i < 8; i++) {
      var rr = R * (0.3 + i * 0.1);
      ring(cx, cy, rr, depthColors[i] || '#2a4060', 0.25);
    }

    // ═══ KLEIN BOTTLE (counter-rotating rings) ═══
    ring(cx, cy, R * 0.98, '#3a5070', 0.15, 180);
    ring(cx, cy, R * 0.25, '#3a5070', 0.12, -60);

    // ═══ GUT RING (blackholes orbit here) ═══
    var gutR = R * 0.65;
    ring(cx, cy, gutR, '#f0883e', 0.12, 120);

    // ═══ MEMBRANE RING (gates orbit here) ═══
    var memR = R * 0.5;
    ring(cx, cy, memR, '#3fb950', 0.12, 90);

    // ═══ LEFT PANEL — status ═══
    var leftLines = [];

    // ═══ SEED DATA ═══
    fetch('/gaia-seed.json').then(function(r){return r.json()}).then(function(seed) {
      var pins = Object.keys(seed.io_pin_map || {}).length;
      var levels = seed.depth_levels || [];
      var el = document.getElementById('w259-left');
      if (el) el.innerHTML = '<span style="color:#f0883e">▲</span> wave ' + seed.wave + ' · ' + pins + ' pins · ' + levels.length + ' depth<br>' + el.innerHTML;
    }).catch(function(){});

    // ═══ BLACKHOLES ═══
    fetch('/data/blackhole-axis-259.json').then(function(r){return r.json()}).then(function(axis) {
      var holes = axis.blackholes || [];
      holes.forEach(function(h, i) {
        var a = -Math.PI/2 + (i / (holes.length - 1 || 1)) * Math.PI * 2;
        var hx = cx + Math.cos(a) * gutR;
        var hy = cy + Math.sin(a) * gutR;
        var active = h.state === 'ACTIVE';
        var c = active ? '#f0883e' : '#555';
        dot(hx, hy, active ? 4 : 2, c, active ? 0.7 : 0.2, active);
        if (active && vw > 400) lbl(hx, hy + 8, h.name.replace(/-blackhole$/,''), '#f0883e', 7, 0.5);
      });
      var el = document.getElementById('w259-left');
      if (el) el.innerHTML += '<span style="color:#f0883e">◉</span> ' + axis.state_summary.active + '/' + axis.state_summary.total + ' blackholes · gut<br>';
    }).catch(function(){});

    // ═══ GATES ═══
    fetch('/data/organism-census.json').then(function(r){return r.json()}).then(function(census) {
      var gates = census.gates || {};
      var keys = Object.keys(gates);
      var aliveCount = 0;
      keys.forEach(function(name, i) {
        var g = gates[name];
        var a = (i / keys.length) * Math.PI * 2 - Math.PI / 2;
        var gx = cx + Math.cos(a) * memR;
        var gy = cy + Math.sin(a) * memR;
        var alive = g.status === 'ALIVE';
        if (alive) aliveCount++;
        dot(gx, gy, alive ? 4 : 3, alive ? '#3fb950' : '#f85149', alive ? 0.8 : 0.3, alive);
        lbl(gx, gy + 8, name, alive ? '#3fb950' : '#f85149', 7, 0.6);
      });
      var el = document.getElementById('w259-left');
      if (el) el.innerHTML += '<span style="color:#3fb950">●</span> ' + aliveCount + '/' + keys.length + ' gates · membrane<br>';
    }).catch(function(){});

    // ═══ KLEIN FACES (crossing markers) ═══
    fetch('/data/klein-faces-259.json').then(function(r){return r.json()}).then(function(kf) {
      var outX = cx + R * 0.8, outY = cy - R * 0.6;
      dot(outX, outY, 6, '#f0e68c', 0.6, true);
      lbl(outX, outY + 10, 'out · SUN→IN', '#f0e68c', 8, 0.7);

      var inX = cx - R * 0.8, inY = cy + R * 0.6;
      dot(inX, inY, 6, '#5aad72', 0.6, true);
      lbl(inX, inY + 10, 'in · CELL→OUT', '#5aad72', 8, 0.7);

      // fold line
      var d = document.createElement('div');
      var dx = outX - inX, dy = outY - inY, len = Math.sqrt(dx*dx + dy*dy);
      d.style.cssText = 'position:absolute;left:'+inX+'px;top:'+inY+'px;width:'+len+'px;height:1px;background:linear-gradient(90deg,#5aad72 0%,transparent 40%,transparent 60%,#f0e68c 100%);opacity:0.15;transform-origin:0 0;transform:rotate('+Math.atan2(dy,dx)*180/Math.PI+'deg);';
      wrap.appendChild(d);

      // fold point
      dot(cx, cy, 3, '#fff', 0.3, true);
      lbl(cx, cy + 8, '∅ fold', '#aaa', 7, 0.4);
    }).catch(function(){});

    // ═══ LEFT STATUS PANEL ═══
    var leftPanel = panel(6, 0, '', 'bottom');
    leftPanel.id = 'w259-left';
    leftPanel.style.bottom = '52px';
    leftPanel.style.maxWidth = (vw * 0.45) + 'px';

    // ═══ RIGHT INVENTORY PANEL ═══
    var rightPanel = panel(6, 6, '<span style="color:#888">loading...</span>', 'right');
    rightPanel.id = 'w259-right';
    rightPanel.style.maxWidth = (vw * 0.45) + 'px';

    // ═══ DOCK (inventory) ═══
    fetch('/data/space-dock-259.json').then(function(r){return r.json()}).then(function(dock) {
      var inv = dock.INVENTORY || {};
      var el = document.getElementById('w259-right');
      if (el) el.innerHTML = '<span style="color:#d4a574">⬡</span> ' + inv.html_pages + ' pages · ' + inv.js_instruments + ' JS<br>' +
        '<span style="color:#d4a574">⬡</span> ' + inv.data_bones + ' bones · ' + inv.walker_rooms + ' rooms<br>' +
        '<span style="color:#d4a574">⬡</span> ' + inv.hub_genres + ' genres · ' + inv.rss_items + ' RSS';
    }).catch(function(){});

    // ═══ RSS ═══
    fetch('/feed.xml').then(function(r){return r.text()}).then(function(xml) {
      var items = (xml.match(/<item>/g) || []).length;
      var el = document.getElementById('w259-right');
      if (el) el.innerHTML += '<br><span style="color:#f0883e">📡</span> ' + items + ' items fermenting';
    }).catch(function(){});

    // ═══ HEARTBEAT ═══
    var heart = document.createElement('div');
    heart.style.cssText = 'position:absolute;left:8px;bottom:36px;color:#f85149;font-size:11px;opacity:0.4;animation:w259b 2s ease-in-out infinite;text-shadow:0 0 8px #f85149;';
    heart.textContent = 'lub-DUB';
    wrap.appendChild(heart);

    // ═══ THREE RINGS BADGE ═══
    var badge = document.createElement('div');
    badge.style.cssText = 'position:absolute;left:50%;bottom:36px;transform:translateX(-50%);color:#5a5650;font-size:7px;opacity:0.3;white-space:nowrap;';
    badge.textContent = '💍 primals.eco + nestgate.io + primal.eco';
    wrap.appendChild(badge);

    console.log('[W259] Klein dissolution v4 — THE GLASS — visible');
  }

  var ready = function() { setTimeout(build, 2000); };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ready);
  else ready();

  var resizeTimer;
  window.addEventListener('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(build, 300);
  });

  setInterval(function() {
    if (document.getElementById('w259')) { document.getElementById('w259').remove(); build(); }
  }, 30000);
})();
'''

sftp = ssh.open_sftp()
js_path = f'{REAL}/js/wave259-overlay.js'
with sftp.file(js_path, 'w') as f:
    f.write(overlay_js)
print(f"Pushed wave259-overlay.js v4 ({len(overlay_js)} bytes)")
with sftp.file('/opt/Gaia/static/js/wave259-overlay.js', 'w') as f:
    f.write(overlay_js)
print("Copied to gate static/js/")
sftp.close()

# Verify
import urllib.request
r = urllib.request.urlopen('http://192.168.4.244:8080/js/wave259-overlay.js', timeout=5)
data = r.read()
print(f"\n✓ :8080 → {r.status} {len(data)}B")
assert b'v4' in data, "NOT v4!"

ssh.close()
print("""
=== THE GLASS v4 ===

  z-index: 9999 (above EVERYTHING)
  opacity: 0.5-0.8 for dots, 0.6-0.7 for labels
  box-shadow GLOW on every dot
  text-shadow on every label (readable on dark bg)
  dark panels with border for stats (left + right)

  THIS IS VISIBLE. Reload.
""")
