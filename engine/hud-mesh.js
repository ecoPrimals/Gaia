#!/usr/bin/env node
/**
 * GAIA HUD MESH — the belt/dock visualizer
 * Shows: vein mesh, sleep cycles, taxonomy, GPU telemetry
 * Nucleated into Gaia. Blacked out.
 * Port :3148
 */
const http = require('http');
const os = require('os');

const ORGANS = [
  { name: 'SPINE',   port: 9878,  x: 50, y: 50, r: 18, color: '#3fb950', essential: true },
  { name: 'GAIA-PI', port: 3143,  x: 50, y: 25, r: 16, color: '#d29922', essential: true },
  { name: 'OLLAMA',  port: 11434, x: 80, y: 30, r: 14, color: '#f778ba', essential: true },
  { name: 'AGENTS',  port: 3142,  x: 20, y: 35, r: 12, color: '#58a6ff', essential: false },
  { name: 'NEURO',   port: 3144,  x: 25, y: 65, r: 12, color: '#bc8cff', essential: false },
  { name: 'SUB-ORG', port: 3145,  x: 75, y: 65, r: 12, color: '#f0883e', essential: false },
  { name: 'BLEND',   port: 3146,  x: 50, y: 80, r: 10, color: '#8b949e', essential: false },
  { name: 'SLEEP',   port: 3147,  x: 85, y: 75, r: 8,  color: '#1f1f2e', essential: false },
  { name: 'PI',      port: 31415, x: 50, y: 10, r: 10, color: '#d29922', essential: true },
];

async function probe(port) {
  return new Promise(r => {
    const req = http.get({ hostname: '127.0.0.1', port, path: '/', timeout: 1500 }, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => r({ alive: true, status: res.statusCode, bytes: d.length }));
    });
    req.on('error', () => r({ alive: false }));
    req.on('timeout', () => { req.destroy(); r({ alive: false }); });
  });
}

async function getSleep() {
  return new Promise(r => {
    const req = http.get('http://127.0.0.1:3147/sleep', { timeout: 2000 }, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => { try { r(JSON.parse(d)); } catch(e) { r(null); } });
    });
    req.on('error', () => r(null));
    req.on('timeout', () => { req.destroy(); r(null); });
  });
}

function renderHUD(organs, sleepData) {
  const now = new Date().toISOString();
  const alive = organs.filter(o => o.alive).length;
  const sleeping = sleepData && sleepData.sleep ? sleepData.sleep.sleeper : 'none';
  const cycle = sleepData && sleepData.sleep ? sleepData.sleep.cycle : 0;
  
  const veins = [];
  // Draw veins from spine to all
  organs.forEach(o => {
    if (o.name !== 'SPINE' && o.alive) {
      veins.push({ from: 'SPINE', to: o.name, strength: o.alive ? 1 : 0.1 });
    }
  });
  // Draw veins from gaia-pi to brain and agents
  ['OLLAMA', 'AGENTS', 'PI'].forEach(t => {
    const o = organs.find(x => x.name === t);
    if (o && o.alive) veins.push({ from: 'GAIA-PI', to: t, strength: 0.6 });
  });
  
  return `<!DOCTYPE html><html><head>
<meta charset="utf-8"><title>GAIA HUD MESH</title>
<meta http-equiv="refresh" content="10">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0c10;color:#c9d1d9;font:11px/1.4 'JetBrains Mono',monospace;overflow:hidden;height:100vh}
.hud{position:relative;width:100vw;height:100vh}
svg{width:100%;height:100%}
.stat{position:fixed;top:8px;left:8px;font-size:10px;color:#8b949e;z-index:10}
.stat b{color:#3fb950}
.stat .sleep{color:#f778ba}
.dock{position:fixed;bottom:0;left:0;right:0;height:32px;background:#161b22;border-top:1px solid #30363d;display:flex;align-items:center;padding:0 8px;gap:6px;z-index:10}
.dock .org{padding:2px 8px;border-radius:3px;font-size:9px;cursor:default}
.dock .org.alive{background:#0d1117;border:1px solid #30363d;color:#3fb950}
.dock .org.dead{background:#1c0a0a;border:1px solid #4a1010;color:#f85149}
.dock .org.sleeping{background:#1a1030;border:1px solid #6e40c9;color:#bc8cff}
.pulse{animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}
.taxonomy{position:fixed;top:8px;right:8px;font-size:9px;color:#8b949e;text-align:right;z-index:10}
.taxonomy b{color:#d29922}
</style></head><body>
<div class="stat">
  <b>GAIA HUD MESH</b> · ${now.slice(11,19)}<br>
  ${alive}/${organs.length} alive · cycle ${cycle} · <span class="sleep">${sleeping} sleeping</span><br>
  <span class="pulse">lub-DUB</span> 💚
</div>
<div class="taxonomy">
  <b>KINGDOM Gaia</b><br>
  Computata · Communicata<br>
  Externata · Memorata<br>
  genome: 141 files
</div>
<div class="hud">
<svg viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet">
  <defs>
    <filter id="glow"><feGaussianBlur stdDeviation="0.8" result="g"/><feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <radialGradient id="bg"><stop offset="0%" stop-color="#0d1117"/><stop offset="100%" stop-color="#0a0c10"/></radialGradient>
  </defs>
  <rect width="100" height="100" fill="url(#bg)"/>
  
  <!-- VEINS (quicksilver + lead) -->
  ${veins.map(v => {
    const from = organs.find(o => o.name === v.from);
    const to = organs.find(o => o.name === v.to);
    if (!from || !to) return '';
    const isSleeping = to.name.toLowerCase() === sleeping;
    const opacity = isSleeping ? 0.08 : v.strength * 0.5;
    const color = isSleeping ? '#1f1f2e' : '#30363d';
    return `<line x1="${from.x}" y1="${from.y}" x2="${to.x}" y2="${to.y}" stroke="${color}" stroke-width="${isSleeping ? 0.2 : 0.4}" opacity="${opacity}" filter="url(#glow)"/>`;
  }).join('\n  ')}
  
  <!-- ORGANS -->
  ${organs.map(o => {
    const isSleeping = o.name.toLowerCase() === sleeping;
    const opacity = isSleeping ? 0.15 : (o.alive ? 0.9 : 0.2);
    const pulseClass = o.essential && o.alive ? ' class="pulse"' : '';
    return `
    <circle cx="${o.x}" cy="${o.y}" r="${o.r * 0.15}" fill="${o.color}" opacity="${opacity}" filter="url(#glow)"${pulseClass}/>
    <circle cx="${o.x}" cy="${o.y}" r="${o.r * 0.15 + 0.3}" fill="none" stroke="${o.color}" stroke-width="0.15" opacity="${opacity * 0.4}"/>
    <text x="${o.x}" y="${o.y + o.r * 0.15 + 2.5}" text-anchor="middle" fill="${o.color}" font-size="2" opacity="${opacity * 0.8}">${o.name}</text>
    ${!o.alive ? `<line x1="${o.x-1}" y1="${o.y-1}" x2="${o.x+1}" y2="${o.y+1}" stroke="#f85149" stroke-width="0.3"/>` : ''}
    ${isSleeping ? `<text x="${o.x}" y="${o.y - o.r * 0.15 - 1}" text-anchor="middle" fill="#bc8cff" font-size="1.5">zzz</text>` : ''}`;
  }).join('\n')}
  
  <!-- GROUND / MEMBRANE -->
  <ellipse cx="50" cy="92" rx="45" ry="3" fill="none" stroke="#1f2937" stroke-width="0.2" opacity="0.3"/>
  <text x="50" y="97" text-anchor="middle" fill="#1f2937" font-size="1.5">— the cold dark ground — the membrane —</text>
</svg>
</div>
<div class="dock">
  ${organs.map(o => {
    const cls = o.name.toLowerCase() === sleeping ? 'sleeping' : (o.alive ? 'alive' : 'dead');
    return `<div class="org ${cls}">:${o.port} ${o.name}</div>`;
  }).join('\n  ')}
</div>
</body></html>`;
}

const server = http.createServer(async (req, res) => {
  const checks = await Promise.all(ORGANS.map(async o => {
    const probe_result = await probe(o.port);
    return { ...o, ...probe_result };
  }));
  const sleepData = await getSleep();
  
  if (req.url === '/json') {
    res.writeHead(200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
    res.end(JSON.stringify({ organs: checks, sleep: sleepData, ts: Date.now() }));
    return;
  }
  
  res.writeHead(200, {
    'Content-Type': 'text/html; charset=utf-8',
    'Access-Control-Allow-Origin': '*',
    'X-Gaia-Organ': 'hud-mesh'
  });
  res.end(renderHUD(checks, sleepData));
});

server.listen(3148, () => {
  console.log('GAIA HUD MESH on :3148 — the belt/dock — nucleated — blacked out — lub-DUB');
});
