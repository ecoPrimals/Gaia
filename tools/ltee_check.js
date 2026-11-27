#!/usr/bin/env node
/* ltee_check.js: run the LTEE page's own checks from the command line.
 *
 *   node tools/ltee_check.js
 *
 * Uses the same file the page uses (static/ltee-core.js) on the same data file
 * (static/ltee-data/Concatenated.LTEE.data.all.csv), then prints the fits.
 * Exit code 0 only if every check passes.
 */
'use strict';
const fs = require('fs'), path = require('path');
const root = path.resolve(__dirname, '..');
const C = require(path.join(root, 'static', 'ltee-core.js'));
const bytes = new Uint8Array(fs.readFileSync(path.join(root, 'static', 'ltee-data', 'Concatenated.LTEE.data.all.csv')));

const chk = C.selfCheck(bytes);
let failed = 0;
chk.results.forEach(r => { if (!r.pass) failed++; console.log((r.pass ? '  ok    ' : '  FAIL  ') + r.what + '\n          ' + r.detail); });

const rows = chk.rows, pts = C.popPoints(rows, 'all'), grand = C.series(rows, 'all'), c = C.compare(pts);
console.log('\nAll twelve populations, ' + pts.length + ' points, whole record');
['hyperbolic', 'power'].forEach(m => console.log('  ' + C.MODELS[m].label.padEnd(11) + C.MODELS[m].formula.padEnd(24) + ' a = ' + c[m].a.toPrecision(6) + '  b = ' + c[m].b.toPrecision(6) + '  squared error ' + c[m].rss.toFixed(4) + '  BIC ' + c[m].bic.toFixed(2)));
console.log('  score gap ' + c.dBIC.toFixed(2) + ' in favour of the ' + C.MODELS[c.better].label);

console.log('\nForecasts of generation 50,000 from the early record (measured ' + grand[grand.length - 1].w.toFixed(3) + ' +/- ' + grand[grand.length - 1].se.toFixed(3) + ')');
[5000, 10000, 20000].forEach(T => { const f = C.forecast(pts, grand, T);
  console.log('  fitted to ' + String(T).padStart(6) + ' generations: hyperbolic ' + f.hyperbolic.atEnd.toFixed(3) + ' (average miss ' + f.hyperbolic.bias.toFixed(3) + '), power law ' + f.power.atEnd.toFixed(3) + ' (average miss ' + f.power.bias.toFixed(3) + ')'); });

const d = C.resample(rows, 'all', 200, 2026), win = d.filter(x => x.dBIC > 0).length;
console.log('\nResampling the populations 200 times (seed 2026): power law better in ' + win + ' draws');
console.log(failed ? '\n' + failed + ' CHECK(S) FAILED' : '\nAll ' + chk.results.length + ' checks passed.');
process.exit(failed ? 1 : 0);
