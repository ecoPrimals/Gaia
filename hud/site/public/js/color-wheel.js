/**
 * color-wheel.js — Golden angle (137.5°) color distribution.
 *
 * The golden angle ensures maximum visual separation between
 * adjacent indices. Used by ring-sort, epitope display, pore depth,
 * and any visualization needing N distinct hues without collisions.
 *
 * Math: 360° × (1 - 1/φ) = 360° × (2 - φ) ≈ 137.508°
 * where φ = (1 + √5) / 2 (the golden ratio).
 *
 * Kevin Mok / Tamison / ecoPrimal / attsi
 * ORCID 0009-0004-2141-0321
 */
(function () {
  'use strict';

  var PHI = (1 + Math.sqrt(5)) / 2;
  var GOLDEN_ANGLE = 360 * (2 - PHI); // ≈ 137.508°

  /** Hue (0-360) for index i. Each successive index is maximally separated. */
  function hue(i) {
    return (i * GOLDEN_ANGLE) % 360;
  }

  /** HSL string for index i with optional saturation (0-100) and lightness (0-100). */
  function hsl(i, s, l) {
    return 'hsl(' + hue(i) + ',' + (s != null ? s : 60) + '%,' + (l != null ? l : 50) + '%)';
  }

  /** HSLA string with alpha (0-1). */
  function hsla(i, s, l, a) {
    return 'hsla(' + hue(i) + ',' + (s != null ? s : 60) + '%,' + (l != null ? l : 50) + '%,' + (a != null ? a : 1) + ')';
  }

  /**
   * Generate N maximally-separated colors.
   * Returns array of HSL strings.
   */
  function palette(n, s, l) {
    var colors = [];
    for (var i = 0; i < n; i++) {
      colors.push(hsl(i, s, l));
    }
    return colors;
  }

  /**
   * Map a value (0-1) to a hue via golden angle.
   * Useful for continuous data → color mapping.
   */
  function valueToHue(v) {
    return (v * 360 * PHI) % 360;
  }

  /**
   * Complementary hue — 180° opposite on the wheel.
   */
  function complement(i) {
    return (hue(i) + 180) % 360;
  }

  /**
   * Triadic hues — 120° apart from index i.
   * Returns [hue1, hue2, hue3].
   */
  function triad(i) {
    var h = hue(i);
    return [h, (h + 120) % 360, (h + 240) % 360];
  }

  /**
   * Apply golden-angle coloring to DOM elements.
   * Selector: CSS selector string.
   * Property: CSS property to set (default 'color').
   */
  function paint(selector, property, s, l) {
    var els = document.querySelectorAll(selector);
    var prop = property || 'color';
    for (var i = 0; i < els.length; i++) {
      els[i].style[prop] = hsl(i, s, l);
    }
  }

  /** Set a CSS custom property with the hue for index i. */
  function setCSSVar(i, varName) {
    document.documentElement.style.setProperty(
      varName || '--cw-hue-' + i,
      String(hue(i))
    );
  }

  window.ColorWheel = {
    GOLDEN_ANGLE: GOLDEN_ANGLE,
    PHI: PHI,
    hue: hue,
    hsl: hsl,
    hsla: hsla,
    palette: palette,
    valueToHue: valueToHue,
    complement: complement,
    triad: triad,
    paint: paint,
    setCSSVar: setCSSVar,
    // Backward compat
    hueFromIndex: hue,
    hslFromIndex: hsl,
  };
})();
