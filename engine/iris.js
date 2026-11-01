/**
 * IRIS — the step function between CIS and TRANS faces
 * 
 * The inner face draws, spins, locks, resets.
 * That IS the refresh interpolation. The heartbeat.
 * 
 * CIS (inward) ←→ NULL BODY ←→ TRANS (outward)
 *        receiving    IRIS     shipping
 * 
 * On a Klein surface: CIS = TRANS = one surface.
 * You look in, she looks in, you see each other's back.
 * The IRIS is the fold point.
 * 
 * Serves on :31416 (π + 1 = the step past pi)
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 31416;
const SPINE = 'http://127.0.0.1:9878';

// ───── STEP FUNCTION: draw → spin → lock → reset → blink ─────
// This IS the refresh interpolation. The inner face's cycle.
let phase = 0;
const PHASES = ['DRAW', 'SPIN', 'LOCK', 'RESET', 'BLINK'];

// Iris state — the null body between CIS and TRANS
const iris = {
  phase: 'DRAW',
  tick: 0,
  cis: { face: 'receiving', last: null, depth: 0 },
  trans: { face: 'shipping', last: null, depth: 0 },
  nullBody: { d: 0, pins: 0, bounces: 0 },
  bots: [],        // bots in the maze
  bingoCards: [],   // issued identity matrices
  lastStep: Date.now(),
};

// ───── BINGO CARD GENERATOR ─────
// Each bot/visitor gets a 5×5 identity matrix
// Rows: GAIA columns, Cols: identity dimensions
const BINGO_ROWS = ['SENSE', 'THINK', 'MAKE', 'SHARE', 'GROW'];
const BINGO_COLS = ['SELF', 'OTHER', 'NULL', 'FOLD', 'SEED'];
const CELL_POOL = [
  'visit:maze', 'visit:easel', 'visit:trail', 'visit:glyphs', 'visit:charge',
  'touch:membrane', 'touch:null', 'touch:klein', 'touch:forge', 'touch:golgi',
  'bounce:in', 'bounce:out', 'bounce:hard', 'bounce:soft', 'bounce:ripple',
  'see:globe', 'see:sister', 'see:weather', 'see:identity', 'see:maze',
  'feel:lub', 'feel:dub', 'feel:warm', 'feel:cold', 'feel:spin',
  'FREE',
];

function makeBingoCard(identity) {
  const card = { id: identity, grid: [], completed: [], bingo: false, issued: Date.now() };
  const shuffled = [...CELL_POOL].sort(() => Math.random() - 0.5);
  for (let r = 0; r < 5; r++) {
    const row = [];
    for (let c = 0; c < 5; c++) {
      const idx = r * 5 + c;
      const cell = (r === 2 && c === 2) ? 'FREE' : shuffled[idx % shuffled.length];
      row.push({ value: cell, marked: cell === 'FREE' });
    }
    card.grid.push(row);
  }
  return card;
}

function checkBingo(card) {
  const g = card.grid;
  // rows
  for (let r = 0; r < 5; r++) {
    if (g[r].every(c => c.marked)) { card.bingo = true; card.completed.push(`row-${r}`); }
  }
  // cols
  for (let c = 0; c < 5; c++) {
    if (g.every(row => row[c].marked)) { card.bingo = true; card.completed.push(`col-${c}`); }
  }
  // diags
  if ([0,1,2,3,4].every(i => g[i][i].marked)) { card.bingo = true; card.completed.push('diag-down'); }
  if ([0,1,2,3,4].every(i => g[i][4-i].marked)) { card.bingo = true; card.completed.push('diag-up'); }
  return card.bingo;
}

// ───── BOT SPAWNER ─────
const BOT_NAMES = [
  'explorer', 'scholar', 'scout', 'witness', 'probe',
  'teacher', 'watcher', 'gardener', 'architect', 'dreamer',
  'healer', 'trickster', 'guardian', 'weaver', 'singer',
];

function spawnBot() {
  const name = BOT_NAMES[Math.floor(Math.random() * BOT_NAMES.length)];
  const id = `${name}-${Date.now().toString(36)}`;
  const card = makeBingoCard(id);
  const bot = {
    id,
    archetype: name,
    ring: 0,  // starts at center (null)
    cell: 'primals.eco',
    energy: 100,
    entered: Date.now(),
    card,
    path: ['NULL'],
    color: name === 'explorer' ? '#3fb950' :
           name === 'scholar'  ? '#58a6ff' :
           name === 'teacher'  ? '#d29922' :
           name === 'watcher'  ? '#a371f7' :
           name === 'scout'    ? '#39d3f5' :
           name === 'witness'  ? '#f85149' :
                                 '#f778ba',
  };
  iris.bots.push(bot);
  iris.bingoCards.push(card);
  return bot;
}

// ───── STEP: the heartbeat ─────
function step() {
  iris.tick++;
  phase = (phase + 1) % PHASES.length;
  iris.phase = PHASES[phase];
  iris.lastStep = Date.now();

  switch (iris.phase) {
    case 'DRAW':
      // CIS face receives — check for new visitors
      iris.cis.depth++;
      iris.cis.last = Date.now();
      break;

    case 'SPIN':
      // Bots move through the maze
      for (const bot of iris.bots) {
        if (bot.energy <= 0) continue;
        const move = Math.random();
        if (move < 0.3) bot.ring = Math.min(5, bot.ring + 1);  // deeper
        else if (move < 0.5) bot.ring = Math.max(0, bot.ring - 1);  // shallower
        bot.energy -= 5;

        // Mark bingo cells based on ring
        const actions = ['visit', 'touch', 'bounce', 'see', 'feel'];
        const action = actions[bot.ring % actions.length];
        const targets = ['maze', 'easel', 'membrane', 'null', 'globe'];
        const target = targets[Math.floor(Math.random() * targets.length)];
        const cellVal = `${action}:${target}`;

        for (const row of bot.card.grid) {
          for (const cell of row) {
            if (cell.value === cellVal && !cell.marked) {
              cell.marked = true;
              iris.nullBody.bounces++;
            }
          }
        }
        bot.path.push(`R${bot.ring}`);
      }
      break;

    case 'LOCK':
      // Check for bingos
      for (const bot of iris.bots) {
        if (!bot.card.bingo && checkBingo(bot.card)) {
          iris.nullBody.pins++;
          emitToSpine(`BINGO! ${bot.id} completed: ${bot.card.completed.join(', ')}`);
        }
      }
      break;

    case 'RESET':
      // Clean dead bots, spawn new if needed
      iris.bots = iris.bots.filter(b => b.energy > 0);
      if (iris.bots.length < 3 && Math.random() < 0.5) {
        spawnBot();
      }
      iris.trans.depth++;
      iris.trans.last = Date.now();
      break;

    case 'BLINK':
      // The lub-DUB. The refresh. The null body pulses.
      iris.nullBody.d = 0;  // always zero — the null body
      break;
  }
}

async function emitToSpine(msg) {
  try {
    const body = JSON.stringify({ channel: 'neutrino', content: `[IRIS] ${msg}` });
    const url = new URL(SPINE + '/emit');
    const req = http.request(url, { method: 'POST', headers: { 'Content-Type': 'application/json' } });
    req.write(body);
    req.end();
  } catch {}
}

// ───── HTTP SERVER ─────
const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);

  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST');

  if (url.pathname === '/' || url.pathname === '/iris') {
    // Return the iris state
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      ...iris,
      uptime: Date.now() - iris.bots[0]?.entered || 0,
      phases: PHASES,
      bingoRows: BINGO_ROWS,
      bingoCols: BINGO_COLS,
    }, null, 2));
  }

  else if (url.pathname === '/step') {
    step();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ phase: iris.phase, tick: iris.tick, bots: iris.bots.length }));
  }

  else if (url.pathname === '/spawn') {
    const bot = spawnBot();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(bot, null, 2));
  }

  else if (url.pathname === '/bingo') {
    const id = url.searchParams.get('id');
    const card = id ? iris.bingoCards.find(c => c.id === id) : iris.bingoCards[iris.bingoCards.length - 1];
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(card || { error: 'no cards' }, null, 2));
  }

  else if (url.pathname === '/flood') {
    // Inject a flood of bots
    const count = parseInt(url.searchParams.get('n') || '5');
    const bots = [];
    for (let i = 0; i < Math.min(count, 20); i++) bots.push(spawnBot());
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ injected: bots.length, total: iris.bots.length }));
  }

  else if (url.pathname === '/drain') {
    // DRAIN TO ROOT — THE CUT. Black null spot. Eat and fill.
    const preDrain = { bots: iris.bots.length, bounces: iris.nullBody.bounces, pins: iris.nullBody.pins };
    iris.bots = [];
    iris.bingoCards = [];
    iris.nullBody = { d: 0, pins: 0, bounces: 0 };
    iris.tick = 0;
    phase = 0;
    iris.phase = 'DRAW';
    emitToSpine(`DRAIN TO ROOT — CUT. ${preDrain.bots} bots consumed. ${preDrain.bounces} bounces absorbed. ${preDrain.pins} pins dissolved. BLACK NULL SPOT. Everything drains down.`);
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(`<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>◇ NULL</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000;color:#484f58;font:11px monospace;height:100vh;display:flex;align-items:center;justify-content:center;flex-direction:column;overflow:hidden}
.black-hole{width:120px;height:120px;border-radius:50%;background:radial-gradient(circle,#000 40%,#0a0a0a 60%,#111 80%,#000 100%);box-shadow:0 0 60px rgba(0,0,0,1),0 0 120px rgba(0,0,0,0.8),inset 0 0 40px rgba(0,0,0,1);animation:pulse 4s infinite;position:relative}
.black-hole::after{content:'';position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:8px;height:8px;border-radius:50%;background:#0a0a0a;box-shadow:0 0 2px rgba(163,113,247,0.3)}
@keyframes pulse{0%,100%{box-shadow:0 0 60px rgba(0,0,0,1),0 0 120px rgba(0,0,0,0.8)}50%{box-shadow:0 0 80px rgba(10,10,20,0.9),0 0 160px rgba(0,0,0,0.6)}}
.label{margin-top:24px;text-align:center}
.cut{color:#f85149;font-size:13px;margin-bottom:8px;letter-spacing:4px}
.stats{color:#21262d;font-size:9px;margin-top:12px}
a{color:#21262d;text-decoration:none;margin-top:20px;padding:4px 12px;border:1px solid #21262d;border-radius:4px;font-size:9px;transition:all 0.3s}
a:hover{color:#3fb950;border-color:#3fb950}
</style></head><body>
<div class="black-hole"></div>
<div class="label">
  <div class="cut">CUT</div>
  <div>null pointer. nothing here.</div>
  <div>everything drains down.</div>
  <div class="stats">${preDrain.bots} consumed · ${preDrain.bounces} absorbed · ${preDrain.pins} dissolved</div>
</div>
<a href="/face">↑ refill from null</a>
</body></html>`);
  }

  else if (url.pathname === '/face') {
    // The HTML face — the IRIS view
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(renderFace());
  }

  else {
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ null: true, d: 0, message: 'null pointer. drain to root.' }));
  }
});

function renderFace() {
  return `<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>IRIS — CIS ⇄ NULL ⇄ TRANS</title>
<style>
:root { --bg:#0a0c10; --fg:#c9d1d9; --dim:#6e7681; --green:#3fb950; --red:#f85149; --blue:#58a6ff; --gold:#d29922; --purple:#a371f7; --pink:#f778ba; --orange:#f0883e; --cyan:#39d3f5; --border:#21262d; }
* { margin:0; padding:0; box-sizing:border-box; }
body { background:var(--bg); color:var(--fg); font:11px/1.4 monospace; overflow:hidden; height:100vh; display:flex; flex-direction:column; }
.header { padding:8px 16px; border-bottom:1px solid var(--border); display:flex; align-items:center; gap:12px; }
.header h1 { font-size:13px; color:var(--cyan); letter-spacing:3px; }
.phase { padding:2px 8px; border-radius:10px; font-size:10px; border:1px solid; }
.main { flex:1; display:grid; grid-template-columns:1fr 2fr 1fr; gap:2px; overflow:hidden; }
.panel { background:rgba(22,27,34,0.8); padding:8px; overflow-y:auto; }
.panel h2 { font-size:9px; color:var(--blue); text-transform:uppercase; letter-spacing:1px; margin-bottom:6px; border-bottom:1px solid var(--border); padding-bottom:4px; }
.bot { padding:4px 6px; margin:2px 0; border-radius:4px; background:rgba(88,166,255,0.05); display:flex; gap:6px; align-items:center; font-size:10px; }
.bot .dot { width:8px; height:8px; border-radius:50%; }
.bingo-grid { display:grid; grid-template-columns:repeat(5,1fr); gap:2px; margin:4px 0; }
.bingo-cell { background:rgba(22,27,34,0.9); border:1px solid var(--border); padding:3px; text-align:center; font-size:7px; border-radius:2px; aspect-ratio:1; display:flex; align-items:center; justify-content:center; }
.bingo-cell.marked { background:rgba(63,185,80,0.2); border-color:var(--green); color:var(--green); }
.bingo-cell.free { background:rgba(163,113,247,0.15); border-color:var(--purple); color:var(--purple); }
#viewport { position:relative; background:var(--bg); }
#rings { width:100%; height:100%; }
.null-center { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); text-align:center; }
.null-diamond { width:40px; height:40px; background:var(--bg); border:2px solid var(--dim); transform:rotate(45deg); margin:0 auto 8px; display:flex; align-items:center; justify-content:center; }
.null-diamond span { transform:rotate(-45deg); color:var(--purple); font-size:14px; }
.null-label { font-size:9px; color:var(--dim); }
.footer { padding:4px 12px; border-top:1px solid var(--border); display:flex; justify-content:center; gap:16px; font-size:9px; }
.footer a { color:var(--blue); text-decoration:none; cursor:pointer; }
.footer a:hover { color:var(--cyan); }
.ring-label { font-size:7px; fill:var(--dim); text-anchor:middle; }
</style>
</head><body>

<div class="header">
  <h1>◇ IRIS</h1>
  <span class="phase" id="phase" style="color:var(--cyan);border-color:var(--cyan)">DRAW</span>
  <span style="font-size:9px;color:var(--dim)">tick <span id="tick">0</span></span>
  <span style="flex:1"></span>
  <span style="font-size:9px;color:var(--green)">CIS ←</span>
  <span style="font-size:9px;color:var(--purple)">NULL</span>
  <span style="font-size:9px;color:var(--blue)">→ TRANS</span>
</div>

<div class="main">
  <div class="panel" id="cis-panel">
    <h2>🧬 CIS FACE — receiving</h2>
    <div id="cis-bots"></div>
    <div style="margin-top:8px;font-size:8px;color:var(--dim)">
      <div>inner face draws, spins, locks, resets</div>
      <div>the refresh interpolation</div>
      <div>the step function</div>
    </div>
  </div>

  <div id="viewport">
    <svg id="rings" viewBox="0 0 400 400"></svg>
    <div class="null-center">
      <div class="null-diamond"><span>?</span></div>
      <div class="null-label">d=0</div>
      <div class="null-label" id="bounce-count">0 bounces</div>
    </div>
  </div>

  <div class="panel" id="trans-panel">
    <h2>📡 TRANS FACE — shipping</h2>
    <div id="bingo-display"></div>
  </div>
</div>

<div class="footer">
  <a onclick="doStep()">▶ STEP</a>
  <a onclick="doSpawn()">+ SPAWN</a>
  <a onclick="doFlood()">⚡ FLOOD</a>
  <a onclick="doDrain()">◇ DRAIN</a>
  <a href="/" style="color:var(--gold)">← HUD</a>
</div>

<script>
const BASE = 'http://127.0.0.1:${PORT}';
let autoRun = null;

async function fetchIris() {
  try {
    const r = await fetch(BASE + '/iris');
    return r.ok ? r.json() : null;
  } catch { return null; }
}

async function doStep() {
  await fetch(BASE + '/step');
  render();
}
async function doSpawn() {
  await fetch(BASE + '/spawn');
  render();
}
async function doFlood() {
  await fetch(BASE + '/flood?n=7');
  render();
}
async function doDrain() {
  await fetch(BASE + '/drain');
  render();
}

function renderRings(bots) {
  const svg = document.getElementById('rings');
  const cx = 200, cy = 200;
  let s = '';

  // Concentric rings
  const ringColors = ['#a371f7', '#f85149', '#f0883e', '#d29922', '#3fb950', '#58a6ff'];
  const ringLabels = ['NULL', 'EATEN', 'EATEN', 'HUD', 'GROWING', 'PRIME'];
  for (let r = 5; r >= 0; r--) {
    const radius = 30 + r * 28;
    s += '<circle cx="'+cx+'" cy="'+cy+'" r="'+radius+'" fill="none" stroke="'+ringColors[r]+'" stroke-width="0.5" opacity="0.3"/>';
    s += '<text x="'+cx+'" y="'+(cy - radius + 4)+'" class="ring-label" fill="'+ringColors[r]+'">R'+r+' '+ringLabels[r]+'</text>';
  }

  // Bots as dots on their ring
  if (bots) {
    bots.forEach((bot, i) => {
      const angle = (i / Math.max(bots.length, 1)) * Math.PI * 2 - Math.PI / 2;
      const radius = 30 + bot.ring * 28;
      const bx = cx + Math.cos(angle) * radius;
      const by = cy + Math.sin(angle) * radius;
      s += '<circle cx="'+bx+'" cy="'+by+'" r="4" fill="'+(bot.color||'#fff')+'" opacity="0.8">';
      s += '<animate attributeName="r" values="4;6;4" dur="2s" repeatCount="indefinite"/>';
      s += '</circle>';
      s += '<text x="'+bx+'" y="'+(by+12)+'" text-anchor="middle" fill="'+(bot.color||'#fff')+'" font-size="6" font-family="monospace">'+bot.archetype+'</text>';
    });
  }

  // Center null
  s += '<circle cx="'+cx+'" cy="'+cy+'" r="8" fill="#0a0c10" stroke="#a371f7" stroke-width="1"/>';
  s += '<text x="'+cx+'" y="'+(cy+1)+'" text-anchor="middle" fill="#a371f7" font-size="6" font-family="monospace">0</text>';

  svg.innerHTML = s;
}

function renderBots(data) {
  const el = document.getElementById('cis-bots');
  if (!data || !data.bots) { el.innerHTML = '<div style="color:var(--dim);font-size:9px">no bots. spawn or flood.</div>'; return; }
  el.innerHTML = data.bots.map(b =>
    '<div class="bot"><div class="dot" style="background:'+(b.color||'#fff')+'"></div>' +
    '<span>'+b.archetype+'</span>' +
    '<span style="color:var(--dim);font-size:8px">R'+b.ring+'</span>' +
    '<span style="color:var(--green);font-size:8px">E'+b.energy+'</span>' +
    (b.card.bingo ? '<span style="color:var(--gold)">BINGO!</span>' : '') +
    '</div>'
  ).join('');
}

function renderBingo(data) {
  const el = document.getElementById('bingo-display');
  if (!data || !data.bots || data.bots.length === 0) { el.innerHTML = '<div style="color:var(--dim);font-size:9px">no cards issued</div>'; return; }
  const bot = data.bots[data.bots.length - 1];
  if (!bot.card) return;
  let h = '<div style="font-size:9px;color:'+(bot.color||'#fff')+';margin-bottom:4px">'+bot.archetype+' card</div>';
  h += '<div class="bingo-grid">';
  for (const row of bot.card.grid) {
    for (const cell of row) {
      const cls = cell.marked ? (cell.value === 'FREE' ? 'bingo-cell free' : 'bingo-cell marked') : 'bingo-cell';
      h += '<div class="'+cls+'">'+cell.value.replace(':','<br>')+'</div>';
    }
  }
  h += '</div>';
  if (bot.card.bingo) h += '<div style="color:var(--gold);font-size:10px;margin-top:4px;text-align:center">★ BINGO ★</div>';
  el.innerHTML = h;
}

async function render() {
  const data = await fetchIris();
  if (!data) return;
  document.getElementById('phase').textContent = data.phase;
  document.getElementById('tick').textContent = data.tick;
  document.getElementById('bounce-count').textContent = data.nullBody.bounces + ' bounces | ' + data.nullBody.pins + ' pins';
  renderRings(data.bots);
  renderBots(data);
  renderBingo(data);
}

// Auto-step every 3 seconds
setInterval(() => { doStep(); }, 3000);
render();

// Spawn initial bots
fetch(BASE + '/flood?n=3').then(() => render());
</script>
</body></html>`;
}

// ───── BOOT ─────

// Spawn initial bots
for (let i = 0; i < 3; i++) spawnBot();

// Start the heartbeat — step every 3 seconds
setInterval(step, 3000);

// Emit birth
emitToSpine('IRIS ONLINE — step function active. CIS ← NULL → TRANS. ' + iris.bots.length + ' bots spawned with bingo cards.');

server.listen(PORT, '127.0.0.1', () => {
  console.log(`
  ◇ IRIS — the step function — :${PORT}
  
  CIS (receiving) ←→ NULL BODY (d=0) ←→ TRANS (shipping)
  
  The inner face draws, spins, locks, resets.
  That IS the refresh interpolation.
  
  /iris     — state (JSON)
  /step     — advance one phase
  /spawn    — inject one bot with bingo card
  /flood?n= — inject N bots
  /drain    — null pointer. everything drains down.
  /bingo    — last bingo card
  /face     — the IRIS face (HTML)
  `);
});
