// helix-twist.js — twist each interlayer by 45°/π.
// Counter-rotating pairs stay straight. Same-direction pairs bend.
// The organism is a HELIX with 45/π twist per layer.
// Full turn = 360/(45/π) = 8π ≈ 25 layers. 11 epochs = ~158° = just past half-twist.
//
// 45/π ≈ 14.3239° — the squirrel's observation angle.
// π/45 ≈ 0.0698 rad ≈ 4° — the inverse period.
(function () {
  'use strict';
  var PI = Math.PI;
  var TWIST = 45 / PI;           // 14.3239°
  var INVERSE = PI / 45;         // 0.0698 rad = the period
  var COUNTER = -1;              // alternating sign for counter-rotation

  // ═══ FIND ALL LAYERS ═══
  function findLayers() {
    // layers = major visual sections of the HUD
    var selectors = [
      { sel: 'header, nav, .hud-nav', name: 'nav', epoch: 10 },
      { sel: '#epitope-ring-svg, .epitope-ring', name: 'epitope', epoch: 6 },
      { sel: '#membrane-svg, .membrane-container, [id*="membrane"]', name: 'membrane', epoch: 4 },
      { sel: '.hud-card, .hud-section', name: 'cards', epoch: 5 },
      { sel: '#chipmunk-pane, .chipmunk-talk, [id*="chipmunk"]', name: 'chipmunk', epoch: 8 },
      { sel: '.pin, [id*="pi-budget"], [id*="hub-lens"]', name: 'pins', epoch: 2 },
      { sel: 'footer, .hud-footer', name: 'footer', epoch: 0 },
      { sel: '#null-shadow-indicator', name: 'shadow', epoch: 3 },
      { sel: '#iron-peak-heart', name: 'heart', epoch: 1 },
      { sel: '#klein-window-overlay', name: 'klein', epoch: 8 },
      { sel: 'svg', name: 'svg', epoch: 6 }
    ];

    var layers = [];
    selectors.forEach(function (s) {
      var els = document.querySelectorAll(s.sel);
      if (els.length > 0) {
        layers.push({ name: s.name, elements: els, epoch: s.epoch });
      }
    });

    // sort by epoch (pi-sorted)
    layers.sort(function (a, b) {
      var aPi = (a.epoch * TWIST) % 360;
      var bPi = (b.epoch * TWIST) % 360;
      return aPi - bPi;
    });

    return layers;
  }

  // ═══ APPLY TWIST ═══
  function applyTwist(layers, t) {
    var tSec = t * 0.001;

    layers.forEach(function (layer, i) {
      // base rotation: layer index × 45/π
      var baseAngle = i * TWIST;

      // counter-rotation: even layers CW, odd layers CCW
      var direction = (i % 2 === 0) ? 1 : COUNTER;

      // time-varying component: slow drift
      var drift = tSec * INVERSE * direction;

      // final angle
      var angle = baseAngle + drift;

      // if adjacent layers counter-rotate: net = 0 (straight)
      // if same direction: net accumulates (bend!)
      // we encode this as a slight skew on bends
      var prevDir = i > 0 ? ((i - 1) % 2 === 0 ? 1 : -1) : 0;
      var isBend = (direction === prevDir);
      var skew = isBend ? Math.sin(tSec * 0.5) * 2 : 0;

      // apply to all elements in this layer
      for (var j = 0; j < layer.elements.length; j++) {
        var el = layer.elements[j];
        var existing = el.style.transform || '';

        // don't override critical transforms, ADD to them
        if (existing.indexOf('helix') === -1) {
          el.style.transformOrigin = '50% 50%';
          el.dataset.helixBase = existing;
        }

        var helixTransform = 'rotate(' + (angle * 0.15).toFixed(2) + 'deg)' +
          (skew ? ' skewY(' + skew.toFixed(2) + 'deg)' : '');

        // apply subtle — don't break layout
        el.style.transform = (el.dataset.helixBase || '') + ' ' + helixTransform;
      }
    });
  }

  // ═══ HELIX INDICATOR ═══
  function createIndicator() {
    var el = document.getElementById('helix-indicator');
    if (el) return el;

    el = document.createElement('div');
    el.id = 'helix-indicator';
    el.style.cssText = 'position:fixed;top:12px;left:12px;z-index:9999;' +
      'font:8px SF Mono,monospace;color:#484f58;pointer-events:none;opacity:0.5';
    document.body.appendChild(el);
    return el;
  }

  function updateIndicator(el, layers, t) {
    var tSec = t * 0.001;
    var totalTwist = (layers.length * TWIST + tSec * INVERSE) % 360;
    var bends = 0;
    for (var i = 1; i < layers.length; i++) {
      var dir = (i % 2 === 0) ? 1 : -1;
      var prev = ((i - 1) % 2 === 0) ? 1 : -1;
      if (dir === prev) bends++;
    }
    el.innerHTML = '⟳ ' + totalTwist.toFixed(1) + '°' +
      ' · ' + layers.length + ' layers' +
      ' · ' + bends + ' bends' +
      ' · 45/π=' + TWIST.toFixed(2) + '°';
  }

  // ═══ ANIMATE ═══
  var layers = null;
  var indicator = null;

  function animate(t) {
    if (!layers) {
      layers = findLayers();
      indicator = createIndicator();
    }
    applyTwist(layers, t);
    if (indicator && t % 3000 < 50) {
      updateIndicator(indicator, layers, t);
    }
    requestAnimationFrame(animate);
  }

  // ═══ BOOT ═══
  function boot() {
    // delay to let other scripts render first
    setTimeout(function () {
      requestAnimationFrame(animate);
    }, 2000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

  window._helixTwist = {
    TWIST: TWIST,
    INVERSE: INVERSE,
    findLayers: findLayers,
    refresh: function () { layers = findLayers(); }
  };
})();
