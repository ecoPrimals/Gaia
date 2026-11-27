/* house.js - the house: its gates, how each stands in the mesh, and the engine's picture of them. One file, read by
   the HUD, the atlas and the MERCATOR page, so all three say the same thing about the house.

   Two things are read, both from this site:
     /static/mercator.json   the names for the engine's picture (/static/mercator.png) and the mesh as it was when the
                             picture was drawn. The kenshi.reborn engine writes both: kenshi-reborn --mercator --snapshot
     /api/mesh               the mesh as it is now: which bodies answer, on which commit, which primals each runs.
                             Only names, standings, commits and primal names are read from it. Addresses are not.

   gaiaHouse.load()                 -> a promise of the house (below). The mesh is asked again at most every 20 seconds.
   gaiaHouse.picture(holder, house) lays the picture into holder with every name over its place in it.
   gaiaHouse.table(holder, house, link)   the gates as rows: where, in the picture, in the mesh now, commit, primals.
                                    link(primal) may give an address for a primal's own page.
   gaiaHouse.drawn(house) / .now(house)   one sentence each: the mesh as the picture has it, and as it is.
   gaiaHouse.runs(house, primal)    the gates that run a primal.
   gaiaHouse.graph(pins)            from /static/atlas-pins.json: every node of the spore graph by its name in small
                                    letters -> {name, kind, page, pin}, so a primal named by a gate finds its page and
                                    the pin it hangs on.

   The house: {taken (ms), gates: [{name, zone, drawn, now, tip, up: [primal], down: [primal], pi}], extra: [bodies of
   the mesh that are not in the picture], machines: n, zones: [name], moved: [gate names that stand differently now],
   asked: the mesh answered this page, failed: it did not, level: both bodies on one commit (true, false or null)}.
   A gate's zone is a house, never finer: the picture and this file know "House 1" and "House 2" and nothing else. */
(function (root) {
  'use strict';
  var D = root.document;
  var WORDS = {answers: 'answers', silent: 'silent', outside: 'not a body of the mesh', unknown: 'unknown', machine: 'machine'};
  var names = null, bodies = null, level = null, failed = false, askedAt = 0, asking = null, naming = null;

  function el(tag, cls, text) { var e = D.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function get(url) { return fetch(url, {cache: 'no-store'}).then(function (r) { if (!r.ok) throw new Error(url + ' ' + r.status); return r.json(); }); }
  function ago(secs) {
    if (secs < 90) return 'a moment ago';
    if (secs < 5400) return Math.round(secs / 60) + ' minutes ago';
    if (secs < 129600) return Math.round(secs / 3600) + ' hours ago';
    return Math.round(secs / 86400) + ' days ago';
  }
  function list(a) { return Array.isArray(a) ? a.filter(function (s) { return typeof s === 'string'; }) : []; }

  // what the mesh says now, by gate name. Addresses and host names in the answer are not read.
  function read(m) {
    var out = {};
    function take(b, answers) {
      if (!b || typeof b.name !== 'string') return;
      var pi = b.pi_body || null;
      out[b.name] = {answers: answers, tip: answers ? String(b.tip || '') : '', up: pi ? list(pi.up) : [], down: pi ? list(pi.down) : [], pi: !!pi};
    }
    take(m.self, true);
    (m.peers || []).forEach(function (p) { take(p, !!p.answers); });
    level = m.level === true ? true : m.level === false ? false : null;
    return out;
  }
  function make() {
    var gates = (names.nodes || []).filter(function (n) { return n.kind === 'gate'; }).map(function (n) {
      var live = bodies ? bodies[n.name] : null, now = bodies ? (!live ? 'outside' : live.answers ? 'answers' : 'silent') : null;
      return {name: n.name, zone: n.zone || 'roaming', drawn: n.standing, now: now, tip: live ? live.tip : (bodies ? '' : n.tip || ''),
              up: live ? live.up : (bodies ? [] : list(n.primals_up)), down: live ? live.down : (bodies ? [] : list(n.primals_down)),
              pi: live ? live.pi : (!bodies && list(n.primals_up).length + list(n.primals_down).length > 0)};
    });
    var extra = [];
    if (bodies) Object.keys(bodies).forEach(function (name) {
      if (gates.some(function (g) { return g.name === name; })) return;
      var b = bodies[name]; extra.push({name: name, zone: '', drawn: null, now: b.answers ? 'answers' : 'silent', tip: b.tip, up: b.up, down: b.down, pi: b.pi});
    });
    var zones = [];
    gates.forEach(function (g) { if (zones.indexOf(g.zone) < 0) zones.push(g.zone); });
    return {names: names, taken: names.taken_unix * 1000, gates: gates, extra: extra, zones: zones,
            machines: (names.nodes || []).filter(function (n) { return n.kind !== 'gate'; }).length,
            moved: gates.filter(function (g) { return g.now && g.now !== g.drawn; }).map(function (g) { return g.name; }).concat(extra.map(function (g) { return g.name; })),
            asked: !!bodies, failed: failed, level: bodies ? level : null};
  }
  function load() {
    if (!naming) naming = get('/static/mercator.json').then(function (j) { names = j; }, function (e) { naming = null; throw e; });
    if (!asking && Date.now() - askedAt > 20000) {
      askedAt = Date.now();
      asking = get('/api/mesh').then(function (m) { if (!m || !m.self) throw new Error('no body'); bodies = read(m); failed = false; }, function () { failed = !bodies; })
        .then(function () { asking = null; });
    }
    return Promise.all([naming, asking || Promise.resolve()]).then(make);
  }

  function count(n, word) { return n + ' ' + word + (n === 1 ? '' : 's'); }
  function drawn(h) {                                                 // the mesh as the picture has it
    var m = h.names.mesh || {};
    return !m.answered ? 'no gate answered about the mesh, so every gate is unlit'
      : m.answering + ' of ' + m.gates + ' gates answered in the mesh' + (m.silent ? ', ' + m.silent + ' silent' : '')
        + (m.level === true ? ', level' : m.level === false ? ', not level' : '') + ', ' + count(m.primals_up, 'primal') + ' up' + (m.primals_down ? ', ' + m.primals_down + ' down' : '');
  }
  function now(h) {                                                   // the mesh as it is
    if (!h.asked) return h.failed ? 'the mesh did not answer this page' : 'asking the mesh';
    var all = h.gates.concat(h.extra), a = all.filter(function (g) { return g.now === 'answers'; }), s = all.filter(function (g) { return g.now === 'silent'; });
    var up = 0, down = 0; all.forEach(function (g) { up += g.up.length; down += g.down.length; });
    return a.length + ' of ' + count(h.gates.length, 'gate') + ' answer in the mesh now' + (s.length ? ', ' + s.length + ' silent' : '')
      + (h.level === true ? ', level' : h.level === false ? ', not level' : '') + ', ' + count(up, 'primal') + ' up' + (down ? ', ' + down + ' down' : '');
  }
  function runs(h, primal) {
    var p = String(primal).toLowerCase();
    return h.gates.concat(h.extra).filter(function (g) { return g.up.some(function (u) { return u.toLowerCase() === p; }); }).map(function (g) { return g.name; });
  }
  function graph(pins) {
    var out = {};
    ((pins && pins.pins) || []).forEach(function (p) { (p.graph || []).forEach(function (g) { out[String(g[0]).toLowerCase()] = {name: g[0], kind: g[1], page: g[3] || '', pin: p.id}; }); });
    return out;
  }

  function style() {
    if (D.getElementById('gaia-house-css')) return;
    var s = el('style'); s.id = 'gaia-house-css';
    s.textContent = '.gh-stage{position:relative;border:1px solid #1e2228;border-radius:12px;overflow:hidden;background:#1a1a2e}' +
      '.gh-stage img{display:block;width:100%;height:auto}' +
      '.gh-stage svg{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}' +
      '.gh-stage svg line{stroke:#ffffff55;stroke-width:1;vector-effect:non-scaling-stroke}' +
      ".gh-name{position:absolute;font:500 11px/1.25 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;padding:1px 5px;border-radius:3px;background:#08090bcc;border:1px solid #ffffff22;color:#e0dcd6;white-space:nowrap}" +
      '.gh-name.answers{color:#f5f0e8;border-color:#5aad72}.gh-name.silent{color:#ffb4b4;border-color:#d45b5b}.gh-name.outside,.gh-name.unknown{color:#8a857e}' +
      '.gh-name.machine{color:#5a5650;border-color:transparent;background:#08090b99}' +
      ".gh-zone{position:absolute;transform:translate(-50%,-50%);font:500 12px/1 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;letter-spacing:.18em;text-transform:uppercase;color:#ffffff66;white-space:nowrap}" +
      '.gh-dot{position:absolute;width:5px;height:5px;margin:-2.5px 0 0 -2.5px;border-radius:50%;background:#ffffffaa}' +
      '.gh-table{width:100%;border-collapse:collapse}.gh-table th{text-align:left;white-space:nowrap;font-weight:400;opacity:.65;font-size:.85em;text-transform:uppercase;letter-spacing:.05em;padding:6px 10px;border-bottom:1px solid #1e2228}' +
      '.gh-table td{padding:6px 10px;border-bottom:1px solid #1e2228;vertical-align:top}.gh-table td.gh-mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;white-space:nowrap}' +
      '.gh-table a{color:inherit;text-decoration:none;border-bottom:1px solid #ffffff33}.gh-table .gh-down{color:#d45b5b}' +
      '.gh-answers{color:#5aad72}.gh-silent{color:#d45b5b}.gh-outside,.gh-unknown{color:#8a857e}' +
      '@media (max-width:640px){.gh-name.machine,.gh-name.outside{display:none}}';
    D.head.appendChild(s);
  }

  // The picture with the names laid over it: each just above its point, moved up or down when it would cover another.
  // The names are lit as the picture is: by how each gate stood when it was drawn.
  function picture(holder, h) {
    style();
    var st = holder._gh;
    if (!st) {
      var stage = el('div', 'gh-stage'), img = el('img'), svg = D.createElementNS('http://www.w3.org/2000/svg', 'svg');
      img.width = (h.names.size || [1600, 900])[0]; img.height = (h.names.size || [1600, 900])[1];
      svg.setAttribute('viewBox', '0 0 100 100'); svg.setAttribute('preserveAspectRatio', 'none'); svg.setAttribute('aria-hidden', 'true');
      stage.appendChild(img); stage.appendChild(svg); holder.textContent = ''; holder.appendChild(stage);
      st = holder._gh = {stage: stage, img: img, svg: svg, h: h, taken: null};
      img.addEventListener('load', function () { lay(st); });
      root.addEventListener('resize', function () { lay(st); });
    }
    st.h = h;
    if (st.taken !== h.names.taken_unix) { st.taken = h.names.taken_unix; st.img.src = '/static/mercator.png?t=' + h.names.taken_unix; }
    st.img.alt = 'The gates of the house drawn as a world by the kenshi.reborn engine. When it was drawn, ' + drawn(h) + '.';
    lay(st);
    return st;
  }
  function lay(st) {
    var stage = st.stage, n = st.h.names;
    Array.prototype.slice.call(stage.querySelectorAll('.gh-name,.gh-zone,.gh-dot')).forEach(function (e) { e.remove(); });
    while (st.svg.firstChild) st.svg.removeChild(st.svg.firstChild);
    var W = stage.clientWidth, H = stage.clientHeight, placed = [];
    if (!W || !H) return;
    (n.zones || []).forEach(function (z) {
      if (!z.at) return;
      var e = el('div', 'gh-zone', z.name); e.style.left = (z.at[0] * 100) + '%'; e.style.top = (z.at[1] * 100 + 9) + '%'; stage.appendChild(e);
    });
    var order = {answers: 0, silent: 0, outside: 1, unknown: 1, machine: 2};
    (n.nodes || []).filter(function (x) { return x.at; }).sort(function (a, b) { return order[a.standing] - order[b.standing] || a.at[1] - b.at[1]; }).forEach(function (x) {
      var px = x.at[0] * W, py = x.at[1] * H;
      var d = el('div', 'gh-dot'); d.style.left = px + 'px'; d.style.top = py + 'px'; stage.appendChild(d);
      var e = el('div', 'gh-name ' + x.standing, x.name); stage.appendChild(e);
      e.title = x.name + (x.zone ? ' · ' + x.zone : '') + ' · when drawn: ' + (WORDS[x.standing] || x.standing);
      if (root.getComputedStyle(e).display === 'none') { d.remove(); return; }
      var w = e.offsetWidth, hh = e.offsetHeight, box = null;
      for (var k = 0; k < 14 && !box; k++) {
        var step = Math.ceil(k / 2) * (hh + 3), top = (k % 2 === 0) ? py - 8 - hh - step : py + 8 + step;
        var left = Math.min(Math.max(px - w / 2, 2), W - w - 2);
        if (top < 2 || top + hh > H - 2) continue;
        var c = {l: left - 2, t: top - 1, r: left + w + 2, b: top + hh + 1};
        if (!placed.some(function (p) { return c.l < p.r && c.r > p.l && c.t < p.b && c.b > p.t; })) box = c;
      }
      if (!box) { e.remove(); return; }
      placed.push(box);
      e.style.left = (box.l + 2) + 'px'; e.style.top = (box.t + 1) + 'px';
      var ly = (box.t + 1 < py) ? box.b - 1 : box.t + 1, line = D.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('x1', px / W * 100); line.setAttribute('y1', py / H * 100);
      line.setAttribute('x2', (box.l + box.r) / 2 / W * 100); line.setAttribute('y2', ly / H * 100);
      st.svg.appendChild(line);
    });
  }

  function table(holder, h, link) {
    style();
    var t = el('table', 'gh-table'), head = el('tr'), body = el('tbody');
    ['Gate', 'Where', 'In the picture', 'In the mesh now', 'Commit', 'Primals'].forEach(function (w) { head.appendChild(el('th', null, w)); });
    var th = el('thead'); th.appendChild(head); t.appendChild(th); t.appendChild(body);
    h.gates.concat(h.extra).forEach(function (g) {
      var tr = el('tr');
      tr.appendChild(el('td', 'gh-mono', g.name)); tr.appendChild(el('td', null, g.zone));
      tr.appendChild(el('td', 'gh-' + (g.drawn || 'outside'), g.drawn ? (WORDS[g.drawn] || g.drawn) : 'not in the picture'));
      tr.appendChild(el('td', g.now ? 'gh-' + g.now : 'gh-outside', g.now ? WORDS[g.now] : (h.failed ? 'the mesh did not answer this page' : 'asking')));
      tr.appendChild(el('td', 'gh-mono', g.tip));
      var td = el('td');
      if (g.pi) {
        td.appendChild(D.createTextNode(g.up.length + ' up' + (g.down.length ? ', ' + g.down.length + ' down' : '') + (g.up.length + g.down.length ? ': ' : '')));
        g.up.concat(g.down).forEach(function (p, i) {
          var to = link ? link(p) : null, e = to ? el('a', null, p) : el('span', null, p);
          if (to) { e.href = to; e.target = '_blank'; e.rel = 'noopener'; }
          if (i >= g.up.length) e.className = 'gh-down';
          if (i) td.appendChild(D.createTextNode(' · '));
          td.appendChild(e);
        });
      }
      tr.appendChild(td); body.appendChild(tr);
    });
    holder.textContent = ''; holder.appendChild(t);
    return t;
  }

  root.gaiaHouse = {load: load, picture: picture, table: table, drawn: drawn, now: now, runs: runs, graph: graph, ago: ago, WORDS: WORDS};
})(typeof window !== 'undefined' ? window : globalThis);
