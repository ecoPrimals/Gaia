/* anderson-core.js — the Anderson model, small enough to run in a browser tab.
 *
 * H = sum_i e_i |i><i|  +  sum_<ij> |i><j|      on a chain (1D), sheet (2D) or block (3D), periodic edges
 * e_i drawn evenly from [-W/2, +W/2].  W is the disorder; the hopping is 1.
 *
 * What is measured: the level-spacing ratio  r = min(s_n, s_n+1) / max(s_n, s_n+1)  of neighbouring
 * eigenvalue gaps near the band centre.  Its average tells the two regimes apart:
 *   about 0.5307  the states spread through the whole lattice (extended; statistics of random matrices, GOE)
 *   about 0.3863  the states stay where they are (localized; uncorrelated levels, Poisson)  = 2 ln 2 - 1
 *
 * Everything here is exact dense linear algebra (Householder reduction, then QL), no approximation
 * beyond floating point.  The same file runs in a web worker and in Node (for the checks).
 */
(function (root) {
  'use strict';

  var R_GOE = 0.5307, R_POISSON = 2 * Math.LN2 - 1;

  /* A small seeded generator (mulberry32): the same seed gives the same lattice on any machine. */
  function rng(seed) {
    var a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      var t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  /* Number of sites: L, L*L or L*L*L (whole-number arithmetic, the same on every machine). */
  function sites(dim, L) { var n = 1, d; for (d = 0; d < dim; d++) n *= L; return n; }

  /* The Hamiltonian as a dense symmetric matrix, row-major. dim 1..3, L >= 3 sites along each edge. */
  function hamiltonian(dim, L, W, rand) {
    var n = sites(dim, L), a = new Float64Array(n * n), i, d, stride, x, j;
    for (i = 0; i < n; i++) a[i * n + i] = (rand() - 0.5) * W;
    for (i = 0; i < n; i++) {
      stride = 1;
      for (d = 0; d < dim; d++) {
        x = Math.floor(i / stride) % L;
        j = i + (x === L - 1 ? -(L - 1) * stride : stride);     /* the neighbour one step on, wrapping round */
        a[i * n + j] = 1; a[j * n + i] = 1;
        stride *= L;
      }
    }
    return a;
  }

  /* Householder reduction of a real symmetric matrix to tridiagonal form (eigenvalues only).
     On return d holds the diagonal, e the off-diagonal (e[0] unused). The matrix is overwritten. */
  function tridiagonal(a, n, d, e) {
    var i, j, k, l, f, g, h, hh, scale, row, rowj;
    for (i = n - 1; i > 0; i--) {
      l = i - 1; h = 0; scale = 0; row = i * n;
      if (l > 0) {
        for (k = 0; k <= l; k++) scale += Math.abs(a[row + k]);
        if (scale === 0) e[i] = a[row + l];
        else {
          for (k = 0; k <= l; k++) { a[row + k] /= scale; h += a[row + k] * a[row + k]; }
          f = a[row + l];
          g = f >= 0 ? -Math.sqrt(h) : Math.sqrt(h);
          e[i] = scale * g; h -= f * g; a[row + l] = f - g; f = 0;
          for (j = 0; j <= l; j++) {
            g = 0; rowj = j * n;
            for (k = 0; k <= j; k++) g += a[rowj + k] * a[row + k];
            for (k = j + 1; k <= l; k++) g += a[k * n + j] * a[row + k];
            e[j] = g / h; f += e[j] * a[row + j];
          }
          hh = f / (h + h);
          for (j = 0; j <= l; j++) {
            f = a[row + j]; e[j] = g = e[j] - hh * f; rowj = j * n;
            for (k = 0; k <= j; k++) a[rowj + k] -= (f * e[k] + g * a[row + k]);
          }
        }
      } else e[i] = a[row + l];
      d[i] = h;
    }
    e[0] = 0;
    for (i = 0; i < n; i++) d[i] = a[i * n + i];
  }

  /* QL with implicit shifts on the tridiagonal matrix: d becomes the eigenvalues (unsorted). */
  function ql(d, e, n) {
    var i, l, m, iter, b, c, dd, f, g, p, r, s;
    for (i = 1; i < n; i++) e[i - 1] = e[i];
    e[n - 1] = 0;
    for (l = 0; l < n; l++) {
      iter = 0;
      do {
        for (m = l; m < n - 1; m++) {
          dd = Math.abs(d[m]) + Math.abs(d[m + 1]);
          if (Math.abs(e[m]) <= 2.220446049250313e-16 * dd) break;
        }
        if (m !== l) {
          if (iter++ === 80) throw new Error('eigenvalues did not settle');
          g = (d[l + 1] - d[l]) / (2 * e[l]);
          r = Math.sqrt(g * g + 1);
          g = d[m] - d[l] + e[l] / (g + (g >= 0 ? r : -r));
          s = 1; c = 1; p = 0;
          for (i = m - 1; i >= l; i--) {
            f = s * e[i]; b = c * e[i];
            r = Math.sqrt(f * f + g * g);
            e[i + 1] = r;
            if (r === 0) { d[i + 1] -= p; e[m] = 0; break; }
            s = f / r; c = g / r; g = d[i + 1] - p;
            r = (d[i] - g) * s + 2 * c * b;
            p = s * r;
            d[i + 1] = g + p;
            g = c * r - b;
          }
          if (r === 0 && i >= l) continue;
          d[l] -= p; e[l] = g; e[m] = 0;
        }
      } while (m !== l);
    }
  }

  /* All eigenvalues of a dense symmetric matrix, ascending. The matrix is overwritten. */
  function eigenvalues(a, n) {
    var d = new Float64Array(n), e = new Float64Array(n);
    tridiagonal(a, n, d, e);
    ql(d, e, n);
    return d.sort();
  }

  /* Spacing ratios of the levels in the middle `window` share of the spectrum (the band centre). */
  function ratios(ev, window) {
    var n = ev.length, keep = Math.max(4, Math.floor(n * window)), lo = Math.floor((n - keep) / 2), out = [], i, s1, s2;
    for (i = lo + 1; i < lo + keep - 1; i++) {
      s1 = ev[i] - ev[i - 1]; s2 = ev[i + 1] - ev[i];
      if (s1 > 0 || s2 > 0) out.push(Math.min(s1, s2) / Math.max(s1, s2));
    }
    return out;
  }

  /* One measurement: `reals` independent lattices at the same disorder.
     Returns the mean ratio, its standard error across lattices, and a 20-bin histogram of all ratios. */
  function measure(q, progress) {
    var dim = q.dim, L = q.L, W = q.W, reals = q.reals, window = q.window || 0.34, seed = q.seed >>> 0;
    var n = sites(dim, L), means = [], hist = new Array(20).fill(0), count = 0, k, rs, i, sum, t0 = Date.now();
    for (k = 0; k < reals; k++) {
      rs = ratios(eigenvalues(hamiltonian(dim, L, W, rng(seed + 7919 * k)), n), window);
      sum = 0;
      for (i = 0; i < rs.length; i++) { sum += rs[i]; hist[Math.min(19, Math.floor(rs[i] * 20))]++; }
      means.push(sum / rs.length); count += rs.length;
      if (progress) progress(k + 1, reals);
    }
    var mean = 0, v = 0;
    for (k = 0; k < reals; k++) mean += means[k];
    mean /= reals;
    for (k = 0; k < reals; k++) v += (means[k] - mean) * (means[k] - mean);
    return { dim: dim, L: L, W: W, sites: n, reals: reals, seed: seed, window: window, r: mean,
             err: reals > 1 ? Math.sqrt(v / (reals - 1) / reals) : null, ratios: count, hist: hist, ms: Date.now() - t0 };
  }

  var api = { VERSION: 'anderson-core 1', R_GOE: R_GOE, R_POISSON: R_POISSON, rng: rng, sites: sites, hamiltonian: hamiltonian, eigenvalues: eigenvalues, ratios: ratios, measure: measure };
  root.AndersonCore = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof self !== 'undefined' ? self : globalThis);
