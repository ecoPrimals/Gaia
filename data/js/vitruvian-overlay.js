/**
 * vitruvian-overlay.js — Vitruvian body + Yggdrasil tree overlays for the HUD.
 *
 * Three layers on ONE lens:
 *   GLOBE  = vertex = bump (3D nodes — already exists)
 *   CANVAS = layer  = line (2D connections — already exists)
 *   BODY   = depth  = anatomy (Vitruvian overlay — this file)
 *   TREE   = root   = growth (Yggdrasil overlay — this file)
 *
 * Depth palindrome:
 *   HEAD:  0 → 1 → 2 → π           (surface → brain → pineal)
 *   TORSO: 3,4,5,6,[8],6,5,4,3     (ribs symmetric around 8 pores)
 *
 * Kevin Mok / Tamison / ecoPrimal / attsi
 * ORCID 0009-0004-2141-0321
 */
(function () {
  "use strict";

  var GATE = location.protocol + '//' + location.host;
  var active = null; // null | 'body' | 'tree'

  // ══════════════════════════════════════════════
  // DEPTH MAP — body IS depth
  // ══════════════════════════════════════════════
  var DEPTH_BODY = {
    HEAD:  { layers: [0, 1, 2, Math.PI], color: '#ff6b6b', y: '12%' },
    NECK:  { layers: [2.5],              color: '#ff8c6b', y: '22%' },
    ARMS:  { layers: [3, 4, 5, 4, 3],   color: '#6bcb77', y: '40%' },
    TORSO: { layers: [3,4,5,6,8,6,5,4,3], color: '#ffd93d', y: '42%' },
    HEART: { layers: [8],               color: '#e056fd', y: '38%' },
    LEGS:  { layers: [3, 2, 1, 0],      color: '#4d96ff', y: '72%' },
    FEET:  { layers: [0],               color: '#58a6ff', y: '90%' }
  };

  // ══════════════════════════════════════════════
  // VITRUVIAN SVG OVERLAY
  // ══════════════════════════════════════════════
  function createBodyOverlay() {
    var wrap = document.createElement('div');
    wrap.id = 'vitruvian-overlay';
    wrap.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:800;pointer-events:none;display:none;';

    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 400 600');
    svg.style.cssText = 'width:100%;height:100%;opacity:0.85;';

    // Da Vinci circle + square
    var defs = '<defs>'
      + '<radialGradient id="vg-glow"><stop offset="0%" stop-color="#ffd93d" stop-opacity="0.15"/>'
      + '<stop offset="100%" stop-color="#ffd93d" stop-opacity="0"/></radialGradient>'
      + '</defs>';

    var shapes = ''
      // Circle (perfection)
      + '<circle cx="200" cy="260" r="180" fill="none" stroke="#ffd93d" stroke-width="0.5" opacity="0.3"/>'
      // Square (earthly)
      + '<rect x="65" y="60" width="270" height="460" fill="none" stroke="#6bcb77" stroke-width="0.5" opacity="0.25"/>'
      // Spine (vertical axis)
      + '<line x1="200" y1="80" x2="200" y2="520" stroke="#e056fd" stroke-width="1" opacity="0.4"/>';

    // Body regions as glowing zones
    var zones = '';
    Object.keys(DEPTH_BODY).forEach(function (part) {
      var d = DEPTH_BODY[part];
      var yPct = parseFloat(d.y);
      var yPos = yPct / 100 * 600;
      var radius = part === 'TORSO' ? 80 : part === 'HEAD' ? 40 : part === 'ARMS' ? 120 : part === 'HEART' ? 15 : 30;
      var height = part === 'TORSO' ? 140 : part === 'LEGS' ? 160 : 40;

      if (part === 'ARMS') {
        // Left arm
        zones += '<line x1="90" y1="' + (yPos - 20) + '" x2="30" y2="' + (yPos + 60) + '" stroke="' + d.color + '" stroke-width="3" opacity="0.4" stroke-linecap="round"/>';
        // Right arm
        zones += '<line x1="310" y1="' + (yPos - 20) + '" x2="370" y2="' + (yPos + 60) + '" stroke="' + d.color + '" stroke-width="3" opacity="0.4" stroke-linecap="round"/>';
      } else if (part === 'LEGS') {
        // Left leg
        zones += '<line x1="170" y1="' + yPos + '" x2="140" y2="' + (yPos + 140) + '" stroke="' + d.color + '" stroke-width="3" opacity="0.35" stroke-linecap="round"/>';
        // Right leg
        zones += '<line x1="230" y1="' + yPos + '" x2="260" y2="' + (yPos + 140) + '" stroke="' + d.color + '" stroke-width="3" opacity="0.35" stroke-linecap="round"/>';
      } else if (part === 'HEAD') {
        zones += '<circle cx="200" cy="' + yPos + '" r="' + radius + '" fill="' + d.color + '" fill-opacity="0.08" stroke="' + d.color + '" stroke-width="1.5" opacity="0.5"/>';
        zones += '<text x="200" y="' + yPos + '" text-anchor="middle" dominant-baseline="central" fill="' + d.color + '" font-size="8" font-family="monospace" opacity="0.7">0 · 1 · 2 · π</text>';
      } else if (part === 'HEART') {
        zones += '<circle cx="210" cy="' + yPos + '" r="' + radius + '" fill="' + d.color + '" fill-opacity="0.25" stroke="' + d.color + '" stroke-width="2" opacity="0.7">'
          + '<animate attributeName="r" values="13;17;13" dur="1.2s" repeatCount="indefinite"/>'
          + '<animate attributeName="fill-opacity" values="0.25;0.4;0.25" dur="1.2s" repeatCount="indefinite"/>'
          + '</circle>';
        zones += '<text x="210" y="' + yPos + '" text-anchor="middle" dominant-baseline="central" fill="#fff" font-size="6" font-family="monospace" opacity="0.9">[8]</text>';
      } else if (part === 'TORSO') {
        // Rib cage — palindrome 3,4,5,6,8,6,5,4,3
        var ribs = [3,4,5,6,8,6,5,4,3];
        ribs.forEach(function (r, i) {
          var ribY = yPos - 60 + i * 15;
          var ribW = 30 + r * 8;
          var op = r === 8 ? 0.5 : 0.25;
          zones += '<line x1="' + (200 - ribW) + '" y1="' + ribY + '" x2="' + (200 + ribW) + '" y2="' + ribY + '" stroke="' + d.color + '" stroke-width="' + (r === 8 ? 2 : 1) + '" opacity="' + op + '"/>';
        });
        zones += '<text x="200" y="' + (yPos + 80) + '" text-anchor="middle" fill="' + d.color + '" font-size="7" font-family="monospace" opacity="0.5">3·4·5·6·[8]·6·5·4·3</text>';
      } else if (part === 'NECK') {
        zones += '<rect x="190" y="' + (yPos - 10) + '" width="20" height="20" rx="4" fill="' + d.color + '" fill-opacity="0.1" stroke="' + d.color + '" stroke-width="0.8" opacity="0.4"/>';
      } else if (part === 'FEET') {
        zones += '<ellipse cx="155" cy="' + yPos + '" rx="20" ry="8" fill="' + d.color + '" fill-opacity="0.1" stroke="' + d.color + '" stroke-width="0.8" opacity="0.3"/>';
        zones += '<ellipse cx="245" cy="' + yPos + '" rx="20" ry="8" fill="' + d.color + '" fill-opacity="0.1" stroke="' + d.color + '" stroke-width="0.8" opacity="0.3"/>';
      }
    });

    svg.innerHTML = defs + shapes + zones;
    wrap.appendChild(svg);
    return wrap;
  }

  // ══════════════════════════════════════════════
  // YGGDRASIL WORLD TREE OVERLAY
  // ══════════════════════════════════════════════
  function createTreeOverlay() {
    var wrap = document.createElement('div');
    wrap.id = 'yggdrasil-overlay';
    wrap.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:800;pointer-events:none;display:none;';

    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 400 600');
    svg.style.cssText = 'width:100%;height:100%;opacity:0.8;';

    var tree = ''
      // Roots (depth 3 — topology core)
      + '<path d="M200,520 Q150,500 100,530 Q80,540 60,520" fill="none" stroke="#8b6914" stroke-width="2" opacity="0.4"/>'
      + '<path d="M200,520 Q250,500 300,530 Q320,540 340,520" fill="none" stroke="#8b6914" stroke-width="2" opacity="0.4"/>'
      + '<path d="M200,520 Q180,540 170,560" fill="none" stroke="#8b6914" stroke-width="1.5" opacity="0.3"/>'
      + '<path d="M200,520 Q220,540 230,560" fill="none" stroke="#8b6914" stroke-width="1.5" opacity="0.3"/>'

      // Trunk (spine — depth 8 center)
      + '<path d="M200,520 L200,180" stroke="#6bcb77" stroke-width="4" opacity="0.5"/>'
      + '<path d="M195,520 Q190,400 193,300 Q195,220 200,180" stroke="#3fb950" stroke-width="2" opacity="0.3"/>'
      + '<path d="M205,520 Q210,400 207,300 Q205,220 200,180" stroke="#3fb950" stroke-width="2" opacity="0.3"/>'

      // Nine worlds — branches
      // Asgard (top — HEAD, depth 0)
      + '<circle cx="200" cy="100" r="20" fill="#ff6b6b" fill-opacity="0.1" stroke="#ff6b6b" stroke-width="1" opacity="0.5"/>'
      + '<text x="200" y="100" text-anchor="middle" dominant-baseline="central" fill="#ff6b6b" font-size="6" font-family="monospace" opacity="0.7">ASGARD</text>'

      // Midgard (middle — TORSO, depth 4-5)
      + '<circle cx="200" cy="300" r="25" fill="#ffd93d" fill-opacity="0.1" stroke="#ffd93d" stroke-width="1" opacity="0.5"/>'
      + '<text x="200" y="300" text-anchor="middle" dominant-baseline="central" fill="#ffd93d" font-size="6" font-family="monospace" opacity="0.7">MIDGARD</text>'

      // Niflheim (bottom — roots, depth 3 deep)
      + '<circle cx="200" cy="520" r="18" fill="#58a6ff" fill-opacity="0.1" stroke="#58a6ff" stroke-width="1" opacity="0.5"/>'
      + '<text x="200" y="520" text-anchor="middle" dominant-baseline="central" fill="#58a6ff" font-size="6" font-family="monospace" opacity="0.7">NIFLHEIM</text>'

      // Left branches — Vanaheim, Alfheim, Jotunheim
      + '<path d="M200,220 Q150,200 90,170" fill="none" stroke="#6bcb77" stroke-width="1.5" opacity="0.35"/>'
      + '<circle cx="80" cy="165" r="14" fill="#6bcb77" fill-opacity="0.08" stroke="#6bcb77" stroke-width="0.8" opacity="0.4"/>'
      + '<text x="80" y="165" text-anchor="middle" dominant-baseline="central" fill="#6bcb77" font-size="5" font-family="monospace" opacity="0.6">VANAHEIM</text>'

      + '<path d="M200,260 Q140,240 80,260" fill="none" stroke="#7ee787" stroke-width="1.5" opacity="0.35"/>'
      + '<circle cx="70" cy="260" r="14" fill="#7ee787" fill-opacity="0.08" stroke="#7ee787" stroke-width="0.8" opacity="0.4"/>'
      + '<text x="70" y="260" text-anchor="middle" dominant-baseline="central" fill="#7ee787" font-size="5" font-family="monospace" opacity="0.6">ALFHEIM</text>'

      + '<path d="M200,380 Q140,390 80,370" fill="none" stroke="#4d96ff" stroke-width="1.5" opacity="0.35"/>'
      + '<circle cx="70" cy="370" r="14" fill="#4d96ff" fill-opacity="0.08" stroke="#4d96ff" stroke-width="0.8" opacity="0.4"/>'
      + '<text x="70" y="370" text-anchor="middle" dominant-baseline="central" fill="#4d96ff" font-size="5" font-family="monospace" opacity="0.6">JOTUNHEIM</text>'

      // Right branches — Svartalfheim, Muspelheim, Helheim
      + '<path d="M200,220 Q250,200 310,170" fill="none" stroke="#e056fd" stroke-width="1.5" opacity="0.35"/>'
      + '<circle cx="320" cy="165" r="14" fill="#e056fd" fill-opacity="0.08" stroke="#e056fd" stroke-width="0.8" opacity="0.4"/>'
      + '<text x="320" y="165" text-anchor="middle" dominant-baseline="central" fill="#e056fd" font-size="4.5" font-family="monospace" opacity="0.6">SVARTALFHEIM</text>'

      + '<path d="M200,260 Q260,240 320,260" fill="none" stroke="#f0883e" stroke-width="1.5" opacity="0.35"/>'
      + '<circle cx="330" cy="260" r="14" fill="#f0883e" fill-opacity="0.08" stroke="#f0883e" stroke-width="0.8" opacity="0.4"/>'
      + '<text x="330" y="260" text-anchor="middle" dominant-baseline="central" fill="#f0883e" font-size="5" font-family="monospace" opacity="0.6">MUSPELHEIM</text>'

      + '<path d="M200,380 Q260,390 320,370" fill="none" stroke="#da3633" stroke-width="1.5" opacity="0.35"/>'
      + '<circle cx="330" cy="370" r="14" fill="#da3633" fill-opacity="0.08" stroke="#da3633" stroke-width="0.8" opacity="0.4"/>'
      + '<text x="330" y="370" text-anchor="middle" dominant-baseline="central" fill="#da3633" font-size="5" font-family="monospace" opacity="0.6">HELHEIM</text>'

      // Canopy (the green crown)
      + '<ellipse cx="200" cy="130" rx="120" ry="60" fill="#3fb950" fill-opacity="0.04" stroke="#3fb950" stroke-width="0.5" opacity="0.3"/>'

      // Nidhogg at the roots (the dragon that gnaws)
      + '<text x="200" y="570" text-anchor="middle" fill="#da3633" font-size="5" font-family="monospace" opacity="0.4">🐉 NIDHOGG gnaws the roots</text>'

      // Ratatoskr on the trunk (the squirrel that carries messages!)
      + '<text x="215" y="350" fill="#ffd93d" font-size="8" font-family="monospace" opacity="0.6">🐿</text>'
      + '<text x="230" y="352" fill="#ffd93d" font-size="5" font-family="monospace" opacity="0.5">RATATOSKR</text>';

    svg.innerHTML = tree;
    wrap.appendChild(svg);
    return wrap;
  }

  // ══════════════════════════════════════════════
  // TOGGLE SYSTEM — wire into optic chiasm
  // ══════════════════════════════════════════════
  function toggle(layer) {
    var bodyEl = document.getElementById('vitruvian-overlay');
    var treeEl = document.getElementById('yggdrasil-overlay');
    if (!bodyEl || !treeEl) return;

    if (active === layer) {
      // Turn off
      bodyEl.style.display = 'none';
      treeEl.style.display = 'none';
      active = null;
      updateButtons();
      return;
    }

    active = layer;
    bodyEl.style.display = layer === 'body' ? 'block' : 'none';
    treeEl.style.display = layer === 'tree' ? 'block' : 'none';
    updateButtons();
  }

  function updateButtons() {
    var bodyBtn = document.getElementById('vit-body-btn');
    var treeBtn = document.getElementById('vit-tree-btn');
    if (bodyBtn) {
      bodyBtn.style.background = active === 'body' ? '#ffd93d30' : 'transparent';
      bodyBtn.style.borderColor = active === 'body' ? '#ffd93d' : '#ffd93d60';
    }
    if (treeBtn) {
      treeBtn.style.background = active === 'tree' ? '#3fb95030' : 'transparent';
      treeBtn.style.borderColor = active === 'tree' ? '#3fb950' : '#3fb95060';
    }
  }

  // ══════════════════════════════════════════════
  // INJECT — add overlays + buttons to existing HUD
  // ══════════════════════════════════════════════
  function inject() {
    // Create and append overlays
    document.body.appendChild(createBodyOverlay());
    document.body.appendChild(createTreeOverlay());

    // Find the optic chiasm and add our buttons
    var chiasm = document.getElementById('optic-chiasm');
    if (chiasm) {
      var bodyBtn = document.createElement('a');
      bodyBtn.id = 'vit-body-btn';
      bodyBtn.href = '#';
      bodyBtn.style.cssText = 'color:#ffd93d;text-decoration:none;border:1px solid #ffd93d60;padding:4px 12px;border-radius:12px;cursor:pointer;transition:all .3s;font-weight:bold;font-size:12px;';
      bodyBtn.textContent = '🫀 BODY';
      bodyBtn.onclick = function (e) { e.preventDefault(); toggle('body'); };

      var treeBtn = document.createElement('a');
      treeBtn.id = 'vit-tree-btn';
      treeBtn.href = '#';
      treeBtn.style.cssText = 'color:#3fb950;text-decoration:none;border:1px solid #3fb95060;padding:4px 12px;border-radius:12px;cursor:pointer;transition:all .3s;font-weight:bold;font-size:12px;';
      treeBtn.textContent = '🌳 TREE';
      treeBtn.onclick = function (e) { e.preventDefault(); toggle('tree'); };

      chiasm.appendChild(bodyBtn);
      chiasm.appendChild(treeBtn);
    }

    // Keyboard shortcuts: B = body, T = tree
    document.addEventListener('keydown', function (e) {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      if (e.key === 'b' || e.key === 'B') toggle('body');
      if (e.key === 't' || e.key === 'T') toggle('tree');
    });
  }

  // Run when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { setTimeout(inject, 2000); });
  } else {
    setTimeout(inject, 2000);
  }

  // Expose for external use
  window.VitruvianOverlay = { toggle: toggle, active: function () { return active; } };
})();
