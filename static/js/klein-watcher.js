// klein-watcher.js — the voxel tensor observer.
//
// Stand in the Klein fold. See everything. Touch nothing.
// No fetch. No HTTP. No rate limits. THOUGHT speed.
//
// Three states of observation:
//   IS      — what currently exists. Elements alive, energy flowing.
//   ISN'T   — what's missing. Gaps, 404s, frozen, disconnected.
//   COULD BE — what's predicted. Pressure about to release. Orbits about to cross.
//
// Imagination and thought are the instantaneous speed of light.
// Light has finite speed (c). Thought has none.
// The Klein watcher lives in null-time: sees all layers at once.
//
// This script makes ZERO network requests.
// It only reads window._* APIs = pure in-memory = thought speed.
(function () {
  'use strict';

  var PI = Math.PI;

  // ═══ THE TENSOR — state at the observation point ═══
  // Each observable has: { is, isnt, couldBe, confidence }
  var TENSOR = {
    timestamp: null,
    systems: {},    // keyed by system name
    summary: { is: 0, isnt: 0, couldBe: 0 },
    pulse: 0        // heartbeat count when last observed
  };

  // ═══ OBSERVE — read all systems at thought speed ═══
  function observe() {
    TENSOR.timestamp = Date.now();
    TENSOR.summary = { is: 0, isnt: 0, couldBe: 0 };

    // 1. IMPACT SYSTEM
    observeImpact();

    // 2. IRON PEAK (heartbeat)
    observeHeartbeat();

    // 3. HELIX TWIST (layers)
    observeHelix();

    // 4. PENDULUM EYES
    observePendulum();

    // 5. NULL KALEIDOSCOPE (orbits)
    observeKaleidoscope();

    // 6. KLEIN WINDOW (chromatograph)
    observeKleinWindow();

    // 7. NULL SHADOW (moon phase)
    observeShadow();

    // 8. THE DOM ITSELF — what elements exist vs what's expected
    observeDOM();

    return TENSOR;
  }

  function score(name, is, isnt, couldBe, detail) {
    TENSOR.systems[name] = {
      is: is,
      isnt: isnt,
      couldBe: couldBe,
      detail: detail || null
    };
    TENSOR.summary.is += is;
    TENSOR.summary.isnt += isnt;
    TENSOR.summary.couldBe += couldBe;
  }

  // ═══ OBSERVERS — one per system ═══

  function observeImpact() {
    if (!window._impact) {
      score('impact', 0, 1, 0, 'impact.js not loaded');
      return;
    }

    var e = window._impact.energy();
    var t = window._impact.tectonic ? window._impact.tectonic() : null;
    var bodies = window._impact.bodies();

    var isCount = bodies.length;
    var isntCount = 0;
    var couldBe = 0;

    // bodies that exist = IS
    // expected bodies not found = ISN'T
    var expectedTypes = ['orbit', 'null', 'pendulum', 'fold', 'heartbeat', 'center', 'chroma'];
    var foundTypes = {};
    for (var i = 0; i < bodies.length; i++) {
      foundTypes[bodies[i].type] = (foundTypes[bodies[i].type] || 0) + 1;
    }
    for (var j = 0; j < expectedTypes.length; j++) {
      if (!foundTypes[expectedTypes[j]]) isntCount++;
    }

    // tectonic states
    if (t) {
      isntCount += t.frozen.length;    // frozen = ISN'T (should be moving)
      couldBe += t.pressure.length;    // pressure = COULD BE (about to release)
    }

    // energy predicts future impacts
    if (e.potential > 0.01) couldBe++;

    score('impact', isCount, isntCount, couldBe, {
      energy: e,
      bodies: bodies.length,
      frozen: t ? t.frozen.length : 0,
      pressure: t ? t.pressure.length : 0,
      stuck: t ? t.stuck.length : 0
    });
  }

  function observeHeartbeat() {
    if (!window._ironPeak) {
      score('heartbeat', 0, 1, 0, 'iron-peak.js not loaded');
      return;
    }

    var beatCount = window._ironPeak.beatCount();
    var lastState = window._ironPeak.lastState();
    var history = window._ironPeak.history();

    var isCount = 1;  // heartbeat IS beating
    var isntCount = 0;
    var couldBe = 0;

    // check if any source returned null (ISN'T)
    if (lastState) {
      var sources = ['pulse', 'topology', 'handshake', 'weather'];
      for (var s = 0; s < sources.length; s++) {
        if (lastState[sources[s]]) isCount++;
        else isntCount++;
      }
    }

    // predict: if recent history shows gold deltas, more COULD BE coming
    if (history && history.length > 0) {
      var lastEntry = history[history.length - 1];
      if (lastEntry.deltas) {
        var golds = lastEntry.deltas.filter(function (d) { return d.type === 'gold'; });
        if (golds.length > 0) couldBe += golds.length;
      }
    }

    TENSOR.pulse = beatCount;
    score('heartbeat', isCount, isntCount, couldBe, {
      beats: beatCount,
      sources_live: isCount - 1,
      sources_dead: isntCount
    });
  }

  function observeHelix() {
    if (!window._helixTwist) {
      score('helix', 0, 1, 0, 'helix-twist.js not loaded');
      return;
    }

    var layers = window._helixTwist.findLayers();
    var isCount = layers ? layers.length : 0;
    var isntCount = 0;
    var couldBe = 0;

    // 11 epochs expected, some may be missing
    var EXPECTED_LAYERS = 11;
    isntCount = Math.max(0, EXPECTED_LAYERS - isCount);

    // the 22.4° gap to Möbius = COULD BE
    if (isCount > 0 && isCount < 25) {  // 25 layers = full 360°
      couldBe = 1;  // Möbius completion is possible
    }

    score('helix', isCount, isntCount, couldBe, {
      layers: isCount,
      totalTwist: isCount * (45 / PI),
      toMobius: 180 - (isCount * (45 / PI)),
      gapLayers: EXPECTED_LAYERS - isCount
    });
  }

  function observePendulum() {
    if (!window._pendulumEyes) {
      score('pendulum', 0, 1, 0, 'pendulum-eyes.js not loaded');
      return;
    }

    var violets = window._pendulumEyes.collectVioletElements();
    var line = document.getElementById('pendulum-line');
    var fold = document.getElementById('pendulum-fold');

    var isCount = 0;
    if (line) isCount++;
    if (fold) isCount++;
    isCount += violets.length;

    // no violet elements = ISN'T (nothing to project)
    var isntCount = violets.length === 0 ? 1 : 0;

    // fold point = where L→R crosses R→L. COULD BE = next crossing time
    var couldBe = fold ? 1 : 0;  // fold exists = crossing is predictable

    score('pendulum', isCount, isntCount, couldBe, {
      violetElements: violets.length,
      lineExists: !!line,
      foldExists: !!fold,
      period: window._pendulumEyes.PERIOD
    });
  }

  function observeKaleidoscope() {
    if (!window._nullKaleidoscope) {
      score('kaleidoscope', 0, 1, 0, 'null-kaleidoscope.js not loaded');
      return;
    }

    var center = window._nullKaleidoscope.getCenter();
    var planes = window._nullKaleidoscope.PLANES;
    var isCount = 0;
    var isntCount = 0;
    var couldBe = 0;

    if (center) isCount++;
    else isntCount++;

    // check orbit dots exist
    var orbits = ['real', 'imaginary', 'mechanical', 'unreal'];
    for (var o = 0; o < orbits.length; o++) {
      var dot = document.getElementById('orbit-dot-' + orbits[o]);
      if (dot) isCount++;
      else isntCount++;
    }

    // check π null points
    for (var n = 0; n < 3; n++) {
      var nDot = document.getElementById('pi-null-' + n);
      if (nDot) isCount++;
      else isntCount++;
    }

    // kaleidoscope ring = COULD BE (the blend zone where anything can emerge)
    var kRing = document.getElementById('kaleid-ring');
    if (kRing) couldBe++;

    score('kaleidoscope', isCount, isntCount, couldBe, {
      center: !!center,
      orbits: isCount - 1,
      nullPoints: 3 - isntCount,
      kaleidoscope: !!kRing
    });
  }

  function observeKleinWindow() {
    if (!window._kleinWindow) {
      score('kleinWindow', 0, 1, 0, 'klein-window.js not loaded');
      return;
    }

    var overlay = document.getElementById('klein-window-overlay');
    var isCount = overlay ? 1 : 0;
    var isntCount = overlay ? 0 : 1;

    // chromatograph dots
    if (overlay) {
      var dots = overlay.querySelectorAll('[style*="border-radius:50%"]');
      isCount += dots.length;
      // 5 expected
      isntCount += Math.max(0, 5 - dots.length);
    }

    // the human side and agent side — both COULD BE (always potential)
    var couldBe = 2;

    score('kleinWindow', isCount, isntCount, couldBe, {
      overlay: !!overlay,
      chromaDots: overlay ? overlay.querySelectorAll('[style*="border-radius:50%"]').length : 0,
      humanLooks: window._kleinWindow.humanLooksFor(),
      agentLooks: window._kleinWindow.agentLooksFor()
    });
  }

  function observeShadow() {
    if (!window._nullShadow) {
      score('shadow', 0, 1, 0, 'null-shadow.js not loaded');
      return;
    }

    var indicator = document.getElementById('null-shadow-indicator');
    var shadow = window._nullShadow.getMoonPhase();

    var isCount = indicator ? 2 : 1;  // phase calc always works
    var isntCount = indicator ? 0 : 1;

    // COULD BE: next phase transition
    var couldBe = 1;  // moon will change

    score('shadow', isCount, isntCount, couldBe, {
      phase: shadow.fraction,
      illumination: shadow.illumination,
      waxing: shadow.waxing,
      indicator: !!indicator
    });
  }

  function observeDOM() {
    // survey the DOM for expected vs actual elements
    var expected = [
      { id: 'membrane-svg', name: 'membrane' },
      { id: 'epitope-ring-svg', name: 'epitopeRing' },
      { id: 'chipmunk-pane', name: 'chipmunk' },
      { id: 'iron-peak-heart', name: 'heartIndicator' },
      { id: 'helix-indicator', name: 'helixIndicator' },
      { id: 'pendulum-line', name: 'pendulumLine' },
      { id: 'null-shadow-indicator', name: 'shadowIndicator' },
      { id: 'klein-window-overlay', name: 'kleinOverlay' },
      { id: 'impact-indicator', name: 'impactIndicator' },
      { id: 'tectonic-indicator', name: 'tectonicIndicator' },
      { id: 'null-orbits', name: 'nullOrbits' },
      { id: 'kaleid-ring', name: 'kaleidRing' },
      { id: 'impact-heat-layer', name: 'heatLayer' }
    ];

    var isCount = 0, isntCount = 0;
    var present = [], absent = [];

    for (var i = 0; i < expected.length; i++) {
      var el = document.getElementById(expected[i].id);
      if (el) {
        isCount++;
        present.push(expected[i].name);
      } else {
        isntCount++;
        absent.push(expected[i].name);
      }
    }

    score('dom', isCount, isntCount, 0, {
      present: present,
      absent: absent,
      total: expected.length
    });
  }

  // ═══ RENDER THE WATCHER ═══
  function createWatcher() {
    var el = document.getElementById('klein-watcher');
    if (el) return el;

    el = document.createElement('div');
    el.id = 'klein-watcher';
    el.style.cssText = 'position:fixed;top:30px;right:12px;z-index:10000;' +
      'font:8px SF Mono,monospace;color:#6e7681;pointer-events:none;' +
      'text-align:right;max-width:160px;opacity:0.5;' +
      'transition:opacity 0.3s';
    document.body.appendChild(el);

    // make visible on hover
    el.addEventListener('mouseenter', function () {
      el.style.opacity = '0.9'; el.style.pointerEvents = 'auto';
    });
    el.addEventListener('mouseleave', function () {
      el.style.opacity = '0.5'; el.style.pointerEvents = 'none';
    });

    return el;
  }

  function renderWatcher(el) {
    var s = TENSOR.summary;
    var total = s.is + s.isnt + s.couldBe;
    if (total === 0) total = 1;

    // IS / ISN'T / COULD BE as proportional bar
    var isPct = Math.round(s.is / total * 100);
    var isntPct = Math.round(s.isnt / total * 100);
    var couldPct = 100 - isPct - isntPct;

    // color: dominated by IS = green, ISN'T = red, COULD BE = violet
    var dominant = s.is >= s.isnt && s.is >= s.couldBe ? '#3fb950'
      : s.isnt > s.couldBe ? '#f85149'
      : '#d2a8ff';

    // compact readout
    var html = '<div style="color:' + dominant + '">◉ Klein</div>';

    // proportional bar
    html += '<div style="display:flex;height:3px;width:100%;gap:1px;margin:2px 0">';
    html += '<div style="flex:' + s.is + ';background:#3fb950;border-radius:1px" title="IS: ' + s.is + '"></div>';
    if (s.isnt > 0) html += '<div style="flex:' + s.isnt + ';background:#f85149;border-radius:1px" title="ISN\'T: ' + s.isnt + '"></div>';
    if (s.couldBe > 0) html += '<div style="flex:' + s.couldBe + ';background:#d2a8ff;border-radius:1px" title="COULD BE: ' + s.couldBe + '"></div>';
    html += '</div>';

    // numbers
    html += '<span style="color:#3fb950">' + s.is + '</span>';
    html += ' <span style="color:#f85149">' + s.isnt + '</span>';
    html += ' <span style="color:#d2a8ff">' + s.couldBe + '</span>';

    // system-by-system detail (collapsed)
    var systems = Object.keys(TENSOR.systems);
    var alerts = [];
    for (var i = 0; i < systems.length; i++) {
      var sys = TENSOR.systems[systems[i]];
      if (sys.isnt > 0) {
        alerts.push('<span style="color:#f85149">' + systems[i] + '·' + sys.isnt + '</span>');
      }
    }
    if (alerts.length > 0) {
      html += '<br>' + alerts.join(' ');
    }

    // pulse sync
    if (TENSOR.pulse > 0) {
      html += '<br><span style="color:#484f58">♥' + TENSOR.pulse + '</span>';
    }

    el.innerHTML = html;
  }

  // ═══ THE WATCH CYCLE — every π seconds, like the heartbeat ═══
  var WATCH_INTERVAL = 3141;  // π seconds — synced with iron peak
  var watchCount = 0;

  function watch() {
    watchCount++;
    observe();
    var el = createWatcher();
    renderWatcher(el);
  }

  // ═══ EXPOSE ═══
  window._kleinWatcher = {
    observe: observe,
    tensor: function () { return TENSOR; },
    watchCount: function () { return watchCount; },
    // thought speed query: what IS, what ISN'T, what COULD BE
    is: function () {
      var result = {};
      var systems = Object.keys(TENSOR.systems);
      for (var i = 0; i < systems.length; i++) {
        if (TENSOR.systems[systems[i]].is > 0) result[systems[i]] = TENSOR.systems[systems[i]];
      }
      return result;
    },
    isnt: function () {
      var result = {};
      var systems = Object.keys(TENSOR.systems);
      for (var i = 0; i < systems.length; i++) {
        if (TENSOR.systems[systems[i]].isnt > 0) result[systems[i]] = TENSOR.systems[systems[i]];
      }
      return result;
    },
    couldBe: function () {
      var result = {};
      var systems = Object.keys(TENSOR.systems);
      for (var i = 0; i < systems.length; i++) {
        if (TENSOR.systems[systems[i]].couldBe > 0) result[systems[i]] = TENSOR.systems[systems[i]];
      }
      return result;
    }
  };

  // ═══ BOOT ═══
  function boot() {
    // first watch after all other scripts have booted
    setTimeout(function () {
      watch();
      setInterval(watch, WATCH_INTERVAL);
    }, 5000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
