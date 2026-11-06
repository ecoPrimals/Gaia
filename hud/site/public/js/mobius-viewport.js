/**
 * Möbius Viewport — unlock the HUD from the browser rectangle.
 *
 * PROBLEM: MG = {W:700, H:480} — the membrane is trapped in a box.
 * The box is the browser shape. Everything is locked to it.
 *
 * SOLUTION: The viewport is a LENS, not a cage. The membrane is
 * continuous, infinite, möbius. The browser rectangle is just the
 * aperture — what you can see through. The null exhaust IS the
 * screen edges. Look into nothing → see reality underneath.
 *
 * Architecture:
 *   - MG dynamically tracks window size (no more 700×480)
 *   - π-ratio governs content distribution (center-to-edge)
 *   - Corners anchor to celestial orientation (solar/galaxy)
 *   - Null ring at the membrane edge = the exhaust boundary
 *   - Everything is always UNDER the HUD — the HUD is a lens
 *   - Content pushed to sides/center by π pressure
 *
 * Kevin Mok / Tamison / ecoPrimal / attsi
 * ORCID 0009-0004-2141-0321
 */

(function () {
  "use strict";

  const PI = Math.PI;

  /* ── Viewport geometry — ALWAYS tracks the actual window ── */
  const VP = {
    W: window.innerWidth,
    H: window.innerHeight,
    cx: window.innerWidth / 2,
    cy: window.innerHeight / 2,
    R: 0,      // membrane radius — π-derived
    nullR: 0,  // null ring radius — where content exhales to void
    aspect: 1, // aspect ratio
    diagonal: 0,
    piPressure: 0, // π-ratio pressure — how much to push content
  };

  function recalc() {
    VP.W = window.innerWidth;
    VP.H = window.innerHeight;
    VP.cx = VP.W / 2;
    VP.cy = VP.H / 2;
    VP.aspect = VP.W / VP.H;
    VP.diagonal = Math.sqrt(VP.W * VP.W + VP.H * VP.H);

    // Membrane radius: inscribed circle of the viewport
    // This is the largest circle that fits inside the rectangle
    VP.R = Math.min(VP.W, VP.H) / 2;

    // Null ring: the exhaust boundary. π × inscribed radius = the ring
    // where content meets void. Beyond this = null exhaust.
    VP.nullR = VP.R * PI / 2;

    // π-pressure: how much the aspect deviates from π-ratio (π:1 ≈ 3.14:1)
    // At π-ratio, pressure = 0 (perfect). Deviation = pressure to redistribute.
    VP.piPressure = Math.abs(VP.aspect - PI) / PI;
  }
  recalc();

  /* ── Corner anchors — celestial orientation at the viewport corners ── */
  // The four corners are NOT dead space. They're orientation.
  // Each corner = a celestial anchor point.
  // The membrane floats BETWEEN them.
  const CORNERS = {
    tl: { id: "polaris",  name: "Polaris",       note: "North — up/left",   symbol: "★" },
    tr: { id: "sun",      name: "Sol",            note: "East — sunrise",    symbol: "☉" },
    br: { id: "galaxy",   name: "Milky Way Core", note: "South — galactic",  symbol: "✦" },
    bl: { id: "moon",     name: "Luna",           note: "West — tidal",      symbol: "☽" },
  };

  // Corner coordinates (with π-margin from edges)
  function cornerCoords() {
    const m = VP.R * 0.08; // margin = 8% of membrane radius
    return {
      tl: { x: m,          y: m },
      tr: { x: VP.W - m,   y: m },
      br: { x: VP.W - m,   y: VP.H - m },
      bl: { x: m,          y: VP.H - m },
    };
  }

  /* ── Null exhaust — the void ring at the membrane boundary ── */
  // The null zone is the space between the inscribed membrane circle
  // and the viewport rectangle. This is where content EXHAUSTS to void.
  // It's not empty — it's the möbius fold where inside becomes outside.

  function nullZone() {
    // The four "crescents" between the circle and the rectangle corners
    // These are the null exhaust regions
    const area_rect = VP.W * VP.H;
    const area_circle = PI * VP.R * VP.R;
    const null_area = area_rect - area_circle;
    const null_fraction = null_area / area_rect;
    return {
      area: null_area,
      fraction: null_fraction, // how much of the viewport is null
      ringWidth: (VP.diagonal / 2) - VP.R, // distance from circle edge to corner
    };
  }

  /* ── π-distribution — how content flows from center to edge ── */
  // Content density follows 1/r² from center (like gravity, like light).
  // At the center: maximum density. At the null ring: zero.
  // The π-ratio determines the falloff curve.

  function piDensity(x, y) {
    const dx = x - VP.cx;
    const dy = y - VP.cy;
    const r = Math.sqrt(dx * dx + dy * dy);
    if (r >= VP.nullR) return 0; // beyond null ring = void
    // density falls off as cos²(r/nullR × π/2) — smooth to zero at boundary
    const t = r / VP.nullR;
    const density = Math.cos(t * PI / 2);
    return density * density; // cos² for smooth rolloff
  }

  // Where to place something given its "importance" (0=edge, 1=center)
  function piPlace(importance) {
    // importance=1 → center, importance=0 → null ring edge
    // The radius from center follows arccos(√importance) × nullR / (π/2)
    const r = Math.acos(Math.sqrt(Math.max(0, Math.min(1, importance)))) * VP.nullR / (PI / 2);
    return {
      radius: r,
      maxRadius: VP.nullR,
      density: piDensity(VP.cx + r, VP.cy),
    };
  }

  /* ── Möbius wrap — coordinates that wrap continuously ── */
  // On a möbius strip, going past one edge brings you back on the other
  // side, inverted. This function wraps coordinates so nothing "falls off".

  function mobiusWrap(x, y) {
    let wx = x, wy = y;
    let flipped = false;

    // Horizontal wrap with inversion
    if (wx < 0) { wx = -wx; wy = VP.H - wy; flipped = !flipped; }
    if (wx > VP.W) { wx = 2 * VP.W - wx; wy = VP.H - wy; flipped = !flipped; }

    // Vertical wrap with inversion
    if (wy < 0) { wy = -wy; wx = VP.W - wx; flipped = !flipped; }
    if (wy > VP.H) { wy = 2 * VP.H - wy; wx = VP.W - wx; flipped = !flipped; }

    return { x: wx, y: wy, flipped };
  }

  /* ── Patch MG — override the hardcoded 700×480 ── */
  function patchMG() {
    // Find PtMembrane's MG and update it
    // MG is created in pt-membrane.js as {W:700, H:480, R:π×54, cx:350, cy:250}
    // We need to reach into the shared _mc object

    // Strategy: override at the SVG level
    // The SVG viewBox is set to "0 0 700 480" — we patch this
    const svg = document.querySelector('#chipmunk-overlay svg');
    if (svg) {
      // Keep the viewBox as the coordinate system (700×480 is the internal coordinate space)
      // But make the SVG fill the actual viewport with preserveAspectRatio
      // "xMidYMid meet" = centered, maintains aspect, with null exhaust in the gaps
      svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
      svg.style.width = '100vw';
      svg.style.height = '100vh';
    }
  }

  /* ── Null exhaust SVG — overlay the void ring ── */
  function buildNullExhaust() {
    const existing = document.getElementById('mobius-null-exhaust');
    if (existing) existing.remove();

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.id = 'mobius-null-exhaust';
    svg.setAttribute('viewBox', `0 0 ${VP.W} ${VP.H}`);
    svg.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;' +
      'z-index:9999;pointer-events:none;mix-blend-mode:multiply;';

    // Null ring — gradient from transparent (at membrane edge) to dark (at viewport edge)
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');

    const grad = document.createElementNS('http://www.w3.org/2000/svg', 'radialGradient');
    grad.id = 'null-exhaust-gradient';
    grad.setAttribute('cx', '50%');
    grad.setAttribute('cy', '50%');
    // r = distance from center to corner / viewport half-diagonal
    const rPct = (VP.nullR / (VP.diagonal / 2) * 100).toFixed(1);
    grad.setAttribute('r', '70.7%'); // √2/2 = corner distance

    const stop1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
    stop1.setAttribute('offset', `${(VP.R / (VP.diagonal / 2) * 100).toFixed(1)}%`);
    stop1.setAttribute('stop-color', '#000');
    stop1.setAttribute('stop-opacity', '0');

    const stop2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
    stop2.setAttribute('offset', '100%');
    stop2.setAttribute('stop-color', '#000');
    stop2.setAttribute('stop-opacity', '0.85');

    grad.appendChild(stop1);
    grad.appendChild(stop2);
    defs.appendChild(grad);
    svg.appendChild(defs);

    // Full-viewport rect with the gradient
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('x', '0');
    rect.setAttribute('y', '0');
    rect.setAttribute('width', VP.W);
    rect.setAttribute('height', VP.H);
    rect.setAttribute('fill', 'url(#null-exhaust-gradient)');
    svg.appendChild(rect);

    // Corner anchors — celestial markers
    const cc = cornerCoords();
    for (const [pos, anchor] of Object.entries(CORNERS)) {
      const coord = cc[pos];
      const txt = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      txt.setAttribute('x', coord.x);
      txt.setAttribute('y', coord.y);
      txt.setAttribute('text-anchor', 'middle');
      txt.setAttribute('dominant-baseline', 'middle');
      txt.setAttribute('fill', 'rgba(255,255,255,0.15)');
      txt.setAttribute('font-size', `${Math.max(12, VP.R * 0.06)}px`);
      txt.setAttribute('font-family', 'monospace');
      txt.textContent = anchor.symbol;

      // Label below/above the symbol
      const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      label.setAttribute('x', coord.x);
      label.setAttribute('y', coord.y + (pos.startsWith('t') ? 16 : -12));
      label.setAttribute('text-anchor', 'middle');
      label.setAttribute('dominant-baseline', 'middle');
      label.setAttribute('fill', 'rgba(255,255,255,0.08)');
      label.setAttribute('font-size', `${Math.max(8, VP.R * 0.025)}px`);
      label.setAttribute('font-family', 'monospace');
      label.textContent = anchor.name;

      svg.appendChild(txt);
      svg.appendChild(label);
    }

    // Center null mark — the point where you look INTO nothing
    const nullMark = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    nullMark.setAttribute('cx', VP.cx);
    nullMark.setAttribute('cy', VP.cy);
    nullMark.setAttribute('r', '2');
    nullMark.setAttribute('fill', 'none');
    nullMark.setAttribute('stroke', 'rgba(255,255,255,0.06)');
    nullMark.setAttribute('stroke-width', '0.5');
    svg.appendChild(nullMark);

    // Null ring outline — the boundary between content and void
    const nullRing = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    nullRing.setAttribute('cx', VP.cx);
    nullRing.setAttribute('cy', VP.cy);
    nullRing.setAttribute('r', VP.R);
    nullRing.setAttribute('fill', 'none');
    nullRing.setAttribute('stroke', 'rgba(255,255,255,0.04)');
    nullRing.setAttribute('stroke-width', '0.5');
    nullRing.setAttribute('stroke-dasharray', `${PI * 2} ${PI}`);
    svg.appendChild(nullRing);

    document.body.appendChild(svg);
  }

  /* ── Resize handler ── */
  let resizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      recalc();
      patchMG();
      buildNullExhaust();
      document.body.setAttribute('data-vp-aspect', VP.aspect.toFixed(3));
      document.body.setAttribute('data-vp-pi-pressure', VP.piPressure.toFixed(3));
      document.body.setAttribute('data-vp-null-fraction', nullZone().fraction.toFixed(3));
    }, 100);
  });

  /* ── Init ── */
  function init() {
    recalc();

    // Set body attributes
    document.body.setAttribute('data-vp-aspect', VP.aspect.toFixed(3));
    document.body.setAttribute('data-vp-pi-pressure', VP.piPressure.toFixed(3));
    document.body.setAttribute('data-vp-null-fraction', nullZone().fraction.toFixed(3));

    // Build the null exhaust overlay
    buildNullExhaust();

    // Patch the SVG aspect ratio
    // Delay to let pt-membrane build first
    setTimeout(patchMG, 500);
    setTimeout(patchMG, 2000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  /* ── Expose ── */
  window.MobiusViewport = {
    VP,
    CORNERS,
    recalc,
    cornerCoords,
    nullZone,
    piDensity,
    piPlace,
    mobiusWrap,
    patchMG,
  };

})();
