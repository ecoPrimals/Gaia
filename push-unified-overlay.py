#!/usr/bin/env python3
"""
UNIFIED OVERLAY — ALL pages dissolve into ONE Klein surface.
Every bone, every stat, every face — pulled into one HUD view.
This IS the dissolution. Not separate pages. Just GAIA.
"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)

REAL = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'

overlay_js = r'''// wave259-overlay.js v3 — KLEIN DISSOLUTION
// Every page dissolves into ONE surface. Not separate views. Just GAIA.
// Reads from: seed, pulse, blackholes, census, klein, turbo, dock, feed
(function() {
  'use strict';

  function build() {
    if (document.getElementById('w259')) document.getElementById('w259').remove();

    var wrap = document.createElement('div');
    wrap.id = 'w259';
    wrap.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:50;overflow:hidden;font-family:monospace;';
    document.body.appendChild(wrap);

    var style = document.createElement('style');
    style.textContent = [
      '@keyframes w259p{0%,100%{opacity:0.4;transform:translate(-50%,-50%) scale(1)}50%{opacity:0.7;transform:translate(-50%,-50%) scale(1.4)}}',
      '@keyframes w259b{0%,100%{opacity:0.12}50%{opacity:0.35}}',
      '@keyframes w259spin{from{transform:translate(-50%,-50%) rotate(0deg)}to{transform:translate(-50%,-50%) rotate(360deg)}}',
      '#w259 .dot{position:absolute;border-radius:50%;transform:translate(-50%,-50%)}',
      '#w259 .ring{position:absolute;border-radius:50%;transform:translate(-50%,-50%);background:transparent}',
      '#w259 .lbl{position:absolute;transform:translate(-50%,0);white-space:nowrap}',
      '#w259 .stat{position:absolute;white-space:nowrap}',
    ].join('\n');
    document.head.appendChild(style);

    var vw = window.innerWidth, vh = window.innerHeight;
    var cx = vw/2, cy = vh/2;
    var R = Math.min(vw, vh) * 0.42;

    function dot(x,y,r,c,o,pulse) {
      var d = document.createElement('div');
      d.className='dot';
      d.style.cssText='left:'+x+'px;top:'+y+'px;width:'+(r*2)+'px;height:'+(r*2)+'px;background:'+c+';opacity:'+o+';';
      if(pulse) d.style.animation='w259p '+(2+Math.random()*2)+'s ease-in-out infinite';
      wrap.appendChild(d); return d;
    }
    function ring(x,y,r,c,o,spin) {
      var d = document.createElement('div');
      d.className='ring';
      d.style.cssText='left:'+x+'px;top:'+y+'px;width:'+(r*2)+'px;height:'+(r*2)+'px;border:1px solid '+c+';opacity:'+o+';';
      if(spin) d.style.animation='w259spin '+spin+'s linear infinite';
      wrap.appendChild(d); return d;
    }
    function lbl(x,y,t,c,s,o) {
      var l = document.createElement('div');
      l.className='lbl';
      l.style.cssText='left:'+x+'px;top:'+y+'px;color:'+c+';font-size:'+s+'px;opacity:'+o+';';
      l.textContent=t;
      wrap.appendChild(l); return l;
    }
    function stat(x,y,t,c,s,o,anchor) {
      var l = document.createElement('div');
      l.className='stat';
      l.style.cssText='left:'+x+'px;top:'+y+'px;color:'+c+';font-size:'+s+'px;opacity:'+o+';'+(anchor==='right'?'text-align:right;transform:translateX(-100%);':'');
      l.innerHTML=t;
      wrap.appendChild(l); return l;
    }

    // ═══ DEPTH RINGS (ouroboros skeleton) ═══
    fetch('/gaia-seed.json').then(function(r){return r.json()}).then(function(seed) {
      var levels = seed.depth_levels || [];
      levels.forEach(function(dl) {
        var r2 = dl.R * R;
        ring(cx, cy, r2, '#1e2228', 0.08);
      });
      var pins = Object.keys(seed.io_pin_map || {}).length;
      stat(10, vh-56, '<span style="color:#f0883e">▲</span> wave '+seed.wave+' · '+pins+' pins · '+levels.length+' depth', '#8a857e', 9, 0.25);
    }).catch(function(){});

    // ═══ PULSE (heartbeat) ═══
    fetch('/pulse').then(function(r){return r.json()}).then(function(p) {
      var alive = p.alive || p.services_alive || '?';
      var load = p.load || p.cpu_load || '?';
      var rss = p.rss_mb || '?';
      stat(vw-10, 10, '❤ '+alive+' alive · load '+load+' · '+rss+'MB', '#f85149', 9, 0.25, 'right');
    }).catch(function(){
      stat(vw-10, 10, '❤ pulse unreachable', '#f85149', 9, 0.15, 'right');
    });

    // ═══ BLACKHOLES (gut ring) ═══
    fetch('/data/blackhole-axis-259.json').then(function(r){return r.json()}).then(function(axis) {
      var gutR = R * 0.62;
      ring(cx, cy, gutR, '#f0883e', 0.03, 120);
      var holes = axis.blackholes || [];
      holes.forEach(function(h,i) {
        var a = -Math.PI/2 + (i/(holes.length-1||1)) * Math.PI * 2;
        var hx = cx + Math.cos(a) * gutR;
        var hy = cy + Math.sin(a) * gutR;
        var active = h.state === 'ACTIVE';
        var c = active ? '#f0883e' : '#333';
        dot(hx, hy, active?3:2, '#000', 0.6, false);
        dot(hx, hy, active?5:3, c, active?0.2:0.06, active);
      });
      stat(10, vh-44, '<span style="color:#f0883e">◉</span> '+axis.state_summary.active+'/'+axis.state_summary.total+' blackholes active · gut intake', '#8a857e', 9, 0.25);
    }).catch(function(){});

    // ═══ GATES (membrane ring) ═══
    fetch('/data/organism-census.json').then(function(r){return r.json()}).then(function(census) {
      var memR = R * 0.48;
      ring(cx, cy, memR, '#5aad72', 0.03, 90);
      var gates = census.gates || {};
      var keys = Object.keys(gates);
      var aliveCount = 0;
      keys.forEach(function(name,i) {
        var g = gates[name];
        var a = (i/keys.length) * Math.PI * 2 - Math.PI/2;
        var gx = cx + Math.cos(a) * memR;
        var gy = cy + Math.sin(a) * memR;
        var alive = g.status === 'ALIVE';
        if(alive) aliveCount++;
        dot(gx, gy, 3, alive?'#3fb950':'#f85149', alive?0.5:0.15, alive);
        lbl(gx, gy+7, name, alive?'#3fb950':'#f85149', 6, 0.25);
      });
      stat(10, vh-32, '<span style="color:#3fb950">●</span> '+aliveCount+'/'+keys.length+' gates alive · membrane', '#8a857e', 9, 0.25);
    }).catch(function(){});

    // ═══ KLEIN FACES (the crossing) ═══
    fetch('/data/klein-faces-259.json').then(function(r){return r.json()}).then(function(kf) {
      var outX=cx+R*0.85, outY=cy-R*0.65;
      dot(outX,outY,4,'#f0e68c',0.25,true);
      lbl(outX,outY+8,'out.nestgate.io','#f0e68c',8,0.2);
      lbl(outX,outY+18,'SUN→IN','#f0e68c',6,0.1);

      var inX=cx-R*0.85, inY=cy+R*0.65;
      dot(inX,inY,4,'#5aad72',0.25,true);
      lbl(inX,inY+8,'in.nestgate.io','#5aad72',8,0.2);
      lbl(inX,inY+18,'CELL→OUT','#5aad72',6,0.1);

      // fold line
      var d=document.createElement('div');
      var dx=outX-inX, dy=outY-inY, len=Math.sqrt(dx*dx+dy*dy);
      d.style.cssText='position:absolute;left:'+inX+'px;top:'+inY+'px;width:'+len+'px;height:1px;background:linear-gradient(90deg,#5aad72,transparent,#f0e68c);opacity:0.04;transform-origin:0 0;transform:rotate('+Math.atan2(dy,dx)*180/Math.PI+'deg);';
      wrap.appendChild(d);
      dot(cx,cy,2,'#fff',0.08,false);
    }).catch(function(){});

    // ═══ SPACE DOCK (inventory) ═══
    fetch('/data/space-dock-259.json').then(function(r){return r.json()}).then(function(dock) {
      var inv = dock.INVENTORY || {};
      stat(vw-10, 28, inv.html_pages+' pages · '+inv.js_instruments+' JS · '+inv.data_bones+' bones', '#d4a574', 9, 0.2, 'right');
      stat(vw-10, 42, inv.walker_rooms+' rooms · '+inv.hub_genres+' genres · '+inv.rss_items+' RSS', '#d4a574', 9, 0.2, 'right');
    }).catch(function(){});

    // ═══ RSS (the mouth) ═══
    fetch('/feed.xml').then(function(r){return r.text()}).then(function(xml) {
      var items = (xml.match(/<item>/g)||[]).length;
      stat(vw-10, 56, '📡 '+items+' RSS items fermenting', '#f0883e', 9, 0.2, 'right');
    }).catch(function(){});

    // ═══ TURBO STATS ═══
    fetch('/data/turbo-state.json').then(function(r){return r.json()}).then(function(t) {
      var solves = t.solves_per_sec || t.solve_rate || '?';
      stat(vw-10, 70, '🔥 '+solves+' solves/sec', '#f85149', 9, 0.2, 'right');
    }).catch(function(){
      // Try getting turbo from the page itself
    });

    // ═══ HEARTBEAT ═══
    var heart = document.createElement('div');
    heart.style.cssText='position:absolute;left:10px;bottom:8px;color:#f85149;font-size:10px;opacity:0.12;animation:w259b 2s ease-in-out infinite;';
    heart.textContent='lub-DUB';
    wrap.appendChild(heart);

    // ═══ THREE RINGS (cert domains) ═══
    stat(10, vh-20, '<span style="color:#d4a574">💍</span> primals.eco + nestgate.io + primal.eco = 28 SANs', '#5a5650', 8, 0.15);

    // ═══ KLEIN BOTTLE OUTLINE (spinning slowly) ═══
    ring(cx, cy, R * 0.95, '#2a3040', 0.04, 180);
    ring(cx, cy, R * 0.3, '#2a3040', 0.03, -60);

    console.log('[W259] Klein dissolution overlay — ALL data, ONE surface');
  }

  // Build after page loads
  var ready = function() { setTimeout(build, 1500); };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ready);
  else ready();

  // Rebuild on resize
  var resizeTimer;
  window.addEventListener('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(build, 300);
  });

  // Refresh data every 30s
  setInterval(function() {
    var old = document.getElementById('w259');
    if (old) { old.remove(); build(); }
  }, 30000);
})();
'''

sftp = ssh.open_sftp()
js_path = f'{REAL}/js/wave259-overlay.js'
with sftp.file(js_path, 'w') as f:
    f.write(overlay_js)
print(f"Pushed wave259-overlay.js v3 ({len(overlay_js)} bytes)")
with sftp.file('/opt/Gaia/static/js/wave259-overlay.js', 'w') as f:
    f.write(overlay_js)
print("Copied to gate static/js/")
sftp.close()

# Verify
import urllib.request
r = urllib.request.urlopen('http://192.168.4.244:8080/js/wave259-overlay.js', timeout=5)
print(f"\n✓ :8080 → {r.status} {len(r.read())}B")

ssh.close()
print("""
=== KLEIN DISSOLUTION OVERLAY v3 ===

  ALL pages dissolve into ONE surface:

  LEFT COLUMN (status):                    RIGHT COLUMN (inventory):
    ▲ wave 259 · 28 pins · 8 depth           195 pages · 274 JS · 1863 bones
    ◉ 9/13 blackholes active · gut            1989 rooms · 9 genres · 2562 RSS
    ● gates alive · membrane                  📡 RSS items fermenting
    💍 3 domains = 28 SANs                    🔥 solves/sec
    lub-DUB                                   ❤ alive · load · RAM

  CENTER:
    ○ 8 depth rings (ouroboros skeleton)
    ● 13 blackholes on gut ring (spinning slowly)
    ● gates on membrane ring (spinning opposite)
    ● Klein faces: out (gold) / in (green) / fold line
    ● Klein bottle outline (outer + inner, counter-rotating)

  Refreshes every 30s. Rebuilds on resize.
  Not separate pages. Just GAIA. The dissolution.
""")
