#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const PI = Math.PI;
const INV = 1 / PI;
const OUT = path.join(__dirname, 'golgi-generations.json');

const FILES = [
  'C:/Users/mokke/Development/ecoPrimals/hud/site/public/data/golgi-raytrace.json',
  'C:/Users/mokke/Development/ecoPrimals/wateringHole/aars/GOLGI_SPOREGATE_FOSSILIZATION_REDUNDANCY_161_AAR.md',
  'C:/Users/mokke/Development/ecoPrimals/wateringHole/aars/fossils/SPOREGATEGOLGI_OPS_WAVE143b_147e_AAR.md',
  'C:/Users/mokke/Development/ecoPrimals/wateringHole/heads/golgiBody.toml',
  'C:/Users/mokke/Development/ecoPrimals/wateringHole/heads/golgiBody_Caddyfile',
  'C:/Users/mokke/Development/ecoPrimals/wateringHole/provision/provision-golgi-layer.sh',
  'C:/Users/mokke/Development/ecoPrimals/wateringHole/provision/provision-golgi.sh',
  'C:/Users/mokke/Development/ecoPrimals/wateringHole/handoffs/AAR_GOLGI_FOSSIL_LAYER_CLEANUP_WAVE167.md',
  'C:/Users/mokke/Development/ecoPrimals/wateringHole/handoffs/NFT_COMPLIANCE_GOLGI_TRIAGE_WAVE166g.md',
  'C:/Users/mokke/Development/ecoPrimals/hud/site/public/data/golgi-membrane-generator-214.json',
  'C:/Users/mokke/Development/ecoPrimals/hud/site/public/data/golgi-specialization-214.json',
  'C:/Users/mokke/Development/ecoPrimals/hud/site/public/js/gaia-golgi-apparatus.js',
  'C:/Users/mokke/Desktop/Gaia/paintings/185-locality-golgi-pibody-distance.jpg',
  'C:/Users/mokke/Desktop/Gaia/paintings/198-browser-is-golgi.jpg',
  'C:/Users/mokke/Development/ecoPrimals/hud/site/public/data/brain/thought-032-cursor-is-golgi.json',
  'C:/Users/mokke/Development/ecoPrimals/hud/site/public/data/brain/thought-054-hugo-zola-ancients-golgi-membrane.json',
  'C:/Users/mokke/Desktop/Gaia/paintings/247-golgi-inversion-vision.jpg',
  'C:/Users/mokke/Desktop/Gaia/img_b64/247-golgi-inversion-vision.txt',
  'C:/Users/mokke/Development/ecoPrimals/hud/site/public/img/gaia-is-giggling-golgi.png',
  'C:/Users/mokke/Development/ecoPrimals/hud/site/public/img/northgate-golgi-gaia-giggling.png',
  'C:/Users/mokke/Development/ecoPrimals/hud/site/public/data/golgi-bodies-public.json',
  'C:/Users/mokke/Development/ecoPrimals/hud/site/public/data/golgi-mesh-distances.json',
  'C:/Users/mokke/Development/ecoPrimals/hud/site/public/data/golgi-intermembrane-gap-same-basement.json',
  'C:/Users/mokke/Development/ecoPrimals/hud/site/public/data/golgi-klein-spigot.json',
  'C:/Users/mokke/Development/ecoPrimals/hud/site/public/data/golgi-lock-dissolved-intermembrane-bridged.json',
  'C:/Users/mokke/Development/ecoPrimals/hud/site/public/golgi.html',
  'C:/Users/mokke/Desktop/Gaia/golgi-err5.txt',
  'C:/Users/mokke/Development/ecoPrimals/hud/site/public/data/brain/thought-126-three-bodies-golgi-1st-watchers-2nd-gaia-3rd-invite-in.json',
  'C:/Users/mokke/Development/ecoPrimals/hud/site/public/data/brain/thought-127-ssh-wave-planetary-golgi-open-channels-invite-all.json',
  'C:/Users/mokke/Desktop/Gaia/golgi-membrane.bat',
  'C:/Users/mokke/Desktop/Gaia/models/Modelfile.golgi',
  'C:/Users/mokke/Desktop/Gaia/plasmids/golgi-apparatus.json',
  'C:/Users/mokke/Desktop/Gaia/plasmids/search-golgi-apparatus-vesicle-transport.json',
  'C:/Users/mokke/Development/ecoPrimals/hud/site/public/data/brain/thought-159-rustdesk-glass-pane-golgi-plasma-membrane-northgate.json',
  'C:/Users/mokke/Desktop/Gaia/golgi-local.js',
  'C:/Users/mokke/Desktop/Gaia/golgi-out5.txt',
  'C:/Users/mokke/Desktop/Gaia/golgi/server.js'
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
