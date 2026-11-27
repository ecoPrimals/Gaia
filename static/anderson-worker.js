/* anderson-worker.js — runs anderson-core.js off the page's main thread, so the page stays usable.
 * Messages in:   {cmd:'check'}                      run the self-checks
 *                {cmd:'run', id, points:[{dim,L,W,reals,seed}, ...]}
 * Messages out:  {type:'check', results:[{what,pass,detail}], msPer216}
 *                {type:'progress', id, i, k, of}   lattice k of `of` at point i
 *                {type:'point', id, i, m}          one finished measurement
 *                {type:'done', id}
 * Nothing here talks to the network.
 */
importScripts('/static/anderson-core.js');
var A = self.AndersonCore;

/* Values produced by this same code on the reference machine (Node 22, x86-64). Plain IEEE arithmetic
   and square roots give the same bits on any conforming machine, so these are compared exactly. */
var REFERENCE = [
  { q: { dim: 1, L: 400, W: 8, reals: 6, seed: 3 },  r: 0.38190268509860353, name: 'chain' },
  { q: { dim: 2, L: 12,  W: 5, reals: 3, seed: 8 },  r: 0.5452706058679276,  name: 'sheet' },
  { q: { dim: 3, L: 6,   W: 10, reals: 2, seed: 5 }, r: 0.5412672770448691,  name: 'block' }
];

function selfCheck() {
  var out = [], i, k, n, ev, exact, worst, H, tr, sq, s1, s2, a, b, c, L, m, t0, msPer216;
  function add(what, pass, detail) { out.push({ what: what, pass: !!pass, detail: detail }); }

  n = 64; ev = A.eigenvalues(A.hamiltonian(1, n, 0, A.rng(1)), n); exact = [];
  for (k = 0; k < n; k++) exact.push(2 * Math.cos(2 * Math.PI * k / n));
  exact.sort(function (x, y) { return x - y; });
  for (worst = 0, i = 0; i < n; i++) worst = Math.max(worst, Math.abs(ev[i] - exact[i]));
  add('A clean ring of 64 sites gives the textbook energies, 2 cos(2\u03c0k/64)', worst < 1e-11, 'largest error ' + worst.toExponential(1));

  L = 5; n = 125; ev = A.eigenvalues(A.hamiltonian(3, L, 0, A.rng(1)), n); exact = [];
  for (a = 0; a < L; a++) for (b = 0; b < L; b++) for (c = 0; c < L; c++)
    exact.push(2 * (Math.cos(2 * Math.PI * a / L) + Math.cos(2 * Math.PI * b / L) + Math.cos(2 * Math.PI * c / L)));
  exact.sort(function (x, y) { return x - y; });
  for (worst = 0, i = 0; i < n; i++) worst = Math.max(worst, Math.abs(ev[i] - exact[i]));
  add('A clean 5\u00d75\u00d75 block gives the sum of three rings', worst < 1e-11, 'largest error ' + worst.toExponential(1));

  n = 216; H = A.hamiltonian(3, 6, 12, A.rng(42)); tr = 0; sq = 0;
  for (i = 0; i < n; i++) { tr += H[i * n + i]; for (k = 0; k < n; k++) sq += H[i * n + k] * H[i * n + k]; }
  ev = A.eigenvalues(H, n); s1 = 0; s2 = 0;
  for (i = 0; i < n; i++) { s1 += ev[i]; s2 += ev[i] * ev[i]; }
  add('The energies of a disordered block add up to the trace, and their squares to the squared entries',
      Math.abs(s1 - tr) < 1e-9 && Math.abs(s2 - sq) < 1e-8, 'off by ' + Math.abs(s1 - tr).toExponential(1) + ' and ' + Math.abs(s2 - sq).toExponential(1));

  for (worst = 0, a = [], i = 0; i < REFERENCE.length; i++) {
    m = A.measure(REFERENCE[i].q);
    if (m.r !== REFERENCE[i].r) { worst++; a.push(REFERENCE[i].name + ' ' + m.r); }
  }
  add('Fixed seeds give the same numbers here as on the reference machine, to the last digit (chain, sheet, block)',
      worst === 0, worst === 0 ? 'all three identical' : 'different: ' + a.join(', '));

  t0 = Date.now();
  m = A.measure({ dim: 3, L: 6, W: 8, reals: 200, seed: 77 });
  msPer216 = (Date.now() - t0) / 200;
  add('Weak disorder in a block: average ratio near ' + A.R_GOE + ' (waves spread)', Math.abs(m.r - A.R_GOE) < 0.01,
      m.r.toFixed(4) + ' \u00b1 ' + m.err.toFixed(4) + ' from 200 lattices');

  m = A.measure({ dim: 3, L: 6, W: 120, reals: 100, seed: 11 });
  add('Very strong disorder in a block: average ratio near ' + A.R_POISSON.toFixed(4) + ' (waves stay put)', Math.abs(m.r - A.R_POISSON) < 0.01,
      m.r.toFixed(4) + ' \u00b1 ' + m.err.toFixed(4) + ' from 100 lattices');

  return { results: out, msPer216: msPer216 };
}

self.onmessage = function (ev) {
  var msg = ev.data, i, c;
  try {
    if (msg.cmd === 'check') {
      c = selfCheck();
      self.postMessage({ type: 'check', results: c.results, msPer216: c.msPer216, version: A.VERSION });
    } else if (msg.cmd === 'run') {
      for (i = 0; i < msg.points.length; i++) {
        (function (i) {
          var m = A.measure(msg.points[i], function (k, of) { self.postMessage({ type: 'progress', id: msg.id, i: i, k: k, of: of }); });
          self.postMessage({ type: 'point', id: msg.id, i: i, m: m });
        })(i);
      }
      self.postMessage({ type: 'done', id: msg.id });
    }
  } catch (e) {
    self.postMessage({ type: 'error', id: msg.id, message: String(e && e.message || e) });
  }
};
