// network-fold.js v2 — fold the network maps, show face entities ↔ those behind them
// Merges tuebor investigation (30 nodes) + detroit graph (341 entities) via 24 overlapping entities
// Force-directed layout with three zones: FACE | BOTH | BEHIND
(function() {
'use strict';

var PI2 = Math.PI * 2;
var BEHIND_TYPES = { ownership: 1, formation: 1, funding: 1, controlled_by: 1, parent_company: 1 };
var FACE_TYPES   = { governance: 1, board_membership: 1, appointment: 1, oversight: 1 };

var CLASS_COLORS = {
  'non-self': '#e85d3a', 'self': '#3fb950', 'partial': '#d29922', 'null': '#484f58'
};

var EDGE_COLORS = {
  ownership: '#e85d3a', formation: '#f85149', funding: '#d29922',
  parent_company: '#f0883e', controlled_by: '#ff7b72',
  governance: '#58a6ff', board_membership: '#bc8cff', oversight: '#8b949e', appointment: '#79c0ff',
  payment: '#e85d3a', money_flow: '#f0883e', employment: '#3fb950',
  investigation: '#f778ba', corruption: '#f85149',
  support: '#58a6ff', donation: '#d29922', journalism: '#79c0ff',
  smear: '#f85149', amplification: '#f0883e'
};

var TUEBOR_RING = '#f778ba';

var _canvas, _ctx, _W, _H;
var _nodes = [], _edges = [];
var _nodeMap = {};
var _focusId = null;
var _hovered = null;
var _offset = { x: 0, y: 0 };
var _scale = 1;
var _dragging = false;
var _dragNode = null;
var _dragStart = null;
var _simRunning = false;
var _animFrame = null;
var _filterMode = 'all'; // all | behind | face | tuebor

function init(container) {
  _canvas = document.createElement('canvas');
  _canvas.style.cssText = 'width:100%;height:100%;background:rgba(13,17,23,.97);cursor:grab;border-radius:8px;display:block';
  container.appendChild(_canvas);

  // Controls
  var bar = document.createElement('div');
  bar.style.cssText = 'position:absolute;bottom:10px;left:50%;transform:translateX(-50%);display:flex;gap:6px;z-index:202';
  var filters = [
    ['all', 'ALL'],
    ['behind', '← BEHIND'],
    ['face', 'FACE →'],
    ['tuebor', '⚖ TUEBOR'],
  ];
  filters.forEach(function(f) {
    var btn = document.createElement('button');
    btn.textContent = f[1];
    btn.dataset.mode = f[0];
    btn.style.cssText = 'background:rgba(48,54,61,.8);color:#8b949e;border:1px solid #30363d;padding:3px 10px;font:10px monospace;cursor:pointer;border-radius:4px';
    btn.onclick = function() {
      _filterMode = f[0];
      updateVisibility();
      draw();
      bar.querySelectorAll('button').forEach(function(b) {
        b.style.borderColor = b.dataset.mode === _filterMode ? '#58a6ff' : '#30363d';
        b.style.color = b.dataset.mode === _filterMode ? '#58a6ff' : '#8b949e';
      });
    };
    if (f[0] === 'all') { btn.style.borderColor = '#58a6ff'; btn.style.color = '#58a6ff'; }
    bar.appendChild(btn);
  });
  container.appendChild(bar);

  _canvas.addEventListener('mousedown', onDown);
  _canvas.addEventListener('mousemove', onMove);
  _canvas.addEventListener('mouseup', onUp);
  _canvas.addEventListener('mouseleave', onUp);
  _canvas.addEventListener('wheel', onWheel, { passive: false });
  _canvas.addEventListener('dblclick', onDbl);
  window.addEventListener('resize', resize);
  resize();
  load();
}

function resize() {
  if (!_canvas || !_canvas.parentElement) return;
  var r = _canvas.parentElement.getBoundingClientRect();
  var dpr = window.devicePixelRatio || 1;
  _W = _canvas.width = r.width * dpr;
  _H = _canvas.height = r.height * dpr;
  _canvas.style.width = r.width + 'px';
  _canvas.style.height = r.height + 'px';
  _ctx = _canvas.getContext('2d');
  if (_nodes.length) draw();
}

function load() {
  fetch('/detroit-data/fold.json')
    .then(function(r) { return r.json(); })
    .then(function(data) {
      buildGraph(data);
      simulate();
    })
    .catch(function(err) { console.error('network-fold: load failed', err); });
}

function buildGraph(data) {
  _nodes = [];
  _edges = [];
  _nodeMap = {};

  var nodes = data.nodes || [];
  var edges = data.edges || [];

  // Position nodes initially by category
  var cx = _W / 2, cy = _H / 2;

  nodes.forEach(function(n) {
    var cat = n.category || 'interact';
    var xBias = cat === 'face' ? -0.35 : cat === 'behind' ? 0.35 : cat === 'both' ? 0 : (cat === 'tuebor_only' ? 0.5 : 0);
    var tierSpread = (n.tier || 3) * 30;
    var angle = Math.random() * PI2;

    var node = {
      id: n.id,
      label: n.label,
      sort_class: n.sort_class || 'null',
      tier: n.tier || 5,
      edges: n.edges || 0,
      category: cat,
      in_tuebor: n.in_tuebor,
      tuebor_type: n.tuebor_type,
      behind_entities: n.behind_entities || [],
      face_entities: n.face_entities || [],
      connections: n.connections || [],
      r: Math.max(3, Math.min(22, Math.sqrt((n.edges || 1)) * 2.5)),
      color: CLASS_COLORS[n.sort_class] || '#484f58',
      x: cx + xBias * _W * 0.4 + Math.cos(angle) * tierSpread + (Math.random() - 0.5) * 80,
      y: cy + Math.sin(angle) * tierSpread + (Math.random() - 0.5) * 200,
      vx: 0, vy: 0,
      fx: null, fy: null,
      visible: true,
    };
    _nodes.push(node);
    _nodeMap[n.id] = node;
  });

  // Build edges
  var edgeSet = {};
  edges.forEach(function(e) {
    var from = _nodeMap[e.from];
    var to = _nodeMap[e.to];
    if (!from || !to) return;
    var key = [e.from, e.to].sort().join('|') + '|' + e.type;
    if (edgeSet[key]) return;
    edgeSet[key] = true;

    var etype = 'interact';
    if (BEHIND_TYPES[e.type]) etype = 'behind';
    else if (FACE_TYPES[e.type]) etype = 'face';

    _edges.push({
      from: from,
      to: to,
      type: e.type,
      edgeType: etype,
      source: e.source,
      color: EDGE_COLORS[e.type] || '#30363d',
      visible: true,
    });
  });
}

function updateVisibility() {
  var mode = _filterMode;
  _nodes.forEach(function(n) {
    if (mode === 'all') { n.visible = true; return; }
    if (mode === 'tuebor') { n.visible = n.in_tuebor; return; }
    if (mode === 'behind') {
      n.visible = n.category === 'behind' || n.category === 'both' || n.behind_entities.length > 0;
      return;
    }
    if (mode === 'face') {
      n.visible = n.category === 'face' || n.category === 'both' || n.face_entities.length > 0;
      return;
    }
  });
  _edges.forEach(function(e) {
    e.visible = e.from.visible && e.to.visible;
    if (mode === 'behind') e.visible = e.visible && (e.edgeType === 'behind' || e.edgeType === 'face');
    if (mode === 'face') e.visible = e.visible && (e.edgeType === 'face' || e.edgeType === 'behind');
    if (mode === 'tuebor') e.visible = e.visible && e.source === 'tuebor';
  });
}

// ═══ FORCE SIMULATION ═══

function simulate() {
  _simRunning = true;
  var iter = 0;
  var maxIter = 200;
  var alpha = 1;

  function tick() {
    if (!_simRunning || iter > maxIter) {
      _simRunning = false;
      draw();
      return;
    }
    alpha = 1 - iter / maxIter;
    alpha = alpha * alpha * 0.8;

    // Repulsion
    for (var i = 0; i < _nodes.length; i++) {
      var ni = _nodes[i];
      if (!ni.visible) continue;
      for (var j = i + 1; j < _nodes.length; j++) {
        var nj = _nodes[j];
        if (!nj.visible) continue;
        var dx = ni.x - nj.x;
        var dy = ni.y - nj.y;
        var d2 = dx * dx + dy * dy;
        if (d2 < 1) d2 = 1;
        var d = Math.sqrt(d2);
        var force = 800 / d2;
        var fx = dx / d * force * alpha;
        var fy = dy / d * force * alpha;
        ni.vx += fx; ni.vy += fy;
        nj.vx -= fx; nj.vy -= fy;
      }
    }

    // Attraction along edges
    _edges.forEach(function(e) {
      if (!e.visible) return;
      var dx = e.to.x - e.from.x;
      var dy = e.to.y - e.from.y;
      var d = Math.sqrt(dx * dx + dy * dy);
      if (d < 1) return;
      var ideal = 60;
      var force = (d - ideal) * 0.003 * alpha;
      var fx = dx / d * force;
      var fy = dy / d * force;
      e.from.vx += fx; e.from.vy += fy;
      e.to.vx -= fx; e.to.vy -= fy;
    });

    // Category gravity — pull face left, behind right
    _nodes.forEach(function(n) {
      if (!n.visible) return;
      var cat = n.category;
      var targetX = _W / 2;
      if (cat === 'face') targetX = _W * 0.25;
      else if (cat === 'behind') targetX = _W * 0.75;
      else if (cat === 'both') targetX = _W * 0.5;
      else if (cat === 'tuebor_only') targetX = _W * 0.85;
      n.vx += (targetX - n.x) * 0.002 * alpha;
      // Vertical centering
      n.vy += (_H / 2 - n.y) * 0.0005 * alpha;
    });

    // Apply velocities
    _nodes.forEach(function(n) {
      if (n.fx !== null) { n.x = n.fx; n.y = n.fy; n.vx = 0; n.vy = 0; return; }
      n.vx *= 0.7;
      n.vy *= 0.7;
      n.x += n.vx;
      n.y += n.vy;
      // Boundary
      n.x = Math.max(n.r + 10, Math.min(_W - n.r - 10, n.x));
      n.y = Math.max(n.r + 30, Math.min(_H - n.r - 30, n.y));
    });

    iter++;
    draw();
    _animFrame = requestAnimationFrame(tick);
  }
  tick();
}

// ═══ DRAWING ═══

function draw() {
  if (!_ctx) return;
  var ctx = _ctx;
  ctx.save();
  ctx.clearRect(0, 0, _W, _H);
  ctx.translate(_W / 2 + _offset.x, _H / 2 + _offset.y);
  ctx.scale(_scale, _scale);
  ctx.translate(-_W / 2, -_H / 2);

  // Zone labels
  ctx.font = 'bold 11px monospace';
  ctx.textAlign = 'center';
  ctx.fillStyle = 'rgba(88,166,255,0.25)';
  ctx.fillText('FACE  ENTITIES', _W * 0.25, 18);
  ctx.fillStyle = 'rgba(139,148,158,0.25)';
  ctx.fillText('BOTH', _W * 0.5, 18);
  ctx.fillStyle = 'rgba(232,93,58,0.25)';
  ctx.fillText('BEHIND  THE  FACE', _W * 0.75, 18);

  // Zone dividers
  ctx.setLineDash([2, 6]);
  ctx.strokeStyle = 'rgba(48,54,61,0.5)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(_W * 0.375, 28); ctx.lineTo(_W * 0.375, _H - 10);
  ctx.moveTo(_W * 0.625, 28); ctx.lineTo(_W * 0.625, _H - 10);
  ctx.stroke();
  ctx.setLineDash([]);

  // Draw edges
  _edges.forEach(function(e) {
    if (!e.visible) return;
    var focused = _focusId && (e.from.id === _focusId || e.to.id === _focusId);

    ctx.beginPath();
    ctx.moveTo(e.from.x, e.from.y);
    ctx.lineTo(e.to.x, e.to.y);

    if (focused) {
      ctx.strokeStyle = e.color + 'aa';
      ctx.lineWidth = 2;
      if (e.edgeType === 'behind') {
        ctx.setLineDash([5, 3]);
      }
    } else if (_focusId) {
      ctx.strokeStyle = 'rgba(48,54,61,0.06)';
      ctx.lineWidth = 0.5;
    } else {
      var baseAlpha = e.edgeType === 'behind' ? '20' : e.edgeType === 'face' ? '18' : '0a';
      ctx.strokeStyle = e.color + baseAlpha;
      ctx.lineWidth = e.source === 'tuebor' ? 1.2 : 0.7;
      if (e.edgeType === 'behind') ctx.setLineDash([4, 4]);
    }
    ctx.stroke();
    ctx.setLineDash([]);

    // Edge label on focused
    if (focused) {
      var mx = (e.from.x + e.to.x) / 2;
      var my = (e.from.y + e.to.y) / 2;
      ctx.fillStyle = 'rgba(201,209,217,0.5)';
      ctx.font = '8px monospace';
      ctx.textAlign = 'center';
      ctx.fillText(e.type.replace(/_/g, ' '), mx, my - 4);
    }
  });

  // Draw nodes
  _nodes.forEach(function(n) {
    if (!n.visible) return;

    var focused = n.id === _focusId;
    var hovered = n.id === _hovered;
    var connected = false;
    if (_focusId && !focused) {
      for (var i = 0; i < _edges.length; i++) {
        var e = _edges[i];
        if (!e.visible) continue;
        if ((e.from.id === _focusId && e.to.id === n.id) || (e.to.id === _focusId && e.from.id === n.id)) {
          connected = true;
          break;
        }
      }
    }

    var alpha = _focusId ? (focused || connected ? 1 : 0.12) : 0.85;

    // Tuebor ring
    if (n.in_tuebor) {
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.r + 3, 0, PI2);
      ctx.strokeStyle = TUEBOR_RING + (alpha < 1 ? '33' : '66');
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }

    // Node circle
    ctx.beginPath();
    ctx.arc(n.x, n.y, n.r, 0, PI2);
    var hex = n.color;
    var fillAlpha = alpha < 1 ? '33' : 'cc';
    ctx.fillStyle = hex + fillAlpha;
    ctx.fill();
    if (focused || hovered) {
      ctx.strokeStyle = '#e6edf3';
      ctx.lineWidth = 2;
      ctx.stroke();
    }

    // Category indicator dot
    if (n.category === 'both') {
      ctx.beginPath();
      ctx.arc(n.x + n.r - 2, n.y - n.r + 2, 3, 0, PI2);
      ctx.fillStyle = '#bc8cff';
      ctx.fill();
    }

    // Label
    var showLabel = n.r > 5 || focused || connected || hovered || n.tier <= 2;
    if (showLabel && alpha > 0.1) {
      ctx.fillStyle = 'rgba(201,209,217,' + (alpha * 0.9) + ')';
      ctx.font = (focused ? 'bold 11px' : '9px') + ' monospace';
      ctx.textAlign = n.x < _W * 0.4 ? 'right' : n.x > _W * 0.6 ? 'left' : 'center';
      var lx = n.x < _W * 0.4 ? n.x - n.r - 4 : n.x > _W * 0.6 ? n.x + n.r + 4 : n.x;
      var label = n.label.length > 28 ? n.label.slice(0, 26) + '\u2026' : n.label;
      ctx.fillText(label, lx, n.y + 3);
    }
  });

  // Info panel
  if (_focusId && _nodeMap[_focusId]) {
    drawPanel(ctx, _nodeMap[_focusId]);
  }

  // Legend
  drawLegend(ctx);

  ctx.restore();
}

function drawPanel(ctx, n) {
  var pw = 360, ph = 170;
  var px = 14, py = _H - ph - 14;

  ctx.fillStyle = 'rgba(13,17,23,0.94)';
  ctx.strokeStyle = n.color + '55';
  ctx.lineWidth = 1;
  roundRect(ctx, px, py, pw, ph, 6);
  ctx.fill(); ctx.stroke();

  ctx.textAlign = 'left';
  ctx.fillStyle = '#e6edf3';
  ctx.font = 'bold 12px monospace';
  ctx.fillText(n.label.slice(0, 40), px + 10, py + 20);

  ctx.fillStyle = '#8b949e';
  ctx.font = '10px monospace';
  var meta = 'tier ' + n.tier + ' \u00b7 ' + n.sort_class + ' \u00b7 ' + n.edges + ' edges';
  if (n.in_tuebor) meta += ' \u00b7 \u2696 tuebor';
  if (n.tuebor_type) meta += ' (' + n.tuebor_type + ')';
  ctx.fillText(meta, px + 10, py + 36);

  var y = py + 54;
  if (n.behind_entities.length > 0) {
    ctx.fillStyle = '#e85d3a';
    ctx.font = 'bold 9px monospace';
    ctx.fillText('BEHIND:', px + 10, y);
    y += 13;
    ctx.font = '9px monospace';
    n.behind_entities.slice(0, 3).forEach(function(b) {
      ctx.fillText('\u2192 ' + b.type.replace(/_/g,' ') + ': ' + (b.label || b.id).slice(0, 35), px + 18, y);
      y += 12;
    });
    if (n.behind_entities.length > 3) {
      ctx.fillText('  +' + (n.behind_entities.length - 3) + ' more', px + 18, y);
      y += 12;
    }
  }

  if (n.face_entities.length > 0) {
    ctx.fillStyle = '#58a6ff';
    ctx.font = 'bold 9px monospace';
    ctx.fillText('FACE OF:', px + 10, y);
    y += 13;
    ctx.font = '9px monospace';
    n.face_entities.slice(0, 3).forEach(function(f) {
      ctx.fillText('\u2192 ' + f.type.replace(/_/g,' ') + ': ' + (f.label || f.id).slice(0, 35), px + 18, y);
      y += 12;
    });
    if (n.face_entities.length > 3) {
      ctx.fillText('  +' + (n.face_entities.length - 3) + ' more', px + 18, y);
    }
  }
}

function drawLegend(ctx) {
  var lx = _W - 160, ly = 30;
  ctx.fillStyle = 'rgba(13,17,23,0.8)';
  roundRect(ctx, lx - 8, ly - 14, 155, 100, 4);
  ctx.fill();

  ctx.font = '9px monospace';
  ctx.textAlign = 'left';

  var items = [
    ['#e85d3a', 'non-self (hostile)'],
    ['#3fb950', 'self (sovereign)'],
    ['#d29922', 'partial (mixed)'],
    ['#484f58', 'null (unknown)'],
    [TUEBOR_RING, '\u2696 tuebor investigation'],
  ];
  items.forEach(function(item, i) {
    ctx.fillStyle = item[0];
    ctx.beginPath();
    ctx.arc(lx, ly + i * 16, 4, 0, PI2);
    ctx.fill();
    ctx.fillStyle = '#8b949e';
    ctx.fillText(item[1], lx + 10, ly + i * 16 + 3);
  });
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r);
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}

// ═══ INTERACTION ═══

function screenToWorld(sx, sy) {
  return {
    x: (sx - _W / 2 - _offset.x) / _scale + _W / 2,
    y: (sy - _H / 2 - _offset.y) / _scale + _H / 2
  };
}

function hitTest(ex, ey) {
  var r = _canvas.getBoundingClientRect();
  var dpr = window.devicePixelRatio || 1;
  var sx = (ex - r.left) * dpr;
  var sy = (ey - r.top) * dpr;
  var w = screenToWorld(sx, sy);
  for (var i = _nodes.length - 1; i >= 0; i--) {
    var n = _nodes[i];
    if (!n.visible) continue;
    var dx = w.x - n.x, dy = w.y - n.y;
    if (dx * dx + dy * dy < (n.r + 5) * (n.r + 5)) return n;
  }
  return null;
}

function onDown(e) {
  var hit = hitTest(e.clientX, e.clientY);
  if (hit) {
    _focusId = hit.id === _focusId ? null : hit.id;
    _dragNode = hit;
    hit.fx = hit.x; hit.fy = hit.y;
    _canvas.style.cursor = 'grabbing';
    draw();
    return;
  }
  _focusId = null;
  _dragging = true;
  _dragStart = { x: e.clientX - _offset.x, y: e.clientY - _offset.y };
  _canvas.style.cursor = 'grabbing';
  draw();
}

function onMove(e) {
  if (_dragNode) {
    var r = _canvas.getBoundingClientRect();
    var dpr = window.devicePixelRatio || 1;
    var sx = (e.clientX - r.left) * dpr;
    var sy = (e.clientY - r.top) * dpr;
    var w = screenToWorld(sx, sy);
    _dragNode.x = _dragNode.fx = w.x;
    _dragNode.y = _dragNode.fy = w.y;
    draw();
    return;
  }
  if (_dragging && _dragStart) {
    _offset.x = e.clientX - _dragStart.x;
    _offset.y = e.clientY - _dragStart.y;
    draw();
    return;
  }

  var hit = hitTest(e.clientX, e.clientY);
  var newH = hit ? hit.id : null;
  if (newH !== _hovered) {
    _hovered = newH;
    _canvas.style.cursor = hit ? 'pointer' : 'grab';
    draw();
  }
}

function onUp() {
  if (_dragNode) {
    _dragNode.fx = null; _dragNode.fy = null;
    _dragNode = null;
  }
  _dragging = false;
  _dragStart = null;
  _canvas.style.cursor = _hovered ? 'pointer' : 'grab';
}

function onWheel(e) {
  e.preventDefault();
  var factor = e.deltaY > 0 ? 0.92 : 1.08;
  _scale = Math.max(0.15, Math.min(6, _scale * factor));
  draw();
}

function onDbl(e) {
  var hit = hitTest(e.clientX, e.clientY);
  if (hit) {
    _focusId = hit.id === _focusId ? null : hit.id;
    draw();
  }
}


// ═══ PUBLIC API ═══

function show() {
  var existing = document.getElementById('network-fold-wrap');
  if (existing) {
    existing.style.display = 'block';
    resize();
    return;
  }

  var wrap = document.createElement('div');
  wrap.id = 'network-fold-wrap';
  wrap.style.cssText = 'position:fixed;top:3%;left:3%;width:94%;height:90%;z-index:200;border:1px solid rgba(90,184,122,0.3);border-radius:8px;backdrop-filter:blur(12px);background:rgba(13,17,23,.95)';

  var header = document.createElement('div');
  header.style.cssText = 'position:absolute;top:0;left:0;right:0;height:28px;display:flex;align-items:center;justify-content:space-between;padding:0 12px;z-index:201';

  var title = document.createElement('span');
  title.style.cssText = 'color:#58a6ff;font:bold 11px monospace';
  title.textContent = '\u{1f9ec} NETWORK FOLD \u2014 face entities \u2194 those behind them';
  header.appendChild(title);

  var close = document.createElement('button');
  close.textContent = '\u00d7';
  close.style.cssText = 'background:none;border:none;color:#8b949e;font-size:20px;cursor:pointer;padding:0 4px';
  close.onclick = hide;
  header.appendChild(close);

  wrap.appendChild(header);
  document.body.appendChild(wrap);
  init(wrap);
}

function hide() {
  var wrap = document.getElementById('network-fold-wrap');
  if (wrap) wrap.style.display = 'none';
  if (_animFrame) cancelAnimationFrame(_animFrame);
  _simRunning = false;
}

window._networkFold = { show: show, hide: hide };
})();
