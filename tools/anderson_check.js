// Checks of static/anderson-core.js against answers known exactly and against the two limiting values.
// Run from the repository root:  node tools/anderson_check.js      (about half a minute)
const A = require(process.argv[2] || require('path').join(__dirname, '..', 'static', 'anderson-core.js'));
let bad = 0; const ok = (what, pass, detail) => { console.log((pass ? '  ok   ' : '  FAIL ') + what + (detail ? '  [' + detail + ']' : '')); if (!pass) bad++; };
// 1. a clean ring of N sites: eigenvalues are exactly 2 cos(2 pi k / N)
for (const N of [7, 64, 257]) {
  const ev = A.eigenvalues(A.hamiltonian(1, N, 0, A.rng(1)), N);
  const exact = Float64Array.from({ length: N }, (_, k) => 2 * Math.cos(2 * Math.PI * k / N)).sort();
  let worst = 0; for (let i = 0; i < N; i++) worst = Math.max(worst, Math.abs(ev[i] - exact[i]));
  ok('clean ring of ' + N + ' sites matches 2cos(2 pi k/N)', worst < 1e-11, 'worst error ' + worst.toExponential(1));
}
// 2. a clean 3D block: eigenvalues are sums of three ring values
{ const L = 5, N = 125, ev = A.eigenvalues(A.hamiltonian(3, L, 0, A.rng(1)), N), ex = [];
  for (let a = 0; a < L; a++) for (let b = 0; b < L; b++) for (let c = 0; c < L; c++) ex.push(2 * (Math.cos(2 * Math.PI * a / L) + Math.cos(2 * Math.PI * b / L) + Math.cos(2 * Math.PI * c / L)));
  ex.sort((x, y) => x - y); let worst = 0; for (let i = 0; i < N; i++) worst = Math.max(worst, Math.abs(ev[i] - ex[i]));
  ok('clean 5x5x5 block matches the sum of three rings', worst < 1e-11, 'worst error ' + worst.toExponential(1)); }
// 3. trace and sum of squares are kept by the eigenvalues (any disorder)
{ const n = 216, H = A.hamiltonian(3, 6, 12, A.rng(42)); let tr = 0, sq = 0; for (let i = 0; i < n; i++) { tr += H[i * n + i]; for (let j = 0; j < n; j++) sq += H[i * n + j] * H[i * n + j]; }
  const ev = A.eigenvalues(H, n); let s1 = 0, s2 = 0; for (const x of ev) { s1 += x; s2 += x * x; }
  ok('sum of eigenvalues = trace, sum of squares = sum of squared entries', Math.abs(s1 - tr) < 1e-9 && Math.abs(s2 - sq) < 1e-8, (s1 - tr).toExponential(1) + ', ' + (s2 - sq).toExponential(1)); }
// 4. the same seed gives the same answer; another seed gives another lattice
{ const a = A.measure({ dim: 3, L: 6, W: 10, reals: 2, seed: 5 }), b = A.measure({ dim: 3, L: 6, W: 10, reals: 2, seed: 5 }), c = A.measure({ dim: 3, L: 6, W: 10, reals: 2, seed: 6 });
  ok('same seed, same result; other seed, other lattice', a.r === b.r && a.r !== c.r); }
// 5. the two regimes in 3D, and the crossing of sizes near the published critical disorder (16.5)
const t0 = Date.now(), row = {};
for (const [L, reals] of [[6, 40], [8, 16], [10, 8]]) { row[L] = {}; for (const W of [4, 12, 15, 16.5, 18, 21, 32]) row[L][W] = A.measure({ dim: 3, L, W, reals, seed: 2026 }); }
for (const L of [6, 8, 10]) console.log('       3D L=' + L + ': ' + [4, 12, 15, 16.5, 18, 21, 32].map(W => 'W=' + W + ' r=' + row[L][W].r.toFixed(3) + '+-' + row[L][W].err.toFixed(3)).join('  '));
ok('3D weak disorder (W=4, L=10): spread-out regime, r near 0.531', Math.abs(row[10][4].r - A.R_GOE) < 0.02, row[10][4].r.toFixed(4));
ok('3D strong disorder (W=32, L=10): most of the way down to the stay-put value, below 0.43', row[10][32].r < 0.43 && row[10][32].r > A.R_POISSON, row[10][32].r.toFixed(4));
{ const far = A.measure({ dim: 3, L: 6, W: 120, reals: 100, seed: 11 });
  ok('3D very strong disorder (W=120, L=6): the stay-put value itself, 0.386, within 0.01', Math.abs(far.r - A.R_POISSON) < 0.01, far.r.toFixed(4) + ' +- ' + far.err.toFixed(4)); }
ok('well below the transition (W=4) every size sits at the spread-out value, within 0.015', [6, 8, 10].every(L => Math.abs(row[L][4].r - A.R_GOE) < 0.015), [6, 8, 10].map(L => row[L][4].r.toFixed(4)).join(' '));
ok('above it bigger lattices look LESS spread out (W=21: L=10 below L=6)', row[10][21].r < row[6][21].r, (row[10][21].r - row[6][21].r).toFixed(4));
console.log('       timing: one 1000-site lattice ' + (row[10][4].ms / 8).toFixed(0) + ' ms, one 512-site ' + (row[8][4].ms / 16).toFixed(0) + ' ms, one 216-site ' + (row[6][4].ms / 40).toFixed(0) + ' ms; this block ' + ((Date.now() - t0) / 1000).toFixed(1) + ' s');
// 6. flat sheet and chain at the same disorder: lower dimension is closer to stay-put
{ const c1 = A.measure({ dim: 1, L: 600, W: 4, reals: 6, seed: 9 }), c2 = A.measure({ dim: 2, L: 24, W: 4, reals: 6, seed: 9 }), c3 = A.measure({ dim: 3, L: 8, W: 4, reals: 6, seed: 9 });
  console.log('       W=4: chain r=' + c1.r.toFixed(3) + ' (600 sites)  sheet r=' + c2.r.toFixed(3) + ' (576 sites)  block r=' + c3.r.toFixed(3) + ' (512 sites)');
  ok('at W=4 a chain is in the stay-put regime while a block is spread out', c1.r < 0.42 && c3.r > 0.50); }
console.log(bad ? '  ' + bad + ' CHECK(S) FAILED' : '  ALL OK'); process.exit(bad ? 1 : 0);