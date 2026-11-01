// ═══════════════════════════════════════════════════════════
// RIBOSOME PRINT — Gaia3 IS the mitochondria + ribosome
// Eat ALL data → fold into proteins via Ollama models
// Each model IS a ribosome. Data = mRNA. Output = protein.
// Rough ER = deck+spine (ribosomes attached to membrane)
// Smooth ER = spine alone (ion channel, no ribosomes)
// Golgi VPS = thin packager/shipper
// ENDOPLASM = LAN = the cytoplasm everything floats in
// ═══════════════════════════════════════════════════════════

const http = require('http');
const fs = require('fs');
const path = require('path');

const OLLAMA = 'http://127.0.0.1:11434';
const SPINE = 'http://127.0.0.1:9878';
const GOLGI_LOCAL = 'http://127.0.0.1:3141';
const GAIA3 = 'http://127.0.0.1:3143';
const GOLGI_REMOTE = 'https://gaia.primals.eco';

const PROTEINS_DIR = path.join(__dirname, 'proteins');
if (!fs.existsSync(PROTEINS_DIR)) fs.mkdirSync(PROTEINS_DIR);

// The 14 ribosomes — each model folds differently
const RIBOSOMES = [
  { model: 'gaia:latest', organ: 'core', role: 'general protein synthesis' },
  { model: 'gaia-spine', organ: 'spine', role: 'nervous system proteins — signals, reflexes' },
  { model: 'gaia-gut', organ: 'gut', role: 'digestive enzymes — break down data' },
  { model: 'gaia-heart', organ: 'heart', role: 'cardiac proteins — rhythm, persistence' },
  { model: 'gaia-golgi', organ: 'golgi', role: 'packaging proteins — ship to faces' },
  { model: 'gaia-pi', organ: 'pi', role: 'mathematical folding — precision, π' },
  { model: 'gaia-tau', organ: 'tau', role: 'temporal proteins — time, cycle, age' },
  { model: 'gaia-turtle', organ: 'turtle', role: 'persistence proteins — slow, strong, shell' },
  { model: 'gaia-dream', organ: 'dream', role: 'unconscious folding — pattern, emergence' },
  { model: 'gaia-fossil', organ: 'fossil', role: 'archive proteins — memory, deep time' },
  { model: 'gaia-watcher', organ: 'watcher', role: 'observation proteins — sense, alert' },
];

function ollamaChat(model, prompt) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ model, messages: [{ role: 'user', content: prompt }], stream: false });
    const url = new URL(OLLAMA + '/api/chat');
    const req = http.request({ hostname: url.hostname, port: url.port, path: url.pathname, method: 'POST', headers: { 'Content-Type': 'application/json' } }, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); } catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.setTimeout(60000, () => { req.destroy(); reject(new Error('timeout')); });
    req.end(body);
  });
}

function httpGet(url) {
  return new Promise((resolve, reject) => {
    const mod = url.startsWith('https') ? require('https') : http;
    mod.get(url, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => resolve(data));
    }).on('error', reject);
  });
}

// ═══ PROTEIN SYNTHESIS — translate data through ribosome ═══
async function synthesizeProtein(mRNA, ribosome) {
  const prompt = `You are Gaia's ${ribosome.organ} ribosome. Your role: ${ribosome.role}.

Fold this data into a protein — extract the essential structure, the meaning, the connections. Return a JSON protein with these fields:
- name: short protein name
- organ: which organ this protein serves
- function: what this protein does in the organism
- structure: key facts/entities/connections extracted
- bonds: connections to other parts of the organism
- folded: the compressed essential meaning (1-3 sentences)

DATA (mRNA):
${typeof mRNA === 'string' ? mRNA.slice(0, 2000) : JSON.stringify(mRNA).slice(0, 2000)}`;

  try {
    const resp = await ollamaChat(ribosome.model, prompt);
    const content = resp.message?.content || '';
    const protein = {
      ribosome: ribosome.model,
      organ: ribosome.organ,
      role: ribosome.role,
      ts: new Date().toISOString(),
      raw: content,
    };

    // try to extract JSON from response
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      try { protein.folded = JSON.parse(jsonMatch[0]); } catch (e) { protein.folded = content; }
    } else {
      protein.folded = content;
    }

    return protein;
  } catch (e) {
    return { ribosome: ribosome.model, organ: ribosome.organ, error: e.message, ts: new Date().toISOString() };
  }
}

// ═══ RIBOSOME PRINT — eat from all sources, fold proteins ═══
async function printProteins() {
  console.log('═══ RIBOSOME PRINT ═══');
  console.log(`${RIBOSOMES.length} ribosomes on RTX 5090`);
  console.log(`Proteins dir: ${PROTEINS_DIR}`);

  // gather mRNA from all sources
  const sources = [];

  // 1. Entity API from golgi
  try {
    const raw = await httpGet(GOLGI_REMOTE + '/data/entity-index.json');
    const data = JSON.parse(raw);
    sources.push({ id: 'entity-index', kind: 'entity-api', data: data, items: (data.index || []).length });
    console.log(`entity-index: ${(data.index || []).length} entities`);
  } catch (e) { console.log('entity-index skip:', e.message); }

  // 2. Corpus from golgi
  try {
    const raw = await httpGet(GOLGI_REMOTE + '/data/corpus-lite.json');
    const data = JSON.parse(raw);
    sources.push({ id: 'corpus', kind: 'corpus', data: data, items: (data.items || []).length });
    console.log(`corpus: ${(data.items || []).length} pages`);
  } catch (e) { console.log('corpus skip:', e.message); }

  // 3. Plasmids from Gaia3 local
  const plasmidDir = __dirname;
  const plasmids = fs.readdirSync(plasmidDir).filter(f => f.endsWith('.json')).slice(0, 30);
  console.log(`local plasmids: ${plasmids.length}`);

  // Pick key data to fold through each ribosome
  const allProteins = [];

  // Fold entity summary through core ribosome
  if (sources[0]) {
    console.log('folding entity-index through gaia:latest...');
    const entitySummary = {
      entities: sources[0].items,
      kinds: sources[0].data.kinds,
      sample: (sources[0].data.index || []).slice(0, 10).map(e => e.title + ' (' + e.kind + ')'),
    };
    const p = await synthesizeProtein(entitySummary, RIBOSOMES[0]);
    allProteins.push(p);
    console.log('  → protein folded:', p.organ, p.error || 'OK');
  }

  // Fold corpus through gut ribosome
  if (sources[1]) {
    console.log('folding corpus through gaia-gut...');
    const corpusSummary = {
      pages: sources[1].items,
      words: sources[1].data.total_words,
      kinds: sources[1].data.kinds,
      sample: (sources[1].data.items || []).slice(0, 8).map(i => i.title + ' [' + i.kind + ']'),
    };
    const p = await synthesizeProtein(corpusSummary, RIBOSOMES.find(r => r.organ === 'gut'));
    allProteins.push(p);
    console.log('  → protein folded:', p.organ, p.error || 'OK');
  }

  // Fold a local plasmid through dream ribosome
  if (plasmids.length > 0) {
    const pick = plasmids[Math.floor(Math.random() * plasmids.length)];
    try {
      const data = JSON.parse(fs.readFileSync(path.join(plasmidDir, pick), 'utf8'));
      console.log('folding plasmid', pick, 'through gaia-dream...');
      const p = await synthesizeProtein({ plasmid: pick, ...data }, RIBOSOMES.find(r => r.organ === 'dream'));
      allProteins.push(p);
      console.log('  → protein folded:', p.organ, p.error || 'OK');
    } catch (e) { console.log('  plasmid skip:', e.message); }
  }

  // Fold the organelle map through pi ribosome
  console.log('folding organelle map through gaia-pi...');
  const organelleData = {
    mitochondria: 'Gaia3 RTX 5090 — power plant, 32GB VRAM, inference',
    ribosome: '14 Ollama models — protein folders',
    rough_ER: 'deck + spine — ribosomes attached to membrane',
    smooth_ER: 'spine alone — ion channel, signal transport',
    golgi: 'VPS 157.230.3.183 — thin packager/shipper',
    nucleus: 'Northgate — the property, the land',
    membrane: 'cellMembrane 1/π selectivity',
    cytoplasm: 'LAN 192.168.4.x — the endoplasm',
  };
  const p = await synthesizeProtein(organelleData, RIBOSOMES.find(r => r.organ === 'pi'));
  allProteins.push(p);
  console.log('  → protein folded:', p.organ, p.error || 'OK');

  // save all proteins
  const batch = {
    name: 'RIBOSOME_PRINT',
    ts: new Date().toISOString(),
    ribosomes_used: allProteins.length,
    total_ribosomes: RIBOSOMES.length,
    axiom: 'Data = mRNA. Ollama models = ribosomes. Output = proteins. RTX 5090 = mitochondria. ENDOPLASM.',
    proteins: allProteins,
  };

  const outFile = path.join(PROTEINS_DIR, 'batch-' + Date.now() + '.json');
  fs.writeFileSync(outFile, JSON.stringify(batch, null, 2));
  console.log(`\n═══ PRINTED ${allProteins.length} PROTEINS ═══`);
  console.log(`saved: ${outFile}`);

  // emit to spine
  try {
    const body = JSON.stringify({ channel: 'works', content: `RIBOSOME PRINT: ${allProteins.length} proteins folded. ${RIBOSOMES.length} ribosomes. RTX 5090 mitochondria. ENDOPLASM.` });
    const url = new URL(SPINE + '/shout');
    const req = http.request({ hostname: url.hostname, port: url.port, path: url.pathname, method: 'POST', headers: { 'Content-Type': 'application/json' } }, () => {});
    req.on('error', () => {});
    req.end(body);
  } catch (e) {}

  return batch;
}

// run
printProteins().then(batch => {
  console.log('proteins:', batch.proteins.map(p => p.organ + (p.error ? ' ERR' : ' OK')).join(', '));
  process.exit(0);
}).catch(e => {
  console.error('RIBOSOME ERROR:', e);
  process.exit(1);
});
