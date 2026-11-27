/* ltee-core.js
 *
 * The published fitness measurements of Lenski's long-term evolution experiment
 * (Wiser, Ribeck and Lenski 2013, Science 342:1364; data on Dryad, CC0,
 * doi:10.5061/dryad.0hc2m), read from the file as published, and two curves
 * fitted to them:
 *
 *   hyperbolic   w(t) = 1 + a t / (t + b)      levels off at 1 + a
 *   power law    w(t) = (b t + 1)^a            never levels off
 *
 * Nothing here is drawn from a model: every number comes from the colony
 * counts in the file. The same file runs in a browser and under Node, so the
 * page and the command-line check use one implementation.
 */
(function (root) {
  'use strict';

  var VERSION = 'ltee-core 1';
  var DATA_MD5 = '295cae6114ea687b2b140935c71ccebc';   // as listed by Dryad for Concatenated.LTEE.data.all.csv
  var DATA_BYTES = 68275;

  // ---- MD5 (RFC 1321), to confirm the data file is the published one --------
  function md5(bytes) {
    var s = [7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
             5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
             4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
             6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21];
    var K = new Int32Array(64), i;
    for (i = 0; i < 64; i++) K[i] = Math.floor(Math.abs(Math.sin(i + 1)) * 4294967296) | 0;
    var n = bytes.length, padded = ((n + 8) >> 6) + 1, buf = new Uint8Array(padded * 64);
    buf.set(bytes); buf[n] = 0x80;
    var bits = n * 8, dv = new DataView(buf.buffer);
    dv.setUint32(padded * 64 - 8, bits >>> 0, true);
    dv.setUint32(padded * 64 - 4, Math.floor(bits / 4294967296), true);
    var a0 = 0x67452301, b0 = 0xefcdab89 | 0, c0 = 0x98badcfe | 0, d0 = 0x10325476;
    var M = new Int32Array(16);
    for (var off = 0; off < buf.length; off += 64) {
      for (i = 0; i < 16; i++) M[i] = dv.getInt32(off + i * 4, true);
      var A = a0, B = b0, C = c0, D = d0;
      for (i = 0; i < 64; i++) {
        var F, g;
        if (i < 16) { F = (B & C) | (~B & D); g = i; }
        else if (i < 32) { F = (D & B) | (~D & C); g = (5 * i + 1) % 16; }
        else if (i < 48) { F = B ^ C ^ D; g = (3 * i + 5) % 16; }
        else { F = C ^ (B | ~D); g = (7 * i) % 16; }
        F = (F + A + K[i] + M[g]) | 0;
        A = D; D = C; C = B;
        B = (B + ((F << s[i]) | (F >>> (32 - s[i])))) | 0;
      }
      a0 = (a0 + A) | 0; b0 = (b0 + B) | 0; c0 = (c0 + C) | 0; d0 = (d0 + D) | 0;
    }
    var out = '';
    [a0, b0, c0, d0].forEach(function (v) {
      for (var k = 0; k < 4; k++) out += ('0' + ((v >>> (8 * k)) & 255).toString(16)).slice(-2);
    });
    return out;
  }

  // ---- the data file ---------------------------------------------------------
  // Columns: Generation, Red.Pop, White.Pop, Population, Rep, Red.0, White.0, D.0,
  //          Red.1, White.1, D.1, Fitness, Complete, Mutator.Ever
  function parse(text) {
    var lines = text.split(/\r?\n/), head = lines[0].split(','), rows = [];
    var col = {}; head.forEach(function (h, i) { col[h.trim()] = i; });
    function num(v) { var x = parseFloat(v); return isFinite(x) ? x : NaN; }
    for (var i = 1; i < lines.length; i++) {
      if (!lines[i].trim()) continue;
      var c = lines[i].split(',');
      rows.push({
        line: i + 1,
        gen: num(c[col['Generation']]),
        redPop: c[col['Red.Pop']].trim(), whitePop: c[col['White.Pop']].trim(),
        pop: c[col['Population']].trim(), rep: c[col['Rep']].trim(),
        red0: num(c[col['Red.0']]), white0: num(c[col['White.0']]), d0: num(c[col['D.0']]),
        red1: num(c[col['Red.1']]), white1: num(c[col['White.1']]), d1: num(c[col['D.1']]),
        fitness: num(c[col['Fitness']]),
        complete: c[col['Complete']].trim() === 'Yes',
        mutator: c[col['Mutator.Ever']].trim() === 'Yes'
      });
    }
    return rows;
  }

  // Relative fitness from one competition: each competitor's realised growth
  // rate is ln(count at the end x dilution / count at the start x dilution);
  // fitness is the evolved population's rate over its ancestor's.
  function fitnessFromCounts(r) {
    var red = Math.log((r.red1 * r.d1) / (r.red0 * r.d0));
    var white = Math.log((r.white1 * r.d1) / (r.white0 * r.d0));
    return r.redPop === r.pop ? red / white : white / red;
  }

  // Mean fitness at each generation: replicates are averaged within a
  // population first, then populations are averaged. which: 'all' (every
  // population that has a measurement), 'complete' (only the populations
  // measured through to the end), 'nonmutator', 'mutator', or one population's name.
  function series(rows, which, source) {
    var byGen = {};
    rows.forEach(function (r) {
      if (which === 'complete' && !r.complete) return;
      if (which === 'nonmutator' && r.mutator) return;
      if (which === 'mutator' && !r.mutator) return;
      if (which !== 'all' && which !== 'complete' && which !== 'nonmutator' && which !== 'mutator' && r.pop !== which) return;
      var w = source === 'counts' ? fitnessFromCounts(r) : r.fitness;
      if (!isFinite(w)) return;
      var g = byGen[r.gen] || (byGen[r.gen] = {});
      (g[r.pop] || (g[r.pop] = [])).push(w);
    });
    var gens = Object.keys(byGen).map(Number).sort(function (a, b) { return a - b; });
    return gens.map(function (t) {
      var pops = Object.keys(byGen[t]), means = pops.map(function (p) {
        var v = byGen[t][p], s = 0; v.forEach(function (x) { s += x; }); return s / v.length;
      });
      var m = 0; means.forEach(function (x) { m += x; }); m /= means.length;
      var ss = 0; means.forEach(function (x) { ss += (x - m) * (x - m); });
      var assays = 0; pops.forEach(function (p) { assays += byGen[t][p].length; });
      return { t: t, w: m, se: means.length > 1 ? Math.sqrt(ss / (means.length - 1) / means.length) : NaN,
               pops: means.length, assays: assays };
    });
  }

  // Every population's own mean at every generation, each as one point. This is
  // the set of points the published fit was made to (441 of them for all twelve).
  function popPoints(rows, which, source) {
    var out = [];
    populations(rows).forEach(function (p) {
      if (which === 'complete' && !p.complete) return;
      if (which === 'nonmutator' && p.mutator) return;
      if (which === 'mutator' && !p.mutator) return;
      if (which !== 'all' && which !== 'complete' && which !== 'nonmutator' && which !== 'mutator' && p.name !== which) return;
      series(rows, p.name, source).forEach(function (q) { out.push({ t: q.t, w: q.w, pop: p.name }); });
    });
    return out;
  }

  // Small seeded generator (mulberry32), so a resampling run can be repeated exactly.
  function rng(seed) {
    var a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      var t = a; t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  // ---- the two curves --------------------------------------------------------
  var MODELS = {
    hyperbolic: {
      label: 'hyperbolic', formula: 'w = 1 + a t / (t + b)', bounded: true,
      f: function (t, p) { return 1 + p[0] * t / (t + p[1]); },
      starts: [[0.5, 2000], [1, 5000], [0.7, 500], [2, 50000], [0.3, 200]]
    },
    power: {
      label: 'power law', formula: 'w = (b t + 1)^a', bounded: false,
      f: function (t, p) { return Math.pow(p[1] * t + 1, p[0]); },
      starts: [[0.1, 0.005], [0.2, 0.001], [0.05, 0.05], [0.5, 0.0001], [0.1, 0.0005]]
    }
  };

  function rss(model, pts, p) {
    var f = MODELS[model].f, s = 0;
    for (var i = 0; i < pts.length; i++) { var d = pts[i].w - f(pts[i].t, p); s += d * d; }
    return s;
  }

  // Nelder-Mead on the logarithms of the two parameters (both must be positive).
  function nelderMead(fn, x0, iters) {
    var n = x0.length, sim = [x0.slice()], i, j;
    for (i = 0; i < n; i++) { var x = x0.slice(); x[i] += 0.4; sim.push(x); }
    var val = sim.map(fn);
    for (var it = 0; it < iters; it++) {
      var order = val.map(function (v, k) { return k; }).sort(function (a, b) { return val[a] - val[b]; });
      sim = order.map(function (k) { return sim[k]; }); val = order.map(function (k) { return val[k]; });
      if (Math.abs(val[n] - val[0]) <= 1e-15 * (Math.abs(val[0]) + 1e-300) && it > 50) break;
      var cen = new Array(n).fill(0);
      for (i = 0; i < n; i++) for (j = 0; j < n; j++) cen[j] += sim[i][j] / n;
      var refl = cen.map(function (c, k) { return c + (c - sim[n][k]); }), fr = fn(refl);
      if (fr < val[0]) {
        var exp = cen.map(function (c, k) { return c + 2 * (c - sim[n][k]); }), fe = fn(exp);
        if (fe < fr) { sim[n] = exp; val[n] = fe; } else { sim[n] = refl; val[n] = fr; }
      } else if (fr < val[n - 1]) { sim[n] = refl; val[n] = fr; }
      else {
        var con = cen.map(function (c, k) { return c + 0.5 * (sim[n][k] - c); }), fc = fn(con);
        if (fc < val[n]) { sim[n] = con; val[n] = fc; }
        else for (i = 1; i <= n; i++) { sim[i] = sim[i].map(function (v, k) { return sim[0][k] + 0.5 * (v - sim[0][k]); }); val[i] = fn(sim[i]); }
      }
    }
    var best = 0; for (i = 1; i <= n; i++) if (val[i] < val[best]) best = i;
    return { x: sim[best], f: val[best] };
  }

  // Least-squares fit from several starting points; the best is kept. When a
  // starting point is given (a fit already made to nearly the same points) only
  // that one is used.
  function fit(model, pts, from) {
    var m = MODELS[model], n = pts.length, best = null;
    function fn(x) { var v = rss(model, pts, [Math.exp(x[0]), Math.exp(x[1])]); return isFinite(v) ? v : 1e300; }
    (from ? [from] : m.starts).forEach(function (s) {
      var r = nelderMead(fn, [Math.log(s[0]), Math.log(s[1])], 4000);
      r = nelderMead(fn, r.x, 4000);                       // restart from the answer to tighten it
      if (!best || r.f < best.f) best = r;
    });
    var p = [Math.exp(best.x[0]), Math.exp(best.x[1])], mean = 0;
    pts.forEach(function (q) { mean += q.w; }); mean /= n;
    var tot = 0; pts.forEach(function (q) { tot += (q.w - mean) * (q.w - mean); });
    var k = 2;
    return { model: model, a: p[0], b: p[1], n: n, rss: best.f, r2: 1 - best.f / tot,
             aic: n * Math.log(best.f / n) + 2 * k, bic: n * Math.log(best.f / n) + k * Math.log(n) };
  }

  // How far the fit is from a true minimum: the slope of the error in each
  // parameter, scaled so that 0 means flat.
  function slope(model, pts, f) {
    var out = [], p = [f.a, f.b];
    for (var i = 0; i < 2; i++) {
      var h = p[i] * 1e-5, up = p.slice(), dn = p.slice(); up[i] += h; dn[i] -= h;
      out.push(Math.abs((rss(model, pts, up) - rss(model, pts, dn)) / (2 * h) * p[i] / f.rss));
    }
    return Math.max(out[0], out[1]);
  }

  function compare(pts) {
    var h = fit('hyperbolic', pts), p = fit('power', pts), d = h.bic - p.bic;
    return { hyperbolic: h, power: p, dBIC: d, odds: Math.exp(d / 2), better: d > 0 ? 'power' : 'hyperbolic' };
  }

  // Fit on the early part of the record only (pts with t <= upTo), then score
  // the forecast against the later averages in `score` (t > upTo), which the
  // fit never saw. bias < 0 means the curve forecast too little fitness.
  function forecast(pts, score, upTo) {
    var early = pts.filter(function (q) { return q.t <= upTo; }), late = score.filter(function (q) { return q.t > upTo; });
    var out = { upTo: upTo, nEarly: early.length, nLate: late.length };
    ['hyperbolic', 'power'].forEach(function (m) {
      var f = fit(m, early), s = 0, bias = 0;
      late.forEach(function (q) { var d = MODELS[m].f(q.t, [f.a, f.b]) - q.w; s += d * d; bias += d; });
      out[m] = { fit: f, rms: late.length ? Math.sqrt(s / late.length) : NaN, bias: late.length ? bias / late.length : NaN,
                 atEnd: late.length ? MODELS[m].f(late[late.length - 1].t, [f.a, f.b]) : NaN };
    });
    out.measuredAtEnd = late.length ? late[late.length - 1].w : NaN;
    out.seAtEnd = late.length ? late[late.length - 1].se : NaN;
    out.endT = late.length ? late[late.length - 1].t : NaN;
    return out;
  }

  // Would the answer survive a different draw of populations? Draw as many
  // populations as there are, with repeats allowed, refit both curves, and do
  // that `times` times. Returns one entry per draw.
  function resample(rows, which, times, seed, progress) {
    var names = [], byPop = {}, rand = rng(seed), out = [];
    popPoints(rows, which).forEach(function (q) { if (!byPop[q.pop]) { byPop[q.pop] = []; names.push(q.pop); } byPop[q.pop].push(q); });
    var all = []; names.forEach(function (nm) { all = all.concat(byPop[nm]); });
    var h0 = fit('hyperbolic', all), p0 = fit('power', all);
    for (var k = 0; k < times; k++) {
      var pts = [];
      for (var j = 0; j < names.length; j++) pts = pts.concat(byPop[names[Math.floor(rand() * names.length)]]);
      var h = fit('hyperbolic', pts, [h0.a, h0.b]), p = fit('power', pts, [p0.a, p0.b]);
      out.push({ dBIC: h.bic - p.bic, ha: h.a, hb: h.b, pa: p.a, pb: p.b });
      if (progress) progress(k + 1, times);
    }
    return out;
  }

  function populations(rows) {
    var seen = {}, out = [];
    rows.forEach(function (r) {
      if (!seen[r.pop]) { seen[r.pop] = { name: r.pop, complete: r.complete, mutator: r.mutator, assays: 0, last: 0 }; out.push(seen[r.pop]); }
      if (isFinite(r.fitness)) { seen[r.pop].assays++; if (r.gen > seen[r.pop].last) seen[r.pop].last = r.gen; }
    });
    return out.sort(function (a, b) { return a.name < b.name ? -1 : 1; });
  }

  // ---- checks ---------------------------------------------------------------
  // The curves as printed in the open-access follow-up paper (Lenski et al. 2015,
  // Proc. R. Soc. B 282:20152292, section 3a), with the values it quotes for them
  // at 40,000, 50,000 and 60,000 generations.
  var PUBLISHED = {
    hyperbolic: { a: '0.7007', b: '4431', at: [1.6308, 1.6437, 1.6525] },
    power: { a: '0.0950', b: '0.00515', at: [1.6597, 1.6951, 1.7246] },
    times: [40000, 50000, 60000]
  };
  // What this code gives on the reference machine (Node 22, x86-64) for all
  // twelve populations. Logarithms and powers may differ in the last bit between
  // machines, so these are compared to five figures, not exactly.
  var REFERENCE = { ha: 0.7007418487, hb: 4431.074121, pa: 0.09497023365, pb: 0.005148821349, dBIC: 34.470475 };

  function selfCheck(bytes) {
    var out = [];
    function add(what, pass, detail) { out.push({ what: what, pass: !!pass, detail: detail }); }
    function enc(s) { var u = new Uint8Array(s.length); for (var i = 0; i < s.length; i++) u[i] = s.charCodeAt(i); return u; }
    function rel(x, y) { return Math.abs(x - y) / Math.abs(y); }

    var m1 = md5(enc('')), m2 = md5(enc('abc')), m3 = md5(enc('The quick brown fox jumps over the lazy dog'));
    add('The checksum code gives the textbook answers for three known texts',
        m1 === 'd41d8cd98f00b204e9800998ecf8427e' && m2 === '900150983cd24fb0d6963f7d28e17f72' && m3 === '9e107d9d372bb6826bd81d3542a419d6',
        'empty text, "abc" and the quick brown fox');

    var sum = md5(bytes);
    add('The data file is, byte for byte, the one the authors deposited', bytes.length === DATA_BYTES && sum === DATA_MD5,
        bytes.length.toLocaleString('en') + ' bytes, checksum ' + sum + (sum === DATA_MD5 ? ', the checksum Dryad lists' : ', but Dryad lists ' + DATA_MD5));

    var text = ''; for (var i = 0; i < bytes.length; i++) text += String.fromCharCode(bytes[i]);
    var rows = parse(text), pops = populations(rows), grand = series(rows, 'all'), measured = 0;
    rows.forEach(function (r) { if (isFinite(r.fitness)) measured++; });
    add('It holds what the paper describes: twelve populations, measured from the start to generation 50,000',
        rows.length === 928 && pops.length === 12 && grand.length === 41 && grand[0].t === 0 && grand[40].t === 50000 && measured === 922,
        rows.length + ' competitions, ' + measured + ' with a result, ' + pops.length + ' populations, ' + grand.length + ' time points');

    var worst = 0, n = 0;
    rows.forEach(function (r) { var w = fitnessFromCounts(r); if (isFinite(w) && isFinite(r.fitness)) { n++; worst = Math.max(worst, Math.abs(w - r.fitness)); } });
    add('Every fitness value in the file follows from its own colony counts', n === measured && worst < 1e-8,
        n + ' recomputed; largest difference ' + worst.toExponential(1));

    var times = grand.map(function (q) { return q.t; });
    var th = [0.6, 3000], tp = [0.12, 0.002];
    var fh = fit('hyperbolic', times.map(function (t) { return { t: t, w: MODELS.hyperbolic.f(t, th) }; }));
    var fp = fit('power', times.map(function (t) { return { t: t, w: MODELS.power.f(t, tp) }; }));
    var e = Math.max(rel(fh.a, th[0]), rel(fh.b, th[1]), rel(fp.a, tp[0]), rel(fp.b, tp[1]));
    add('Given points that lie exactly on a known curve, the fitting code returns that curve (both kinds)', e < 1e-6,
        'largest error in a recovered value: ' + e.toExponential(1) + ' of the value. These made-up points test the code only and are not used below.');

    var pts = popPoints(rows, 'all'), c = compare(pts);
    var sh = slope('hyperbolic', pts, c.hyperbolic), sp = slope('power', pts, c.power);
    add('On the real data each fit sits at the bottom of its error: no small change to either number improves it', sh < 1e-4 && sp < 1e-4,
        'remaining slope ' + sh.toExponential(1) + ' (hyperbolic) and ' + sp.toExponential(1) + ' (power law); 0 is flat');

    var okPub = c.hyperbolic.a.toFixed(4) === PUBLISHED.hyperbolic.a && c.hyperbolic.b.toFixed(0) === PUBLISHED.hyperbolic.b &&
                c.power.a.toFixed(4) === PUBLISHED.power.a && c.power.b.toFixed(5) === PUBLISHED.power.b, offPub = 0;
    PUBLISHED.times.forEach(function (t, k) {
      offPub = Math.max(offPub, Math.abs(MODELS.hyperbolic.f(t, [c.hyperbolic.a, c.hyperbolic.b]) - PUBLISHED.hyperbolic.at[k]),
                                Math.abs(MODELS.power.f(t, [c.power.a, c.power.b]) - PUBLISHED.power.at[k]));
    });
    add('The fits land on the curves the authors printed: w = 1 + 0.7007 t / (t + 4431) and w = (0.00515 t + 1)^0.0950',
        okPub && offPub < 0.0005,
        'here: 1 + ' + c.hyperbolic.a.toFixed(4) + ' t / (t + ' + c.hyperbolic.b.toFixed(0) + ') and (' + c.power.b.toFixed(5) + ' t + 1)^' + c.power.a.toFixed(4) +
        '; their quoted values at 40,000, 50,000 and 60,000 generations matched within ' + offPub.toFixed(4));

    var r = Math.max(rel(c.hyperbolic.a, REFERENCE.ha), rel(c.hyperbolic.b, REFERENCE.hb), rel(c.power.a, REFERENCE.pa), rel(c.power.b, REFERENCE.pb));
    add('Your machine gives the same numbers as the reference machine, to five figures', r < 1e-5 && Math.abs(c.dBIC - REFERENCE.dBIC) < 1e-3,
        'largest difference ' + r.toExponential(1) + ' of the value; score gap ' + c.dBIC.toFixed(4) + ' here, ' + REFERENCE.dBIC.toFixed(4) + ' there');

    return { results: out, rows: rows };
  }

  var api = { VERSION: VERSION, PUBLISHED: PUBLISHED, REFERENCE: REFERENCE, selfCheck: selfCheck, DATA_MD5: DATA_MD5, DATA_BYTES: DATA_BYTES, MODELS: MODELS,
              md5: md5, parse: parse, fitnessFromCounts: fitnessFromCounts, series: series, popPoints: popPoints,
              rng: rng, rss: rss, fit: fit, slope: slope, compare: compare, forecast: forecast,
              resample: resample, populations: populations };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.LteeCore = api;
})(typeof self !== 'undefined' ? self : this);
