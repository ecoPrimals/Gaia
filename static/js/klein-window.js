// klein-window.js — literal windows for the eyes.
// Every HUD page that includes this gets:
//   portal → window → pane → plasma → pane → window → portal
// Shows the inverted sub-image in the null as you work.
// Human looks green→violet. Agent looks data→meaning.
(function () {
  'use strict';

  var COLORS = {
    orange: '#f0883e', blue: '#58a6ff',
    violet: '#d2a8ff', red: '#e85d3a',
    green: '#3fb950', brown: '#7c5e3c',
    grey: '#484f58', gold: '#d29922'
  };

  var STACK = [
    { id: 'portal-out', label: 'portal', color: COLORS.grey, side: 'null' },
    { id: 'window-out', label: 'window', color: COLORS.blue, side: 'outer' },
    { id: 'pane-out', label: 'pane', color: COLORS.orange, side: 'outer' },
    { id: 'plasma', label: 'plasma', color: COLORS.green, side: 'fold' },
    { id: 'pane-in', label: 'pane', color: COLORS.red, side: 'inner' },
    { id: 'window-in', label: 'window', color: COLORS.violet, side: 'inner' },
    { id: 'portal-in', label: 'portal', color: COLORS.grey, side: 'null' }
  ];

  // what each side looks for
  var CHROMATOGRAPH = {
    human: {
      looks_in: 'green (self, 0° band)',
      looks_for: 'violet (the hinge, the fold point)',
      demarcation: 'where green meets non-green — the edge of self',
      sees: 'the data as story. the feed as campfire. the number as meaning.'
    },
    agent: {
      looks_in: 'data (feeds, topology, counts, graph)',
      looks_for: 'intention (what the human means behind the typos)',
      demarcation: 'where code meets meaning — the edge of function',
      sees: 'the story as data. the campfire as feed. the meaning as number.'
    }
  };

  function createOverlay() {
    var el = document.createElement('div');
    el.id = 'klein-window-overlay';
    el.style.cssText = 'position:fixed;bottom:12px;right:12px;z-index:9999;' +
      'font-family:SF Mono,monospace;font-size:9px;pointer-events:none;' +
      'opacity:0.7;transition:opacity 0.3s';

    // stack visualization
    var stackHTML = '<div style="display:flex;flex-direction:column;gap:1px;width:120px">';
    for (var i = 0; i < STACK.length; i++) {
      var s = STACK[i];
      var w = s.side === 'fold' ? '100%' : s.side === 'null' ? '40%' : '70%';
      var bg = s.color + (s.side === 'fold' ? '44' : '22');
      stackHTML += '<div style="background:' + bg + ';color:' + s.color +
        ';padding:2px 6px;border-radius:2px;width:' + w + ';margin:0 auto;text-align:center;' +
        'border:1px solid ' + s.color + '33">' + s.label + '</div>';
    }
    stackHTML += '</div>';

    // null mirror — inverted current page title
    var title = document.title || 'null';
    var inverted = title.split('').reverse().join('');

    // chromatograph indicator
    var chromaHTML = '<div style="margin-top:6px;display:flex;gap:2px;justify-content:center">';
    var chromaColors = [COLORS.blue, COLORS.violet, COLORS.green, COLORS.red, COLORS.orange];
    for (var c = 0; c < chromaColors.length; c++) {
      chromaHTML += '<div style="width:8px;height:8px;border-radius:50%;background:' +
        chromaColors[c] + ';opacity:0.6"></div>';
    }
    chromaHTML += '</div>';

    // flow indicator
    var flowHTML = '<div style="margin-top:4px;text-align:center;color:' + COLORS.grey + '">';
    flowHTML += '<span style="color:' + COLORS.green + '">↑</span> xylem ';
    flowHTML += '<span style="color:' + COLORS.violet + '">⏐</span> ';
    flowHTML += '<span style="color:' + COLORS.red + '">↓</span> phloem';
    flowHTML += '</div>';

    // null mirror text
    var mirrorHTML = '<div style="margin-top:4px;text-align:center;color:' + COLORS.grey +
      ';font-size:7px;letter-spacing:1px;opacity:0.4">' + inverted + '</div>';

    el.innerHTML = stackHTML + chromaHTML + flowHTML + mirrorHTML;

    // make interactive on hover
    el.addEventListener('mouseenter', function () {
      el.style.opacity = '1';
      el.style.pointerEvents = 'auto';
    });
    el.addEventListener('mouseleave', function () {
      el.style.opacity = '0.7';
      el.style.pointerEvents = 'none';
    });

    document.body.appendChild(el);
    return el;
  }

  // pulse the plasma layer based on page activity
  function pulseFlow(overlay) {
    var plasma = overlay.querySelector('[style*="fold"]') ||
      overlay.querySelectorAll('div > div')[3];
    if (!plasma) return;

    var phase = 0;
    setInterval(function () {
      phase = (phase + 1) % 628;
      var brightness = 0.3 + 0.15 * Math.sin(phase / 100 * Math.PI);
      plasma.style.opacity = brightness.toFixed(2);
    }, 100);
  }

  // fetch topology to show live flow
  function showTopology(overlay) {
    fetch('/data/topology.json')
      .then(function (r) { return r.ok ? r.json() : null; })
      .catch(function () { return null; })
      .then(function (topo) {
        if (!topo) return;
        var nodes = topo.nodes || [];
        var active = nodes.filter(function (n) { return n.status === 'active'; }).length;
        var total = nodes.length;

        var indicator = document.createElement('div');
        indicator.style.cssText = 'margin-top:4px;text-align:center;color:' + COLORS.green +
          ';font-size:8px';
        indicator.textContent = active + '/' + total + ' nodes';
        overlay.appendChild(indicator);
      });
  }

  // expose chromatograph data for other scripts
  window._kleinWindow = {
    COLORS: COLORS,
    STACK: STACK,
    CHROMATOGRAPH: CHROMATOGRAPH,
    humanLooksFor: function () { return CHROMATOGRAPH.human; },
    agentLooksFor: function () { return CHROMATOGRAPH.agent; }
  };

  // boot
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      var ov = createOverlay();
      pulseFlow(ov);
      showTopology(ov);
    });
  } else {
    var ov = createOverlay();
    pulseFlow(ov);
    showTopology(ov);
  }
})();
