/**
 * piGut.js — The intestinal lining of Gaia's desk
 *
 * Gaia IS the host. No "localhost" — just paths.
 * Old dead ports (3141-3145, 9878, 31415) → relative paths.
 * Tensor-sorted by organ proximity: sense → body → mind → spine.
 * k-nearest: related routes cluster together.
 */
(function piGut() {
  // ═══ TENSOR ROUTE MAP — k-n sorted by organ ═══
  // Dimension 0: SENSE (eyes, scan, immune, fire)
  // Dimension 1: BODY  (pulse, model, thymus, barriers)
  // Dimension 2: MIND  (agents, spawn, identity, feed)
  // Dimension 3: SPINE (throat, shout, one-feed, rss)
  // ═══ π-PORT CONSTANTS ═══
  const PI_TISSUE = 5820;  // π[52:56] → tissue proxy (northGate RTX 5090)
  const PI_OLLAMA = 1693;  // π[40:44] → ollama
  const PI_DATA   = 9937;  // π[44:48] → data server
  const PI_GATE   = 4197;  // π[36:40] → gate

  const R = {
    // DIM 0 — SENSE
    '3144/sense':    '/eyes',
    '3144/fire':     '/v1/chat/completions',
    '3144/immune':   '/thymus',
    '3144/scan':     '/intersects',
    '3144/hormesis': '/barriers',
    '3144/converge': '/corpus',
    '3144/thymus':   '/thymus',
    '3144/patrol':   '/barriers',
    '3144/maze':     '/terra',
    // DIM 1 — BODY
    '3141/pulse':    '/pulse',
    '3141/model':    '/api/tags',
    // DIM 2 — MIND
    '3142/agents':   '/now.json',
    '3142/spawn':    '/v1/chat/completions',
    '3145/lan':      '/home',
    '3145/identity': '/zk',
    '3145/redox':    '/circulatory',
    '3145/feed':     '/now.json',
    // DIM 3 — SPINE
    '3143/throat':   '/rss',
    '9878/':         '/now.json',
    '9878/shout':    '/v1/chat/completions',
    '9878/pulse':    '/pulse',
    '31415/one-feed':'/now.json',
  };

  // ═══ INTERCEPT — old port refs → relative paths ═══
  const _oldPorts = /localhost:(314[1-5]|9878|31415)/;
  const _ollamaPort = /localhost:11434/;
  // ZK SMASH: catch ANY raw IP:port pattern on the LAN
  const _rawIP = /https?:\/\/192\.168\.\d+\.\d+:(\d+)(\/.*)?/;
  const _tissuePort = /[:\/]11437/;

  // π-host resolver: same host, different π-port
  function piHost(piPort) {
    return location.protocol + '//' + location.hostname + ':' + piPort;
  }

  function resolve(url) {
    if (typeof url !== 'string') return url;
    for (const [k, v] of Object.entries(R)) {
      if (url.includes(k)) {
        const q = url.indexOf('?');
        return v + (q > -1 ? url.slice(q) : '');
      }
    }
    // ZK SMASH: tissue proxy → π:5820
    if (_tissuePort.test(url)) {
      try {
        const u = new URL(url);
        return piHost(PI_TISSUE) + u.pathname + u.search;
      } catch(e) {}
    }
    // ZK SMASH: ollama → π:1693
    if (_ollamaPort.test(url) || /[:\/]11436/.test(url)) {
      try {
        const u = new URL(url);
        return piHost(PI_OLLAMA) + u.pathname + u.search;
      } catch(e) {}
    }
    if (_oldPorts.test(url)) {
      try { return new URL(url).pathname; } catch(e) {}
    }
    // ZK SMASH: any raw 192.168.x.x:port → same host, π-port or passthrough
    if (_rawIP.test(url)) {
      try {
        const u = new URL(url);
        const port = parseInt(u.port);
        // Map known ports to π-ports
        const portMap = {11437: PI_TISSUE, 11434: PI_OLLAMA, 11436: PI_OLLAMA,
                         8080: PI_DATA, 8443: PI_GATE, 3000: 3383};
        const piPort = portMap[port] || port;
        return piHost(piPort) + u.pathname + u.search;
      } catch(e) {}
    }
    return url;
  }

  const _fetch = window.fetch;
  window.fetch = function(url, opts) { return _fetch.call(this, resolve(url), opts); };

  const _xo = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function(m, url, ...r) { return _xo.call(this, m, resolve(url), ...r); };

  console.log('%c🫁 piGut — %d routes tensor-sorted. Gaia IS the host.',
    'color:#5ab87a;font-weight:bold', Object.keys(R).length);
})();
