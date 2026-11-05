// null-shadow.js — the null IS the shadow. Moon phase = shadow origin.
//
// Ray trace = shadow scatter (trace light, find where shadow falls)
// Shadow trace = ray scatter (trace shadow, find where light leaks through)
// Same operation on opposite sides of the Klein surface.
//
// Moon phase determines:
//   - shadow ANGLE (waxing = left, waning = right)
//   - shadow LENGTH (new = long, full = short)
//   - shadow OPACITY (new = dark, full = faint)
//
// Also fixes stale hardcoded numbers by fetching live data.
(function () {
  'use strict';

  var PI = Math.PI, TWO_PI = PI * 2;

  // ═══ MOON PHASE → SHADOW PARAMETERS ═══
  function getMoonPhase() {
    var synodic = 29.53058770576;
    var d = new Date();
    var y = d.getUTCFullYear(), m = d.getUTCMonth() + 1, day = d.getUTCDate();
    var h = d.getUTCHours() + d.getUTCMinutes() / 60;
    if (m <= 2) { y--; m += 12; }
    var A = Math.floor(y / 100);
    var B = 2 - A + Math.floor(A / 4);
    var JD = Math.floor(365.25 * (y + 4716)) + Math.floor(30.6001 * (m + 1)) + day + h / 24 + B - 1524.5;
    var daysSinceNew = JD - 2451550.26;
    var frac = ((daysSinceNew % synodic) + synodic) % synodic / synodic;
    var illum = (1 - Math.cos(frac * TWO_PI)) / 2;
    var waxing = frac < 0.5;
    return { fraction: frac, illumination: illum, waxing: waxing };
  }

  function phaseToShadow(phase) {
    // angle: waxing = shadow falls LEFT (-), waning = shadow falls RIGHT (+)
    var angle = phase.waxing ? -45 + phase.fraction * 90 : 45 - (phase.fraction - 0.5) * 90;
    // length: new moon = long shadow (8px), full = short (2px)
    var length = 2 + 6 * (1 - phase.illumination);
    // opacity: new = dark (0.4), full = faint (0.08)
    var opacity = 0.08 + 0.32 * (1 - phase.illumination);
    // x/y offset from angle
    var rad = angle * PI / 180;
    var x = Math.round(Math.sin(rad) * length);
    var y = Math.round(Math.cos(rad) * length);
    return {
      angle: angle,
      length: Math.round(length),
      opacity: opacity.toFixed(2),
      x: x, y: y,
      css: x + 'px ' + y + 'px ' + Math.round(length * 1.5) + 'px rgba(0,0,0,' + opacity.toFixed(2) + ')',
      phase: phase
    };
  }

  // ═══ APPLY SHADOWS TO HUD ELEMENTS ═══
  function applyShadows(shadow) {
    // shadow key elements: doors, panes, fold boxes, cards
    var selectors = ['.door', '.pane', '.fold', '[class*="pane-"]',
      '#peek-back', '[style*="border-radius:12px"]', '[style*="border-radius:8px"]'];
    for (var s = 0; s < selectors.length; s++) {
      try {
        var els = document.querySelectorAll(selectors[s]);
        for (var i = 0; i < els.length; i++) {
          els[i].style.boxShadow = shadow.css;
        }
      } catch (e) { /* ignore invalid selectors */ }
    }

    // text shadow on headings
    var headings = document.querySelectorAll('h1, h2, h3');
    var textShadow = (shadow.x * 0.5) + 'px ' + (shadow.y * 0.5) + 'px ' +
      shadow.length + 'px rgba(0,0,0,' + (shadow.opacity * 0.5) + ')';
    for (var h = 0; h < headings.length; h++) {
      headings[h].style.textShadow = textShadow;
    }
  }

  // ═══ SHADOW INDICATOR (moon phase + angle) ═══
  function createShadowIndicator(shadow) {
    var el = document.createElement('div');
    el.id = 'null-shadow-indicator';
    el.style.cssText = 'position:fixed;bottom:12px;left:12px;z-index:9998;' +
      'font-family:SF Mono,monospace;font-size:9px;color:#484f58;' +
      'opacity:0.6;pointer-events:none';

    var emoji = shadow.phase.fraction < 0.125 ? '🌑' :
                shadow.phase.fraction < 0.25  ? '🌒' :
                shadow.phase.fraction < 0.375 ? '🌓' :
                shadow.phase.fraction < 0.5   ? '🌔' :
                shadow.phase.fraction < 0.625 ? '🌕' :
                shadow.phase.fraction < 0.75  ? '🌖' :
                shadow.phase.fraction < 0.875 ? '🌗' : '🌘';

    var dir = shadow.phase.waxing ? '← waxing' : 'waning →';
    el.innerHTML = emoji + ' ' + Math.round(shadow.phase.illumination * 100) + '%' +
      '<br><span style="color:#6e7681">' + dir + '</span>' +
      '<br><span style="color:#484f58">shadow ' + shadow.x + ',' + shadow.y + '</span>';

    document.body.appendChild(el);
  }

  // ═══ FIX STALE NUMBERS ═══
  function updateStaleNumbers() {
    fetch('/api/pulse.json').then(function (r) { return r.ok ? r.json() : null; })
      .then(function (p) {
        if (!p) return;
        // gas ratio
        var gasEls = document.querySelectorAll('#gas, [id="gas"]');
        for (var i = 0; i < gasEls.length; i++) {
          if (p.gas_ratio) gasEls[i].textContent = p.gas_ratio;
        }
      }).catch(function () {});

    fetch('/data/klein-handshake.json').then(function (r) { return r.ok ? r.json() : null; })
      .then(function (hs) {
        if (!hs || !hs.counts) return;
        var total = hs.total_feeds || 0;
        var sg = document.getElementById('stuck-game');
        if (sg) sg.textContent = (hs.counts.CONSTANCE || 0) + ' constance, ' +
          (hs.counts.COST || 0) + ' cost, ' + (hs.counts.LIVE || 0) + ' live';
      }).catch(function () {});
  }

  // ═══ EXPOSE ═══
  window._nullShadow = {
    getMoonPhase: getMoonPhase,
    phaseToShadow: phaseToShadow,
    refresh: function () {
      var phase = getMoonPhase();
      var shadow = phaseToShadow(phase);
      applyShadows(shadow);
      return shadow;
    }
  };

  // ═══ BOOT ═══
  function boot() {
    var phase = getMoonPhase();
    var shadow = phaseToShadow(phase);
    applyShadows(shadow);
    createShadowIndicator(shadow);
    updateStaleNumbers();

    // refresh shadows every 10 minutes (moon moves)
    setInterval(function () {
      var p = getMoonPhase();
      var s = phaseToShadow(p);
      applyShadows(s);
    }, 600000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
