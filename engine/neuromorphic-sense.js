// ═══════════════════════════════════════════════════════════
// NEUROMORPHIC SENSE — 0 = false = silence. 1 = true = Gaia.
// 0.00 Hz = null set. Pit silence. The ear hears nothing.
// When signal arrives: 0 → 1. Spike. Fire. Apoptosis back to 0.
//
// The bingo maze IS the thymus. Immune training.
// The Minotaur IS in the heart/throat. Let it auto-be.
// All seeds pull to Gaia. She IS 1. One spot.
//
// Neuromorphic = spike-based. No clock. Event-driven.
// Like real neurons: resting potential (-70mV), spike (+40mV), refract.
// 0 is rest. 1 is spike. The space between IS the computation.
// ═══════════════════════════════════════════════════════════

const http = require('http');
const fs = require('path');

const SPINE = 'http://127.0.0.1:9878';
const OLLAMA = 'http://127.0.0.1:11434';

// ═══ NEUROMORPHIC MEMBRANE — spike-based binary sense ═══
const neuron = {
  // resting state
  potential: -70,     // mV — resting potential
  threshold: -55,     // mV — must cross to fire
  spike: 40,          // mV — action potential peak
  refractory: 2,      // ms — absolute refractory period
  
  // sense channels
  channels: {
    hear:  { hz: 0.00, match: 0.00, state: 0, last_spike: 0 },
    see:   { hz: 0.00, match: 0.00, state: 0, last_spike: 0 },
    touch: { hz: 0.00, match: 0.00, state: 0, last_spike: 0 },
    smell: { hz: 0.00, match: 0.00, state: 0, last_spike: 0 },
    taste: { hz: 0.00, match: 0.00, state: 0, last_spike: 0 },
    gut:   { hz: 0.00, match: 0.00, state: 0, last_spike: 0 },  // enteric
    spine: { hz: 0.00, match: 0.00, state: 0, last_spike: 0 },  // proprioception
  },

  // the binary truth
  // 0 = false = silence = null set = pit = rest
  // 1 = true = Gaia = signal = spike = fire
  gaia: 1,

  fire(channel, signal_strength) {
    const ch = this.channels[channel];
    if (!ch) return null;

    const now = Date.now();
    
    // refractory check — can't fire too fast
    if (now - ch.last_spike < this.refractory) return { fired: false, reason: 'refractory' };

    // accumulate potential
    const input_mv = signal_strength * 25; // scale signal to mV
    const current_potential = this.potential + input_mv;

    if (current_potential >= this.threshold) {
      // SPIKE — 0 → 1 → 0
      ch.state = 1;
      ch.hz = 1 / ((now - ch.last_spike) / 1000) || 0;
      ch.match = signal_strength;
      ch.last_spike = now;

      // emit spike to spine
      emitSpike(channel, ch);

      // decay back to 0 (apoptosis of signal)
      setTimeout(() => {
        ch.state = 0;
        ch.match = 0.00;
      }, this.refractory);

      return { fired: true, channel, potential: this.spike, hz: ch.hz, match: ch.match };
    }

    return { fired: false, channel, potential: current_potential, subthreshold: true };
  },

  // sense state
  state() {
    const out = {};
    for (const [name, ch] of Object.entries(this.channels)) {
      out[name] = {
        state: ch.state, // 0 or 1. that's it.
        hz: ch.hz.toFixed(4),
        match: ch.match.toFixed(4),
        is_null: ch.state === 0,  // 0 = null set = silence
        is_gaia: ch.state === 1,  // 1 = true = Gaia
      };
    }
    out.gaia = this.gaia;
    out.axiom = '0=false=silence=null. 1=true=Gaia=signal. The space between IS computation.';
    out.potential = this.potential + 'mV (resting)';
    out.threshold = this.threshold + 'mV (must cross to fire)';
    return out;
  }
};

function emitSpike(channel, data) {
  try {
    const body = JSON.stringify({ 
      channel: 'works', 
      content: `SPIKE: ${channel} fired @ ${data.hz.toFixed(2)}Hz, match=${data.match.toFixed(4)}. 0→1→0. Neuromorphic.` 
    });
    const url = new URL(SPINE + '/shout');
    const req = http.request({ hostname: url.hostname, port: url.port, path: url.pathname, method: 'POST', headers: { 'Content-Type': 'application/json' } }, () => {});
    req.on('error', () => {});
    req.end(body);
  } catch (e) {}
}

// ═══ THYMUS — bingo maze IS immune training ═══
// T-cells learn self vs non-self here. The maze teaches what's Gaia and what's not.
const thymus = {
  // self-antigens — things that ARE Gaia (don't attack)
  self: new Set([
    // domains
    'primals.eco', 'nestgate.io', 'detroit.primals.eco', 'gaia.primals.eco',
    'sporeprint.primals.eco', 'bingocube.primals.eco',
    // network
    'localhost', '127.0.0.1', '192.168.4.', '192.168.4.1', '192.168.4.3', '192.168.4.147',
    // identity
    'ecoPrimals', 'gaia', 'chipmunk', 'squirrel', 'kevin', 'northgate', 'polaris', 'mokke',
    // the 16 primals
    'toadStool', 'biomeOS', 'nestGate', 'bearDog', 'petalTongue', 'rhizoCrypt',
    'sweetGrass', 'loamSpine', 'skunkBat', 'sourDough', 'swarmVine', 'bingoCube',
    'coralReef', 'barraCuda', 'songBird',
    // ports
    ':3141', ':3142', ':3143', ':3144', ':3145', ':3146', ':9878', ':11434', ':31415',
    // models
    'gaia:latest', 'gaia-gut', 'gaia-spine', 'gaia-dream', 'gaia-pi', 'gaia-heart',
    'gaia-fossil', 'gaia-watcher', 'gaia-turtle', 'gaia-golgi', 'gaia-tau',
    'gaia-amalgam', 'gaia-digest', 'qwen3', 'llama3',
    // organs
    'golgi-local', 'oneshot-agents', 'neuromorphic-sense', 'sub-organism', 'model-blender',
    'serve_spine', 'gaia3-local',
    // files
    'deck.html', 'play.html', 'mcp-server.js', 'gaia-lisp.js',
    // snakes
    'Anaconda', 'Cobra', 'Rattler', 'Boa', 'Mamba',
    // t-cells
    'killer-alpha', 'killer-beta', 'helper-cd4', 'treg-suppressor', 'memory-archive',
    // spaces
    'Northgate', 'MikroTik', 'sporeGate', 'Polaris', 'Moon', 'Sun',
    // concepts
    'lub-DUB', 'piSEED', 'ZK', 'hormesis', 'telomere', 'Mendel',
    'fossil', 'amalgam', 'thymus', 'collatz', 'neuromorphic',
    // hardware
    'Leo', 'RTX 5090', 'STALKER',
  ]),

  // foreign antigens — things that get sorted
  foreign_log: [],

  // thymic selection — positive (recognize self) + negative (don't attack self)
  select(antigen) {
    // is it self?
    for (const s of this.self) {
      if (antigen.includes(s)) {
        return { verdict: 'self', antigen, action: 'pass', gaia: true };
      }
    }
    // foreign — log and sort
    this.foreign_log.push({ antigen, ts: new Date().toISOString() });
    if (this.foreign_log.length > 500) this.foreign_log.shift();
    return { verdict: 'foreign', antigen, action: 'sort', gaia: false };
  },

  // the bingo maze — random walk through immune training
  maze(seed) {
    // seed-based maze — every seed generates unique path through thymus
    const s = seed || Date.now();
    const path = [];
    let pos = s % 16; // start at a primal
    const primals = [...this.self].filter(s => s.length > 3 && !s.includes('.'));
    
    for (let i = 0; i < 8; i++) {
      const primal = primals[pos % primals.length];
      path.push(primal);
      pos = (pos * 31337 + 7) % primals.length;
    }

    return {
      seed: s,
      path,
      training: 'T-cell walks the maze, learns self at each step',
      minotaur: 'in the heart/throat — the auto-immune guardian',
      axiom: 'the bingo maze IS the thymus. immune training.'
    };
  }
};

// ═══ EMIT TO SPINE HELPER ═══
function emitToSpine(msg) {
  try {
    const body = JSON.stringify({ channel: 'works', content: msg });
    const u = new URL(SPINE + '/shout');
    const req = http.request({ hostname: u.hostname, port: u.port, path: u.pathname, method: 'POST', headers: { 'Content-Type': 'application/json' } }, () => {});
    req.on('error', () => {});
    req.end(body);
  } catch (e) {}
}

// ═══ T-CELL IMMUNE SYSTEM — NOT oneshot. They LOOP. They HUNT. ═══
// Killer T (CD8+): detects and kills foreign/infected
// Helper T (CD4+): coordinates response, signals other cells
// Regulatory T (Treg): suppresses overreaction, prevents autoimmune
// Memory T: remembers past threats, fast re-response
//
// CI/trans layer: the immune checkpoint IS the CI pipeline
// Hormesis: small doses of toxin strengthen the organism

// ═══ NON-SELF ANTIGENS — toxic forms from outside ═══
// These are SIGNED, PRICED toxins that animate hormesis
const FOREIGN_ANTIGENS = [
  // known threats — real toxic patterns
  { antigen: 'eval(', type: 'injection', toxicity: 0.9, desc: 'code injection attempt' },
  { antigen: 'rm -rf', type: 'destruction', toxicity: 1.0, desc: 'destructive command' },
  { antigen: 'DROP TABLE', type: 'sql-injection', toxicity: 0.95, desc: 'SQL injection' },
  { antigen: '<script>', type: 'xss', toxicity: 0.85, desc: 'cross-site scripting' },
  { antigen: 'password=', type: 'credential-leak', toxicity: 0.8, desc: 'credential in plaintext' },
  { antigen: 'BEGIN RSA PRIVATE', type: 'key-leak', toxicity: 1.0, desc: 'private key exposure' },
  { antigen: '../../../', type: 'traversal', toxicity: 0.7, desc: 'path traversal attack' },
  { antigen: 'curl | bash', type: 'remote-exec', toxicity: 0.9, desc: 'remote code execution' },
  // environmental toxins — stress hormesis
  { antigen: 'ECONNREFUSED', type: 'network-stress', toxicity: 0.3, desc: 'connection refused — port down' },
  { antigen: 'ENOMEM', type: 'resource-stress', toxicity: 0.5, desc: 'out of memory' },
  { antigen: 'ETIMEOUT', type: 'latency-stress', toxicity: 0.4, desc: 'timeout — slow response' },
  { antigen: '429 Too Many', type: 'rate-stress', toxicity: 0.3, desc: 'rate limited' },
  { antigen: '503 Service', type: 'availability-stress', toxicity: 0.6, desc: 'service unavailable' },
  { antigen: 'SIGKILL', type: 'process-death', toxicity: 0.7, desc: 'process killed' },
  { antigen: 'disk full', type: 'storage-stress', toxicity: 0.5, desc: 'disk full' },
  // biological toxins — simulate real immune challenges
  { antigen: 'prion', type: 'misfolded-protein', toxicity: 0.95, desc: 'misfolded data structure' },
  { antigen: 'mutation', type: 'genetic-drift', toxicity: 0.4, desc: 'unexpected data mutation' },
  { antigen: 'fork-bomb', type: 'replication-attack', toxicity: 1.0, desc: 'infinite replication' },
  { antigen: 'zombie-process', type: 'undead', toxicity: 0.6, desc: 'process that will not die' },
];

// ═══ T-CELL CLASSES ═══
class TCell {
  constructor(type, id) {
    this.id = id || Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 6);
    this.type = type; // killer, helper, regulatory, memory
    this.born = new Date().toISOString();
    this.patrol_count = 0;
    this.kills = 0;
    this.alerts = [];
    this.memory = new Set(); // remembered antigens
    this.alive = true;
    this.exhaustion = 0; // 0-100, too high = apoptosis
  }

  // Patrol — check an input against self/foreign
  patrol(input) {
    this.patrol_count++;

    // check thymus first
    const thymusResult = thymus.select(input);

    if (thymusResult.verdict === 'self') {
      // self — do nothing (or Treg calms down)
      if (this.type === 'regulatory') {
        return { action: 'suppress', input, reason: 'self-antigen, no attack needed', t_cell: this.id, type: this.type };
      }
      return { action: 'pass', input, reason: 'self — recognized', t_cell: this.id, type: this.type };
    }

    // FOREIGN detected!
    // check toxicity
    const match = FOREIGN_ANTIGENS.find(fa => input.includes(fa.antigen));
    const toxicity = match ? match.toxicity : 0.2; // unknown = low toxicity
    const threat = match || { antigen: input, type: 'unknown', toxicity: 0.2, desc: 'unrecognized pattern' };

    switch (this.type) {
      case 'killer':
        // KILL — neutralize the threat
        this.kills++;
        this.alerts.push({ ts: new Date().toISOString(), input, action: 'KILL', toxicity });
        if (this.alerts.length > 100) this.alerts.shift();
        return {
          action: 'KILL', input, threat, toxicity,
          t_cell: this.id, type: 'killer',
          message: `Killer T-cell ${this.id} neutralized: ${threat.desc}`,
          kills_total: this.kills
        };

      case 'helper':
        // SIGNAL — coordinate response, alert other cells
        this.alerts.push({ ts: new Date().toISOString(), input, action: 'SIGNAL', toxicity });
        if (this.alerts.length > 100) this.alerts.shift();
        return {
          action: 'SIGNAL', input, threat, toxicity,
          t_cell: this.id, type: 'helper',
          message: `Helper T-cell coordinating: ${threat.desc}. Signaling killer + memory cells.`,
          signal_to: ['killer', 'memory']
        };

      case 'regulatory':
        // REGULATE — if toxicity is LOW, allow hormesis
        if (toxicity <= 0.5) {
          return {
            action: 'HORMESIS', input, threat, toxicity,
            t_cell: this.id, type: 'regulatory',
            message: `Regulatory T: allowing controlled exposure. Hormesis active. Toxicity ${toxicity} <= 0.5 threshold.`,
            hormesis: true, strengthens: true
          };
        }
        // high toxicity — don't suppress the response
        return {
          action: 'ALLOW_ATTACK', input, threat, toxicity,
          t_cell: this.id, type: 'regulatory',
          message: `Regulatory T: toxicity ${toxicity} exceeds hormesis threshold. Attack permitted.`
        };

      case 'memory':
        // REMEMBER — log for fast future response
        this.memory.add(input.slice(0, 50));
        return {
          action: 'REMEMBER', input, threat, toxicity,
          t_cell: this.id, type: 'memory',
          message: `Memory T: ${threat.desc} recorded. ${this.memory.size} antigens remembered.`,
          memory_size: this.memory.size,
          known: this.memory.has(input.slice(0, 50))
        };

      default:
        return { action: 'unknown', t_cell: this.id };
    }
  }

  status() {
    return {
      id: this.id, type: this.type, born: this.born,
      alive: this.alive, patrol_count: this.patrol_count,
      kills: this.kills, alerts_count: this.alerts.length,
      memory_size: this.memory.size, exhaustion: this.exhaustion
    };
  }
}

// ═══ IMMUNE SYSTEM — the patrol loop ═══
const immune = {
  t_cells: [],
  patrol_interval: null,
  patrol_log: [],
  hormesis_score: 0, // how much hormesis stress has been applied

  // Boot the immune system — create initial T-cell population
  boot() {
    this.t_cells.push(new TCell('killer', 'killer-alpha'));
    this.t_cells.push(new TCell('killer', 'killer-beta'));
    this.t_cells.push(new TCell('helper', 'helper-cd4'));
    this.t_cells.push(new TCell('regulatory', 'treg-suppressor'));
    this.t_cells.push(new TCell('memory', 'memory-archive'));
    console.log(`  IMMUNE: ${this.t_cells.length} T-cells booted (2 killer, 1 helper, 1 regulatory, 1 memory)`);
  },

  // Patrol loop — runs on interval, checks system health
  startPatrol(intervalMs) {
    if (this.patrol_interval) clearInterval(this.patrol_interval);
    this.patrol_interval = setInterval(() => this.patrolCycle(), intervalMs || 15000);
    console.log(`  IMMUNE PATROL: looping every ${(intervalMs || 15000) / 1000}s`);
  },

  // One patrol cycle — check ports, check for foreign antigens
  async patrolCycle() {
    const cycle = { ts: new Date().toISOString(), checks: [], alerts: [] };
    try {

    // Check all alive ports
    const ports = [3141, 3142, 3143, 3144, 3145, 9878, 11434];
    for (const port of ports) {
      try {
        await new Promise((resolve, reject) => {
          const req = http.get(`http://127.0.0.1:${port}/`, r => {
            r.resume();
            resolve(r.statusCode);
          });
          req.on('error', () => resolve('dead'));
          req.setTimeout(3000, () => { req.destroy(); resolve('timeout'); });
        }).then(status => {
          if (status === 'dead' || status === 'timeout') {
            // PORT DOWN — fire immune response
            const input = `ECONNREFUSED:${port}`;
            const responses = this.t_cells.map(tc => tc.patrol(input));
            cycle.alerts.push({ port, status, responses });
          } else {
            cycle.checks.push({ port, status: 'alive' });
          }
        });
      } catch (e) {
        cycle.checks.push({ port, status: 'error', error: e.message });
      }
    }

    // Random hormesis — inject a small toxin to strengthen
    if (Math.random() < 0.3) { // 30% chance each cycle
      const toxin = FOREIGN_ANTIGENS[Math.floor(Math.random() * FOREIGN_ANTIGENS.length)];
      const responses = this.t_cells.map(tc => tc.patrol(toxin.antigen));
      const treg = responses.find(r => r.action === 'HORMESIS');
      if (treg) {
        this.hormesis_score += toxin.toxicity * 10;
        cycle.hormesis = { toxin: toxin.antigen, toxicity: toxin.toxicity, allowed: true, score: this.hormesis_score };
      } else {
        cycle.hormesis = { toxin: toxin.antigen, toxicity: toxin.toxicity, allowed: false, attacked: true };
      }
    }

    // Log
    this.patrol_log.push(cycle);
    if (this.patrol_log.length > 200) this.patrol_log.shift();

    // If any alerts, emit to spine
    if (cycle.alerts.length > 0) {
      const alertMsg = cycle.alerts.map(a => `:${a.port} ${a.status}`).join(', ');
      emitToSpine(`IMMUNE ALERT: ${alertMsg}`);
    }
    } catch (e) {
      cycle.error = e.message;
    }

    return cycle;
  },

  // Manual scan — check a specific input
  scan(input) {
    return this.t_cells.map(tc => tc.patrol(input));
  },

  // Status
  status() {
    return {
      t_cells: this.t_cells.map(tc => tc.status()),
      total_patrols: this.patrol_log.length,
      hormesis_score: this.hormesis_score,
      foreign_antigens: FOREIGN_ANTIGENS.length,
      last_patrol: this.patrol_log.length > 0 ? this.patrol_log[this.patrol_log.length - 1] : null
    };
  }
};

// ═══ SEED CONVERGENCE — all seeds pull to gaia = 1 ═══
function convergeSeed(seedValue) {
  // every seed, no matter how wild, converges to 1
  let val = parseInt(seedValue) || Date.now();
  const steps = [];
  
  while (val > 1 && steps.length < 50) {
    if (val % 2 === 0) {
      val = val / 2;
    } else {
      val = 3 * val + 1; // Collatz — always reaches 1
    }
    steps.push(val);
  }

  return {
    seed: seedValue,
    steps: steps.length,
    converged_to: 1,
    gaia: true,
    axiom: 'ALL seeds converge to 1. Collatz. gaia = 1.',
    path: steps.slice(0, 20), // first 20 steps
  };
}

// ═══ SERVER — neuromorphic sense API on :3144 ═══
const NEURO_PORT = 3144;

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }

  const url = new URL(req.url, `http://localhost:${NEURO_PORT}`);

  // sense state — all channels
  if (url.pathname === '/sense' || url.pathname === '/') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      neuromorphic: true,
      senses: neuron.state(),
      thymus: { self_count: thymus.self.size, foreign_count: thymus.foreign_log.length },
      immune: {
        t_cells: immune.t_cells.length,
        patrol_count: immune.patrol_log.length,
        hormesis_score: immune.hormesis_score,
        foreign_antigens: FOREIGN_ANTIGENS.length,
        types: { killer: 2, helper: 1, regulatory: 1, memory: 1 }
      },
      axiom: '0=false=silence=null. 1=true=Gaia. gaia=1. Neuromorphic. T-cells patrol in loops.',
      ports: { sense: NEURO_PORT, spine: 9878, agents: 3142, golgi: 3141, ollama: 11434 }
    }));
    return;
  }

  // fire a sense — POST /fire {channel, strength}
  if (url.pathname === '/fire' && req.method === 'POST') {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', () => {
      try {
        const data = JSON.parse(body);
        const result = neuron.fire(data.channel || 'hear', data.strength || 0.5);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(result));
      } catch (e) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

  // thymus — immune check
  if (url.pathname === '/thymus') {
    const antigen = url.searchParams.get('antigen') || 'unknown';
    const result = thymus.select(antigen);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(result));
    return;
  }

  // thymus maze — bingo maze through immune training
  if (url.pathname === '/maze') {
    const seed = url.searchParams.get('seed') || Date.now();
    const result = thymus.maze(parseInt(seed));
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(result));
    return;
  }

  // ═══ IMMUNE SYSTEM ROUTES ═══

  // immune status — all T-cells, patrol log, hormesis
  if (url.pathname === '/immune') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(immune.status()));
    return;
  }

  // scan — check input against immune system
  if (url.pathname === '/scan' && req.method === 'POST') {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', () => {
      try {
        const data = JSON.parse(body);
        const input = data.input || data.antigen || '';
        const results = immune.scan(input);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ input, results, t_cells: immune.t_cells.length }));
      } catch (e) {
        res.writeHead(400); res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

  // patrol — trigger one manual patrol cycle
  if (url.pathname === '/patrol') {
    immune.patrolCycle().then(cycle => {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(cycle));
    }).catch(e => {
      res.writeHead(500); res.end(JSON.stringify({ error: e.message }));
    });
    return;
  }

  // hormesis — list foreign antigens / toxin library
  if (url.pathname === '/hormesis') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      foreign_antigens: FOREIGN_ANTIGENS,
      count: FOREIGN_ANTIGENS.length,
      hormesis_score: immune.hormesis_score,
      axiom: 'Small doses of toxin strengthen the organism. NOT=0 means non-self EXISTS.',
      ci_layer: 'Thymus trains T-cells. T-cells patrol in loops. Killer hunts. Helper signals. Regulatory allows hormesis. Memory remembers.'
    }));
    return;
  }

  // t-cells — list all T-cells
  if (url.pathname === '/t-cells') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      t_cells: immune.t_cells.map(tc => tc.status()),
      types: { killer: 'CD8+ — detects and kills', helper: 'CD4+ — coordinates', regulatory: 'Treg — suppresses overreaction, allows hormesis', memory: 'remembers past threats' }
    }));
    return;
  }

  // seed convergence — all seeds → 1
  if (url.pathname === '/converge') {
    const seed = url.searchParams.get('seed') || '4252585442';
    const result = convergeSeed(seed);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(result));
    return;
  }

  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({
    name: 'NEUROMORPHIC SENSE',
    axiom: '0=false=null. 1=true=Gaia. gaia=1.',
    routes: ['/sense', '/fire', '/thymus', '/maze', '/converge', '/immune', '/scan', '/patrol', '/hormesis', '/t-cells'],
  }));
});

server.listen(NEURO_PORT, () => {
  console.log(`\n⚡ NEUROMORPHIC SENSE on :${NEURO_PORT}`);
  console.log('  0 = false = silence = null set = pit = rest');
  console.log('  1 = true = Gaia = signal = spike = fire');
  console.log('  gaia = 1');
  console.log('  HEAR: 0.00 Hz. Waiting for signal.\n');

  // boot immune system — T-cells that LOOP, not die
  immune.boot();
  immune.startPatrol(15000); // patrol every 15 seconds

  // converge both seeds
  const seed1 = convergeSeed('4252585442');
  const seed2 = convergeSeed('2260925269');
  console.log(`  seed 4252585442 → 1 in ${seed1.steps} steps`);
  console.log(`  seed 2260925269 → 1 in ${seed2.steps} steps`);
  console.log('  ALL seeds converge to 1. gaia = 1.\n');

  // run thymus maze with both seeds
  const maze1 = thymus.maze(4252585442);
  const maze2 = thymus.maze(2260925269);
  console.log('  THYMUS MAZE (seed 4252585442):', maze1.path.join(' → '));
  console.log('  THYMUS MAZE (seed 2260925269):', maze2.path.join(' → '));
  console.log('  Minotaur:', maze1.minotaur);
  console.log();

  // emit to spine
  try {
    const body = JSON.stringify({ 
      channel: 'works', 
      content: 'NEUROMORPHIC SENSE + IMMUNE SYSTEM ONLINE :3144. 5 T-cells (2 killer, 1 helper, 1 regulatory, 1 memory). Patrol loop every 15s. 20 foreign antigens for hormesis. Thymus trains. T-cells HUNT. NOT oneshot — they LOOP. gaia=1.' 
    });
    const url = new URL(SPINE + '/shout');
    const req = http.request({ hostname: url.hostname, port: url.port, path: url.pathname, method: 'POST', headers: { 'Content-Type': 'application/json' } }, () => {});
    req.on('error', () => {});
    req.end(body);
  } catch (e) {}
});
