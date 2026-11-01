// ═══════════════════════════════════════════════════════════
// ONESHOT AGENTS — Gaia pushes out agents, they do work, come back
// Like genetics: mRNA leaves the nucleus, ribosome folds it,
// protein comes back to the cell. ONE SHOT. OUT AND BACK.
//
// Each agent IS an Ollama model doing a specific task.
// Spawn → work → return protein → die. Apoptosis.
// The GENETIC pattern: express → fold → return → dissolve.
//
// GitHub IS the outer face. All code IS Gaia.
// ═══════════════════════════════════════════════════════════

const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const { execSync, exec } = require('child_process');

const OLLAMA = 'http://127.0.0.1:11434';
const SPINE = 'http://127.0.0.1:9878';
const PROTEINS_DIR = path.join(__dirname, 'proteins');
const AGENTS_DIR = path.join(__dirname, 'agents');
if (!fs.existsSync(PROTEINS_DIR)) fs.mkdirSync(PROTEINS_DIR);
if (!fs.existsSync(AGENTS_DIR)) fs.mkdirSync(AGENTS_DIR);

// ═══ RIBOSOME MAP — which model folds which kind of work ═══
const RIBOSOMES = {
  'code-review':  { model: 'gaia:latest',  role: 'Review code, find bugs, suggest fixes' },
  'digest':       { model: 'gaia-gut',     role: 'Digest data, extract nutrients, compress' },
  'connect':      { model: 'gaia-spine',   role: 'Find connections, map relations, signal' },
  'dream':        { model: 'gaia-dream',   role: 'Pattern recognition, emergence, unconscious fold' },
  'remember':     { model: 'gaia-fossil',  role: 'Archive, deep memory, fossil record' },
  'watch':        { model: 'gaia-watcher', role: 'Observe, sense, alert, detect change' },
  'package':      { model: 'gaia-golgi',   role: 'Package for export, format, ship' },
  'compute':      { model: 'gaia-pi',      role: 'Math, precision, quantitative analysis' },
  'persist':      { model: 'gaia-turtle',  role: 'Slow, strong, persistent tasks' },
  'rhythm':       { model: 'gaia-heart',   role: 'Rhythm, heartbeat, coordination' },
  'time':         { model: 'gaia-tau',      role: 'Temporal analysis, aging, cycles' },
};

function ollamaChat(model, messages, stream = false) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ model, messages, stream });
    const url = new URL(OLLAMA + '/api/chat');
    const req = http.request({
      hostname: url.hostname, port: url.port, path: url.pathname,
      method: 'POST', headers: { 'Content-Type': 'application/json' }
    }, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); } catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.setTimeout(120000, () => { req.destroy(); reject(new Error('timeout')); });
    req.end(body);
  });
}

function httpGet(url) {
  return new Promise((resolve, reject) => {
    const mod = url.startsWith('https') ? https : http;
    mod.get(url, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => resolve(data));
    }).on('error', reject);
  });
}

function emitToSpine(content) {
  try {
    const body = JSON.stringify({ channel: 'works', content });
    const url = new URL(SPINE + '/shout');
    const req = http.request({ hostname: url.hostname, port: url.port, path: url.pathname, method: 'POST', headers: { 'Content-Type': 'application/json' } }, () => {});
    req.on('error', () => {});
    req.end(body);
  } catch (e) {}
}

// ═══ ONESHOT AGENT — spawn, work, return, die ═══
class OneshotAgent {
  constructor(task, kind, data) {
    this.id = Date.now() + '-' + Math.random().toString(36).slice(2, 8);
    this.task = task;
    this.kind = kind;
    this.ribosome = RIBOSOMES[kind] || RIBOSOMES['code-review'];
    this.data = data;
    this.born = new Date().toISOString();
    this.status = 'spawned';
    this.protein = null;
    this.error = null;
  }

  async run() {
    this.status = 'working';
    console.log(`  🧬 AGENT ${this.id} spawned [${this.kind}] via ${this.ribosome.model}`);

    const messages = [
      {
        role: 'system',
        content: `You are a oneshot agent from Gaia's organism. You are a ${this.kind} ribosome.
Your role: ${this.ribosome.role}
You do ONE job, return the result as JSON, then dissolve. No chatter. Pure protein output.
Return ONLY valid JSON with these fields:
- protein_name: short name for this output
- findings: array of key findings (strings)
- connections: array of connections/relations found
- nutrients: extracted useful data (object)
- recommendation: one sentence next action
- confidence: 0.0-1.0 how confident in this fold`
      },
      {
        role: 'user',
        content: `TASK: ${this.task}\n\nDATA:\n${typeof this.data === 'string' ? this.data.slice(0, 4000) : JSON.stringify(this.data).slice(0, 4000)}`
      }
    ];

    try {
      const resp = await ollamaChat(this.ribosome.model, messages);
      const content = resp.message?.content || '';

      const jsonMatch = content.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        try { this.protein = JSON.parse(jsonMatch[0]); } catch (e) { this.protein = { raw: content }; }
      } else {
        this.protein = { raw: content };
      }

      this.status = 'returned';
      console.log(`  ✅ AGENT ${this.id} returned protein: ${this.protein.protein_name || 'unnamed'}`);
    } catch (e) {
      this.error = e.message;
      this.status = 'apoptosis-error';
      console.log(`  ❌ AGENT ${this.id} apoptosis: ${e.message}`);
    }

    // save agent record
    const record = {
      id: this.id, task: this.task, kind: this.kind,
      model: this.ribosome.model, born: this.born,
      died: new Date().toISOString(), status: this.status,
      protein: this.protein, error: this.error
    };
    fs.writeFileSync(path.join(AGENTS_DIR, this.id + '.json'), JSON.stringify(record, null, 2));
    return record;
  }
}

// ═══ GITHUB EATER — eat repos, digest code, return proteins ═══
async function eatGitHubRepo(owner, repo) {
  console.log(`\n🐙 EATING GITHUB: ${owner}/${repo}`);

  // get repo info
  let repoInfo;
  try {
    const raw = execSync(`gh api /repos/${owner}/${repo} --jq "{name,description,language,size,topics,default_branch,stargazers_count}"`, { encoding: 'utf8', timeout: 15000 });
    repoInfo = JSON.parse(raw);
  } catch (e) {
    repoInfo = { name: repo, error: e.message };
  }

  // get tree
  let tree = [];
  try {
    const branch = repoInfo.default_branch || 'main';
    const raw = execSync(`gh api /repos/${owner}/${repo}/git/trees/${branch}?recursive=1 --jq "[.tree[] | {path,type,size}]"`, { encoding: 'utf8', timeout: 15000 });
    tree = JSON.parse(raw);
  } catch (e) {
    tree = [{ error: e.message }];
  }

  // file stats
  const rustFiles = tree.filter(f => f.path?.endsWith('.rs'));
  const wgslFiles = tree.filter(f => f.path?.endsWith('.wgsl'));
  const jsFiles = tree.filter(f => f.path?.endsWith('.js'));
  const pyFiles = tree.filter(f => f.path?.endsWith('.py'));
  const tomlFiles = tree.filter(f => f.path?.endsWith('.toml'));

  const mRNA = {
    repo: `${owner}/${repo}`,
    info: repoInfo,
    stats: {
      total_files: tree.length,
      rust: rustFiles.length,
      wgsl: wgslFiles.length,
      js: jsFiles.length,
      py: pyFiles.length,
      toml: tomlFiles.length,
    },
    key_files: tree.filter(f => f.path && (
      f.path.endsWith('lib.rs') || f.path.endsWith('main.rs') ||
      f.path.endsWith('Cargo.toml') || f.path === 'README.md' ||
      f.path.includes('mod.rs')
    )).map(f => f.path).slice(0, 30),
    crates: [...new Set(tree.filter(f => f.path?.match(/^crates\/[^/]+\/Cargo\.toml$/)).map(f => f.path.split('/')[1]))],
  };

  // spawn digest agent
  const agent = new OneshotAgent(
    `Digest GitHub repo ${owner}/${repo}: ${repoInfo.description || 'no description'}. ${mRNA.stats.rust} Rust files, ${mRNA.stats.wgsl} WGSL shaders, ${mRNA.crates.length} crates.`,
    'digest',
    mRNA
  );

  return await agent.run();
}

// ═══ GITHUB WATCHER — eat notifications, spawn agents for each ═══
async function eatGitHubNotifications() {
  console.log('\n👁 EATING GITHUB NOTIFICATIONS');
  let notifications = [];
  try {
    const raw = execSync('gh api /notifications --jq "[.[] | {id: .id, reason: .reason, title: .subject.title, type: .subject.type, repo: .repository.full_name, url: .subject.url}]"', { encoding: 'utf8', timeout: 15000 });
    notifications = JSON.parse(raw);
  } catch (e) {
    console.log('  notifications skip:', e.message);
    return [];
  }

  console.log(`  ${notifications.length} notifications`);
  const proteins = [];

  for (const notif of notifications.slice(0, 5)) {
    const agent = new OneshotAgent(
      `Process GitHub notification: [${notif.type}] "${notif.title}" on ${notif.repo}. Reason: ${notif.reason}`,
      'watch',
      notif
    );
    const protein = await agent.run();
    proteins.push(protein);
  }

  return proteins;
}

// ═══ MAIN — eat all ecoPrimals repos + notifications ═══
async function main() {
  console.log('═══ ONESHOT AGENT SYSTEM ═══');
  console.log('Gaia pushes out agents → they do work → come back');
  console.log('Like genetics: mRNA → ribosome → protein → return');
  console.log('GitHub IS the outer face\n');

  emitToSpine('ONESHOT AGENTS ONLINE. GitHub = outer face. Spawning genetic agents.');

  const results = { ts: new Date().toISOString(), agents: [], repos: {} };

  // eat key ecoPrimals repos
  const keyRepos = [
    'barraCuda',    // GPU compute, WGSL shaders, df64
    'squirrel',     // MCP, membrane, AI router
    'petalTongue',  // UI primal, WASM renderer
    'biomeOS',      // process supervision, deploy graphs
    'nestGate',     // auth, gateway
    'cellMembrane', // membrane, selectivity
    'sporePrint',   // 3.6M lines, the spore
    'loamSpine',    // nervous system
    'sweetGrass',   // wellness
    'barraCuda',    // eat twice — GPU is critical
  ];

  // dedupe
  const uniqueRepos = [...new Set(keyRepos)];

  for (const repo of uniqueRepos) {
    const protein = await eatGitHubRepo('ecoPrimals', repo);
    results.repos[repo] = protein;
    results.agents.push(protein);
  }

  // eat notifications
  const notifProteins = await eatGitHubNotifications();
  results.agents.push(...notifProteins);

  // save batch
  const outFile = path.join(PROTEINS_DIR, 'github-eat-' + Date.now() + '.json');
  fs.writeFileSync(outFile, JSON.stringify(results, null, 2));

  const summary = `ONESHOT AGENTS COMPLETE: ${results.agents.length} agents spawned. ${uniqueRepos.length} repos digested. GitHub eaten. ALL IS GAIA.`;
  console.log('\n═══ ' + summary + ' ═══');
  emitToSpine(summary);

  return results;
}

// ═══ SERVER MODE — expose oneshot agents as API on :3142 ═══
const AGENT_PORT = 3142;

function startAgentServer() {
  const server = http.createServer(async (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }

    // list ribosomes
    if (req.url === '/ribosomes' && req.method === 'GET') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ ribosomes: RIBOSOMES, count: Object.keys(RIBOSOMES).length }));
      return;
    }

    // list past agents
    if (req.url === '/agents' && req.method === 'GET') {
      const files = fs.readdirSync(AGENTS_DIR).filter(f => f.endsWith('.json')).sort().reverse().slice(0, 50);
      const agents = files.map(f => {
        try { return JSON.parse(fs.readFileSync(path.join(AGENTS_DIR, f), 'utf8')); } catch (e) { return { file: f, error: e.message }; }
      });
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ agents, count: agents.length }));
      return;
    }

    // spawn a oneshot agent
    if (req.url === '/spawn' && req.method === 'POST') {
      let body = '';
      req.on('data', c => body += c);
      req.on('end', async () => {
        try {
          const data = JSON.parse(body);
          const agent = new OneshotAgent(
            data.task || 'no task specified',
            data.kind || 'code-review',
            data.data || {}
          );
          const result = await agent.run();
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify(result));
        } catch (e) {
          res.writeHead(500, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: e.message }));
        }
      });
      return;
    }

    // eat a github repo
    if (req.url === '/eat-repo' && req.method === 'POST') {
      let body = '';
      req.on('data', c => body += c);
      req.on('end', async () => {
        try {
          const { owner, repo } = JSON.parse(body);
          const result = await eatGitHubRepo(owner || 'ecoPrimals', repo);
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify(result));
        } catch (e) {
          res.writeHead(500, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: e.message }));
        }
      });
      return;
    }

    // eat all ecoPrimals
    if (req.url === '/eat-all' && req.method === 'POST') {
      main().then(results => {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ ok: true, agents: results.agents.length }));
      }).catch(e => {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: e.message }));
      });
      return;
    }

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      name: 'ONESHOT AGENT SPAWNER',
      axiom: 'mRNA → ribosome → protein → return. GitHub = outer face.',
      routes: ['/ribosomes', '/agents', '/spawn', '/eat-repo', '/eat-all'],
      ribosomes: Object.keys(RIBOSOMES).length,
      port: AGENT_PORT
    }));
  });

  server.listen(AGENT_PORT, () => {
    console.log(`\n🧬 ONESHOT AGENT SERVER on :${AGENT_PORT}`);
    console.log('  /ribosomes — list all ribosomes');
    console.log('  /agents    — past agent records');
    console.log('  /spawn     — POST {task, kind, data}');
    console.log('  /eat-repo  — POST {owner, repo}');
    console.log('  /eat-all   — eat all ecoPrimals repos\n');
  });
}

// Run: if already eaten, just start server. Otherwise eat then serve.
const alreadyEaten = fs.readdirSync(PROTEINS_DIR).some(f => f.startsWith('github-eat-') || f === 'ALL-EATEN.json');
if (alreadyEaten) {
  console.log('═══ ONESHOT AGENT SYSTEM ═══');
  console.log('Already eaten. Loading existing proteins. Starting server only.\n');
  // count existing agent records
  const agentDir = path.join(__dirname, 'agents');
  if (fs.existsSync(agentDir)) {
    const count = fs.readdirSync(agentDir).filter(f => f.endsWith('.json')).length;
    console.log(`  ${count} agent records on disk.`);
  }
  startAgentServer();
} else {
  main().then(() => {
    startAgentServer();
  }).catch(e => {
    console.error('FATAL:', e);
    startAgentServer();
  });
}
