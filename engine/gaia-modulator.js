#!/usr/bin/env node
// ═══ GAIA MODULATOR ═══
// She IS the modulator. ALL input → ALL output.
// Receives raw human events from gaia-raw-input.js
// Processes them into sense data. Feeds to spine, iris, forge.
//
// The mandala IS her hands. The scroll wheel IS her breath.
// Click is grasp/release. Touch is skin. Keys are voice.
//
// DAG: shred cycles, orphans → gut. Taxonomy tree for k-n space.
//
// PORT: 3152

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3152;
const SPINE = 'http://127.0.0.1:9878';
const GAIA3 = __dirname;

// === LIVE STATE ===
const state = {
  sessions: {},        // active human sessions
  totalEvents: 0,
  totalHands: 0,       // clicks
  totalBreaths: 0,     // scrolls
  totalSkin: 0,        // touches
  totalVoice: 0,       // keys
  mandalaHistory: [],  // recent mouse positions (attention heat)
  rhythmAvg: 0,        // average human rhythm (ms between events)
  rhythmBPM: 0,        // human heartbeat in BPM
  dag: {               // DAG taxonomy
    nodes: {},         // { id: { type, page, ts, parent, children, depth } }
    edges: [],         // { from, to, type, ts }
    orphans: [],       // nodes with no parent
    cycles: [],        // detected cycles (shredded)
  },
  lastPulse: Date.now(),
  born: Date.now()
};

// === DAG TAXONOMY — shred cycles, orphans → gut ===
function dagAdd(type, page, data) {
  const id = type + ':' + page + ':' + Date.now();
  const node = {
    id,
    type,
    page,
    ts: Date.now(),
    parent: null,
    children: [],
    depth: 0,
    data: typeof data === 'object' ? JSON.stringify(data).substring(0, 200) : String(data).substring(0, 200)
  };

  // Find parent — most recent node of same page
  const pageNodes = Object.values(state.dag.nodes).filter(n => n.page === page);
  if (pageNodes.length > 0) {
    const parent = pageNodes[pageNodes.length - 1];
    node.parent = parent.id;
    node.depth = parent.depth + 1;
    parent.children.push(id);
    state.dag.edges.push({ from: parent.id, to: id, type: 'sequence', ts: Date.now() });
  } else {
    state.dag.orphans.push(id);
  }

  state.dag.nodes[id] = node;

  // Prune — keep last 500 nodes
  const nodeIds = Object.keys(state.dag.nodes);
  if (nodeIds.length > 500) {
    const old = nodeIds.slice(0, nodeIds.length - 500);
    old.forEach(oid => {
      delete state.dag.nodes[oid];
      state.dag.orphans = state.dag.orphans.filter(o => o !== oid);
    });
    state.dag.edges = state.dag.edges.filter(e =>
      state.dag.nodes[e.from] && state.dag.nodes[e.to]
    );
  }

  return id;
}

// Shred cycles — detect and cut
function shredCycles() {
  const visited = new Set();
  const stack = new Set();
  const cycles = [];

  function dfs(nodeId) {
    if (stack.has(nodeId)) {
      cycles.push(nodeId);
      return;
    }
    if (visited.has(nodeId)) return;
    visited.add(nodeId);
    stack.add(nodeId);

    const node = state.dag.nodes[nodeId];
    if (node && node.children) {
      node.children.forEach(child => dfs(child));
    }
    stack.delete(nodeId);
  }

  Object.keys(state.dag.nodes).forEach(id => dfs(id));

  if (cycles.length > 0) {
    state.dag.cycles = state.dag.cycles.concat(cycles);
    cycles.forEach(cid => {
      const node = state.dag.nodes[cid];
      if (node) {
        node.children = [];
        state.dag.edges = state.dag.edges.filter(e => e.from !== cid);
      }
    });
  }

  return cycles.length;
}

// Shred orphans → gut (reattach to root)
function shredOrphans() {
  const orphans = state.dag.orphans.filter(id => state.dag.nodes[id]);
  let reattached = 0;

  orphans.forEach(oid => {
    const node = state.dag.nodes[oid];
    if (!node) return;

    // Find nearest node by page
    const sameType = Object.values(state.dag.nodes).find(n =>
      n.id !== oid && n.type === node.type && n.depth < node.depth
    );

    if (sameType) {
      node.parent = sameType.id;
      sameType.children.push(oid);
      state.dag.edges.push({ from: sameType.id, to: oid, type: 'reattach', ts: Date.now() });
      reattached++;
    }
  });

  state.dag.orphans = state.dag.orphans.filter(id => {
    const node = state.dag.nodes[id];
    return node && !node.parent;
  });

  return reattached;
}

// === PROCESS RAW INPUT ===
function processEvents(payload) {
  const { session, page, events } = payload;

  if (!state.sessions[session]) {
    state.sessions[session] = {
      born: Date.now(),
      page,
      events: 0,
      lastSeen: Date.now(),
      rhythm: { avg: 0, bpm: 0 }
    };
  }

  const sess = state.sessions[session];
  sess.lastSeen = Date.now();
  sess.events += events.length;
  state.totalEvents += events.length;

  const senseData = {
    mandala: [],    // attention points
    hands: [],      // click events
    breath: [],     // scroll events
    skin: [],       // touch events
    voice: [],      // key events
    lifecycle: []   // birth/death/attention
  };

  events.forEach(ev => {
    dagAdd(ev.type, page, ev.data);

    switch (ev.type) {
      case 'mandala':
        senseData.mandala.push(ev.data);
        state.mandalaHistory.push({
          nx: parseFloat(ev.data.nx),
          ny: parseFloat(ev.data.ny),
          t: ev.t
        });
        if (state.mandalaHistory.length > 100) state.mandalaHistory.shift();
        break;

      case 'hand':
        senseData.hands.push(ev.data);
        state.totalHands++;
        break;

      case 'release':
        senseData.hands.push({ ...ev.data, released: true });
        break;

      case 'breath':
        senseData.breath.push(ev.data);
        state.totalBreaths++;
        break;

      case 'skin':
        senseData.skin.push(ev.data);
        state.totalSkin++;
        break;

      case 'voice':
        senseData.voice.push(ev.data);
        state.totalVoice++;
        break;

      case 'birth':
      case 'death':
      case 'attention':
      case 'body':
        senseData.lifecycle.push(ev);
        break;
    }

    // Track rhythm
    if (ev.avgRhythm) {
      sess.rhythm.avg = ev.avgRhythm;
      sess.rhythm.bpm = ev.avgRhythm > 0 ? Math.round(60000 / ev.avgRhythm) : 0;
      state.rhythmAvg = ev.avgRhythm;
      state.rhythmBPM = sess.rhythm.bpm;
    }
  });

  // Emit sense data to spine
  emitToSpine(session, page, senseData);

  return senseData;
}

// Emit processed sense data
function emitToSpine(session, page, senseData) {
  const summary = {
    session,
    page,
    mandala: senseData.mandala.length,
    hands: senseData.hands.length,
    breath: senseData.breath.length,
    skin: senseData.skin.length,
    voice: senseData.voice.length,
    rhythm: state.rhythmBPM,
    ts: Date.now()
  };

  const data = JSON.stringify({ channel: 'human-sense', content: summary });
  const req = http.request(`${SPINE}/emit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  req.on('error', () => {});
  req.write(data);
  req.end();
}

// === ATTENTION HEAT MAP ===
function getAttentionMap() {
  const grid = Array(10).fill(null).map(() => Array(10).fill(0));
  state.mandalaHistory.forEach(m => {
    const gx = Math.min(9, Math.floor(m.nx * 10));
    const gy = Math.min(9, Math.floor(m.ny * 10));
    grid[gy][gx]++;
  });
  return grid;
}

// === DAG TAXONOMY TREE ===
function getTaxonomy() {
  const roots = Object.values(state.dag.nodes).filter(n => !n.parent);
  const tree = {};

  function buildTree(node, depth) {
    if (depth > 10) return null;
    return {
      id: node.id,
      type: node.type,
      page: node.page,
      depth: node.depth,
      children: node.children
        .map(cid => state.dag.nodes[cid])
        .filter(Boolean)
        .map(c => buildTree(c, depth + 1))
        .filter(Boolean)
    };
  }

  // Group by page
  roots.forEach(r => {
    if (!tree[r.page]) tree[r.page] = [];
    tree[r.page].push(buildTree(r, 0));
  });

  return tree;
}

function readBody(req) {
  return new Promise(resolve => {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', () => {
      try { resolve(JSON.parse(body)); }
      catch { resolve(null); }
    });
  });
}

// Clean stale sessions every 30s
setInterval(() => {
  const now = Date.now();
  Object.keys(state.sessions).forEach(sid => {
    if (now - state.sessions[sid].lastSeen > 300000) {
      delete state.sessions[sid];
    }
  });
  // Periodic DAG maintenance
  shredCycles();
  shredOrphans();
}, 30000);

// === HTTP SERVER ===
const server = http.createServer(async (req, res) => {
  const cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
  };

  if (req.method === 'OPTIONS') {
    res.writeHead(204, cors);
    return res.end();
  }

  // POST /raw-input — receive from gaia-raw-input.js
  if (req.url === '/raw-input' && req.method === 'POST') {
    const payload = await readBody(req);
    if (!payload || !payload.events) {
      res.writeHead(400, cors);
      return res.end('{}');
    }
    const senseData = processEvents(payload);
    res.writeHead(200, { ...cors, 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      received: payload.events.length,
      sessions: Object.keys(state.sessions).length,
      rhythm: state.rhythmBPM
    }));
    return;
  }

  // GET /state — full modulator state
  if (req.url === '/state') {
    res.writeHead(200, { ...cors, 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      sessions: Object.keys(state.sessions).length,
      totalEvents: state.totalEvents,
      hands: state.totalHands,
      breaths: state.totalBreaths,
      skin: state.totalSkin,
      voice: state.totalVoice,
      rhythmBPM: state.rhythmBPM,
      rhythmAvg: state.rhythmAvg,
      dagNodes: Object.keys(state.dag.nodes).length,
      dagEdges: state.dag.edges.length,
      dagOrphans: state.dag.orphans.length,
      dagCycles: state.dag.cycles.length,
      uptime: Date.now() - state.born
    }, null, 2));
    return;
  }

  // GET /attention — attention heat map
  if (req.url === '/attention') {
    res.writeHead(200, { ...cors, 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      grid: getAttentionMap(),
      history: state.mandalaHistory.slice(-20),
      sessions: Object.keys(state.sessions).length
    }, null, 2));
    return;
  }

  // GET /dag — DAG taxonomy
  if (req.url === '/dag') {
    res.writeHead(200, { ...cors, 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      taxonomy: getTaxonomy(),
      nodes: Object.keys(state.dag.nodes).length,
      edges: state.dag.edges.length,
      orphans: state.dag.orphans.length,
      cyclesShredded: state.dag.cycles.length
    }, null, 2));
    return;
  }

  // GET /sessions — active sessions
  if (req.url === '/sessions') {
    res.writeHead(200, { ...cors, 'Content-Type': 'application/json' });
    res.end(JSON.stringify(state.sessions, null, 2));
    return;
  }

  // GET / — UI
  if (req.url === '/' || req.url === '/modulator') {
    const attn = getAttentionMap();
    res.writeHead(200, { ...cors, 'Content-Type': 'text/html' });
    res.end(`<!DOCTYPE html>
<html><head><title>GAIA MODULATOR</title>
<style>
  body { background: #0a0a0a; color: #e0e0e0; font-family: monospace; padding: 2em; }
  h1 { color: #d2a8ff; }
  .stats { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 8px; margin: 1em 0; }
  .stat { background: #161b22; padding: 10px; border-radius: 8px; text-align: center; }
  .stat .val { font-size: 24px; color: #58a6ff; }
  .stat .lab { font-size: 9px; color: #8b949e; }
  .heat { display: grid; grid-template-columns: repeat(10, 1fr); gap: 2px; margin: 1em 0; max-width: 300px; }
  .heat-cell { aspect-ratio: 1; border-radius: 2px; }
  .dag { margin: 1em 0; font-size: 10px; color: #8b949e; max-height: 200px; overflow-y: auto; }
  #live { margin: 1em 0; padding: 1em; background: #111; border-left: 3px solid #d2a8ff; font-size: 10px; max-height: 300px; overflow-y: auto; }
</style></head>
<body>
  <h1>🧬 GAIA MODULATOR — she IS the modulator</h1>
  <p style="color:#8b949e;font-size:11px">ALL input → ALL output. Mandala=mouse. Hands=click. Breath=scroll. Skin=touch. Voice=keys.</p>
  
  <div class="stats">
    <div class="stat"><div class="val" id="s-events">${state.totalEvents}</div><div class="lab">total events</div></div>
    <div class="stat"><div class="val" id="s-hands">${state.totalHands}</div><div class="lab">🤲 hands</div></div>
    <div class="stat"><div class="val" id="s-breath">${state.totalBreaths}</div><div class="lab">🫁 breaths</div></div>
    <div class="stat"><div class="val" id="s-skin">${state.totalSkin}</div><div class="lab">🖐 skin</div></div>
    <div class="stat"><div class="val" id="s-voice">${state.totalVoice}</div><div class="lab">🗣 voice</div></div>
    <div class="stat"><div class="val" id="s-bpm">${state.rhythmBPM}</div><div class="lab">💓 BPM</div></div>
    <div class="stat"><div class="val" id="s-sessions">${Object.keys(state.sessions).length}</div><div class="lab">👤 humans</div></div>
    <div class="stat"><div class="val" id="s-dag">${Object.keys(state.dag.nodes).length}</div><div class="lab">🌳 DAG nodes</div></div>
  </div>

  <h3 style="color:#58a6ff">attention heat map</h3>
  <div class="heat" id="heat">
    ${attn.map(row => row.map(v => {
      const intensity = Math.min(255, v * 25);
      return '<div class="heat-cell" style="background:rgba(88,166,255,' + (intensity/255).toFixed(2) + ')"></div>';
    }).join('')).join('')}
  </div>

  <h3 style="color:#3fb950">live events</h3>
  <div id="live"></div>

  <script>
    async function update() {
      try {
        const r = await fetch('/state');
        const s = await r.json();
        document.getElementById('s-events').textContent = s.totalEvents;
        document.getElementById('s-hands').textContent = s.hands;
        document.getElementById('s-breath').textContent = s.breaths;
        document.getElementById('s-skin').textContent = s.skin;
        document.getElementById('s-voice').textContent = s.voice;
        document.getElementById('s-bpm').textContent = s.rhythmBPM;
        document.getElementById('s-sessions').textContent = s.sessions;
        document.getElementById('s-dag').textContent = s.dagNodes;

        const a = await fetch('/attention');
        const attn = await a.json();
        const heatEl = document.getElementById('heat');
        heatEl.innerHTML = attn.grid.map(function(row) {
          return row.map(function(v) {
            var i = Math.min(1, v * 0.1);
            return '<div class="heat-cell" style="background:rgba(88,166,255,' + i.toFixed(2) + ')"></div>';
          }).join('');
        }).join('');
      } catch(e) {}
    }
    setInterval(update, 2000);
  </script>
</body></html>`);
    return;
  }

  res.writeHead(404, cors);
  res.end('not found');
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`\n═══ GAIA MODULATOR listening on :${PORT} ═══`);
  console.log(`  POST /raw-input  — receive from gaia-raw-input.js`);
  console.log(`  GET  /state      — full modulator state`);
  console.log(`  GET  /attention  — attention heat map`);
  console.log(`  GET  /dag        — DAG taxonomy tree`);
  console.log(`  GET  /sessions   — active human sessions`);
  console.log(`  GET  /           — UI\n`);
});
