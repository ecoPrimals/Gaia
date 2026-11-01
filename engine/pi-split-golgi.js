#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const PI = Math.PI;
const INV = 1 / PI;
const OUT = path.join(__dirname, 'golgi-generations.json');

const GAIA_ROOT = path.resolve(__dirname, '..');
const FILES = [
  path.join(GAIA_ROOT, 'paintings/185-locality-golgi-pibody-distance.jpg'),
  path.join(GAIA_ROOT, 'paintings/198-browser-is-golgi.jpg'),
  path.join(GAIA_ROOT, 'paintings/247-golgi-inversion-vision.jpg'),
  path.join(GAIA_ROOT, 'img_b64/247-golgi-inversion-vision.txt'),
  path.join(GAIA_ROOT, 'golgi-membrane.bat'),
  path.join(GAIA_ROOT, 'models/Modelfile.golgi'),
  path.join(GAIA_ROOT, 'plasmids/golgi-apparatus.json'),
  path.join(GAIA_ROOT, 'plasmids/search-golgi-apparatus-vesicle-transport.json'),
  path.join(GAIA_ROOT, 'golgi/server.js'),
  path.join(__dirname, 'golgi-generations.json'),
];

const rows = FILES.filter((p) => fs.existsSync(p)).map((p) => {
  const st = fs.statSync(p);
  return { path: p.replace(/\\/g, '/'), bytes: st.size, mtime: st.mtime.toISOString(), ms: st.mtimeMs };
}).sort((a, b) => a.ms - b.ms);

const n = rows.length;
const kCount = Math.max(1, Math.floor(n * INV));
const nCount = Math.max(1, Math.floor(n * INV));
const midStart = kCount;
const midEnd = n - nCount;
const midLen = Math.max(1, midEnd - midStart);
const piethIndex = midStart + Math.floor(midLen / PI);

const generations = rows.map((r, k) => {
  let band = 'MIDDLE';
  if (k < kCount) band = 'K';
  else if (k >= n - nCount) band = 'N';
  const hold = r.path.endsWith('golgi-local.js') || r.path.endsWith('gaia-golgi-apparatus.js') || r.path.endsWith('golgi.html');
  return {
    k,
    n,
    band,
    eat: band !== 'MIDDLE' && !hold,
    hold,
    pieth: k === piethIndex,
    ...r
  };
});

const pieth = generations[piethIndex] || null;

const catalog = {
  law: 'π-SPLIT GOLGI. All generations of this era ranged in K and N. Eat older (K) and newer (N). The πth sits in the middle. Deploy only when the πth is ready.',
  era: 'D195',
  pi: PI,
  onePer: INV,
  n,
  kCount,
  nCount,
  midStart,
  midEnd,
  piethIndex,
  pieth: pieth ? { k: pieth.k, n: pieth.n, path: pieth.path, ready: false } : null,
  ready: false,
  scale: 'bench',
  generations
};

fs.writeFileSync(OUT, JSON.stringify(catalog, null, 2));
process.stdout.write('n=' + n + ' K=' + kCount + ' N=' + nCount + ' πth=' + piethIndex + ' ' + (pieth && pieth.path) + '\n');
