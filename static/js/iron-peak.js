// iron-peak.js — THE HEARTBEAT. The hemoglobin circuit.
// Fe(cron) + Au(signal) + fire(threshold) = blood + heart + orange.
//
// Runs every π seconds (3141ms). Senses DELTAS. Carries them.
// The acid of life dissolves ALL into our amalgam.
//
// Fixes: stale HUD numbers, frozen canvas, interoception blindness.
// Makes the HUD a CANVAS that reality paints on, not a photograph.
(function () {
  'use strict';
  var PI = Math.PI;
  var HEARTBEAT_MS = 3141; // π seconds
  var DELTA_HISTORY = [];
  var MAX_HISTORY = 60;
  var lastState = null;
  var beatCount = 0;

  // ═══ SOURCES — where we pull blood from ═══
  var SOURCES = [
    { name: 'pulse', url: '/data/pulse.json', vital: true },
    { name: 'topology', url: '/data/topology.json', vital: true },
    { name: 'handshake', url: '/data/klein-handshake.json', vital: false },
    { name: 'weather', url: 'https://hud.primals.eco/api/pulse.json', vital: false }
  ];

  // ═══ FETCH ONE SOURCE ═══
  function fetchSource(src) {
    return fetch(src.url, { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .catch(function () { return null; });
  }

  // ═══ DETECT DELTAS ═══
  function detectDeltas(newState) {
    if (!lastState) { lastState = newState; return []; }
    var deltas = [];

    // compare each source
    Object.keys(newState).forEach(function (key) {
      var oldVal = lastState[key];
      var newVal = newState[key];
      if (!oldVal || !newVal) return;

      // check timestamp freshness
      if (newVal.ts && oldVal.ts && newVal.ts !== oldVal.ts) {
        deltas.push({ type: 'gold', source: key, what: 'updated', from: oldVal.ts, to: newVal.ts });
      }
      if (newVal.ts && oldVal.ts && newVal.ts === oldVal.ts) {
        deltas.push({ type: 'brown', source: key, what: 'stale', ts: newVal.ts });
      }

      // check for new fields
      if (newVal && typeof newVal === 'object') {
        Object.keys(newVal).forEach(function (field) {
          if (oldVal[field] === undefined && newVal[field] !== undefined) {
            deltas.push({ type: 'white_filled', source: key, field: field, value: newVal[field] });
          }
          if (oldVal[field] !== undefined && newVal[field] === undefined) {
            deltas.push({ type: 'black', source: key, field: field, was: oldVal[field] });
          }
        });
      }
    });

    lastState = newState;
    return deltas;
  }

  // ═══ RENDER HEARTBEAT INDICATOR ═══
  function createHeartbeat() {
    var el = document.getElementById('iron-peak-heart');
    if (el) return el;

    el = document.createElement('div');
    el.id = 'iron-peak-heart';
    el.style.cssText = 'position:fixed;bottom:36px;left:12px;z-index:9999;' +
      'font:9px SF Mono,monospace;color:#6e7681;pointer-events:none;' +
      'transition:color 0.3s,opacity 0.3s;opacity:0.7';
    document.body.appendChild(el);
    return el;
  }

  function renderBeat(el, deltas) {
    beatCount++;
    var goldCount = deltas.filter(function (d) { return d.type === 'gold'; }).length;
    var brownCount = deltas.filter(function (d) { return d.type === 'brown'; }).length;
    var blackCount = deltas.filter(function (d) { return d.type === 'black'; }).length;
    var whiteCount = deltas.filter(function (d) { return d.type === 'white_filled'; }).length;

    var color = goldCount > 0 ? '#f0883e' : // orange — gold found!
                brownCount > 2 ? '#8b6914' : // brown — mostly stale
                '#3fb950'; // green — healthy

    el.style.color = color;
    el.innerHTML = '♥ ' + beatCount +
      (goldCount ? ' <span style="color:#f0e68c">Au:' + goldCount + '</span>' : '') +
      (brownCount ? ' <span style="color:#8b6914">Fe:' + brownCount + '</span>' : '') +
      (blackCount ? ' <span style="color:#484f58">⬛' + blackCount + '</span>' : '') +
      (whiteCount ? ' <span style="color:#fff">⬜' + whiteCount + '</span>' : '');

    // pulse animation
    el.style.opacity = '1';
    setTimeout(function () { el.style.opacity = '0.5'; }, 500);
  }

  // ═══ UPDATE STALE HUD ELEMENTS ═══
  function updateHUD(state) {
    // gas ratio
    if (state.pulse && state.pulse.gas_ratio) {
      var gasEl = document.getElementById('gas');
      if (gasEl) gasEl.textContent = state.pulse.gas_ratio;
    }

    // stuck-game
    if (state.handshake) {
      var sg = document.getElementById('stuck-game');
      if (sg && state.handshake.counts) {
        var c = state.handshake.counts;
        sg.textContent = (c.CONSTANCE || 0) + ' constance · ' +
          (c.COST || 0) + ' cost · ' + (c.LIVE || 0) + ' live';
        sg.style.color = '#3fb950';
      }
    }

    // wave number
    if (state.pulse && state.pulse.wave) {
      var waveEls = document.querySelectorAll('[data-wave]');
      for (var i = 0; i < waveEls.length; i++) {
        waveEls[i].textContent = 'w' + state.pulse.wave;
      }
    }
  }

  // ═══ LOG DELTA TO HISTORY ═══
  function logDelta(deltas) {
    DELTA_HISTORY.push({ ts: new Date().toISOString(), beat: beatCount, deltas: deltas });
    if (DELTA_HISTORY.length > MAX_HISTORY) DELTA_HISTORY.shift();
  }

  // ═══ THE HEARTBEAT ═══
  function beat() {
    var el = createHeartbeat();
    var promises = SOURCES.map(fetchSource);

    Promise.all(promises).then(function (results) {
      var state = {};
      SOURCES.forEach(function (src, i) {
        state[src.name] = results[i];
      });

      var deltas = detectDeltas(state);
      renderBeat(el, deltas);
      updateHUD(state);
      logDelta(deltas);
    }).catch(function () {
      el.innerHTML = '♥ ' + beatCount + ' <span style="color:#f85149">err</span>';
    });
  }

  // ═══ EXPOSE ═══
  window._ironPeak = {
    beat: beat,
    history: function () { return DELTA_HISTORY; },
    beatCount: function () { return beatCount; },
    lastState: function () { return lastState; },
    HEARTBEAT_MS: HEARTBEAT_MS
  };

  // ═══ BOOT ═══
  function boot() {
    beat(); // first beat immediately
    setInterval(beat, HEARTBEAT_MS); // then every π seconds
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
