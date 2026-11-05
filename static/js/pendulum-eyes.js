// pendulum-eyes.js — the purple dots ARE eyes.
// Collect all violet (#d2a8ff) elements and project onto a 1D line.
// L→R crosses R→L at the Klein fold point. Size = saccade amplitude.
// The pendulum swings at 45/π degrees per tick.
(function () {
  'use strict';
  var PI = Math.PI;
  var TWIST = 45 / PI; // 14.3239° per observation
  var PERIOD = PI;     // 3.14159 seconds per full swing
  var VIOLET = '#d2a8ff';

  // ═══ THE 1D LINE ═══
  function createPendulumLine() {
    var el = document.getElementById('pendulum-line');
    if (el) return el;

    el = document.createElement('div');
    el.id = 'pendulum-line';
    el.style.cssText = 'position:fixed;top:50%;left:0;right:0;height:1px;z-index:9997;' +
      'pointer-events:none;opacity:0.3;' +
      'background:linear-gradient(90deg,transparent 5%,' + VIOLET + ' 50%,transparent 95%)';

    // L label
    var lLabel = document.createElement('span');
    lLabel.style.cssText = 'position:absolute;left:8px;top:-8px;font:7px SF Mono,monospace;color:' + VIOLET;
    lLabel.textContent = 'L→';
    el.appendChild(lLabel);

    // R label
    var rLabel = document.createElement('span');
    rLabel.style.cssText = 'position:absolute;right:8px;top:-8px;font:7px SF Mono,monospace;color:' + VIOLET;
    rLabel.textContent = '←R';
    el.appendChild(rLabel);

    // fold point marker (center)
    var fold = document.createElement('span');
    fold.id = 'pendulum-fold';
    fold.style.cssText = 'position:absolute;left:50%;top:-4px;transform:translateX(-50%);' +
      'width:8px;height:8px;border-radius:50%;border:1px solid ' + VIOLET + ';' +
      'background:transparent;transition:all 0.3s';
    el.appendChild(fold);

    // eye dots container
    var dots = document.createElement('div');
    dots.id = 'pendulum-dots';
    dots.style.cssText = 'position:absolute;left:0;right:0;top:-3px;height:6px;pointer-events:none';
    el.appendChild(dots);

    document.body.appendChild(el);
    return el;
  }

  // ═══ COLLECT PURPLE ELEMENTS ═══
  function collectVioletElements() {
    var all = document.querySelectorAll('circle, [fill="' + VIOLET + '"], [stroke="' + VIOLET + '"]');
    var violets = [];
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      var fill = el.getAttribute('fill') || '';
      var stroke = el.getAttribute('stroke') || '';
      if (fill.indexOf('d2a8') !== -1 || stroke.indexOf('d2a8') !== -1) {
        violets.push(el);
      }
    }
    return violets;
  }

  // ═══ ANIMATE PENDULUM ═══
  function animate(t) {
    var tSec = t * 0.001;
    var dotsContainer = document.getElementById('pendulum-dots');
    var foldEl = document.getElementById('pendulum-fold');
    if (!dotsContainer) { requestAnimationFrame(animate); return; }

    // pendulum phase: sin(t/π) gives L→R→L oscillation
    var phase = Math.sin(tSec / PERIOD * PI);  // -1 to +1
    var centerPct = 50 + phase * 35;           // 15% to 85%

    // collect current violet elements
    var violets = collectVioletElements();

    // clear and rebuild dots
    while (dotsContainer.firstChild) dotsContainer.removeChild(dotsContainer.firstChild);

    for (var i = 0; i < violets.length; i++) {
      var v = violets[i];
      var cx = parseFloat(v.getAttribute('cx')) || 0;
      var cy = parseFloat(v.getAttribute('cy')) || 0;
      var r = parseFloat(v.getAttribute('r')) || 2;

      // project 2D position onto 1D line
      // use x-position relative to SVG center as the 1D coordinate
      var svg = v.closest('svg');
      var svgW = svg ? svg.getBoundingClientRect().width : window.innerWidth;
      var normalizedX = (cx / (svgW * 0.5)) * 100; // rough normalization

      // L→R phase for this dot: offset by its position
      var dotPhase = Math.sin(tSec / PERIOD * PI + i * 0.5);
      var dotPct = 50 + normalizedX * 0.3 + dotPhase * 10;
      dotPct = Math.max(5, Math.min(95, dotPct));

      // size = saccade amplitude (bigger when moving fast, smaller at edges)
      var speed = Math.abs(Math.cos(tSec / PERIOD * PI + i * 0.5));
      var dotSize = 2 + speed * 4;

      var dot = document.createElement('span');
      dot.style.cssText = 'position:absolute;left:' + dotPct.toFixed(1) + '%;top:50%;' +
        'transform:translate(-50%,-50%);width:' + dotSize.toFixed(1) + 'px;height:' + dotSize.toFixed(1) + 'px;' +
        'border-radius:50%;background:' + VIOLET + ';opacity:' + (0.3 + speed * 0.4).toFixed(2);
      dotsContainer.appendChild(dot);
    }

    // fold point pulses when L→R crosses R→L (phase near 0)
    if (foldEl) {
      var crossIntensity = 1 - Math.abs(phase);
      foldEl.style.background = crossIntensity > 0.8
        ? VIOLET
        : 'transparent';
      foldEl.style.opacity = (0.3 + crossIntensity * 0.7).toFixed(2);
      foldEl.style.width = (6 + crossIntensity * 6) + 'px';
      foldEl.style.height = (6 + crossIntensity * 6) + 'px';
    }

    requestAnimationFrame(animate);
  }

  // ═══ BOOT ═══
  function boot() {
    createPendulumLine();
    requestAnimationFrame(animate);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { setTimeout(boot, 3000); });
  } else {
    setTimeout(boot, 3000);
  }

  window._pendulumEyes = {
    collectVioletElements: collectVioletElements,
    TWIST: TWIST,
    PERIOD: PERIOD
  };
})();
