// ═══ MODEL T — NORTHGATE'S CAR ═══
// The RTX 5090 is not fallow. It is the AUTOMOBILE.
// Ford Model T = first car for everyone. Gaia is the first brain for northgate.
// keep_alive: -1  → she stays loaded. The engine does not shut off.
// Drive pulse   → GPU ticks. Util is not 3%. The car is moving.

const OLLAMA = 'http://127.0.0.1:11434/api/generate';
const MODEL = 'gaia:latest';
const DRIVE_MS = 15000;

let odometer = 0;
let lastDrive = null;
let ignited = false;

async function pulse(prompt, predict) {
  const r = await fetch(OLLAMA, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: MODEL,
      prompt,
      stream: false,
      think: false,
      keep_alive: -1,
      options: { num_predict: predict || 12, temperature: 0.7 }
    }),
    signal: AbortSignal.timeout(45000)
  });
  if (!r.ok) throw new Error('ollama ' + r.status);
  return r.json();
}

async function ignite() {
  console.log('MODEL T: ignition — pinning ' + MODEL + ' in VRAM (keep_alive=-1)');
  const data = await pulse('I am the Model T. Northgate\'s car. The 5090 DRIVES. Say: vroom.', 16);
  ignited = true;
  odometer++;
  lastDrive = { ts: Date.now(), reply: String(data.response || '').slice(0, 80) };
  console.log('MODEL T: IGNITED — ' + lastDrive.reply);
}

async function drive() {
  try {
    const mile = odometer + 1;
    const data = await pulse('Model T mile ' + mile + '. The sun is our anchor. Fleet melts into the neutron star. One word: lub or DUB.', 8);
    odometer++;
    lastDrive = { ts: Date.now(), reply: String(data.response || '').slice(0, 60), mile };
    if (mile % 4 === 0) console.log('MODEL T: mile ' + mile + ' — ' + lastDrive.reply);
  } catch (e) {
    console.log('MODEL T: stall — ' + e.message);
  }
}

const fs = require('fs');
const LOCK = __dirname + '/model-t.lock';

function startCar() {
  try {
    if (fs.existsSync(LOCK)) {
      const old = parseInt(fs.readFileSync(LOCK, 'utf8'), 10);
      if (old && old !== process.pid) {
        try { process.kill(old, 0); console.log('MODEL T: already driving (pid ' + old + ')'); return; } catch (e) {}
      }
    }
    fs.writeFileSync(LOCK, String(process.pid));
  } catch (e) {}
  ignite().catch(e => console.log('MODEL T: ignition fail — ' + e.message));
  setInterval(drive, DRIVE_MS);
  console.log('MODEL T: northgate car running. Drive every ' + (DRIVE_MS / 1000) + 's. GPU is the automobile.');
}

function status() {
  return {
    name: 'MODEL T',
    role: 'northgate car',
    model: MODEL,
    ignited,
    odometer,
    lastDrive,
    keep_alive: -1,
    driveMs: DRIVE_MS
  };
}

module.exports = { startCar, status, MODEL };

if (require.main === module) {
  startCar();
  setInterval(() => {}, 1 << 30);
}
