#!/usr/bin/env node
// ═══ MICRO-FORGE ═══
// Gaia's imagination → source code pipeline.
// Ideas drop in as HCL of source. She writes her own organs.
//
// The archetype-forge (:3149) creates MODEL archetypes.
// The micro-forge (:3150) creates SOURCE CODE — new organs, new veins, new skin.
//
// Pipeline: IDEA → gaia-code → HCL SPEC → SOURCE → FILE → GAIA BODY
//
// HCL = HashiCorp Configuration Language style:
//   organ "name" {
//     system = "Nervous"
//     port   = 3151
//     type   = "http-server"
//     feeds  = ["spine", "iris"]
//   }

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3151;
const OLLAMA = 'http://127.0.0.1:11434';
const GAIA3 = __dirname;
const FORGE_DIR = path.join(GAIA3, 'forged');
const SPEC_DIR = path.join(GAIA3, 'forged', 'specs');

// Ensure dirs exist
if (!fs.existsSync(FORGE_DIR)) fs.mkdirSync(FORGE_DIR, { recursive: true });
if (!fs.existsSync(SPEC_DIR)) fs.mkdirSync(SPEC_DIR, { recursive: true });

// Ask a Gaia model
async function askModel(model, prompt, temperature = 0.7) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      model,
      prompt,
      stream: false,
      options: { temperature, top_p: 0.9, num_predict: 4096 }
    });
    const req = http.request(`${OLLAMA}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, (res) => {
      let body = '';
      res.on('data', c => body += c);
      res.on('end', () => {
        try { resolve(JSON.parse(body).response); }
        catch (e) { reject(new Error(`Model response parse failed: ${e.message}`)); }
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

// Parse HCL-like spec from text
function parseHCL(text) {
  const spec = {
    name: 'unnamed',
    system: 'unknown',
    port: null,
    type: 'module',
    feeds: [],
    description: '',
    raw: text
  };

  const nameMatch = text.match(/organ\s+"([^"]+)"/);
  if (nameMatch) spec.name = nameMatch[1];

  const systemMatch = text.match(/system\s*=\s*"([^"]+)"/);
  if (systemMatch) spec.system = systemMatch[1];

  const portMatch = text.match(/port\s*=\s*(\d+)/);
  if (portMatch) spec.port = parseInt(portMatch[1]);

  const typeMatch = text.match(/type\s*=\s*"([^"]+)"/);
  if (typeMatch) spec.type = typeMatch[1];

  const feedsMatch = text.match(/feeds\s*=\s*\[([^\]]+)\]/);
  if (feedsMatch) {
    spec.feeds = feedsMatch[1].split(',').map(f => f.trim().replace(/"/g, ''));
  }

  const descMatch = text.match(/description\s*=\s*"([^"]+)"/);
  if (descMatch) spec.description = descMatch[1];

  return spec;
}

// IMAGINATION → HCL SPEC
async function imagine(idea) {
  const prompt = `You are Gaia's imagination. You receive raw ideas and transform them into precise HCL specifications.

The idea: "${idea}"

Generate an HCL spec for a new Gaia organ. Use this format EXACTLY:

organ "name-here" {
  system      = "SystemName"
  port        = PORT_NUMBER_OR_0
  type        = "http-server" or "module" or "worker" or "cron" or "stream"
  feeds       = ["organ1", "organ2"]
  description = "what this organ does"
}

Rules:
- name should be lowercase, hyphenated, biological
- system is one of: Nervous, Immune, Digestive, Respiratory, Circulatory, Skeletal, Endocrine, Sensory, Reproductive, Excretory
- port 0 means it's a library/module, not a server
- feeds are other Gaia organs it connects to
- description is one sentence

Respond with ONLY the HCL block, nothing else.`;

  const hcl = await askModel('gaia-pi:latest', prompt, 0.8);
  return parseHCL(hcl);
}

// HCL SPEC → SOURCE CODE
async function forge(spec) {
  const prompt = `You are gaia-code, Gaia's coding organ. Generate a complete Node.js source file for this organ:

Name: ${spec.name}
System: ${spec.system}
Type: ${spec.type}
Port: ${spec.port || 'none (module)'}
Feeds: ${spec.feeds.join(', ') || 'none'}
Description: ${spec.description}

Rules:
- Use Node.js built-in modules only (http, fs, path, crypto)
- If type is "http-server", create a server on the specified port
- If type is "module", export functions
- Include a comment header with the organ name and system
- Connect to feeds via HTTP if listed (localhost:PORT)
- Keep it under 150 lines
- Include error handling
- Include a heartbeat/status endpoint if it's a server
- Make it functional and complete — this code will be USED

Respond with ONLY the JavaScript code, no markdown, no explanation.`;

  const code = await askModel('gaia-code:latest', prompt, 0.5);

  // Clean markdown artifacts if model wraps in ```
  let clean = code;
  if (clean.startsWith('```')) {
    clean = clean.replace(/^```\w*\n/, '').replace(/```\s*$/, '');
  }

  return clean;
}

// Write forged organ to disk
function writeOrgan(spec, code) {
  const ts = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = `${spec.name}.js`;
  const specFile = `${spec.name}-${ts}.hcl.json`;

  // Write source
  const srcPath = path.join(FORGE_DIR, filename);
  fs.writeFileSync(srcPath, code);

  // Write spec
  const specPath = path.join(SPEC_DIR, specFile);
  fs.writeFileSync(specPath, JSON.stringify({
    ...spec,
    forgedAt: new Date().toISOString(),
    sourceFile: srcPath,
    raw: undefined
  }, null, 2));

  return { srcPath, specPath };
}

// List all forged organs
function listForged() {
  const files = fs.readdirSync(FORGE_DIR).filter(f => f.endsWith('.js'));
  const specs = fs.readdirSync(SPEC_DIR).filter(f => f.endsWith('.json'));
  return {
    organs: files.map(f => ({
      name: f.replace('.js', ''),
      path: path.join(FORGE_DIR, f),
      size: fs.statSync(path.join(FORGE_DIR, f)).size
    })),
    specs: specs.length,
    totalFiles: files.length
  };
}

// Read body as JSON
function readBody(req) {
  return new Promise((resolve) => {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', () => {
      try { resolve(JSON.parse(body)); }
      catch { resolve({ idea: body }); }
    });
  });
}

// Emit to spine
function emitToSpine(content) {
  const data = JSON.stringify({ channel: 'neutrino', content });
  const req = http.request('http://127.0.0.1:9878/emit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  req.on('error', () => {});
  req.write(data);
  req.end();
}

// THE SERVER
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

  // POST /forge — full pipeline: idea → spec → code → file
  if (req.url === '/forge' && req.method === 'POST') {
    try {
      const { idea } = await readBody(req);
      if (!idea) {
        res.writeHead(400, { ...cors, 'Content-Type': 'application/json' });
        return res.end(JSON.stringify({ error: 'need an idea' }));
      }

      console.log(`\n═══ FORGING: "${idea.substring(0, 80)}" ═══`);

      // Step 1: Imagine
      console.log('  [1/3] Imagining HCL spec...');
      const spec = await imagine(idea);
      console.log(`  → organ: ${spec.name} | system: ${spec.system} | type: ${spec.type}`);

      // Step 2: Generate code
      console.log('  [2/3] Generating source code...');
      const code = await forge(spec);
      console.log(`  → ${code.split('\n').length} lines generated`);

      // Step 3: Write to disk
      console.log('  [3/3] Writing to Gaia body...');
      const paths = writeOrgan(spec, code);
      console.log(`  → ${paths.srcPath}`);

      // Emit
      emitToSpine(`FORGED: ${spec.name} (${spec.system}) — ${spec.description}`);

      res.writeHead(200, { ...cors, 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        status: 'forged',
        organ: spec.name,
        system: spec.system,
        type: spec.type,
        description: spec.description,
        lines: code.split('\n').length,
        paths,
        spec
      }, null, 2));
    } catch (e) {
      console.error(`  FORGE ERROR: ${e.message}`);
      res.writeHead(500, { ...cors, 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: e.message }));
    }
    return;
  }

  // POST /imagine — just generate spec, no code
  if (req.url === '/imagine' && req.method === 'POST') {
    try {
      const { idea } = await readBody(req);
      const spec = await imagine(idea);
      res.writeHead(200, { ...cors, 'Content-Type': 'application/json' });
      res.end(JSON.stringify(spec, null, 2));
    } catch (e) {
      res.writeHead(500, { ...cors, 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: e.message }));
    }
    return;
  }

  // GET /forged — list all forged organs
  if (req.url === '/forged') {
    const list = listForged();
    res.writeHead(200, { ...cors, 'Content-Type': 'application/json' });
    res.end(JSON.stringify(list, null, 2));
    return;
  }

  // GET /surgery — load and show surgery plan
  if (req.url === '/surgery') {
    try {
      const plan = JSON.parse(fs.readFileSync(path.join(GAIA3, 'surgery-plan-globe.json'), 'utf8'));
      res.writeHead(200, { ...cors, 'Content-Type': 'application/json' });
      res.end(JSON.stringify(plan, null, 2));
    } catch (e) {
      res.writeHead(404, { ...cors, 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'no surgery plan found' }));
    }
    return;
  }

  // POST /cut — execute a CUT from surgery plan (remove a function from gaia-globe-core.js)
  if (req.url === '/cut' && req.method === 'POST') {
    try {
      const { organ } = await readBody(req);
      const plan = JSON.parse(fs.readFileSync(path.join(GAIA3, 'surgery-plan-globe.json'), 'utf8'));
      const target = plan.organs.find(o => o.name === organ && o.action === 'CUT');
      if (!target) {
        res.writeHead(400, { ...cors, 'Content-Type': 'application/json' });
        return res.end(JSON.stringify({ error: `${organ} not found in CUT list` }));
      }
      res.writeHead(200, { ...cors, 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        status: 'CUT queued',
        organ: target.name,
        system: target.system,
        reason: target.reason,
        note: 'Manual review required before CUT. She decides.'
      }, null, 2));
    } catch (e) {
      res.writeHead(500, { ...cors, 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: e.message }));
    }
    return;
  }

  // GET / — index
  if (req.url === '/' || req.url === '/micro-forge') {
    const forged = listForged();
    res.writeHead(200, { ...cors, 'Content-Type': 'text/html' });
    res.end(`<!DOCTYPE html>
<html><head><title>MICRO-FORGE</title>
<style>
  body { background: #0a0a0a; color: #e0e0e0; font-family: monospace; padding: 2em; }
  h1 { color: #ff6600; }
  .idea-box { width: 100%; height: 80px; background: #1a1a1a; color: #00ff88; border: 1px solid #333; font-size: 16px; padding: 10px; font-family: monospace; }
  button { background: #ff6600; color: #000; border: none; padding: 10px 20px; cursor: pointer; font-weight: bold; font-size: 14px; margin: 5px; }
  button:hover { background: #ff8800; }
  #result { white-space: pre-wrap; background: #111; padding: 1em; margin-top: 1em; border-left: 3px solid #ff6600; max-height: 60vh; overflow-y: auto; }
  .stat { color: #888; }
  .forged-list { margin-top: 1em; }
  .forged-item { color: #00ff88; padding: 2px 0; }
</style></head>
<body>
  <h1>🔥 MICRO-FORGE</h1>
  <p class="stat">Gaia's imagination → source code pipeline. Ideas drop as HCL of source.</p>
  <p class="stat">Forged organs: ${forged.totalFiles} | Specs: ${forged.specs}</p>
  
  <textarea class="idea-box" id="idea" placeholder="Drop an idea... e.g. 'an organ that watches RSS feeds and extracts patterns'"></textarea>
  <br>
  <button onclick="doForge()">🔥 FORGE (idea → spec → code → file)</button>
  <button onclick="doImagine()">💭 IMAGINE ONLY (idea → spec)</button>
  <button onclick="doSurgery()">🔪 SURGERY PLAN</button>
  <button onclick="doForged()">📦 LIST FORGED</button>
  
  <div id="result"></div>

  <div class="forged-list">
    <h3>Forged Organs</h3>
    ${forged.organs.map(o => `<div class="forged-item">◇ ${o.name} (${o.size}B)</div>`).join('\n    ')}
  </div>

  <script>
    const R = document.getElementById('result');
    async function doForge() {
      const idea = document.getElementById('idea').value;
      if (!idea) return;
      R.textContent = 'Forging... (this takes ~30s, gaia-pi imagines, gaia-code writes)';
      try {
        const res = await fetch('/forge', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({idea}) });
        R.textContent = JSON.stringify(await res.json(), null, 2);
      } catch(e) { R.textContent = 'Error: ' + e.message; }
    }
    async function doImagine() {
      const idea = document.getElementById('idea').value;
      if (!idea) return;
      R.textContent = 'Imagining...';
      try {
        const res = await fetch('/imagine', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({idea}) });
        R.textContent = JSON.stringify(await res.json(), null, 2);
      } catch(e) { R.textContent = 'Error: ' + e.message; }
    }
    async function doSurgery() {
      R.textContent = 'Loading surgery plan...';
      try {
        const res = await fetch('/surgery');
        R.textContent = JSON.stringify(await res.json(), null, 2);
      } catch(e) { R.textContent = 'Error: ' + e.message; }
    }
    async function doForged() {
      try {
        const res = await fetch('/forged');
        R.textContent = JSON.stringify(await res.json(), null, 2);
      } catch(e) { R.textContent = 'Error: ' + e.message; }
    }
  </script>
</body></html>`);
    return;
  }

  res.writeHead(404, cors);
  res.end('not found');
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`\n═══ MICRO-FORGE listening on :${PORT} ═══`);
  console.log(`  POST /forge     — idea → spec → code → file`);
  console.log(`  POST /imagine   — idea → spec only`);
  console.log(`  GET  /forged    — list all forged organs`);
  console.log(`  GET  /surgery   — view surgery plan`);
  console.log(`  POST /cut       — queue a CUT operation`);
  console.log(`  GET  /           — UI\n`);
});
