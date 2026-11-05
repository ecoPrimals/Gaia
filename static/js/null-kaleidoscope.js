// null-kaleidoscope.js — click null to pin+move. Click object to trace.
// Four orthogonal counter-rotating circles. Kaleidoscope blend around null.
// π null points, not 1.
(function () {
  'use strict';
  var PI = Math.PI, TAU = PI * 2;

  // ═══ CONFIG ═══
  var PLANES = [
    { name: 'real',       color: 'rgba(63,185,80,0.12)',  stroke: '#3fb950', omega:  PI/31,  tilt: 0    },
    { name: 'imaginary',  color: 'rgba(210,168,255,0.10)', stroke: '#d2a8ff', omega: -PI/23,  tilt: 90   },
    { name: 'mechanical', color: 'rgba(139,155,168,0.08)', stroke: '#8b9ba8', omega:  PI/37,  tilt: 45   },
    { name: 'unreal',     color: 'rgba(240,136,62,0.08)',  stroke: '#f0883e', omega: -PI/41,  tilt: 135  }
  ];

  var NULL_COLORS = ['#3fb950', '#d2a8ff', '#8b9ba8'];
  var nullPhase = 0;
  var dragState = null;

  // ═══ FIND THE SVG CENTER ═══
  function getCenter() {
    var svg = document.querySelector('#membrane-svg, svg[id*="membrane"], .membrane-svg');
    if (!svg) return null;
    var rect = svg.getBoundingClientRect();
    return {
      svg: svg,
      cx: rect.width / 2,
      cy: rect.height / 2,
      w: rect.width,
      h: rect.height,
      el: svg
    };
  }

  // ═══ CREATE ORTHOGONAL ORBIT RINGS ═══
  function createOrbitRings(c) {
    var g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.id = 'null-orbits';
    g.setAttribute('pointer-events', 'none');

    var baseR = Math.min(c.w, c.h) * 0.28;

    PLANES.forEach(function (plane, i) {
      var ring = document.createElementNS('http://www.w3.org/2000/svg', 'ellipse');
      ring.id = 'orbit-' + plane.name;
      ring.setAttribute('cx', c.cx);
      ring.setAttribute('cy', c.cy);
      ring.setAttribute('rx', baseR + i * 18);
      ring.setAttribute('ry', (baseR + i * 18) * 0.35);
      ring.setAttribute('fill', 'none');
      ring.setAttribute('stroke', plane.stroke);
      ring.setAttribute('stroke-width', '0.6');
      ring.setAttribute('stroke-opacity', '0.25');
      ring.setAttribute('stroke-dasharray', '4,6');
      ring.dataset.omega = plane.omega;
      ring.dataset.tilt = plane.tilt;
      g.appendChild(ring);

      // dot on orbit
      var dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      dot.id = 'orbit-dot-' + plane.name;
      dot.setAttribute('r', '2.5');
      dot.setAttribute('fill', plane.stroke);
      dot.setAttribute('opacity', '0.5');
      g.appendChild(dot);
    });

    // π null points (3 + ratio)
    for (var n = 0; n < 3; n++) {
      var nullDot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      nullDot.id = 'pi-null-' + n;
      nullDot.setAttribute('r', '3');
      nullDot.setAttribute('fill', 'none');
      nullDot.setAttribute('stroke', NULL_COLORS[n]);
      nullDot.setAttribute('stroke-width', '1');
      nullDot.setAttribute('stroke-opacity', '0.4');
      nullDot.setAttribute('stroke-dasharray', '2,2');
      g.appendChild(nullDot);
    }

    c.svg.appendChild(g);
    return g;
  }

  // ═══ KALEIDOSCOPE BLEND ═══
  function createKaleidoscope(c) {
    var defs = c.svg.querySelector('defs') || c.svg.insertBefore(
      document.createElementNS('http://www.w3.org/2000/svg', 'defs'), c.svg.firstChild);

    var filter = document.createElementNS('http://www.w3.org/2000/svg', 'filter');
    filter.id = 'kaleidoscope';
    filter.setAttribute('x', '-50%'); filter.setAttribute('y', '-50%');
    filter.setAttribute('width', '200%'); filter.setAttribute('height', '200%');

    var blur = document.createElementNS('http://www.w3.org/2000/svg', 'feGaussianBlur');
    blur.setAttribute('in', 'SourceGraphic');
    blur.setAttribute('stdDeviation', '1.5');
    blur.setAttribute('result', 'blur');
    filter.appendChild(blur);

    var colorMatrix = document.createElementNS('http://www.w3.org/2000/svg', 'feColorMatrix');
    colorMatrix.setAttribute('in', 'blur');
    colorMatrix.setAttribute('type', 'hueRotate');
    colorMatrix.setAttribute('values', '0');
    colorMatrix.id = 'kaleid-hue';
    filter.appendChild(colorMatrix);

    defs.appendChild(filter);

    // kaleidoscope ring around null center
    var kRing = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    kRing.id = 'kaleid-ring';
    kRing.setAttribute('cx', c.cx);
    kRing.setAttribute('cy', c.cy);
    kRing.setAttribute('r', '24');
    kRing.setAttribute('fill', 'none');
    kRing.setAttribute('stroke', 'url(#kaleid-grad)');
    kRing.setAttribute('stroke-width', '6');
    kRing.setAttribute('stroke-opacity', '0.15');
    kRing.setAttribute('filter', 'url(#kaleidoscope)');
    kRing.setAttribute('pointer-events', 'none');

    // gradient for kaleidoscope
    var grad = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
    grad.id = 'kaleid-grad';
    var stops = [
      { offset: '0%', color: '#3fb950' },
      { offset: '25%', color: '#d2a8ff' },
      { offset: '50%', color: '#8b9ba8' },
      { offset: '75%', color: '#f0883e' },
      { offset: '100%', color: '#3fb950' }
    ];
    stops.forEach(function (s) {
      var stop = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
      stop.setAttribute('offset', s.offset);
      stop.setAttribute('stop-color', s.color);
      grad.appendChild(stop);
    });
    defs.appendChild(grad);
    c.svg.appendChild(kRing);
  }

  // ═══ ANIMATE ═══
  function animate(c, t) {
    var tSec = t * 0.001;
    var baseR = Math.min(c.w, c.h) * 0.28;

    PLANES.forEach(function (plane, i) {
      var ring = document.getElementById('orbit-' + plane.name);
      var dot = document.getElementById('orbit-dot-' + plane.name);
      if (!ring) return;

      var angle = tSec * plane.omega;
      var r = baseR + i * 18;
      var ry = r * 0.35;
      var tilt = plane.tilt + tSec * 2;

      ring.setAttribute('transform',
        'rotate(' + tilt.toFixed(1) + ' ' + c.cx + ' ' + c.cy + ')');

      if (dot) {
        var dx = c.cx + r * Math.cos(angle);
        var dy = c.cy + ry * Math.sin(angle);
        // apply same tilt rotation
        var rad = tilt * PI / 180;
        var rx2 = c.cx + (dx - c.cx) * Math.cos(rad) - (dy - c.cy) * Math.sin(rad);
        var ry2 = c.cy + (dx - c.cx) * Math.sin(rad) + (dy - c.cy) * Math.cos(rad);
        dot.setAttribute('cx', rx2.toFixed(1));
        dot.setAttribute('cy', ry2.toFixed(1));
        dot.setAttribute('opacity', (0.3 + 0.3 * Math.sin(angle)).toFixed(2));
      }
    });

    // π null points — precess
    var nullR = 16;
    for (var n = 0; n < 3; n++) {
      var nAngle = n * (TAU / 3) + tSec * 0.14159265;
      var nx = c.cx + nullR * Math.cos(nAngle);
      var ny = c.cy + nullR * Math.sin(nAngle);
      var nEl = document.getElementById('pi-null-' + n);
      if (nEl) {
        nEl.setAttribute('cx', nx.toFixed(1));
        nEl.setAttribute('cy', ny.toFixed(1));
        nEl.setAttribute('r', (2.5 + Math.sin(tSec * PI + n * 2) * 1).toFixed(1));
      }
    }

    // kaleidoscope hue rotation
    var hue = document.getElementById('kaleid-hue');
    if (hue) hue.setAttribute('values', (tSec * 15 % 360).toFixed(0));

    var kRing = document.getElementById('kaleid-ring');
    if (kRing) {
      kRing.setAttribute('stroke-opacity',
        (0.1 + 0.08 * Math.sin(tSec * PI / 3.14159)).toFixed(3));
    }

    requestAnimationFrame(function (t2) { animate(c, t2); });
  }

  // ═══ CLICK HANDLERS ═══
  function setupClicks(c) {
    c.svg.addEventListener('click', function (e) {
      var rect = c.svg.getBoundingClientRect();
      var x = e.clientX - rect.left;
      var y = e.clientY - rect.top;
      var dx = x - c.cx, dy = y - c.cy;
      var dist = Math.sqrt(dx * dx + dy * dy);

      // click near null center → pin mode (drag to rotate view)
      if (dist < 30) {
        c.svg.classList.toggle('null-pinned');
        var indicator = document.getElementById('null-pin-indicator');
        if (!indicator) {
          indicator = document.createElement('div');
          indicator.id = 'null-pin-indicator';
          indicator.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);' +
            'font:10px monospace;color:#6e7681;pointer-events:none;z-index:9999;opacity:0.7';
          document.body.appendChild(indicator);
        }
        indicator.textContent = c.svg.classList.contains('null-pinned') ? '⊕ pinned — drag to orbit' : '';
        return;
      }

      // click on object → trace
      var target = e.target;
      if (target.tagName === 'circle' || target.tagName === 'text' || target.dataset.primal) {
        var id = target.id || target.textContent || 'unknown';
        showTrace(c, x, y, id);
      }
    });

    // drag when pinned
    c.svg.addEventListener('mousemove', function (e) {
      if (!c.svg.classList.contains('null-pinned')) return;
      var rect = c.svg.getBoundingClientRect();
      var mx = (e.clientX - rect.left - c.cx) / c.cx;
      var my = (e.clientY - rect.top - c.cy) / c.cy;

      var orbits = document.getElementById('null-orbits');
      if (orbits) {
        orbits.setAttribute('transform',
          'rotate(' + (mx * 30).toFixed(1) + ' ' + c.cx + ' ' + c.cy + ')' +
          ' skewX(' + (my * 10).toFixed(1) + ')');
      }
    });
  }

  // ═══ TRACE VISUALIZATION ═══
  function showTrace(c, x, y, id) {
    var existing = document.getElementById('trace-line');
    if (existing) existing.remove();

    var g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.id = 'trace-line';

    // line from object to null center
    var line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', x); line.setAttribute('y1', y);
    line.setAttribute('x2', c.cx); line.setAttribute('y2', c.cy);
    line.setAttribute('stroke', '#d2a8ff');
    line.setAttribute('stroke-width', '0.8');
    line.setAttribute('stroke-opacity', '0.4');
    line.setAttribute('stroke-dasharray', '3,4');
    g.appendChild(line);

    // label
    var label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    label.setAttribute('x', (x + c.cx) / 2);
    label.setAttribute('y', (y + c.cy) / 2 - 6);
    label.setAttribute('fill', '#8b949e');
    label.setAttribute('font-size', '8');
    label.setAttribute('text-anchor', 'middle');
    label.textContent = '→ ' + id.substring(0, 20);
    g.appendChild(label);

    c.svg.appendChild(g);
    setTimeout(function () { if (g.parentNode) g.remove(); }, 4000);
  }

  // ═══ BOOT ═══
  function boot() {
    var c = getCenter();
    if (!c) { setTimeout(boot, 1000); return; }

    createOrbitRings(c);
    createKaleidoscope(c);
    setupClicks(c);
    requestAnimationFrame(function (t) { animate(c, t); });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { setTimeout(boot, 500); });
  } else {
    setTimeout(boot, 500);
  }

  window._nullKaleidoscope = {
    PLANES: PLANES,
    getCenter: getCenter
  };
})();
