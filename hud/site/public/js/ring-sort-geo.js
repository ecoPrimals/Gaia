/**
 * Ring-Sort Geo — static bars become rings that topo-sort and re-sort.
 *
 * The geo subdivision bars at the bottom were STATIC pills.
 * Now they're rings — topes that spin, bounce, grind, agglutinate.
 * Data updates → rings re-sort: big ones push small ones out,
 * new granularity emerges when data splits, the sorting IS the display.
 *
 * Reads from /dashboard.json (same feed as hud-core).
 * Replaces the static #d-geo content with a canvas + summary.
 *
 * Kevin Mok / Tamison / ecoPrimal / attsi
 * ORCID 0009-0004-2141-0321
 */
(function () {
  'use strict';

  var PI  = Math.PI;
  var TAU = PI * 2;
  var PHI = (1 + Math.sqrt(5)) / 2; // golden ratio for spacing

  /* ═══ State ═══ */
  var rings     = [];
  var lastTotal = 1;
  var frame     = 0;
  var canvas    = null;
  var ctx       = null;
  var animId    = null;
  var mounted   = false;
  var hovered   = null;

  /* ═══ Colors ═══ */
  var ASN_C = {
    datacenter:'#e74c3c', self:'#58a6ff', cloud:'#f1c40f',
    residential:'#2ecc71', colocation:'#9b59b6',
    telecom:'#ff6b35', unknown:'#6e7681'
  };
  var CC_C = {
    US:'#ff6b35','IE/US':'#e74c3c',IE:'#e74c3c',CN:'#f1c40f',
    DE:'#58a6ff',GB:'#a6e3a1',FR:'#f778ba',JP:'#ff9f43',
    CA:'#3fb950','??':'#484f58'
  };

  /* ═══ Ring constructor ═══ */
  function R(id, label, mass, color, kind, depth) {
    return {
      id: id, label: label, mass: mass, prevMass: mass,
      color: color, kind: kind, depth: depth || 0,
      angle: Math.random() * TAU,
      vel: (Math.random() - 0.5) * 0.003,
      orbit: 0,        // radius from center
      thick: 0,         // arc thickness
      arcLen: 0,        // arc sweep (radians)
      opacity: 0,       // fade in
      flash: 1.0,       // change flash
      children: [],     // sub-rings (regions under countries)
      grinding: false   // collision state
    };
  }

  /* ═══ Parse dashboard data into rings ═══ */
  function ingest(d) {
    if (!d) return;
    var incoming = [];
    var total = d.total_requests || 1;
    lastTotal = total;

    // Layer 0: ASN types (inner rings)
    var asn = d.asn_types || {};
    var asnT = 0;
    for (var k in asn) asnT += asn[k];
    asnT = asnT || 1;
    for (var t in asn) {
      if (!asn[t]) continue;
      incoming.push(R('a_' + t, t, asn[t], ASN_C[t] || '#6e7681', 'asn', 0));
    }

    // Layer 1: Countries (outer rings)
    var geo = d.geography || [];
    for (var i = 0; i < geo.length; i++) {
      var g = geo[i];
      if (!g.requests) continue;
      var cr = R('c_' + g.country, g.country, g.requests,
                  CC_C[g.country] || '#58a6ff', 'country', 1);
      // Layer 2: Regions (sub-rings, only drawn when country is hovered)
      var regions = g.regions || [];
      for (var j = 0; j < regions.length; j++) {
        var rg = regions[j];
        if (!rg.requests) continue;
        cr.children.push(R(
          'r_' + g.country + '_' + rg.region, rg.region,
          rg.requests, CC_C[g.country] || '#58a6ff', 'region', 2
        ));
      }
      incoming.push(cr);
    }

    // Merge: preserve position state from existing rings
    for (var n = 0; n < incoming.length; n++) {
      var nr = incoming[n];
      var ex = null;
      for (var e = 0; e < rings.length; e++) {
        if (rings[e].id === nr.id) { ex = rings[e]; break; }
      }
      if (ex) {
        ex.prevMass = ex.mass;
        var delta = nr.mass - ex.mass;
        ex.mass = nr.mass;
        ex.label = nr.label;
        ex.children = nr.children;
        // Mass change → velocity nudge (grinding)
        if (Math.abs(delta) > 0) {
          ex.vel += delta * 0.000005;
          ex.flash = Math.min(1, ex.flash + 0.6);
        }
      } else {
        rings.push(nr);
      }
    }

    // Fade out dead rings
    var alive = {};
    for (var m = 0; m < incoming.length; m++) alive[incoming[m].id] = true;
    for (var q = rings.length - 1; q >= 0; q--) {
      if (!alive[rings[q].id]) {
        rings[q].opacity -= 0.02;
        if (rings[q].opacity <= 0) rings.splice(q, 1);
      }
    }

    topoSort();
  }

  /* ═══ Topo-sort: rings find their own order ═══ */
  function topoSort() {
    // Sort within each kind by mass (descending)
    // This IS the topo-sort — heaviest ring gets the prime position
    rings.sort(function (a, b) {
      if (a.kind !== b.kind) {
        // asn inner, country outer
        if (a.kind === 'asn') return -1;
        if (b.kind === 'asn') return 1;
        return 0;
      }
      return b.mass - a.mass;
    });

    // Assign orbit radii based on sorted position
    if (!canvas) return;
    var dpr = window.devicePixelRatio || 1;
    var maxR = Math.min(canvas.width / dpr, canvas.height / dpr) / 2 - 16;

    var asnRings = [], ccRings = [];
    for (var c = 0; c < rings.length; c++) {
      if (rings[c].kind === 'asn') asnRings.push(rings[c]);
      else ccRings.push(rings[c]);
    }

    // ASN tier total (for relative sizing within tier)
    var asnTotal = 0;
    for (var a = 0; a < asnRings.length; a++) asnTotal += asnRings[a].mass;
    asnTotal = asnTotal || 1;

    // Country tier total
    var ccTotal = 0;
    for (var b = 0; b < ccRings.length; b++) ccTotal += ccRings[b].mass;
    ccTotal = ccTotal || 1;

    // ASN rings: inner orbit (20-45% of maxR)
    // Sized relative to their own tier total so they fill the space
    for (var ai = 0; ai < asnRings.length; ai++) {
      var ar = asnRings[ai];
      var afrac = ar.mass / asnTotal;
      ar.orbit = maxR * (0.2 + (ai / Math.max(1, asnRings.length)) * 0.25);
      ar.thick = Math.max(4, afrac * maxR * 0.12);
      ar.arcLen = Math.max(0.2, afrac * TAU * 0.8);
    }

    // Country rings: outer orbit (55-92% of maxR)
    for (var ci = 0; ci < ccRings.length; ci++) {
      var cr = ccRings[ci];
      var cfrac = cr.mass / ccTotal;
      cr.orbit = maxR * (0.55 + (ci / Math.max(1, ccRings.length)) * 0.37);
      cr.thick = Math.max(4, cfrac * maxR * 0.15);
      cr.arcLen = Math.max(0.15, cfrac * TAU * 0.7);
    }
  }

  /* ═══ Hex alpha helper ═══ */
  function ha(hex, a) {
    return hex + Math.floor(Math.max(0, Math.min(1, a)) * 255)
                     .toString(16).padStart(2, '0');
  }

  /* ═══ Draw one frame ═══ */
  function draw() {
    if (!ctx || !canvas) return;
    var dpr = window.devicePixelRatio || 1;
    var W = canvas.width / dpr, H = canvas.height / dpr;
    var cx = W / 2, cy = H / 2;

    ctx.clearRect(0, 0, W, H);
    frame++;

    // Physics: update angles, handle collisions
    for (var i = 0; i < rings.length; i++) {
      var r = rings[i];

      // Spin: ASN clockwise (stator), country counter-clockwise (rotor)
      var baseSpin = r.kind === 'asn' ? 0.004 : -0.002;
      r.vel += (baseSpin - r.vel) * 0.008;
      r.angle = (r.angle + r.vel) % TAU;
      if (r.angle < 0) r.angle += TAU;

      // Fade in
      r.opacity = Math.min(1, r.opacity + 0.03);
      // Decay flash
      r.flash *= 0.97;
      r.grinding = false;
    }

    // Collision detection — rings grinding
    for (var a = 0; a < rings.length; a++) {
      for (var b = a + 1; b < rings.length; b++) {
        if (rings[a].kind !== rings[b].kind) continue;
        var da = rings[a].angle - rings[b].angle;
        da = Math.abs(((da + PI) % TAU + TAU) % TAU - PI);
        var dr = Math.abs(rings[a].orbit - rings[b].orbit);
        if (da < 0.25 && dr < 15) {
          // GRIND — exchange angular velocity, flash
          var tmp = rings[a].vel;
          rings[a].vel = rings[b].vel * 0.85;
          rings[b].vel = tmp * 0.85;
          rings[a].grinding = true;
          rings[b].grinding = true;
          rings[a].flash = Math.min(1, rings[a].flash + 0.3);
          rings[b].flash = Math.min(1, rings[b].flash + 0.3);
        }
      }
    }

    // Draw: faint orbit guidelines
    ctx.setLineDash([2, 6]);
    ctx.lineWidth = 0.5;
    ctx.strokeStyle = '#21262d';
    var maxR = Math.min(W, H) / 2 - 20;
    for (var g = 0.25; g <= 0.9; g += 0.15) {
      ctx.beginPath();
      ctx.arc(cx, cy, maxR * g, 0, TAU);
      ctx.stroke();
    }
    ctx.setLineDash([]);

    // Draw rings
    for (var j = 0; j < rings.length; j++) {
      var rr = rings[j];
      var alpha = rr.opacity * (0.4 + rr.flash * 0.6);
      var isHov = hovered === rr.id;

      // Main arc
      ctx.beginPath();
      ctx.arc(cx, cy, rr.orbit, rr.angle - rr.arcLen / 2, rr.angle + rr.arcLen / 2);
      ctx.lineWidth = rr.thick * (isHov ? 1.4 : 1);
      ctx.lineCap = 'round';
      ctx.strokeStyle = ha(rr.color, alpha);
      ctx.stroke();

      // Grinding glow
      if (rr.grinding || rr.flash > 0.2) {
        ctx.beginPath();
        ctx.arc(cx, cy, rr.orbit, rr.angle - rr.arcLen / 2, rr.angle + rr.arcLen / 2);
        ctx.lineWidth = rr.thick * 2.5;
        ctx.strokeStyle = ha(rr.color, rr.flash * 0.15);
        ctx.stroke();
      }

      // Label at leading edge
      var lAngle = rr.angle + rr.arcLen / 2 + 0.05;
      var lr = rr.orbit + rr.thick + 6;
      var lx = cx + lr * Math.cos(lAngle);
      var ly = cy + lr * Math.sin(lAngle);

      var fontSize = Math.max(8, Math.min(12, rr.thick * 0.9));
      ctx.font = (isHov ? 'bold ' : '') + fontSize + 'px monospace';
      ctx.fillStyle = ha(rr.color, Math.min(1, alpha + 0.3));
      ctx.textAlign = (lAngle % TAU > PI / 2 && lAngle % TAU < PI * 1.5) ? 'right' : 'left';
      ctx.textBaseline = 'middle';
      ctx.fillText(rr.label, lx, ly);

      // Percentage below label
      var pct = Math.round(rr.mass / lastTotal * 100);
      if (pct > 0) {
        ctx.font = '7px monospace';
        ctx.fillStyle = '#6e768166';
        ctx.fillText(pct + '%', lx, ly + fontSize * 0.8);
      }

      // Draw child rings when hovered
      if (isHov && rr.children.length) {
        for (var ci = 0; ci < rr.children.length; ci++) {
          var ch = rr.children[ci];
          var childOrbit = rr.orbit - rr.thick - 4 - ci * 6;
          var childArc = Math.max(0.08, (ch.mass / rr.mass) * rr.arcLen);
          var childAngle = rr.angle - rr.arcLen / 2 + (ci / rr.children.length) * rr.arcLen;
          ctx.beginPath();
          ctx.arc(cx, cy, childOrbit, childAngle, childAngle + childArc);
          ctx.lineWidth = 2;
          ctx.lineCap = 'round';
          ctx.strokeStyle = ha(rr.color, 0.5);
          ctx.stroke();
          ctx.font = '7px monospace';
          ctx.fillStyle = ha(rr.color, 0.5);
          var clx = cx + (childOrbit + 8) * Math.cos(childAngle + childArc / 2);
          var cly = cy + (childOrbit + 8) * Math.sin(childAngle + childArc / 2);
          ctx.fillText(ch.label, clx, cly);
        }
      }
    }

    // Center info
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.font = '8px monospace';
    ctx.fillStyle = '#484f5866';
    ctx.fillText(rings.length + ' ring' + (rings.length !== 1 ? 's' : ''), cx, cy - 5);
    ctx.fillText('topo-sorting', cx, cy + 5);
  }

  /* ═══ Animation loop ═══ */
  function tick() {
    draw();
    animId = requestAnimationFrame(tick);
  }

  /* ═══ Hit test for hover ═══ */
  function hitTest(mx, my) {
    if (!canvas) return null;
    var rect = canvas.getBoundingClientRect();
    var x = (mx - rect.left) * (canvas.width / rect.width);
    var y = (my - rect.top) * (canvas.height / rect.height);
    var cx = canvas.width / 2, cy = canvas.height / 2;
    var dist = Math.sqrt((x - cx) * (x - cx) + (y - cy) * (y - cy));
    var angle = Math.atan2(y - cy, x - cx);
    if (angle < 0) angle += TAU;

    for (var i = 0; i < rings.length; i++) {
      var r = rings[i];
      if (Math.abs(dist - r.orbit) > r.thick * 1.5) continue;
      var da = angle - r.angle;
      da = ((da + PI) % TAU + TAU) % TAU - PI;
      if (Math.abs(da) < r.arcLen / 2 + 0.1) return r.id;
    }
    return null;
  }

  /* ═══ Mount: replace static bars ═══ */
  function mount() {
    var geo = document.getElementById('d-geo');
    if (!geo) return false;
    if (mounted) return true;

    // Create canvas — make it square-ish so rings fill the space
    canvas = document.createElement('canvas');
    canvas.id = 'ring-sort-canvas';
    var w = Math.max(280, Math.min(420, geo.offsetWidth || 300));
    var h = w; // square canvas = circular rings fill it
    var dpr = window.devicePixelRatio || 1;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    canvas.style.cssText = 'width:' + w + 'px;height:' + h + 'px;display:block;margin:0 auto;' +
      'position:relative;z-index:4;background:rgba(13,17,23,0.92);border-radius:50%;' +
      'border:1px solid #21262d44;box-shadow:0 0 20px rgba(88,166,255,0.05);';
    ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    ctx = canvas.getContext('2d');

    // Insert before the static geo div
    geo.parentNode.insertBefore(canvas, geo);

    // Hide the static bars (keep them in DOM for fallback / screen readers)
    geo.style.display = 'none';

    // Hover interaction
    canvas.addEventListener('mousemove', function (e) {
      hovered = hitTest(e.clientX, e.clientY);
      canvas.style.cursor = hovered ? 'pointer' : 'default';
    });
    canvas.addEventListener('mouseleave', function () { hovered = null; });

    mounted = true;
    tick();
    return true;
  }

  /* ═══ Resize ═══ */
  window.addEventListener('resize', function () {
    if (!canvas || !ctx) return;
    var geo = document.getElementById('d-geo');
    var w = Math.max(280, Math.min(420, (geo ? geo.offsetWidth : 300)));
    var h = w;
    var dpr = window.devicePixelRatio || 1;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    topoSort();
  });

  /* ═══ Fetch data ═══ */
  function poll() {
    fetch('/dashboard.json', { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) { if (d) ingest(d); })
      .catch(function () {});
  }

  /* ═══ Init ═══ */
  function init() {
    // Wait for hud-core to create #d-geo first
    var tries = 0;
    var iv = setInterval(function () {
      tries++;
      if (mount() || tries > 20) {
        clearInterval(iv);
        poll();
        // Re-poll at π² seconds (~ 9.87s), offset from hud-core's 8s
        setInterval(poll, Math.round(PI * PI * 1000));
      }
    }, 500);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  /* ═══ Public API ═══ */
  window.RingSortGeo = {
    rings:    function () { return rings; },
    ingest:   ingest,
    topoSort: topoSort,
    poll:     poll
  };
})();
