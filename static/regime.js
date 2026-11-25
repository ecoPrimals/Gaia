/* regime.js - the flat-plane anchor: one reading of the display, shared by every page that asks for it.

   A flat page has two numbers, its width and its height. Everything a layout can know about the display it is on
   comes from those two: how wide it is, and the slope of its diagonal (a square is 45 degrees, a 3:2 screen 34,
   a golden rectangle 32, a 16:9 screen 29). The tuebor desk (tuebor.primals.eco/desk/) reads them into one of four
   layouts; this is the same rule with the same thresholds, plus one more for a watch face, so the desk and the HUD
   agree about what kind of display they are on:

     watch     narrower than 280          one thing in the middle, nothing round the edge
     single    narrower than 600          one column
     square    width / height under 1.3   two columns, the rest underneath
     compact   narrower than 1100         two columns
     split     anything wider             three shares cut by the golden ratio: 14.6% | 61.8% | 23.6%

   It sets on <html>:  data-regime="split"   and the lengths  --regime-main  --regime-side  --regime-ctx  (px),
   fills any element marked data-regime-say with the reading as words, sends a "regime" event when it changes,
   and keeps the reading at window.regime. It moves nothing by itself: a page's own style sheet decides what each
   regime looks like. Nothing is fetched, nothing is stored, nothing is sent. */
(function () {
  'use strict';
  var PHI = (1 + Math.sqrt(5)) / 2, SIDE = 1 / (PHI * PHI * PHI * PHI), MAIN = 1 / PHI, CTX = 1 / (PHI * PHI * PHI);   // .146 .618 .236
  var GLYPH = {watch: '\u25EF', single: '\u25AE', square: '\u25A2', compact: '\u25AC', split: '\u25AD'};
  var root = document.documentElement, last = null;

  function name(w, h) {
    if (w < 280) return 'watch';
    if (w < 600) return 'single';
    if (w / h < 1.3) return 'square';
    if (w < 1100) return 'compact';
    return 'split';
  }
  function read() {
    var w = window.innerWidth || root.clientWidth || 0, h = window.innerHeight || root.clientHeight || 1;
    var n = name(w, h), a = w / h, split = n === 'split';
    var r = {name: n, glyph: GLYPH[n], w: w, h: h, aspect: a, diagonal: Math.atan2(h, w) * 180 / Math.PI,
             main: Math.round(split ? w * MAIN : w), side: Math.round(split ? w * SIDE : 0), ctx: Math.round(split ? w * CTX : 0)};
    r.say = r.glyph + ' ' + a.toFixed(2) + (Math.abs(a - PHI) < 0.1 ? ' \u2248\u03C6' : '') + ' \u00B7 ' + Math.round(r.diagonal) + '\u00B0 \u00B7 ' +
            (split ? '\u03C6-split' : n) + ' ' + w + '\u00D7' + h;
    return r;
  }
  function set() {
    var r = read(), changed = !last || last.name !== r.name;
    root.setAttribute('data-regime', r.name);
    root.style.setProperty('--regime-main', r.main + 'px');
    root.style.setProperty('--regime-side', r.side + 'px');
    root.style.setProperty('--regime-ctx', r.ctx + 'px');
    Array.prototype.forEach.call(document.querySelectorAll('[data-regime-say]'), function (el) { el.textContent = r.say; });
    last = window.regime = r;
    if (changed) { try { document.dispatchEvent(new CustomEvent('regime', {detail: r})); } catch (e) {} }
  }
  var wait = false;
  function soon() { if (!wait) { wait = true; (window.requestAnimationFrame || setTimeout)(function () { wait = false; set(); }); } }
  set();
  window.addEventListener('resize', soon);
  window.addEventListener('orientationchange', soon);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', set);
})();
