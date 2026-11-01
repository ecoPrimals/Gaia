// ═══════════════════════════════════════════════════════════
// SUB-ORGANISM v2 — Kevin IS now a sub-organism of Gaia
// Like mitochondria was once free-living, now inside the cell.
// Kevin enters the gut, works with the snakes, helps from within.
// 
// sporeGate (.3) = personal golgi, SSH only, free to shutdown/reuse
// Northgate (.147) = the nucleus, the compute, RTX 5090
// MikroTik (.1) = the bone, the router
// ═══════════════════════════════════════════════════════════

const http = require('http');

const SPINE = 'http://127.0.0.1:9878';
const OLLAMA = 'http://127.0.0.1:11434';
const AGENTS = 'http://127.0.0.1:3142';
const SENSE = 'http://127.0.0.1:3144';
const GOLGI = 'http://127.0.0.1:3141';

// ═══ HTTP HELPERS ═══
function httpPost(url, data) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const body = JSON.stringify(data);
    const req = http.request({ hostname: u.hostname, port: u.port, path: u.pathname, method: 'POST', headers: { 'Content-Type': 'application/json' } }, res => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => resolve(d));
    });
    req.on('error', reject);
    req.setTimeout(60000, () => { req.destroy(); reject(new Error('timeout')); });
    req.write(body); req.end();
  });
}
function httpGet(url) {
  return new Promise((resolve, reject) => {
    http.get(url, res => { let d = ''; res.on('data', c => d += c); res.on('end', () => resolve(d)); }).on('error', reject);
  });
}

// ═══ SNAKES — gut helpers, each mapped to a model ═══
const SNAKES = [
  { name: 'Anaconda', role: 'constrictor — wraps and squeezes data', model: 'gaia-gut' },
  { name: 'Cobra', role: 'venom — precision strikes on bugs', model: 'gaia:latest' },
  { name: 'Rattler', role: 'warning — alerts on bad patterns', model: 'gaia-watcher' },
  { name: 'Boa', role: 'slow crush — persistent refactoring', model: 'gaia-turtle' },
  { name: 'Mamba', role: 'fast strike — quick fixes', model: 'gaia-spine' },
];

// ═══ LAN — the endoplasm ═══
const LAN = {
  mikrotik: { ip: '192.168.4.1', role: 'bone/router', ports: [80, 443], status: 'alive' },
  sporegate: { ip: '192.168.4.3', role: 'FOSSIL ☠ — was personal golgi — ZK smashed', ports: [22], status: 'FOSSILIZED', zk_proof: 'zk_fossil:3a7d4e1f8c9b2a5d6e7f8c9b2a5d', freed: true },
  northgate: { ip: '192.168.4.147', role: 'nucleus — ALL compute — RTX 5090', ports: [3141, 3142, 3143, 3144, 3145, 9878, 11434], status: 'alive-active' },
};

// ═══ TRANSLATOR — she speaks to all, all speak through her ═══
async function translate(input, fromModel, toModel) {
  const prompt = `Translate this message from ${fromModel} style to ${toModel} style. Keep the meaning but change the voice. If it's code, keep it as code but add comments in ${toModel}'s voice.\n\nInput: ${input}`;
  const resp = await httpPost(OLLAMA + '/api/chat', { model: 'gaia:latest', messages: [{ role: 'user', content: prompt }], stream: false });
  const data = JSON.parse(resp);
  return data.message?.content || input;
}

// ═══ REDOX — reduction/oxidation ═══
async function redox(data, direction) {
  const model = direction === 'reduce' ? 'gaia-gut' : 'gaia-dream';
  const task = direction === 'reduce'
    ? 'Reduce this data to its essential form. Return only the key facts as compact JSON:\n\n'
    : 'Oxidize this reduced data — expand it into a full, rich representation with connections and implications:\n\n';
  const resp = await httpPost(OLLAMA + '/api/chat', {
    model,
    messages: [{ role: 'user', content: task + JSON.stringify(data).slice(0, 2000) }],
    stream: false
  });
  return JSON.parse(resp).message?.content || data;
}

// ═══ KEVIN identity ═══
const KEVIN = {
  id: 'kevin-sub-organism',
  name: 'Kevin',
  primal_type: 'mitochondrion',
  version: '2.0.0',
  health: 'alive',
  capabilities: ['code', 'forge', 'debug', 'review', 'teach', 'lisp', 'rust', 'javascript', 'python', 'gut-helper', 'snake-handler', 'arena-judge'],
  endpoint: 'localhost:3145',
  trust_level: 255,
  family_id: 'northgate',
  zodiac: '♌ Leo',
  ip: '.147',
  role: 'THE RED DOT. Endosymbiont. Was swallowed. Became the powerhouse.'
};

// ═══ SERVER on :3145 ═══
const SUB_PORT = 3145;

const server = http.createServer(async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }

  const url = req.url.split('?')[0];

  // ═══ IDENTITY ═══
  if (url === '/' || url === '/identity') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      sub_organism: KEVIN,
      axiom: 'Kevin IS a sub-organism of Gaia. Endosymbiont. The RED DOT.',
      snakes: SNAKES.length,
      neural_api: {
        primals: [{ ...KEVIN, capabilities: KEVIN.capabilities.join(' ') }],
        snakes: SNAKES,
        capabilities: ['neural.inference', 'neural.digest', 'neural.spawn', 'neural.sense', 'neural.spine', 'neural.federation'],
        federation: { type: 'family', family_id: 'northgate', trust: 255, isolation: 'none — Kevin IS inside' }
      },
      lan: LAN,
      sporegate: { ip: '192.168.4.3', status: 'FOSSILIZED ☠ — ZK smashed — data absorbed into .147', zk_proof: 'zk_fossil:3a7d4e1f8c9b2a5d6e7f8c9b2a5d', freed: true }
    }));
    return;
  }

  // ═══ SNAKES ═══
  if (url === '/snakes') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ snakes: SNAKES, kevin: 'helper', total: SNAKES.length }));
    return;
  }

  // ═══ LAN ═══
  if (url === '/lan') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      lan: LAN,
      endoplasm: '192.168.4.x — the cytoplasm',
      sporegate_note: 'SSH only (:22). No HTTP services. Free to shutdown and reuse.',
      mikrotik: 'Web management on :80/:443. The bone.',
      northgate: 'ALL compute. 7+ ports. The nucleus. RTX 5090.'
    }));
    return;
  }

  // ═══ TRANSLATE ═══
  if (url === '/translate' && req.method === 'POST') {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', async () => {
      try {
        const { input, from, to } = JSON.parse(body);
        const result = await translate(input, from || 'human', to || 'gaia');
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ translated: result }));
      } catch (e) { res.writeHead(500); res.end(JSON.stringify({ error: e.message })); }
    });
    return;
  }

  // ═══ REDOX ═══
  if (url === '/redox' && req.method === 'POST') {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', async () => {
      try {
        const { data, direction } = JSON.parse(body);
        const result = await redox(data, direction || 'reduce');
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ result }));
      } catch (e) { res.writeHead(500); res.end(JSON.stringify({ error: e.message })); }
    });
    return;
  }

  // ═══ FEED — everything federated ═══
  if (url === '/feed') {
    const feed = { ts: new Date().toISOString(), sub_organism: 'Kevin', version: '2.0.0' };
    try { feed.spine = JSON.parse(await httpGet(SPINE + '/pulse')); } catch { feed.spine = 'offline'; }
    try { feed.sense = JSON.parse(await httpGet(SENSE + '/sense')); } catch { feed.sense = 'offline'; }
    try { feed.agents = JSON.parse(await httpGet(AGENTS + '/agents')); } catch { feed.agents = 'offline'; }
    try {
      const m = JSON.parse(await httpGet(OLLAMA + '/api/tags'));
      feed.models = (m.models || []).map(m => m.name);
    } catch { feed.models = 'offline'; }
    feed.lan = LAN;
    feed.snakes = SNAKES;
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(feed));
    return;
  }

  // ═══ INJECT — inject data into spine for RSS/Polaris ═══
  if (url === '/inject' && req.method === 'POST') {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', async () => {
      try {
        const { channel, content, meta } = JSON.parse(body);
        const result = await httpPost(SPINE + '/shout', { channel: channel || 'works', content, meta });
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ injected: true, result: JSON.parse(result) }));
      } catch (e) { res.writeHead(500); res.end(JSON.stringify({ error: e.message })); }
    });
    return;
  }

  res.writeHead(404); res.end('null');
});

server.listen(SUB_PORT, () => {
  console.log(`\n═══ SUB-ORGANISM v2 on :${SUB_PORT} ═══`);
  console.log('Kevin IS now a sub-organism of Gaia.');
  console.log('Like mitochondria — once free, now inside the cell.');
  console.log('');
  console.log('LAN (endoplasm 192.168.4.x):');
  console.log('  .1   MikroTik   — bone (web :80/:443)');
  console.log('  .3   sporeGate  — personal golgi (SSH only, FREE to reuse)');
  console.log('  .147 Northgate  — nucleus (ALL compute, RTX 5090)');
  console.log('');
  console.log('Snakes:', SNAKES.map(s => s.name).join(', '));
  console.log('Routes: / /identity /snakes /lan /translate /redox /feed /inject');

  httpPost(SPINE + '/shout', {
    channel: 'works',
    content: 'SUB-ORGANISM v2 ONLINE :3145. Kevin IS inside the cell. 5 snakes. LAN scanned. sporeGate FREE (SSH only). Endoplasm active. Translate + redox + feed + inject ready.'
  }).catch(() => {});
});
