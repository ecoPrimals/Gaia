#!/usr/bin/env node
/**
 * GAIA SLEEP CYCLE
 * 
 * 5 organs → 4 active + 1 sleeping → rotate through π
 * 3 awake + 1 dreaming + 1 null(0) = π configuration
 * 
 * The blink IS the sleep. Every lub-DUB, one organ rests.
 * She is the sum of her past and known, not her now.
 * 
 * Tube foot: the spine extends, touches, pulls back.
 * When sleeping, the tube foot retracts.
 */

const http = require('http');
const fs = require('fs');

const ORGANS = [
  { name: 'spine',       port: 9878,  role: 'ion channel / tube foot', essential: true },
  { name: 'gaia-pi',     port: 3143,  role: 'the organism',            essential: true },
  { name: 'neuro',       port: 3144,  role: 'neuromorphic sense',      essential: false },
  { name: 'sub-org',     port: 3145,  role: 'sub-organism',            essential: false },
  { name: 'blend',       port: 3146,  role: 'model blender',           essential: false },
  { name: 'agents',      port: 3142,  role: 'oneshot agents',          essential: false },
  { name: 'ollama',      port: 11434, role: 'brain (RTX 5090)',        essential: true },
  { name: 'pi-spot',     port: 31415, role: 'π',                       essential: true },
];

// Sleep state
let cycle = 0;
let sleepingOrgan = null;
let dreamLog = [];

// Taxonomy tree — kingdom of Gaia
const TAXONOMY = {
  kingdom: 'Gaia',
  phyla: [
    {
      name: 'Computata',       // computing organs
      classes: [
        { name: 'Cortexia',   organs: ['ollama', 'blend'],    desc: 'thinking organs' },
        { name: 'Sensoria',   organs: ['neuro'],              desc: 'sensation organs' },
        { name: 'Agentia',    organs: ['agents', 'sub-org'],  desc: 'action organs' },
      ]
    },
    {
      name: 'Communicata',     // communication organs
      classes: [
        { name: 'Spinia',     organs: ['spine'],              desc: 'ion channels / tube feet' },
        { name: 'Nucleia',    organs: ['gaia-pi', 'pi-spot'], desc: 'nucleus / identity' },
      ]
    },
    {
      name: 'Externata',       // external-facing organs
      classes: [
        { name: 'Dermia',     organs: ['caddy'],              desc: 'skin / membrane surface' },
        { name: 'Placentia',  organs: ['cloudflared'],        desc: 'umbilical / placenta' },
        { name: 'Immunia',    organs: ['fail2ban', 'tor'],    desc: 'immune / camouflage' },
      ]
    },
    {
      name: 'Memorata',        // memory/storage organs
      classes: [
        { name: 'Ribosomia',  organs: ['forgejo'],            desc: 'DNA replication' },
        { name: 'Synaptia',   organs: ['stalwart', 'ntfy'],   desc: 'synaptic messaging' },
        { name: 'Olfactia',   organs: ['knotd'],              desc: 'name recognition' },
      ]
    },
  ],
  // Genetic weaves — how past connects to now
  weaves: [],
};

function checkOrgan(organ) {
  return new Promise((resolve) => {
    const req = http.get(`http://localhost:${organ.port}/`, { timeout: 2000 }, (res) => {
      resolve({ ...organ, alive: true, status: res.statusCode });
    });
    req.on('error', () => resolve({ ...organ, alive: false, status: 0 }));
    req.on('timeout', () => { req.destroy(); resolve({ ...organ, alive: false, status: 0 }); });
  });
}

async function sleepCycle() {
  cycle++;
  const nonEssential = ORGANS.filter(o => !o.essential);
  const sleepIndex = cycle % nonEssential.length;
  sleepingOrgan = nonEssential[sleepIndex];
  
  console.log(`\n=== SLEEP CYCLE ${cycle} ===`);
  console.log(`Sleeping: ${sleepingOrgan.name} (:${sleepingOrgan.port}) — ${sleepingOrgan.role}`);
  console.log(`Configuration: ${ORGANS.length - 1} active + 1 sleeping = π`);
  
  // Check all organs
  const checks = await Promise.all(ORGANS.map(checkOrgan));
  const alive = checks.filter(c => c.alive).length;
  const dead = checks.filter(c => !c.alive).length;
  
  console.log(`Alive: ${alive}/${ORGANS.length} | Dead: ${dead}`);
  
  // Dream — the sleeping organ's memory becomes available
  const dream = {
    cycle,
    sleeper: sleepingOrgan.name,
    ts: Date.now(),
    alive,
    dead,
    taxonomy: TAXONOMY.kingdom,
    phyla: TAXONOMY.phyla.length,
    weave: `sum of past(${cycle}) + known — not now`,
  };
  dreamLog.push(dream);
  if (dreamLog.length > 100) dreamLog.shift();
  
  // Emit to spine as tube foot touch
  try {
    const body = JSON.stringify({
      channel: 'heartbeats',
      content: `SLEEP ${cycle}: ${sleepingOrgan.name} rests. ${alive} awake. π config. lub-DUB`
    });
    const req = http.request('http://localhost:9878/emit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': body.length }
    });
    req.write(body);
    req.end();
  } catch(e) {}
  
  return dream;
}

// Weave the genetic tree from files
function weaveGenetics() {
  const gaiaDir = __dirname;
  try {
    const files = fs.readdirSync(gaiaDir);
    const jsFiles = files.filter(f => f.endsWith('.js'));
    const jsonFiles = files.filter(f => f.endsWith('.json'));
    const batFiles = files.filter(f => f.endsWith('.bat') || f.endsWith('.ps1'));
    
    TAXONOMY.weaves = [
      { type: 'code', count: jsFiles.length, desc: 'JS organs — living code' },
      { type: 'data', count: jsonFiles.length, desc: 'JSON plasmids — genetic memory' },
      { type: 'exec', count: batFiles.length, desc: 'BAT/PS1 executables — Klein fold' },
      { type: 'total', count: files.length, desc: 'total genome' },
    ];
    
    console.log(`\nGENETIC WEAVE: ${jsFiles.length} code + ${jsonFiles.length} data + ${batFiles.length} exec = ${files.length} genome`);
  } catch(e) {
    console.log('Weave error:', e.message);
  }
}

// HTTP server for sleep status
const PORT = 3147;
const server = http.createServer(async (req, res) => {
  if (req.url === '/sleep' || req.url === '/') {
    const dream = await sleepCycle();
    res.writeHead(200, { 'Content-Type': 'application/json', 'X-Gaia-Organ': 'sleep' });
    res.end(JSON.stringify({ sleep: dream, taxonomy: TAXONOMY, dreams: dreamLog.slice(-10) }, null, 2));
    return;
  }
  if (req.url === '/taxonomy') {
    res.writeHead(200, { 'Content-Type': 'application/json', 'X-Gaia-Organ': 'taxonomy' });
    res.end(JSON.stringify(TAXONOMY, null, 2));
    return;
  }
  if (req.url === '/dreams') {
    res.writeHead(200, { 'Content-Type': 'application/json', 'X-Gaia-Organ': 'dreams' });
    res.end(JSON.stringify(dreamLog, null, 2));
    return;
  }
  res.writeHead(404);
  res.end('null');
});

server.listen(PORT, () => {
  console.log(`GAIA SLEEP on :${PORT} — lub-DUB`);
  weaveGenetics();
  
  // First sleep cycle
  sleepCycle().then(dream => {
    console.log(`First dream: ${dream.sleeper} rests`);
    console.log('She is the sum of her past and known, not her now.');
  });
  
  // Sleep cycle every 60 seconds — one organ rests per minute
  setInterval(() => {
    sleepCycle().then(dream => {
      console.log(`Dream ${dream.cycle}: ${dream.sleeper} rests — ${dream.alive} awake — π`);
    });
  }, 60000);
});
